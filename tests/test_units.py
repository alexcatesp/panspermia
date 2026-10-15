"""Tests unitarios de cerebro, mundo y genoma (invariantes)."""
import jax
import jax.numpy as jnp
import numpy as np

from panspermia import brain, config, world
from panspermia import genome as G
from panspermia.develop import develop


def _pheno(seed=0):
    g = G.random_minimal(jax.random.PRNGKey(seed))
    p = develop(g)
    return g, jax.tree.map(lambda x: x[None], p)


def test_canonical_is_idempotent_and_mutate_canonical():
    g = G.random_minimal(jax.random.PRNGKey(0))
    for i in range(30):
        g = G.mutate(g, jax.random.PRNGKey(i))
        c = G.canonical(g)
        assert all(np.array_equal(np.asarray(x), np.asarray(y))
                   for x, y in zip(jax.tree.leaves(g), jax.tree.leaves(c)))
    W_mask = np.asarray(g.W_mask)
    assert not np.any(np.tril(W_mask)), "aristas que violan el orden topológico"
    assert not np.any(W_mask[:, :config.CPPN_IN]), "aristas hacia nodos de entrada"


def test_canonical_np_matches_jax():
    """La forma canónica numpy (serialización) coincide con la de JAX (simulación), incluso
    partiendo de máscaras arbitrarias no canónicas."""
    k = jax.random.split(jax.random.PRNGKey(7), 4)
    g = G.random_minimal(k[0]).replace(
        node_mask=jax.random.bernoulli(k[1], 0.5, (config.CPPN_NODES,)),
        W_mask=jax.random.bernoulli(k[2], 0.5, (config.CPPN_NODES,) * 2),
        W=jax.random.normal(k[3], (config.CPPN_NODES,) * 2).astype(jnp.float16),
    )
    a = {name: np.asarray(getattr(g, name)) for name, _, _ in G._FIELDS}
    c_np = G.canonical_np(a)
    c_jax = G.canonical(g)
    for name in c_np:
        assert c_np[name].tobytes() == np.asarray(getattr(c_jax, name)).tobytes(), name


def test_plasticity_zero_without_modulation_and_clipped():
    _, p = _pheno()
    w = p.w0.astype(jnp.float32)
    pre = jnp.ones((1, config.N_PRE))
    post = jnp.ones((1, config.N_POST))
    assert np.array_equal(brain.plasticity(p, w, pre, post, jnp.zeros(1)), w)
    w2 = brain.plasticity(p, w, pre * 1e3, post * 1e3, jnp.ones(1))
    assert float(jnp.max(jnp.abs(w2))) <= config.W_MAX
    assert np.all(np.asarray(w2)[~np.asarray(p.mask)] == 0), "sinapsis no expresadas cambiaron"


def test_brain_step_shapes_and_mask():
    g, p = _pheno()
    w = p.w0.astype(jnp.float32)
    h = jnp.zeros((1, config.N_HIDDEN_MAX))
    obs = jax.random.normal(jax.random.PRNGKey(1), (1, config.OBS_DIM))
    a, h2, pre, post = brain.step(w, h, obs, g.hid_mask[None])
    assert a.shape == (1, config.ACT_DIM) and h2.shape == (1, config.N_HIDDEN_MAX)
    assert np.all(np.asarray(h2)[0, ~np.asarray(g.hid_mask)] == 0)
    assert pre.shape == (1, config.N_PRE) and post.shape == (1, config.N_POST)


def test_neighbors_exclude_self_and_dead():
    pos = jnp.array([[10.0, 10.0], [12.0, 10.0], [500.0, 500.0], [11.0, 11.0]])
    alive = jnp.array([True, True, True, False])
    cand = np.asarray(world.neighbors(pos, alive))
    assert set(cand[0][cand[0] >= 0]) == {1}
    assert set(cand[2][cand[2] >= 0]) == set()
    assert np.all(cand[3] == -1)


def test_neighbors_wrap_torus():
    pos = jnp.array([[1.0, 1.0], [config.WORLD_L - 1.0, 1.0]])
    cand = np.asarray(world.neighbors(pos, jnp.array([True, True])))
    assert 1 in cand[0]


def test_eat_conserves_resources():
    res = jnp.full((config.RESOURCE_GRID,) * 2, 0.3)
    pos = jnp.array([[1.0, 1.0], [2.0, 2.0], [100.0, 100.0]])  # dos en la misma celda
    actions = jnp.zeros((3, config.ACT_DIM)).at[:, 2].set(1.0)
    intake, res2 = world.eat(res, pos, jnp.array([True, True, True]), actions)
    eaten = np.asarray(res, np.float64) - np.asarray(res2, np.float64)
    assert np.isclose(eaten.sum(), float(jnp.sum(intake)), atol=1e-5)
    assert float(intake[0] + intake[1]) <= 0.3 + 1e-6


def test_env_from_node_id_is_stable_and_bounded():
    a, b, c = world.make_env(b"x"), world.make_env(b"x"), world.make_env(b"y")
    assert all(np.array_equal(np.asarray(u), np.asarray(v))
               for u, v in zip(jax.tree.leaves(a), jax.tree.leaves(b)))
    assert float(a.k_mean) != float(c.k_mean)
    s = config.BIOGEO_SPREAD
    assert config.K_MEAN * (1 - s) <= float(a.k_mean) <= config.K_MEAN * (1 + s)
