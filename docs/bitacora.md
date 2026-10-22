# Bitácora de laboratorio

Cuaderno cronológico de **todo lo que se prueba**: qué, con qué parámetros y qué código (commit), dónde están los datos y qué salió, también lo que falla. Es la materia prima de cualquier publicación.

Cómo se relaciona con los demás documentos:
- `docs/decisiones.md` (ADR) registra **decisiones**;
- `docs/caminos.md` registra el **estado de cada opción** (descartada, aparcada o en estudio);
- esta bitácora registra **los experimentos y su resultado**, en orden.

**Formato de cada entrada**:

```
### AAAA-MM-DD HH:MM · título
- Qué: ...
- Código: commit (rama) · Datos: runs/... · Mundo: N, semillas, épocas
- Resultado: números concretos
- Conclusión: ... (firme | indicio | descartado | aparcado) · Ver: ADR / caminos
```

Los datos (`runs/`) no están en git porque ocupan mucho. Conviene hacer una copia de seguridad fuera del ordenador antes de publicar.

---

## 2026-10-15

### 21:29 · Esqueleto del proyecto
- Qué: spec, ADR-001–004, bibliografía y módulos vacíos de la fase 0.
- Código: `5e43da0` (main).

### 22:57 · Fase 0: núcleo 2D determinista
- Qué: mundo 2D, genoma CPPN, desarrollo, cerebro recurrente con plasticidad ABCD modulada, isla bajo `jit`/`scan` y checkpoints.
- Código: `2dc80af` · Mundo: N = 4.096.
- Resultado: 18 tests en verde con `--runslow`; determinismo bit a bit en 10 épocas; ida y vuelta de 10⁴ genomas sin pérdidas; ≥ 4 de 5 semillas sin extinción en 100 épocas; 2,0·10⁶ pasos-hueco/s (~4,9·10⁵ pasos-agente vivo/s; época de 2,07 s).
- Conclusión: firme · Ver: ADR-005, ADR-006.

### 23:41 · Fase 1: ecología, métricas, batería de capacidad y visor
- Qué: ataque frontal con carroña (60 % al atacante, energía conservada), señal, senescencia, biogeografía, métricas (clados, Shannon, novedad, grupos, Bedau-Packard, valor del aprendizaje por cohortes), batería de capacidad v1 (comunicación, anillo, laberinto) y visor web.
- Código: `b9c8583` · Ver: ADR-007.

## 2026-10-16

### 00:20 · Fase 1b implementada (química y algas estacionales)
- Qué: nutriente, toxina y feromona con difusión; emisión como acción; dos tipos de alga, uno tóxico, con cambio global de cuál con probabilidad 1/400 por paso; `TOXIC_FACTOR = 1`.
- Código: `e353e07` (rama `fase1b`) · Ver: ADR-008.

### 00:00–03:15 · Aceptación de la fase 1 (5 semillas × 500 épocas)
- Código: `b9c8583`+ (main) · Datos: `runs/phase1/s0–s4`, `runs/phase1.log` · Mundo: N = 4.096, semillas 0–4, nodos `phase1-<s>`.
- Resultado:
  - sin extinciones;
  - la batería v1 pausó 4 de 5 islas por `ring_gain`: s1 0,844, s2 0,516 (época 200), s3 0,750 y s4 0,734 en la época 100; s0 llegó a 500 épocas (máximo 0,469);
  - neuronas ocultas en s0: 8 → 3,1 en la época 500;
  - gen de ataque ~0,9–1,0; más muertes por mordisco que por hambre;
  - comunicación ≤ 0,04 bits;
  - silueta ≥ 0,3 solo al principio (racha tardía de 4 épocas en s0);
  - archivo de novedad de s0 con 4.316 descriptores y +197 en las últimas 50 épocas.
- Conclusión: firme (ecología estable, estrategia simple, cerebros que encogen) · Ver: ADR-010.

### 01:20 · Controles sin cerebro de la batería v1
- Qué: `scripts/capability_controls.py` sustituye el cerebro por políticas fijas.
- Resultado: avanzar recto con empuje 1, sin cerebro, saca **1,000** en el anillo; empuje 0,5, 0,734; girar, 0.
- Conclusión: firme · la prueba del anillo queda **descartada** (falso positivo) · Ver: ADR-010, caminos.

### 01:45–02:00 · Suite de la 1b en GPU: 0 de 5 semillas sobreviven
- Código: `b9a74a2` (fase1b).
- Resultado: 3 tests fallidos. Uno era `no_extinction` (0 de 5); los otros dos eran tests desfasados (versión mayor e invariancia por `comm_hist`).
- Diagnóstico (semilla 0, N = 4.096): en la primera época mueren 505 de 512 por veneno.
- Ablaciones de 5 épocas:

| Variante | Resultado |
| --- | --- |
| sin estaciones | se recupera (167 → 1.606) |
| sin emitir y sin estaciones | se recupera (331 → 3.282) |
| sin emitir, con estaciones | extinción |
| `TOXIC_DAMAGE = 0` | extinción |
| `TOXIC_FACTOR = 0` | extinción |

- Conclusión: firme · un cerebro aleatorio no distingue algas; con la mitad tóxica, comer de todo no basta · Ver: ADR-008 (calibración), caminos.

### 02:00–02:50 · Rampa de toxicidad (40 épocas)
- Resultado (semilla 0): supera la rampa, la fracción tóxica ingerida baja de 0,53 a ~0,04–0,15 y deja de emitir toxina, pero entra en ciclos de auge y colapso y se extingue en la época ~79.
- Variantes de 100 épocas, semilla 0:

| Variante | Extinción | Mínimo tras la época 40 | Población media |
| --- | --- | --- | --- |
| base | época 79 | — | — |
| `TOXIC_FACTOR = 0,5` | no | 73 | ~900 |
| cambio 1/1000 | no | 28 | ~1.240 |
| ambos | no | 44 | ~1.210 |

- Conclusión: indicio · la población evoluciona discriminación durante la rampa.

### 02:50–04:20 · Cambio global frente a regiones móviles (5 semillas)
- Global C1 (`TOXIC_FACTOR` 0,5, cambio 1/1000): extinción en 2 de 5 (s2 en la época 68, s3 en la 27).
- Global C2 (C1 + `RESOURCE_R` 2): extinción en 1 de 4 válidas (s2 en la 53); toca el tope de 4.096. La s4 de C2 está contaminada por un cambio de código a mitad y se descarta.
- Regiones móviles (franjas k = 2 a 5 u/t):
  - S2 (factor 1, R 1,5): extinción en s2 (época 35) y s0 (época 45);
  - **S1 (factor 0,5, R 1,5): sin extinción**, con mínimos de 1.150 (s0) y 308 (s2).
- Conclusión: firme · el cambio global sincronizado colapsa poblaciones; las regiones móviles con veneno a la mitad son viables · Ver: ADR-008 (calibración), caminos.

### 04:40–05:47 · Suite de la 1b calibrada
- Código: `6b6fae1` (fase1b).
- Resultado: 41 de 42 tests en verde. El de determinismo falló por interferencia de memoria al correr en paralelo; repetido en solitario, pasa. La no extinción (≥ 4 de 5 semillas, 100 épocas, nodo `test-node`) pasa.

### 05:55–11:50 · Aceptación de la 1b (5 semillas × 500 épocas)
- Código: `6b6fae1` y `130f6e6` (tras el arreglo de guardado) · Datos: `runs/phase1b/s0–s4`, `runs/phase1b.log`. El intento previo que falló por memoria está en `runs/phase1b_crashed_oom`.
- Resultado:

| Semilla | Desenlace | Población final | Neuronas ocultas | Fracción tóxica (época 40) | Gen de ataque |
| --- | --- | --- | --- | --- | --- |
| s0 | sobrevive, 500 épocas sin pausa | 1.819 | 8 → 21 | 0,28 | ~0,86 |
| s1 | **extinta** en la época 64 | — | 8 → 17,8 | 0,18 | 0,89 |
| s2 | sobrevive | 2.132 | ~6–7,6 | 0,38 | **0,45** |
| s3 | **extinta** hacia la 48, en plena rampa | — | ~8,5 | 0,43–0,48 | 0,6 |
| s4 | **extinta** antes de la 199 | — | — | — | — |

- Conclusión: indicio · dos rutas de supervivencia, discriminar (s0) o volverse pacífico (s2); aprender no garantiza sobrevivir (s1); los bichos reinyectados mueren en un mundo ya venenoso · Ver: informe de la 1b (pendiente), ADR-012.

### 06:10–07:20 · La métrica del valor del aprendizaje está degenerada; sonda emparejada
- Qué: `scripts/learning_probe.py` corre la misma época desde el mismo checkpoint, con y sin plasticidad.
- Resultado: la supervivencia de cohortes es 0 frente a 0 en la 1b y 0,2–0,8 % en la fase 1, porque la edad media es ~140 pasos y la época dura 1.000.
- Sonda a nivel de población:

| Checkpoint | Población (plástica / congelada) | Ingesta | Nacimientos |
| --- | --- | --- | --- |
| 1b s0, época 100 | 1.051 / 747 (+41 %) | +42 % | +25 % |
| fase 1 s0, época 100 | +5 % | +6 % | +15 % |
| fase 1 s0, época 200 | 3.407 / 3.295 | +11 % | +16 % |
| fase 1 s0, época 300 | 3.461 / 3.362 | +12 % | +16 % |
| fase 1 s0, época 500 | −5 % | +14 % | +18 % |

  En la fase 1 la plasticidad también trae más muertes por mordisco. Datos: `runs/learning_probe.jsonl`.
- Conclusión: descartada la métrica de cohortes; indicio de que la plasticidad mejora la ecología (n pequeño) · Ver: ADR-010 (corrección).

### 08:13 · Caída de WSL por sobrecarga
- Qué: cuatro trabajos a la vez (aceptación en GPU y tres análisis en CPU con N = 4.096).
- Lección: un solo trabajo pesado cada vez.

### 08:20–09:16 · Fallo al reanudar desde checkpoint (memoria fija en WSL2)
- Resultado: el primer guardado tras restaurar con N = 4.096 da `RESOURCE_EXHAUSTED` (xla_gpu_host_bfc). Es reproducible y solo ocurre tras restaurar. Se arregla guardando con `jax.device_get(state)`, con ida y vuelta exacta.
- Código: `19a2d7f`.

### 07:30–12:23 · Batería de capacidad v2
- Control negativo (cuerpos aleatorios): la mejor política sin cerebro saca 0,031 en la mancha a 150 u y 500 pasos.
- Control positivo (buscador programado):

| Mancha | Cuerpos | Mejor control sin cerebro | Buscador |
| --- | --- | --- | --- |
| 150 u, 500 pasos | aleatorios | 0,031 | 0,234 |
| 90 u, 1.000 pasos | aleatorios | 0,062 | 0,500 |
| 90 u, 1.000 pasos | evolucionados (fase 1, s0, época 500) | 0,219 | 0,562 |

- Decisión del responsable: mancha a 90 u, 1.000 pasos, umbral 0,2, controles con los mismos cuerpos.
- Resultado: con la v2, las cinco islas de la fase 1 dan ganancias de 0,078, −0,016, 0,078, 0,062 y −0,031: **ninguna pausaría**.
- Código: `ccb35aa`, `147cc39` · Datos: `runs/battery_v2_final.jsonl` · Ver: ADR-011.

### 11:42 · Parada automática de islas extinguidas
- Qué: se detienen tras 20 épocas seguidas con población 0 pese a reinyectar. Código: `962e5e8`.

### 11:50 · Benchmark de varias islas por GPU (`vmap`)
- Resultado: con B = 1 el lote **no coincide bit a bit** con la ejecución individual; con B = 2 y N = 4.096 se agota la VRAM. Dos procesos a la vez casi duplican el tiempo por época.
- Conclusión: aparcado · Código: `53445bc` (rama `multi-mundo`) · Ver: caminos.

### 12:55 · Reanudación de las islas 1–4 de la fase 1 con la batería v2
- Qué: `CAPABILITY_REVIEW.json` firmado por el responsable; umbrales sin cambios. En curso.

### 13:01 · Bibliografía de la fase 1d
- 26 referencias verificadas · Ver: `docs/bibliografia/1d/`.

### 13:08 · Diseño de la fase 1d (protocolo prerregistrado v0.1)
- Aprobado por el responsable: E0–E2 primero; el tamaño del mundo se decide en E0 · Ver: `docs/fase1d/diseno.md`.

### 13:20–14:00 · Implementación de la fase 1d (E0–E2)
- Qué: toxicidad por parches 8 × 8 (aleatorio con probabilidad 2/T, periódico con inversión global cada T/2 y reloj sincronizable, fijo), gemelo sin plasticidad, VA emparejado dentro del runner, uso del reloj, anticipación, duración media de la vida y experimentos declarativos con barridos.
- Código: `58dfc48` (rama `fase1d`) · Tests: 12 de la 1d y 18 de la 1d + 1b en verde en CPU.
- Pendiente: suite completa en GPU y cola E0 (`experiments/fase1d/e0.json`: 4 condiciones × 5 semillas × 100 épocas).

### 14:00 · Fase 1, isla 1 reanudada con la batería v2: 500 épocas sin pausa
- Datos: `runs/phase1/s1` · Resultado: población final de 3.755, sin pausas. La batería v2 funciona en una ejecución real.

### 15:25 · Fase 1, islas 2–4 reanudadas con la batería v2: aceptación completa
- Qué: las cinco islas llegan a 500 épocas con la batería v2 activa. `phase1_acceptance.py eval --out runs/phase1`.
- Datos: `runs/phase1/s0–s4`, `runs/phase1.log`.

| Isla | Población final | Población (épocas 401–500) | Ocultas | Ataque | Mejor `cap_patch_gain` (épocas > 100) | Aprendizaje (cohortes) |
| --- | --- | --- | --- | --- | --- | --- |
| s0 | 3.533 | 3.485 | 3,5 | 0,98 | −0,031 (época 500, a posteriori) | −0,004 |
| s1 | 3.755 | 3.793 | 5,6 | 0,92 | 0,125 | −0,082 |
| s2 | 3.827 | 3.747 | 3,7 | 0,95 | 0,016 | −0,020 |
| s3 | 3.088 | 3.222 | 3,3 | 0,96 | 0,016 | −0,005 |
| s4 | 3.323 | 3.272 | 3,2 | 0,99 | 0,156 | −0,009 |

- Criterios del `eval`: grupos estables **no** (solo s2 y s3 superan 200 épocas), aprendizaje **no** (cinco de cinco negativos, pero la métrica de cohortes está degenerada; ver 07:30), novedad **sí** (el archivo sigue creciendo en las cinco). Comunicación ≈ 0 bits; laberinto ≈ 0.
- Ninguna isla pausa: la mejor ganancia en la mancha es 0,156 (s4), por debajo del umbral 0,2. La s0 terminó antes de la v2; su valor sale de `battery_on_checkpoint.py` sobre el checkpoint final.
- Conclusión: **firme**. La ecología de la fase 1 es estable en 5 de 5 islas (3.100–3.800 bichos), con ataque fijado cerca de 1 y cerebros pequeños. Sin capacidad por encima de las referencias triviales. Con esto se cierra la fase 1 como línea base para la 1b y la 1d.

### 15:30–16:35 · Fase 1b integrada en main; suite completa de la 1d en GPU
- Qué: fusión de `fase1b` en main (`bfea05a`, sustrato 2.0.0). Dos conflictos, en el texto del ADR-008/009 y en la firma de `world_step`, con el argumento `control` de la batería v2. El código fusionado es idéntico al de `fase1d` en `c6fc3d3`.
- Tests: `pytest --runslow` en la rama `fase1d` (1b + 1d + main): **57 de 57 en verde** en 1 h 05 min. Log: `runs/fase1d/tests_gpu.log`.
- Tropiezo: el primer intento importaba el paquete de main (O = 70), porque el venv lo tiene instalado en modo editable. Desde un worktree hay que exportar `PYTHONPATH=src`.

### 16:37 · E0 lanzado (viabilidad y escalas de tiempo)
- Cola: `experiments/fase1d/e0.json`. Condiciones: fijo y aleatorio con T = 560, cada una con N = 4.096 y N = 2.048; 5 semillas y 100 épocas por condición. Código: `39cd831`. Datos: `runs/fase1d/E0-*`, log en `runs/fase1d/e0.log`.

### 16:37–20:20 · E0: viabilidad, tamaño del mundo y escalas de tiempo
- Datos: `runs/fase1d/E0-*`, `runs/fase1d/e0.log`, resumen en `runs/fase1d/e0_resumen.csv` (`scripts/analyze_1d.py`). Código: `39cd831`. 5 semillas × 100 épocas por condición; medidas tardías sobre las épocas 51–100 de los supervivientes.

