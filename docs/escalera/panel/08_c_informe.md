# Panel 08 · Diseño de C: modulación con signo de resultado (26-10-2026, 22:35)

## Lo que lo motiva
- **H2 negativo** (ADR-030): el veneno diferido y el inmediato dan 0/10 en la trampa del alga invertida, con H-control válido.
- **Panel 07 (ADR-032):** se salta H3. Orden: D → C sobre el inmediato → C diferido → B + C.
- **Responsable (22:16):** solo C. La publicación de la maduración, aparcada por ahora.
- **Resultado de D (22:30; bitácora, última entrada).** Regla prerregistrada → **C como término aditivo**.
  - Hay moduladoras: f_mod ≥ 0,5 en 9/10 mundos, con 1,0–2,8 por bicho.
  - m no sigue al resultado (bocado − cobro): sin señal en 10/10.
  - Solo en 2/10 baja con el cobro inmediato.
  - m está **saturada**: |m| > 0,99 en el 42–64 % de los pasos, y en el 1–56 % de los bichos es constante. Las moduladoras **también conducen** (`brain.py`: «también proyectan como ocultas normales; además definen m_t»), así que la modulación es tónica (un signo fijo) y no fásica.

## Preguntas del responsable que el panel debe tener en cuenta (22:17–22:27)
1. **¿Cómo se construye el cerebro en la bibliografía?** Resumen del moderador:
   - **soltoggio2008evolutionary** (`docs/bibliografia/1d/`): las moduladoras son **dedicadas** (solo modulan, no conducen) y la modulación es **local** por neurona; el premio entra como un sentido; la tarea va por pruebas separadas.
   - **niv2002evolution** y Montague et al. (1995): el néctar entra en una neurona tipo dopamina que, al evolucionar, calcula «premio − lo esperado». La arquitectura viene dada y evolucionan los parámetros. *Detalle de memoria del moderador; tenemos el texto completo, comprobadlo si lo usáis.*
   - Izhikevich (2007): traza por sinapsis más dopamina global, que da el experimentador.
   - Najarro y Risi (2020): ABCD sin modulación, es decir, auto-organización o maduración, que es lo que vemos.
2. **«¿El chivato es aprendizaje por refuerzo?»** Sí: el error de predicción de recompensa. Pero sin retropropagación y con la propia energía como resultado, así que los principios 1 y 5 quedan intactos. Precio declarado: la pieza la ponemos nosotros. El resultado sería «aprenden si tienen chivato», no «el aprendizaje surge solo». El panel debe decir cómo se formula esto en el artículo y qué parte sigue siendo evolutiva.
3. **«¿Por qué a pontes2020evolutionary sí les salió? ¿Es cuestión de número de mundos?»** El moderador ve tres diferencias:
   - (i) **Sustrato:** programas con memoria, donde aprender es guardar un dato al primer error.
   - (ii) **Tarea:** un rastro de decisiones separadas, con el significado de la pista sorteado por organismo y el error marcado al instante.
   - (iii) **Tiempo:** decenas de miles de generaciones frente a ~500 nuestras («gen máx 520»). El aprendizaje aparece el último de una secuencia.
   - Además, **solo el 7 % de los linajes** aprende (el 2 % reaprende). Con esa tasa, **nuestro criterio de 9/10 no se cumpliría aunque el aprendizaje fuera posible** (C8 de `condiciones_aprendizaje.md`). Pero en 30 mundos no hay ni un caso aislado: el máximo de E − X es +0,026.

## Preguntas
1. **Forma de C (un solo cambio, aditivo según la regla de D).** El moderador ve:
   - **C1, aditiva:** m ← m + k·δ, con δ = ΔE − ⟨ΔE⟩ (cambio de energía del paso menos su media móvil, de constante τ_δ), calculado fuera de la red (un circuito fijo, como el VUM de Montague).
   - **C1b:** δ como **entrada** nueva solo a las moduladoras. La red decide cuánto la usa; se parece más a Niv.
   - **C2:** moduladoras dedicadas (no conducen). Ataca la saturación, pero la regla de D dice aditiva, no estructural.
   - **C3:** modulación local por neurona.
   - ¿Cuál? ¿k y τ_δ son constantes o genes? ¿Qué es exactamente ΔE: bocado − cobro, o la energía total, que incluye metabolismo y movimiento? ¿Hay que acotar m, por ejemplo con tanh?
2. **Mundo, padre y primaria:**
   - ¿P5-inmediato, con la misma trampa y ≥ 9/10?
   - Controles: el padre, **δ barajado en el tiempo dentro de cada bicho** (Método, panel 07) y el H-control repetido.
   - Con la pregunta 3 del responsable, ¿se mantiene el 9/10 o se declara además una lectura de «casos aislados» (un mundo con E − X ≥ 0,05 y réplica)? Sin tocar el criterio prerregistrado de pasar.
3. **Tiempo evolutivo:** ¿300 épocas bastan? ¿O se desde cero, o se parte de los checkpoints de P5-inmediato (época 300) para no gastar las primeras generaciones? Y la opción «Larga» de Pontes (más generaciones), ¿cuándo?
4. **Sustrato:** ¿3.8.0 desde `escalera-trazas` (con TRACE_ON = 0, para que B + C sea luego un solo interruptor)? Tests: apagado, idéntico bit a bit; δ calculado a mano; el control positivo de `test_trazas.py` (c) con m = δ real; determinismo.
5. **Predicción.**

## Ficheros
- `docs/decisiones.md`: ADR-030, ADR-031 (y su adenda) y ADR-032 (y sus resultados).
- `docs/escalera/hoja_de_ruta.md` §4, `docs/escalera/condiciones_aprendizaje.md` y `docs/bibliografia/escalera/README.md` §§17–19.
- `docs/escalera/panel/07_*`.
- Código: `D:\Development\panspermia-trazas\src\panspermia\` (brain.py, island.py, config.py) y `tests/test_trazas.py`.
- Datos: `runs/fase1d/_diag_signo.jsonl` y `_analisis_veneno.json`.

## Formato (máximo ~500 palabras, en español)
Forma de C (1) · mundo, controles y criterio (2) · tiempo evolutivo (3) · sustrato y tests (4) · predicción. Solo lectura: no modifiques ficheros ni lances procesos.
