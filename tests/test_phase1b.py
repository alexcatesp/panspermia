"""Tests de la fase 1b (ADR-008): química artificial y algas estacionales."""
import jax.numpy as jnp
import numpy as np

from panspermia import config, island, world

RES = config.RESOURCE_GRID


def _f64(x):
    return np.asarray(x, np.float64)


def test_emit_costs_energy_and_fills_cell():
    chem = jnp.zeros((config.N_CHEM, RES, RES))
    pos = jnp.array([[100.0, 100.0], [500.0, 500.0]])
    actions = jnp.zeros((2, config.ACT_DIM)).at[0, 5:8].set(1.0)
    cost, amount, chem2 = world.emit(chem, pos, jnp.array([True, True]), actions)
    per = config.EMIT_RATE * config.DT
    assert np.allclose(np.asarray(amount[0]), per) and float(jnp.sum(amount[1])) == 0.0
    assert np.isclose(float(cost[0]), per * sum(config.EMIT_COST))
    assert np.isclose(float(jnp.sum(chem2)), 3 * per)


def test_toxin_conserves_energy():
    chem = jnp.zeros((config.N_CHEM, RES, RES)).at[1, 12, 12].set(2.0)
    res = jnp.full((RES, RES), 0.5)
    pos = jnp.array([[12 * 8 + 4.0, 12 * 8 + 4.0], [12 * 8 + 2.0, 12 * 8 + 6.0], [900.0, 900.0]])
    energy = jnp.array([30.0, 30.0, 30.0])
    dmg, chem2, res2 = world.toxin(chem, res, pos, jnp.array([True, True, True]), energy)
    assert float(dmg[0]) > 0 and float(dmg[2]) == 0.0
    total_before = _f64(energy).sum() + _f64(chem[1]).sum() + _f64(res).sum()
    total_after = (_f64(energy) - _f64(dmg)).sum() + _f64(chem2[1]).sum() + _f64(res2).sum()
    assert np.isclose(total_before, total_after, atol=1e-3)


def test_chem_step_diffuses_and_recycles():
    chem = jnp.zeros((config.N_CHEM, RES, RES)).at[:, 64, 64].set(10.0)
    res = jnp.zeros((RES, RES))
    chem2, res2 = world.chem_step(chem, res)
    assert float(chem2[0, 64, 65]) > 0, "no difunde"
    # nutriente + toxina + algas se conservan; la feromona se disipa
    before = _f64(chem[:2]).sum() + _f64(res).sum()
    after = _f64(chem2[:2]).sum() + _f64(res2).sum()
    assert np.isclose(before, after, atol=1e-3)
    assert _f64(chem2[2]).sum() < 10.0


def test_toxic_algae_subtract_energy():
    res = jnp.full((RES, RES), 1.0)
    chem = jnp.zeros((config.N_CHEM, RES, RES))
    pos = jnp.array([[4.0, 4.0]])
    actions = jnp.zeros((1, config.ACT_DIM)).at[0, 2].set(1.0)
    toxic = jnp.ones((RES, RES), bool)
    gain, intake, toxic_in, _, _, _ = world.eat(res, chem, pos, jnp.array([True]), actions, toxic, 1.0)
    assert float(toxic_in[0]) == float(intake[0]) > 0
    assert np.isclose(float(gain[0]), -config.TOXIC_FACTOR * float(intake[0]))


def test_toxicity_ramp_starts_as_food():
    """Rampa: con toxicidad 0 el alga tóxica alimenta; con 0,5, nada; con 1, resta."""
    res = jnp.full((RES, RES), 1.0)
    chem = jnp.zeros((config.N_CHEM, RES, RES))
    pos = jnp.array([[4.0, 4.0]])
    actions = jnp.zeros((1, config.ACT_DIM)).at[0, 2].set(1.0)
    toxic = jnp.ones((RES, RES), bool)
    gains = [float(world.eat(res, chem, pos, jnp.array([True]), actions, toxic, t)[0][0])
             for t in (0.0, 1.0 / (1.0 + config.TOXIC_FACTOR), 1.0)]
    assert gains[0] > 0 and np.isclose(gains[1], 0.0, atol=1e-6) and gains[2] < 0
    assert config.TOXIC_RAMP_STEPS > 0


def test_toxic_cells_alternate_and_disable():
    env = world.make_env(b"x")
    a = np.asarray(world.toxic_cells(env, jnp.int32(0), jnp.int32(0)))
    b = np.asarray(world.toxic_cells(env, jnp.int32(0), jnp.int32(1)))
    assert a.any() and b.any() and not (a & b).any() and (a | b).all()
    off = env.replace(seasonal=jnp.float32(0.0))
    assert not np.asarray(world.toxic_cells(off, jnp.int32(0), jnp.int32(0))).any()


def test_chem_gradient_points_to_source():
    chem = jnp.zeros((config.N_CHEM, RES, RES)).at[0, 51, 50].set(1.0)  # una celda delante (x+)
    pos = jnp.array([[50 * 8 + 4.0, 50 * 8 + 4.0]])
    heading = jnp.array([[1.0, 0.0]])
    lateral = jnp.array([[0.0, 1.0]])
    obs = np.asarray(world.sense_chem(chem, pos, heading, lateral))[0]
    n = config.N_CHEM
    assert obs[n + 0] > 0, "gradiente adelante del nutriente"
    assert obs[2 * n + 0] == 0.0, "sin gradiente lateral"


def test_island_runs_with_chemistry():
    s = island.init_island(0, b"t", n_max=128, n_init=64)
    s, st = island.epoch(s, 100)
    for k in ("toxic_intake_frac", "emit_toxin", "deaths_poison", "chem_nutrient_total"):
        assert k in st and np.isfinite(float(st[k]))
    assert float(st["emit_nutrient"]) > 0  # cerebros aleatorios emiten


def test_toxic_regions_split_island_and_move():
    """Regiones de toxicidad: media isla en cada régimen y fronteras que se desplazan."""
    env = world.make_env(b"x")
    r0 = np.asarray(world.toxic_regions(env, jnp.int32(0)))
    later = int(config.WORLD_L / (4 * config.TOXIC_REGION_K) / config.TOXIC_REGION_SPEED / config.DT)
    r1 = np.asarray(world.toxic_regions(env, jnp.int32(later)))
    assert 0.4 < r0.mean() < 0.6
    assert 0.2 < (r0 != r1).mean()  # un cuarto de longitud de onda después ha cambiado mucho