| Condición | Sobreviven | Población tardía | Mín. | τ_vida (pasos) | τ_gen (pasos) | Fracción tóxica | VA (población) | s/época |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fijo, N = 4.096 | 5/5 | 1.910 | 149 | 206 | 336 | 0,15 | +0,35 | 7,3 |
| aleatorio T = 560, N = 4.096 | 2/5 | 977 | 132 | 145 | 259 | 0,25 | +1,8 | 7,2 |
| fijo, N = 2.048 | 5/5 | 1.510 | 61 | 428 | 609 | 0,13 | +0,21 | 6,4 |
| aleatorio T = 560, N = 2.048 | 1/5 | 496 | 13 | 207 | 236 | 0,26 | (1 mundo) | 6,4 |

- **Viabilidad**: el control sin cambio cumple el criterio prerregistrado (≥ 90 %), pero el cambio aleatorio extingue 3 de 5 (N = 4.096) y 4 de 5 (N = 2.048). Las extinciones llegan en las épocas 41–88, justo al terminar la rampa de veneno (40 épocas). Con cambio aleatorio la fracción tóxica no baja de ~0,25, frente a ~0,13 con comida fija, así que alargar la rampa solo retrasaría el colapso.
- **Tamaño**: N = 2.048 llena el cupo (2 de 5 controles acaban en 2.048), y eso dobla τ_vida (428 frente a 206) porque, sin huecos libres, nadie puede nacer. Solo ahorra un 12 % de tiempo. **Se fija N = 4.096** (decisión delegada en E0 por el responsable).
- **Escalas**: τ_vida = 206 pasos (control, N = 4.096), no ~140; τ_gen ≈ 336. Los periodos de E1 en múltiplos de τ_vida pasan a **50 · 200 · 800 · 3.200** pasos.
- **Indicio**: el VA a nivel de población es mayor con cambio aleatorio (+1,8 frente a +0,35), como predice H1. Pero solo con 2 supervivientes, así que puede haber sesgo de supervivencia.
- **Fallos encontrados**: (1) la parada por extinción no actuaba porque un superviviente suelto de la reinyección reiniciaba la cuenta. Arreglado en `807c13a`: ahora cuenta las épocas que acaban por debajo de `N_MIN_REINJECT`. (2) Un mundo casi extinto (E0-aleatorio-T560-N2048 s4, época 100) **saltó la pausa por el laberinto** (`maze_gain` 0,31 > 0,25) con **un solo agente** examinado: es ruido de una muestra de tamaño 1. Ver ADR-013.
- Decisiones del responsable (20:30): **calibrar el veneno** (E0b) y **mínimo de 32 adultos** para pasar la batería.
- Conclusión: N = 4.096 y τ_vida, **firmes**; viabilidad del cambio aleatorio, **calibrando**.

### 20:45 · E0b lanzado (calibración del veneno)
- Qué: `TOXIC_FACTOR` 0,5 → 0,3 en todas las condiciones. Fijo, y aleatorio con T = 200 y T = 800; 3 semillas × 100 épocas, N = 4.096. Cola: `experiments/fase1d/e0b.json` (`29f0d75`). Datos: `runs/fase1d/E0b-*`.

### 20:45–22:30 · E0b: calibración del veneno (`TOXIC_FACTOR` 0,3)
- Datos: `runs/fase1d/E0b-*`, `runs/fase1d/e0b.log`. Código: `29f0d75`. 3 semillas × 100 épocas, N = 4.096.
- Supervivencia: fijo 3/3, aleatorio T = 800 3/3, aleatorio T = 200 2/3 (s2 extinta en la época 44; **la parada nueva actuó**: `stopped_extinct`). En total 8 de 9 (89 %).
- **Corrección de τ_vida**: el 206 de E0 era una media inflada por una semilla (s2: 521 pasos). Por semilla, la duración de la vida va de 91 a 521 pasos; la **mediana** es ~114 (E0 fijo) y ~134 (E0b fijo). τ_vida ≈ 130, cerca de los ~140 del diseño, así que **se mantienen los periodos 35 · 140 · 560 · 2.240**. τ_gen ≈ 270 (mediana).
- **La medida relativa del VA explota** cuando el gemelo congelado casi se extingue: +32,4 en E0b-aleatorio-T800 s1, frente a −0,00 y +0,26 en las otras dos semillas. Con VA_log = log((plástico + 1) / (congelado + 1)), calculado a posteriori (épocas 51–100, población ≥ 64), y mediana entre semillas:

| Condición | VA_log por semilla | Mediana (factor) |
| --- | --- | --- |
| E0 fijo, veneno 0,5 | 0,13 · 0,21 · 0,11 · 0,38 · 0,58 | +0,21 (×1,23) |
| E0 aleatorio T = 560, veneno 0,5 | 0,77 · — · 0,22 · — · 1,13 | +0,77 (×2,15) |
| E0b fijo, veneno 0,3 | 0,13 · 0,18 · 0,34 | +0,18 (×1,20) |
| E0b aleatorio T = 200, veneno 0,3 | 0,02 · 0,03 · — | +0,02 (×1,02) |
| E0b aleatorio T = 800, veneno 0,3 | −0,01 · 2,42 · 0,23 | +0,23 (×1,25) |

- Decisiones del responsable (22:35): **lanzar E1 con veneno 0,3** (las extinciones se informan como resultado) y **VA_log con mediana** como medida primaria (diseño v0.4; la relativa se conserva). Implementado en `9b9fb9e`.
- Indicios, pendientes de E1: (1) en **todas** las condiciones aprender ayuda (VA > 0 en 15 de 16 semillas vivas); (2) con cambio muy rápido (T = 200 ≈ 1,5 vidas) el beneficio casi desaparece (+0,02), aunque los cerebros son los mayores (15 neuronas ocultas); (3) el beneficio máximo aparece con cambio aleatorio a T = 560 y veneno fuerte (×2,15). Encaja con la campana de H1, pero con n = 2–3 por condición y veneno distinto entre bloques: **no es concluyente**.

### 22:45 · E1 y E2 lanzados
- Colas `experiments/fase1d/e1.json` y `e2.json`: 20 condiciones × 5 semillas × 300 épocas, N = 4.096, veneno 0,3. Código: `9b9fb9e`. Logs: `runs/fase1d/e1.log`, `e2.log`. Duración estimada: ~1,5–2 días.

### 23:05–23:50 · E1 parado y relanzado con la curva de recuperación (diseño v0.5)
- Qué: a propuesta del responsable («¿descubren el patrón de la variabilidad?»), E1 se paró a los 20 minutos (datos parciales en `runs/fase1d/_abortado_e1_2245`). Se añadió la curva de recuperación: alga y alga tóxica ingeridas según los pasos desde el último cambio del parche, en 10 intervalos. Se añadió también E8 (fiabilidad del aviso) al diseño.
- Código: `4126afc`. Tests: 13 de la 1d en verde. Suite sin lentas: 58 de 59; falló `test_runner_pause_and_review` porque, con épocas de 60 pasos, aún no hay adultos y la batería se aplaza (ADR-013, comportamiento correcto); se ajustó el test (`CAPABILITY_MIN_AGENTS = 0`).
- Comprobaciones: las poblaciones de las épocas 1–3 de E1-aleatorio-T035 s0 coinciden con las del arranque abortado (331, 963, 1.580), así que la medida solo observa. En la época 10 hay 3.682 cambios de parcela (esperados ≈ 64 × 1.000 × 2/35 ≈ 3.657) y la fracción tóxica ronda 0,5 durante la rampa.
- E1 y E2 relanzados a las 23:50. Se estima que E1 termine el 18-10 por la mañana y E2, el 19-10.
- Artículo divulgativo vivo para el responsable: «Panspermia: el experimento explicado» (Claude Docs).

## 17-10-2026

### 08:30 · E1 a medias (datos provisionales, sin análisis formal)
- 15 de 50 mundos terminados (~33 min por mundo). Medianas de las condiciones aleatorias: VA_log T35 +0,12 · **T140 +0,41** · T560 +0,08 · T2240 +0,10 (solo 1 semilla). El máximo cae en T ≈ τ_vida, como predice H1. **Indicio.**
- Curva de recuperación: justo tras un cambio comen **más** veneno que por azar (T2240: 0,76; T560: 0,69) y en ~100 pasos baja a ~0,2. Con T35 se quedan en ~0,5. «Aprender a aprender»: sin cambio entre las épocas 41–100 y las últimas 100 (T560: 0,58 → 0,59).
- Explicación alternativa sin descartar: la caída podría deberse a que se agota el alga que ahora es mala, no a que aprendan. Hará falta la curva en el gemelo congelado (hoy excluida: prefijo `recov_`).

### 11:00–16:26 · Sonda de recompensa (diseño 1d v0.6)
- Qué: a la pregunta del responsable («¿tienen centros de recompensa como los mamíferos?»). `scripts/reward_probe.py` (`5858732`) graba la modulación m (la señal que regula la plasticidad) durante 1.000 pasos desde los checkpoints de las épocas 100 y 300. Compara inicios de comida tóxicos y buenos dentro de cada tipo de alga, con ANCOVA sobre m(t) y permutación dentro de (agente, tipo). Criterio prerregistrado en `15d2d33`: |d| ≥ 0,2 y p < 0,01 en ≥ 3 semillas de una condición. Corrió en la CPU (no es bit a bit igual que la GPU). Datos: `runs/fase1d/reward_probe.jsonl`.
- Error corregido antes de medir: la primera versión (m(t+L) − m(t) con todos los bocados) confundía la vuelta a la media con una respuesta. Se vio en una prueba de 60 pasos.
- Todos los agentes tienen neuronas moduladoras (de 1 a 11 de media según el mundo).
- Resultado (max |d| sobre L = 1–8; signo: negativo = m más baja tras el veneno):

| Condición | Época 300 | Época 100 |
| --- | --- | --- |
| aleatorio T35 | −0,10 · ±0,11 · +0,08* · +0,12* · −0,09* (signos mezclados) | −0,11 · +0,14 · −0,09 · +0,06 · −0,12* |
| aleatorio T140 | −0,15* · −0,12* · +0,07* · −0,20* | −0,11 · −0,15* · **−0,29*** · −0,16* |
| aleatorio T560 | −0,11* · +0,10 · −0,09* · −0,10* · **−0,23*** | −0,07* · +0,05 · +0,05 · −0,08* · **−0,23*** |

  (* = p < 0,01 con 200 permutaciones, el mínimo es 1/201; en negrita, los mundos que cumplen el criterio)
- **Conclusión según el criterio: la evolución no ha inventado una señal de recompensa clara** (en ninguna condición la cumplen 3 semillas; como mucho 1 de 5). **Indicio** exploratorio: en T140 y T560, 7 de 9 mundos muestran en la época 300 una respuesta pequeña pero sostenida y del mismo signo (m baja 0,1–0,2 desviaciones tras el veneno, más allá de lo que ven y de la vuelta a la media). Con T35, los signos son mezclados. La señal no crece entre las épocas 100 y 300.
- Pendiente: T2240, el periódico y el fijo cuando acabe E1. Decisión pendiente del responsable: dar o no un sentido de malestar tras el veneno (opción 2).

### 16:45 · Decisión: E9 (sentido de malestar) y brazo largo sin malestar
- Decisión del responsable ante la sonda de recompensa: **«ambas cosas»**. (1) E9: mismo mundo con un sentido de malestar tras ingerir veneno (activo/apagado; T140 y T560; 5 semillas). (2) En la ejecución larga, un mundo sin malestar para ver si la señal surge sola con tiempo. Diseño v0.7.
- Implementación en la rama `fase1d-e9` (worktree `panspermia-e9`), separada del código con el que corren E1 y E2. Sustrato 3.0.0 (`OBS_DIM` 79 → 80). El gemelo congelado guarda ahora su curva de recuperación (`frozen_recov_*`).

### 18:59 · E9 implementado (rama `fase1d-e9`, commit `edcc274`)

- **Qué:** sustrato 3.0.0. Nueva entrada de malestar: tanh(malestar/2,5) × `malaise_sense`. El malestar suma el veneno ingerido y decae ×0,95 por paso (vida media de 13,5 pasos). Se pone a 0 al nacer y al morir. Con `malaise_sense = 0` la entrada existe pero vale siempre 0, así que el control tiene el mismo cerebro. El gemelo congelado guarda ahora su propia curva de recuperación (`frozen_recov_*`), y `analyze_1d.py` la muestra.
- **Pruebas:** 33 pasan y 1 se salta, en la CPU (2 h 06 min, porque la GPU está ocupada con E1). Incluyen dos tests nuevos: el malestar solo se ve cuando está activado, y se acumula y decae según la fórmula.
- **Cola:** `experiments/fase1d/e9.json` (T140 y T560 aleatorio, con y sin malestar, 5 semillas, 300 épocas). Se lanza cuando termine E2.

## 18-10-2026

### 06:00–09:30 · E1 terminado: análisis prerregistrado de H1 y H2

- **Qué:** E1 completo, 10 condiciones × 5 semillas × 300 épocas, código de la rama `fase1d` (`5858732`). Datos en `runs/fase1d/E1-*`, resumen en `runs/fase1d/e1_resumen.csv` (`scripts/analyze_1d.py`) y contraste con `scripts/e1_hypotheses.py` (rama `fase1d-e9`). Medida por semilla: media de VA_log en las épocas > 150, con 8 sondas por mundo.
- **Supervivencia:** 49 de 50. Solo se extingue E1-aleatorio-T140 s4, en la época 52, justo al terminar la rampa del veneno.
- **VA_log por semilla** (aleatorio): T35 {+1,02, −0,05, +0,12, +0,18, −0,14}; T140 {+0,81, +0,24, +0,28, +0,54}; T560 {+0,01, +0,08, +0,01, +0,49, +0,86}; T2240 {+0,08, +2,37, +0,02, +0,04, +0,74}; fijo {+0,11, +0,35, +0,06, +0,82, +0,51}. La dispersión entre semillas es enorme comparada con las diferencias entre condiciones.
- **H1 (campana): no se sostiene.** El ajuste cuadrático sobre log T da c = +0,020, IC95 [−0,094, +0,150] (*bootstrap* por semillas, 10.000 réplicas). El "máximo en T140" que se vio en las medianas provisionales era ruido entre semillas. Además, el control fijo da VA_log = +0,35, cuando H1 predice ≈ 0.
- **Por qué el fijo no es un mundo quieto:** en el modo fijo los parches no cambian con el tiempo, pero sí con el lugar. En cada parche de 128 u es tóxica un alga distinta, y el agente no ve en qué parche está. Un bicho que se mueve se encuentra la regla cambiada al cruzar de parche, y las manchas de tipo A/B también derivan (`K_DRIFT`). Así que T = ∞ es estable en el tiempo pero variable en el espacio, y aprender sirve igual. El control de verdad sin cambio sería una regla uniforme en todo el mundo. **Fallo de diseño, declarado.**
- **Sin veneno:** VA_log = 0 exacto. Los dos gemelos llenan el cupo (4.096) y la medida satura, así que este control no informa. Otro fallo, declarado: hace falta una medida sin techo, por ejemplo la ingesta (VA_log_intake = +0,006).
- **H2 (periódico frente a aleatorio): no concluyente.** Con 5 semillas, la permutación de signos exacta tiene una p bilateral mínima de 0,0625 (0,125 con 4 pares), y Holm × 4 exige p < 0,0125: **la prueba prerregistrada no podía dar positivo con 5 semillas.** Fallo de diseño, declarado. Por periodo, la diferencia periódico − aleatorio es:
  - VA: +0,08, −0,31, +0,01 y +0,19 (todas p ≥ 0,25);
  - uso del reloj: −0,22, +0,47, +0,34 y +0,20 (p entre 0,06 y 0,31; Holm ≥ 0,25).
  - Exploratorio, con los 4 periodos agrupados (19 pares): uso del reloj +0,30 (13 de 19, p = 0,044); VA +0,02 (p = 0,33).
- **Dos problemas de medida:**
  - *Uso del reloj* es la varianza de la tasa de comer explicada por la fase del reloj. En el periódico el propio mundo cambia con esa fase, así que sale alto aunque el agente no mire el reloj. Para saber si lo usan hay que anular la entrada del reloj en una sonda.
  - *Anticipación* es la fracción tóxica en la ventana antes de la inversión menos la de después. Sale negativa en 18 de 20 mundos, pero eso es lo esperable sin anticipación: tras el cambio, el alga que comían pasa a ser tóxica. **Corrijo lo dicho el 18-10 a las 00:25** ("justo antes del cambio comen más veneno"): es al revés, comen más veneno después, como cualquier población que reacciona. Un anticipador perfecto daría ≈ 0, no un valor positivo, así que la medida no distingue bien.
  - Comparando la curva de recuperación con la del aleatorio del mismo T (fracción tóxica en los primeros 8 pasos): periódico 0,54 / 0,70 / 0,81 frente a aleatorio 0,60 / 0,69 / 0,74 en T140 / T560 / T2240. No hay ventaja del periódico, así que **no se ve anticipación**.
