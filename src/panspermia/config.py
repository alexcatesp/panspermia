"""Constantes globales de la especificación (docs/spec.md). Única fuente de números."""

SUBSTRATE_VERSION = "2.0.0"  # major distinto => migrantes rechazados (2.x: química + algas estacionales, ADR-008)

# --- Mundo 2D (fases 0-1) ---
WORLD_L = 1024.0
DT = 0.1
RESOURCE_GRID = 128
N_RAYS = 16
RAY_CONE_DEG = 180.0
RAY_CHANNELS = 4  # distancia, recurso (con signo según tipo de alga), agente, señal
N_CHEM = 3        # sustancias: nutriente, toxina, feromona (ADR-008)
CHEM_OBS = 3 * N_CHEM  # por sustancia: concentración local, gradiente adelante y lateral
OBS_DIM = N_RAYS * RAY_CHANNELS + 6 + CHEM_OBS  # 64 + energía, vel(2), reloj(2), señal + 9 = 79
ACT_DIM = 5 + N_CHEM  # empuje, giro, comer, atacar, señal, emitir nutriente/toxina/feromona = 8

# --- Población ---
N_MAX = 4096
N_INIT = 512
N_MIN_REINJECT = 64
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
TOXIC_FLIP_PROB = 1.0 / 400           # por paso (proceso sin memoria: no predecible por reloj)
TOXIC_FACTOR = 1.0                    # comer alga tóxica resta lo que habría sumado

# Paredes (solo en entornos de prueba de capacidad; vacías en las islas)
WALL_SAMPLES = 8             # muestras por rayo para detectar paredes

# Recursos: crecimiento logístico con Kmax en manchas derivantes (suma de ondas planas toroidales)
RESOURCE_R = 1.0
RESOURCE_SEED = 0.002        # aporte mínimo para que celdas agotadas rebroten
K_MEAN = 4.0
K_WAVES = 8
K_WAVE_MAX_FREQ = 4          # números de onda enteros => periódico en el toro
K_DRIFT = 0.002              # rad / unidad de tiempo
K_CONTRAST = 0.8

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
    "ring_gain": 0.5,        # éxito en comida en anillo − éxito de genomas aleatorios
    "maze_gain": 0.25,       # éxito en laberinto − éxito de genomas aleatorios
}
PROBE_AGENTS = 64            # agentes adultos muestreados por prueba
PROBE_RING_STEPS = 500
PROBE_MAZE_STEPS = 1000
PROBE_SUCCESS_INTAKE = 1.0   # ingesta mínima para contar éxito
PROBE_ENERGY = 100.0         # energía inicial en las pruebas (sin reproducción)
PROBE_FOOD = 4.0             # recurso por celda de comida en las pruebas
PROBE_RING_RADIUS = (120.0, 136.0)

# --- Visor (spec §Persistencia: vídeo cada 50 épocas) ---
RECORD_STRIDE = 2            # se guarda 1 de cada RECORD_STRIDE pasos de la época grabada
RECORD_RES_STRIDE = 20       # campo de recursos cada RECORD_RES_STRIDE pasos
RECORD_RES_GRID = 64         # campo de recursos submuestreado a 64 × 64
