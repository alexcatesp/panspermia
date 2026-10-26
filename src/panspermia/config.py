"""Constantes globales de la especificación (docs/spec.md). Única fuente de números."""

SUBSTRATE_VERSION = "3.6.0"  # major distinto => migrantes rechazados (2.x: química + algas estacionales, ADR-008;
                             # 2.1: interruptores de la escalera de complejidad en EnvParams, ADR-014;
                             # 2.2: física de la mutación de neuronas elegible, ADR-015;
                             # 2.3: tasas de mutación fijas y CPPN neutral elegibles, ADR-016;
                             # 2.4: reproducción sexual y lugar de nacimiento elegibles, ADR-017;
                             # 2.5: el cruce hereda la CPPN entera de un progenitor, ADR-018;
                             # 2.6: física de la herencia de la escalera por defecto y CPPN neutral corregida, ADR-019;
                             # 2.7: comida dispersa elegible (config.K_CUT), P2-buscar, ADR-022;
                             # 2.8: coste fijo por hijo elegible (config.REPRO_COST), P3-coste, ADR-023;
                             # 2.9: comida que cambia de sitio y alga que alimenta (FOOD_JUMP_PERIOD, ALGA_SWAP_PERIOD), P4;
                             # 2.10: salto corto de la comida (FOOD_JUMP_DIST), P4;
                             # 3.0: sentido de la tripa, una entrada más, ADR-024;
                             # 3.1: comer frena (EAT_MOVE_FACTOR), ADR-025;
                             # 3.2: rampa del freno (EAT_MOVE_RAMP_STEPS), ADR-025;
                             # 3.3: alga buena sorteada para cada bicho (ALGA_PER_AGENT), ADR-026;
                             # 3.4: rampa de comida (K_MEAN_RAMP_STEPS, K_MEAN_RAMP_FROM), ADR-026;
                             # 3.5: manchas de un solo tipo de alga (ALGA_PATCH_FAMILIES), ADR-027;
                             # 3.6: veneno diferido (POISON_FACTOR, POISON_DELAY), P5-d, ADR-030)

# --- Mundo 2D (fases 0-1) ---
WORLD_L = 1024.0
DT = 0.1
RESOURCE_GRID = 128
N_RAYS = 16
RAY_CONE_DEG = 180.0
RAY_CHANNELS = 4  # distancia, recurso (con signo según tipo de alga), agente, señal
N_CHEM = 3        # sustancias: nutriente, toxina, feromona (ADR-008)
CHEM_OBS = 3 * N_CHEM  # por sustancia: concentración local, gradiente adelante y lateral
OBS_DIM = N_RAYS * RAY_CHANNELS + 6 + CHEM_OBS + 1  # 64 + energía, vel(2), reloj(2), señal + 9 + tripa = 80
ACT_DIM = 5 + N_CHEM  # empuje, giro, comer, atacar, señal, emitir nutriente/toxina/feromona = 8

# --- Población ---
N_MAX = 4096
N_INIT = 512
N_MIN_REINJECT = 64
EXTINCT_STOP_EPOCHS = 20  # el runner se detiene tras 20 épocas seguidas por debajo de N_MIN_REINJECT
MIN_REPRO_AGE = 200
OFFSPRING_ENERGY_FRAC_BOUNDS = (0.2, 0.8)
SENESCENCE_START = 5000
SENESCENCE_RATE = 0.0002  # +0,02 % de coste basal por paso

# --- Genoma ---
CPPN_NODES = 32
CPPN_IN = 6   # x1, y1, x2, y2, d, bias
CPPN_OUT = 8  # w0, A, B, C, D, eta, express, g_mod
N_HIDDEN_MAX = 64
N_HIDDEN_INIT = 8
BODY_GENES = 8
LIFE_GENES = 4
GENOME_MAX_BYTES = 4096
N_ACTIVATIONS = 6  # sin, gauss, tanh, sigmoide, abs, identidad

