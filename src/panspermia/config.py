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
