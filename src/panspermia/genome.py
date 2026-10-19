"""Genoma: estructura, mutación, forma canónica, hash y serialización (spec §Genoma, §Ciclo de vida).

El genoma es un pytree de arrays de tamaño fijo (topología variable mediante máscaras). Los
campos flotantes se guardan en float16 también en memoria, de modo que serializar y deserializar
es exactamente sin pérdidas. La cabecera de direccionamiento (id, parent_id, origin_node) no
forma parte del pytree: se calcula fuera de `jit` al serializar (ADR-005).

Convención de la CPPN: nodos 0..5 entradas, 6..23 ocultos, 24..31 salidas. Solo se admiten
aristas i→j con i < j y j no de entrada (orden topológico por índice, sin recurrencia).
"""
from __future__ import annotations

from dataclasses import dataclass

import blake3
import jax
import jax.numpy as jnp
import msgpack
import numpy as np
import zstandard
from flax import struct

from . import config as C

F16 = jnp.float16

_IDX = np.arange(C.CPPN_NODES)
_IS_INPUT = _IDX < C.CPPN_IN
_IS_OUTPUT = _IDX >= C.CPPN_OUT_START
_IS_HIDDEN = ~_IS_INPUT & ~_IS_OUTPUT
# Aristas permitidas por la topología: i < j y destino no de entrada.
VALID_EDGE = np.triu(np.ones((C.CPPN_NODES, C.CPPN_NODES), dtype=bool), k=1) & ~_IS_INPUT[None, :]


@struct.dataclass
class Genome:
    node_mask: jax.Array   # bool[32]
    act_id: jax.Array      # int8[32]
    bias: jax.Array        # f16[32]
    W: jax.Array           # f16[32, 32]
    W_mask: jax.Array      # bool[32, 32]
    hid_mask: jax.Array    # bool[64]
    hid_pos: jax.Array     # f16[64, 2]
    hid_type: jax.Array    # bool[64]  (True = moduladora)
    body: jax.Array        # f16[8]
    life: jax.Array        # f16[4]: umbral repro (bruto), fracción hijo (bruto), sigma, tasa estructural
    generation: jax.Array  # uint32[]


_FIELDS = (
    # nombre, dtype, forma
    ("node_mask", np.bool_, (C.CPPN_NODES,)),
    ("act_id", np.int8, (C.CPPN_NODES,)),
    ("bias", np.float16, (C.CPPN_NODES,)),
    ("W", np.float16, (C.CPPN_NODES, C.CPPN_NODES)),
    ("W_mask", np.bool_, (C.CPPN_NODES, C.CPPN_NODES)),
    ("hid_mask", np.bool_, (C.N_HIDDEN_MAX,)),
    ("hid_pos", np.float16, (C.N_HIDDEN_MAX, 2)),
    ("hid_type", np.bool_, (C.N_HIDDEN_MAX,)),
    ("body", np.float16, (C.BODY_GENES,)),
    ("life", np.float16, (C.LIFE_GENES,)),
)


@dataclass(frozen=True)
class GenomeMeta:
    """Cabecera de un genoma serializado (fuera del pytree)."""
    id: bytes
    parent_id: bytes = bytes(16)
    origin_node: bytes = bytes(16)
    substrate_version: str = C.SUBSTRATE_VERSION


# ---------------------------------------------------------------------------------------------
# Forma canónica
# ---------------------------------------------------------------------------------------------

