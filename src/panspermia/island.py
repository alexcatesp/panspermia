"""Motor de isla: IslandState, world_step y epoch con lax.scan bajo jit (spec §Motor de isla)."""

def init_island(seed: int, node_id: bytes):
    raise NotImplementedError

def world_step(state, _):
    """sensores → cerebro → física → comer/atacar → energía → muertes → nacimientos → plasticidad → recursos."""
    raise NotImplementedError

def epoch(state, k: int):
    """Ejecuta k pasos y devuelve (state, EpochStats)."""
    raise NotImplementedError