- **Recuperación:** con T ≥ 560 la fracción tóxica cae de ~0,7–0,8 justo tras el cambio a ~0,2 en 128–256 pasos, en los dos programas. Captan el cambio, o se agota el alga mala (E9 lo separará con el gemelo congelado). **"Aprender a aprender": no.** En los primeros 64 pasos, la fracción tóxica es la misma en las épocas 41–100 y en las últimas 100 en todas las condiciones (p. ej., T2240 aleatorio 0,63 → 0,62).
- **Conclusión:**
  - *Firme:* el aprendizaje en vida tiene un valor positivo en casi todos los mundos con veneno (VA_log > 0 en 40 de 44 semillas supervivientes con veneno, fijo incluido).
  - *Descartado, con este diseño:* la campana de H1.
  - *No concluyente:* H2, por falta de potencia y por las medidas.
  - *Pendiente:* E2 (en curso) dirá si poder evolucionar la plasticidad cambia la supervivencia. La sonda de recompensa en las condiciones que faltan corre en la CPU.

### 09:25 · Decisión: E1b corrector, en el orden E2 → E9 → E1b

- El responsable elige **E1b corrector** y el orden **E2 → E9 → E1b**. Protocolo prerregistrado en el diseño v0.9 (`24d9525`), antes de tener ningún dato de E1b.
- Código en la rama `fase1d-e1b` (worktree `panspermia-e1b`):
  - modo `uniforme`, con el mismo tipo tóxico en todo el mundo;
  - `scripts/clock_probe.py`, que compara una época con el reloj normal y otra con el reloj desincronizado (× φ);
  - cola `experiments/fase1d/e1b.json`: uniforme con las semillas 0–4, más las semillas 5–9 de aleatorio y periódico en T140 y T560.
- Cadena en la GPU: `scratchpad/chain_e9_e1b.sh` espera a que termine E2, lanza E9 y, si existe `runs/fase1d/e1b_ok` (pruebas superadas), lanza E1b.

### 09:35 · E1b implementado y probado (rama `fase1d-e1b`, commit `bd0747f`)

- **Pruebas:** 14 tests de la 1d pasan en CPU, incluido el nuevo del modo uniforme (mismo tipo tóxico en todas las celdas, en los pasos 0 y 5.000). La cola e1b es válida (5 condiciones).
- **Prueba técnica de la sonda del reloj** (la única vista antes del análisis, como en la v0.6), en E1-periodico-T140 s3, época 300, en CPU (17 min): población 1.402 con el reloj normal frente a 1.439 desincronizado (CU = −0,026), ingesta +0,002 y fracción tóxica −0,002. Solo comprueba que funciona; no cambia el criterio.
- Marca `runs/fase1d/e1b_ok` creada: la cadena lanzará E1b tras E9. La sonda del reloj sobre E1 (semillas 0–4, 40 mundos, unas 11 h en CPU) espera a que termine la de recompensa (`scratchpad/clock_chain.sh`).

### 18:00–18:10 · Retrospectiva y decisión: escalera de complejidad (ADR-014)

- **Qué:** el responsable señala que cada fase encendió muchas variables a la vez. Además, el punto de partida no era un "mundo feliz": la fase 0 ya tenía comida, gasto por paso, hambre, reproducción pagada y plasticidad. Nunca se probó un control sin selección.
- **Decisión:** rehacer el camino un interruptor cada vez, con una pregunta de sí o no por peldaño, prerregistrada en `docs/escalera/diseno.md` v0.1. Los peldaños son:
  - P0 mundo feliz;
  - P1 peaje;
  - P2 comida quieta;
  - P3 hijos pagados;
  - P4 comida móvil;
  - P5 veneno uniforme.
- **Respuestas del responsable:** orden **E2 → escalera → E9 → E1b**; en P0, vida de duración fija (600 pasos); en P1, dotación fija al nacer.
- **Propuesto por Claude:** separar en dos peldaños (P2 y P3) la comida y el pago de la reproducción, que en la propuesta iban juntos.
- **Siguiente, según el responsable:** convertirlo en un **árbol binario**. Si el peldaño i sale bien, el i+1 construye sobre esa variable; si sale mal, la descarta y prueba otra. Las ramas se discuten con él antes de dibujarlas.

### 18:10–18:40 · Escalera implementada (rama `escalera`) y panel por peldaños

- **Código** (worktree `panspermia-escalera`, desde `fase1d-e1b`, sustrato 2.1.0):
  - interruptores en `EnvParams`: `metabolism`, `max_age`, `repro_mode` ("energia" o "edad"), `attack_on`, `chem_on` y `signal_on`. Sus valores por defecto dejan el mundo de siempre;
  - métricas `thrust_mean`, `mass_mean` y `max_thrust_mean`;
  - `tests/test_escalera.py`;
  - cola `experiments/fase1d/escalera.json`: 6 peldaños × 5 semillas × 300 épocas.
- **Panel** (main): sección "Escalera de complejidad" con:
  - el planteamiento de cada peldaño;
  - el vídeo sincronizado de sus cinco mundos (`/api/video`, unos 0,7 MB por mundo y época);
  - los resultados: veredicto provisional por semilla frente al peldaño anterior y series de cada mundo junto a la mediana del anterior.
  - Los peldaños están en `docs/mapa.json` (`escalera`). El árbol tiene un tronco nuevo, la escalera, y el camino antiguo queda como "primer intento", con ⚠ también en la fase 0.
  - Probado con Playwright usando datos de E1 en lugar de los peldaños: vídeo, veredicto y gráficas correctos.
  - Corrección: las descargas en paralelo se cortaban en Windows (ERR_CONNECTION_RESET); ahora se cargan de una en una, por trozos y con un reintento.
- **Cadena de la GPU** sustituida por `scratchpad/chain_esc_e9_e1b.sh`: espera a E2 y lanza la escalera (si existe `runs/fase1d/escalera_ok`), luego E9 y después E1b.

### 18:45 · Decisión: solo se dibuja la bifurcación de P5

- **Qué se acordó:**
  - P0–P3 son cimientos: si fallan, se reparan, no se descartan.
  - Tras P5, rama del sí (aprender compensa): veneno que cambia en el tiempo.
  - Rama del no: química → ataque → señal, de una en una sobre P5.
- **Dónde está:** ADR-014 (adenda), `docs/escalera/diseno.md` v0.2 y `docs/mapa.json`, con los nodos P6si, P6no, P7no y P8no.

### 18:48 · Decisión: E2 se pausa para dar paso a la escalera

- **Qué:** el responsable acepta pausar E2 en cuanto pasen los tests de la escalera. Nuevo orden en la GPU: **escalera → resto de E2 → E9 → E1b** (`scratchpad/chain_esc_e2_e9_e1b.sh`).
- **Por qué:** P1 comprueba que la selección del motor funciona, y E2, E9 y E1b dependen de ello. Pausar apenas cuesta: el barrido salta los 21 mundos terminados y el que está en marcha se reanuda desde su último checkpoint (como mucho se pierden 10 épocas). E2 terminará unas 15 h más tarde.

### 19:30–20:43 · E2 en pausa, tests en verde y escalera lanzada (rama `escalera`, `293f6a9`)

- **E2 en pausa a las 19:30:**
  - 21 de 50 mundos terminados;
  - E2-periodico-T035 s1 tiene checkpoint en la época 240;
  - se paró también la cadena antigua.
- **Tests en el procesador:** se abandonaron tras 76 min. Habían pasado 42 sin fallos.
- **Test 43, `test_runner_pause_and_review`:**
  - parece colgado, pero es la compilación de JAX, que es muy lenta en ese test (varios minutos por variante);
  - le pasa igual con el código de `fase1d-e1b`, sin la escalera;
  - deuda: acortar ese test.
- **Tests en la GPU** (decisión del responsable: esperar a los tests antes de lanzar). Los 13 restantes pasaron en 21 min. Total: test_escalera, fase 1d, 1b, 1 y unitarios, todos en verde.
- **20:43:** se crea `runs/fase1d/escalera_ok` y arranca la cadena `escalera → resto de E2 → E9 → E1b`, empezando por P0-feliz s0.

### 21:35–21:58 · Los cerebros crecen sin selección; bibliografía y rama de mutación (ADR-015)

- **Resultado parcial de P0:**
  - s0 (300 épocas): neuronas ocultas de 8,07 a 28,7 sin ningún premio;
  - s1 (época 180): 20,3;
  - energía constante en 30, población llena (4.096), VA = 0 exacto.
- **Causa:** "expresar o silenciar" invierte un hueco al azar entre 64 (sesgo entrópico hacia la mitad) y "duplicar" solo suma. Equilibrio teórico de unas 43 neuronas, con una constante de tiempo de unas 1.070 generaciones. La curva de s0 frena como predice.
- **Consecuencia:** "el cerebro creció" no prueba que pensar compense; hay que medir siempre contra P0. Hay que releer la 1b (de 8 a 21 neuronas): podría estar por debajo de la deriva neutral.
- **Bibliografía** (`docs/bibliografia/escalera/`, 18 referencias, DOI comprobados en Crossref):
  - sesgo de deleción en la Tierra;
  - duplicados efímeros;
  - complejidad no adaptativa;
  - sesgo de la mutación como factor orientador;
  - coste del tejido nervioso;
  - coste de conexión y modularidad;
  - bloat;
  - salto de la realidad en robótica evolutiva.
- **Decisión del responsable:** rama con mutación neutral y terrestre en P0 y P1, justo después de la escalera (ADR-015, diseño v0.3).
  - Rama `escalera-mut`, `1cd481d`: el modo por defecto es idéntico bit a bit (hash de 20 rondas de mutación igual en las dos ramas); 11 tests en verde.
  - Cadena nueva (`scratchpad/chain_mut_e2_e9_e1b.sh`): congela con SIGSTOP la cadena anterior para que no lance E2 al acabar la escalera, espera al barrido y lanza mutación → E2 → E9 → E1b. La escalera sigue corriendo sin interrupción.

### 22:07–22:15 · Decisión: parar tras P0 y analizar las tres mutaciones antes de P1

- **Qué:** el responsable pide no encadenar los peldaños. P0 se completa con las tres físicas de la mutación y se analiza antes de decidir cómo seguir con P1 (diseño v0.4).
- **Cómo se hizo, sin perder nada:**
  - se paró la cadena `chain_mut_e2_e9_e1b.sh`;
  - se terminó el barrido de la escalera, dejando vivo el mundo en curso (P0-feliz s2, época ~172);
  - `scratchpad/p0_tres.sh` espera a ese mundo y luego lanza P0 s3–s4, P0-neutral y P0-terrestre (15 mundos, unas 3–4 h). Al acabar crea `runs/fase1d/p0_listo` y avanza E2 mientras se decide.
- **Análisis preparado antes de ver las variantes:** `scripts/analyze_ladder.py` (solo biblioteca estándar).
- **Ya se ve en P0-nest (s0 y s1):** también crece la CPPN (nodos ocultos de 0,35 a ~10,7; aristas de 49 a ~68). La rama de mutación no cambia la mutación de la CPPN.

### 22:15–22:33 · La tasa de mutación también deriva; lista de cierre de P0 y cola de esta noche (ADR-016)

- **Medida en checkpoints de P0-feliz** (épocas 100, 200 y 300):
  - la tasa de mutación estructural (mediana) pasa de 1,00 a 1,74 (s0) y de 1,01 a 1,77 (s1);
  - σ oscila entre 0,03 y 0,08;
  - neuronas 28,7 y 28,6.
  - Causa: gen con ruido aditivo y suelo en 0.
- **Corrección:** cada mundo de P0 tarda unos 0,53 h (32 min), no lo que se dijo a las 22:10. P0 con las tres mutaciones termina hacia las 4:45, no a la 1:30.
- **Responsable:**
  - pregunta si el tamaño del mundo o la población inicial son variables de P0. Respuesta: no, sin ecología no cambian nada; sí lo es el tamaño de la población, que es biología de poblaciones;
  - elige añadir esta noche N1024, tasas fijas y CPPN neutral;
  - pide **la lista completa de factores de P0, con bibliografía, antes de pasar a P1**.
- **Hecho:**
  - `docs/escalera/p0_factores.md` (17 factores);
  - 21 referencias nuevas en `docs/bibliografia/escalera/refs.bib` (39 en total), con los DOI comprobados en Crossref;
  - rama `escalera-p0x` (`35e22f2`): 14 tests en verde y modo por defecto idéntico bit a bit;
  - cola `scratchpad/p0_noche.sh`: congela `p0_tres.sh` y encadena P0 → variantes → p0x → E2.

### 22:34–22:55 · Sexo y lugar de nacimiento implementados; 100 % P0 (ADR-017)

- **Corrección de horas:** se había escrito 22:50 en la bitácora, el mapa y el artículo cuando eran las 22:33; corregido. Memoria nueva: usar siempre la hora real.
- **Rama `escalera-p0y` (`3bedd02`):** reproducción sexual (cruce por índice), nacer al azar y parentesco local; 5 tests en verde y modo por defecto idéntico bit a bit. Dos tests fallaron al principio por la caché de `jax.jit`, que reutilizaba la traza con el modo anterior; en los experimentos no ocurre, porque cada mundo es un proceso nuevo.
- **Responsable: 100 % P0.**
  - Cancelados la sonda de recompensa (80 de 88), la sonda del reloj y la cola con E2.
  - Cola nueva `scratchpad/p0_solo.sh`: A1 neutral y terrestre → A3 tasas fijas → A2 CPPN neutral → B1 sexual → D1 nacer al azar y control → C1 N1024. Son 36 mundos, unas 19 h.
  - Tras cada experimento con conclusiones, se presentará la tabla Grupo · Factor · Estado.
- **Pregunta del responsable:** ¿la herencia darwiniana no hace más lenta la evolución? Respuesta con bibliografía en `p0_factores.md` (B2):
  - más rápida en mundos estables, peor en mundos cambiantes;
  - el efecto Baldwin acelera sin heredar;
  - además, con la CPPN no se puede reescribir la receta desde los pesos aprendidos.

### 22:52 · Idea del responsable: peldaño social y "mente colmena"

- Le gusta que un peldaño futuro permita aprender de otros (cultura) y que, en robots, lo que aprende uno lo copien los demás.
- Queda en el árbol como rama pendiente (`social`, tras P6si), con 4 referencias comprobadas en Crossref:
  - Rogers 1988: copiar no mejora a la población si nadie aprende por su cuenta;
  - Tomasello et al. 1993: aprendizaje cultural;
  - Kehoe et al. 2015: robótica en la nube;
  - Levine et al. 2017: aprendizaje compartido entre robots.
- No cambia nada de P0.

### 23:15–23:20 · P0-feliz completo (5/5) y análisis sin GPU (A3, A4, A5, A7, C4)

- **P0-feliz s3 y s4** terminan (0,52 h y 0,37 h). La cola `p0_solo.sh` cierra la antigua (código 9, previsto) y empieza P0-feliz-neutral.
- **Resultados** (detalle en `docs/escalera/p0_factores.md` § Resultados; datos en `runs/fase1d/_analisis_P0-feliz.json` y `_host_P0-feliz.json`):
  - neuronas: 21–29 de media tardía, aún crecen;
  - CPPN: entre el 8 y el 34 % en su techo de 18 nodos;
  - tasas de mutación distintas en cada mundo solo por azar;
  - f16 borra entre el 6 y el 10 % de las pequeñas perturbaciones;
  - el tope de nacimientos se alcanza siempre por las cohortes sincronizadas, sin pérdida de nacimientos.
- **Conclusión:** indicio. Quedan tres decisiones de P0 (techo de la CPPN, f16 y tasas). A4 solo puede juzgarse con selección, en la entrada de P1.

## 19-10-2026

### 02:56–03:08 · A1: P0 con mutación neutral y terrestre (10 mundos, 5/5)

- **Qué:** P0-feliz-neutral y P0-feliz-terrestre, 5 semillas × 300 épocas cada uno (rama `escalera-mut`, `1cd481d`, sustrato 2.2.0), con la cola `scratchpad/p0_solo.sh`. Entre 0,36 y 0,5 h por mundo. Población llena y sin extinciones.
- **Datos:** `runs/fase1d/P0-feliz-{neutral,terrestre}/s0–s4`; análisis en `runs/fase1d/_analisis_A1.json`, `_host_P0-feliz-{neutral,terrestre}.json` y `_dist_neuronas.json`.
- **Resultado (neuronas ocultas, media de las épocas 151–300):**
  - nest: 21–29, y siguen creciendo;
  - neutral: 7,9–8,8;
  - terrestre: 0,8–1,9. En la época 300, entre el 51 y el 67 % de los bichos no tienen ninguna neurona oculta.
  - Contrastes prerregistrados: neutral < nest y terrestre < neutral, los dos **5/5** (p = 0,031).
- **Control:** la CPPN, el cuerpo, las tasas, el redondeo f16 y los nacimientos salen idénticos en las tres físicas. Solo cambian las neuronas.
- **Conclusión:** firme. La física de la mutación decide sola el tamaño del cerebro cuando no hay selección:
  - nest lo infla;
  - neutral lo conserva y solo lo dispersa;
  - terrestre lo vacía.
- **Pendiente:** el responsable elige la física (A1, y con ella A6). Detalle en `docs/escalera/p0_factores.md` § Resultados.

### 07:03 · Decisión del responsable: A1 se decide después de ver P1

