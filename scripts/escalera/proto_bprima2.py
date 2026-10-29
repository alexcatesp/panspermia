"""Control positivo de b′ con estadística real de P5-inmediato-C (mide_r2.py): rachas de bocados completos (+0,5) con
media ~5 pasos, ~31 % de pasos con bocado bueno, ~1,2 % malos (−0,75), migajas (|r| < 0,001) en ~66 % de los demás."""
import numpy as np, math
K, TAU, EVERY = 8.65, 50.0, 4
def run(eps, trace, seed, T=60000, p_bout=0.06, p_cue=1/150, gap=40, mean_run=5, p_bad=0.04, eta=0.02, m_own=0.0):
    rng = np.random.default_rng(seed)
    lam = math.exp(-EVERY / 40.0) if trace else 0.0
    w = np.zeros(2); e = np.zeros(2); rbar = dacc = 0.0
    sched = {}; left = 0; val = 0.0; cue = dec = 0
    for t in range(T):
        if rng.random() < p_cue: cue = 4; sched[t + gap] = 0.5
        if rng.random() < p_cue: dec = 4
        if left == 0:
            if t in sched: val = sched.pop(t); left = rng.geometric(1 / mean_run)
            elif rng.random() < p_bout: val = -0.75 if rng.random() < p_bad else 0.5; left = rng.geometric(1 / mean_run)
        else:
            sched.pop(t, None)
        if left > 0: r = val; left -= 1
        else: r = rng.uniform(1e-5, 1e-3) if rng.random() < 0.66 else 0.0
        d = r - rbar
        if eps > 0 and abs(r) <= eps: d = 0.0
        rbar += (r - rbar) / TAU; dacc += d
        pre = np.array([cue > 0, dec > 0], float); cue = max(cue - 1, 0); dec = max(dec - 1, 0)
        if t % EVERY == 0:
            m = np.clip(m_own + K * dacc, -1, 1); dacc = 0.0
            e = lam * e + (1 - lam) * pre
            w = np.clip(w + eta * m * e, -4, 4)
    return w
for eps in (0.0, 1e-6, 0.01, 0.05, 0.2):
    for tr in (True, False):
        ws = np.array([run(eps, tr, s) for s in range(6)])
        dif = ws[:, 0] - ws[:, 1]
        print(f'eps {eps:<6} traza {tr!s:<5} pista {ws[:,0].round(2)} señuelo {ws[:,1].round(2)} pista−señuelo med {np.median(dif):+.3f} ({(dif>0).sum()}/6)', flush=True)
