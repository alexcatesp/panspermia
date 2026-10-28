"""b′, δ solo en sucesos (3.9, ADR-034): δ y r̄ a mano, barajado del δ filtrado y control positivo del mecanismo con la
estadística de P5-inmediato-C (B + C: trazas y δ por sucesos). CPU o GPU, N pequeño."""
import math

import jax
import jax.numpy as jnp
import numpy as np

from panspermia import brain, config, island
from test_c import _setup

EPS = 0.05


def _series(monkeypatch, delta_on, eps, steps, plastic=False):
    _setup(monkeypatch, delta_on, DELTA_EVENT_EPS=eps)
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


def test_event_delta_by_hand(monkeypatch):
    """r̄ se actualiza en todos los pasos; δ_acc solo suma r − r̄ en los pasos con |r| > ε y se vacía en cada paso plástico."""
    _, ser = _series(monkeypatch, 1, EPS, 80)
    n_ev = n_quiet = 0
    for e in ser:
        a = e["alive"]
        r = np.where(e["alive0"], e["r"], 0.0)
        ev = np.abs(r) > EPS
        n_ev += int((ev & a).sum())
        n_quiet += int((~ev & (r != 0) & a).sum())
        assert np.allclose(e["rbar"][a], (e["rbar0"] + (r - e["rbar0"]) / config.DELTA_TAU)[a], atol=1e-6)
        want = 0.0 if e["t"] % config.PLASTICITY_EVERY == 0 else e["dacc0"] + np.where(ev, r - e["rbar0"], 0.0)
        assert np.allclose(e["dacc"][a], np.broadcast_to(want, a.shape)[a], atol=1e-6)
    assert n_ev > 0 and n_quiet > 0  # hubo bocados completos y migajas


def test_eps_off_keeps_c(monkeypatch):
    """Con ε = 0, el δ de C: también en las migajas y en los pasos sin comer (δ = −r̄)."""
    _, ser = _series(monkeypatch, 1, 0.0, 40)
    for e in ser[1:]:
        if e["t"] % config.PLASTICITY_EVERY == 0:
            continue
        a = e["alive"]
        r = np.where(e["alive0"], e["r"], 0.0)
        assert np.allclose(e["dacc"][a], (e["dacc0"] + r - e["rbar0"])[a], atol=1e-6)


def test_shuffled_events_is_a_lagged_copy(monkeypatch):
    """Con DELTA_ON = 2 y ε, el δ barajado en t es el δ filtrado de t − L, L ∈ [32, 63]: conserva cuántos sucesos hay."""
    T = 300
    _, real = _series(monkeypatch, 1, EPS, T)
    _, shuf = _series(monkeypatch, 2, EPS, T)
    gated = np.stack([np.where(np.abs(np.where(e["alive0"], e["r"], 0.0)) > EPS,
                               np.where(e["alive0"], e["r"], 0.0) - e["rbar0"], 0.0) for e in real])
    ds = np.stack([e["dacc"] - (0 if e["t"] % config.PLASTICITY_EVERY == 0 else e["dacc0"]) for e in shuf])
    plastic_step = np.array([e["t"] % config.PLASTICITY_EVERY == 0 for e in real])
    alive_all = np.stack([e["alive"] for e in real]).all(0)
    hits = total = 0
    for t in range(100, T):
        if plastic_step[t]:
            continue
        for i in np.nonzero(alive_all)[0]:
            total += 1
            hits += bool(np.isclose(ds[t, i], gated[t - config.DELTA_BUFFER + 1:t - config.DELTA_LAG_MIN + 1, i],
                                    atol=1e-6).any())
    assert total > 0 and hits == total
    # cuántos sucesos: los de la ventana de la que copia (al principio del mundo se come más)
    ts = [t for t in range(100, T) if not plastic_step[t]]
    got = np.mean([(ds[t, alive_all] != 0).mean() for t in ts])
    want = np.mean([(gated[t - config.DELTA_BUFFER + 1:t - config.DELTA_LAG_MIN + 1][:, alive_all] != 0).mean()
                    for t in ts])
    assert want > 0 and abs(got - want) < 0.3 * want


