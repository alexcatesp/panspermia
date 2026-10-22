"""Escalera de complejidad (ADR-014): cada interruptor del mundo hace lo que dice y nada más."""
import jax
import jax.numpy as jnp
import numpy as np
import pytest

from panspermia import config, island, world

# Peldaño 0 con una vida corta para que el test quepa en 300 pasos (en el experimento, 600)
P0 = {"metabolism": 0, "k_mean": 0.0, "seasonal": 0, "repro_mode": "edad", "max_age": 230,
      "attack_on": 0, "chem_on": 0, "signal_on": 0}


def _env(**kw):
    return world.with_overrides(world.make_env(b"escalera-test"), **kw)


def test_defaults_are_the_usual_world_and_overrides_validate():
    env = world.make_env(b"escalera-test")
    assert float(env.metabolism) == 1 and int(env.max_age) == config.NO_MAX_AGE
    assert int(env.repro_mode) == config.REPRO_MODES["energia"]
    assert float(env.attack_on) == float(env.chem_on) == float(env.signal_on) == 1
    assert int(_env(repro_mode="edad").repro_mode) == config.REPRO_MODES["edad"]
    for bad in ({"repro_mode": "inventado"}, {"metabolism": 0.5}, {"max_age": 0}, {"k_mean": -1.0},
                {"signal_on": 2}):
        with pytest.raises(ValueError):
            _env(**bad)


def test_happy_world_free_life_fixed_lifespan_and_births_by_age():
    """Peldaño 0: sin gasto, sin comida, sin ataque, química ni señal; muerte a edad fija."""
    s = island.init_island(0, b"escalera-test", n_max=128, n_init=32, env_overrides=P0)
    assert float(jnp.sum(s.resources)) == 0.0
    s, st = island.epoch(s, 100)
    assert int(st["population"]) == 32 and int(st["births"]) == 0
    assert np.all(np.asarray(s.energy)[np.asarray(s.alive)] == config.E_INIT)  # vivir es gratis
    s, st = island.epoch(s, 200)
    alive = np.asarray(s.alive)
    assert int(st["births"]) == 128 - 32                  # a partir de la edad 200 llenan el mundo
    assert int(st["deaths_age"]) == 32                    # los fundadores mueren a la edad 230
    assert int(st["deaths_starvation"]) == int(st["deaths_poison"]) == 0
    assert int(st["population"]) == 96
    assert np.all(np.asarray(s.energy)[alive] == config.E_INIT)  # el hijo nace con E_INIT nueva
    assert float(st["energy_drained"]) == 0.0 and float(st["intake"]) == 0.0
    assert float(jnp.sum(s.chem)) == 0.0 and float(jnp.sum(jnp.abs(s.signal))) == 0.0


def test_births_by_age_do_not_need_or_take_parent_energy():
    """Peldaño 1: un adulto con poca energía tiene hijo; el padre no paga y el hijo nace con E_INIT."""
    def state(mode):
        s = island.init_island(0, b"escalera-test", n_max=16, n_init=4,
                               env_overrides={"repro_mode": mode})
        return s.replace(age=jnp.where(s.alive, config.MIN_REPRO_AGE, 0),
                         energy=jnp.where(s.alive, 5.0, 0.0))  # por debajo de cualquier umbral
    s, n, newborn = island._births(state("edad"), jax.random.PRNGKey(1))
    assert int(n) == 4
    e = np.asarray(s.energy)
    assert np.all(e[:4] == 5.0) and np.all(e[np.asarray(newborn)] == config.E_INIT)
    _, n, _ = island._births(state("energia"), jax.random.PRNGKey(1))
    assert int(n) == 0


def test_toll_without_food_costs_energy_and_movement_costs_more():
    """Peldaño 1: sin comida la energía solo baja, y moverse cuesta más que quedarse quieto."""
    env = {**P0, "metabolism": 1, "max_age": config.NO_MAX_AGE}
    s = island.init_island(0, b"escalera-test", n_max=8, n_init=2, env_overrides=env)
    s = s.replace(pheno=s.pheno.replace(n_hidden=jnp.zeros_like(s.pheno.n_hidden)))
    e = world.energy_update(s, jnp.array([0.0, 10.0] + [0.0] * 6), jnp.zeros(8), jnp.zeros(8),
                            jnp.zeros(8, bool))
    assert float(e[0]) < config.E_INIT and float(e[1]) < float(e[0])
    s0 = s.replace(env=s.env.replace(metabolism=jnp.float32(0.0)))
    e0 = world.energy_update(s0, jnp.array([0.0, 10.0] + [0.0] * 6), jnp.zeros(8), jnp.zeros(8),
                             jnp.zeros(8, bool))
    assert np.all(np.asarray(e0)[:2] == config.E_INIT)


