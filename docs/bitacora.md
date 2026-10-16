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