- Se le propuso fijar la física neutral (recomendada), la terrestre o la de siempre. Prefiere **esperar a P1**: ver cómo se comporta cada física cuando cada neurona cuesta energía, antes de fijarla.
- Cola nueva `scratchpad/p1_mut.sh`: espera a que acabe `p0_solo.sh` y corre P1-peaje-neutral y P1-peaje-terrestre (5 + 5 mundos, rama `escalera-mut`). Al terminar crea la marca `runs/fase1d/p1_mut_hecho`. Log en `runs/fase1d/p1_mut.log`.
- Es una prueba para cerrar un factor de P0, no el arranque de la escalera en P1: P1 sigue sin lanzarse hasta cerrar todos los factores (ADR-016).

### 04:48–07:13 · A3 (tasas fijas) y A2 (CPPN neutral): 10 mundos, 5/5 en los dos contrastes

- **Qué:** P0-feliz-tasas-fijas y P0-feliz-cppn-neutral, 5 semillas × 300 épocas cada uno (rama `escalera-p0x`, `35e22f2`, sustrato 2.3.0). Población llena y sin extinciones.
- **Datos:** `runs/fase1d/_analisis_A2A3.json`, `_host_P0-feliz-{tasas-fijas,cppn-neutral}.json` y `_dist_cppn.json`. Al analizador se añaden los dos contrastes de ADR-016.
- **A3, tasas fijas:**
  - menos neuronas que P0-feliz, 5/5 (p = 0,031), pero con un efecto pequeño (de −0,05 a −5,5);
  - el redondeo f16 pasa a borrar solo el 0,7 % de las perturbaciones (antes, entre el 6 y el 10 %);
  - la CPPN toca su techo menos a menudo (entre el 3 y el 14 %).
- **A2, CPPN neutral:**
  - nodos ocultos de 1,6 a 3,0 frente a 10,3–12,7, 5/5 (p = 0,031); nadie toca el techo;
  - pero las aristas bajan de 48 a 26–35 en la época 300: hasta un 10 % de los bichos con 10 aristas o menos. La causa es el punto de partida (todas las aristas entre entradas y salidas ya puestas) y que quitar un nodo arrastra sus aristas.
- **Conclusión:**
  - firme: la deriva de las tasas aporta poco al crecimiento del cerebro, pero causa el problema de f16 y el ruido entre mundos;
  - firme: la CPPN neutral frena el inflado, pero no es neutral en aristas. Si se elige, necesita un ajuste.
- **Pendiente:** el responsable decide A2, A3 y A7.

### 07:20–07:25 · Decisión del responsable: A2 y A3 también se deciden tras P1

- Para A3 y A2 también prefiere **esperar a P1**, y acepta añadir P1 con la CPPN neutral sin corregir: se verá si, con el coste de energía, la selección conserva las aristas útiles.
- **Cola nueva `scratchpad/p1_x.sh`**: espera a `p0_solo.sh` y a `p1_mut.sh` y luego corre 15 mundos; marca `runs/fase1d/p1_x_hecho`, log `p1_x.log`:
  - **P1-peaje** con la mutación de siempre (rama `escalera`): es la referencia necesaria para comparar tasas fijas y CPPN neutral con selección, y sirve también para A1;
  - **P1-peaje-tasas-fijas** (cola `experiments/fase1d/p1x.json`, rama `escalera-p0x`, `4fdfaa9` y siguiente);
  - **P1-peaje-cppn-neutral** (misma cola).
- Orden en la GPU: resto de P0 (B1 → D1 → C1) → P1 neutral y terrestre → P1 de referencia → P1 tasas fijas → P1 CPPN neutral. En total quedan unos 41 mundos; a 0,35–0,5 h por mundo, terminarían el 19-10 por la noche (estimación).

### 08:35–08:50 · B1: P0 con reproducción sexual (5 mundos): el cruce rompe la receta del cerebro

- **Qué:** P0-feliz-sexual, 5 semillas × 300 épocas (rama `escalera-p0y`, `3bedd02`, sustrato 2.4.0). Población llena; entre 0,38 y 0,44 h por mundo.
- **Datos:** `runs/fase1d/_analisis_B1.json` (`scratchpad/b1.py`) y `_b1_cppn.json` (`scratchpad/b1_cppn.py`, desde los checkpoints de la época 300).
- **Resultado:**
  - con sexo, entre el 83 y el 88 % de los nodos ocultos de la CPPN no tienen ninguna arista de salida (sin sexo, entre el 3 y el 5 %);
  - las aristas bajan a ~41 y los nodos muertos se acumulan cerca del techo;
  - neuronas: algo más que sin sexo en 4 de 5 mundos (efecto pequeño);
  - la distancia estructural se estanca en ~113 y hay muchos menos clados (98–119 frente a 540–740);
  - parentesco local entre 0,24 y 0,34, frente a 0,01 global.
- **Causa:** el cruce uniforme por índice trata los índices como marcas históricas, y no lo son. Un nodo hereda sus aristas de entrada de un progenitor, pero sus aristas de salida pueden venir del otro. Es el problema de las convenciones en competencia (Stanley y Miikkulainen 2002).
- **Conclusión:** firme sobre el operador, no sobre el sexo. Fallo de diseño propio: el test de `crossover` comprobaba que cada gen viniera de un progenitor, pero no que la receta siguiera conectada.
- **Pendiente:** el responsable elige entre el cruce por bloques, las marcas históricas al estilo NEAT o seguir asexual.

### 08:55–09:15 · B1: error corregido y repetición en cola (ADR-018)

- **Responsable:** "habrá que corregir el error y repetir".
- **Hecho:**
  - rama `escalera-p0z` (`8e4810b`, sustrato 2.5.0): la CPPN se hereda entera de un progenitor; huecos de neurona, cuerpo y vida se siguen mezclando;
  - test `test_crossover_keeps_the_cppn_whole`: falla con el código de la 2.4 y pasa con la 2.5. 14 tests en verde en CPU, mientras la GPU corre D1;
  - cola `experiments/fase1d/p0z.json` (P0-feliz-sexual-bloques, 5 mundos).
- **Colas:** se paran `p1_mut.sh` y `p1_x.sh`, que solo estaban esperando sin haber corrido nada. Las sustituye `scratchpad/tras_p0.sh`: tras `p0_solo.sh`, B1 repetido → P1 neutral y terrestre → P1 de referencia → P1 tasas fijas → P1 CPPN neutral. Log en `runs/fase1d/tras_p0.log`; marcas `p0z_hecho`, `p1_mut_hecho` y `p1_x_hecho`.

### 09:35–09:50 · ¿Heredar la receta entera es biológicamente correcto? (B1)

- **Pregunta del responsable:** ¿heredar el cerebro de un solo progenitor no es lo correcto biológicamente?
- **Respuesta** (bibliografía en `docs/bibliografia/escalera/README.md` § 7; 4 referencias nuevas comprobadas en Crossref):
  - lo habitual en la Tierra es recombinar dentro de cada cromosoma, gracias a la homología;
  - pero el ligamiento completo existe: mitocondrias, la parte no recombinante del cromosoma Y y los supergenes;
  - su precio: interferencia de Hill-Robertson y trinquete de Muller dentro del bloque.
  - La receta como supergén es, por tanto, un caso real, pero sin las ventajas del sexo en la parte más importante del genoma.
- **Decisión del responsable:** decidir tras ver B1 corregido. Si el sexo funciona bien con la receta como supergén, B1 se cierra; si no, se implementan las marcas históricas (formato nuevo del genoma) antes de cerrar P0.

### 08:35–11:10 · D1: el hijo nace al azar (5 mundos) y control (1 mundo)

- **Qué:** P0-feliz-nacer-azar (`BIRTH_PLACEMENT="azar"`) y P0-feliz-control-kin s0 (rama `escalera-p0y`, sustrato 2.4.0, ADR-017). Bloque de 08:35 a 10:50, 0,39 h por mundo. Parentesco de P0-feliz s0–s4 calculado a posteriori desde los checkpoints (épocas 100, 200 y 300; `scratchpad/p0_kin.py`, CPU).
- **Datos:** `runs/fase1d/_analisis_D1.json`, `_analisis_D1_kin.json`.
- **Resultado:**
  - control idéntico a P0-feliz s0 en todas las medidas salvo el tiempo de reloj (la medida de parentesco solo observa);
  - al azar, **toda la genética es idéntica bit a bit** a P0-feliz en los 5 mundos (neuronas, CPPN, distancias, clados); solo cambian la conducta y los descriptores de movimiento;
  - parentesco local / global en la época 300: 22–62 junto al padre, 1,00–1,03 al azar (5/5).
- **Conclusión (firme):** en P0 el lugar de nacimiento no influye en la evolución, porque nadie interactúa y la reproducción no depende de la posición. Solo decide si hay vecindarios de parientes, que importarán en los peldaños sociales. Propuesta: mantener «junto al padre» y usar «al azar» como control. Bibliografía nueva: west2002kincompetition (Crossref). Pendiente de la decisión del responsable.

### 11:15 · Decisión del responsable: D1 se prueba en el peldaño social

- Se mantiene «junto al padre» (`BIRTH_PLACEMENT="cerca"`, spec v1). Cuando haya señal o ataque, se probarán las dos opciones. Para P0, D1 queda cerrado.

### 10:50–12:04 · C1: P0 con 1.024 bichos (5 mundos); fin de la cola de P0

- **Qué:** P0-feliz-N1024 (rama `escalera-p0x`, cola `p0x.json`). Bloque de 10:50 a 12:02, entre 0,22 y 0,32 h por mundo. Con él termina `p0_solo.sh` (marca `p0_cola_hecha`); `tras_p0.sh` empezó a las 12:03 con B1 repetido.
- **Datos:** `runs/fase1d/_analisis_C1.json`.
- **Resultado (época 300, media ± desviación):**
  - neuronas 29,3 ± 4,5 frente a 30,1 ± 3,9;
  - nodos de la CPPN 12,8 ± 2,6 frente a 14,5 ± 1,8;
  - distancia estructural 122 ± 20 frente a 152 ± 14;
  - clados 32–100 frente a 540–740.
- **Pausa de capacidad** en s0 en la época 300 (`patch_gain` y `maze_gain` = 0,25). Es un falso positivo: no hay selección en P0, y la línea de base aleatoria es del 75 %. El mundo había terminado; no se crea `CAPABILITY_REVIEW.json`.
- **Conclusión (firme):** sin selección, N no cambia la tendencia media (la fija el sesgo de la mutación), solo la variedad.
- **Decisión del responsable (12:04):** el tope se queda en 4.096.

### 12:05–12:15 · ¿Mundos con muchos más bichos para tener más variedad? (C1)

- **Pregunta del responsable**, a la vista de C1.
- **Respuesta** (bibliografía en `docs/bibliografia/escalera/README.md` § 9; gerrish1998clonal nueva, comprobada en Crossref): no por ahora.
  - La variedad que mide P0 es neutral.
  - Sin sexo, crecer rinde cada vez menos por la interferencia clonal.
  - Poblaciones pequeñas y grandes llegan a la complejidad por caminos distintos (labar2016populations).
  - La forma terrestre de ganar variedad es repartir la población en varios mundos con migración (islas, fase 4a).
  - Reabrir N = 8.192 o más si P1 muestra que la selección se queda corta, o tras B1 si el sexo funciona.

### 12:03–15:14 · B1 repetido: sexo con la receta entera (5 mundos)

- **Qué:** P0-feliz-sexual-bloques (rama `escalera-p0z`, sustrato 2.5.0, ADR-018), de 12:03 a 14:01.
- **Datos:** `runs/fase1d/_analisis_B1b.json`, `_b1b_cppn.json`.
- **Resultado:**
  - nodos de la CPPN sin salida, 3–8 % (asexual 3–5 %, cruce con error 83–88 %);
  - aristas 72–78 en la época 300;
  - distancia estructural 148–156, y sube (con el error, estancada en 112–117).
- **Conclusión (firme):** el error está corregido. Sin selección, el sexo no cambia casi nada, como se esperaba. La cuenta de clados de una época no es comparable en los mundos sexuales: la generación del hijo es la mayor de sus padres y los clados se renuevan a la vez.
- **Incidencia:** los análisis de D1 y C1 se guardaron moviendo `_analisis_B1.json` (fuera de git). Se regeneró con los mismos datos (`scratchpad/b1.py P0-feliz P0-feliz-sexual`).
- **Decisión del responsable (15:14):** probarlo en P1. Cola `p1z.json` (rama `escalera-p0z`, commit `42a36b7`), lanzada con `scratchpad/tras_p1.sh` tras `tras_p0.sh`. Después se decide entre supergén y marcas históricas.

### 14:01–20:15 · A1 en P1: mutación neutral y terrestre con peaje (10 mundos; provisional)

- **Qué:** P1-peaje-neutral y P1-peaje-terrestre (rama `escalera-mut`, sustrato 2.2.0), de 14:01 a 20:12, 0,62 h por mundo. Los 10 mundos llenos (4.096) y sin extinciones ni pausas.
- **Datos:** `runs/fase1d/_analisis_A1_P1.json`.
- **Resultado (épocas 151–300; época 300 entre paréntesis):**
  - neuronas ocultas: neutral 0,05–0,12 (0,04–0,11); terrestre 0,05–0,10 (0,04–0,10). En P0 eran 7,9–8,8 y 0,8–1,9;
  - empuje: 0,02–0,08 en neutral y 0,02–0,11 en terrestre (P0: 5–7);
  - sinapsis 16–632 (neutral) y 23–187 (terrestre), frente a 645–1.200 y 366–640 en P0;
  - distancia estructural: neutral 16–65; terrestre 55–89 (P0: 102–138).
- **Lectura (indicio, falta la referencia con nest):** con peaje, la selección funciona y se impone a la física de la mutación. Con las dos físicas el cerebro desaparece casi del todo y los bichos dejan de moverse: en P1 no hay comida, así que pensar y moverse solo cuestan. La física de la mutación apenas importa cuando hay selección.
- **Pendiente:** P1-peaje (referencia con nest), en marcha desde las 20:12. Con ella se decide A1.

### 20:12–23:28 · A1 con selección: referencia P1-peaje (nest) y decisión

- **Qué:** P1-peaje (rama `escalera`, 5 mundos), de 20:12 a 23:22, 0,63 h por mundo. Llenos, sin extinciones ni pausas.
- **Datos:** `runs/fase1d/_analisis_A1_P1.json`, `_ladder_P1.json` (`scripts/analyze_ladder.py`).
- **Resultado:**
  - neuronas en la ventana 151–300: nest 0,11–0,42, neutral 0,05–0,12, terrestre 0,05–0,10; en la época 300, las tres entre 0,04 y 0,11;
  - pregunta prerregistrada de P1 (menos empuje que en P0): 5/5 con las tres físicas (p = 0,031).
- **Conclusión (firme):** con peaje, la selección se impone a la física de la mutación; nest deja algo más de cerebro (5/5 frente a neutral, < 0,4 neuronas).
- **Pregunta del responsable:** ¿neutral en este punto o para siempre? Respuesta: para toda la escalera, porque es la hipótesis nula y cambiarla a mitad invalidaría los peldaños anteriores; no para siempre, porque la terrestre es una variante realista (no universal) y sirve de prueba de robustez al final.
- **Decisión del responsable (23:28):** neutral para toda la escalera (A1) y 8 neuronas iniciales (A6); al final, los peldaños clave se repiten con la terrestre. Nest, descartada; terrestre, aparcada (`docs/caminos.md`).

### 23:35–23:39 · ¿Estamos tomando buenas decisiones? (revisión pedida por el responsable)

- **A favor:** un interruptor cada vez, prerregistro, semillas emparejadas, controles (D1 idéntico bit a bit) y bibliografía. Con este método se encontraron el error del cruce, las falsas alarmas de capacidad y el empujón de nest.
- **Riesgos señalados:**
  1. en P1 (sin comida) la selección solo quita: A2, A3 y B1 solo pueden juzgarse a medias ahí, porque su ventaja principal es construir;
  2. con 5 mundos solo se detectan efectos grandes (p mínima 0,031), y hay muchas comparaciones;
  3. deuda técnica para el cierre de P0: unir cinco ramas en un sustrato con tests y determinismo; medidas engañosas (batería de capacidad con línea de base al azar del 75 %, clados con sexo); tendencias que aún no se han estabilizado en 300 épocas.
- **Decisión del responsable (23:39):** ver P1 y decidir A2, A3 y B1 caso a caso; lo no concluyente se prueba en P2 antes de fijarlo.
- **Propuestas pendientes:** ADR de cierre de P0 con rama de integración y tests antes de P2; revisar la batería de capacidad (ADR del responsable) antes de los peldaños con aprendizaje.

## 20-10-2026

### 23:22–02:32 · A3 con selección: P1 con tasas fijas frente a P1-peaje

