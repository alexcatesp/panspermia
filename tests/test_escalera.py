"""Escalera de complejidad (ADR-014): cada interruptor del mundo hace lo que dice y nada más."""
import jax
import jax.numpy as jnp
import numpy as np
import pytest

from panspermia import brain, config, island, world

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


def test_food_short_jump_is_rigid_shift(monkeypatch):
    """P4-sitio con salto corto: dentro de un periodo el campo no cambia; en cada periodo es el de siempre
    desplazado FOOD_JUMP_DIST en una dirección al azar (misma forma y misma comida total)."""
    env = _env(drift=0.0)
    base = np.asarray(world.kmax_field(env, jnp.int32(0)))
    monkeypatch.setattr(config, "FOOD_JUMP_PERIOD", 100)
    monkeypatch.setattr(config, "FOOD_JUMP_DIST", 128.0)
    cell = config.WORLD_L / base.shape[0]
    dirs = []
    for t in (100, 200, 300):
        a, b = (np.asarray(world.kmax_field(env, jnp.int32(u))) for u in (t, t + 99))
        assert np.array_equal(a, b)
        assert abs(a.mean() - base.mean()) < 0.02 * base.mean()
        xc = np.real(np.fft.ifft2(np.fft.fft2(a) * np.conj(np.fft.fft2(base))))   # correlación en el toro
        s = np.array(np.unravel_index(np.argmax(xc), xc.shape), dtype=float)
        s = (s + base.shape[0] / 2) % base.shape[0] - base.shape[0] / 2
        assert abs(np.linalg.norm(s) * cell - 128.0) <= 1.5 * cell
        dirs.append(tuple(s))
    assert len(set(dirs)) > 1


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


def test_gut_sense_reports_energy_from_eating_over_window(monkeypatch):
    """Tripa (ADR-024): la última entrada es tanh(energía dada por lo comido en los últimos GUT_WINDOW
    pasos / GUT_OBS_SCALE), con su signo; el alga vacía da 0. Apagada (por defecto), la entrada es 0."""
    monkeypatch.setattr(config, "ALGA_SWAP_PERIOD", 1000)
    ov = {"seasonal": 0, "attack_on": 0, "chem_on": 0, "signal_on": 0, "metabolism": 0, "gut_sense": 1}
    s = island.init_island(0, b"escalera-test", n_max=2, n_init=2, env_overrides=ov)
    assert float(world.make_env(b"escalera-test").gut_sense) == 0
    a = np.asarray(world.algae_type_a(s.env, s.step))
    cells = [np.argwhere(a)[0], np.argwhere(~a)[0]]
    pos = jnp.asarray([(c + 0.5) * world.RES_CELL for c in cells], jnp.float32)
    s = s.replace(pos=pos, vel=jnp.zeros_like(s.vel), energy=jnp.full(2, 50.0),
                  resources=jnp.full_like(s.resources, 5.0))
    feeds = 0 if bool(world.nourishing_is_a(s.env, s.step)) else 1
    eat = jnp.array([1.0, 0.0, 0.0])
    energies = [np.asarray(s.energy)]
    for _ in range(config.GUT_WINDOW + 1):
        s, _ = island.world_step(s, plastic=False, births=False, control=eat)
        energies.append(np.asarray(s.energy))
    gut = np.asarray(s.gut).sum(1)
    window = energies[-1] - energies[-1 - config.GUT_WINDOW]   # sin metabolismo: energía = lo comido
    assert gut[feeds] > 0 and np.isclose(gut[feeds], window[feeds], atol=1e-4)  # energía en f32 cerca de 50
    assert gut[1 - feeds] == 0
    obs, _ = world.sense(s, world.neighbors(s.pos, s.alive))
    assert obs.shape[1] == config.OBS_DIM
    assert np.allclose(np.asarray(obs[:, -1]), np.tanh(gut / config.GUT_OBS_SCALE), atol=1e-6)
    off, _ = world.sense(s.replace(env=s.env.replace(gut_sense=jnp.float32(0.0))),
                         world.neighbors(s.pos, s.alive))
    assert np.all(np.asarray(off[:, -1]) == 0)
    assert np.allclose(np.asarray(off[:, :-1]), np.asarray(obs[:, :-1]))



