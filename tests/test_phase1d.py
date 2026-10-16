"""Tests de la fase 1d: programa temporal de toxicidad, reloj configurable y medidas temporales."""
import jax
import jax.numpy as jnp
import numpy as np
import pytest

from panspermia import config, island, metrics, world


def _env(**kw):
    return world.with_overrides(world.make_env(b"fase1d-test"), **kw)


def _run_patches(env, steps, key=0):
    p = world.initial_patches(env, jax.random.PRNGKey(key))
    hist = [np.asarray(p)]
    for s in range(steps):
        p = world.step_patches(env, p, jnp.int32(s), jax.random.fold_in(jax.random.PRNGKey(key), s))
        hist.append(np.asarray(p))
    return np.stack(hist)


def test_overrides_validate():
    with pytest.raises(ValueError):
        _env(no_existe=1)
    with pytest.raises(ValueError):
        _env(tox_mode="inventado")
    with pytest.raises(ValueError):
        _env(tox_period=1)
    assert int(_env(tox_mode="periodico").tox_mode) == config.TOX_MODES["periodico"]


def test_random_patches_flip_at_rate():
    """Programa aleatorio: cada parche se invierte con prob. 2/T por paso (estancia media T/2)."""
    t = 40.0
    h = _run_patches(_env(tox_mode="aleatorio", tox_period=t), 400)
    rate = np.mean(h[1:] != h[:-1])
    assert abs(rate - 2 / t) < 0.01, rate
    # cambios locales: nunca todos los parches a la vez
    assert np.max(np.sum(h[1:] != h[:-1], axis=(1, 2))) < config.TOX_PATCHES ** 2


def test_periodic_patches_flip_together_every_half_period():
    t = 40
    h = _run_patches(_env(tox_mode="periodico", tox_period=t), 120)
    assert not h[0].any()  # empieza sincronizado
    changed = np.nonzero(np.any(h[1:] != h[:-1], axis=(1, 2)))[0] + 1
    assert list(changed) == [20, 40, 60, 80, 100, 120]
    assert all((h[i] == h[i][0, 0]).all() for i in range(len(h)))  # todos iguales siempre


def test_fixed_patches_never_change():
    h = _run_patches(_env(tox_mode="fijo", tox_period=10), 50)
    assert (h == h[0]).all() and 0 < h[0].mean() < 1


def test_franjas_mode_is_default_and_unchanged():
    env = world.make_env(b"x")
    assert int(env.tox_mode) == config.TOX_MODES["franjas"]
    patches = jnp.ones((config.TOX_PATCHES, config.TOX_PATCHES), bool)
    a = world.toxic_cells(env, jnp.int32(7), jnp.int32(0))
    b = world.toxic_cells(env, jnp.int32(7), jnp.int32(0), patches)
    assert np.array_equal(np.asarray(a), np.asarray(b))  # en modo franjas los parches no influyen


def test_patch_mode_uses_patches():
    env = _env(tox_mode="fijo")
    zeros = jnp.zeros((config.TOX_PATCHES, config.TOX_PATCHES), bool)
    a = np.asarray(world.algae_type_a(env, jnp.int32(0)))
    t0 = np.asarray(world.toxic_cells(env, jnp.int32(0), jnp.int32(0), zeros))
    t1 = np.asarray(world.toxic_cells(env, jnp.int32(0), jnp.int32(0), ~zeros))
    assert np.array_equal(t0, a) and np.array_equal(t1, ~a)


def test_island_with_schedule_runs_and_reports():
    s = island.init_island(0, b"t", n_max=128, n_init=64,
                           env_overrides={"tox_mode": "periodico", "tox_period": 40, "clock_period": 40})
    s, st = island.epoch(s, 100)
    assert float(st["tox_patch_flips"]) == 5 * config.TOX_PATCHES ** 2  # inversiones en los pasos 20, 40, …, 100
    series = {k[7:]: np.asarray(v) for k, v in st.items() if k.startswith("series_")}
    tm = metrics.temporal_metrics(series, s.env, int(s.step) - 100)
    assert 0.0 <= tm["clock_rhythm"] <= 1.0 and tm["anticipation"] is not None


