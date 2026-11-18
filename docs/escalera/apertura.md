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

## Resultado (17-11-2026, 12:55; 9 mundos terminados, `apertura_regla.py`)

`novelty_added` medio: E (101–300) → T (1.501–2.000), T/E.
- ap-C: 7,96 → 0,52 (0,07); 9,59 → 0,83 (0,09); 7,78 → 0,67 (0,09).
- ap-Cbar: 8,12 → 0,38 (0,05); 8,57 → 0,23 (0,03); 8,05 → 0,68 (0,08).
- ap-P0: 1,03 → 0,07 (0,07); 1,69 → 0,16 (0,09); 2,19 → 0,36 (0,17).

**Veredicto por la regla fijada: no hay apertura.** T(C) > 2·mediana T(P0) (0,32) se cumple en 3/3, pero T/E ≥ 0,5 en 0/3: la novedad cae un 91–93 % en C. Cola de C frente a Cbar: mediana 0,67 frente a 0,38 (×1,76 > 1,25), pero con 3 semillas y solapamiento (0,68 de Cbar s32 frente a 0,52 de C s30); indicio débil, sin potencia. Lectura de la regla: todos decaen → el cuello está en el mundo, no en el aprendizaje.
**Cautelas:** (1) `novelty_added` mide entradas nuevas en un archivo de descriptores medios; un archivo que se llena y la rampa de comida (épocas 1–100) pueden bajarla sin que la evolución se pare. (2) Las variables por época (cerebro, masa, distancia de genomas, descriptores) siguen derivando al final en los tres tipos de mundo, también en el nulo P0 (deriva neutral), y las pruebas z por época están inflados por la autocorrelación (`apertura_deriva.py`): no discriminan. Falta un modelo sombra (Bedau-Packard completo) para separar deriva de novedad adaptativa.

## Parte 2: mundo que cambia (prerregistro, 17-11-2026, 13:20)

**Motivo:** con el mundo estático todo decae (parte 1). En los mundos de 300 épocas, el que más novedad conservó fue P4-salto64 (comida desplazada 64 u cada 1.000 pasos: 11,3 → 4,7, T/E 0,42), y los E1/E2 con toxicidad cambiante la mantuvieron en el techo (32 altas por época, `NOVELTY_MAX_ADD`; no comparable en magnitud). Hipótesis: un mundo que cambia exige novedad sostenida. (El código excluye `ALGA_PATCH_FAMILIES` con `FOOD_JUMP_PERIOD`, así que no se puede añadir el salto al mundo de C sin un sustrato nuevo.)
**Mundos (rama `escalera-p4`, sustrato 2.10.0; semillas 30–32, 2.000 épocas; cadena `scripts/escalera/apertura2.sh`, marca `apertura2_hecho`):** `ap2-salto` (P4-salto64 con plasticidad), `ap2-salto-fijo` (mismo mundo con plasticidad apagada: control sin aprendizaje en vida) y `ap2-P0` (nulo sin selección en el mismo sustrato).
**Reglas (las de la parte 1):** abierto si T(ap2-salto) > 2·mediana T(ap2-P0) y T/E ≥ 0,5 en 3/3; el aprendizaje en vida contribuye si mediana T(ap2-salto) > 1,25·mediana T(ap2-salto-fijo). Una extinción se anota y no se reintenta.

### Resultado de la parte 2 (18-11-2026, 18:50; mundos terminados a las 17:49, sin caídas)

| mundo | T/E por semilla (30, 31, 32) | T (épocas 1.501–2.000) | mediana T |
|---|---|---|---|
| ap2-salto (plástico) | 0,09 · 0,20 · 0,05 | 0,48 · 0,77 · 0,33 | 0,48 |
| ap2-salto-fijo (sin plasticidad) | 0,04 · 0,03 · 0,04 | 0,20 · 0,11 · 0,34 | 0,20 |
| ap2-P0 (nulo) | 0,06 · 0,09 · 0,20 | 0,06 · 0,17 · 0,41 | 0,17 |

- **Apertura: no** (T/E ≥ 0,5 en 0/3; el máximo es 0,20). Aun con el mundo cambiando cada 1.000 pasos, la novedad cae un 80–95 % entre las épocas 101–300 y la cola.
- **Aprendizaje en vida contribuye: sí por la regla** (0,48 > 1,25 × 0,20, ×2,4), y ap2-salto supera a 2·P0 en 2/3 semillas (no en s32, donde el nulo sube a 0,41). Solo 3 semillas y valores absolutos pequeños: indicio, no conclusión. Mismo patrón que en C (≈ ×1,8).
- Los clados vivos son ~72 en los mundos con selección y ~343 en el nulo (menos diversidad con selección); la actividad Bedau-Packard simplificada es mayor en el nulo (6,9 frente a ~1): sin modelo sombra no distingue novedad adaptativa de deriva.
- Script: `scripts/escalera/apertura2_regla.py`.
