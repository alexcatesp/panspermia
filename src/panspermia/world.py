"""Mundo 2D toroidal: física, recursos, sensores por rayos y energía (spec §Mundo).

Salvaguarda 1: este módulo es el ÚNICO interfaz de los agentes con algo externo, y solo expone
la simulación. No añadir aquí acceso a red, ficheros ni procesos."""

def init_resources(env, key):
    raise NotImplementedError

def sense(state):
    """Observaciones [N, OBS_DIM]."""
    raise NotImplementedError

def physics(state, actions):
    raise NotImplementedError

def energy_update(state, actions):
    raise NotImplementedError
