"""C, modulación con signo de resultado (3.8, ADR-033): apagado idéntico a 3.6.0, δ y su acumulación a mano,
reinicios, determinismo, barajado, cambio de signo con m saturada y control positivo del mecanismo. CPU o GPU, N pequeño."""
from pathlib import Path
from types import SimpleNamespace

import jax
import jax.numpy as jnp
import numpy as np

from panspermia import brain, config, island
from ref_p5i import CFG, FIELDS, run

DATA = Path(__file__).parent / "data"


def _setup(monkeypatch, delta_on, **extra):
    for k, v in {**CFG, "DELTA_ON": delta_on, **extra}.items():
        cur = getattr(config, k)
        monkeypatch.setattr(config, k, float(v) if cur is None else type(cur)(v))
    jax.clear_caches()  # las constantes se leen al trazar


def _series(monkeypatch, delta_on, steps, plastic=True):
    """Recorre `steps` pasos y guarda por paso (paso viejo, rbar, dacc, gut del paso, vivos antes y después)."""
    _setup(monkeypatch, delta_on)
    s = island.init_island(0, b"c-test", n_max=64, n_init=64)
    step = jax.jit(lambda c: island.world_step(c, plastic=plastic, births=False)[0])
    out = []
    for _ in range(steps):
        s2 = step(s)
        out.append(dict(t=int(s.step), rbar0=np.asarray(s.rbar), dacc0=np.asarray(s.dacc), rbar=np.asarray(s2.rbar),
                        dacc=np.asarray(s2.dacc), r=np.asarray(s2.gut)[:, int(s.step) % config.GUT_WINDOW],
                        alive0=np.asarray(s.alive), alive=np.asarray(s2.alive)))
        s = s2
    return s, out


def test_off_matches_360(monkeypatch):
    ref = np.load(DATA / f"p5i_360_{jax.default_backend()}.npz")
    monkeypatch.setattr(config, "DELTA_ON", 0)
    got = run(config, island)
    for f in FIELDS:
        assert np.array_equal(ref[f], got[f]), f


def test_delta_and_accumulation_by_hand(monkeypatch):
    """r = bocado − cobro (en el inmediato el cobro va en el bocado: r = gut del paso); r̄ ← r̄ + (r − r̄)/τ;
    δ_acc suma δ = r − r̄ y se vacía en cada paso plástico (paso viejo múltiplo de PLASTICITY_EVERY)."""
    _, ser = _series(monkeypatch, 1, 40)
    for e in ser:
        a = e["alive"]
        r = np.where(e["alive0"], e["r"], 0.0)
        assert np.allclose(e["rbar"][a], (e["rbar0"] + (r - e["rbar0"]) / config.DELTA_TAU)[a], atol=1e-6)
        want = 0.0 if e["t"] % config.PLASTICITY_EVERY == 0 else e["dacc0"] + (r - e["rbar0"])
        assert np.allclose(e["dacc"][a], np.broadcast_to(want, a.shape)[a], atol=1e-6)
    assert any(np.abs(e["r"]).max() > 0 for e in ser)  # hubo bocados


def test_reset_and_determinism(monkeypatch):
    a, _ = _series(monkeypatch, 1, 60)
    b, _ = _series(monkeypatch, 1, 60)
    for f in ("w", "rbar", "dacc", "energy"):
        assert np.array_equal(np.asarray(getattr(a, f)), np.asarray(getattr(b, f))), f
    dead = ~np.asarray(a.alive)
    assert np.all(np.asarray(a.rbar)[dead] == 0.0) and np.all(np.asarray(a.dacc)[dead] == 0.0)
    assert np.abs(np.asarray(a.rbar)).max() > 0


def test_on_changes_learning_only(monkeypatch):
    """Con plastic=False, δ no toca la dinámica: C encendido y apagado dan el mismo mundo."""
    off, _ = _series(monkeypatch, 0, 40, plastic=False)
    on, _ = _series(monkeypatch, 1, 40, plastic=False)
    for f in ("w", "energy", "pos", "alive"):
        assert np.array_equal(np.asarray(getattr(off, f)), np.asarray(getattr(on, f))), f
    plastic_on, _ = _series(monkeypatch, 1, 40)
    plastic_off, _ = _series(monkeypatch, 0, 40)
    assert not np.array_equal(np.asarray(plastic_on.w), np.asarray(plastic_off.w))