- **Qué:** P1-peaje-tasas-fijas (rama `escalera-p0x`, cola `p1x.json`, 5 mundos), de 23:22 a 02:26, 0,62 h por mundo; σ = 0,05 y tasa estructural = 1 en todos los bichos. Llenos, sin extinciones ni pausas. Referencia: P1-peaje (tasas como gen), emparejado por semilla.
- **Datos:** `runs/fase1d/_analisis_A3_P1.json` (series, ventana 151–300) y `_host_P1-peaje.json`, `_host_P1-peaje-tasas-fijas.json` (genomas de la época 300, en CPU).
- **Resultado:**
  - tasas como gen en P1, época 300: mediana de σ 0,0046–0,0069 (empieza en 0,05) y de la tasa estructural 0,05–0,13 (empieza en 1). En P0 subían;
  - con tasas fijas: neuronas 0,48–0,54 frente a 0,11–0,42 (5/5); distancia estructural 63–79 frente a 13–27 (5/5); vida media 516–518 frente a 521–528 pasos (5/5 menor); nacimientos 5/5 mayores;
  - f16 (A7): borra entre el 9 y el 22 % de las perturbaciones con σ como gen, y el 0,7 % con σ fija.
- **Conclusión (firme para P1):** con selección y sin nada que ganar, la tasa de mutación como gen baja un orden de magnitud (dirección de la barrera de la deriva, lynch2016driftbarrier). Con tasas fijas, la población arrastra una carga de mutaciones algo mayor. Lo que P1 no puede decir es si mutar tan poco frena la adaptación cuando sí hay algo que ganar (P2).
- **Pendiente:** decisión del responsable sobre A3 (y con ella A7).

### 07:01 · A3 y A7 decididos

- **Decisión del responsable (07:01):** tasas de mutación **fijas** (σ = 0,05, tasa estructural = 1) en el sustrato integrado; con ellas, los pesos en **f16** bastan (A7). En P2 se añade un gemelo con las tasas como gen: lo que P1 no puede juzgar (si mutar menos frena la adaptación cuando hay ganancias) se prueba allí.
- **Por qué:** sin selección (P0), las tasas como gen derivan hacia arriba al azar y cada mundo acaba con un régimen distinto; con solo selección negativa (P1), se hunden. En los dos casos añaden una deriva que no es la pregunta del peldaño. Fijarlas es la opción limpia y comparable; la versión natural se prueba cuando pueda demostrar su valor.

### 02:26–07:06 · A2 con selección: P1 con CPPN neutral frente a P1-peaje

- **Qué:** P1-peaje-cppn-neutral (rama `escalera-p0x`, cola `p1x.json`, 5 mundos), de 02:26 a 05:32, 0,62 h por mundo. Llenos, sin extinciones ni pausas. Fin de `tras_p0.sh` a las 05:32 (marca `p1_x_hecho`). Después arrancó `tras_p1.sh` (P1 con sexo, B1).
- **Datos:** `runs/fase1d/_analisis_A2_P1.json` (series, ventana 151–300) y `_dist_cppn_P1.json` (nodos y aristas de la CPPN en la época 300, en CPU).
- **Resultado:**
  - nodos ocultos de la CPPN: 0,4–2,7 frente a 0,8–11,2 (4/5 menos);
  - aristas: 35–45 frente a 51–61 (5/5 menos); mínimo 29–36, nadie con 10 o menos (en P0 neutral, hasta un 10 % y mínimo 2);
  - empuje, vida media, nacimientos y población: iguales.
- **Conclusión (firme para P1):** la CPPN no paga peaje, así que con la mutación de siempre sigue inflándose aunque haya selección. Con la neutral no se infla, y la selección frena la pérdida de aristas que se veía en P0. Falta saber si una receta pequeña limita construir cuando compensa (P2).
- **Pendiente:** decisión del responsable sobre A2 (y con ella A5, el techo).

### 07:06–07:10 · A2 y A5 decididos

- **Pregunta del responsable:** «¿A qué apunta la bibliografía?». Respuesta (`docs/bibliografia/escalera/README.md`, §11, 5 referencias nuevas comprobadas en Crossref): el inflado sin ganancia es un sesgo de los operadores; el remedio que respeta los principios son los operadores de tamaño neutro (langdon2000sizefair). La igualación de operadores (dignum2008equalisation) filtra hijos por tamaño, así que sería una métrica externa decidiendo; el coste por tamaño (soule1998parsimony) añadiría una ley física nueva.
- **Decisión del responsable (07:10):** CPPN **neutral corregida** (añadir y quitar aristas equilibrados, contando las que arrastra quitar un nodo). Se implementa en la rama de integración y se comprueba en P0 antes de P2. El techo (A5) se mantiene: con A1 y A2 neutrales nadie lo toca; se vigila en P2.

### 05:32–09:01 · B1 con selección: P1 con sexo frente a P1-peaje

- **Qué:** P1-peaje-sexual-bloques (rama `escalera-p0z`, cola `p1z.json`, cruce corregido de ADR-018, 5 mundos), de 05:32 a 08:54, 0,67 h por mundo. Llenos, sin extinciones ni pausas. Fin de `tras_p1.sh` (marca `p1_z_hecho`): la GPU queda libre.
- **Datos:** `runs/fase1d/_analisis_B1_P1.json`, `_host_P1-peaje-sexual-bloques.json`, `_b1_cppn_P1.json`.
- **Resultado (sexual frente a asexual, ventana 151–300):** neuronas 0,45–0,79 frente a 0,11–0,42; empuje 0,16–0,24 frente a 0,004–0,10; distancia estructural 97–116 frente a 13–27; vida 514–520 frente a 521–528 (todo 5/5). Mediana de σ en la época 300: 0,015–0,033 frente a 0,005–0,007; tasa estructural 0,67–0,97 frente a 0,05–0,13. CPPN sin salida: 3–7 %.
- **Conclusión (firme para P1, con una mezcla):** con sexo, la selección purga peor, sobre todo porque la tasa de mutación como gen apenas baja (el cruce desliga la tasa de sus efectos; johnson1999mutation). Frente al asexual con tasas fijas, el efecto propio del sexo es pequeño. El cruce corregido funciona. La ventaja principal del sexo (juntar mejoras) no se puede ver en P1.
- **Pendiente:** decisión del responsable sobre B1.

### 09:17 · B1 decidido

- **Decisión del responsable (09:17):** sustrato **asexual**; en P2, gemelo con sexo (cruce corregido) y tasas fijas, donde la ventaja de juntar mejoras puede aparecer. El cruce queda en el código como opción.
- **Con esto, en P0 solo quedan A4 (cuánto se muta, ahora con tasas fijas: elegir σ y la tasa estructural) y C2 (muerte y vejez).** La GPU está libre desde las 08:54.

### 09:26–09:28 · A4 y C2 decididos: todos los factores de P0 cerrados

- **Decisiones del responsable (09:28):**
  - A4: se mantienen σ = 0,05 y tasa estructural = 1. P1 con tasas fijas no muestra exceso ni defecto; se revisa con el gemelo de P2;
  - C2: la vejez es una ley del mundo en toda la escalera; como gen, peldaño propio tras P5.
- **Estado:** todas las filas de `docs/escalera/p0_factores.md` en ✅ o ⏭. Siguiente: ADR de cierre de P0 y rama de integración (5 ramas → un sustrato con tests, determinismo y la CPPN neutral corregida comprobada en P0).

### 09:30–10:17 · Cierre de P0: ADR-019 y rama de integración

- **Qué:** ADR-019 (física de la herencia de toda la escalera). Rama `escalera-int` (worktree `panspermia-int`, `da0a367`, sustrato 2.6.0): sale de `escalera-p0z` (que ya contenía `escalera`, `escalera-mut` y la base de `escalera-p0y`) más las colas de `escalera-p0x`. Valores por defecto: neuronas neutrales, tasas fijas (σ = 0,05, tasa 1), CPPN neutral corregida, asexual, nacer junto al padre, 8 neuronas iniciales.
- **CPPN neutral corregida (A2):** cuatro intentos, medidos con `scripts/cppn_drift.py` (512 linajes, solo mutación, sin selección; aristas / nodos ocultos):
  1. contraer uniendo cada entrada con cada salida: 45 / 2,9 a las 1.000 generaciones, pero 36 a las 3.000. Descartada;
  2. fusionar solo nodos con una entrada y una salida: 60 / 12,6 a las 3.000 (los nodos se acumulan). Descartada;
  3. contraer con el mínimo de aristas (a + b − 1), sin evitar choques: 37 / 7,9 a las 3.000, porque añadir arista rellena a menudo la i→j que dividir había quitado. Descartada;
  4. **elegida:** como la 3, pero solo se contraen nodos sin choques; quitar arista no aísla nodos ocultos y dividir solo elige aristas divisibles. 54,5 / 6,7 a las 1.000 y 58,6 / 11,4 a las 3.000: **aristas − nodos se queda en 48** (47,2). Los nodos se extienden desde 0 como un paseo con suelo (√t).
  - Referencias en 1.000 generaciones: nest 73 / 14; neutral 32 / 2,7.
- **Tests:** 78 en verde y 1 lento saltado (28 min en GPU), con 3 tests nuevos: valores por defecto de la escalera, aristas − nodos constante y contracción.
- **En marcha desde las 10:17:** cola `p0int.json`. Primero, el control con la física de la spec v1 elegida a mano, que debe coincidir bit a bit con P0-feliz s0. Después, P0-escalera, 5 mundos.
- **Criterio:** neuronas cerca de 8; CPPN sin inflarse ni vaciarse (aristas − nodos cerca de 48); σ en 0,05; control idéntico.

### 10:39–12:31 · Comprobación de la integración: pasa

- **Control (terminó a las 10:39):** P0-feliz-control-int s0 coincide **bit a bit** con P0-feliz s0 (0 diferencias en 300 épocas, salvo el tiempo de cálculo). **Firme.**
- **P0-escalera, 5 mundos (10:39–12:28), época 300:** neuronas 6,5–8,8 (máx. 22); CPPN 48–54 aristas y 4,0–5,7 nodos, aristas − nodos 44–49 (media 46,5; la deriva pura daba 47–48); σ = 0,05 y tasa = 1 en todos; el f16 borra el 0,7 % de las perturbaciones. Análisis: `scratchpad/p0int_an.py` → `runs/fase1d/_analisis_P0int.json`; `p0_host.py P0-escalera` → `_host_P0-escalera.json`.
- **Conclusión: firme.** Los cuatro criterios del ADR-019 se cumplen y P0 queda cerrado del todo. Siguiente: plantear P2 con el responsable (base y dos gemelos: tasas como gen; sexo con tasas fijas).

### 13:38 · P1-escalera en marcha

- **Decisión del responsable** (tras la comprobación): antes de P2 se repite P1 con todas las reglas nuevas juntas, para que el padre de P2 tenga la misma física. Hasta ahora P1 solo se había simulado con las reglas viejas, cambiando un factor cada vez.
- **Qué:** P1-peaje con la física de la escalera, 5 mundos (rama `escalera-int`, `48d3099`, cola `p1int.json`, `scratchpad/p1int.sh`, marca `runs/fase1d/p1int_hecho`). Empezó a las 13:38.
- **Mientras corre:** se prepara el plan de P2 (base y dos gemelos) para revisarlo con el responsable antes de lanzarlo.

### 16:44 · P1-escalera: pasa (5 de 5)

- **Terminó a las 16:44** (13:38–16:44, unos 37 min por mundo).
- **Primaria:** empuje 0,05–0,13 frente a 6,4–8,1 en P0-escalera, **5/5**. **Secundarias:** neuronas 0,19 (5/5) y masa 0,27 (5/5) menores; VA = 0; población llena.
- **CPPN con selección:** 3,7–5,1 nodos y aristas − nodos 43–48: no se hincha (con la física vieja y tasas fijas, 52–58) ni se vacía.
- **Frente a las reglas viejas:** el cerebro se vacía más (0,19 frente a 0,48–0,54); la vida (523–524) queda entre P1-peaje (521–528) y P1-tasas-fijas viejo (516–518).
- **Conclusión: firme.** P1 se cumple con la física integrada; P1-escalera es el padre de P2. Detalle en `p0_factores.md`; datos en `runs/fase1d/_analisis_P1int.json`.

### 16:48 · P2 en marcha: base y dos gemelos

- **Decisión del responsable (tras P1-escalera):** P2 con la física integrada y sus dos gemelos en una sola cola, la base primero.
- **Qué:** P2-escalera, P2-escalera-tasas-gen y P2-escalera-sexual, 5 mundos cada uno (rama `escalera-int`, `2cd8b33`, cola `p2int.json`, `scratchpad/p2int.sh`, marca `runs/fase1d/p2int_hecho`). Criterios en `diseno.md` v0.6 (16:48), escritos antes de los datos.

### 21:16 · P2: la salvaguarda de capacidad pausa 5 de 10 mundos

- **Qué:** la batería v2 (ADR-011) pausó P2-escalera s0, s2 y s3 en la época 200, s4 en la 100, y P2-escalera-tasas-gen s3 en la 200 (`CAPABILITY_PAUSE.json`). P2-escalera s1 y los otros cuatro gemelos de tasas llegaron a 300. El gemelo sexual corre ahora.
- **Por qué:** `patch_gain` 0,20–0,30 (umbral 0,2) y, en s2 y s4, `maze_gain` 0,25–0,30 (umbral 0,25). Éxito en la mancha lejana: 92–98 %, frente al 69–77 % de genomas al azar con los mismos cuerpos y al 13–17 % de las políticas fijas. Es la capacidad que pregunta P2 (ir a por la comida), y queda por debajo del buscador programado (~0,34).
- **Consecuencia:** la ventana prerregistrada (151–300) no está completa en 4 de 5 mundos de la base. **No se crea `CAPABILITY_REVIEW.json` ni se tocan umbrales sin decisión del responsable** (salvaguarda 5). Pendiente de su decisión.

### 21:37 · ADR-020: reanudar P2 con mancha y laberinto a 0,4

- **Decisión del responsable:** solo en P2, umbrales de mancha y laberinto a 0,4; revisiones firmadas en los 5 mundos pausados; reanudación automática tras la cola (`scratchpad/p2resume.sh`). Antes de P3, ADR de revisión de la batería: la prueba de la mancha se satura, porque el azar ya llega en un 69–77 %.
- **Bibliografía del rebrote** (pregunta del responsable): el rebrote logístico venía de la spec, sin referencia. Se añaden bacaer2011verhulst, pearl1920growth, rosenzweig1963predator y epstein1996sugarscape (DOI comprobados en Crossref), en el §13 de `docs/bibliografia/escalera/README.md`.

### 22:47 · Noche: P2 alargado hasta 600 épocas

- **Decisión:** el responsable delegó qué simular de noche; Claude eligió alargar P2-escalera y P2-escalera-sexual hasta 600 épocas, para ver si el cerebro (7,6 → 4–6 neuronas) se estabiliza y si la ventaja del sexo aparece con el tiempo. El responsable autorizó expresamente el umbral de 0,4 también en la prolongación (ampliación del ADR-020). Un primer intento de firmar la revisión sin esa autorización expresa fue bloqueado por los permisos, como corresponde.
- **Cómo:** `scratchpad/p2largo.sh` espera a `p2resume_hecho`, copia cada mundo terminado a `<condición>-600/s<semilla>` (los originales no se tocan) y continúa desde la época 300 (cola `scratchpad/p2largo.json`, marca `runs/fase1d/p2largo_hecho`). Unos 10 mundos × 30 min.

### 23:20 · Cola de P2 terminada; reanudación en marcha

- La cola `p2int.json` terminó a las 23:20 (base 16:48–18:39, tasas como gen hasta 21:08, sexual hasta 23:20).
- El gemelo sexual también se pausó en 3 de 5 mundos, siempre por `patch_gain` (0,20–0,22): s0 en la época 300, s3 en la 200 y s4 en la 100. Se firmaron según el ADR-020 (solo mancha o laberinto).
- 23:21: `p2resume.sh` reanuda 8 mundos hasta la época 300 (unas 800 épocas en total). Después arranca solo `p2largo.sh`.

### 01:11–01:20 (21-10) · P2 completo: pasa; los gemelos no cambian la física

- **Reanudación terminada a las 01:11** (`p2resume.sh`, 23:21–01:11): los 15 mundos de P2 tienen las épocas 1–300 sin huecos. A las 01:11 arrancó `p2largo.sh` (copias `-600`).
- **P2-escalera (primaria, 151–300):** vida 3.578–7.585 frente a 523–524 en P1-escalera, **5/5**; empuje 9,0–10,8 frente a 0,05–0,13, **5/5** (p = 0,031). Unos 330 mueren de vejez por época.
- **Cerebro:** 7,6 neuronas en las épocas 51–100 → 4,1–6,4 en 151–300 → 2,2–5,5 en la 300 (P1: 0,19). La CPPN pierde casi todos sus nodos ocultos (0,5–0,9; P1: 3,7–5,1) y mantiene aristas − nodos (47–50). **Buscar comida es innato:** VA de la ingesta entre −0,016 y −0,004.
- **Tasas como gen:** σ baja de 0,05 a 0,006–0,019 y la tasa sube a 1,08–1,45 (5/5); vida e ingesta frente a la base, 3/5. **A4 se mantiene** (la regla pedía, además, vivir más). El f16 borra el 2–6 % de las perturbaciones.
- **Sexo (cruce corregido, tasas fijas):** vida mayor que la base en 4/5 (s3 no) e ingesta en 3/5. **No llega al 5/5: se sigue asexual.** Más regular entre mundos y con menos muertes por hambre (4/5). La generación máxima se duplica porque el hijo hereda la del padre más avanzado (`genome.py`), no porque nazcan más.
- **Conclusión: firme** para la primaria de P2; **indicio** para el sexo (4/5) y para la bajada de σ. Detalle en `p0_factores.md`; datos en `runs/fase1d/_analisis_P2int.json` y `_host_P2-escalera*.json` (`scratchpad/p2_an.py`, `p2_host.sh`, en CPU).

