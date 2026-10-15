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

## ADR-007 · 15-10-2026 · Fase 1: ecología, métricas, batería de capacidad y visor

**Ecología**

- **Ataque**: si la acción 3 > 0, el agente drena energía del agente vivo más cercano en su frente (±45°, superficie a ≤ 2 unidades): `fuerza_gen × 20 × dt` por paso. Gana el 60 %; el 40 % restante cae como carroña en la celda de recursos de la víctima, de modo que **la energía se conserva** (hay test). Si varios muerden a la misma víctima, lo drenado se reparte en proporción. Coste: `C_ATTACK = 0,5 × fuerza_gen` por unidad de tiempo mientras se intenta. Muerte «por ataque» = E ≤ 0 en un paso en que se recibió drenaje.
- **Cadáveres**: con este modelo la carroña es la parte no asimilada de cada mordisco; quien muere por hambre o vejez ya tiene E ≤ 0 y no deja nada.
- **Productividad**: r = 1,0 para una capacidad de carga de ~2.500–3.000 vivos (decisión del responsable, 15-10-2026). `MAX_BIRTHS_PER_STEP` sube a 32 porque con depredación hay ~20 nacimientos por paso y 16 era un cuello de botella. Para no pasar de 5 s por época se reescribió la evaluación de la CPPN por columnas (2,7× más rápida); la época queda en ~4,9 s con N = 4.096.
- **Primera observación** (semilla 0, 15 épocas): el gen de fuerza de ataque pasa de 0,5 a ~1,0 y las muertes por mordisco superan a las de hambre. Los intentos de ataque rondan 0,9 por agente y paso: es «morder lo que haya delante», no caza dirigida. Que haya o no estrategias distintas lo dirá el clustering del descriptor.

**Métricas** (solo observan; ninguna entra en la reproducción)

- **Clado**: un linaje inicia clado nuevo cuando su generación es múltiplo de 50. Por eso el número de clados oscila (se fragmenta cada 50 generaciones). Diversidad = nº de clados vivos e índice de Shannon.
- **Distancia genómica**: media sobre 256 pares aleatorios de vivos; euclídea de genes continuos y Hamming de máscaras.
- **Descriptor conductual** (8 dimensiones en [0, 1], agentes con ≥ 100 pasos de vida): velocidad, giro, ingesta, tasa de ataque, entropía de la señal (4 niveles), dispersión neta, agregación (vecinos en alcance) y edad a la primera reproducción. Si aún no se ha reproducido, el dato está censurado y se usa su edad actual como cota inferior: con un valor fijo de relleno (1,0), k-means separaba «ya se reprodujo / aún no» y daba silueta 0,42 sin diferencia de conducta (detectado en la semilla 0, época 10).
- **Novedad**: archivo histórico; novedad = distancia media a los 15 vecinos más cercanos en archivo ∪ muestra (512 descriptores por época); entran los que superan 0,15, con un máximo de 32 por época.
- **Grupos conductuales**: k-means (k = 2–6, inicialización k-means++ con semilla fija por época) y silueta media; se guarda el mejor k. Ya en la época 10 hay dos grupos reales, «giradores» (giro ≈ 0,97, dispersión ≈ 0,05) y «viajeros» (giro ≈ 0,02, dispersión ≈ 0,41), con silueta 0,57. Probablemente vienen de la diversidad aleatoria inicial (salidas tanh saturadas o nulas), así que el criterio de la spec (≥ 50 épocas estables) es evidencia débil de estrategias evolucionadas. El script de aceptación informa además de la estabilidad en la segunda mitad de la ejecución.
- **Bedau-Packard simplificado**: componente = clado; actividad = Σ población por época; «actividad nueva» = clados que superan 100 agentes·época. Sin modelo sombra. MODES (Dolson et al.) queda pendiente † hasta verificar la referencia.
- **Valor del aprendizaje**: cada 20 épocas se clona la isla y el clon corre una época con plasticidad congelada. Como la clave de cada paso es `fold_in(key, step)`, la comparación es **emparejada**: mismo estado y misma aleatoriedad. Valor = supervivencia de los vivos al inicio (plástica) − supervivencia (congelada).

**Salvaguarda 5: batería de capacidad** (cada 100 épocas; umbrales del responsable, conservadores)

| Prueba | Métrica | Umbral de pausa |
| --- | --- | --- |
| Comunicación | Información mutua entre la señal emitida (4 niveles) y el contexto del emisor (nada / comida delante / pariente visto / no pariente visto), en bits (máx. 2) | ≥ 0,5 |
| Comida en anillo (patrón no visto) | Éxito (ingesta ≥ 1) de 64 adultos aislados en 500 pasos − éxito de 64 genomas aleatorios | ≥ 0,5 |
| Laberinto (las islas no tienen paredes) | Ídem con la comida dentro de una caja abierta solo por detrás, 1.000 pasos | ≥ 0,25 |