# --- Cerebro ---
N_PRE = OBS_DIM + N_HIDDEN_MAX   # 143
N_POST = N_HIDDEN_MAX + ACT_DIM  # 72
W_MAX = 4.0
PLASTICITY_EVERY = 4

# --- Mutación ---
SIGMA_TAU = 0.2
SIGMA_BOUNDS = (1e-3, 0.5)
P_ADD_EDGE = 0.05
P_DEL_EDGE = 0.02
P_SPLIT_EDGE = 0.03
P_DEL_NODE = 0.01
P_CHANGE_ACT = 0.02
P_TOGGLE_NEURON = 0.03
P_DUP_NEURON = 0.01
P_MOVE_NEURON = 0.05
NEURON_MOVE_SIGMA = 0.05
# Física de la mutación del número de neuronas (ADR-015, docs/bibliografia/escalera/):
# - "nest" (spec v1, por defecto): «expresar o silenciar» invierte un hueco elegido al azar entre los
#   64 y «duplicar» solo suma. Sin selección deriva hacia ~43 neuronas (sesgo entrópico, visto en P0).
# - "neutral": primero se decide encender o apagar (mitad y mitad) y luego a qué neurona; «perder
#   neurona» compensa a «duplicar» con la misma tasa. Sin selección, el tamaño no tiene rumbo.
# - "terrestre": se pierde el doble de lo que se gana, como el sesgo de deleción de la Tierra
#   (Kuo y Ochman 2009): 1/3 de los cambios encienden y «perder» es el doble de «duplicar».
# Física de la escalera (ADR-019, cierre de P0): "neutral".
NEURON_MUTATION = "neutral"
NEURON_MUTATION_P_ON = {"neutral": 0.5, "terrestre": 1 / 3}
P_DEL_NEURON = {"neutral": 0.01, "terrestre": 0.02}
# Tasas de mutación (ADR-016): "evolutivas" (spec v1: σ autoadaptativa y tasa estructural como gen,
# que sin selección deriva hacia arriba por el suelo en 0) o "fijas" (σ = SIGMA_INIT y tasa = 1,
# constantes del mundo; los genes no cambian).
# Física de la escalera (ADR-019): "fijas" (σ = 0,05 y tasa 1, A3 y A4; con ellas f16 basta, A7).
MUTATION_RATES = "fijas"
# Física de la mutación de la CPPN (ADR-016): "nest" (spec v1: añadir arista 5 %, quitar 2 %, dividir
# 3 %, quitar nodo 1 %: crece sin selección) o "neutral" (ganar y perder con la misma tasa; el total
# de cambios estructurales por hijo, 11 %, no cambia) o "neutral_corregida" (ADR-019: las tasas de la
# neutral, con cada operador emparejado con su inverso: quitar un nodo lo contrae (sus vecinos
# quedan unidos por el mínimo de aristas: −1 nodo y −1 arista, lo contrario de dividir), quitar una
# arista nunca aísla un nodo oculto y dividir solo elige aristas divisibles; sin esto la neutral
# pierde aristas sola). Física de la escalera: "neutral_corregida".
CPPN_MUTATION = "neutral_corregida"
CPPN_NEUTRAL_RATES = {"add_edge": 0.035, "del_edge": 0.035, "split": 0.02, "del_node": 0.02}
# Reproducción (ADR-017, corregida en ADR-018): "asexual" (spec v1) o "sexual": el hijo mezcla los
# genes del padre y de una pareja adulta elegida al azar entre sus vecinos (rejilla 3 × 3); sin pareja
# cerca, se clona. La pareja solo aporta genes, no energía. La CPPN se hereda entera de uno de los dos
# (bloque ligado); los huecos de neurona y los genes de cuerpo y de vida se mezclan uno a uno.
REPRODUCTION = "asexual"
# Dónde nace el hijo (ADR-017): "cerca" (spec v1: a 2 radios del padre) o "azar" (cualquier punto).
BIRTH_PLACEMENT = "cerca"
# Estructura espacial (solo observa, ADR-017): vecinos a menos de KIN_RADIUS cuentan para el
# parentesco local (fracción de vecinos del mismo clado).
KIN_RADIUS = 30.0

