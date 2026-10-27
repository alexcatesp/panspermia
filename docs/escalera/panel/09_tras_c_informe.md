# Panel 09 · Tras C: ¿y ahora qué? (27-10-2026, 21:40)

## Lo que lo motiva
- **C (ADR-033):** m_eff = clip(m + 8,65·δ_acc, −1, 1), con δ = (bocado − cobro) − su EMA de 50 pasos, sobre P5-inmediato. 10 mundos con δ real (C) y 10 con δ barajado 32–63 pasos (Cbar), 300 épocas desde cero. Datos: `runs/fase1d/_analisis_c.json`, `_crianza_c.jsonl`, `_diag_signo_c.jsonl`; detalle en la bitácora (27-10).
- **Primaria (trampa del alga invertida, `diseno.md` v2.5): no pasa, 0/10.** E − X en C: +0,040, −0,002, −0,038, +0,027, −0,073, +0,002, −0,003, +0,007, +0,024, −0,088 (mediana 0,000; ruido 0,007). Cbar, mediana +0,001. Sin indicio y sin «caso aislado». H-control sobre C: pasa (10/10).
- **Secundarias (prerregistradas como secundarias):**

| Medida | C | Cbar | Padre (P5-inmediato) | p (C frente a Cbar) |
|---|---|---|---|---|
| Sonda mixta ΔD (aprende − congelado, mismo mundo) | **+0,176** (9/10 > 0) | −0,011 | −0,046 | 0,0008 |
| P(comer el alga buena), aprende − congelado | **+0,138** (10/10) | +0,036 | +0,033 | 0,006 |
| P(comer en vacío), aprende − congelado | −0,041 | +0,042 | +0,073 | 0,05 |
| Ventaja de ingesta A | +76 % | +27 % | +50 % | 0,017 |
| ρ(m_eff, resultado), con señal | 10/10 (en parte por construcción) | 0/10 | — | — |
| Actualizaciones con el signo de m invertido por δ | 28–38 % | 28–39 % | — | — |
| f_mod ≥ 0,5 | 5/10 | 9/10 | 9/10 (D) | — |

- **Supervivencia en la crianza invertida (X/E, no prerregistrada):** C 0,78; Cbar 0,43; padre 0,40 (p = 0,0002). **El diagnóstico (21:35, regla fijada antes) dice que es innata:** criados desde el cerebro de recién nacido, C con δ real 0,795; **C congelado 0,807**; C sin δ 0,689; Cbar con su barajado 0,373; Cbar con δ real 0,409. δ real supera a sin δ en 10/10 (+0,103), pero el congelado iguala o supera al que aprende en 6/10. Con δ real, los genomas de Cbar ganan poco (+0,033).
- **Lectura del moderador:**
  1. Con δ hay aprendizaje en vida **sobre qué comer cuando ya se está encima** (ΔD, P(comer buena)); con δ barajado no lo hay. Es el primer efecto de la experiencia con significado en toda la escalera.
  2. No hay aprendizaje **de a dónde ir** (la trampa mide el sitio con el cerebro congelado tras la crianza).
  3. La evolución con δ produjo genomas innatamente más seguros ante el alga que daña, y una plasticidad que necesita a δ para no hacer daño.
  4. El control positivo del mecanismo (`tests/test_c.py`) mostró que, con k = 8,65, m_eff es casi binaria: −1 siempre que no se come y +1 tras un buen bocado. Lo activo sin premio baja de peso. Eso castiga a los estímulos que anuncian comida a distancia (el color de la mancha se ve antes de comer), justo lo que mediría la trampa.
- **Contador de comparaciones:** 14 (C y su barajado). H1, H2 gastados; H3 saltado (panel 07).
- **Opciones previstas en la hoja de ruta (Plan B 1 · C):** si C sale bien, C diferido → B + C; si mal, publicar la maduración.

## Preguntas
1. **Veredicto de C.** ¿Cómo se clasifica? (¿negativo en la primaria con indicio fuerte en secundarias?, ¿o el ΔD basta para hablar de aprendizaje de consecuencias?). ¿Hace falta una réplica prerregistrada del ΔD con semillas nuevas antes de afirmarlo?
2. **Siguiente paso, uno solo.** Opciones que ve el moderador (el panel puede proponer otras):
   - (a) **Réplica confirmatoria de ΔD** con 10 semillas nuevas de C y Cbar, ΔD como primaria (≥ 9/10 y > Cbar).
   - (b) **B + C:** trazas de elegibilidad (ADR-031, ya construidas, `TRACE_TAU` 40) con δ, para dar crédito al estímulo que anuncia el bocado (a dónde ir). Ojo al punto 4: la parte negativa de δ cuando no se come castigaría a ese estímulo. ¿Hay que cambiar δ (p. ej., δ solo en sucesos de comer, o r̄ que no cobre en vacío) antes de combinarlas?
   - (c) **C2, moduladoras dedicadas** (no conducen), o C1b (δ como entrada).
   - (d) **C diferido** (el plan original: C sobre P5-d con cobro a 30 pasos).
   - (e) **Más generaciones** (reanudar C desde la época 300, el exploratorio declarado en ADR-033).
   - (f) **Publicar** la maduración y C como resultado.
