# Registro de decisiones (ADR)

Formato: número, fecha, decisión, motivo, alternativas descartadas. Las decisiones que abren canales al mundo real (spec §Salvaguardas, punto 2) se registran aquí antes de implementarse.

## ADR-001 · 15-10-2026 · Licencias

- **Código**: Apache-2.0. Es permisiva (facilita colaboración académica y forks de investigación) e incluye concesión explícita de patentes.
- **Documentación**: CC BY 4.0.
- **Genomas compartidos en la red**: CC0. Son datos que circulan entre nodos de terceros; cualquier restricción complicaría el archivo filogenético.
- Descartadas: MIT (sin cláusula de patentes); AGPL-3.0 (obligaría a publicar forks en red, pero frena la adopción y la reutilización académica).

## ADR-002 · 15-10-2026 · Stack: JAX sobre GPU

- Todo el núcleo en JAX (`jit`, `vmap`, `lax.scan`); física 2D propia en fases 0–1 y MuJoCo MJX en fase 2+.
- En Windows se ejecuta en WSL2.
- Descartado: PyTorch (peor ajuste para simulaciones vectorizadas puras y determinismo bajo `jit`); Genie u otros entornos aprendidos (sin API masiva, física no fiable, explotables por los agentes).

## ADR-003 · 15-10-2026 · Salvaguardas como requisito de diseño

- Se adopta la sección "Salvaguardas" de la spec como vinculante desde la fase 0, aunque el riesgo actual sea bajo: añadirlas tarde a una red P2P abierta es mucho más difícil.

## ADR-004 · 15-10-2026 · Nombre provisional

- "Panspermia": las semillas (genomas) viajan entre mundos (islas). Renombrable antes de publicar.

## ADR-005 · 15-10-2026 · Detalles de implementación de la fase 0

Decisiones que la spec no fija o que la concretan. Todas las constantes nuevas están en `config.py` (bloque «Detalles de implementación de la fase 0»).

- **Entorno**: Ubuntu 24.04 en WSL2 instalado en `D:\WSL\Ubuntu-24.04`; venv en `~/.venvs/panspermia`; instalación con `scripts/setup_wsl.sh`. Se instala con `pip` porque `uv pip install` 0.13.1 rechazaba al azar ruedas NVIDIA válidas («Invalid Wheel-Version») devolviendo código 0. GPU real: RTX 5070 Ti 16 GB (la spec cita una 5070 de 12 GB como referencia). JAX 0.11.2. Se desactiva la preasignación de VRAM (`XLA_PYTHON_CLIENT_PREALLOCATE=false`) porque el escritorio de Windows ocupa ~4,5 GB.
- **Genoma en memoria en f16**: los flotantes del genoma son `float16` también en memoria (la mutación calcula en f32 y redondea), así la serialización es exactamente sin pérdidas. Los genomas son siempre canónicos: `mutate` termina con `canonical`, y `from_bytes` rechaza blobs no canónicos.
- **Cabecera fuera del pytree**: `id`, `parent_id` y `origin_node` no viven en el estado de la isla (BLAKE3 no es computable bajo `jit`). Dentro de la isla el linaje usa `uid` enteros (`Lineage.uid/parent_uid/birth_step`); el id BLAKE3 se calcula al serializar. `from_bytes` devuelve `(Genome, GenomeMeta)`.
- **id** = BLAKE3-128 de `"panspermia-genome-v<major>" + payload canónico` (solo contenido; sin generación ni padre).
- **CPPN**: nodos 0–5 entradas, 6–23 ocultos, 24–31 salidas. Aristas válidas: i < j y destino no de entrada. Las entradas ignoran `act_id` (forma canónica: identidad, sesgo 0). Rango de genes: |W|, |bias|, |body|, |life[0:2]| ≤ 8; `hid_pos` ∈ [−1, 1]; σ ∈ [10⁻³, 0,5]; tasa estructural ∈ [0, 4].
- **Genes de vida**: `life[0]` umbral de reproducción (bruto → sigmoide → [10, 100]); `life[1]` fracción al hijo (bruto → [0,2, 0,8]); `life[2]` σ directo; `life[3]` tasa estructural directa.
- **Salidas de la CPPN → fenotipo**: w₀ = tanh(o₀); A..D = tanh(o₁..o₄); η = 0,1·sigmoide(o₅); expresión si o₆ > 0; g = tanh(o₇).
- **Cerebro**: sin sesgo neuronal (b = 0) en la fase 0, porque el sustrato no tiene neurona de sesgo. Las acciones usan [o_t; h_{t+1}] (incluye las conexiones directas obs→acción del sustrato). Las neuronas moduladoras también proyectan como ocultas normales.
- **Nacimientos en lote fijo**: como mucho `MAX_BIRTHS_PER_STEP = 16` nacimientos por paso (los candidatos que no caben esperan al paso siguiente); `mutate` + `develop` solo se evalúan sobre ese lote (no sobre los N slots) y dentro de `lax.cond`, para que el coste sea proporcional a los nacimientos. Con 64 la época con N = 4.096 subía de ~2,1 s a ~5,4 s, porque casi todos los pasos tienen algún nacimiento (media ≈ 1,5–3,5 por paso). Los candidatos se ordenan por una puntuación uniforme aleatoria (`top_k`), los slots libres por índice.
- **Claves**: la clave de la isla es fija; cada paso usa `fold_in(key, step)`. El resultado no depende de cómo se trocee la ejecución en épocas (hay test).
- **`step` es int32** (JAX sin x64): 2³¹ pasos ≈ 2·10⁶ épocas.
- **Vecindad**: rejilla de celdas de 64 unidades con hasta 32 agentes visibles por celda (`argsort` estable sobre enteros, determinista); cada agente mira las 3 × 3 celdas que le rodean. Alcance sensorial máximo 60.
- **Canales de los rayos**: proximidad del agente más cercano (1 − d/alcance), recurso medio en 4 muestras a lo largo del rayo, parentesco (1 − distancia de color/√3) y señal del agente detectado.
- **Manchas de Kmax**: suma de 8 ondas planas con números de onda enteros (periódicas en el toro) que derivan en el tiempo, en lugar de ruido de Perlin. Se añade un aporte mínimo `RESOURCE_SEED` para que las celdas agotadas rebroten (la logística pura deja R = 0 fijo).
- **Ingesta**: cada agente come de la celda de recursos bajo su centro; si la demanda supera el recurso, se reparte proporcionalmente.
- **Alcance de la fase 0**: se incluyen señal, senescencia y biogeografía (son baratas y no cambian formas); el ataque queda para la fase 1 (la acción existe pero se ignora y `C_ATTACK = 0`). Los cadáveres no depositan nada porque sin ataque solo se muere con E ≤ 0.
- **Extinción y reinyección**: la reinyección (genomas mínimos aleatorios, aún no hay archivo) la hace el runner entre épocas si la población baja de 64. El criterio de «sin extinción» se evalúa con la reinyección desactivada: población mínima > 0 en todos los pasos.
- **Ecología inicial**: con los primeros valores (K̄ = 1, r = 0,3, ingesta 2) los 512 agentes aleatorios morían de hambre sin reproducirse. Se sube a K̄ = 4 e ingesta máx. 5/tiempo para que un agente que avanza y come tenga balance positivo, y r = 0,5 para que la capacidad de carga sea ~1.300–1.600 agentes (con r = 0,15 se quedaba en ~550 de 4.096 slots). Tras un cuello de botella en la primera época (~150 agentes) la población se estabiliza.