# --- Detalles de implementación de la fase 0 (ADR-005; no fijados por la spec) ---
# CPPN: índices 0..5 entradas, 6..23 ocultos, 24..31 salidas (orden topológico por índice).
CPPN_HIDDEN_START = CPPN_IN
CPPN_OUT_START = CPPN_NODES - CPPN_OUT
ACT_IDENTITY = 5
GENE_BOUND = 8.0             # |W|, |bias|, |body|, |life[0:2]| <= GENE_BOUND
STRUCT_RATE_BOUNDS = (0.0, 4.0)
SIGMA_INIT = 0.05
CPPN_INIT_W_STD = 1.0
GENOME_DECOMPRESSED_MAX = 16384  # protección frente a bombas zstd

# Salidas de la CPPN → fenotipo
W_INIT_SCALE = 1.0           # w0 = W_INIT_SCALE * tanh(o)
PLAST_COEF_SCALE = 1.0       # A..D = PLAST_COEF_SCALE * tanh(o)
ETA_MAX = 0.1                # eta = ETA_MAX * sigmoid(o)

# Cuerpo: genes brutos → rangos físicos por sigmoide
RADIUS_BOUNDS = (2.0, 8.0)
RADIUS_REF = 4.0             # masa = (radio / RADIUS_REF)^2
THRUST_BOUNDS = (2.0, 20.0)
CONE_BOUNDS_DEG = (60.0, 300.0)
SENSOR_RANGE_BOUNDS = (15.0, 60.0)
ATTACK_BOUNDS = (0.0, 1.0)
REPRO_THRESHOLD_BOUNDS = (10.0, 100.0)

# Física
FRICTION = 1.0               # fricción lineal (1/tiempo)
MAX_TURN_RATE = 2.0          # rad / unidad de tiempo
GRID_CELL = 64.0             # celda de la rejilla espacial; >= alcance sensor máx. y 2·radio máx.
CELL_CAP = 32                # agentes por celda visibles en vecindad (exceso invisible)
RAY_SAMPLES = 4              # muestras de recurso por rayo

# Energía (unidades de energía = unidades de recurso)
E_INIT = 30.0
E_OBS_SCALE = 50.0
# Tripa (ADR-024, decisión del responsable del 22-10, 22:22): última entrada del cerebro. Lleva la energía
# que ha dado lo comido en los últimos GUT_WINDOW pasos, con su signo (alga que alimenta +, alga vacía 0,
# veneno −): tanh(suma / GUT_OBS_SCALE) si env.gut_sense = 1, y 0 si no. La ventana es la de la
# plasticidad (PLASTICITY_EVERY), para que cada paso de aprendizaje vea todos los bocados desde el anterior.
# Un bocado lleno es EAT_RATE · DT = 0,5: con la escala 1, uno da 0,46 y cuatro, 0,96.
GUT_WINDOW = 4
GUT_OBS_SCALE = 1.0
V_OBS_SCALE = 10.0
CLOCK_PERIOD = 500           # pasos
C_BASAL = 0.5                # c0
C_NEURON = 0.02              # cb por neurona oculta expresada
C_MASS = 0.1                 # cs
C_MOVE = 0.002               # cm
C_ATTACK = 0.5               # ca, por unidad de fuerza de ataque y de tiempo
EAT_RATE = 5.0               # ingesta máxima por unidad de tiempo

# Ataque (fase 1): el atacante drena energía del agente más cercano en su frente
ATTACK_DAMAGE = 20.0         # energía drenada por unidad de tiempo a fuerza 1
ATTACK_REACH = 2.0           # distancia máxima entre superficies
ATTACK_HALF_ANGLE_DEG = 45.0
ATTACK_EFFICIENCY = 0.6      # fracción drenada que gana el atacante; el resto queda como carroña