def _task(seed, T, gap=40, p_cue=1 / 150, p_bout=0.06, mean_run=5):
    """Estadística de P5-inmediato-C (scratchpad/mide_r2.py, 28-10): rachas de bocados completos (+0,5) de ~5 pasos en
    ~31 % de los pasos y migajas (|r| < 0,001) en el 66 % del resto. Pista A 40 pasos antes de una racha buena (+0,5),
    pista B antes de una mala (−0,75, el alga equivocada) y un señuelo con la misma frecuencia que no anuncia nada."""
    rng = np.random.default_rng(seed)  # solo el test; el núcleo no usa numpy.random
    r, pre = np.zeros(T, np.float32), np.zeros((T, 3), np.float32)
    sched, left, val, on = {}, 0, 0.0, np.zeros(3, int)
    for t in range(T):
        if rng.random() < p_cue:
            on[0] = 4
            sched[t + gap] = 0.5
        if rng.random() < p_cue:
            on[1] = 4
            sched[t + gap] = -0.75
        if rng.random() < p_cue:
            on[2] = 4
        if left == 0:
            if t in sched:
                val, left = sched.pop(t), rng.geometric(1 / mean_run)
            elif rng.random() < p_bout:
                val, left = 0.5, rng.geometric(1 / mean_run)
        else:
            sched.pop(t, None)
        if left > 0:
            r[t], left = val, left - 1
        elif rng.random() < 0.66:
            r[t] = rng.uniform(1e-5, 1e-3)
        pre[t] = on > 0
        on = np.maximum(on - 1, 0)
    return r, pre


def _learn(monkeypatch, eps, lam, r, pre):
    """El circuito de island (_delta, δ_acc, m_eff = clip(k·δ_acc)) y la regla de brain sobre N bichos sintéticos."""
    monkeypatch.setattr(config, "DELTA_ON", 1)
    monkeypatch.setattr(config, "DELTA_EVENT_EPS", eps)
    jax.clear_caches()
    n = r.shape[1]
    full = lambda v: jnp.full((n, 3, 1), v, jnp.float32)
    ph = type("P", (), dict(A=full(1.0), B=full(0.0), C=full(0.0), D=full(0.0), eta=full(0.02), g=full(1.0)))

    def body(c, x):
        w, e, rbar, dacc, t = c
        rt, pt = x
        delta, rbar = island._delta(rt, rbar)
        dacc = dacc + delta

        def upd(we):
            m = island._with_delta(jnp.zeros(n), dacc)
            return brain.plasticity_trace(ph, we[0], we[1], pt, jnp.ones((n, 1)), m, lam)

        w, e = jax.lax.cond(t % config.PLASTICITY_EVERY == 0, upd, lambda we: we, (w, e))
        dacc = jnp.where(t % config.PLASTICITY_EVERY == 0, 0.0, dacc)
        return (w, e, rbar, dacc, t + 1), None

    z = jnp.zeros((n, 3, 1))
    c0 = (z, z, jnp.zeros(n), jnp.zeros(n), jnp.int32(0))
    w = jax.jit(lambda r, p: jax.lax.scan(body, c0, (r, p))[0][0])(jnp.asarray(r), jnp.asarray(pre))
    return np.asarray(w)[:, :, 0]


def test_positive_control_cue_before_bite(monkeypatch):
    """B + C, control positivo con la estadística real. Con δ por sucesos y trazas, la pista del alga buena acaba por
    encima del señuelo y la del alga equivocada por debajo, y discriminan mucho más que con el δ de C (ε = 0, castigo
    tónico) o sin trazas. Al escribirlo (28-10) se vio que todos los pesos suben a la vez (se refuerza lo activo antes de
    comer); la medida es el orden y la diferencia A − B, no el signo."""
    seeds, T = 6, 40000
    data = [_task(s, T) for s in range(seeds)]
    r = np.stack([d[0] for d in data], 1)
    pre = np.stack([d[1] for d in data], 1)
    lam = math.exp(-config.PLASTICITY_EVERY / 40.0)
    b = _learn(monkeypatch, EPS, lam, r, pre)
    c = _learn(monkeypatch, 0.0, lam, r, pre)
    no_trace = _learn(monkeypatch, EPS, 0.0, r, pre)
    ab = lambda w: np.median(w[:, 0] - w[:, 1])
    print("A−B b′", round(ab(b), 3), "C", round(ab(c), 3), "sin trazas", round(ab(no_trace), 3),
          "| b′ A, B, señuelo", np.median(b, 0).round(2))
    assert ((b[:, 0] > b[:, 2]) & (b[:, 2] > b[:, 1])).sum() >= 5
    assert ab(b) > 2 * ab(c) and ab(b) > 3 * abs(ab(no_trace))
    for e2 in (0.01, 0.2):  # ε en el hueco de la distribución real: mismo resultado
        assert np.allclose(_learn(monkeypatch, e2, lam, r, pre), b, atol=1e-5)