def canonical(genome: Genome) -> Genome:
    """Pone a cero pesos enmascarados y neutraliza nodos inactivos antes del hash.

    Además fuerza las invariantes estructurales: entradas y salidas siempre activas, aristas solo
    entre nodos activos y permitidas por el orden topológico.
    """
    always = jnp.asarray(_IS_INPUT | _IS_OUTPUT)
    node_mask = genome.node_mask | always
    W_mask = genome.W_mask & jnp.asarray(VALID_EDGE) & node_mask[:, None] & node_mask[None, :]
    W = jnp.where(W_mask, genome.W, jnp.zeros((), F16))
    computes = node_mask & ~jnp.asarray(_IS_INPUT)
    bias = jnp.where(computes, genome.bias, jnp.zeros((), F16))
    act_id = jnp.where(computes, genome.act_id, jnp.int8(C.ACT_IDENTITY)).astype(jnp.int8)
    return genome.replace(node_mask=node_mask, W_mask=W_mask, W=W, bias=bias, act_id=act_id)


# ---------------------------------------------------------------------------------------------
# Creación y mutación (puras; compatibles con jit/vmap)
# ---------------------------------------------------------------------------------------------

def crossover(a: Genome, b: Genome, key: jax.Array) -> Genome:
    """Cruce (ADR-017, corregido en ADR-018): la CPPN entera viene de `a` o de `b` al 50 % (un bloque
    ligado, como un cromosoma); cada hueco de neurona y cada gen de cuerpo y de vida, de uno u otro.

    La versión 2.4 cruzaba la CPPN nodo a nodo por índice, como si los índices fueran marcas históricas.
    No lo son: el mismo índice nace de divisiones distintas en cada linaje, y un nodo heredaba sus
    aristas de entrada de un progenitor y las de salida del otro (83–88 % de nodos sin salida en P0;
    "convenciones en competencia", Stanley y Miikkulainen 2002). Los huecos de neurona no tienen ese
    problema: no guardan aristas, sus pesos salen de la CPPN según su posición."""
    k = jax.random.split(key, 4)
    n = jax.random.bernoulli(k[0], 0.5)
    h = jax.random.bernoulli(k[1], 0.5, (C.N_HIDDEN_MAX,))
    bo = jax.random.bernoulli(k[2], 0.5, (C.BODY_GENES,))
    li = jax.random.bernoulli(k[3], 0.5, (C.LIFE_GENES,))

    def pick(m, x, y):
        return jnp.where(m, y, x)

    child = Genome(
        node_mask=pick(n, a.node_mask, b.node_mask), act_id=pick(n, a.act_id, b.act_id),
        bias=pick(n, a.bias, b.bias), W=pick(n, a.W, b.W), W_mask=pick(n, a.W_mask, b.W_mask),
        hid_mask=pick(h, a.hid_mask, b.hid_mask), hid_pos=pick(h[:, None], a.hid_pos, b.hid_pos),
        hid_type=pick(h, a.hid_type, b.hid_type), body=pick(bo, a.body, b.body), life=pick(li, a.life, b.life),
        generation=jnp.maximum(a.generation, b.generation),
    )
    return canonical(child)


def random_minimal(key: jax.Array) -> Genome:
    """Genoma inicial: CPPN mínima (entradas→salidas) y N_HIDDEN_INIT neuronas."""
    k = jax.random.split(key, 8)
    n = C.CPPN_NODES
    node_mask = jnp.asarray(_IS_INPUT | _IS_OUTPUT)
    W_mask = jnp.asarray(_IS_INPUT[:, None] & _IS_OUTPUT[None, :])
    W = (C.CPPN_INIT_W_STD * jax.random.normal(k[0], (n, n))).astype(F16)
    act_id = jax.random.randint(k[1], (n,), 0, C.N_ACTIVATIONS).astype(jnp.int8)
    hid_mask = jnp.arange(C.N_HIDDEN_MAX) < C.N_HIDDEN_INIT
    hid_pos = jax.random.uniform(k[2], (C.N_HIDDEN_MAX, 2), minval=-1.0, maxval=1.0).astype(F16)
    hid_type = jax.random.bernoulli(k[3], 0.5, (C.N_HIDDEN_MAX,))
    body = (0.5 * jax.random.normal(k[4], (C.BODY_GENES,))).astype(F16)
    life_raw = 0.5 * jax.random.normal(k[5], (2,))
    life = jnp.concatenate([life_raw, jnp.array([C.SIGMA_INIT, 1.0])]).astype(F16)
    g = Genome(
        node_mask=node_mask, act_id=act_id, bias=jnp.zeros((n,), F16), W=W, W_mask=W_mask,
        hid_mask=hid_mask, hid_pos=hid_pos, hid_type=hid_type, body=body, life=life,
        generation=jnp.uint32(0),
    )
    return canonical(g)