3. **El cambio de δ:** si se toca δ (punto 4), ¿es un cambio de diseño que gasta un intento o una corrección del mecanismo antes de la primera prueba real de «a dónde ir»? ¿Cómo se fija k sin mirar E − X?
4. **Primaria del paso elegido** (medida, umbral, semillas, nulo), y qué cuenta como negativo.
5. **Para el artículo:** cómo se formula lo que ya tenemos (aprendizaje de qué comer, dependiente de una señal de valor fija que ponemos nosotros; supervivencia innata).

## Formato de la respuesta (ronda 1)
Máximo ~600 palabras. Para cada pregunta: postura, por qué (con datos de arriba o bibliografía con clave de `docs/bibliografia/`), y riesgo principal. Al final, **una sola recomendación** para la pregunta 2, y la predicción numérica de su primaria.

# Ronda 1 (27-10, 21:37–21:38; resúmenes del moderador)

## Biología del aprendizaje (ronda 1)
- **P1:** primaria negativa; ΔD es indicio fuerte, no confirmado (secundaria entre 14 comparaciones). Riesgo: que ΔD sea en parte maduración dependiente de δ.
- **P2:** (a) réplica del ΔD con 10 semillas nuevas. (b) apila mecánica sobre un efecto sin replicar.
- **P3:** el problema de δ negativo en vacío es real (schultz1997neural: la pausa por omisión es pequeña y asimétrica; el RPE solo se transfiere al estímulo si hay un valor aprendido). δ por sucesos o rectificado es un cambio de diseño: gasta un intento (C-evento). k por viabilidad y por forma de m_eff (≥ 30 % de pasos con |m_eff| < 1), nunca mirando E − X.
- **P4:** ΔD > 0 en ≥ 9/10, mediana C > Cbar con p < 0,01; negativo con ≤ 7/10 o diferencia de medianas ≤ 0,08; 8/10 = indicio. Secundaria: P(comer buena) 10/10.
- **P5:** «la modulación con el signo del resultado (señal fija puesta por nosotros) produce aprendizaje en vida de qué comer, no de a dónde ir; la supervivencia es innata (garcia1966relation); con δ barajado desaparece».
- **Predicción:** mediana ΔD +0,12; 8/10 lo más probable; P(pasa) ≈ 45 %.

## Método y estadística (ronda 1)
- **P1:** negativo en la primaria; ΔD es indicio fuerte exploratorio, hace falta réplica. Sobrevive a Bonferroni de 5 secundarias (0,004), pero 9/10 por signos (p 0,011) no sobrevive a 14+ comparaciones. ΔD, P(buena) y A salen de la misma sonda: no son tres confirmaciones. Maldición del ganador. El diagnóstico de supervivencia innata se montó tras ver datos (hipótesis nueva). Riesgo: que ΔD sea del genoma evolucionado con δ y no de aprender; propone una **ablación de δ en la sonda** sobre los mismos genomas de C.
- **P2:** (a) réplica con 10 semillas nuevas de C frente a los 10 Cbar existentes. «≥ 9/10» tiene poca potencia (38 % si p_signo = 0,8).
- **P3:** tocar δ es diseño nuevo, gasta intento. k por viabilidad y control positivo sintético, nunca por E − X o ΔD.
- **P4:** pasa si ΔD > 0 en ≥ 8/10, mediana ≥ 0,08 y Mann-Whitney unilateral frente a Cbar p < 0,025; negativo si falla cualquiera; P(buena) y A, descriptivas.
- **P5:** «exploratorio, n = 10, pendiente de réplica»; no usar «aprendizaje de consecuencias» hasta la réplica; no citar ρ(m_eff, resultado).
- **Predicción:** mediana ΔD ≈ +0,10 (0,04–0,17); 7–8/10; P(pasa) ≈ 45 %.

## Ingeniería de vida artificial y cómputo (ronda 1)
- **P1:** negativo con indicio fuerte; ΔD (p 0,0008) sobrevive a Bonferroni de 14 (≈ 0,011). P(buena) +0,138 con P(vacío) −0,041 apunta a selectividad, no a gula.
- **P2:** en `island.py` δ = r − r̄ se acumula cada paso; en vacío δ = −r̄ y con k = 8,65 la suma satura m_eff a −1: castigo continuo que borra la sinapsis de la pista anticipadora. B + C sin tocar δ está condenado.
- **P3:** corrección del mecanismo que igualmente gasta intento (contador 15). δ solo en sucesos (|r| > ε): la mediana de |δ| en sucesos es la que dio k = 8,65, así que k queda fijado por construcción. La escala de las trazas se compensa con un control positivo en CPU (pista 40 pasos antes del bocado), nunca con E − X.
- **Recomendación: (b′) B + C con δ por sucesos** (`DELTA_ON=3` o `DELTA_EVENT_EPS`, `TRACE_ON=1`, `TRACE_TAU` 40; control barajado en sucesos; sustrato 3.9.0; ~14–16 h). Sin réplica aparte.
- **P4:** E − X > 0,03 en ≥ 9/10 y mediana > barajado (signos pareados p < 0,05); negativo con ≤ 6/10 o mediana < 0,01; 7–8/10 = indicio.
- **Predicción:** mediana E − X ≈ +0,02; P(pasa) ≈ 12 %; ΔD ≈ +0,15.
