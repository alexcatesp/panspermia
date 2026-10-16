"""Criterios de aceptación de la fase 0 (spec §Fases)."""
import jax
import jax.numpy as jnp
import numpy as np
import pytest

from panspermia import config, island
from panspermia import genome as G
from panspermia.develop import develop


def _leaves_bitwise_equal(a, b) -> bool:
    la, lb = jax.tree.leaves(a), jax.tree.leaves(b)
    return len(la) == len(lb) and all(
        x.shape == y.shape and x.dtype == y.dtype
        and np.asarray(x).tobytes() == np.asarray(y).tobytes()
        for x, y in zip(la, lb))


def _mutated_population(n_lineages: int, n_generations: int, seed: int = 0) -> G.Genome:
    """n_lineages × n_generations genomas: cada linaje muta en cadena desde un genoma mínimo."""
    k0, k1 = jax.random.split(jax.random.PRNGKey(seed))
    roots = jax.vmap(G.random_minimal)(jax.random.split(k0, n_lineages))

    def chain(g, k):
        child = jax.vmap(G.mutate)(g, jax.random.split(k, n_lineages))
        return child, child

    _, hist = jax.jit(lambda r, ks: jax.lax.scan(chain, r, ks))(
        roots, jax.random.split(k1, n_generations))
    return jax.tree.map(lambda x: x.reshape((-1,) + x.shape[2:]), hist)


def test_obs_dims_match_spec():
    """Sustrato 2.x (ADR-008): 70 observaciones de la spec v1 + 9 químicas; 5 + 3 acciones."""
    assert config.OBS_DIM == 79 and config.ACT_DIM == 8
    assert config.N_PRE == 143 and config.N_POST == 72


def test_genome_roundtrip_10k_mutated():
    """Ida y vuelta sin pérdidas sobre 10^4 genomas mutados; tamaño <= GENOME_MAX_BYTES."""
    pop = jax.device_get(_mutated_population(100, 100))
    sizes = []
    for i in range(10_000):
        g = G.index(pop, i)
        blob = G.to_bytes(g, parent_id=bytes(range(16)), origin_node=b"\x01" * 16)
        sizes.append(len(blob))
        g2, meta = G.from_bytes(blob)
        assert _leaves_bitwise_equal(g, g2), f"genoma {i} distinto tras ida y vuelta"
        assert meta.id == G.genome_id(g)
        assert meta.parent_id == bytes(range(16)) and meta.origin_node == b"\x01" * 16
    assert max(sizes) <= config.GENOME_MAX_BYTES


def test_mutation_changes_structure():
    """Tras 100 generaciones aparecen nodos, aristas y neuronas nuevas (los operadores actúan)."""
    pop = _mutated_population(100, 100)
    last = jax.tree.map(lambda x: x[-100:], pop)
    assert int(jnp.max(jnp.sum(last.node_mask, -1))) > config.CPPN_IN + config.CPPN_OUT
    assert int(jnp.max(jnp.sum(last.hid_mask, -1))) > config.N_HIDDEN_INIT
    assert int(jnp.max(last.generation)) == 100


def _valid_blob() -> tuple[G.Genome, bytes]:
    g = G.random_minimal(jax.random.PRNGKey(1))
    for i in range(20):
        g = G.mutate(g, jax.random.PRNGKey(100 + i))
    return g, G.to_bytes(g)


def _forge(g: G.Genome, *, fix_id: bool = True, **overrides) -> bytes:
    """Serializa a mano un genoma alterado saltándose las comprobaciones de to_bytes."""
    import msgpack
    import zstandard
    arrays = {name: np.asarray(getattr(g, name)) for name, _, _ in G._FIELDS}
    arrays.update(overrides)
    data = msgpack.packb([G._encode_field(arrays[name]) for name, _, _ in G._FIELDS],
                         use_bin_type=True)
    import blake3
    gid = blake3.blake3(b"panspermia-genome-v1" + data).digest(length=16) if fix_id else bytes(16)
    doc = {"v": config.SUBSTRATE_VERSION, "id": gid, "parent": bytes(16), "origin": bytes(16),
           "gen": 0, "data": data}
    return zstandard.ZstdCompressor().compress(msgpack.packb(doc, use_bin_type=True))