def _choose(key: jax.Array, mask: jax.Array) -> tuple[jax.Array, jax.Array]:
    """Índice uniforme (aplanado) entre los True de `mask`; devuelve (idx, hay_alguno)."""
    scores = jnp.where(mask.ravel(), jax.random.uniform(key, (mask.size,)), -1.0)
    return jnp.argmax(scores), jnp.any(mask)


def _clip_f16(x: jax.Array, lo: float, hi: float) -> jax.Array:
    return jnp.clip(x, lo, hi).astype(F16)


def mutate(genome: Genome, key: jax.Array) -> Genome:
    """Aplica los operadores de mutación de la spec. Pura, compatible con jit/vmap."""
    g = genome
    n = C.CPPN_NODES
    ks = jax.random.split(key, 24)
    life = g.life.astype(jnp.float32)

    # Autoadaptación de sigma (prob. 1)
    sigma = life[2] * jnp.exp(C.SIGMA_TAU * jax.random.normal(ks[0]))
    sigma = jnp.clip(sigma, *C.SIGMA_BOUNDS)
    rate = jnp.clip(life[3], *C.STRUCT_RATE_BOUNDS)
    if C.MUTATION_RATES == "fijas":  # ADR-016: constantes del mundo, no genes
        sigma, rate = jnp.float32(C.SIGMA_INIT), jnp.float32(1.0)
    elif C.MUTATION_RATES != "evolutivas":
        raise ValueError(f"MUTATION_RATES desconocida: {C.MUTATION_RATES}")
    if C.CPPN_MUTATION == "nest":
        p_add, p_del, p_split, p_del_node = C.P_ADD_EDGE, C.P_DEL_EDGE, C.P_SPLIT_EDGE, C.P_DEL_NODE
    elif C.CPPN_MUTATION == "neutral":
        r = C.CPPN_NEUTRAL_RATES
        p_add, p_del, p_split, p_del_node = r["add_edge"], r["del_edge"], r["split"], r["del_node"]
    else:
        raise ValueError(f"CPPN_MUTATION desconocida: {C.CPPN_MUTATION}")

    # Perturbación de parámetros activos (prob. 1)
    noise = lambda k, shape: sigma * jax.random.normal(k, shape)
    W = jnp.where(g.W_mask, g.W.astype(jnp.float32) + noise(ks[1], (n, n)), 0.0)
    computes = g.node_mask & ~jnp.asarray(_IS_INPUT)
    bias = jnp.where(computes, g.bias.astype(jnp.float32) + noise(ks[2], (n,)), 0.0)
    body = g.body.astype(jnp.float32) + noise(ks[3], (C.BODY_GENES,))
    life_new = life.at[0:2].add(noise(ks[4], (2,)))
    if C.MUTATION_RATES == "evolutivas":
        life_new = life_new.at[3].add(noise(ks[5], ()))
    life_new = life_new.at[2].set(sigma)

    node_mask, W_mask, act_id = g.node_mask, g.W_mask, g.act_id
    hid_mask, hid_pos, hid_type = g.hid_mask, g.hid_pos.astype(jnp.float32), g.hid_type

    def happens(k, p):
        return jax.random.uniform(k) < jnp.minimum(1.0, p * rate)

    valid_edge = jnp.asarray(VALID_EDGE)

    # Añadir conexión CPPN
    free_edges = valid_edge & ~W_mask & node_mask[:, None] & node_mask[None, :]
    e, ok = _choose(ks[6], free_edges)
    do = happens(ks[7], p_add) & ok
    i, j = e // n, e % n
    W_mask = W_mask.at[i, j].set(jnp.where(do, True, W_mask[i, j]))
    W = W.at[i, j].set(jnp.where(do, jax.random.normal(ks[8]), W[i, j]))

    # Eliminar conexión CPPN
    e, ok = _choose(ks[9], W_mask)
    do = happens(ks[10], p_del) & ok
    i, j = e // n, e % n
    W_mask = W_mask.at[i, j].set(jnp.where(do, False, W_mask[i, j]))
    W = W.at[i, j].set(jnp.where(do, 0.0, W[i, j]))

    # Dividir conexión: activa un nodo oculto libre k con i < k < j
    e, ok = _choose(ks[11], W_mask)
    i, j = e // n, e % n
    idx = jnp.arange(n)
    free_k = jnp.asarray(_IS_HIDDEN) & ~node_mask & (idx > i) & (idx < j)
    k_node, ok_k = _choose(ks[12], free_k)
    do = happens(ks[13], p_split) & ok & ok_k
    w_ij = W[i, j]
    node_mask = node_mask.at[k_node].set(jnp.where(do, True, node_mask[k_node]))
    bias = bias.at[k_node].set(jnp.where(do, 0.0, bias[k_node]))
    new_act = jax.random.randint(ks[14], (), 0, C.N_ACTIVATIONS).astype(jnp.int8)
    act_id = act_id.at[k_node].set(jnp.where(do, new_act, act_id[k_node]))
    W_mask = W_mask.at[i, j].set(jnp.where(do, False, W_mask[i, j]))
    W = W.at[i, j].set(jnp.where(do, 0.0, W[i, j]))
    W_mask = W_mask.at[i, k_node].set(jnp.where(do, True, W_mask[i, k_node]))
    W = W.at[i, k_node].set(jnp.where(do, 1.0, W[i, k_node]))
    W_mask = W_mask.at[k_node, j].set(jnp.where(do, True, W_mask[k_node, j]))
    W = W.at[k_node, j].set(jnp.where(do, w_ij, W[k_node, j]))

    # Eliminar nodo CPPN oculto (la forma canónica limpia sus aristas)
    k_node, ok = _choose(ks[15], jnp.asarray(_IS_HIDDEN) & node_mask)
    do = happens(ks[16], p_del_node) & ok
    node_mask = node_mask.at[k_node].set(jnp.where(do, False, node_mask[k_node]))

    # Cambiar activación de un nodo activo no de entrada
    k_node, ok = _choose(ks[17], node_mask & ~jnp.asarray(_IS_INPUT))
    do = happens(ks[18], C.P_CHANGE_ACT) & ok
    new_act = jax.random.randint(ks[19], (), 0, C.N_ACTIVATIONS).astype(jnp.int8)
    act_id = act_id.at[k_node].set(jnp.where(do, new_act, act_id[k_node]))

    # Expresar o silenciar neurona oculta (física elegible, ADR-015; "nest" es la de la spec v1)
    kk = jax.random.split(ks[20], 8)
    mode = C.NEURON_MUTATION
    if mode == "nest":  # invierte un hueco al azar: deriva hacia la mitad sin selección
        h = jax.random.randint(kk[0], (), 0, C.N_HIDDEN_MAX)
        do = happens(kk[1], C.P_TOGGLE_NEURON)
        hid_mask = hid_mask.at[h].set(jnp.where(do, ~hid_mask[h], hid_mask[h]))
    elif mode in C.NEURON_MUTATION_P_ON:  # primero encender o apagar; después a qué neurona
        kn = jax.random.split(jax.random.fold_in(ks[20], 0x6E6575), 3)
        on = jax.random.uniform(kn[0]) < C.NEURON_MUTATION_P_ON[mode]
        h_off, ok_off = _choose(kn[1], ~hid_mask)
        h_on, ok_on = _choose(kn[2], hid_mask)
        h = jnp.where(on, h_off, h_on)
        do = happens(kk[1], C.P_TOGGLE_NEURON) & jnp.where(on, ok_off, ok_on)
        hid_mask = hid_mask.at[h].set(jnp.where(do, on, hid_mask[h]))
    else:
        raise ValueError(f"NEURON_MUTATION desconocida: {mode}")

    # Duplicar neurona: copia una activa en un hueco libre con posición desplazada
    src, ok_s = _choose(kk[2], hid_mask)
    dst, ok_d = _choose(kk[3], ~hid_mask)
    do = happens(kk[4], C.P_DUP_NEURON) & ok_s & ok_d
    new_pos = jnp.clip(hid_pos[src] + C.NEURON_MOVE_SIGMA * jax.random.normal(kk[5], (2,)), -1, 1)
    hid_mask = hid_mask.at[dst].set(jnp.where(do, True, hid_mask[dst]))
    hid_pos = hid_pos.at[dst].set(jnp.where(do, new_pos, hid_pos[dst]))
    hid_type = hid_type.at[dst].set(jnp.where(do, hid_type[src], hid_type[dst]))

    if mode != "nest":  # perder neurona: la otra cara de duplicar (Lynch y Conery 2000)
        kd = jax.random.split(jax.random.fold_in(ks[20], 0x64656C), 2)
        victim, ok_v = _choose(kd[0], hid_mask)
        do = happens(kd[1], C.P_DEL_NEURON[mode]) & ok_v
        hid_mask = hid_mask.at[victim].set(jnp.where(do, False, hid_mask[victim]))

    # Mover neurona
    m, ok = _choose(kk[6], hid_mask)
    do = happens(kk[7], C.P_MOVE_NEURON) & ok
    moved = jnp.clip(hid_pos[m] + C.NEURON_MOVE_SIGMA * jax.random.normal(ks[21], (2,)), -1, 1)
    hid_pos = hid_pos.at[m].set(jnp.where(do, moved, hid_pos[m]))

    b = C.GENE_BOUND
    life_out = jnp.stack([
        jnp.clip(life_new[0], -b, b),
        jnp.clip(life_new[1], -b, b),
        jnp.clip(life_new[2], *C.SIGMA_BOUNDS),
        jnp.clip(life_new[3], *C.STRUCT_RATE_BOUNDS),
    ]).astype(F16)
    child = Genome(
        node_mask=node_mask, act_id=act_id, bias=_clip_f16(bias, -b, b), W=_clip_f16(W, -b, b),
        W_mask=W_mask, hid_mask=hid_mask, hid_pos=_clip_f16(hid_pos, -1.0, 1.0),
        hid_type=hid_type, body=_clip_f16(body, -b, b), life=life_out,
        generation=(g.generation + 1).astype(jnp.uint32),
    )
    # sigma en f16 puede redondear fuera de los límites; se reajusta tras el cast
    child = child.replace(life=child.life.at[2].set(
        jnp.clip(child.life[2], np.float16(C.SIGMA_BOUNDS[0]), np.float16(C.SIGMA_BOUNDS[1]))))
    return canonical(child)


