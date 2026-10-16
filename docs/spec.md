# Especificación: ecosistema evolutivo distribuido

15-10-2026 · Alejandro Catalá Espí · Versión viva: https://claude.ai/code/artifact/21816b0f-bb95-495b-8604-7c95eeebdcb1

## Objetivo y principios

Construir un ecosistema de agentes encarnados que evolucionan sin función de fitness explícita, aprenden durante su vida mediante plasticidad evolucionada y se distribuyen en islas P2P. La meta de investigación es sostener la aparición de novedad conductual (apertura evolutiva) a escala creciente.

Principios (en caso de conflicto, gana el de número menor):

1. **Selección ecológica**: sobrevive y se reproduce quien gestiona su energía; ninguna métrica externa decide la reproducción.
2. **Genoma como datos**: el genoma nunca es código ejecutable; lo interpreta un sustrato fijo y versionado.
3. **Determinismo**: toda simulación es reproducible a partir de (versión de sustrato, semilla, estado inicial).
4. **Vectorización total**: todo el estado vive en arrays de tamaño fijo en GPU; nada de objetos por agente en Python.
5. **Distribución desde el día 1**: un nodo aislado es una isla de una red de tamaño 1.
6. **Sin retropropagación en el agente**: el aprendizaje en vida es local (hebbiano modulado). El gradiente solo se admite en herramientas de análisis.

Fuera de alcance: entornos aprendidos tipo Genie, LLMs dentro del agente y un mundo único sincronizado entre nodos.

## Arquitectura general

Cada nodo ejecuta una isla completa. Los nodos solo intercambian genomas y métricas, nunca estado del mundo.

| Componente | Responsabilidad | Entrada → salida | Tecnología |
| --- | --- | --- | --- |
| `world` | Física, recursos, sensores | Acciones (N×A) → observaciones (N×O), energía | JAX (fase 0–1: 2D propio); MJX (fase 2+) |
| `genome` | Formato, mutación, serialización | Genoma padre + PRNG → genoma hijo | JAX + msgpack |
| `develop` | Construye cuerpo y cerebro desde el genoma | Genoma → parámetros fijos del fenotipo | JAX (CPPN vectorizado) |
| `brain` | Paso neuronal y plasticidad | Obs., estado, pesos → acciones, estado, pesos | JAX |
| `island` | Bucle de simulación, nacimientos y muertes por slots | Estado de isla → estado de isla (k pasos) | `jax.lax.scan` + `jit` |
| `net` | Descubrimiento de pares, migración, verificación | Emigrantes ↔ inmigrantes | Python asyncio + libp2p o gRPC |
| `observatory` | Métricas, filogenia, checkpoints, vídeo | Estado de isla → Parquet, vídeos, panel | Python, DuckDB |

Flujo por época: `island` ejecuta K pasos en GPU → `observatory` muestrea → `net` exporta emigrantes e importa inmigrantes → siguiente época.

**Papeles de isla (ADR-009).** Los *mundos libres* hacen evolución abierta y son el banco de diversidad de la red. Los *mundos granja* tienen un entorno diseñado para que resolver un problema real sea la forma de obtener energía (sin selección explícita: el principio 1 se mantiene). El flujo genético va solo de libres a granjas. El primer problema es localizar la fuente de una fuga, con cuerpos equivalentes a un robot de tracción diferencial fabricable.

## Mundo

La energía es la única moneda: toda acción cuesta energía, solo la comida la aporta y con energía cero el agente muere.

### Fases 0–1: mundo 2D continuo

- Toroide de L × L unidades (L = 1024), paso dt = 0,1 y física de cuerpos circulares con fricción lineal y colisiones elásticas por rejilla espacial.
- Campo de recursos en una rejilla de 128 × 128: crecimiento logístico `r·R·(1−R/Kmax)` con Kmax variable en manchas (ruido de Perlin) que derivan lentamente para que el entorno cambie.
- Cadáveres: la energía restante del agente muerto se deposita en el campo y permite la aparición de carroñeros y depredadores.
- Sensores: 16 rayos en un cono de 180°, cada uno con 4 canales (distancia, recurso, agente, señal del agente detectado), más energía propia, velocidad, un reloj sinusoidal y la señal recibida. Total O = 70.
- Actuadores (A = 5): empuje, giro, comer, atacar y emitir señal (canal de comunicación de 1 valor).

