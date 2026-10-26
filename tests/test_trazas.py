"""Trazas de elegibilidad (3.7, ADR-031): equivalencia, crédito diferido, control positivo del mecanismo, acotación,
determinismo y reinicios. Todo en CPU con N pequeño."""
import math
from types import SimpleNamespace

import jax
import jax.numpy as jnp
import numpy as np

from panspermia import brain, config, island

LAM = math.exp(-config.PLASTICITY_EVERY / 40.0)


def _pheno(p, q, A=1.0, B=0.0, C_=0.0, D=0.0, eta=1.0, g=1.0):
    full = lambda v: jnp.full((1, p, q), v, jnp.float32)
    return SimpleNamespace(A=full(A), B=full(B), C=full(C_), D=full(D), eta=full(eta), g=full(g))


def _run(monkeypatch, trace_on, tau, steps=40, seed=0):
    monkeypatch.setattr(config, "TRACE_ON", trace_on)
    monkeypatch.setattr(config, "TRACE_TAU", tau)
    jax.clear_caches()  # las constantes se leen al trazar
    s = island.init_island(seed, b"trazas-test", n_max=64, n_init=64)
    step = jax.jit(lambda c: island.world_step(c)[0])
    for _ in range(steps):
        s = step(s)
    return s


def test_trace_off_and_lambda_zero_match_the_old_rule(monkeypatch):
    off = _run(monkeypatch, 0, 40.0)
    zero = _run(monkeypatch, 1, 1e-9)                                     # λ = exp(−4/1e-9) = 0
    for name in ("w", "h", "energy", "pos", "alive"):
        assert np.array_equal(np.asarray(getattr(off, name)), np.asarray(getattr(zero, name))), name


def test_delayed_credit_by_hand():
    """Un pre y un post en la actualización 0 sin modulación; 7 actualizaciones (28 pasos) sin actividad; m = 1 en la 7.ª."""
    p, q = 3, 2
    ph, w = _pheno(p, q), jnp.zeros((1, p, q))
    pre0, post0 = jnp.zeros((1, p)).at[0, 0].set(1.0), jnp.zeros((1, q)).at[0, 1].set(1.0)
    zero_pre, zero_post = jnp.zeros((1, p)), jnp.zeros((1, q))

    def credit(k, lam):
        e = jnp.zeros((1, p, q))
        wt, e = brain.plasticity_trace(ph, w, e, pre0, post0, jnp.zeros(1), lam)
        for _ in range(k - 1):
            wt, e = brain.plasticity_trace(ph, wt, e, zero_pre, zero_post, jnp.zeros(1), lam)
        wt, e = brain.plasticity_trace(ph, wt, e, zero_pre, zero_post, jnp.ones(1), lam)
        return np.asarray(wt)[0]

    expect = np.zeros((p, q))
    expect[0, 1] = (1 - LAM) * LAM ** 7
    assert np.allclose(credit(7, LAM), expect, rtol=1e-5, atol=0)
    assert np.array_equal(credit(7, 0.0), np.zeros((p, q)))               # sin traza no hay crédito
    w_old = brain.plasticity(ph, w, zero_pre, zero_post, jnp.ones(1))      # la regla de siempre tampoco
    assert np.array_equal(np.asarray(w_old)[0], np.zeros((p, q)))
    assert credit(75, LAM).max() < 1e-3 * expect.max() * 10              # 300 pasos después, ≈ 0


def test_delayed_conditioning_is_learned_only_with_trace():
    """Control positivo del mecanismo, sin evolución. En la mitad de los ensayos (al azar) aparece el estímulo (pre 0);
    7 actualizaciones (28 pasos) después llega el resultado: m = +½ si hubo estímulo y −½ si no (la recompensa menos
    su media, centrada en el momento del resultado); m = 0 el resto del tiempo. Un distractor (pre 1) se activa al azar
    con la misma frecuencia. Con traza, el estímulo gana peso y el distractor casi nada; sin traza, el estímulo nada.
    Al escribir el test (26-10) se vio que, con m solo positiva, la traza premia la actividad reciente, sea cual sea, y
    gana el distractor; y que con una línea base en cada paso el estímulo, 28 pasos antes, sale castigado: la traza
    necesita una modulación que diga «mejor o peor de lo esperado» en el momento del resultado."""
    p, q, trials, gap = 2, 1, 300, 7
    ph = _pheno(p, q, eta=0.05)
    rng = np.random.default_rng(0)                                         # solo el test; el núcleo no usa numpy.random
    cs = rng.random(trials) < 0.5
    distractor = rng.random(trials * (gap + 1)) < 0.5 / (gap + 1)

    def learn(lam):
        w, e, t = jnp.zeros((1, p, q)), jnp.zeros((1, p, q)), 0
        for i in range(trials):
            for k in range(gap + 1):
                pre = jnp.asarray([[1.0 if (k == 0 and cs[i]) else 0.0, 1.0 if distractor[t] else 0.0]])
                m = jnp.full((1,), 0.5 if cs[i] else -0.5) if k == gap else jnp.zeros(1)
                w, e = brain.plasticity_trace(ph, w, e, pre, jnp.ones((1, q)), m, lam)
                t += 1
        return np.asarray(w)[0, :, 0]

    with_trace, without = learn(LAM), learn(0.0)
    assert with_trace[0] > 0.1 and with_trace[0] > 3 * abs(with_trace[1])
    assert without[0] == 0.0


def test_trace_is_bounded():
    p, q = 4, 3
    ph = _pheno(p, q, A=50.0, B=5.0, C_=5.0, D=5.0, eta=1.0, g=1.0)
    w, e = jnp.zeros((1, p, q)), jnp.zeros((1, p, q))
    pre, post = jnp.ones((1, p)), jnp.ones((1, q))
    hebb_max = 50.0 + 5.0 * 3
    for _ in range(200):
        w, e = brain.plasticity_trace(ph, w, e, pre, post, jnp.ones(1), LAM)
    assert np.all(np.isfinite(np.asarray(w))) and np.abs(np.asarray(w)).max() <= config.W_MAX
    assert np.abs(np.asarray(e)).max() <= hebb_max * (1 + 1e-6)


def test_trace_deterministic_and_reset(monkeypatch):
    a = _run(monkeypatch, 1, 40.0, steps=60)
    b = _run(monkeypatch, 1, 40.0, steps=60)
    assert np.array_equal(np.asarray(a.trace), np.asarray(b.trace))
    assert np.array_equal(np.asarray(a.w), np.asarray(b.w))
    assert a.trace.shape == (64, config.N_PRE, config.N_POST)
    dead = ~np.asarray(a.alive)
    assert np.all(np.asarray(a.trace)[dead] == 0.0)                       # se borra al morir
    assert np.abs(np.asarray(a.trace)).max() > 0                          # y los vivos la llevan
