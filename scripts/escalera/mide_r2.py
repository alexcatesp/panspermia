"""Distribución de r = bocado − cobro en mundos de C (solo observa): fracción de pasos con suceso, tamaños, r̄, rachas."""
import sys, json
from pathlib import Path
import jax, jax.numpy as jnp, numpy as np
from panspermia import config as C, island
import madura_alga as M
CFG = dict(ALGA_PER_AGENT=1, ALGA_PATCH_FAMILIES=1, K_CUT=1.7, EAT_MOVE_FACTOR=0, EAT_MOVE_RAMP_STEPS=100000,
           K_MEAN_RAMP_STEPS=100000, K_MEAN_RAMP_FROM=2, POISON_FACTOR=2.5, POISON_RAMP_STEPS=100000, POISON_DELAY=0,
           DELTA_K=8.65, DELTA_TAU=50, DELTA_ON=1)
island.setup_determinism()
for k, v in CFG.items():
    cur = getattr(C, k); setattr(C, k, float(v) if cur is None else type(cur)(float(v)))
run = Path(sys.argv[1]); out = {}
for seed in (0, 3):
    s = M.load(run, seed, 300)
    step = jax.jit(lambda c: island.world_step(c, plastic=True, births=True)[0])
    R, A, RB = [], [], []
    for _ in range(400):
        t = int(s.step); s = step(s)
        R.append(np.asarray(s.gut)[:, t % C.GUT_WINDOW]); A.append(np.asarray(s.alive)); RB.append(np.asarray(s.rbar))
    R, A, RB = np.stack(R), np.stack(A), np.stack(RB)
    r, rb = R[A], RB[A]
    ev = np.abs(r) > 0
    pos, neg = r[r > 0], r[r < 0]
    # rachas de sucesos consecutivos por bicho
    runs = []
    for i in np.nonzero(A.all(0))[0][:500]:
        x = np.abs(R[:, i]) > 0; c = 0
        for v in x:
            if v: c += 1
            elif c: runs.append(c); c = 0
    q = lambda a: [round(float(v), 4) for v in np.quantile(a, [0.05, 0.25, 0.5, 0.75, 0.95])] if a.size else None
    out[seed] = dict(frac_suceso=round(float(ev.mean()), 4), frac_pos=round(float((r > 0).mean()), 4), frac_neg=round(float((r < 0).mean()), 4),
                     r_pos_q=q(pos), r_neg_q=q(neg), abs_r_min=float(np.abs(r[ev]).min()), r_pequenos_lt_001=int(((np.abs(r) > 0) & (np.abs(r) < 0.01)).sum()),
                     rbar_q=q(rb), delta_ev_abs_med=round(float(np.median(np.abs(r[ev] - rb[ev]))), 4), racha_q=q(np.array(runs, float)))
    edges=[0,1e-3,1e-2,0.05,0.1,0.2,0.3,0.4,0.49,0.51,0.7,0.76,10]
    h,_=np.histogram(np.abs(r[ev]),edges); print(seed,'abs r hist',dict(zip([f'{a}-{b}' for a,b in zip(edges,edges[1:])],(h/h.sum()).round(4).tolist())))
    big=np.abs(r)>0.05; print(seed,'frac pasos |r|>0.05',round(float(big.mean()),4),'med |delta| ahi',round(float(np.median(np.abs(r[big]-rb[big]))),4),'sesgo pos',round(float((r[big]>0).mean()),3))
    print(seed, json.dumps(out[seed]), flush=True)