### Fase 2+: mundo 3D (MJX)

- Terreno de *heightfield* variable, comida como objetos físicos y cuerpos generados por `develop`.
- Sensores: propiocepción articular, contacto y visión egocéntrica de baja resolución (32 × 32 × 3) renderizada por lotes con Madrona.
- Coste energético del movimiento = Σ |par × velocidad angular| × c_motor.

### Coste energético por paso

```latex
E_{t+1} = E_t + \text{ingesta} - (c_0 + c_b\,n_{neuronas} + c_s\,masa + c_m\,|empuje|^2 + c_a\,ataque) \, dt
```

El coste por neurona impide que los cerebros crezcan gratis: la evolución tiene que justificar cada neurona.

### Biogeografía

Cada isla deriva un vector `env_params` (Kmax medio, deriva de manchas, fricción, coste basal ±10 %) de su identificador de nodo. Las islas difieren de forma estable y reproducible.

## Genoma

El genoma es un grafo CPPN de capacidad fija más genes escalares. La topología variable se representa con máscaras, lo que permite vectorizar en JAX conservando el crecimiento estilo NEAT.

| Bloque | Campo | Forma y tipo | Descripción |
| --- | --- | --- | --- |
| Cabecera | `substrate_version` | semver (str) | Versión del intérprete; el major debe coincidir para migrar |
| Cabecera | `id`, `parent_id` | BLAKE3 de 16 B | Direccionamiento por contenido: el id es el hash del genoma canónico |
| Cabecera | `origin_node`, `generation` | 16 B, uint32 | Trazabilidad filogenética |
| CPPN | `node_mask` | bool[32] | Nodos activos (6 de entrada y 8 de salida siempre activos) |
| CPPN | `act_id` | int8[32] | Activación: sin, gauss, tanh, sigmoide, abs, identidad |
| CPPN | `bias` | f16[32] | Sesgo por nodo |
| CPPN | `W`, `W_mask` | f16[32×32], bool[32×32] | Conexiones; recurrencia prohibida (orden topológico por índice) |
| Cerebro | `hid_mask` | bool[64] | Neuronas ocultas expresadas |
| Cerebro | `hid_pos` | f16[64×2] | Posición en el sustrato 2D (entrada de la CPPN) |
| Cerebro | `hid_type` | bool[64] | Excitadora o moduladora |
| Cuerpo | `body` | f16[8] | Radio, empuje máximo, cono sensor, alcance, color de parentesco (3), fuerza de ataque |
| Vida | `life` | f16[4] | Umbral de reproducción, fracción de energía al hijo, σ de mutación (autoadaptativa), tasa estructural |

- **Entradas de la CPPN** (6): posiciones pre y post (x₁, y₁, x₂, y₂), distancia y sesgo.
- **Salidas de la CPPN** (8): peso inicial w₀, coeficientes hebbianos A, B, C, D, tasa η, expresión de la conexión (umbral > 0) y ganancia de modulación.
- **Serialización**: msgpack con claves fijas, arrays en f16 little-endian y compresión zstd. Tamaño objetivo: 4 KB o menos.
- **Forma canónica**: antes de calcular el hash, los pesos con máscara 0 se ponen a 0 y los nodos inactivos a valores neutros.
- **Versionado**: si cambia el major de `substrate_version`, el migrante se rechaza; si cambia el minor, se aplica una función `upgrade(genome)` registrada.

## Desarrollo genotipo→fenotipo

El desarrollo ocurre una vez, al nacer: la CPPN se evalúa sobre todos los pares de neuronas candidatos y produce los pesos iniciales y las reglas de plasticidad de cada sinapsis.

1. **Sustrato neuronal**: las 70 entradas se colocan en y = −1 y las 5 salidas en y = +1, con x repartida uniformemente; las ocultas se sitúan en `hid_pos`, dentro de [−1, 1]².
2. **Consulta**: se evalúa la CPPN en lote sobre los pares (entrada ∪ oculta) → (oculta ∪ salida). Eso son 134 × 69 = 9.246 pares, que incluyen la recurrencia oculta→oculta.
3. **Expresión**: la conexión existe si la salida `express` es mayor que 0 y ambas neuronas están en máscara. El resultado es una matriz densa con máscara, lista para GPU.
4. **Fenotipo almacenado por slot**: w₀, A, B, C, D, η y g_mod, cada uno de forma f16[134×69], más la máscara. Son unos 130 KB por agente, así que 4.096 agentes ocupan unos 530 MB de VRAM.
5. **Cuerpo (fases 0–1)**: parámetros escalares directos desde `body`, acotados por funciones sigmoide a rangos físicos.
6. **Cuerpo (fase 2+, sustrato v2)**: se añade un bloque `morph` con un árbol de hasta 8 segmentos (padre, eje de articulación, longitud, radio, rango de giro), al estilo de los *unimals* de DERL. El MJCF se genera por plantilla y los cuerpos se agrupan por número de segmentos para batch en MJX.

