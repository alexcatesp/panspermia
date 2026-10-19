"""Reproducción sexual, lugar de nacimiento y parentesco local (ADR-017)."""
import jax
import jax.numpy as jnp
import numpy as np
import pytest

from panspermia import config, island, metrics
from panspermia import genome as G

P0 = {"metabolism": 0, "k_mean": 0.0, "seasonal": 0, "repro_mode": "edad", "max_age": 600,
      "attack_on": 0, "chem_on": 0, "signal_on": 0}


def test_crossover_takes_each_gene_from_one_parent():
    a = G.random_minimal(jax.random.PRNGKey(1))
    b = G.random_minimal(jax.random.PRNGKey(2))
    c = G.crossover(a, b, jax.random.PRNGKey(3))
    for f in ("bias", "act_id", "hid_pos", "body", "life"):
        x, y, z = (np.asarray(getattr(g, f)) for g in (a, b, c))
        assert np.all((z == x) | (z == y)), f
    assert not np.array_equal(np.asarray(c.body), np.asarray(a.body))  # mezcla de verdad
    same = G.crossover(a, a, jax.random.PRNGKey(4))
    assert all(np.array_equal(np.asarray(u), np.asarray(v)) for u, v in zip(jax.tree.leaves(same), jax.tree.leaves(G.canonical(a))))


def _adult_state(n_max=64, n_init=16):
    s = island.init_island(0, b"p0y-test", n_max=n_max, n_init=n_init, env_overrides=P0)
    # todos juntos en una esquina para que tengan vecinos
    pos = jnp.where(s.alive[:, None], 100.0 + 20.0 * jax.random.uniform(jax.random.PRNGKey(9), s.pos.shape), s.pos)
    return s.replace(pos=pos, age=jnp.where(s.alive, config.MIN_REPRO_AGE, 0))


def _births(mode_rep="asexual", place="cerca"):
    config.REPRODUCTION, config.BIRTH_PLACEMENT = mode_rep, place
    try:
        s = _adult_state()
        alive0 = np.asarray(s.alive)
        s2, n, newborn = jax.jit(lambda st, k: island._births(st, k))(s, jax.random.PRNGKey(5))  # traza nueva con el modo
        return s, s2, int(n), np.asarray(newborn), alive0
    finally:
        config.REPRODUCTION, config.BIRTH_PLACEMENT = "asexual", "cerca"


def _evolved(seed, rounds=300):
    """Genoma con una CPPN propia: muchas mutaciones con la tasa estructural alta."""
    g = G.random_minimal(jax.random.PRNGKey(seed))
    g = g.replace(life=g.life.at[3].set(5.0))
    mut = jax.jit(G.mutate)
    for i in range(rounds):
        g = mut(g, jax.random.PRNGKey(1000 * seed + i))
    return g


def _dead_nodes(g):
    hidden = np.zeros(config.CPPN_NODES, bool)
    hidden[config.CPPN_IN:config.CPPN_NODES - config.CPPN_OUT] = True
    nm, wm = np.asarray(g.node_mask), np.asarray(g.W_mask)
    return int(np.sum(nm & hidden & ~wm.any(axis=1))), int(np.sum(nm & hidden & ~wm.any(axis=0)))


def test_crossover_keeps_the_cppn_whole():
    """ADR-018: la CPPN del hijo es entera la de un progenitor, y no deja nodos sin salida nuevos."""
    a, b = _evolved(1), _evolved(2)
    assert int(np.sum(np.asarray(a.node_mask) != np.asarray(b.node_mask))) > 0  # CPPN distintas
    fields = ("node_mask", "act_id", "bias", "W", "W_mask")
    seen = set()
    for i in range(16):
        c = G.crossover(a, b, jax.random.PRNGKey(100 + i))
        from_a = all(np.array_equal(np.asarray(getattr(c, f)), np.asarray(getattr(G.canonical(a), f))) for f in fields)
        from_b = all(np.array_equal(np.asarray(getattr(c, f)), np.asarray(getattr(G.canonical(b), f))) for f in fields)
        assert from_a or from_b
        seen.add("a" if from_a else "b")
        assert _dead_nodes(c) in (_dead_nodes(a), _dead_nodes(b))
    assert seen == {"a", "b"}


def test_sexual_children_mix_two_parents():
    s, s2, n, newborn, alive0 = _births("sexual")
    assert n == 16
    adults_body = np.asarray(s.genome.body)[alive0].astype(np.float32)
    kids_body = np.asarray(s2.genome.body)[newborn].astype(np.float32)
    # cada gen del hijo viene (antes de la mutación) de algún adulto; con σ pequeña, el más cercano
    # en cada gen no es siempre el mismo adulto: hay mezcla de dos padres
    mixed = 0
    for kid in kids_body:
        nearest = np.argmin(np.abs(adults_body - kid[None, :]), axis=0)
        mixed += len(set(nearest.tolist())) > 1
    assert mixed >= n // 2


def test_birth_placement_random_scatters_children():
    _, s2c, _, nb_c, _ = _births("asexual", "cerca")
    _, s2a, _, nb_a, _ = _births("asexual", "azar")
    near = np.asarray(s2c.pos)[nb_c]
    far = np.asarray(s2a.pos)[nb_a]
    assert np.all((near > 80) & (near < 150))          # junto a sus padres (en 100–120)
    assert np.mean((far < 80) | (far > 150)) > 0.5     # repartidos por el mundo


def test_kin_local_and_simpson():
    s = _adult_state()
    k = float(metrics.kin_local(s))
    assert 0.0 <= k <= 1.0
    clade = np.array([1, 1, 2, 2, 3, 0], np.uint32)
    alive = np.array([True] * 5 + [False])
    assert abs(metrics.simpson(clade, alive) - (0.16 + 0.16 + 0.04)) < 1e-9


def test_unknown_modes_are_rejected():
    for name in ("REPRODUCTION", "BIRTH_PLACEMENT"):
        old = getattr(config, name)
        setattr(config, name, "inventado")
        try:
            with pytest.raises(ValueError):
                jax.jit(lambda st, k: island._births(st, k))(_adult_state(), jax.random.PRNGKey(5))
        finally:
            setattr(config, name, old)