def test_genome_rejects_invalid():
    """NaN/Inf, formas erróneas, rangos fuera de límites o hash incoherente => ValueError."""
    g, blob = _valid_blob()
    G.from_bytes(blob)  # el válido pasa
    W = np.asarray(g.W).copy()
    i, j = np.argwhere(np.asarray(g.W_mask))[0]
    bad = {}
    W_nan = W.copy(); W_nan[i, j] = np.nan; bad["nan"] = _forge(g, W=W_nan)
    W_inf = W.copy(); W_inf[i, j] = np.inf; bad["inf"] = _forge(g, W=W_inf)
    W_big = W.copy(); W_big[i, j] = 100; bad["fuera_rango"] = _forge(g, W=W_big)
    bad["forma"] = _forge(g, body=np.zeros(7, np.float16))
    bad["act"] = _forge(g, act_id=np.full(32, 9, np.int8))
    pos = np.asarray(g.hid_pos).copy(); pos[0, 0] = 2.0; bad["hid_pos"] = _forge(g, hid_pos=pos)
    life = np.asarray(g.life).copy(); life[2] = 0.9; bad["sigma"] = _forge(g, life=life)
    W_nc = W.copy(); W_nc[0, 1] = 1.0; bad["no_canonico"] = _forge(g, W=W_nc)
    bad["hash"] = _forge(g, fix_id=False)
    bad["basura"] = b"\x28\xb5\x2f\xfd" + b"\x00" * 50
    bad["vacio"] = b""
    bad["grande"] = b"\x00" * (config.GENOME_MAX_BYTES + 1)
    for name, b in bad.items():
        with pytest.raises(ValueError):
            G.from_bytes(b)
            pytest.fail(f"aceptado: {name}")


def test_genome_rejects_other_major_version():
    import msgpack
    import zstandard
    _, blob = _valid_blob()
    doc = msgpack.unpackb(zstandard.ZstdDecompressor().decompress(blob), raw=False)
    doc["v"] = f"{int(config.SUBSTRATE_VERSION.split('.')[0]) + 1}.0.0"
    with pytest.raises(ValueError):
        G.from_bytes(zstandard.ZstdCompressor().compress(msgpack.packb(doc, use_bin_type=True)))


def test_develop_deterministic():
    """develop(g) produce el mismo fenotipo bit a bit en ejecuciones repetidas."""
    g, _ = _valid_blob()
    f = jax.jit(develop)
    p1 = jax.device_get(f(g))
    p2 = jax.device_get(f(g))
    p3 = jax.device_get(jax.jit(develop)(g))
    assert _leaves_bitwise_equal(p1, p2) and _leaves_bitwise_equal(p1, p3)
    assert p1.w0.shape == (config.N_PRE, config.N_POST) and p1.w0.dtype == np.float16


def _run(seed: int, epochs: int, k: int, n_max: int = config.N_MAX, n_init: int = config.N_INIT):
    s = island.init_island(seed, b"test-node", n_max=n_max, n_init=n_init)
    for _ in range(epochs):
        s, _ = island.epoch(s, k)
    return jax.device_get(s)


def test_island_bitwise_determinism_10_epochs():
    """Misma semilla => estado idéntico bit a bit tras 10 épocas."""
    a = _run(0, 10, config.EPOCH_STEPS)
    b = _run(0, 10, config.EPOCH_STEPS)
    assert int(a.step) == 10 * config.EPOCH_STEPS
    assert _leaves_bitwise_equal(a, b)


def test_epoch_split_invariance():
    """La clave por paso es fold_in(key, step): 2 épocas de k == 1 época de 2k (bit a bit)."""
    a = _run(3, 2, 100, n_max=256, n_init=64)
    b = _run(3, 1, 200, n_max=256, n_init=64)
    # comm_hist es un acumulador de observación que se reinicia en cada época por diseño
    assert _leaves_bitwise_equal(a.replace(comm_hist=None), b.replace(comm_hist=None))


def test_different_seeds_differ():
    a = _run(1, 1, 50, n_max=128, n_init=32)
    b = _run(2, 1, 50, n_max=128, n_init=32)
    assert not np.array_equal(a.pos, b.pos)


@pytest.mark.slow
def test_no_extinction_100_epochs_4_of_5_seeds():
    """>= 100 épocas sin extinción en al menos 4 de 5 semillas (sin reinyección)."""
    survived = 0
    for seed in range(5):
        s = island.init_island(seed, b"test-node")
        ok = True
        for _ in range(100):
            s, st = island.epoch(s, config.EPOCH_STEPS)
            if int(st["population_min"]) == 0:
                ok = False
                break
        survived += ok
    assert survived >= 4