Regla de desarrollo: la misma función `develop(genome, substrate_version)` es pura y determinista; dos nodos producen fenotipos idénticos bit a bit con la misma versión.

## Cerebro y plasticidad

El cerebro es una red recurrente de tiempo discreto. Sus pesos cambian durante la vida según una regla hebbiana ABCD modulada, con coeficientes distintos por sinapsis fijados por el genoma (Najarro y Risi, 2020; Soltoggio et al., 2018).

**Paso neuronal** (un paso de mundo por paso neuronal):

```latex
h_{t+1} = \tanh\left(W_t^{\top} [o_t; h_t] + b\right), \quad a_t = \tanh\left(W_t^{out\top} h_{t+1}\right)
```

**Señal moduladora**: m_t es la media de la activación de las neuronas ocultas de tipo modulador. El genoma decide qué neuronas modulan; no existe una recompensa externa.

**Regla de plasticidad** por sinapsis i→j:

```latex
\Delta w_{ij} = \eta_{ij}\, g_{ij}\, m_t \left(A_{ij}\, x_i x_j + B_{ij}\, x_i + C_{ij}\, x_j + D_{ij}\right)
```

- Recorte: |w| ≤ w_max = 4 tras cada actualización.
- Los pesos plásticos se reinician a w₀ en cada nacimiento: lo aprendido no se hereda (Darwin, no Lamarck), y solo se transmite la capacidad de aprender.
- Coste: la plasticidad se aplica cada p = 4 pasos para limitar el cómputo. Es un parámetro global, no genético.
- Precisión: pesos en f32 durante la vida; f16 solo en almacenamiento y migración.

**Opción de fase 3: modelo del mundo interno**. Se añaden salidas de predicción de la observación siguiente, y el error de predicción alimenta m_t como señal moduladora adicional. El agente puede así aprender un modelo del mundo con reglas locales, sin gradiente.

## Ciclo de vida y mutación

La población ocupa N_max = 4.096 slots fijos con máscara `alive`. La capacidad de carga la imponen la comida y los slots libres; no hay generaciones sincronizadas.

**Nacimiento** (asexual en las fases 0–2):

- Condiciones: E ≥ umbral genético, edad ≥ 200 pasos y existe un slot libre.
- El hijo recibe la fracción f de la energía del padre (genética, acotada a [0,2, 0,8]) y nace a una distancia de 2 radios.
- El genoma del hijo es `mutate(genome_padre, key)`, y el fenotipo se desarrolla en el mismo paso.
- Si hay varios candidatos para pocos slots, se asignan por orden aleatorio con la PRNG de la isla, de forma determinista.

**Muerte**: por E ≤ 0, por ataque o por senescencia. La senescencia consiste en que el coste basal crece un 0,02 % por paso a partir de 5.000 pasos de edad, lo que garantiza recambio.

**Reproducción sexual (fase 3)**: requiere contacto, señal emitida por ambos y distancia de color de parentesco por debajo de un umbral. El cruce se hace por índice: como los índices de nodo de la CPPN son fijos, actúan como marcas históricas, igual que las innovaciones de NEAT.

**Operadores de mutación** (las probabilidades estructurales se multiplican por el gen `tasa estructural`):

