"""Control positivo de b′ ajustado a la tarea real: dos pistas de color, A (mancha buena) y B (mancha equivocada), que
llegan 40 pasos antes de una racha de bocados (+0,5 o −0,75), y un señuelo con la misma frecuencia. Fondo con rachas
buenas sin anunciar (~31 % de pasos con bocado), migajas en ~66 % del resto. Se mide w_A − w_B (discrimina) y el señuelo."""
import numpy as np, math
TAU, EVERY = 50.0, 4
def run(variant, seed, K=8.65, T=60000, p_bout=0.06, p_cue=1/150, gap=40, mean_run=5, eta=0.02, trace=True):
    rng = np.random.default_rng(seed)
    lam = math.exp(-EVERY / 40.0) if trace else 0.0
    w = np.zeros(3); e = np.zeros(3); rbar = dacc = 0.0
    sched = {}; left = 0; val = 0.0; cues = np.zeros(3, int)
    for t in range(T):
        if rng.random() < p_cue: cues[0] = 4; sched[t + gap] = 0.5
        if rng.random() < p_cue: cues[1] = 4; sched[t + gap] = -0.75
        if rng.random() < p_cue: cues[2] = 4
        if left == 0:
            if t in sched: val = sched.pop(t); left = rng.geometric(1 / mean_run)
            elif rng.random() < p_bout: val = 0.5; left = rng.geometric(1 / mean_run)
        else:
            sched.pop(t, None)
        if left > 0: r = val; left -= 1
        else: r = rng.uniform(1e-5, 1e-3) if rng.random() < 0.66 else 0.0
        ev = abs(r) > 0.05
        if variant == 'C':      d = r - rbar; rbar += (r - rbar) / TAU
        elif variant == 'b1':   d = (r - rbar) if ev else 0.0; rbar += (r - rbar) / TAU          # panel 09: r̄ por paso
        elif variant == 'b2':                                                                      # r̄ solo en sucesos
            d = (r - rbar) if ev else 0.0
            if ev: rbar += (r - rbar) / TAU
        dacc += d
        pre = (cues > 0).astype(float); cues = np.maximum(cues - 1, 0)
        if t % EVERY == 0:
            m = np.clip(K * dacc, -1, 1); dacc = 0.0
            e = lam * e + (1 - lam) * pre
            w = np.clip(w + eta * m * e, -4, 4)
    return w
for v in ('C', 'b1', 'b2'):
    for tr in (True, False):
        ws = np.array([run(v, s, trace=tr) for s in range(6)])
        ab = ws[:, 0] - ws[:, 1]
        print(f'{v:<3} traza {tr!s:<5} A {np.median(ws[:,0]):+.2f}  B {np.median(ws[:,1]):+.2f}  señuelo {np.median(ws[:,2]):+.2f}  A−B med {np.median(ab):+.2f} ({(ab>0).sum()}/6)  A−señuelo {np.median(ws[:,0]-ws[:,2]):+.2f}  señuelo−B {np.median(ws[:,2]-ws[:,1]):+.2f}', flush=True)
