# Panel 04 · (b0): validar una medida de crecimiento abierto con los datos que ya hay (26-10-2026, 02:48)

## Contexto
- El panel 03 (ADR-029, `docs/escalera/hoja_de_ruta.md` §6) pidió (b0): validar, **ya y en CPU ligera**, una medida de crecimiento abierto contra nulos, con los datos existentes. Se declara exploratorio, porque esas ejecuciones ya se han mirado. **El nulo, la ventana tardía y el criterio se fijan antes de mirar** las series de esas medidas.
- Hoy (26-10, 02:44) H-control pasó: la trampa del alga invertida ve un aprendizaje impuesto a mano. Las manchas (10 mundos) terminan hacia las 07:00.

## Datos disponibles (nadie ha mirado aún estas columnas con esta pregunta)
- Por época, en `runs/fase1d/<ejecución>/s<k>/stats/summary.json` (lista de dicts) y en parquet:
  - `novelty_mean`, `novelty_added`, `archive_size`: archivo de novedad sobre 12 descriptores de conducta (`metrics.py`: speed, turn, intake, attacks, signal_entropy, dispersion, aggregation, repro_age, emisiones, toxic_frac). Ojo: varios descriptores son constantes en la escalera (sin ataque, química ni señal).
  - Actividad evolutiva de Bedau–Packard: `bp_new_activity`, `bp_total_activity`, `bp_mean_activity`, `bp_components`.
  - `clade_shannon`, `clades_alive`, `genome_distance`, `genome_distance_struct`, `hidden_mean`, `synapses_mean`, `cppn_nodes_mean`, `cppn_edges_mean`, `population`, `generation_max`.
- La batería de capacidades está en `CAPABILITY_*.json` y en `result.json` de cada mundo (solo en las épocas de examen).
- **Ejecuciones:**
  - **Largas:** P2-escalera-600 y P2-escalera-sexual-600, 5 semillas × 600 épocas (comida quieta y fácil; el cerebro se vacía).
  - **De 300 épocas:** P1-escalera, P2-escalera, P3-escaso, P3-disperso, P4-alga, P4-salto64, la tripa, frena-rampa, alga por bicho (10 semillas) y, desde mañana, manchas.
  - **Posibles nulos sin selección o con selección mínima:**
    - P0-escalera (mundo feliz: sin metabolismo ni vejez; la reproducción no depende de nada; 5 × 300). Es el nulo de deriva natural.
    - P0-feliz-* (variantes de la física de mutación).
    - P1-escalera (solo peaje de vida).
- Advertencia conocida: en P0 el cerebro crecía solo por un sesgo de la mutación «nest» (ADR-015). P0-escalera ya usa la física neutral.

## Preguntas
1. **Medida:** ¿qué medida (o dos como mucho) de crecimiento abierto se prerregistra? ¿El archivo de novedad (pendiente de `archive_size` o `novelty_added` en la mitad tardía), la actividad nueva de Bedau–Packard, la complejidad del cerebro o de la CPPN, otra? Con su definición exacta.
2. **Nulo:** ¿P0-escalera como nulo de deriva? ¿Otro (genomas al azar, barajar la serie)? ¿Cómo se compara una ejecución de 600 épocas con nulos de 300?
3. **Ventana y criterio:** ¿qué ventana tardía (p. ej., épocas 150–300 o 300–600)? ¿Qué cuenta como «crece más que el nulo» (pendiente con IC, prueba de signos por semilla, umbral)? ¿Qué resultado diría «la medida vale», «no vale» o «no se puede saber con estos datos»?
4. **Validación de la medida en sí:** ¿cómo se comprueba que distingue algo (p. ej., que P2 con selección no da lo mismo que P0 al principio, o que se satura en los mundos estables)? ¿Hace falta un control positivo (un mundo que sabemos que cambia, como P4-salto64 o P4-alga)?
5. **Coste:** confirmar que es CPU ligera (solo leer JSON) y no compite con la GPU.

## Formato (máximo ~450 palabras, en español)
Medida(s) con definición · nulo · ventana y criterio de decisión · validación · riesgos. Termina con una propuesta concreta y cerrada que se pueda ejecutar tal cual.

Solo lectura: no modifiques ficheros ni lances procesos. **No abras las series de esas columnas** antes de proponer (puedes leer el código de `metrics.py` en `D:\Development\panspermia-algabicho\src\panspermia\metrics.py`, la spec y la hoja de ruta).