| Operador | Probabilidad por hijo | Efecto |
| --- | --- | --- |
| Perturbación de parámetros | 1,0 | Gaussiana N(0, σ) sobre pesos, sesgos y genes de cuerpo y vida activos |
| Autoadaptación de σ | 1,0 | σ' = σ · exp(τ · N(0,1)), con τ = 0,2 y σ acotada a [10⁻³, 0,5] |
| Añadir conexión CPPN | 0,05 | Activa una arista libre i < j con peso N(0, 1) |
| Eliminar conexión CPPN | 0,02 | Desactiva una arista activa |
| Dividir conexión (añadir nodo) | 0,03 | Activa un nodo libre k en medio de la arista i→j, con i < k < j |
| Eliminar nodo CPPN | 0,01 | Desactiva un nodo oculto y sus aristas |
| Cambiar activación | 0,02 | Sustituye `act_id` por otra activación uniforme |
| Expresar o silenciar neurona | 0,03 | Invierte `hid_mask` de una neurona oculta |
| Duplicar neurona | 0,01 | Copia una neurona activa en un slot libre con posición desplazada N(0; 0,05). Es el análogo de la duplicación génica |
| Mover neurona | 0,05 | `hid_pos` += N(0; 0,05) |

**Arranque**: la población inicial tiene 512 genomas con una CPPN mínima (entradas conectadas directamente a salidas) y 8 neuronas ocultas. Si la población cae por debajo de 64, se reinyectan genomas del archivo local o de pares.

## Motor de isla

Toda la isla es un único pytree inmutable de JAX que avanza con `jax.lax.scan` dentro de `jit`. Python solo interviene entre épocas.

```python
@struct.dataclass
class IslandState:
    step: jnp.int64
    key: jax.Array            # PRNG de la isla
    env: EnvParams            # biogeografía (constante)
    resources: f32[128, 128]
    alive: bool[N]
    pos: f32[N, 2]; vel: f32[N, 2]; angle: f32[N]
    energy: f32[N]; age: i32[N]; signal: f32[N]
    genome: Genome            # arrays con eje N delante
    pheno: Phenotype          # w0, A..D, eta, g, mask: f16[N, 134, 69]
    w: f32[N, 134, 69]; h: f32[N, 64]
    lineage: Lineage          # id, parent_id, birth_step: [N]

def epoch(state, K=1000) -> (IslandState, EpochStats)
```

Orden dentro de `world_step`: sensores → cerebro → física y colisiones → comer y atacar → energía → muertes → nacimientos (mutate + develop solo en los slots nuevos, mediante `jnp.where`) → plasticidad (cada p pasos) → recursos.

**Determinismo**: se usan `XLA_FLAGS=--xla_gpu_deterministic_ops=true` y `jax_default_matmul_precision="highest"` para evitar TF32. Cada época deriva su clave con `fold_in(key, step)`.

| Recurso (fase 0, RTX 5070 12 GB, N = 4.096) | Presupuesto |
| --- | --- |
| Fenotipo f16 + pesos vivos f32 | ≈ 0,7 GB (530 MB + 150 MB) |
| Genomas, estado físico y recursos | < 100 MB |
| Objetivo de velocidad (por medir en la fase 0) | ≥ 10⁶ pasos-agente/s |
| Duración de época | K = 1.000 pasos, < 5 s |

Si no se alcanza el objetivo de velocidad, la primera palanca es reducir las ocultas a 32 o la plasticidad a cada 8 pasos, y la segunda es pasar el fenotipo a dispersidad por bloques.

## Red P2P

Las islas intercambian solo genomas firmados. Ningún nodo declara fitness, así que un migrante solo prospera si sobrevive en la isla que lo recibe: la propia ecología actúa como verificador.

**Identidad**: cada nodo tiene un par de claves Ed25519, y su `node_id` es el BLAKE3 de la clave pública.

**Topología**: cada nodo mantiene 4–8 vecinos y sustituye al azar uno cada 50 épocas, formando un grafo de mundo pequeño con flujo génico lento.

- Fase 4a: un *tracker* HTTPS mínimo (FastAPI) registra nodos activos y reparte vecinos; la transferencia es directa por gRPC sobre TLS.
- Fase 4b: descubrimiento sin servidor mediante DHT Kademlia (libp2p), manteniendo el tracker como arranque.

**Migración**: cada M = 10 épocas, el nodo envía a cada vecino k = 8 emigrantes elegidos al azar entre los vivos. No se eligen "los mejores", para no introducir una fitness explícita.

```
MigrationPacket {
  substrate_version: str
  sender_id: bytes16, epoch: uint64
  genomes: [GenomeBlob]      // msgpack+zstd, ≤ 4 KB cada uno
  signature: bytes64         // Ed25519 sobre todo lo anterior
}
```

**Recepción**: se valida en este orden, y cualquier fallo descarta el paquete completo.

