# Medida de apertura evolutiva (ADR-036, rec. 3 de la auditoría) — prerregistro, 16-11-2026

**Pregunta (sí/no):** ¿sigue apareciendo novedad conductual en la última cuarta parte de una ejecución de 2.000 épocas más de lo que aparece sin selección?

**Mundos (3 semillas cada uno, 30–32, 2.000 épocas, sustrato 3.8.0 de `escalera-c`):** `ap-C` (P5-inmediato con δ), `ap-Cbar` (δ barajado: el mismo mundo sin aprendizaje guiado) y `ap-P0` (nulo sin selección: mundo feliz). Cola `scripts/escalera/apertura_<semilla>.json`, cadena `scripts/escalera/apertura.sh` (marca `apertura_hecho`, log `runs/fase1d/apertura_mundos.log`).

**Medida (solo observa):** columnas por época de `stats/` ya existentes: `novelty_added` (nuevas entradas del archivo de novedad en el espacio de descriptores, ADR-007), `bp_new_activity`, `groups_k`, `clades_alive`. Script `scripts/escalera/apertura_datos.py` (CPU).
Por mundo: T = media de `novelty_added` en las épocas 1.501–2.000; E = media en las épocas 101–300 (tramo ya conocido de las ejecuciones de 300).

**Reglas (fijadas antes de lanzar):**
- **Abierto frente al nulo:** T(ap-C) > 2·mediana T(ap-P0) en 3/3 semillas **y** T(ap-C) ≥ 0,5·E(ap-C) en 3/3 (no decae a menos de la mitad).
- **Contribuye el aprendizaje:** además, mediana T(ap-C) > 1,25·mediana T(ap-Cbar).
- **Lectura:** C abierto y Cbar no → el aprendizaje guiado sostiene novedad. Ambos abiertos y > P0 → lo sostiene el mundo/la selección, no el aprendizaje (decisión del responsable 2: «a dónde ir» no era puerta). Ninguno por encima de P0 o todos decaen → el cuello está en el mundo (hay que enriquecerlo: coevolución, más de un reto).
- Descriptivas sin puerta: `bp_new_activity` (ojo: el nulo la infla por deriva neutral, `clades_alive` ≈ 330 frente a ≈ 90), `groups_k`, tamaño de cerebro.

**Datos previos (CPU, 300 épocas, medianas; `apertura_datos.py`):** `novelty_added` por tramos de 100 épocas: P0-escalera 6,4 → 2,7 → 1,6; P0-feliz-neutral 8,7 → 1,6 → 1,6; C 9,0 → 8,0 → 6,0; Cbar 11,7 → 10,4 → 5,8; b′ 9,8 → 10,9 → 6,8; P3-escaso 18 → 2,3 → 0,8. C y Cbar decaen menos que el nulo y que los peldaños anteriores, pero C ≈ Cbar: si sigue así, no es el aprendizaje.
**Limitación:** una sola métrica de novedad (archivo de descriptores medios); MODES y Bedau-Packard con modelo sombra siguen sin implementar.
