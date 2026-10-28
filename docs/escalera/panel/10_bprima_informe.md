# Panel 10 · b′ construido: primaria y lanzamiento (28-10-2026, 07:29)

## Lo que lo motiva
- **Réplica de C (ADR-034, 28-10, 04:16): pasa 4/4.** ΔD de la sonda mixta en las semillas 10–19: 10/10 > 0, mediana +0,124; Cbar −0,011; diferencia +0,134; Mann-Whitney p = 9·10⁻⁵; nulo ≈ 0. Aprender qué comer con δ está confirmado. La primaria de C (trampa del alga invertida, a dónde ir) fue 0/10.
- **b′ construido** (punto 5 de ADR-034, intento 15). Rama `escalera-bprima` (worktree `panspermia-bprima`, sustrato 3.9.0), desde `escalera-c`, que ya incluye las trazas (`TRACE_ON`, `TRACE_TAU` 40). Una constante nueva:
  - `DELTA_EVENT_EPS`: si es > 0, δ = r − r̄ solo en los pasos con |r| > ε, y δ = 0 en el resto (la modulación es la del cerebro). r̄ se actualiza en todos los pasos.
  - Con `DELTA_ON` 2 se baraja el δ ya filtrado (control: «δ barajado solo en sucesos»).
  - Con ε = 0 es C bit a bit (comprobado en GPU: w, r̄, δ_acc, energía, posiciones y vivos idénticos tras 120 pasos).
  - Tests en `tests/test_bprima.py`: δ y r̄ a mano, ε = 0 igual a C, barajado como copia desfasada del δ filtrado y control positivo. Pasan 4 de 4; la suite completa está corriendo en la GPU.

## Lo que se midió para fijar ε (`scratchpad/mide_r2.py`; solo observa; P5-inmediato-C, época 300, 400 pasos)
- |r| es **bimodal**:
  - el 66 % de los sucesos son **migajas** (< 0,001): comer en celdas casi agotadas o compartidas, porque comer es un reflejo siempre encendido;
  - el 31 % son bocados completos buenos (+0,5 = EAT_RATE·DT);
  - el 1,2 % son bocados malos (−0,75);
  - cada tramo intermedio está por debajo del 1 %.
- r̄ por paso: mediana ≈ 0,055 (p95 ≈ 0,23). Rachas de sucesos: mediana 2 pasos, p95 ≈ 25.
- **Consecuencia para k:** la mediana de |δ| «en sucesos» que dio k = 8,65 (≈ 0,11) estaba dominada por migajas, donde δ ≈ −r̄. En los bocados completos la mediana de |δ| es ≈ 0,36. Con k = 8,65, cada bocado completo satura m_eff a ±1: m es binaria en sucesos, igual que en C.
- **ε = 0,05** (el 10 % de un bocado). El control positivo da exactamente el mismo resultado con ε = 0,01 y ε = 0,2, porque caen en el hueco de la distribución.

## Control positivo (sintético, con la estadística real; `tests/test_bprima.py`, 6 semillas, 40.000 pasos)
- **Diseño:**
  - la pista A llega 40 pasos antes de una racha de bocados buenos (+0,5);
  - la pista B, 40 pasos antes de una racha mala (−0,75, el alga equivocada);
  - el señuelo tiene la misma frecuencia y no anuncia nada;
  - de fondo hay rachas buenas sin anunciar (~31 % de pasos con bocado) y migajas;
  - se usan el circuito real de `island` (`_delta`, δ_acc, m_eff) y la regla real con trazas de `brain`.
- **Resultados** (pesos finales, mediana de 6 semillas; prototipo en numpy `scratchpad/proto_bprima3.py`, y el test con el código real):

| Variante | A | señuelo | B | A − B |
|---|---|---|---|---|
| C (ε = 0) + trazas | −1,62 | −2,00 | −1,74 | +0,18 (5/6) |
| **b′ (ε = 0,05) + trazas** | +3,08 | +2,69 | +2,23 | **+0,86 (6/6)**; código real +0,60 frente a +0,05 de C |
| b′ sin trazas | +2,72 | +2,77 | +2,80 | −0,13 (3/6) |
| r̄ solo en sucesos + trazas (no construida) | +2,34 | +2,04 | +1,70 | +0,63 (6/6) |

- **Lectura:**
  - b′ ordena bien (A > señuelo > B en ≥ 5/6) y discrimina mucho más que C. Sin trazas no discrimina: hacen falta las dos piezas, como previó el panel 09.
  - **Pega 1, deriva común:** todos los pesos suben a la vez. Con un 31 % de pasos con bocado, r̄ por paso queda muy por debajo de un bocado, δ ≈ +0,44 en cada uno y m satura a +1, así que se refuerza todo lo activo en los ~40 pasos antes de comer. Con C pasaba lo contrario (todo baja por el castigo tónico). Lo que distingue a la pista es el orden y la diferencia, no el signo. En un cerebro real, la deriva común podría saturar pesos (W_MAX) o la podría compensar la evolución (A, B, C, D son genes).
  - **Pega 2, k:** ver arriba; k = 8,65 «por construcción» se apoyaba en migajas.

## Preguntas
1. **¿Se lanza b′ tal cual** (ε = 0,05, k = 8,65, trazas τ 40), o la deriva común o la k piden un cambio antes (p. ej. r̄ solo en sucesos, k = 1/0,36 ≈ 2,8, o la deriva como medida secundaria)? Recordad que tocar δ gasta intento.
2. **Diseño de la tanda.** ¿P5-inmediato con b′ y su control b′bar (DELTA_ON 2, mismo ε), 10 semillas cada uno, 300 épocas, desde cero? ¿Calibración de viabilidad antes (las trazas cambian la escala de Δw)? Coste estimado: ~29 min por mundo, ~10 h los 20 mundos más ~1 h de medidas.
3. **Primaria** (medida, umbral, semillas, nulo y qué cuenta como negativo). La pregunta de b′ es «a dónde ir»: ¿trampa del alga invertida E − X (como en C, con su H-control), con qué umbral? ¿El ΔD de la sonda mixta pasa a secundaria de confirmación (no debe perderse lo de C)?
4. **Qué se mira además:** deriva de pesos (|w| medio y fracción en W_MAX), f_mod, crianza invertida.

## Formato de la respuesta (ronda 1)
Máximo ~500 palabras. Para cada pregunta: postura, por qué y riesgo principal. Al final, la primaria propuesta y una predicción numérica de que pase.
