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
