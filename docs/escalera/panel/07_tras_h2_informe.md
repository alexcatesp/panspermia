# Panel 07 · Tras H2 (P5-d): ¿H3, plan B 1 o diagnóstico antes? (26-10-2026, 21:55)

## Resultado que lo motiva
P5-d, veneno diferido e inmediato (ADR-030), 10 + 10 mundos × 300 épocas, F = 2,5. Medidas terminadas el 26-10 a las 21:52. Detalle en `docs/bitacora.md`, última entrada; datos en `runs/fase1d/_analisis_veneno.json`.

- **Primaria (trampa del alga invertida, examen barajado, E − X ≥ 0,05 en ≥ 9/10):**
  - **Diferido 0/10:** mediana +0,004, positivos 6/10, ruido 0,008. Sin indicio.
  - **Inmediato 0/10:** mediana +0,006, positivos 7/10, ruido 0,0065. Sin indicio.
  - Secundarias del examen (selectividad de entrada, D_comer, primer contacto, ingesta): ≈ 0.
- **H-control sobre el inmediato:** positivo 10/10 (frac_buena +0,18 a +0,36), débil 10/10, negativo 10/10. **La trampa funciona en estos mundos.**
- **Crianza invertida (X):** sobrevive solo el 54–73 % (diferido) y el 29–51 % (inmediato), frente al 92–96 % de E. Empiezan sobre su alga de verdad, que en X envenena, y la mayoría se queda y muere. **Ni siquiera con el cobro inmediato, que la tripa ve como neto negativo, aprenden a irse en 200 pasos.**
- **Maduración:** frac_buena N 0,70–0,75 → D 0,78–0,82 → E ≈ X 0,81–0,84 → A 0,83–0,85; A − E ≈ 0; M mediana 0,53 (diferido) y 0,73 (inmediato).
- **Sonda mixta:** ventaja de ingesta A +121 % (diferido) y +50 % (inmediato), nulo ±6 %. ΔD ≈ 0 en el diferido y **negativo** en el inmediato (mediana −0,047, 7/10). P(comer el alga equivocada), plástico − congelado: +0,07 en los dos. **Lo que aprenden en vida es comer más en general, no evitar lo que les daña.**
- **Regla 7 de ADR-030:** el inmediato ≤ 3/10 con viabilidad 10/10 y H-control validado → **H2 cuenta como negativo** y el diferido no se interpreta por sí solo. Es el tercer negativo sobre el mismo mecanismo: alga por bicho, manchas y veneno inmediato. **Saltar H3 e ir al plan B 1 lo decide este panel; no es automático.**
- **Contador:** 13. Predicción del panel 05: el diferido 0–2/10 ✓; el inmediato, quizá un indicio (Método) ✗.

## Lo ya construido
- **Trazas de elegibilidad (ADR-031)**, rama `escalera-trazas` (sustrato 3.7.0, `config.TRACE_ON`, τ = 40), probadas en CPU (`tests/test_trazas.py`). **Hallazgo del control positivo:** la traza solo da crédito al estímulo predictivo si la modulación m lleva el signo del resultado («mejor o peor de lo esperado») en el momento del resultado. Con m solo positiva, gana un distractor; con una línea base en cada paso, el estímulo sale castigado.
- La plasticidad actual: Δw = η·g·m·(A·xi·xj + B·xi + C·xj + D). m es la media de las neuronas ocultas moduladoras expresadas. Las moduladoras ven lo mismo que las demás: obs (80, incluida la tripa y la energía) y h. No hay ninguna entrada de «error de predicción». Código en `D:\Development\panspermia-trazas\src\panspermia\brain.py` e `island.py`.
- Cerebros de ~2 neuronas ocultas expresadas (log de los mundos: «ocultas 1,8–1,9»). Con tan pocas, puede no haber moduladoras.

## Opciones que ve el moderador
- **A. H3:** un tercer diseño de mundo, como pide la hoja de ruta. ¿Cuál? ¿Tiene sentido cuando ni el cobro inmediato se aprende?
- **B. Plan B 1, trazas:** primer uso prerregistrado por el panel 06 sobre P5-d diferido, con un solo cambio (`TRACE_ON`). El control es el P5-d actual. 10 semillas, ~6 h de mundos más ~1 h de medidas.
- **C. Plan B 1, modulación con signo de resultado** (recompensa predicha, Niv 2002; Soltoggio 2008): por ejemplo, que las moduladoras reciban el cambio de energía menos su media móvil, o que m sea directamente ese error. Sustrato nuevo; la combinación con las trazas sería un segundo paso.
- **D. Diagnóstico antes de variar, solo observa (CPU o GPU corta):** sobre los checkpoints de P5-d, medir si hay neuronas moduladoras expresadas y cuántos bichos las tienen; la correlación entre m y el cambio de energía (bocado, cobro); y si m cambia de signo con el cobro inmediato. Decidiría entre B y C sin lanzar mundos.
- **E. Plan B 2, publicar la maduración**, en paralelo con lo que se elija.

## Preguntas
1. ¿Se acepta H2 como negativo según la regla 7? ¿Se salta H3?
2. ¿Qué opción (o qué orden) y por qué? Si es B o C, ¿la primaria sigue siendo la misma trampa, sobre el diferido, sobre el inmediato o sobre los dos?
3. Si D, ¿qué medidas exactas y qué regla de decisión, fijada antes de verlas?
4. Predicción.

## Ficheros
- `docs/escalera/hoja_de_ruta.md` §4; `docs/decisiones.md` ADR-028, ADR-030 y ADR-031; `docs/escalera/diseno.md` v2.4.
- `docs/escalera/condiciones_aprendizaje.md` y `docs/bibliografia/escalera/`.
- `docs/escalera/panel/05_*` y `06_*`.
- Código: `D:\Development\panspermia-trazas\src\panspermia\` (brain.py, island.py, config.py) y `tests/test_trazas.py`.

## Formato (máximo ~450 palabras, en español)
Voto (1) · opción y orden (2) · diagnóstico con su regla, si lo propones (3) · predicción. Solo lectura: no modifiques ficheros ni lances procesos.