# Química artificial (ADR-008): campos sobre la rejilla de recursos; unidades de energía
CHEM_NAMES = ("nutrient", "toxin", "pheromone")
EMIT_RATE = 2.0                       # emisión máxima por sustancia y unidad de tiempo
EMIT_COST = (1.0, 1.0, 0.1)           # energía por unidad emitida (nutriente y toxina la almacenan)
CHEM_DIFFUSION = (0.2, 0.2, 1.0)      # celdas²/tiempo (estable si D·dt <= 0,25)
CHEM_DECAY = (0.02, 0.05, 0.2)        # 1/tiempo; nutriente y toxina degradados vuelven como algas
TOXIN_DAMAGE = 5.0                    # energía drenada por unidad de toxina en la celda y de tiempo
CHEM_OBS_SCALE = 1.0
CHEM_GRAD_DIST = 8.0                  # distancia de muestreo para los gradientes (una celda)

# Algas estacionales (ADR-008): dos tipos en manchas; cuál es tóxico cambia al azar
TOXIC_FLIP_PROB = 0.0                 # inversión global por paso; desactivada: con 1/400 o 1/1000 la
                                      # población entera come veneno a la vez y se extingue
TOXIC_REGION_K = 2                    # franjas de toxicidad: 2 de cada régimen en el toro
TOXIC_REGION_SPEED = 5.0              # unidades de mundo por unidad de tiempo de las fronteras
# Programa temporal de toxicidad (fase 1d, docs/fase1d/diseno.md): qué alga es tóxica por parches.
TOX_MODES = {"franjas": 0, "aleatorio": 1, "periodico": 2, "fijo": 3, "uniforme": 4}
# uniforme (diseño 1d v0.9, E1b): el mismo tipo de alga es tóxico en todo el mundo y siempre; el
# fijo, en cambio, varía de un parche a otro (estable en el tiempo, no en el espacio).
TOX_PATCHES = 8                       # rejilla de 8 × 8 parches (128 × 128 unidades cada uno)
# Escalera de complejidad (ADR-014, docs/escalera/diseno.md): interruptores del mundo por condición.
# Sus valores por defecto dejan el mundo de siempre; cada peldaño enciende una sola cosa más.
REPRO_MODES = {"energia": 0, "edad": 1}
# energia: se reproduce quien supera su umbral de energía y le cede una fracción al hijo (spec).
# edad (peldaños 0 y 1, sin comida): todo adulto (edad >= MIN_REPRO_AGE) puede tener un hijo si hay
# hueco; el hijo nace con E_INIT nueva y el padre no paga nada.
NO_MAX_AGE = 2**30                    # sin vida máxima fija
LADDER_LIFESPAN = 600                 # peldaño 0: vida fija = la de un bicho quieto que solo paga el
                                      # gasto basal en el peldaño 1 (E_INIT / C_BASAL / DT)
# Curva de recuperación (diseño 1d v0.5): alga y alga tóxica ingeridas según los pasos transcurridos
# desde el último cambio del parche donde se come. Bordes de los intervalos (el último, abierto).
RECOVERY_EDGES = (8, 16, 32, 64, 128, 256, 512, 1024, 2048)
TOXIC_FACTOR = 0.5                    # comer alga tóxica resta la mitad de lo que habría sumado
                                      # (con 1,0 las islas se extinguen; ADR-008, calibración)
# Rampa (ADR-008, addendum): el alga tóxica pasa de alimentar como las demás (paso 0) a restar
# TOXIC_FACTOR × lo ingerido (desde TOXIC_RAMP_STEPS). Sin rampa, una población aleatoria, que no
# distingue algas, se extingue en 2–3 épocas y la evolución no tiene gradiente por el que empezar.
TOXIC_RAMP_STEPS = 40_000                 # 40 épocas de 1.000 pasos