def test_eating_brakes_movement(monkeypatch):
    """Comer frena (ADR-025): con EAT_MOVE_FACTOR 0, quien come no se mueve y quien no come sí; la política
    fija del examen (control) no frena. Con el factor por defecto (1), comer no cambia el movimiento."""
    ov = {"seasonal": 0, "attack_on": 0, "chem_on": 0, "signal_on": 0, "metabolism": 0}
    s0 = island.init_island(0, b"escalera-test", n_max=2, n_init=2, env_overrides=ov)
    s0 = s0.replace(pos=jnp.asarray([[100.0, 100.0], [600.0, 600.0]]), vel=jnp.zeros_like(s0.vel))
    real_step = brain.step

    def fake_step(w, h, obs, hid_mask):  # empuje máximo y sin giro; solo el primero come
        actions, h_new, pre, post = real_step(w, h, obs, hid_mask)
        fixed = jnp.zeros_like(actions).at[:, 0].set(1.0).at[0, 2].set(1.0).at[1, 2].set(-1.0)
        return fixed, h_new, pre, post

    def moved(factor, control=None):
        monkeypatch.setattr(config, "EAT_MOVE_FACTOR", factor)
        jax.clear_caches()  # la constante se lee al trazar
        s = s0
        for _ in range(5):
            s, _ = island.world_step(s, plastic=False, births=False, control=control)
        jax.clear_caches()
        return np.linalg.norm(np.asarray(s.pos) - np.asarray(s0.pos), axis=1)

    monkeypatch.setattr(brain, "step", fake_step)
    free, braked = moved(1.0), moved(0.0)
    assert free[0] > 0 and free[1] > 0                              # sin freno, los dos se mueven
    assert braked[0] == 0 and np.isclose(braked[1], free[1])        # con freno, quien come no se mueve
    monkeypatch.setattr(brain, "step", real_step)
    eat_push = jnp.array([1.0, 1.0, 0.0])                           # examen: empuje 1, giro 0, come
    assert np.all(moved(0.0, control=eat_push) > 0)
    assert np.allclose(moved(0.0, control=eat_push), moved(1.0, control=eat_push))


def test_eating_brake_ramp(monkeypatch):
    """Rampa del freno (3.2): con EAT_MOVE_RAMP_STEPS, el factor pasa de 1 a EAT_MOVE_FACTOR linealmente; a mitad
    de la rampa, quien come recorre la mitad que sin freno, y al final de la rampa no se mueve."""
    ov = {"seasonal": 0, "attack_on": 0, "chem_on": 0, "signal_on": 0, "metabolism": 0}
    s0 = island.init_island(0, b"escalera-test", n_max=2, n_init=2, env_overrides=ov)
    s0 = s0.replace(pos=jnp.asarray([[100.0, 100.0], [600.0, 600.0]]), vel=jnp.zeros_like(s0.vel))
    real_step = brain.step

    def fake_step(w, h, obs, hid_mask):  # empuje máximo y sin giro; solo el primero come
        actions, h_new, pre, post = real_step(w, h, obs, hid_mask)
        fixed = jnp.zeros_like(actions).at[:, 0].set(1.0).at[0, 2].set(1.0).at[1, 2].set(-1.0)
        return fixed, h_new, pre, post

    def moved(step):
        jax.clear_caches()  # las constantes se leen al trazar
        s, _ = island.world_step(s0.replace(step=jnp.asarray(step, s0.step.dtype)), plastic=False, births=False)
        jax.clear_caches()
        return np.linalg.norm(np.asarray(s.pos) - np.asarray(s0.pos), axis=1)

    monkeypatch.setattr(brain, "step", fake_step)
    free = moved(500)                                           # sin freno (factor 1): referencia de cada bicho
    monkeypatch.setattr(config, "EAT_MOVE_FACTOR", 0.0)
    monkeypatch.setattr(config, "EAT_MOVE_RAMP_STEPS", 1000)
    start, half, end = moved(0), moved(500), moved(2000)
    assert np.allclose(start, free, rtol=1e-5)                  # al empezar la rampa no frena
    assert np.isclose(half[0], 0.5 * free[0], rtol=1e-3)        # a mitad, quien come recorre la mitad
    assert np.isclose(half[1], free[1], rtol=1e-5)              # quien no come, igual
    assert end[0] == 0 and np.isclose(end[1], free[1], rtol=1e-5)  # al final, freno total


def test_food_ramp(monkeypatch):
    """Rampa de comida (3.4): la capacidad de las algas empieza en K_MEAN_RAMP_FROM × la de siempre, vale la media a
    mitad de la rampa y la de siempre al final; apagada, no cambia nada."""
    env = _env(drift=0.0)
    base = np.asarray(world.kmax_field(env, jnp.int32(500)))
    monkeypatch.setattr(config, "K_MEAN_RAMP_STEPS", 1000)
    monkeypatch.setattr(config, "K_MEAN_RAMP_FROM", 2.0)
    start, half, end, later = (np.asarray(world.kmax_field(env, jnp.int32(t))) for t in (0, 500, 1000, 5000))
    assert np.allclose(start, 2.0 * base, rtol=1e-5)
    assert np.allclose(half, 1.5 * base, rtol=1e-5)
    assert np.allclose(end, base, rtol=1e-5) and np.allclose(later, base, rtol=1e-5)