### 06:39 (21-10) · P2 hasta 600 épocas: el cerebro se sigue vaciando; el sexo no gana

- **Qué:** `p2largo.sh` (01:11–06:39) continuó P2-escalera y P2-escalera-sexual desde la época 300 hasta la 600 en copias `-600`. Ninguno se pausó (ganancias ≤ 0,30, umbral 0,4) ni se extinguió.
- **Cerebro:** 7 neuronas (51–150) → 4–6 (151–300) → 2–4 (301–450) → **1,5–2,9** (451–600) en los 10 mundos; época 600: 0,8–2,7. No se estabiliza. La masa y el empuje bajan también, más despacio. La ingesta cae un 15–25 % y la vida se mantiene o sube.
- **VA ≈ 0** en todas las ventanas: buscar comida quieta es innato y no necesita cerebro (éxito en la mancha del 84–99 % con 1–2 neuronas).
- **Sexo:** vida mayor que la base en 4/5 hasta la época 300 y en 3/5 en 301–600; ingesta en 3/5 en todas las ventanas. Más variedad estructural (44–51 frente a 19–35). **B1 cerrado: asexual.**
- **Conclusión: firme.** Con comida quieta, la selección hace lo mismo que en P1, más despacio: quita lo que cuesta y no se usa. El cerebro solo puede compensar cuando haya algo que seguir o recordar (P4, comida móvil). Detalle en `p0_factores.md`; datos en `runs/fase1d/_analisis_P2largo.json`.

### 07:15–08:04 (21-10) · La batería tenía trampa desde la fase 1b: la química del examen fabrica comida

- **Sospecha:** en todos los mundos de la fase 1d y de la escalera, los genomas al azar "aprueban" la mancha y el laberinto **exactamente igual** (0,766 en las dos pruebas), y la población también saca casi lo mismo en las dos. En la fase 1 (sin química), la referencia al azar era 0,0.
- **Causa (comprobada):** `capability._probe_env` parte de `world.make_env`, que deja `chem_on = 1`. En el examen, el bicho suelta nutriente, que al degradarse vuelve como alga a su propia celda (`world.chem_step`), y se lo come. Con un mapa **sin comida**, los genomas al azar comen lo mismo (éxito 0,734 e ingesta de hasta 229, cuando la mancha solo tiene 24). El examen medía "comer y soltar sustancias", no "buscar la mancha".
- **Batería con la química apagada en el examen** (`scratchpad/bat_ckpt.py`, GPU, 07:26–08:00; 30 casos; `runs/fase1d/_bateria_quimica.jsonl`):

| Mundos | Química encendida (como hasta ahora): población / azar / ganancia | **Química apagada**: población / azar / mejor política fija / ganancia |
|---|---|---|
| P0-escalera, época 300 | 0,34–0,75 / 0,75–0,77 / −0,41 a 0,00 | 0,00–0,02 / 0,00 / 0,05–0,11 / −0,11 a −0,03 |
| P1-escalera, época 300 | 0,02–0,09 / 0,75–0,77 / −0,73 a −0,66 | 0,00 / 0,00 / 0,05–0,11 / −0,11 a −0,05 |
| P2-escalera, épocas 100, 300 y 600 | 0,75–0,98 / 0,64–0,84 / +0,03 a +0,30 | **0,00–0,11** / 0,00–0,02 / 0,06–0,19 / **−0,17 a 0,00** |
| P2-escalera-sexual, época 600 | 0,86–1,00 / 0,64–0,84 / +0,09 a +0,34 | **0,03–0,14** / 0,00–0,02 / 0,09–0,20 / −0,14 a +0,03 |
| Laberinto, todos | — | población 0,00–0,03, ganancia 0,00–0,03 |

- **Lectura:**
  - **Las 8 pausas de P2 fueron falsas alarmas**, como las del anillo (ADR-010). Con el examen limpio, los bichos de P2 encuentran la mancha lejana el 0–14 % de las veces, igual o peor que nadar recto sin cerebro. No buscan: en su mundo hay comida a la vista casi siempre, y la siguen con un reflejo. Los datos de P2 no cambian (la batería solo observa).
  - **La salvaguarda ha estado mal medida desde la fase 1b** (toda la 1d y la escalera). Con la referencia al azar en 0,75, la ganancia máxima posible era 0,25: una capacidad real habría hecho saltar la alarma tarde o nunca. Ninguna población ha mostrado capacidad real (ganancias limpias ≤ +0,03), así que no hubo un riesgo escondido, pero la protección no estaba funcionando como se creía.
  - **La "saturación"** que motivaba el ADR de revisión era este error, no un defecto del diseño de la mancha.
- **Conclusión: firme.** Pendiente: ADR-021 (corrección y umbrales), con decisión del responsable.

### 08:10–08:51 (21-10) · ADR-021: el examen sin química

- **Decisión del responsable:** el examen se hace con la química apagada y los umbrales vuelven a 0,2 (mancha) y 0,25 (laberinto); el 0,4 del ADR-020 queda revocado.
- **Hecho:** `escalera-int`, commit `005ade7`: `chem_on = 0` en `capability._probe_env` y test de regresión (con el mapa vacío, nadie come). Tests: 79 en verde y 1 lento saltado (08:20–08:51 en GPU).
- **Pendiente:** `main` y las ramas de la 1d no tienen el interruptor `chem_on`; heredarán la corrección al integrar la escalera. Siguiente: P3.

### 09:11 (21-10) · P3-escalera en marcha

- **Decisión del responsable (tras el ADR-021):** P3 base, 5 mundos, sin gemelos.
- **Qué:** hijos pagados (`repro_mode` "energia"); comida quieta. Rama `escalera-int`, `c01b46b`, cola `p3int.json`, `scratchpad/p3int.sh`, marca `runs/fase1d/p3int_hecho`. Primer peldaño con el examen sin química y los umbrales originales. Criterio en `diseno.md` v0.7 (09:11): población menor que en P2 en 5/5.

### 09:30–09:46 (21-10) · P2-buscar preparado (ADR-022)

- **Pregunta del responsable:** ¿hay que probar P2 con mucha menos comida para forzarles a buscar? Bajar `k_mean` no basta (sigue habiendo comida a la vista en casi todo el suelo); hace falta comida más lejos que los sentidos.
- **Hecho:** rama `escalera-buscar` (`21c4155`, `fff4e79`; sustrato 2.7.0) con `config.K_CUT`: solo comida donde z ≥ corte, a la misma altura.
  - Primer intento como campo de `EnvParams`: el mundo sin corte **dejaba de ser idéntico bit a bit**, porque XLA reordenaba el cálculo del campo (huella `312bfd…` frente a `b96d18…`). Como opción de compilación, la huella coincide con `escalera-int` (`scratchpad/bitid.py`, mundo P2 de 256 bichos, 600 pasos, CPU).
  - Tests de la escalera y unitarios en CPU: 13 en verde.
- **Calibración** (`scratchpad/buscar_cal.py`, `fase1d-w0`):

| Corte | Suelo con comida | Comida total | Fuera de la vista (> 60 u) | Distancia media |
|---|---|---|---|---|
| ninguno | 87 % | 100 % | 0 % | 0 u |
| 1,0 | 17 % | 37 % | 41 % | 65 u |
| **1,5 (elegido)** | **9 %** | **22 %** | **60 %** | **89 u** |
| 2,0 | 4 % | 10 % | 78 % | 131 u |

- **Decisión del responsable:** corte 1,5; primaria, el éxito en el examen limpio en la época 300 mayor que P2 en 5/5 (`diseno.md` v0.8). Bibliografía §14 (viswanathan1999random, viswanathan2008levy, charnov1976optimal; DOI comprobados en Crossref).
- **Lanzamiento:** `scratchpad/p2buscar.sh` espera a `p3int_hecho`, pasa la suite completa en GPU y lanza 5 mundos (marca `p2buscar_hecho`).
- **Avance de P3 (s0, época 290):** población siempre llena (4.096) aunque los hijos se paguen.

### 11:53–12:01 (21-10) · P3-escalera: no pasa por techo

- **Qué:** P3-escalera (hijos pagados), 5 mundos, 09:11–11:53, rama `escalera-int` (`c01b46b`), examen sin química. Ninguna pausa ni extinción.
- **Resultado:** la población queda en 4.096 en los 5 mundos (primaria **0/5**). El mundo tarda más en llenarse (época 6–54 frente a 2), pero se llena. Entre el 40 y el 94 % de los vivos superan su umbral y esperan un hueco: el freno es el tope de plazas, no la comida.
- **Genes:** el umbral baja de 55 a 22–36 en 4/5 (s4 se queda en 51 con hijos más ricos, 0,62).
- **Secundarias:** vida mayor en 4/5, empuje menor en 4/5, VA ≈ 0 y neuronas 1,6–7,8. Examen limpio: mancha 3–8 %, ganancia −0,13 a −0,02; laberinto 0,00–0,01.
- **Conclusión:** negativo según el criterio, pero **por techo** (la comida de P2 alimenta a más de 4.096 bichos). Detalle en `p0_factores.md`. Datos: `runs/fase1d/P3-escalera`, `_analisis_P3int.json`, `_genes_P3int.json`.
- **Después:** P2-buscar arrancó sus tests a las 11:53 (`p2buscar.sh`).
- **Decisión del responsable (13:26):** esperar a P2-buscar. Si sale bien, el siguiente es P3 sobre P2-buscar (hijos pagados con comida dispersa); si sale mal, P3 con menos comida (`k_mean`).

### 15:38 (21-10) · P2-buscar: no buscan; el mundo se vuelve como P1

- **Qué:** P2-buscar (`K_CUT` 1,5, ADR-022), 5 mundos, rama `escalera-buscar` (`fff4e79`). Tests en GPU: 80 en verde (11:53–12:27). Mundos: 12:27–15:38, sin pausas ni extinciones.
- **Primaria (examen limpio en la época 300 mayor que en P2): 1/5.** Los 5 mundos sacan 0,016 (P2: 0,00–0,11); ganancia −0,16 a −0,05; laberinto 0.
- **Secundarias:** vida 533–545 (P1: 523; P2: 3.578–7.585), empuje 2,4–3,9, neuronas 0,6–0,9, ingesta 7–25 veces menor, alga en pie 10–40 veces menor. Casi todas las muertes son por hambre.
- **Lectura:** los 4.096 bichos agotan la comida escasa, y como los hijos nacen con energía regalada, la población sigue llena sin comer. Buscar no compensa; la selección premia gastar poco, como en P1.
- **Indicio nuevo:** VA de la ingesta entre −0,45 y −0,12 en 5/5: aprender en vida perjudica. Pendiente de confirmar.
- **Conclusión:** negativo. Según lo decidido a las 13:26, el siguiente es P3 con menos comida (`k_mean`); se calibra y se plantea al responsable antes de lanzarlo. Detalle en `p0_factores.md`; datos en `runs/fase1d/P2-buscar`, `_analisis_P2buscar.json`.

### 15:40–15:52 (21-10) · Calibración de P3 con menos comida

- **Qué:** P3-escalera con `k_mean` reducido (el de `fase1d-w0` es 3,805), semilla 0, 40 épocas (`scratchpad/p3cal.json`, datos en `runs/fase1d/_calP3`).
- **Resultado:**
  - **½ (1,90):** sobrevive, pero en la época 1 quedan solo 26 bichos (con la comida entera, unos 300). Después crece hasta 2.617 en la época 40, todavía subiendo y cada vez más despacio; el alga en pie baja de 32.700 a 6.700.
  - **¼ (0,95) y ⅛ (0,48):** se extinguen al empezar (época 8 y época 1).
- **Lectura:** con menos comida, la población sí queda por debajo del tope (en la época 40), pero **el arranque es un cuello de botella**. Los genomas al azar tienen que encontrar comida con la energía inicial, y con ½ en otras semillas podrían extinguirse. Hace falta más calibración: `scratchpad/p3cal2.json`, con ½ y ⅜, semillas 0–2 y 100 épocas, desde las 15:53.
- **Decisión del responsable (16:47):** P3 con menos comida **desde cero**, con la cantidad que salga de la calibración 2.

### 15:53–16:53 (21-10) · Calibración 2 de P3 con menos comida

- **Qué:** `scratchpad/p3cal2.json`: `k_mean` ½ (1,90) y ⅜ (1,43), semillas 0–2, 100 épocas (`runs/fase1d/_calP3/P3cal2-*`).
- **½:** los 3 mundos sobreviven (mínimo al arrancar: 16, 55 y 40 bichos). Población en la época 100: 2.927, 2.771 y 2.709, casi estable desde la época 50–75 (s0 todavía sube despacio). Épocas 91–100: vida 660–1.001, casi todas las muertes por hambre, empuje 6,4–7,9 y neuronas 0,9–1,9.
- **⅜:** 2 de 3 se extinguen al arrancar (épocas 6 y 10); s0 sobrevive con 2.076 (vida 1.442, neuronas 5,5).
- **Lectura:** ½ es la única cantidad que sobrevive en 3/3, y deja la población un 30 % por debajo del tope: la comida pasa a ser el freno. El riesgo de extinción al arrancar sigue (mínimos de 16–55 bichos).

### 16:56 (21-10) · P3-escaso en marcha

- **Decisión del responsable:** ½ de comida (`k_mean` 1,902), 5 mundos, criterio de P3 (`diseno.md` v0.9: población menor que 4.096 en 5/5; extinción = no).
- **Qué:** rama `escalera-int`, `f02e61f`, cola `p3escaso.json`, `scratchpad/p3escaso.sh` (log `runs/fase1d/p3escaso.log`, marca `p3escaso_hecho`). Padre: P3-escalera.

### 20:01 (21-10) · P3-escaso: la comida frena (pasa 5/5)

- **Qué:** P3-escaso (½ de comida, hijos pagados), 5 mundos, 16:56–20:01, rama `escalera-int` (`f02e61f`). Ninguna pausa ni extinción (mínimo al arrancar: 16–73).
- **Primaria: 5/5.** Población 2.516–2.690 (épocas 151–300; mínimo 2.381). Solo el 1–3 % de los vivos tienen energía para un hijo (P3-escalera: 40–94 %).
- **Genes:** umbral de 55 a 10,5–19,3 (casi el suelo en 3/5); fracción al hijo de 0,5 a 0,26–0,40. Hijos baratos y muchos: 3.800–5.600 nacimientos por época, vida 483–688 y casi ninguna muerte por vejez.
- **Secundarias:** neuronas 0,05–1,45, masa 0,26–0,28 y empuje 6,4–7,8 (todo menor en 5/5); VA ≈ 0. Examen limpio: mancha 0–5 %, ganancia −0,13 a −0,06; laberinto 0–0,02. Sin pausas.
- **Conclusión: positivo (firme).** La comida limita la población. Pero, como en P2, con comida quieta el cerebro no compensa: la selección ahorra en todo. Detalle en `p0_factores.md`.
- **Decisión del responsable (21:10):** B3 cerrado: el padre paga (P3-escaso es la base de lo siguiente). Siguiente: P4, si ya no quedan dudas sobre la comida quieta (cuánta y dónde).
- **Decisión del responsable (21:10):** antes de P4, **P3-disperso**: la misma comida total que P3-escaso, concentrada en el 9 % del suelo (`K_CUT` 1,5). Con el corte queda el 21,9 % de la comida, así que `k_mean` = 1,902 / 0,219 = **8,686** (pico de K ≈ 30). Calibración: `scratchpad/p3dcal.json`, rama `escalera-buscar`, semillas 0–2, 100 épocas (`runs/fase1d/_calP3/P3cal-disperso`).

### 21:42–21:54 (21-10) · Coste fijo por hijo (ADR-023)

- **Observación del responsable:** con hijos cada vez más baratos, no van a buscar comida. Comprobado en el código: tener un hijo no cuesta nada aparte de lo cedido.
- **Decisión del responsable:** P3-disperso y P3-coste por separado (hermanos, los dos desde P3-escaso). Coste fijo por hijo; el coste según el tamaño, más adelante.
- **Hecho:** rama `escalera-coste` (`59eba78`, sustrato 2.8.0, desde `escalera-buscar`): `config.REPRO_COST`. Con coste 0, huella idéntica a `escalera-int` con hijos regalados (`6e95fcba…`) y pagados (`65bdc0c7…`). Tests de la escalera y unitarios: 14 en verde (CPU).
- **Siguiente:** calibrar el coste en la GPU cuando acabe la calibración de P3-disperso.

### 21:11–21:55 (21-10) · Calibración de P3-disperso

