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

### Réplica de la parte 2 (prerregistro, 18-11-2026, 18:57)

El único indicio positivo (aprendizaje en vida ×2,4) se replica con **semillas 33–35** de `ap2-salto` y `ap2-salto-fijo` (sin nuevo P0; cadena `scripts/escalera/apertura2b.sh`, marca `apertura2b_hecho`). Regla: con las 6 semillas de cada tipo (30–35), el aprendizaje contribuye si mediana T(salto) > 1,25·mediana T(salto-fijo) **y** T(salto) > T(salto-fijo) en ≥ 5 de 6 pares por semilla. Si no se cumple, el indicio se descarta. No cambia la conclusión de apertura (0/3).

### Resultado de la réplica (19-11-2026, 18:55; mundos terminados a las 17:47)

T (épocas 1.501–2.000) por semilla 30–35. ap2-salto: 0,48 · 0,77 · 0,33 · 0,15 · 0,50 · 0,64 (mediana 0,49). ap2-salto-fijo: 0,20 · 0,11 · 0,34 · 0,81 · 0,52 · 0,78 (mediana 0,43). T/E de ap2-salto: 0,02–0,24 (máx. 0,24, otra vez < 0,5).
- **El indicio de la parte 2 no se replica:** mediana ×1,14 (< 1,25) y salto > fijo en 2/6 pares (se exigían ≥ 5/6). **Descartado**: el ×2,4 de 3 semillas era ruido de muestra pequeña. La novedad tardía es igual con y sin plasticidad en vida en este mundo.
- La conclusión de apertura no cambia: 0/6 semillas con T/E ≥ 0,5. Script: `scripts/escalera/apertura2b_regla.py`.

## Parte 3: coevolución (prerregistro, 19-11-2026, 18:58)

**Motivo:** ni el mundo estático (0/3) ni el que cambia (0/6) dan novedad sostenida, y el aprendizaje no la explica. Último eje barato con los interruptores existentes: una presión que cambia porque los propios bichos cambian (depredación, `attack_on=1`; ADR-036: coevolución).
**Mundos (rama `escalera-p4`, sustrato 2.10.0):** `ap3-ataque` = `ap2-salto` + `attack_on=1`; semillas 30–32, 2.000 épocas; cadena `scripts/escalera/apertura3.sh`, marca `apertura3_hecho`. Nulo: los `ap2-P0` ya existentes (mismo sustrato).
**Regla (la de la parte 1):** abierto si T(ap3-ataque) > 2·mediana T(ap2-P0) y T/E ≥ 0,5 en 3/3. Si el mundo se extingue o la batería lo pausa, se anota y no se reintenta ni se tocan umbrales.

### Resultado de la parte 3 (20-11-2026, 08:55; mundos terminados a las 06:51, sin extinciones ni caídas)

| mundo | T/E (s30, s31, s32) | T (épocas 1.501–2.000) | mediana T |
|---|---|---|---|
| ap3-ataque | 0,13 · 0,28 · 0,15 | 1,34 · 1,40 · 1,21 | 1,34 |
| ap2-P0 (nulo) | 0,06 · 0,09 · 0,20 | 0,06 · 0,17 · 0,41 | 0,17 |

- **Apertura por la regla: no** (T/E ≥ 0,5 en 0/3; máx. 0,28). La novedad inicial también sube (E 5–10 frente a 4–6 sin ataque), y el cociente sigue siendo bajo.
- **Indicio (no prerregistrado como criterio de éxito, pero la regla lo mide):** T(ap3-ataque) > 2·T(P0) en 3/3, y la novedad tardía absoluta es ≈ 3× la de ap2-salto (1,2–1,4 frente a 0,5) y ≈ 8× la del nulo. La depredación mantiene más novedad en valor absoluto, aunque decae igual en proporción. Clados vivos ~110–130 (frente a ~72 sin ataque y ~343 en el nulo).
- Siguiente: no un cuarto mundo al azar; implementar la medida sombra (Bedau-Packard con modelo nulo) y comprobar si ese resto es novedad adaptativa o saturación del archivo (el archivo crece 7–8 mil entradas). Script: `scripts/escalera/apertura3_regla.py`.

