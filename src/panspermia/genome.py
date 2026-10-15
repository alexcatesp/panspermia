"""Genoma: estructura, mutación, forma canónica, hash y serialización (spec §Genoma, §Ciclo de vida)."""

def random_minimal(key):
    """Genoma inicial: CPPN mínima (entradas→salidas) y N_HIDDEN_INIT neuronas."""
    raise NotImplementedError

def mutate(genome, key):
    """Aplica los operadores de mutación de la spec. Pura, compatible con jit/vmap."""
    raise NotImplementedError

def canonical(genome):
    """Pone a cero pesos enmascarados y neutraliza nodos inactivos antes del hash."""
    raise NotImplementedError

def genome_id(genome) -> bytes:
    """BLAKE3 (16 B) de la forma canónica serializada."""
    raise NotImplementedError

def to_bytes(genome) -> bytes:
    """msgpack con claves fijas, f16 little-endian, zstd. <= GENOME_MAX_BYTES."""
    raise NotImplementedError

def from_bytes(blob: bytes):
    """Deserializa y VALIDA esquema y rangos; lanza ValueError ante cualquier anomalía."""
    raise NotImplementedError
