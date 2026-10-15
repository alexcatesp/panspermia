"""Constantes globales de la especificación (docs/spec.md). Única fuente de números."""

SUBSTRATE_VERSION = "1.0.0"  # major distinto => migrantes rechazados

# --- Mundo 2D (fases 0-1) ---
WORLD_L = 1024.0
DT = 0.1
RESOURCE_GRID = 128
N_RAYS = 16
RAY_CONE_DEG = 180.0
RAY_CHANNELS = 4  # distancia, recurso, agente, señal
OBS_DIM = N_RAYS * RAY_CHANNELS + 6  # + energía, velocidad(2), reloj(2), señal recibida = 70
ACT_DIM = 5  # empuje, giro, comer, atacar, señal

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
N_PRE = OBS_DIM + N_HIDDEN_MAX   # 134
N_POST = N_HIDDEN_MAX + ACT_DIM  # 69
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
C_ATTACK = 0.0               # ca (sin ataque en fase 0)
EAT_RATE = 5.0               # ingesta máxima por unidad de tiempo

# Recursos: crecimiento logístico con Kmax en manchas derivantes (suma de ondas planas toroidales)
RESOURCE_R = 0.5
RESOURCE_SEED = 0.002        # aporte mínimo para que celdas agotadas rebroten
K_MEAN = 4.0
K_WAVES = 8
K_WAVE_MAX_FREQ = 4          # números de onda enteros => periódico en el toro
K_DRIFT = 0.002              # rad / unidad de tiempo
K_CONTRAST = 0.8

# Biogeografía: ±10 % derivado del node_id
BIOGEO_SPREAD = 0.1

# Nacimientos: tope de nacimientos por paso para vectorizar mutate+develop en lote fijo
MAX_BIRTHS_PER_STEP = 16
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

# --- Salvaguardas (spec §Salvaguardas) ---
CAPABILITY_TEST_EVERY = 100
CAPABILITY_PAUSE_THRESHOLDS: dict[str, float] = {}  # definir antes de la fase 1