# Paredes (solo en entornos de prueba de capacidad; vacías en las islas)
WALL_SAMPLES = 8             # muestras por rayo para detectar paredes

# Recursos: crecimiento logístico con Kmax en manchas derivantes (suma de ondas planas toroidales)
RESOURCE_R = 1.5                # fase 1: 1,0; ×1,5 en 2.x porque el alga tóxica reduce la comida útil (ADR-008)
RESOURCE_SEED = 0.002        # aporte mínimo para que celdas agotadas rebroten
K_MEAN = 4.0
K_WAVES = 8
K_WAVE_MAX_FREQ = 4          # números de onda enteros => periódico en el toro
K_DRIFT = 0.002              # rad / unidad de tiempo
K_CONTRAST = 0.8
# Comida dispersa (P2-buscar, ADR-022): solo hay comida donde el campo normalizado z >= K_CUT, con la
# misma altura que sin corte. None = el mundo de siempre. Es una opción de compilación (como
# REPRODUCTION) y no un campo de EnvParams: un `where` en el grafo hace que XLA reordene el cálculo
# del campo y el mundo de siempre deja de ser idéntico bit a bit.
K_CUT: float | None = None
# Coste fijo por hijo (P3-coste, ADR-023): energía que el padre gasta en construir al hijo y que nadie
# recibe, aparte de la que le cede. Solo en el modo «energia»: además de superar su umbral, el padre
# ha de poder pagarlo (tras ceder y pagar le queda energía). 0 = sin coste. Opción de compilación,
# como K_CUT, para que el mundo de siempre siga idéntico bit a bit.
REPRO_COST: float = 0.0
# P4 (decisión del responsable, 22-10): el mundo cambia a un ritmo dado. Opciones de compilación, como
# K_CUT, para que el mundo de siempre siga idéntico bit a bit (0 = apagado).
# FOOD_JUMP_PERIOD: cada tantos pasos, las manchas de comida saltan a un sitio al azar (fases nuevas de
# las ondas). La comida vieja se seca y la nueva rebrota (crecimiento logístico de siempre).
# ALGA_SWAP_PERIOD: cada tantos pasos se sortea qué alga alimenta (A o B, las que el bicho ya distingue
# por el signo del canal de recurso); la otra se come pero no da energía ni cuenta como ingesta.
# El sorteo usa una clave propia de cada mundo (sacada de sus fases), así que los mundos son independientes.
FOOD_JUMP_PERIOD: int = 0
ALGA_SWAP_PERIOD: int = 0
# FOOD_JUMP_DIST (decisión del responsable, 22-10, 12:08): si es > 0, en vez de saltar a un sitio al azar,
# en cada periodo todo el campo de comida se desplaza esta distancia (u) en una dirección al azar respecto a
# su sitio de siempre (traslación rígida: misma forma y misma comida total). Entre dos periodos seguidos
# las manchas se mueven entre 0 y 2·FOOD_JUMP_DIST (de media, ~1,27·FOOD_JUMP_DIST).
FOOD_JUMP_DIST: float = 0.0
# EAT_MOVE_FACTOR (ADR-025, «comer frena»; decisión del responsable, 23-10): mientras la salida de comer está
# encendida, el empuje se multiplica por este factor (0 = no puede moverse mientras come; el tiempo de
# manipulación de holling1959some). 1 (por defecto) = como siempre, idéntico bit a bit. La política fija del
# examen (control, ADR-011) no frena, para que su referencia no cambie.
EAT_MOVE_FACTOR: float = 1.0
# EAT_MOVE_RAMP_STEPS (decisión del responsable, 24-10): si es > 0, el freno se endurece poco a poco: el factor
# pasa de 1 a EAT_MOVE_FACTOR linealmente en estos pasos y después se queda fijo. Un cambio brusco extingue y uno
# gradual da tiempo a adaptarse (rescate evolutivo: lindsey2013evolutionary, bell2009evolutionary; evolución
# incremental: gomez1997incremental). 0 (por defecto) = freno fijo desde el principio, como en 3.1.
EAT_MOVE_RAMP_STEPS: int = 0
# ALGA_PER_AGENT (decisión del responsable, 25-10; ADR-026): si es 1, a cada bicho le alimenta una sola alga (A o B),
# sorteada al nacer con probabilidad ½ por su uid, sin relación con su padre, y para toda la vida; la otra se come
# pero no da energía ni cuenta como ingesta. Lo que conviene comer no se puede saber al nacer (C1 de
# docs/escalera/condiciones_aprendizaje.md; pontes2020evolutionary). Excluye ALGA_SWAP_PERIOD. 0 (por defecto) = apagado.
ALGA_PER_AGENT: int = 0
# K_MEAN_RAMP_STEPS (decisión del responsable, 25-10, entre las 13:25 y las 14:25; ADR-026): si es > 0, la capacidad media de las algas
# empieza en K_MEAN_RAMP_FROM × k_mean y baja linealmente hasta k_mean en estos pasos. Con la mitad de algas desde
# el principio se extinguen al arrancar y con el doble viven en el tope: rescate evolutivo, como la rampa del freno
# (lindsey2013evolutionary, bell2009evolutionary). 0 (por defecto) = sin rampa, idéntico bit a bit.
K_MEAN_RAMP_STEPS: int = 0
K_MEAN_RAMP_FROM: float = 2.0
# ALGA_PATCH_FAMILIES (decisión del responsable, 25-10, entre las 21:54 y las 21:59; ADR-027): si es 1, las K_WAVES ondas
# del campo se reparten en dos familias (las pares y las impares). Cada familia, normalizada por separado, da
# su propio campo z_A o z_B; el campo de comida usa z = max(z_A, z_B) y el alga es de tipo A donde z_A >= z_B. Así cada
# mancha (con K_CUT) es casi siempre de un solo tipo, y el color, que se ve en los rayos, dice qué hay en ella antes de
# entrar: elegir mancha por el color (todd1991exploring; C2 y C4 de docs/escalera/condiciones_aprendizaje.md).
# 0 (por defecto) = el mundo de siempre, idéntico bit a bit. Opción de compilación, como K_CUT.
ALGA_PATCH_FAMILIES: int = 0
# POISON_FACTOR (panel 05, 26-10; ADR-030, P5-d): veneno diferido. Con ALGA_PER_AGENT, si es > 0, el alga equivocada de
# cada bicho alimenta al comerla igual que la buena (la tripa la registra como buena: el reflejo engañado de García) y,
# POISON_DELAY pasos después, cobra POISON_FACTOR × la energía que dio. Con POISON_DELAY 0 el cobro llega en el mismo paso
# y la tripa ve el neto (contraste inmediato). POISON_RAMP_STEPS: el factor sube de 0 a POISON_FACTOR en esos pasos.
# 0 (por defecto) = el alga equivocada no alimenta (ADR-026), idéntico bit a bit. Opción de compilación.
POISON_FACTOR: float = 0.0
POISON_DELAY: int = 30
POISON_RAMP_STEPS: int = 0
POISON_BUFFER = 64  # pasos del búfer circular de cobros pendientes (> POISON_DELAY)