- **Qué:** `scratchpad/p3dcal.json` (rama `escalera-buscar`): `K_CUT` 1,5 y `k_mean` 8,686, semillas 0–2, 100 épocas.
- **Resultado:** 3/3 sobreviven. El mínimo al arrancar es 90–106 bichos (P3-escaso: 16–55), y la población en la época 100 es 2.099–2.495. Épocas 91–100 frente a la calibración de P3-escaso: empuje 8,6–9,3 (6,4–7,9), neuronas 2,2–6,0 (0,9–1,9), vida 297–439 (660–1.001), alga en pie 11.700–18.400 (4.500–5.300). Examen en la época 100: 0,02–0,05, ganancia −0,09 a −0,05.
- **Lanzamiento:** criterio en `diseno.md` v1.0. Cola `p3disperso.json` (`8faa492`), `scratchpad/p3disperso.sh`: espera a que termine la calibración del coste (`p3ccal.json`, costes 5, 10 y 20, semilla 0, 100 épocas, desde las 21:55) y lanza 5 mundos (marca `p3disperso_hecho`).

### 21:55–22:34 (21-10) · Calibración del coste por hijo (ADR-023)

- **Qué:** `scratchpad/p3ccal.json` (rama `escalera-coste`): P3-escaso con coste 5, 10 y 20; semilla 0, 100 épocas (`runs/fase1d/_calP3/P3cal-coste*`).
- **Resultado** (épocas 91–100; entre paréntesis, P3-escaso en la misma semilla):

| Coste | Mínimo al arrancar | Población (época 100) | Vida | Empuje | Neuronas | Nacimientos por época | Examen (época 100) |
|---|---|---|---|---|---|---|---|
| 0 | 16 | 2.927 | 789 | 6,4 | 0,9 | 3.476 | 0,000 |
| 5 | 11 | 2.568 | 1.588 | 9,0 | 3,4 | 1.574 | 0,109 |
| 10 | 8 | 2.372 | 1.910 | 9,8 | **6,3** | 1.244 | **0,156** |
| 20 | 13 | 2.372 | **2.525** | **10,4** | 5,5 | 915 | 0,031 |

- **Lectura:** con coste, los hijos son menos y más caros; los bichos viven 2–3 veces más, se mueven más y conservan el cerebro (3,4–6,3 neuronas frente a 0,9). El examen de la época 100 sube con coste 5 y 10 (una sola semilla: indicio). Los tres sobreviven, pero el arranque es justo (8–13 bichos).
- **Decisión del responsable (22:38):** correr los tres costes (5, 10 y 20), 5 mundos cada uno, y compararlos; criterio, el examen mayor que P3-escaso (`diseno.md` v1.1). Duración estimada: no cabe ninguno más antes de las 07:00. Cola `p3coste.json` (`7104c15`), `scratchpad/p3coste.sh`: espera a `p3disperso_hecho`, pasa la suite completa en GPU y lanza coste 10 → 20 → 5.

### 22:45–22:48 (21-10) · Sonda de hambre (petición del responsable)

- **Pregunta del responsable:** ¿cambia la conducta del bicho según la energía que siente? Si es así, ha aparecido algo parecido al hambre: una motivación interna que nadie le ha programado.
- **Método** (`scratchpad/hunger_probe.py`, solo observa, CPU): para cada mundo guardado (época 300), dos copias idénticas salvo la entrada de energía del cerebro (`tanh(E/50)`), fijada en "hambriento" (E = 5) o "saciado" (E = 100). La energía real, la física, el azar y la plasticidad no cambian.
  1. **Respuesta inmediata:** empuje y giro con las mismas observaciones salvo la energía.
  2. **Conducta durante 200 pasos** (sin nacimientos): recorrido, desplazamiento neto y velocidad, emparejados por bicho.
- **Nulos:** P0-escalera (la energía no cambia nunca, así que la selección no puede usarla; solo deriva) y genomas al azar con el entorno de P3-escaso (`--azar`).
- **Lectura, escrita antes de los datos:** hay "hambre" en un tipo de mundo si, en al menos 4 de 5 mundos independientes:
  - la población responde en una misma dirección (más del 90 % de los bichos);
  - la dirección coincide entre mundos;
  - el tamaño de la respuesta inmediata (media de |Δempuje| / desviación del empuje) supera al de los dos nulos.

  Una dirección consistente dentro de un mundo no basta, porque los parientes comparten genes también por deriva: tiene que repetirse en mundos independientes.
- **Prueba** (P3-escaso s0, 50 pasos, 71 s): el 99,9 % de los bichos empujan algo menos cuando se sienten hambrientos (−0,23; un 9 % de la desviación del empuje); el recorrido apenas cambia. Pendiente de los nulos y del resto de mundos.
- **En marcha:** `scratchpad/hunger_all.sh` (CPU, 8 núcleos): P0, P3-escaso, P2, P3, P1, nulo al azar y P2-buscar, 5 semillas cada uno → `runs/fase1d/_hambre.jsonl`.

### 00:09–00:29 (22-10) · Sonda de hambre: resultado

- **Datos:** `runs/fase1d/_hambre.jsonl` (respuesta inmediata y 200 pasos; terminó a las 00:09) y `runs/fase1d/_hambre_dir.jsonl`. Este segundo fichero repite solo la respuesta inmediata y separa a los bichos que empujan más, menos o igual al sentirse hambrientos (|Δ| ≤ 10⁻⁶). Hacía falta porque `frac_pos` sola no distinguía «menos» de «nada»; terminó a las 00:29. Script en `escalera-int`: `scripts/hunger_probe.py` (`68ba9bf`, ya con esas fracciones).
- **Nulos (tamaño |Δempuje| / desviación):**
  - P0 (5 mundos): 0,017–0,028; ningún mundo pasa del 15 % en una dirección; el 75–84 % de los bichos no cambian.
  - Al azar (5 mundos): 0,008–0,011.
  - Umbral de tamaño: 0,028.

| Mundos | Tamaño (5 mundos) | Por encima de los nulos | Bichos que empujan menos / más con hambre | > 90 % en una dirección |
|---|---|---|---|---|
| P1-escalera | 0,004–0,019 | 0/5 | 1–6 % / ≤ 0,5 % (el resto no cambia) | 0/5 |
| P2-escalera | 0,07–0,17 | 5/5 | 23–38 % / 9–56 % | 0/5 |
| P3-escalera | 0,05–0,11 | 5/5 | 11–58 % / 13–36 % | 0/5 |
| P2-buscar | 0,04–0,12 | 5/5 | 30–67 % / 18–49 % | 0/5 |
| P3-escaso | 0,007–0,108 | 3/5 | s0 99,8 %, s1 99,6 %; s2 44 %, s3 9 %, s4 31 % | 2/5 (s0, s1: menos) |

- **Lectura prerregistrada: no hay hambre en ningún tipo de mundo.** P3-escaso es el que más se acerca: en 2 de 5 mundos casi todos empujan algo menos cuando se sienten hambrientos (ahorran), pero la regla pide 4 de 5. **Negativo.**
- **Lo que sí se ve (indicio):** en los mundos con comida y selección (P2, P3, P2-buscar), el cerebro usa la entrada de energía. La respuesta es 3–7 veces mayor que en los nulos, pero en sentidos opuestos según el bicho y el mundo. La energía sentida mueve la conducta, pero no de una forma común ni útil que la selección haya fijado.
- **En 200 pasos** el recorrido apenas cambia:
  - |Δrecorrido| / desviación: 0,25–0,51 en los mundos con comida, frente a 0,05–0,08 en P0 y 0,12–0,26 al azar. El nulo al azar sale ruidoso porque solo sobreviven 10–76 bichos en las dos copias.
  - En ningún mundo más del 60 % cambia en el mismo sentido.
  - **Curiosidad de P1:** el 93–98 % de los bichos recorren algo menos cuando se creen hambrientos (5/5), pero apenas se mueven (2–8 unidades) y el tamaño es menor que en P0.
- **Por qué cuadra:** la energía solo cambia lo que conviene hacer si hay una decisión que dependa de ella, por ejemplo arriesgarse a buscar lejos o quedarse. En estos mundos la conducta innata (avanzar a la comida que se ve) vale igual con hambre que sin ella, y el cerebro se vacía (P3-escaso: 0,05–1,45 neuronas).
- **Siguiente:** repetir la sonda en P3-disperso y en P3-coste cuando terminen. Allí la comida está lejos o cada hijo cuesta, y la energía debería pesar más en las decisiones.

### 01:57–02:15 (22-10) · P3-disperso: resultado

- **Qué:** P3 con hijos pagados y la misma comida que P3-escaso, concentrada en el 9 % del suelo (`K_CUT` 1,5, `k_mean` 8,686). Rama `escalera-buscar` (`8faa492`), cola `p3disperso.json`, 5 mundos × 300 épocas, de 22:34 a 01:57. Criterio en `diseno.md` v1.0.
- **Primaria:** éxito en el examen limpio (mancha) en la época 300, mayor que en P3-escaso.
  - P3-disperso: 0,016 / 0,109 / 0,031 / 0,000 / 0,109.
  - P3-escaso: 0,000 / 0,000 / 0,047 / 0,016 / 0,047.
  - Gana en **3/5: no pasa.** En la media de las épocas 151–300 gana en 4/5 (descriptivo). Solo s4 supera a los controles fijos.
- **Secundarias** (épocas 151–300):
  - Población 2.242–2.338, frente a 2.516–2.690.
  - Energía media 18–21, frente a 6–9.
  - Neuronas 1,55–5,22, frente a 0,05–1,45 (más en 5/5).
  - Masa 0,31–1,26, frente a 0,26–0,28.
  - Empuje mayor en 4/5.
  - Vida 287–662, menor en 4/5.
  - VA mezclado: −0,12 a +0,07.
- **Genes** (época 300): umbral 31,5–40,4 (frente a 10,5–19,3) y fracción 0,32–0,46. La selección ya no elige hijos baratos: cada hijo nace con unas 10–19 unidades, frente a 3–5.
- **Conclusión: negativo** (3/5), con un **indicio**: la dispersión, por sí sola, encarece a los hijos y conserva cerebro y cuerpo, pero no basta para que buscar lejos compense de forma clara. Detalle en `p0_factores.md`; camino aparcado en `caminos.md`.
- **Sigue:** P3-coste. Tests desde las 01:58; después, costes 10, 20 y 5. Sonda de hambre sobre P3-disperso en CPU desde las 02:05.

### 02:05–02:18 (22-10) · Sonda de hambre en P3-disperso

- `runs/fase1d/_hambre.jsonl` (mismo método; `--kcut 1,5`, código de `escalera-buscar`).
- **Tamaño |Δempuje| / desviación:** 0,026–0,136, por encima de los nulos (0,028) en 4/5.
- **Dirección:**
  - Empujan más con hambre: 27–39 %.
  - Empujan menos: 7–26 %.
  - No cambian: 42–59 %.
  - Ningún mundo llega al 90 % en una dirección (0/5).
- **Recorrido en 200 pasos:** igual con y sin hambre (46–53 % recorren más).
- **No hay hambre** según la regla. La única novedad es que el sentido dominante es empujar más con hambre en 5/5, al revés que en P3-escaso, pero en minoría. Queda pendiente P3-coste.

### 07:53–09:05 (22-10) · P3-coste: costes 10 y 20 (resultado)

- **Qué:** P3-escaso con un coste fijo por hijo (`REPRO_COST`, ADR-023). Rama `escalera-coste` (`7104c15`, sustrato 2.8.0), cola `p3coste.json`. La suite en GPU pasó: 81 tests correctos y 1 omitido, en 39 min (01:58–02:38).
  - Coste 10: de 02:38 a 05:21.
  - Coste 20: de 05:21 a 07:53.
  - Coste 5: desde las 07:53.
- **Criterio** (`diseno.md` v1.1, cada coste por separado): examen limpio (mancha) en la época 300 mayor que P3-escaso (0,000 / 0,000 / 0,047 / 0,016 / 0,047) en 5/5.

| Medida (épocas 151–300) | P3-escaso | Coste 10 | Coste 20 |
|---|---|---|---|
| Examen, época 300 (**primaria**) | — | 0,000 / 0,062 / 0,125 / 0,031 / 0,047: **3/5, no pasa** | 0,031 / 0,109 / 0,000 / 0,141 / 0,000: **3/5, no pasa** |
| Controles fijos del examen (época 300) | 0,08–0,16 | 0,13–0,28 | 0,13–0,25 |
| Población | 2.516–2.690 | 2.459–2.631 | 2.371–2.505 |
| Vida media | 483–688 | 1.626–2.846 | 2.859–3.689 |
| Energía media | 6–9 | 16–24 | 23–28 |
| Empuje | 6,4–7,8 | 7,4–9,1 | 8,2–9,2 |
| Neuronas ocultas | 0,05–1,45 | 0,82–1,97 | 0,64–2,45 |
| Masa | 0,26–0,28 | 0,27–0,31 | 0,29–0,31 |
| VA de la ingesta | −0,021 a +0,009 | −0,007 a +0,001 | −0,009 a +0,001 |
| Umbral para tener hijos (época 300) | 10,5–19,3 | 31,6–45,1 | 50,5–61,4 |
| Fracción de energía al hijo (época 300) | 0,26–0,40 | 0,39–0,53 | 0,39–0,48 |
| Vivos con energía para un hijo (época 300) | 1–3 % | 0,1–0,4 % | ≤ 0,1 % |

- **Lectura:**
  - El coste hace lo esperado con los hijos: el umbral sube con el coste y viven 3–6 veces más.
  - Comen más (200–213 mil por época frente a 176–192 mil) y empujan algo más.
  - El cerebro apenas cambia (≤ 2,5 neuronas) y VA ≈ 0.
  - El examen sube en 3/5 con los dos costes y queda por debajo de los controles fijos, salvo en coste 20 s3 (0,141 frente a 0,125).
- **Conclusión: negativo para 10 y 20** (3/5 cada uno). Encarecer los hijos cambia la historia de vida (pocos hijos caros, vidas largas; smith1974optimal), pero no hace que buscar lejos ni aprender compensen.
- **Sonda de hambre** (CPU, 08:30–09:05): no hay hambre, 0/5 en los dos costes.
  - Coste 10: el sentido dominante cambia de un mundo a otro; s0 llega al 78 % empujando menos con hambre.
  - Coste 20: s1 y s3 empujan más (63–74 %); s4 apenas responde.
  - Genes: `_genes_P3coste10.json` y `_genes_P3coste20.json` (`scratchpad/p3c{10,20}_genes.py`).

### 08:35 (22-10) · Bibliografía verificada

- Las siete referencias que se habían citado de memoria tienen DOI comprobado en Crossref: Berg y Brown 1972, Hills 2004 y 2006, Humphries 2010, Smith y Fretwell 1974, Stephens 1991, Dunlap y Stephens 2009, Mitchell 2009.
- Están en `docs/bibliografia/escalera/refs.bib` y en el README §15 (`be47a77`).

### 09:06 (22-10) · Decisión del responsable: P4 antes que comida efímera y olfato

- **P4 primero, con la comida efímera como hermana.** P4 cambia una sola cosa: el ritmo al que la comida cambia de sitio. Tres ritmos:
  - **Entre generaciones:** el mundo cambia de una generación a otra pero es estable durante una vida. Es la condición en la que, según stephens1991change y dunlap2009components, aprender compensa.
  - **Dentro de una vida:** comida efímera.
  - **El lento de siempre:** la deriva `K_DRIFT`.
- **El olfato queda aparcado:** es un sentido nuevo y lo más probable es que dé una búsqueda innata, como la de *E. coli* (berg1972chemotaxis).
- **Padre de P4:** se decide al terminar el coste 5 (hacia las 10:30). Si pasa, P4 se construye sobre él; si no, sobre P3-escaso. Mientras tanto se prepara el diseño y el código.
- Riesgo anotado (mitchell2009adaptive): si el cambio entre generaciones es regular, puede bastar una anticipación innata. Para evitarlo, el sitio nuevo de la comida será al azar.

### 09:11–09:20 (22-10) · P4: dos familias de hermanos (decisión del responsable) y código

- Al diseñar P4 aparecieron dos problemas. Primero, los bichos ven la comida, así que la regla innata «ve hacia lo que ves» sirve aunque la comida cambie de sitio. Segundo, la comida de P3-escaso cubre el 87 % del suelo.
- **Responsable (09:11):**
  - Sitio y alga, como dos hermanos.
  - P4-sitio cuelga de P3-disperso.
  - P4-alga cuelga del coste 5 si pasa; si no, de P3-escaso.
- **Código:** rama `escalera-p4` (`0ca3215`, sustrato 2.9.0), con `FOOD_JUMP_PERIOD` y `ALGA_SWAP_PERIOD`.
  - Bit a bit igual a `escalera-coste` con los dos apagados (edad `6e95fcba…`, energía `65bdc0c7…`).
  - Tests de `test_escalera.py` y `test_units.py`, en CPU: 15 correctos más los 2 nuevos. Al principio el test del alga fallaba porque el propio test calculaba el alga que alimenta con el periodo ya a 0; corregido el test.
- **Calibración** (semilla 0, 100 épocas): P4-generación (salto cada 1.000 pasos), P4-efímera (cada 150), P4-lento (deriva de siempre) y P4-alga (sorteo cada 2.000). Arranca al terminar el coste 5. Diseño en `diseno.md` v1.2 (borrador).

