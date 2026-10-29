import numpy as np, math, sys
K, TAU, EVERY, TT = 8.65, 50.0, 4, 40.0
def run(event_eps, trace, seed=0, T=40000, b=0.1, p_bg=0.03, p_cue=1/120, eta=0.05, gap=40, bad_frac=0.5):
    rng = np.random.default_rng(seed)
    lam = math.exp(-EVERY/TT) if trace else 0.0
    w = np.zeros(2); e = np.zeros(2); rbar = 0.0; dacc = 0.0
    pending = []
    cue_on = dec_on = 0
    for t in range(T):
        if rng.random() < p_cue: cue_on = 4; pending.append(t + gap)
        if rng.random() < p_cue: dec_on = 4
        r = 0.0
        if pending and pending[0] == t: pending.pop(0); r = b
        elif rng.random() < p_bg: r = b * rng.uniform(0.2, 1) * (-1.5 if rng.random() < bad_frac else 1.0)
        d = r - rbar
        if event_eps is not None and abs(r) <= event_eps: d = 0.0
        rbar += (r - rbar) / TAU; dacc += d
        pre = np.array([cue_on > 0, dec_on > 0], float)
        cue_on = max(cue_on - 1, 0); dec_on = max(dec_on - 1, 0)
        if t % EVERY == 0:
            m = np.clip(K * dacc, -1, 1); dacc = 0.0
            e = lam * e + (1 - lam) * pre
            w = np.clip(w + eta * m * e, -4, 4)
    return w
for eps in (None, 1e-6, 0.005, 0.02):
    for tr in (True, False):
        ws = np.array([run(eps, tr, s) for s in range(5)])
        print('eps', eps, 'trace', tr, 'pista', ws[:,0].round(3), 'señuelo', ws[:,1].round(3))