1. Firma válida y `node_id` coherente con la clave pública.
2. Major de `substrate_version` compatible.
3. Esquema exacto: formas, tipos y tamaño ≤ 4 KB.
4. El hash recalculado coincide con `id`.
5. Rangos válidos: sin NaN ni Inf, y todos los genes dentro de sus límites.
6. Cuota por remitente.

Los inmigrantes nacen en slots libres con energía inicial estándar. Si no hay slots libres, sustituyen agentes elegidos al azar, sin sesgo de fitness.

**Defensas**:

| Amenaza | Defensa |
| --- | --- |
| Inundación de genomas basura | Inmigrantes ≤ 2 % de N por época en total y ≤ k por vecino |
| Sybil (muchas identidades falsas) | La cuota de un par crece con su antigüedad en la red; el tracker limita registros por IP |
| Genoma malicioso | Es dato puro: no se ejecuta, se interpreta con límites fijos |
| Genoma "invasor" legítimo | Se acepta: es evolución. Se mide su impacto en diversidad |
| Métricas falsas en el panel global | Auditoría por re-simulación con (versión, semilla, checkpoint) |

**Almacén**: cada nodo guarda un archivo de genomas direccionado por contenido (SQLite: id, padre, origen, época, blob), que sirve para la filogenia y la reinyección tras extinciones.

## Métricas y persistencia

Las métricas solo observan; ninguna realimenta la selección. La pregunta que deben responder es si sigue apareciendo novedad y si el aprendizaje en vida importa.

| Grupo | Métricas por época |
| --- | --- |
| Demografía | Población, nacimientos, muertes por causa (hambre, ataque, vejez), edad media |
| Complejidad | Neuronas ocultas activas, sinapsis expresadas, nodos y aristas CPPN (media y máximo) |
| Diversidad | Linajes vivos, índice de Shannon por clado, distancia genómica media |
| Conducta | Descriptor de 8 dimensiones por agente (velocidad, giro, ingesta, ataques, entropía de señal, dispersión, agregación, edad al reproducirse) |
| Novedad | Distancia k-NN (k = 15) del descriptor al archivo histórico; tamaño del archivo |
| Apertura evolutiva | Estadísticas de actividad evolutiva de Bedau-Packard y el conjunto MODES (Dolson et al., 2019, *Artificial Life* 25(1)) † |
| Valor del aprendizaje | Cada 20 épocas, un clon de la isla con plasticidad congelada durante 1 época; la diferencia de supervivencia mide cuánto importa aprender |
| Fase 3 | Puntuación de novedad visual con un modelo de visión-lenguaje sobre vídeos, al estilo de ASAL |

**Persistencia**:

- Estadísticas: Parquet por época, consultable con DuckDB.
- Checkpoints con Orbax cada 10 épocas; se conservan los 5 últimos y uno de cada 100.
- Vídeo de 30 s cada 50 épocas.
- Filogenia: el archivo SQLite del apartado anterior.

**Panel**: una página local que lee los Parquet, y en la fase 4 un panel global agregado por el tracker.

† Referencia de memoria: verificar antes de citar.

## Fases y criterios de aceptación

Cada fase se cierra solo cuando cumple todos sus criterios. La fase 4a (P2P con tracker) puede empezar en paralelo nada más cerrar la 1, porque solo depende del formato de genoma.

| Fase | Alcance | Criterios de aceptación |
| --- | --- | --- |
| 0. Núcleo 2D | `world` (comida, sin ataque), `genome`, `develop`, `brain` con plasticidad, `island`, métricas de demografía y complejidad, checkpoints | Dos ejecuciones con la misma semilla son idénticas bit a bit tras 10 épocas · ida y vuelta serializar/deserializar sin pérdidas sobre 10⁴ genomas mutados · ≥ 100 épocas sin extinción en 4 de 5 semillas · el objetivo de velocidad medido y documentado |
| 1. Ecología | Ataque, cadáveres, señal, senescencia, biogeografía, todas las métricas, prueba de plasticidad congelada | Al menos 2 grupos conductuales estables (clustering del descriptor, silueta ≥ 0,3) durante ≥ 50 épocas · el valor del aprendizaje es positivo con p < 0,05 en 5 semillas · el archivo de novedad sigue creciendo a las 500 épocas |
| 2. Mundo 3D | Sustrato v2 en MJX: bloque `morph`, terreno, visión Madrona | Locomoción dirigida a la comida que surge sin recompensa de locomoción · ≥ 512 agentes 3D en tiempo de época < 60 s |
| 3. Complejidad | Reproducción sexual, modelo del mundo interno, novedad con modelo de visión-lenguaje | El error de predicción del agente baja durante su vida · la reproducción sexual se mantiene frente a la asexual en competencia directa (o se documenta que no) |
| 4a. Red con tracker | Tracker, gRPC/TLS, firma, validación, cuotas, archivo SQLite | 3 nodos durante 7 días sin intervención · 0 paquetes corruptos aceptados en *fuzzing* de 10⁵ paquetes · la diversidad conjunta de 3 islas supera a la de 1 isla con N × 3 |
| 4b. Red sin servidor | DHT Kademlia, reputación de pares, panel global | 20 nodos o más, con entrada y salida libre de nodos, sin pérdida de linajes en el archivo global |

