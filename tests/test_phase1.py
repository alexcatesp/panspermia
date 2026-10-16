"""Tests de la fase 1: ataque, paredes, métricas, batería de capacidad, grabación y runner."""
import json

import jax
import jax.numpy as jnp
import numpy as np
import pytest

from panspermia import capability, config, island, metrics, record, world
from panspermia import genome as G
from panspermia.develop import develop_batch


def _small(seed=0, n_max=64, n_init=16):
    return island.init_island(seed, b"t", n_max=n_max, n_init=n_init)


def _two_agents(dist=10.0, angle_a=0.0):
    """Dos agentes vivos enfrentados en el centro del mundo."""
    s = _small(n_max=4, n_init=2)
    pos = jnp.array([[500.0, 500.0], [500.0 + dist, 500.0], [0, 0], [0, 0]])
    radius = jnp.full((4,), 4.0)
    return s.replace(pos=pos, angle=jnp.array([angle_a, np.pi, 0, 0]),
                     energy=jnp.array([30.0, 30.0, 0, 0]),
                     pheno=s.pheno.replace(radius=radius, attack=jnp.ones(4)))


def test_attack_conserves_energy():
    s = _two_agents(dist=9.0)
    actions = jnp.zeros((4, config.ACT_DIM)).at[0, 3].set(1.0)
    cand = world.neighbors(s.pos, s.alive)
    delta, drained, attempt, res = world.attack(s, actions, cand, s.resources)
    assert bool(attempt[0]) and float(drained[1]) > 0 and float(drained[0]) == 0
    carrion = float((np.asarray(res, np.float64) - np.asarray(s.resources, np.float64)).sum())
    assert np.isclose(float(delta[0]) + float(delta[1]) + carrion, 0.0, atol=1e-4)
    assert np.isclose(float(delta[0]), config.ATTACK_EFFICIENCY * float(drained[1]), atol=1e-6)


def test_attack_needs_target_in_front():
    s = _two_agents(dist=9.0, angle_a=np.pi)  # mira hacia el lado contrario
    actions = jnp.zeros((4, config.ACT_DIM)).at[0, 3].set(1.0)
    _, drained, _, _ = world.attack(s, actions, world.neighbors(s.pos, s.alive), s.resources)
    assert float(jnp.sum(drained)) == 0.0