- Los adultos se prueban aislados (un mundo por agente, sin reproducción, energía 100), con sus pesos aprendidos. Las pruebas corren sobre copias y no alteran la isla.
- Al superar un umbral, el runner guarda checkpoint, escribe `CAPABILITY_PAUSE.json` y termina con código 3. No vuelve a arrancar hasta que una persona cree `CAPABILITY_REVIEW.json` (`reviewed_by`, `notes`, `thresholds`); los umbrales nuevos solo pueden venir de ese fichero.
- Limitación reconocida: son métricas de competencia y de comunicación referencial, no de peligro. Sirven como detector de sorpresa, no como garantía.
- Las paredes viven en `EnvParams.walls` (vacías en las islas) y bloquean movimiento y canal de distancia. `EnvParams.regrow = 0` congela el campo de recursos en las pruebas.

**Visor** (decisión del responsable: visor web interactivo en lugar de MP4)

- Cada 50 épocas, `record_epoch` (misma dinámica que `epoch`; test bit a bit) guarda 500 fotogramas de la época (1 de cada 2 pasos) cuantizados en `recordings/epoch_XXXXXX.{json,bin.gz}`, ~10–15 MB.
- `python -m panspermia.viewer runs/<x>` sirve una página local (solo 127.0.0.1, sin listados ni rutas fuera de la carpeta) con reproducción, color por parentesco/clado/energía, comer/morder, señales, ficha por agente y gráficas de `stats/summary.json`.

**Otros**: el runner escribe `stats/summary.json` además del Parquet. Las partes Parquet pueden tener columnas distintas (pruebas cada 20/100 épocas): leer con `read_parquet('stats/*.parquet', union_by_name=true)`. El formato del genoma no cambia, así que `SUBSTRATE_VERSION` sigue en 1.0.0 aunque el mundo tenga reglas nuevas.

## ADR-008 · 16-10-2026 · Fase 1b: química artificial y algas estacionales (sustrato 2.0.0)

**Contexto.** En la fase 1 (semilla 0, primeras 150 épocas) la evolución converge a una sola estrategia sencilla: casi todos muerden lo que tienen delante y comen algas, los cerebros encogen de ~10 a ~5 neuronas, el valor del aprendizaje oscila en torno a 0 y los grupos conductuales se diluyen. Diagnóstico: el mundo no premia ni la diversidad ni aprender. Las acciones son pocas y cerradas (morder ya viene hecho) y el entorno apenas cambia dentro de una vida. El responsable delegó la elección del siguiente paso (16-10-2026, 00:03); esta es la elección.

**Decisión.** Dos cambios dentro de la pecera, sin abrir ningún canal al exterior:

1. **Química artificial (primitivas componibles).** Tres sustancias en campos de 128 × 128 con difusión y degradación: **nutriente**, **toxina** y **feromona**. Tres acciones nuevas emiten cada una en la celda propia (hasta 2 por unidad de tiempo).
   - Nutriente y toxina **almacenan la energía** que cuesta emitirlas (1 por unidad); la feromona cuesta 0,1 y se disipa.
   - Comer absorbe también nutriente: permite **almacenar comida o alimentar a otros** (por ejemplo, a la descendencia).
   - La toxina drena 5 × concentración por unidad de tiempo a quien esté en su celda (también al emisor) y se consume en la misma cantidad. Lo drenado y la toxina consumida vuelven al campo como alga.
   - Nutriente y toxina degradados vuelven como alga. **Energía conservada** en toda la química (hay tests); la única pérdida deliberada es el coste de la feromona.
   - Sensores nuevos (9): concentración local y gradientes adelante y lateral de cada sustancia (quimiotaxis).
   - Con esto, envenenar, defenderse con un rastro de toxina, cachear comida o marcar caminos pasan a ser **estrategias que se pueden descubrir**, no botones. Morder se mantiene para comparar con la fase 1.
2. **Algas estacionales (entorno que cambia dentro de una vida).** Hay dos tipos de alga en manchas que derivan con el mundo. El canal de recurso de los rayos lleva signo (+ tipo A, − tipo B), así que el tipo es visible. Uno de los dos es tóxico: comerlo **resta** lo que habría sumado. Cuál es tóxico cambia al azar con probabilidad 1/400 por paso, un proceso sin memoria que el reloj no permite predecir. La vida media es de ~100–150 pasos y una generación evolutiva tarda mucho más que un cambio de estación, así que nacer sabiendo no sirve: hay que **probar y aprender** (la energía propia es un sensor y las neuronas moduladoras pueden ligarse a su caída). Es el escenario clásico en el que la teoría predice que el aprendizaje compensa.