def test_alga_per_agent_feeds_each_its_own(monkeypatch):
    """Alga por bicho (3.3, ADR-026): a cada bicho le alimenta una sola alga, sorteada por su uid (la mitad,
    A), fija para toda la vida y distinta en cada mundo; sobre la otra come pero no gana nada. Apagado, como
    siempre. No se puede encender junto al cambio global del alga."""
    env, other = _env(seasonal=0), world.with_overrides(world.make_env(b"otro-mundo"), seasonal=0)
    uid = jnp.arange(1, 4001, dtype=jnp.uint32)
    g = np.asarray(world.good_alga_a(env, uid))
    assert 0.45 < g.mean() < 0.55
    assert np.array_equal(g, np.asarray(world.good_alga_a(env, uid)))      # fija para toda la vida
    assert abs(np.corrcoef(g[:-1], g[1:])[0, 1]) < 0.05                    # uid vecinos (padre e hijo), sin relación
    assert 0.4 < np.mean(g == np.asarray(world.good_alga_a(other, uid))) < 0.6
    ov = {"seasonal": 0, "attack_on": 0, "chem_on": 0, "signal_on": 0, "metabolism": 0}
    s = island.init_island(0, b"escalera-test", n_max=4, n_init=4, env_overrides=ov)
    a = np.asarray(world.algae_type_a(s.env, s.step))
    ca, cb = np.argwhere(a)[0], np.argwhere(~a)[0]
    ga = np.asarray(world.good_alga_a(s.env, uid))
    ua, ub = int(uid[np.argmax(ga)]), int(uid[np.argmin(ga)])               # un uid al que alimenta A y otro B
    pos = jnp.asarray([(c + 0.5) * world.RES_CELL for c in (ca, ca, cb, cb)], jnp.float32)
    s = s.replace(pos=pos, vel=jnp.zeros_like(s.vel), energy=jnp.full(4, 50.0),
                  resources=jnp.full_like(s.resources, 5.0),
                  lineage=s.lineage.replace(uid=jnp.asarray([ua, ub, ua, ub], s.lineage.uid.dtype)))
    eat = jnp.array([1.0, 0.0, 0.0])                                        # quieto y comiendo
    out = {}
    for on in (1, 0):
        monkeypatch.setattr(config, "ALGA_PER_AGENT", on)
        s2, _ = island.world_step(s, plastic=False, births=False, control=eat)
        out[on] = (np.asarray(s2.energy), np.asarray(s2.behavior.intake))
    good = np.array([True, False, False, True])                             # A sobre A, B sobre A, A sobre B, B sobre B
    assert np.all(out[1][1][good] > 0) and np.all(out[1][1][~good] == 0)
    assert np.allclose(out[1][0][good], out[0][0][good])
    assert np.all(out[1][0][~good] < out[0][0][~good])
    monkeypatch.setattr(config, "ALGA_PER_AGENT", 1)
    monkeypatch.setattr(config, "ALGA_SWAP_PERIOD", 1000)
    with pytest.raises(ValueError):
        island.world_step(s, plastic=False, births=False, control=eat)