def test_temporal_metrics_detects_rhythm_and_anticipation():
    env = _env(tox_mode="periodico", tox_period=40, clock_period=40)
    n = 400
    steps = np.arange(n)
    eaters = (100 * (np.mod(steps, 40) < 20)).astype(np.int32)  # comen solo en media fase
    tox_state = ((steps + 1) // 20 % 2).astype(np.float32)
    toxic = np.zeros(n)
    flips = np.nonzero(np.diff(tox_state))[0] + 1
    for f in flips:
        toxic[max(f - 5, 0):f] = 1.0  # justo antes del cambio comen el alga que va a ser buena
    series = {"population": np.full(n, 100), "eaters": eaters, "intake": np.ones(n),
              "toxic": toxic, "tox_state": tox_state}
    tm = metrics.temporal_metrics(series, env, 0)
    assert tm["clock_rhythm"] > 0.9 and tm["anticipation"] > 0.5


def test_paired_learning_value():
    p = {"population": 1100, "intake": 300.0, "births": 50, "toxic_intake_frac": 0.2}
    f = {"population": 1000, "intake": 200.0, "births": 40, "toxic_intake_frac": 0.3}
    va = metrics.paired_learning_value(p, f)
    assert np.isclose(va["va_population"], 0.1) and np.isclose(va["va_intake"], 0.5)
    assert np.isclose(va["va_toxic_frac"], -0.1)
    assert np.isclose(va["va_log_population"], np.log(1101 / 1001))
    # simétrica y acotada aunque el gemelo congelado se extinga
    up = metrics.paired_learning_value({**p, "population": 99}, {**f, "population": 49})
    down = metrics.paired_learning_value({**p, "population": 49}, {**f, "population": 99})
    assert np.isclose(up["va_log_population"], -down["va_log_population"])
    dead = metrics.paired_learning_value(p, {**f, "population": 0})
    assert np.isfinite(dead["va_log_population"]) and dead["va_log_population"] < 8


def _small_run(tmp_path, monkeypatch, **kw):
    import json

    from panspermia import run as runner
    for name, value in (("EPOCH_STEPS", 60), ("CHECKPOINT_EVERY", 2), ("VIDEO_EVERY", 99),
                        ("FROZEN_PLASTICITY_TEST_EVERY", 2), ("CAPABILITY_TEST_EVERY", 99)):
        monkeypatch.setattr(config, name, value)
    out = tmp_path / "run"
    r = runner.run(0, 4, out, b"t", 128, 64, verbose=False, **kw)
    return r, json.loads((out / "stats" / "summary.json").read_text()), json.loads((out / "run.json").read_text())


def test_runner_with_schedule_reports_1d_metrics(tmp_path, monkeypatch):
    env = {"tox_mode": "periodico", "tox_period": 40, "clock_period": 40}
    _r, rows, meta = _small_run(tmp_path, monkeypatch, env_overrides=env)
    assert meta["env_overrides"] == env and meta["plastic"] is True
    assert "lifespan_mean" in rows[-1] and "clock_rhythm" in rows[-1] and "anticipation" in rows[-1]
    assert "va_population" in rows[1] and "frozen_population" in rows[1]  # sonda en la época 2
    assert not any(k.startswith("series_") for k in rows[-1])


def test_runner_without_plasticity_skips_probe_and_freezes_weights(tmp_path, monkeypatch):
    _r, rows, meta = _small_run(tmp_path, monkeypatch, plastic=False)
    assert meta["plastic"] is False
    assert all("va_population" not in row for row in rows)


def test_experiment_queue_validation(tmp_path):
    import json

    from panspermia import experiment
    q = tmp_path / "q.json"
    q.write_text(json.dumps([{"name": "a", "seeds": [0], "config": {"N_RAYS": 3}}]))
    with pytest.raises(ValueError):
        experiment.load_queue(q)
    q.write_text(json.dumps([{"name": "a", "seeds": [0]}, {"name": "a", "seeds": [1]}]))
    with pytest.raises(ValueError):
        experiment.load_queue(q)
    q.write_text(json.dumps([{"name": "a", "seeds": [0], "config": {"TOXIC_FACTOR": 0.25}}]))
    assert experiment.load_queue(q)[0]["config"]["TOXIC_FACTOR"] == 0.25