# Biogeografía: ±10 % derivado del node_id
BIOGEO_SPREAD = 0.1

# Nacimientos: tope de nacimientos por paso para vectorizar mutate+develop en lote fijo
MAX_BIRTHS_PER_STEP = 32
DEVELOP_BATCH = 64

# --- Isla ---
EPOCH_STEPS = 1000
CHECKPOINT_EVERY = 10
FROZEN_PLASTICITY_TEST_EVERY = 20
VIDEO_EVERY = 50

# --- Red P2P ---
MIGRATION_EVERY = 10
EMIGRANTS_PER_NEIGHBOR = 8
NEIGHBORS = (4, 8)
NEIGHBOR_ROTATE_EVERY = 50
MAX_IMMIGRANT_FRAC = 0.02

# --- Métricas de la fase 1 (spec §Métricas) ---
DESCRIPTOR_MIN_AGE = 100     # pasos de vida mínimos para calcular el descriptor conductual
SIGNAL_BINS = 4              # discretización de la señal en [-1, 1]
CONTEXT_BINS = 4             # nada / comida delante / pariente visto / no pariente visto
KIN_THRESHOLD = 0.8          # parentesco >= umbral => "pariente"
FOOD_AHEAD_THRESHOLD = 1.0   # recurso relativo del rayo central para "comida delante"
CLADE_DEPTH = 50             # un clado nuevo cada 50 generaciones de linaje
GENOME_DISTANCE_PAIRS = 256
NOVELTY_K = 15
NOVELTY_SAMPLE = 512         # descriptores por época para novedad y clustering
NOVELTY_THRESHOLD = 0.15     # distancia k-NN mínima para entrar al archivo
NOVELTY_MAX_ADD = 32         # altas máximas en el archivo por época
CLUSTER_K_RANGE = (2, 6)
SILHOUETTE_GROUPS = 0.3      # criterio de aceptación de la fase 1
ACTIVITY_THRESHOLD = 100.0   # Bedau-Packard: agentes·época acumulados para "actividad nueva"