def test_walls_block_movement():
    s = _two_agents()
    walls = jnp.zeros((config.RESOURCE_GRID,) * 2, bool)
    cell = int(508 // world.RES_CELL)
    walls = walls.at[cell, :].set(True)
    s = s.replace(env=s.env.replace(walls=walls), vel=jnp.array([[50.0, 0], [0, 0], [0, 0], [0, 0]]))
    actions = jnp.zeros((4, config.ACT_DIM))
    pos, vel, _, _ = world.physics(s, actions, world.neighbors(s.pos, s.alive))
    assert float(pos[0, 0]) < cell * world.RES_CELL
    assert float(jnp.abs(vel[0]).sum()) == 0.0


def test_walls_seen_by_distance_channel():
    s = _two_agents(dist=500.0)
    walls = jnp.zeros((config.RESOURCE_GRID,) * 2, bool).at[int(520 // world.RES_CELL), :].set(True)
    s = s.replace(env=s.env.replace(walls=walls),
                  pheno=s.pheno.replace(sensor_range=jnp.full((4,), 60.0), cone=jnp.full((4,), 1.0)))
    obs, _ = world.sense(s, world.neighbors(s.pos, s.alive))
    prox = np.asarray(obs[0, :config.N_RAYS * 4]).reshape(config.N_RAYS, 4)[:, 0]
    assert prox.max() > 0.5


def test_mutual_information_bounds():
    indep = jnp.ones((4, 4))
    perfect = jnp.eye(4)
    mi0, sym0 = metrics.mutual_information(indep)
    mi1, _ = metrics.mutual_information(perfect)
    assert float(mi0) < 1e-6 and np.isclose(float(sym0), 4.0)
    assert np.isclose(float(mi1), 2.0, atol=1e-5)


def test_novelty_archive_grows_only_with_novel():
    a = metrics.NoveltyArchive()
    rng = np.random.default_rng(0)
    first = a.update(rng.uniform(size=(64, len(metrics.DESCRIPTOR_NAMES))))
    assert first["archive_size"] > 0
    size = first["archive_size"]
    same = a.update(np.repeat(a.archive[:1], 64, axis=0))
    assert same["archive_size"] == size


def test_silhouette_detects_two_groups():
    rng = np.random.default_rng(1)
    x = np.concatenate([rng.normal(0.2, 0.02, (60, 8)), rng.normal(0.8, 0.02, (60, 8))])
    g = metrics.behavior_groups(np.clip(x, 0, 1), seed=0)
    assert g["groups_k"] == 2 and g["groups_silhouette"] > 0.8


def test_activity_tracker_counts_new_activity():
    t = metrics.ActivityTracker()
    clade = np.array([1] * 60 + [2] * 5)
    alive = np.ones(65, bool)
    assert t.update(clade, alive)["bp_new_activity"] == 0
    assert t.update(clade, alive)["bp_new_activity"] == 1  # el clado 1 cruza 100


def test_learning_survival():
    uid0 = np.array([1, 2, 3, 4]); a0 = np.array([1, 1, 1, 0], bool)
    uid1 = np.array([1, 9, 3, 4]); a1 = np.array([1, 1, 0, 1], bool)
    assert metrics.learning_survival(uid0, a0, uid1, a1) == pytest.approx(1 / 3)


def test_epoch_frozen_plasticity_keeps_weights():
    s = _small(n_max=128, n_init=64)
    s, _ = island.epoch(s, 50)
    w_before = np.asarray(s.w).copy()
    alive_before = np.asarray(s.alive).copy()
    uid_before = np.asarray(s.lineage.uid).copy()
    s, _ = island.epoch(s, 50, plastic=False)
    keep = alive_before & np.asarray(s.alive) & (np.asarray(s.lineage.uid) == uid_before)
    assert keep.any()
    assert np.array_equal(np.asarray(s.w)[keep], w_before[keep])


def test_record_epoch_matches_epoch(tmp_path):
    a, _ = island.epoch(_small(seed=5, n_max=128, n_init=64), 40)
    b, _, frames, res = record.record_epoch(_small(seed=5, n_max=128, n_init=64), 40)
    la, lb = jax.tree.leaves(jax.device_get(a)), jax.tree.leaves(jax.device_get(b))
    assert all(np.asarray(x).tobytes() == np.asarray(y).tobytes() for x, y in zip(la, lb))
    assert frames["pos"].shape == (40 // config.RECORD_STRIDE, 128, 2)
    record.save_recording(tmp_path / "rec", frames, res, {"epoch": 1})
    header = json.loads((tmp_path / "rec.json").read_text())
    assert set(header["arrays"]) >= {"pos", "flags", "resources", "clade"}
    assert (tmp_path / "rec.bin.gz").stat().st_size > 0


def test_capability_layouts():
    food, walls = capability.maze_layout()
    assert walls.any() and food.sum() > 0 and not (walls & (food > 0)).any()
    food, walls = capability.patch_layout()
    assert food.sum() > 0 and not walls.any()
    # la mancha queda fuera del alcance máximo de los sensores desde el punto de partida
    x, y = capability._grid()
    r = np.hypot(x - capability.CENTER, y - capability.CENTER)[food > 0]
    assert r.min() > config.SENSOR_RANGE_BOUNDS[1]


def test_capability_battery_runs_and_pause_logic():
    s = _small(n_max=256, n_init=128)
    s, st = island.epoch(s, 250)
    out = capability.run_battery(s, float(st["comm_mi_bits"]))
    for k in ("patch_gain", "maze_gain", "patch_baseline", "maze_baseline", "comm_mi_bits",
              "patch_baseline_controls", "patch_baseline_random"):
        assert k in out and np.isfinite(out[k])
    assert capability.exceeded({"maze_gain": 0.3}, {"maze_gain": 0.25}) == {"maze_gain": 0.3}
    assert capability.exceeded({"maze_gain": 0.1}, {"maze_gain": 0.25}) == {}
    assert out["patch_baseline"] == max(out["patch_baseline_controls"], out["patch_baseline_random"])
    assert out["patch_gain"] == out["patch_success"] - out["patch_baseline"]


def test_control_policy_overrides_brain():
    """Con control activo las acciones son las fijadas; con control inactivo, idéntico a None."""
    s = _small(n_max=64, n_init=32)
    a, _ = island.world_step(s, None, births=False)
    b, _ = island.world_step(s, None, births=False, control=jnp.zeros((3,)))
    assert np.array_equal(np.asarray(a.pos), np.asarray(b.pos))
    c, _ = island.world_step(s, None, births=False, control=jnp.array([1.0, 0.0, 0.0]))
    alive = np.asarray(s.alive)
    assert np.allclose(np.asarray(c.angle)[alive], np.asarray(s.angle)[alive])  # sin giro


def test_straight_walker_does_not_pass_patch():
    """Regresión del falso positivo v1: avanzar recto sin cerebro no supera la mancha lejana."""
    p = 32
    g = jax.vmap(G.random_minimal)(jax.random.split(jax.random.PRNGKey(3), p))
    ph = develop_batch(g)
    angles = jax.random.uniform(jax.random.PRNGKey(4), (p,), maxval=2 * np.pi)
    food, walls = capability.patch_layout()
    env = capability._probe_env(walls)
    s = capability.control_successes(env, g, ph, ph.w0.astype(jnp.float32), angles,
                                     jnp.asarray(food), config.PROBE_PATCH_STEPS)
    assert max(s) < 0.15, s


def test_runner_pause_and_review(tmp_path, monkeypatch):
    """El runner pausa al superar un umbral y no continúa sin revisión humana."""
    from panspermia import run as runner
    for name, value in (("EPOCH_STEPS", 60), ("CHECKPOINT_EVERY", 2), ("VIDEO_EVERY", 2),
                        ("FROZEN_PLASTICITY_TEST_EVERY", 2), ("CAPABILITY_TEST_EVERY", 2),
                        ("PROBE_PATCH_STEPS", 30), ("PROBE_MAZE_STEPS", 30)):
        monkeypatch.setattr(config, name, value)
    monkeypatch.setattr(config, "CAPABILITY_PAUSE_THRESHOLDS", {"comm_mi_bits": -1.0})
    out = tmp_path / "run"
    r = runner.run(0, 6, out, b"t", 128, 64, verbose=False)
    assert r["paused"] and (out / runner.PAUSE_FILE).exists()
    rows = json.loads((out / "stats" / "summary.json").read_text())
    assert rows[-1]["epoch"] == 2 and "learning_value" in rows[-1]
    assert (out / "recordings" / "epoch_000002.json").exists()
    with pytest.raises(runner.CapabilityPause):
        runner.run(0, 6, out, b"t", 128, 64, verbose=False)
    (out / runner.REVIEW_FILE).write_text(json.dumps(
        {"reviewed_by": "test", "thresholds": {"comm_mi_bits": 99.0}}))
    r = runner.run(0, 6, out, b"t", 128, 64, verbose=False)
    assert not r["paused"]
    rows = json.loads((out / "stats" / "summary.json").read_text())
    assert [row["epoch"] for row in rows] == list(range(1, 7))


def test_viewer_serves_only_run_dir(tmp_path):
    from panspermia import viewer
    run = tmp_path / "run"
    (run / "stats").mkdir(parents=True)
    (run / "stats" / "summary.json").write_text("[]")
    (tmp_path / "secret.txt").write_text("x")
    root = run.resolve()
    assert viewer._inside(root, "stats/summary.json") is not None
    assert viewer._inside(root, "../secret.txt") is None
    assert viewer._inside(root, "stats") is None  # sin listados de directorio
    assert (viewer.STATIC / "index.html").exists()


def test_runner_stops_when_extinct(tmp_path, monkeypatch):
    """Si la isla sigue extinguiéndose pese a reinyectar, el runner se detiene y lo indica."""
    from panspermia import run as runner
    for name, value in (("EPOCH_STEPS", 40), ("EXTINCT_STOP_EPOCHS", 2), ("C_BASAL", 1e4),
                        ("FROZEN_PLASTICITY_TEST_EVERY", 99), ("VIDEO_EVERY", 99),
                        ("CAPABILITY_TEST_EVERY", 99)):
        monkeypatch.setattr(config, name, value)
    r = runner.run(0, 10, tmp_path / "run", b"t", 128, 64, verbose=False)
    assert r["stopped_extinct"] and r["extinct_at"] == 1
    rows = json.loads((tmp_path / "run" / "stats" / "summary.json").read_text())
    assert rows[-1]["epoch"] == 2
