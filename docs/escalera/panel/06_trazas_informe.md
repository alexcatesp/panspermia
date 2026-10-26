# Panel 06 · Diseño de las trazas de elegibilidad (plan B 1), para tenerlas listas en paralelo (26-10-2026, 06:36)

## Contexto
- El panel 05 (ADR-030) decidió construir ya, **solo código y tests en CPU**, en rama propia (sustrato 4.0.0), la plasticidad con trazas de elegibilidad. No se lanzan mundos hasta que la regla de parada lo pida (`docs/escalera/hoja_de_ruta.md` §4).
- P5-d (veneno diferido, 30 pasos) corre en la GPU desde las 06:33. Los tres expertos predicen que no pasará con la plasticidad actual: la modulación es inmediata y no hay crédito a 30 pasos.

## Plasticidad actual (rama `escalera-veneno`, `src/panspermia/brain.py`)
- `step`: h' = tanh(W_hid^T [o; h]) ⊙ mask; a = tanh(W_out^T [o; h']).
  - pre = [obs (80); h (64)] = 144.
  - post = [h' (64); acciones (8)] = 72.
- `modulation`: m_t es la media de las ocultas moduladoras expresadas (`hid_type`).
- `plasticity`: Δw = η·g·m·(A·xi·xj + B·xi + C·xj + D), recortado a |w| ≤ W_MAX. Se aplica cada `PLASTICITY_EVERY` = 4 pasos (island.py:410), con el pre y el post de ese paso.
- η, g, A, B, C y D son salidas de la CPPN por sinapsis (`develop.py`, `CPPN_OUT` = 8: w0, A, B, C, D, η, express, g_mod). Pesos vivos `w` f32 [N, 144, 72].
- **Memoria:** el equipo no tiene archivo de paginación y WSL se ha caído dos veces. Un array más [4.096, 144, 72] f32 son ~170 MB.

## Preguntas
1. **Forma de la regla.** ¿e_t = λ·e_{t−1} + hebb_t y Δw = η·g·m_t·e_t (Izhikevich 2007; Gerstner et al. 2018)? ¿Otra (por ejemplo, la traza solo del término A·xi·xj)? ¿Se actualiza la traza en cada paso o cada 4?
2. **λ (o τ):**
   - ¿una constante global?
   - ¿un gen escalar por bicho, que evoluciona?
   - ¿una salida nueva de la CPPN por sinapsis (CPPN_OUT 9, que rompe el formato del genoma → 4.0.0)?
   - ¿qué rango? 30 pasos de retardo piden τ ≳ 30.
3. **Modulación de recompensa predicha** (Niv 2002; Soltoggio) como alternativa o complemento. ¿Entra ya o se aparca?
4. **Compatibilidad:** con λ = 0 (o con el interruptor apagado), ¿debe ser idéntico bit a bit a 3.6.0? ¿Qué tests: equivalencia apagada, un caso de crédito diferido a mano (un pre y un post en el paso t y una modulación en t + 30 cambian w solo con la traza), memoria y determinismo?
5. **Primer uso cuando toque:** ¿sobre P5-d diferido (mismo mundo, un solo cambio: la plasticidad) con la misma primaria?
6. **Riesgos:** inestabilidad (pesos que se disparan por la traza), coste en GPU y memoria, y cerebros que se vacían (sin neuronas moduladoras no hay m).

## Ficheros
- `D:\Development\panspermia-veneno\src\panspermia\brain.py`, `develop.py`, `island.py` (plasticidad, línea ~400) y `config.py`.
- `docs/escalera/hoja_de_ruta.md` §4, `docs/escalera/condiciones_aprendizaje.md` y `docs/decisiones.md` ADR-030.

## Formato (máximo ~450 palabras, en español)
Diseño cerrado (regla, λ, alcance, tests) · riesgos · qué se aparca. Solo lectura: no modifiques ficheros ni lances procesos.