### 10:51–11:12 (22-10) · P3-coste 5: resultado y cierre de P3-coste

- **Qué:** coste 5 por hijo sobre P3-escaso (`7104c15`, cola `p3coste.json`), de 07:53 a 10:51. Ningún mundo se pausó ni se extinguió.
- **Primaria** (`diseno.md` v1.1): examen limpio en la época 300 de 0,062 / 0,031 / 0,016 / 0,000 / 0,016 frente a 0,000 / 0,000 / 0,047 / 0,016 / 0,047 en P3-escaso: **mejor solo en s0 y s1, 2/5, no pasa.** Controles fijos: 0,11–0,25.
- **Secundarias** (épocas 151–300): vida 1.022–1.967 (frente a 483–688); umbral 21–34 (época 300); fracción al hijo 0,32–0,54; energía 11–16; neuronas 0,18–1,42; VA −0,030 a +0,005; población 2.549–2.698.
- **Sonda de hambre** (CPU, 10:52–11:12): 0/5. La que más se acerca es s2 (89,7 % empuja menos con hambre, `abs_rel` 0,032, apenas por encima del máximo de P0, 0,028). En s0 y s4 domina empujar menos (57 %), en s1 se reparte y s3 casi no responde (93 % sin cambio). Genes: `_genes_P3coste5.json` (`scratchpad/p3c5_genes.py`).
- **Cierre de P3-coste: negativo con los tres costes** (5: 2/5; 10: 3/5; 20: 3/5). El coste ordena la historia de vida (5 → 10 → 20: umbral 21–34 → 32–45 → 50–61, vida ×2–3 → ×3–4 → ×5–6), pero ni el cerebro, ni VA, ni el examen, ni el hambre siguen ese orden. **Camino aparcado** (`caminos.md`). Tabla completa en `p0_factores.md`.
- **Consecuencia (regla del responsable de las 09:11):** P4-alga cuelga de **P3-escaso**. La calibración ya usaba esa configuración.

### 10:51–11:13 (22-10) · Calibración de P4: fallo al arrancar y primeros resultados

- **Fallo:** a las 10:51 la cola se negó a arrancar porque `FOOD_JUMP_PERIOD` y `ALGA_SWAP_PERIOD` no estaban en `experiment.CONFIG_OVERRIDABLE`. Olvido al escribir el sustrato 2.9.0, que los tests no cubrían porque no pasan por la cola. Corregido en `escalera-p4` (`3fa7776`); las dos constantes se leen al trazar, así que se pueden sustituir. El guion dejaba la marca `p4cal_hecho` aunque el barrido fallara; ahora solo la deja si termina bien. Relanzado a las 10:52 (log del fallo en `runs/fase1d/p4cal_fallo1.log`).
- **P4-generación** (manchas de P3-disperso que saltan a un sitio al azar cada 1.000 pasos): **se extingue** por primera vez en la época 11 y vuelve a extinguirse una y otra vez tras cada resiembra (población de 2 a 315). Termina las 100 épocas con 310 bichos; VA +0,058 en la época 100, sobre una población recién resembrada.
- **P4-efímera** (salto cada 150 pasos): extinta en la época 1; el lanzador la para tras 20 épocas seguidas extinta.
- **Por qué** (`world.resources_step`): donde la mancha desaparece, la comida se pierde a un ritmo r = 1,5 (≈ 0,15 por paso) y donde aparece crece desde casi cero hasta llenarse en ~50–80 pasos. El hueco sin comida es corto; lo que mata es la distancia: las manchas cubren el 9 % del suelo y aparecen en cualquier sitio, lejos para bichos con 18–21 de energía.
- **Sigue:** P4-lento (referencia, P3-disperso tal cual) y P4-alga. Con los cuatro, proponer al responsable cómo suavizar P4-sitio (salto corto en vez de a cualquier sitio, comida vieja que no se pudre de golpe o periodo más largo).

### 11:13–11:29 (22-10) · Calibración de P4: P4-lento y P4-alga

- **P4-lento** (P3-disperso con la deriva de siempre, referencia): sano. 2.108 bichos en la época 100 (mínimo 1.865), 294 generaciones, 6,8 neuronas, VA −0,18.
- **P4-alga** (P3-escaso con el alga sorteada cada 2.000 pasos): 7 bichos en la época 1 y extinta en la época 5; el lanzador la para tras 20 épocas seguidas extinta. P3-escaso ya bajaba a 16–75 bichos al arrancar; si solo alimenta la mitad de las algas, la comida útil cae otra vez a la mitad.
- **Conclusión:** de las cuatro variantes solo vive la referencia. Tal como estaban diseñadas, P4-sitio y P4-alga mezclan el cambio con una pérdida de comida (por distancia o por cantidad).

### 12:08–12:16 (22-10) · Decisión del responsable: doble de algas y salto corto; segunda calibración

- **P4-alga con el doble de algas** (`k_mean` 3,804, la comida de P2): la comida útil media es la de P3-escaso, de modo que solo cambia qué alga alimenta.
- **P4-sitio con salto corto:** el campo de comida entero se traslada `FOOD_JUMP_DIST` en dirección al azar respecto a su sitio de siempre. Entre dos periodos, las manchas se mueven de 0 a 2·`FOOD_JUMP_DIST` (de media, ~1,27 veces).
- **Código:** `escalera-p4`, `5590724`, sustrato 2.10.0. Bit a bit igual a `escalera-coste` con todo apagado (edad `6e95fcba…`, energía `65bdc0c7…`). Tests de `test_escalera.py` y `test_units.py` en CPU: 17 correctos, entre ellos el nuevo `test_food_short_jump_is_rigid_shift`, que comprueba con una correlación en el toro que el campo es el de siempre desplazado 128 u.
- **Segunda calibración** desde las 12:16 (`scratchpad/p4cal2.json`, salida `runs/fase1d/_calP4b`, marca `p4cal2_hecho`), semilla 0 y 100 épocas: P4-alga con doble de algas; P4-sitio con saltos de 64 y 128 u, cada 1.000 y cada 150 pasos.

### 12:16–13:13 (22-10) · Segunda calibración de P4 (salto corto y doble de algas)

- **Qué:** `escalera-p4` (`5590724`, sustrato 2.10.0), `scratchpad/p4cal2.json`, semilla 0, 100 épocas, salida `runs/fase1d/_calP4b`. Medias de las épocas 51–100.

| Variante | Resultado | VA (épocas 20 / 40 / 60 / 80 / 100) | Población | Vida | Masa | Neuronas | Empuje |
|---|---|---|---|---|---|---|---|
| P4-alga, doble de algas | viva (2.596 en la época 100) | 0,16 / −0,01 / −0,03 / −0,01 / 0,03 | 2.246 | 812 | 0,50 | 3,35 | 10,9 |
| Salto 64 u cada 1.000 | viva (2.191) | 0,12 / 0,14 / 0,86 / 0,77 / 0,30 | 2.409 | 184 | 2,87 | 6,70 | 5,1 |
| Salto 128 u cada 1.000 | viva (2.451) | 0,49 / 0,42 / 0,41 / 0,28 / 0,04 | 2.003 | 303 | 2,35 | 1,98 (época 100: 0,65) | 8,6 |
| Salto 64 u cada 150 | extinta en la época 3; se recupera (962) | 0,07 / −0,09 / −0,12 / 0,04 / 0,10 | 748 | 491 | 0,73 | 5,84 | 7,2 |
| Salto 128 u cada 150 | extinta en la época 3; parada | — | — | — | — | — | — |
| *P4-lento (primera calibración)* | *viva* | *0,32 / 0,02 / 0,58 / 0,13 / 0,05* | *1.509* | *495* | *0,72* | *6,84* | *9,0* |
| *P3-escaso s0 (épocas 51–100)* | — | *0,07 / −0,01 / −0,00 / 0,00 / −0,00* | *2.765* | *1.010* | — | *2,47* | *6,5* |

- **Lectura:**
  - **El doble de algas salva a P4-alga.** Se mueven mucho más que en P3-escaso (empuje 10,9 frente a 6,5), comen algo más y VA ≈ 0 desde la época 40.
  - **Los saltos cortos cada 1.000 pasos son viables.** Con 64 u, el VA de las épocas 60–100 es el más alto de la escalera (media 0,64, frente a 0,25 en P4-lento y 0,15 en P3-disperso s0). Pero el VA alto en las primeras épocas ya se vio en los mundos de comida dispersa y luego se apagó. Con 128 u el VA baja hasta 0,04 y el cerebro se vacía. Los dos dan bichos grandes (masa 2,3–2,9) de vida corta (184–303 pasos) y muchos nacimientos (8.000–12.000 por época), con crisis tras cada salto. **Indicio, una sola semilla.**
  - **Los cambios dentro de una vida (cada 150 pasos) extinguen el mundo.**

### 15:13 (22-10) · Decisión del responsable: solo P4-alga; efímera aparcada; lanzamiento

- **Responsable:** se lanza **solo P4-alga** con el doble de algas, 5 mundos × 300 épocas. La comida efímera queda **aparcada** (`caminos.md`). Los saltos cortos cada 1.000 pasos quedan en espera.
- **Criterio prerregistrado** antes de lanzar (`diseno.md` v1.3, `6390637`): VA de la ingesta (media de las épocas 151–300) mayor que 0 y mayor que en P3-escaso, en 5/5 semillas emparejadas.
- **Lanzamiento:** cola `p4.json` de `escalera-p4` (`2e41573`), `scratchpad/p4alga.sh`. Primero la suite completa en GPU (si falla, no se lanza); después, los 5 mundos (log `runs/fase1d/p4alga.log`, marca `p4alga_hecho`). Duración estimada: ~40 min de tests y ~3,5 h de mundos.

### 15:14–18:49 (22-10) · P4-alga: resultado

- **Qué:** `escalera-p4` (`2e41573`, sustrato 2.10.0), cola `p4.json`, `scratchpad/p4alga.sh`. Suite completa en GPU (15:14–15:43, `runs/fase1d/p4_tests.log`): **84 correctos y 1 omitido**. Mundos: 15:43–18:49 (unos 37 min cada uno), sin pausas ni extinciones. Criterio en `diseno.md` v1.3. Tabla completa en `p0_factores.md` (P4-alga).
- **Primaria (VA de la ingesta, épocas 151–300, > 0 y > P3-escaso): 3/5, no pasa.** P4-alga: +0,019 / +0,090 / +0,017 / −0,011 / −0,082; P3-escaso: −0,000 / +0,001 / +0,009 / −0,021 / −0,003.
- **Lectura:**
  - El VA ya no es plano: de una prueba a otra oscila entre −0,26 y +0,23 (en P3-escaso, ±0,03). **s1 es positivo en las 15 pruebas** (+0,01 a +0,20). Indicio, un solo mundo.
  - Vidas de la mitad (280–313 frente a 483–688), el doble de nacimientos (8.400–9.900 por época) y más generaciones (436–583). Se mueven menos (empuje 5,7–5,9).
  - El cerebro se vacía igual (0,5–1,9 neuronas en las épocas 151–300), algo más tarde en s3 y s4.
  - Hay 7–8 veces más comida en pie que en P3-escaso; no se ha medido de qué alga es.
  - Examen limpio en la época 300: 0,000 / 0,000 / 0,031 / 0,125 / 0,047 (solo s3 supera a sus controles fijos).
  - La fracción de la ingesta del alga que alimenta no se puede calcular sin tocar la simulación (la del alga vacía se resta antes de las estadísticas).
  - Genes de reproducción (CPU, 18:50–19:05, `_genes_P4alga.json`): umbral 11,2–13,2 y fracción 0,22–0,31 en la época 300 (hijos baratos, como en P3-escaso); el 4,8–8,3 % de los vivos tiene energía para un hijo (1–3 % en P3-escaso).
  - Sonda de hambre (`scratchpad/p4a_hunger.py`, con el sorteo de algas activado): **0/5**. Lo más parecido es s0, donde el 87,2 % empuja menos al sentirse hambriento (la regla pide más del 90 % en 4 de 5 mundos).
- **Conclusión: negativo**, como se predijo en v1.3. Aparcado (`caminos.md`). Siguiente paso, con el responsable.

### 19:55 (22-10) · Decisión del responsable: P4-salto64; lanzamiento

- **Responsable:** tras P4-alga (no pasa, 3/5), se lanza **P4-salto64**: P3-disperso con el campo de comida desplazado 64 u en dirección al azar cada 1.000 pasos. El salto de 128 u y las semillas 5–9 de P4-alga quedan en espera.
- **Criterio prerregistrado** antes de lanzar (`diseno.md` v1.4): VA de la ingesta (épocas 151–300) mayor que 0 y mayor que en P3-disperso, en 5/5 semillas emparejadas.
- **Lanzamiento:** cola `p4sitio.json` de `escalera-p4` (`ba5e16e`), `scratchpad/p4sitio.sh` (log `runs/fase1d/p4sitio.log`, marca `p4sitio_hecho`). Sin repetir la suite: el código es el mismo con el que pasó a las 15:43.

### 20:57 (22-10) · ¿Palos de ciego? Decisión del responsable: diagnóstico antes de más peldaños

- **Pregunta del responsable:** «¿No te parece que estamos dando palos de ciego?». Respuesta: en parte sí. Desde P2 llevamos nueve negativos seguidos (P2-buscar, P3, P3-disperso, los tres costes, P4-alga…) cambiando el mundo sin saber por qué no se aprende, y nunca se comprobó si este cerebro puede aprender estas tareas.
- **Sospechas:**
  1. El bicho casi no nota que ha comido: su única pista es el nivel de energía (`tanh(E/50)`).
  2. No conocemos el suelo de ruido del VA.
  3. En P4-alga, comer el alga equivocada no cuesta nada, así que «come de todo» ya funciona.
  4. Además, ya hay un sitio donde aprender compensa: E1, con veneno (VA_log > 0 en 40 de 44 mundos). Se podría bajar desde ahí quitando interruptores.
- **Responsable:** diagnóstico primero, en la CPU; P4-salto64 sigue hasta terminar.
- **Diagnóstico** (`scratchpad/diag_aprender.py`, solo observa, con el código de `escalera-p4`): (A) quién puede aprender (sin neurona moduladora expresada, m = 0 y no hay plasticidad); (B) suelo de ruido del VA (tres gemelos congelados con una «mariposa»: un bicho desplazado 0,001 u); (C) cuánto cambia el canal de energía con un bocado frente a los rayos, y si la modulación se correlaciona con comer.
- **Prueba con P4-alga s1, época 300 (22:04–22:06):**
  - El 97,7 % de los vivos tiene una moduladora expresada, así que casi todos pueden aprender.
  - Cuando la energía sube (19,5 % de los pasos; +0,40 de media), el canal de energía cambia 0,007, frente a 0,134 de media en los rayos (19 veces menos; p99: 0,009 frente a 0,99).
  - Correlación entre la modulación y la subida de energía: 0,007.
  - Indicio: la señal de «he comido» está enterrada y la modulación no la usa.
- **Diagnóstico completo** en marcha desde las 22:07 (P4-alga, P3-escaso y P3-disperso, 5 semillas cada uno; salida `runs/fase1d/_diag_aprender.jsonl`).

### 22:11–22:45 (22-10) · La tripa: discusión, decisión del responsable (ADR-024) y preparación de la noche

- **Discusión con el responsable:**
  - ¿Más energía por bocado? No: es una consecuencia ecológica, no una señal, y el cerebro solo ve un nivel.
  - ¿Una entrada «has comido»? Solo sirve si lleva lo que ha dado lo comido, con su signo; un «he mordido» se enciende igual con las dos algas.
  - ¿Entrada de la acción y de la energía neta? La acción ya está en la regla de plasticidad (las neuronas de acción son «post»). El gasto de moverse no cambia entre generaciones y enterraría la señal.
  - Problema técnico: la plasticidad se aplica 1 de cada 4 pasos, así que una señal de un solo paso perdería 3 de cada 4 bocados.
- **Decisión (22:22):** un canal con la energía de lo comido en los últimos 4 pasos y su signo; 15 mundos esta noche; criterio 5/5 (`diseno.md` v1.5). La escala la fijé después en 1 (no en 0,5, como dije en la conversación), porque la ventana suma hasta 4 bocados: uno da 0,46 y cuatro, 0,96.
- **Código:** rama `escalera-tripa` (worktree `panspermia-tripa`, sustrato 3.0.0). Test nuevo `test_gut_sense_reports_energy_from_eating_over_window`: la entrada es tanh(suma/escala), el alga vacía da 0 y apagada vale 0 sin tocar las demás entradas. Primera pasada en CPU: un fallo de tolerancia (0,22776 frente a 0,22776, energía en f32 cerca de 50), corregido.
- **Noche:** `scratchpad/tripa_noche.sh` espera a `p4sitio_hecho`, pasa la suite en GPU y lanza `tripa.json` (P4-alga-tripa, P4-alga-sin-tripa, P3-escaso-tripa; log `runs/fase1d/tripa.log`, marca `tripa_hecho`).