# ---------------------------------------------------------------------------------------------
# Serialización, hash y validación (fuera de jit; numpy)
# ---------------------------------------------------------------------------------------------

def _np(genome: Genome) -> dict[str, np.ndarray]:
    out = {}
    for name, dtype, shape in _FIELDS:
        a = np.asarray(getattr(genome, name))
        if a.dtype != dtype or a.shape != shape:
            raise ValueError(f"campo {name}: esperado {dtype}{shape}, recibido {a.dtype}{a.shape}")
        out[name] = a
    return out


def _encode_field(a: np.ndarray) -> bytes:
    if a.dtype == np.bool_:
        return np.packbits(a.ravel(), bitorder="little").tobytes()
    return a.astype(a.dtype.newbyteorder("<")).tobytes()


def _decode_field(raw: bytes, dtype, shape) -> np.ndarray:
    size = int(np.prod(shape))
    if dtype == np.bool_:
        expected = (size + 7) // 8
        if len(raw) != expected:
            raise ValueError("longitud de máscara incorrecta")
        bits = np.unpackbits(np.frombuffer(raw, np.uint8), bitorder="little")
        if bits[size:].any():
            raise ValueError("bits de relleno no nulos")
        return bits[:size].astype(bool).reshape(shape)
    dt = np.dtype(dtype).newbyteorder("<")
    if len(raw) != size * dt.itemsize:
        raise ValueError("longitud de campo incorrecta")
    return np.frombuffer(raw, dt).astype(dtype).reshape(shape)