## ADR-006 · 15-10-2026 · Cierre de la fase 0: aceptación y benchmark

Entorno: WSL2 Ubuntu 24.04 · JAX 0.11.2 · RTX 5070 Ti 16 GB · determinismo activado (`--xla_gpu_deterministic_ops=true`, precisión `highest`).

**Criterios de aceptación** (`pytest --runslow`, 18/18 en verde, 21 min):

| Criterio | Resultado |
| --- | --- |
| Misma semilla → estado idéntico bit a bit tras 10 épocas (N = 4.096) | Cumplido (`test_island_bitwise_determinism_10_epochs`, todos los leaves del `IslandState`) |
| Ida y vuelta sin pérdidas de 10⁴ genomas mutados | Cumplido (100 linajes × 100 generaciones; blobs de ~0,6 KB, muy por debajo de 4 KB) |
| ≥ 100 épocas sin extinción en 4 de 5 semillas | Cumplido sin reinyección (`population_min > 0` en cada paso) |
| Velocidad medida y documentada | Ver tabla |

Además: la ejecución no depende de cómo se trocee en épocas (2 × 100 pasos = 1 × 200 pasos bit a bit) y `from_bytes` rechaza NaN/Inf, formas erróneas, rangos fuera de límites, genomas no canónicos, hash incoherente, major distinto y blobs basura u oversize.

**Benchmark** (`scripts/bench.py`, mediana de 3 épocas de 1.000 pasos tras una de calentamiento):

| N_max | Época | Pasos-slot/s | Vivos (≈) | Pasos-agente vivo/s |
| --- | --- | --- | --- | --- |
| 1.024 | 1,22 s | 8,4·10⁵ | 860 | 7,1·10⁵ |
| 2.048 | 1,66 s | 1,2·10⁶ | 1.010 | 6,1·10⁵ |
| 4.096 | 2,07 s | 2,0·10⁶ | 1.010 | 4,9·10⁵ |

- La duración de época (< 5 s) se cumple con holgura.
- El objetivo de ≥ 10⁶ pasos-agente/s se cumple en **capacidad** (pasos-slot/s: el cómputo es denso sobre los N slots, así que el coste no depende de cuántos estén vivos), pero **no en agentes vivos**, porque con la ecología actual la capacidad de carga es ~1/3 de N_max. Si se quiere cumplir también en vivos, basta subir la productividad de recursos (r o K̄); no hace falta ninguna de las palancas de rendimiento de la spec (32 ocultas, plasticidad cada 8 pasos, dispersidad por bloques).
- La primera época incluye ~20 s de compilación.
- Coste por escala: de 1.024 a 4.096 slots el tiempo de época solo sube 1,7×, así que la GPU aún no está saturada con N = 4.096.