### Réplica de la parte 3 (prerregistro, 20-11-2026, 08:58)

Semillas 33–35 de `ap3-ataque` (`scripts/escalera/apertura3b.sh`, marca `apertura3b_hecho`). Con las 6 semillas (30–35), el indicio de que la depredación sostiene más novedad se confirma si T(ap3-ataque) > 2·mediana T(ap2-P0) (= 0,34) **y** T(ap3-ataque) > mediana T(ap2-salto, 6 semillas) (= 0,49) en ≥ 5/6 semillas. Si no, se descarta. La apertura (T/E ≥ 0,5) se evalúa aparte, con la regla original.

### Resultado de la réplica de la parte 3 (20-11-2026, 20:50; terminada a las 20:31)

T de ap3-ataque, semillas 30–35: 1,34 · 1,40 · 1,21 · 1,35 · 0,68 · 0,81 (mediana 1,27). T/E: 0,13 · 0,28 · 0,15 · 0,19 · 0,22 · 0,05.
- **El indicio se confirma** por la regla prerregistrada: 6/6 semillas con T > 0,34 (2·mediana P0) y > 0,49 (mediana ap2-salto); mínimo 0,68. La depredación sostiene ≈ 2,6× más novedad tardía absoluta que el mismo mundo sin ataque (mediana 1,27 frente a 0,49) y ≈ 7× el nulo.
- **Apertura: no** (T/E ≥ 0,5 en 0/6; máx. 0,28). Sigue siendo una novedad que decae en proporción, aunque a un nivel más alto. Queda abierto si ese nivel es adaptativo o saturación del archivo (se llena hasta ~8,6 mil entradas): hace falta el modelo sombra. Script: `scripts/escalera/apertura3b_regla.py`.

## Parte 4: depredación y señales (prerregistro, 20-11-2026, 20:55)

**Motivo:** la depredación es lo único que movió la novedad tardía (×2,6, 6/6 semillas), sin llegar a apertura (T/E ≤ 0,28). Más coevolución con el mismo interruptor barato: señales entre bichos (`signal_on=1`), que abren un canal de interacción evolucionable.
**Mundos (rama `escalera-p4`):** `ap4-ataque-senal` = `ap3-ataque` + `signal_on=1`; semillas 30–32 × 2.000 épocas (`scripts/escalera/apertura4.sh`, marca `apertura4_hecho`). (Un control P0 con depredación se descartó: sin metabolismo los ataques ya son selección.)
**Regla:** abierto si T > 2·mediana T(ap2-P0) y T/E ≥ 0,5 en 3/3. Efecto secundario: la señal añade novedad si mediana T(ap4) > 1,5·mediana T(ap3-ataque, 6 semillas = 1,27) en ≥ 2/3. Extinción o pausa: se anota, sin reintento ni cambio de umbrales.

### Resultado de la parte 4 (21-11-2026, 10:50)

Cadena acabada a las 09:48 sin caídas ni extinciones (pob. final 3.189 en s32). `scripts/escalera/apertura4_regla.py`:
T (épocas 1501–2000) = 3,46 / 3,89 / 5,54; E = 27,4 / 15,5 / 30,4; T/E = 0,13 / 0,25 / 0,18. clados vivos ≈ 107–131 (P0 ≈ 345).
- **Apertura: no** (T/E < 0,5 en 3/3; T sí > 2·P0 = 0,34 en 3/3).
- **Las señales añaden novedad absoluta: sí** (mediana T 3,89 > 1,5·1,27 = 1,9 en 3/3; ×3,1 sobre ap3-ataque, ×≈ 20 sobre P0).
- Cautela: el archivo llega a ~18.500 entradas; la novedad absoluta puede ser saturación. T/E sigue bajando. Pendiente: modelo sombra.

### Réplica de la parte 4 (prerregistro, 21-11-2026, 12:55)

`ap4-ataque-senal` con semillas 33–35 (`scripts/escalera/apertura4b.sh`, marca `apertura4b_hecho`). Regla: el efecto de las señales se confirma si mediana T(6 semillas) > 1,5·1,27 y T > 1,27 en ≥ 5/6; apertura solo si T/E ≥ 0,5 en todas. Sin reintentos ni cambios de umbrales.