def test_shuffled_is_a_lagged_copy(monkeypatch):
    """Con plastic=False el mundo es el mismo con δ real y barajado; el barajado en t es el δ real de t − L, L ∈ [32, 63],
    conserva la distribución y no se correlaciona con el resultado del paso."""
    T = 400
    _, real = _series(monkeypatch, 1, T, plastic=False)
    _, shuf = _series(monkeypatch, 2, T, plastic=False)
    # δ real de cada paso, exacto: r − r̄ antes de actualizar; el barajado solo se reconstruye fuera de los pasos plásticos
    dr = np.stack([np.where(e["alive0"], e["r"], 0.0) - e["rbar0"] for e in real])
    ds = np.stack([e["dacc"] - (0 if e["t"] % config.PLASTICITY_EVERY == 0 else e["dacc0"]) for e in shuf])
    plastic_step = np.array([e["t"] % config.PLASTICITY_EVERY == 0 for e in real])
    alive_all = np.stack([e["alive"] for e in real]).all(0)
    hits, total = 0, 0
    for t in range(100, T):
        if plastic_step[t]:
            continue
        for i in np.nonzero(alive_all)[0]:
            cand = dr[t - config.DELTA_BUFFER + 1:t - config.DELTA_LAG_MIN + 1, i]
            total += 1
            hits += bool(np.isclose(ds[t, i], cand, atol=1e-6).any())
    assert total > 0 and hits == total
    keep = ~plastic_step[100:]
    a, b = dr[100:][keep][:, alive_all].ravel(), ds[100:][keep][:, alive_all].ravel()
    assert abs(a.mean() - b.mean()) < 0.25 * a.std() and 0.7 < b.std() / a.std() < 1.4
    r = np.stack([e["r"] for e in real])[100:][keep][:, alive_all].ravel()
    ca, cb = np.corrcoef(a, r)[0, 1], np.corrcoef(b, r)[0, 1]
    print("corr(δ, r) real", round(ca, 3), "barajado", round(cb, 3))
    assert ca > 0.5 and abs(cb) < 0.5 * ca


def test_saturated_m_flips_sign():
    """Con m pegada a +1 y un δ_acc típico negativo (−0,209, la mediana de D), m_eff cambia de signo, y Δw con él."""
    import panspermia.island as isl
    old = config.DELTA_ON
    config.DELTA_ON = 1
    try:
        m = isl._with_delta(jnp.ones(2), jnp.array([-0.209, 0.209]))
    finally:
        config.DELTA_ON = old
    assert float(m[0]) < -0.5 and float(m[1]) == 1.0
    full = lambda v: jnp.full((2, 2, 1), v, jnp.float32)
    ph = SimpleNamespace(A=full(1.0), B=full(0.0), C=full(0.0), D=full(0.0), eta=full(0.1), g=full(1.0))
    w = brain.plasticity(ph, jnp.zeros((2, 2, 1)), jnp.ones((2, 2)), jnp.ones((2, 1)), m)
    assert float(w[0, 0, 0]) < 0 < float(w[1, 0, 0])


def test_positive_control_immediate():
    """Control positivo del mecanismo, sin evolución: el estímulo (pre 0) y el resultado llegan en la misma actualización
    (como en el inmediato). m = clip(k·δ) con δ = r − r̄ (EMA) calculado como en island: el estímulo gana peso y un
    distractor al azar con la misma frecuencia (pre 1) no gana: como δ = −r̄ cuando no se come, la parte sin premio
    empuja el distractor hacia abajo (m tónica negativa), no hacia arriba."""
    rng = np.random.default_rng(0)  # solo el test; el núcleo no usa numpy.random
    n = 1500
    cs = rng.random(n) < 0.3                     # el estímulo anuncia un buen bocado
    bite = rng.random(n) < 0.3                   # bocados normales, sin estímulo
    dis = rng.random(n) < 0.3
    full = lambda v: jnp.full((1, 2, 1), v, jnp.float32)
    ph = SimpleNamespace(A=full(1.0), B=full(0.0), C=full(0.0), D=full(0.0), eta=full(0.01), g=full(1.0))
    w, rbar = jnp.zeros((1, 2, 1)), 0.0
    alpha = config.PLASTICITY_EVERY / config.DELTA_TAU  # una actualización = 4 pasos
    for t in range(n):
        r = 1.0 if cs[t] else (0.2 if bite[t] else 0.0)
        delta = r - rbar
        rbar += alpha * (r - rbar)
        m = jnp.clip(jnp.array([config.DELTA_K * delta]), -1.0, 1.0)
        pre = jnp.array([[1.0 if cs[t] else 0.0, 1.0 if dis[t] else 0.0]])
        w = brain.plasticity(ph, w, pre, jnp.ones((1, 1)), m)
    w = np.asarray(w)[0, :, 0]
    print("estímulo", round(float(w[0]), 3), "distractor", round(float(w[1]), 3))
    assert w[0] > 1.0 and w[1] < 0.0
