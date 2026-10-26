# Panel 08 · Segunda ronda: síntesis del diseño de C (26-10-2026, 22:36)

## Coincidencias (los tres)
- **C1 aditiva.** δ se calcula fuera de la red, como un circuito fijo al estilo del VUM de Montague. Se aparcan para después, como peldaños propios: C1b (δ como entrada, que cambiaría OBS_DIM y obligaría a un sustrato major), C2 (moduladoras dedicadas) y C3 (modulación local).
- **El resultado es el flujo de recursos, no la energía total:** r = gain − due (bocado menos el cobro que vence; en el inmediato el cobro ya va restado en `gain`). Nada de metabolismo ni empuje, que se confunden con el freno.
- **k y τ_δ son constantes, no genes.** El gen queda aparcado, como el de τ en ADR-031.
- **Hay que corregir la saturación.** Con m pegada a ±1, un término aditivo pequeño no hace nada, y eso sería un fallo de diseño, no un negativo.
- **Mundo:** P5-inmediato con la misma trampa. **El criterio de pasar (9/10) no se toca.**
- **Controles:**
  - el padre;
  - **δ barajado en el tiempo** dentro de cada bicho, con claves `jax.random`;
  - H-control repetido;
  - control positivo de la señal a nivel de cerebro: el test (c) de `test_trazas.py` con m = δ real.
- **C solo cuenta si supera al barajado,** no basta con superar al padre.
- **Sustrato 3.8.0 menor** desde `escalera-trazas`, con TRACE_ON = 0 y `config.DELTA_ON` = 0. Apagado, idéntico bit a bit.
- **Para el artículo:** «dado un sistema de valor fijo (δ), ¿evoluciona la plasticidad que lo explota?».
  - La pieza δ la ponemos nosotros.
  - Lo evolutivo son los pesos, las reglas ABCD, η, qué neuronas modulan y cómo se usa la señal.
  - Un negativo con el control positivo verde y sin saturación cierra la modulación aditiva sobre este sustrato.

## Discrepancias y síntesis del moderador
1. **La corrección de la saturación.** Método propone tanh(m + k·δ). Biología, quitar la parte tónica, (m − ⟨m⟩) + k·δ. Ingeniería, clip(0,5·m + k·δ, −1, 1).
   → **m_eff = clip(m + k·δ_acc, −1, 1), con k calibrado para que k·δ pueda cruzar la saturación.** Es el cambio más pequeño: la m de siempre más un término. Las otras dos variantes cambian además la escala o el tono de m, que la evolución ya conoce. Test: con un δ típico negativo, Δw cambia de signo con m saturada en +1.
2. **k: una rejilla de 3 valores (Método y Biología) o un valor por regla.**
   → **Un solo k, fijado por una regla mecánica antes de lanzar y sin mirar E − X:** k = 1 / mediana de |δ| en los pasos con suceso. Se mide sobre los datos de D (`_diag_signo/*.npz`, bocado y cobro del inmediato, con la misma EMA). Así un suceso típico mueve m una unidad entera y no se gastan comparaciones en la rejilla. Si con ese k no es viable, k / 2.
3. **τ_δ:** Biología propone 40; Ingeniería, 50–100.
   → **τ_δ = 50 pasos** (EMA con α = 1/50), algo por encima de TRACE_TAU, para que la media no absorba el suceso.
4. **Acumulación (Ingeniería):** la plasticidad corre cada 4 pasos. δ se acumula entre actualizaciones (`dacc`) y se reinicia en el paso plástico. Campos nuevos: `rbar` y `dacc`, f32[N], que se ponen a 0 al nacer y al morir.
5. **Barajado.** δ_bar(t) = δ(t − L), con L sorteado en [32, 63] en cada paso (`fold_in`). Usa un búfer circular de 64 pasos por bicho. Conserva la distribución y rompe la contingencia. Test: misma media y varianza por bicho, y correlación con el resultado ≈ 0.
6. **Tiempo evolutivo.** Método: desde cero. Biología e Ingeniería: desde cero más una reanudación desde la época 300.
   → **Primaria desde cero, 300 épocas: C y C-barajado, 10 semillas cada uno (~12 h).**
   - El padre son los mundos P5-inmediato ya hechos, siempre que un test confirme que 3.8.0 apagado es bit a bit 3.6.0 (`test_trazas` (a) ya lo hace con 3.7.0).
   - **La reanudación desde la época 300 es exploratoria (2–1)** y se lanza solo después, con `rbar` y `dacc` rellenos a 0.
   - «Larga», solo si hay casos aislados replicados.
7. **Lectura secundaria, exploratoria y declarada ahora (Método y Biología).** Un «caso aislado» es un mundo de C con E − X ≥ 0,05 que supera a su barajado y se replica en una segunda tanda con semillas nuevas. **No cuenta como pasa;** solo justifica abrir «Larga». En el artículo, 9/10 mide «aprendizaje robusto», no «aprendizaje posible» (C8).
8. **Contador:** C y su barajado, 1 comparación (14). La reanudación exploratoria no cuenta.

**Predicción del panel:** 9/10, un 10–15 %. Lo más probable es un indicio en 1–3 mundos, con el barajado plano y la ventaja de aprender algo mayor. Si el barajado iguala a C, lo aprendido sigue siendo maduración.

Responde en menos de 120 palabras: **ACEPTO** o **RECHAZO** (con el cambio concreto).