def test_sparse_food_cut_keeps_height(monkeypatch):
    """ADR-022: con K_CUT solo queda comida en las crestas, a la misma altura que sin corte."""
    env = world.make_env(b"escalera-test")
    k0 = np.asarray(world.kmax_field(env, jnp.int32(0)))
    monkeypatch.setattr(config, "K_CUT", 1.5)
    k1 = np.asarray(world.kmax_field(env, jnp.int32(0)))
    assert 0.03 < np.mean(k1 > 0) < 0.2 and np.mean(k0 > 0) > 0.8
    assert np.array_equal(k1[k1 > 0], k0[k1 > 0])
    s = island.init_island(0, b"escalera-test", n_max=64, n_init=16)
    assert np.array_equal(np.asarray(s.resources) > 0, k1 > 0)  # empieza lleno solo en las crestas


def test_fixed_offspring_cost_is_lost(monkeypatch):
    """ADR-023: con coste fijo, el padre pierde lo que cede más el coste, el hijo recibe solo lo cedido
    y quien no puede pagarlo no tiene hijos."""
    monkeypatch.setattr(config, "REPRO_COST", 10.0)
    s = island.init_island(0, b"escalera-test", n_max=16, n_init=4, env_overrides={"repro_mode": "energia"})
    s = s.replace(age=jnp.where(s.alive, config.MIN_REPRO_AGE, 0),
                  energy=jnp.where(s.alive, jnp.array([60.0, 60.0, 18.0, 18.0] + [0.0] * 12), 0.0),
                  pheno=s.pheno.replace(repro_threshold=jnp.full(16, 15.0), offspring_frac=jnp.full(16, 0.5)))
    s2, n, newborn = island._births(s, jax.random.PRNGKey(1))
    e = np.asarray(s2.energy)
    assert int(n) == 2                                   # 18 · 0,5 = 9 < 10: los dos últimos no pueden pagar
    assert np.allclose(e[:4], [20.0, 20.0, 18.0, 18.0])  # 60 − 30 cedidos − 10 de coste
    assert np.allclose(e[np.asarray(newborn)], 30.0)
    monkeypatch.setattr(config, "REPRO_COST", 0.0)       # sin coste, los cuatro tienen hijo
    _, n, _ = island._births(s, jax.random.PRNGKey(1))
    assert int(n) == 4


def test_food_jumps_each_period(monkeypatch):
    """P4-sitio: las manchas se quedan quietas dentro de un periodo y saltan a otro sitio al cambiar
    de periodo, con la misma comida total aproximada; cada mundo salta a su manera."""
    env, other = _env(drift=0.0), world.with_overrides(world.make_env(b"otro-mundo"), drift=0.0)
    base = np.asarray(world.kmax_field(env, jnp.int32(500)))
    monkeypatch.setattr(config, "FOOD_JUMP_PERIOD", 100)
    a, b, c = (np.asarray(world.kmax_field(env, jnp.int32(t))) for t in (100, 199, 200))
    assert np.array_equal(a, b) and not np.allclose(a, c) and not np.allclose(a, base)
    assert abs(a.mean() - c.mean()) < 0.2 * a.mean()
    oa, oc = (np.asarray(world.kmax_field(other, jnp.int32(t))) for t in (100, 200))
    assert not np.allclose(np.corrcoef(a.ravel(), c.ravel())[0, 1], np.corrcoef(oa.ravel(), oc.ravel())[0, 1])


def test_alga_swap_only_one_alga_feeds(monkeypatch):
    """P4-alga: dentro de un periodo alimenta siempre la misma alga; entre periodos se sortea. El alga
    que no toca se come pero no da energía ni cuenta como ingesta."""
    monkeypatch.setattr(config, "ALGA_SWAP_PERIOD", 1000)
    env = _env(seasonal=0)
    draws = [bool(world.nourishing_is_a(env, jnp.int32(1000 * k))) for k in range(40)]
    assert 5 < sum(draws) < 35
    assert all(bool(world.nourishing_is_a(env, jnp.int32(1000 * k + 999))) == draws[k] for k in range(5))
    ov = {"seasonal": 0, "attack_on": 0, "chem_on": 0, "signal_on": 0, "metabolism": 0}
    s = island.init_island(0, b"escalera-test", n_max=2, n_init=2, env_overrides=ov)
    a = np.asarray(world.algae_type_a(s.env, s.step))
    cells = [np.argwhere(a)[0], np.argwhere(~a)[0]]                     # una celda de cada alga
    pos = jnp.asarray([(c + 0.5) * world.RES_CELL for c in cells], jnp.float32)
    s = s.replace(pos=pos, vel=jnp.zeros_like(s.vel), energy=jnp.full(2, 50.0),
                  resources=jnp.full_like(s.resources, 5.0))
    eat = jnp.array([1.0, 0.0, 0.0])                                    # quieto y comiendo
    feeds = 0 if bool(world.nourishing_is_a(s.env, s.step)) else 1        # agente sobre el alga que alimenta
    out = {}
    for period in (1000, 0):
        monkeypatch.setattr(config, "ALGA_SWAP_PERIOD", period)
        s2, _ = island.world_step(s, plastic=False, births=False, control=eat)
        out[period] = (np.asarray(s2.energy), np.asarray(s2.behavior.intake))
    assert out[1000][1][feeds] > 0 and out[1000][1][1 - feeds] == 0
    assert np.isclose(out[1000][0][feeds], out[0][0][feeds])
    assert out[1000][0][1 - feeds] < out[0][0][1 - feeds]