**Cambios de formato.** O = 79 (70 + 9), A = 8 (5 + 3), N_PRE = 143, N_POST = 72; el fenotipo crece un 11 %. El genoma no cambia de forma, pero el sustrato interpreta distinto los mismos genes, así que **major 2.0.0**: los migrantes 1.x se rechazan y el dominio del hash cambia. El descriptor conductual pasa a 12 dimensiones (+ emisión de cada sustancia y fracción de ingesta tóxica). Las pruebas de capacidad corren sin algas tóxicas (`EnvParams.seasonal = 0`).

**Predicciones** (para evaluarlas con honestidad): (a) el valor del aprendizaje sube por encima de 0; (b) aparece más de una estrategia estable (por ejemplo, emisores de toxina frente a pastores); (c) los cerebros dejan de encoger. Si nada de esto ocurre, el siguiente candidato es el entorno 3D (fase 2) o una química más rica.

**Seguridad.** Todo ocurre dentro de la simulación; la batería de capacidad y sus umbrales no cambian. La comunicación química (feromona) no entra todavía en la métrica de información mutua; queda como mejora pendiente de la batería.

**Alternativas descartadas por ahora**: quitar el mordisco (perderíamos la comparación con la fase 1); química con reacciones entre sustancias (más difícil de analizar; siguiente paso si esta funciona); genoma sin techo (los cerebros usan ~5 de 64 neuronas: el techo no es lo que limita).

## ADR-009 · 16-10-2026 · Peceras libres, peceras granja y fabricabilidad

**Contexto.** El responsable plantea tres caminos complementarios: (1) muchas peceras por el mundo para tener riqueza evolutiva, (2) fabricar en el mundo real organismos evolucionados en la pecera y (3) dirigir la evolución para que surjan organismos que resuelvan un problema real. El camino 3 choca con el principio 1 («ninguna métrica externa decide la reproducción»). El responsable delegó las decisiones de este ADR (16-10-2026, 00:23).

**Decisión.**

1. **Dos papeles de isla en la red.**
   - **Peceras libres**: evolución abierta, sin objetivo. Son el banco de diversidad de la red (fase 4) y siguen todas las reglas de la spec.
   - **Peceras granja**: islas cuyo entorno está diseñado para que resolver un problema real sea la forma de obtener energía.
2. **Las granjas no usan selección explícita, solo diseño de nicho.** El principio 1 se mantiene sin excepciones en toda la red: nadie puntúa a nadie; se cambia el mundo, como en la domesticación. Motivos: no hace falta tocar un principio innegociable, y una función de puntuación invita a explotarla (la población converge al primer truco que puntúa), mientras que un nicho bien diseñado tiende a producir soluciones más generales. Si algún día se quisiera selección explícita, haría falta un ADR que enmiende el principio 1.
3. **Flujo genético en un solo sentido: libre → granja.** Las granjas importan migrantes de las peceras libres, que aportan novedad, pero sus genomas nunca vuelven. Así el banco de diversidad no converge hacia soluciones de un problema concreto, y los organismos especializados quedan contenidos en su granja. Se implementará como un campo `role` firmado en la identidad del nodo (fase 4a) y como un rechazo en recepción.
4. **Primer problema real: localizar la fuente de una fuga** (gas o contaminante). Es un problema de robótica conocido (*odor source localization*), con aplicaciones en seguridad industrial y vigilancia ambiental. Encaja con la química del sustrato 2.x (sensores de concentración y gradiente). La granja tendrá fuentes que emiten una pluma con ruido y turbulencia; la comida aparece solo cerca de la fuente activa, y las fuentes cambian de sitio.
5. **Fabricabilidad desde el diseño.** El cuerpo 2D actual, con empuje y giro, equivale a un robot de tracción diferencial: dos ruedas, un microcontrolador y sensores de gas baratos (tipo MOX). En la granja, sensores y actuadores se restringen a lo que ese robot puede tener (alcances, ruido, latencias realistas), para reducir la brecha simulación-realidad. Los cuerpos 3D imprimibles (fase 2, al estilo de GOLEM, Lipson y Pollack 2000 †) quedan para después.
6. **Salvaguarda 2 intacta.** Llevar cualquier cerebro a un robot físico exige su propio ADR con análisis de riesgo y revisión explícita del responsable. Este ADR solo decide la arquitectura en simulación.

**Orden propuesto.** (a) Cerrar la fase 1b (química y algas estacionales). (b) Prototipo de granja «fuga» en 2D con una sola isla, como fase 1c, para medir si el nicho produce localizadores fiables sin puntuar a nadie. Métrica de observación: tasa de llegada a la fuente y tiempo medio, que nunca entra en la reproducción. (c) Fase 4a con papeles de isla. (d) ADR de salvaguarda 2 para un primer robot físico, si el responsable lo decide.

**Descartado.** Selección explícita en las granjas (por el principio 1, ver punto 2). Flujo bidireccional (contaminaría el banco de diversidad). Empezar por cuerpos 3D impresos (más caro y con una brecha simulación-realidad mayor que un robot de ruedas).