def test_poison_delayed(monkeypatch):
    """Veneno diferido (3.6, ADR-030): con alga por bicho, la equivocada alimenta al comerla igual que la buena (la
    tripa la registra) y cobra POISON_FACTOR × lo que dio exactamente POISON_DELAY pasos después; el neto es negativo.
    Con retardo 0 el cobro llega en el mismo paso y la tripa ve el neto."""
    ov = {"seasonal": 0, "attack_on": 0, "chem_on": 0, "signal_on": 0, "metabolism": 0}
    s = island.init_island(0, b"escalera-test", n_max=4, n_init=4, env_overrides=ov)
    a = np.asarray(world.algae_type_a(s.env, s.step))
    ca, cb = np.argwhere(a)[0], np.argwhere(~a)[0]
    uid = jnp.arange(1, 4001, dtype=jnp.uint32)
    ga = np.asarray(world.good_alga_a(s.env, uid))
    ua, ub = int(uid[np.argmax(ga)]), int(uid[np.argmin(ga)])
    pos = jnp.asarray([(c + 0.5) * world.RES_CELL for c in (ca, ca, cb, cb)], jnp.float32)
    s = s.replace(pos=pos, vel=jnp.zeros_like(s.vel), energy=jnp.full(4, 50.0),
                  resources=jnp.full_like(s.resources, 5.0),
                  lineage=s.lineage.replace(uid=jnp.asarray([ua, ub, ua, ub], s.lineage.uid.dtype)))
    eat = jnp.array([1.0, 0.0, 0.0])
    good = np.array([True, False, False, True])
    monkeypatch.setattr(config, "ALGA_PER_AGENT", 1)

    def run(factor, delay, steps):
        monkeypatch.setattr(config, "POISON_FACTOR", factor)
        monkeypatch.setattr(config, "POISON_DELAY", delay)
        c, energy, gut = s, [], None
        for i in range(steps):
            c, _ = island.world_step(c, plastic=False, births=False, control=eat)
            if i == 0:
                gut = np.asarray(c.gut).sum(1)
                c = c.replace(resources=jnp.zeros_like(c.resources))      # un solo bocado
            energy.append(np.asarray(c.energy))
        return np.array(energy), gut, c

    d = 3
    ref, gut_ref, _ = run(0.0, d, d + 2)                                    # sin veneno: la equivocada no alimenta
    pz, gut_p, c = run(2.0, d, d + 2)
    bite = pz[0] - ref[0]                                                  # lo que dio el alga equivocada
    assert np.all(bite[~good] > 0) and np.allclose(bite[good], 0.0)
    assert np.all(gut_p[~good] > gut_ref[~good])                            # la tripa la registra como buena
    for i in range(1, d):                                                  # nada hasta el paso d
        assert np.allclose(pz[i] - ref[i], bite, atol=1e-3)                 # (salvo el rebrote, ~1e-4)
    assert np.allclose(pz[d] - ref[d], bite - 2.0 * bite, atol=1e-3)        # cobra 2 × lo que dio en el paso d
    assert np.all((pz[d] - ref[d])[~good] < 0)                              # neto negativo
    assert np.allclose(np.asarray(c.poison)[:, :d], 0.0, atol=1e-3)        # lo vencido se ha borrado
    imm, gut_i, _ = run(2.0, 0, 2)                                          # contraste inmediato
    assert np.allclose(imm[0] - ref[0], -bite, atol=1e-3)
    assert np.all(gut_i[~good] < 0)                                         # la tripa ve el neto


def test_alga_patch_families(monkeypatch):
    """Manchas de un solo tipo (3.5, ADR-027): el alga es A donde manda la familia de ondas pares y la comida sigue
    a la mayor de las dos familias; con corte, cada casilla con comida tiene el tipo de la familia que la levanta.
    Apagado, el mundo de siempre. No se puede encender junto a los saltos de la comida."""
    env = _env(drift=0.0, k_mean=2.0)
    base_k, base_a = (np.asarray(f(env, jnp.int32(0))) for f in (world.kmax_field, world.algae_type_a))
    monkeypatch.setattr(config, "ALGA_PATCH_FAMILIES", 1)
    monkeypatch.setattr(config, "K_CUT", 1.7)
    K, A = np.asarray(world.kmax_field(env, jnp.int32(0))), np.asarray(world.algae_type_a(env, jnp.int32(0)))
    cx, cy = np.meshgrid(np.asarray(world._RES_CENTERS), np.asarray(world._RES_CENTERS), indexing="ij")
    k, amp, ph = (np.asarray(x, np.float64) for x in (env.wave_k, env.wave_amp, env.wave_phase))
    waves = amp[:, None, None] * np.sin(2 * np.pi * (k[:, 0, None, None] * cx + k[:, 1, None, None] * cy) + ph[:, None, None])
    z_a = waves[0::2].sum(0) / np.sqrt((amp[0::2] ** 2).sum() / 2)
    z_b = waves[1::2].sum(0) / np.sqrt((amp[1::2] ** 2).sum() / 2)
    z = np.maximum(z_a, z_b)
    sure = np.abs(z_a - z_b) > 1e-3                                              # lejos del empate (redondeo f32)
    assert np.array_equal(A[sure], (z_a >= z_b)[sure])
    walls = np.asarray(env.walls)
    expect = np.where((z >= 1.7) & ~walls, 2.0 * np.maximum(0.0, 1 + config.K_CONTRAST * z), 0.0)
    near_cut = np.abs(z - 1.7) < 1e-3
    assert np.allclose(K[~near_cut], expect[~near_cut], rtol=1e-4, atol=1e-4)
    assert 0.03 < (K > 0).mean() < 0.2 and 0.25 < (K * A).sum() / K.sum() < 0.75
    assert not np.array_equal(A, base_a)
    monkeypatch.setattr(config, "FOOD_JUMP_PERIOD", 1000)
    with pytest.raises(ValueError):
        world.algae_type_a(env, jnp.int32(0))
    monkeypatch.setattr(config, "FOOD_JUMP_PERIOD", 0)
    monkeypatch.setattr(config, "ALGA_PATCH_FAMILIES", 0)
    monkeypatch.setattr(config, "K_CUT", None)
    assert np.array_equal(np.asarray(world.kmax_field(env, jnp.int32(0))), base_k)
    assert np.array_equal(np.asarray(world.algae_type_a(env, jnp.int32(0))), base_a)