def canonical_np(a: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    """Equivalente numpy de `canonical` para la ruta de serialización (evita despachar a la GPU)."""
    node_mask = a["node_mask"] | _IS_INPUT | _IS_OUTPUT
    W_mask = a["W_mask"] & VALID_EDGE & node_mask[:, None] & node_mask[None, :]
    computes = node_mask & ~_IS_INPUT
    out = dict(a)
    out.update(
        node_mask=node_mask, W_mask=W_mask,
        W=np.where(W_mask, a["W"], np.float16(0)),
        bias=np.where(computes, a["bias"], np.float16(0)),
        act_id=np.where(computes, a["act_id"], np.int8(C.ACT_IDENTITY)).astype(np.int8),
    )
    return out


def _payload(arrays: dict[str, np.ndarray]) -> bytes:
    return msgpack.packb([_encode_field(arrays[name]) for name, _, _ in _FIELDS], use_bin_type=True)


def _major(version: str) -> str:
    return version.split(".")[0]


def genome_id(genome: Genome) -> bytes:
    """BLAKE3 (16 B) de la forma canónica serializada (solo contenido, sin cabecera)."""
    return _hash(canonical_np(_np(genome)))


def _hash(canonical_arrays: dict[str, np.ndarray]) -> bytes:
    domain = f"panspermia-genome-v{_major(C.SUBSTRATE_VERSION)}".encode()
    return blake3.blake3(domain + _payload(canonical_arrays)).digest(length=16)


def to_bytes(genome: Genome, *, parent_id: bytes = bytes(16), origin_node: bytes = bytes(16)) -> bytes:
    """msgpack con claves fijas, f16 little-endian, zstd. <= GENOME_MAX_BYTES."""
    if len(parent_id) != 16 or len(origin_node) != 16:
        raise ValueError("parent_id y origin_node deben medir 16 B")
    arrays = _np(genome)
    doc = {
        "v": C.SUBSTRATE_VERSION,
        "id": _hash(canonical_np(arrays)),
        "parent": parent_id,
        "origin": origin_node,
        "gen": int(np.asarray(genome.generation)),
        "data": _payload(arrays),
    }
    blob = zstandard.ZstdCompressor(level=19).compress(msgpack.packb(doc, use_bin_type=True))
    if len(blob) > C.GENOME_MAX_BYTES:
        raise ValueError(f"genoma serializado de {len(blob)} B > {C.GENOME_MAX_BYTES} B")
    return blob


_DOC_KEYS = ("v", "id", "parent", "origin", "gen", "data")


def from_bytes(blob: bytes) -> tuple[Genome, GenomeMeta]:
    """Deserializa y VALIDA esquema y rangos; lanza ValueError ante cualquier anomalía."""
    if not isinstance(blob, (bytes, bytearray)) or len(blob) > C.GENOME_MAX_BYTES:
        raise ValueError("blob ausente o mayor que GENOME_MAX_BYTES")
    try:
        raw = zstandard.ZstdDecompressor().decompress(
            bytes(blob), max_output_size=C.GENOME_DECOMPRESSED_MAX)
        doc = msgpack.unpackb(raw, raw=False, strict_map_key=True, max_bin_len=C.GENOME_DECOMPRESSED_MAX)
    except Exception as exc:  # zstd/msgpack lanzan tipos variados
        raise ValueError(f"blob ilegible: {exc}") from exc
    if not isinstance(doc, dict) or tuple(doc.keys()) != _DOC_KEYS:
        raise ValueError("claves de cabecera incorrectas")
    version = doc["v"]
    if not isinstance(version, str) or _major(version) != _major(C.SUBSTRATE_VERSION):
        raise ValueError(f"versión de sustrato incompatible: {version!r}")
    for k in ("id", "parent", "origin"):
        if not isinstance(doc[k], bytes) or len(doc[k]) != 16:
            raise ValueError(f"campo {k} debe ser bytes de 16")
    gen = doc["gen"]
    if not isinstance(gen, int) or isinstance(gen, bool) or not 0 <= gen < 2**32:
        raise ValueError("generation fuera de rango")
    try:
        parts = msgpack.unpackb(doc["data"], raw=False)
    except Exception as exc:
        raise ValueError(f"datos ilegibles: {exc}") from exc
    if not isinstance(parts, list) or len(parts) != len(_FIELDS):
        raise ValueError("número de campos incorrecto")
    arrays = {}
    for (name, dtype, shape), part in zip(_FIELDS, parts):
        if not isinstance(part, bytes):
            raise ValueError(f"campo {name} no es binario")
        arrays[name] = _decode_field(part, dtype, shape)
    _validate_ranges(arrays)
    canon = canonical_np(arrays)
    if any(canon[k].tobytes() != arrays[k].tobytes() for k in arrays):
        raise ValueError("genoma no canónico")
    if _hash(arrays) != doc["id"]:
        raise ValueError("hash incoherente con id")
    g = Genome(**arrays, generation=np.uint32(gen))
    return g, GenomeMeta(id=doc["id"], parent_id=doc["parent"], origin_node=doc["origin"],
                         substrate_version=version)


def _validate_ranges(a: dict[str, np.ndarray]) -> None:
    for name in ("bias", "W", "hid_pos", "body", "life"):
        if not np.all(np.isfinite(a[name].astype(np.float32))):
            raise ValueError(f"{name} contiene NaN o Inf")
    b = C.GENE_BOUND
    if np.any(np.abs(a["W"].astype(np.float32)) > b) or np.any(np.abs(a["bias"].astype(np.float32)) > b):
        raise ValueError("pesos o sesgos de la CPPN fuera de límites")
    if np.any(np.abs(a["body"].astype(np.float32)) > b):
        raise ValueError("genes de cuerpo fuera de límites")
    if np.any(np.abs(a["hid_pos"].astype(np.float32)) > 1.0):
        raise ValueError("posiciones de neuronas fuera de [-1, 1]")
    if np.any(a["act_id"] < 0) or np.any(a["act_id"] >= C.N_ACTIVATIONS):
        raise ValueError("act_id fuera de rango")
    life = a["life"].astype(np.float32)
    lo, hi = np.float16(C.SIGMA_BOUNDS[0]), np.float16(C.SIGMA_BOUNDS[1])
    if np.any(np.abs(life[:2]) > b) or not (lo <= life[2] <= hi):
        raise ValueError("genes de vida fuera de límites")
    if not (C.STRUCT_RATE_BOUNDS[0] <= life[3] <= C.STRUCT_RATE_BOUNDS[1]):
        raise ValueError("tasa estructural fuera de límites")


def stack(genomes: list[Genome]) -> Genome:
    """Apila genomas individuales en un lote con eje N delante."""
    return jax.tree.map(lambda *xs: jnp.stack(xs), *genomes)


def index(genomes: Genome, i: int) -> Genome:
    """Extrae el genoma i de un lote."""
    return jax.tree.map(lambda x: x[i], genomes)