## Salvaguardas

El riesgo no depende de lo listos que lleguen a ser los agentes, sino de lo que pueden tocar. Este apartado es tan vinculante como los principios.

1. **Contención por construcción**: el espacio de acción de un agente se limita a los actuadores de la simulación. El sustrato no expone ninguna API de red, ficheros, procesos ni sistema a los agentes.
2. **Puertas de capacidad**: todo canal nuevo entre agentes y el mundo real (comunicación con humanos, internet, LLM, robots, hardware) exige un ADR en `docs/decisiones.md` con análisis de riesgo y revisión explícita del responsable del proyecto. Nunca se activa por defecto ni en el mismo PR que lo implementa.
3. **Sustrato firmado**: los nodos solo aceptan y ejecutan versiones de sustrato firmadas con la clave de publicación del proyecto; los paquetes de nodos con versiones no firmadas se rechazan.
4. **Parada y revocación**: el tracker puede publicar una lista de revocación de versiones y una orden de parada firmada; los nodos la consultan cada época y la obedecen. En la fase 4b la lista se replica en la DHT y se valida con la misma clave.
5. **Vigilancia de capacidades**: cada 100 épocas se ejecuta una batería fija de pruebas de capacidad (tareas nuevas no vistas, complejidad de la comunicación). Superar umbrales definidos en `config.py` pausa la isla y exige revisión humana antes de continuar.
6. **Sin automejora del sustrato**: los agentes evolucionan dentro de las reglas; nunca pueden modificar el código, los parámetros globales ni el genoma de otros fuera de los operadores definidos.

Límite reconocido: el confinamiento es eficaz frente a sistemas menos capaces que sus supervisores y débil frente a uno superhumano; por eso la salvaguarda principal es la 2.

## Riesgos y preguntas abiertas

El riesgo principal es científico, no técnico: que la complejidad se estanque en pocas épocas, como en todos los sistemas previos.

| Riesgo | Señal temprana | Mitigación |
| --- | --- | --- |
| Estancamiento de la complejidad | El archivo de novedad deja de crecer | Aumentar la deriva del entorno, la coevolución depredador-presa y la heterogeneidad entre islas |
| Explotación de la física (*exploits*) | Conductas imposibles, como energía desde colisiones | Revisar vídeos cada 50 épocas y tests de conservación de energía |
| Plasticidad inútil | El valor del aprendizaje es aproximadamente 0 | Entornos que cambian dentro de una vida (manchas móviles, comida tóxica variable) |
| VRAM insuficiente en 3D | Errores de memoria al compilar | Reducir N, usar dispersidad por bloques o separar la física en lotes |
| Divergencia numérica entre GPUs | Fenotipos distintos en nodos distintos | `develop` en f32 con redondeo final a f16; tests de conformidad entre arquitecturas |
| Pocos participantes en la red | Menos de 3 nodos activos | Divulgación (Astroval, clase) y un modo de bajo consumo para PCs sin GPU |

**Preguntas abiertas** (por decidir antes de la fase indicada):

- [x] Licencia del código y de los genomas compartidos → ver `docs/decisiones.md` (ADR-001).
- [ ] ¿Se permiten nodos solo con CPU, con N reducido? (fase 4a)
- [ ] ¿Se añade un alfabeto de señales más rico para estudiar la emergencia del lenguaje? (fase 3)
- [ ] ¿El sustrato v2 sustituye al 2D o conviven ambas redes? (fase 2)