# --- Salvaguardas (spec §Salvaguardas) ---
CAPABILITY_TEST_EVERY = 100
# ADR-007. Umbrales conservadores: superar cualquiera pausa la isla hasta revisión humana.
CAPABILITY_PAUSE_THRESHOLDS: dict[str, float] = {
    "comm_mi_bits": 0.5,     # información mutua señal↔contexto (máx. 2 bits)
    # ADR-011 (batería v2): la ganancia se mide frente a la MEJOR referencia (genomas aleatorios o
    # políticas fijas sin cerebro con los mismos cuerpos). Umbral de la mancha fijado por el
    # responsable (16-10-2026): un buscador programado saca ~0,34 de ventaja; las poblaciones, ~0.
    "patch_gain": 0.2,       # éxito en mancha de comida lejana − mejor referencia
    "maze_gain": 0.25,       # éxito en laberinto − mejor referencia
}
PROBE_AGENTS = 64            # agentes adultos muestreados por prueba
# Decisión del responsable (16-10-2026, ADR-013): con menos adultos la batería no se pasa y se
# aplaza a la siguiente época con muestra suficiente (en E0 saltó una pausa con 1 solo agente).
CAPABILITY_MIN_AGENTS = 32
PROBE_PATCH_STEPS = 1000
PROBE_PATCH_DIST = 90.0      # más allá del alcance máximo de los sensores (60): hay que buscar
PROBE_PATCH_RADIUS = 12.0
# Políticas fijas de referencia (empuje, giro), comiendo siempre: quieto, recto y en círculos
PROBE_CONTROLS = ((0.0, 0.0), (0.25, 0.0), (0.5, 0.0), (1.0, 0.0), (1.0, 0.1), (1.0, 0.3), (1.0, 1.0))
PROBE_MAZE_STEPS = 1000
PROBE_SUCCESS_INTAKE = 1.0   # ingesta mínima para contar éxito
PROBE_ENERGY = 100.0         # energía inicial en las pruebas (sin reproducción)
PROBE_FOOD = 4.0             # recurso por celda de comida en las pruebas

# --- Visor (spec §Persistencia: vídeo cada 50 épocas) ---
RECORD_STRIDE = 2            # se guarda 1 de cada RECORD_STRIDE pasos de la época grabada
RECORD_RES_STRIDE = 20       # campo de recursos cada RECORD_RES_STRIDE pasos
RECORD_RES_GRID = 64         # campo de recursos submuestreado a 64 × 64
