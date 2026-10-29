"""Complemento de hunger_probe: solo la respuesta inmediata, separando bichos que empujan más,
menos o igual (|Δ| < 1e-6) al sentirse hambrientos. La regla pide «más del 90 % en una dirección»;
frac_pos sola no distingue «menos» de «nada»."""
import json, math, sys
from pathlib import Path
import numpy as np, jax.numpy as jnp
sys.path.insert(0, str(Path(__file__).parent))
import hunger_probe as H
from panspermia import brain, config as C, island, world

run, label, out = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
azar = "--azar" in sys.argv
if "--kcut" in sys.argv:
    C.K_CUT = float(sys.argv[sys.argv.index("--kcut") + 1])
island.setup_determinism()
for seed in range(5):
    s = H.load(run, seed, 300, b"fase1d-w0")
    if azar:
        fresh = island.init_island(seed, b"fase1d-w0", n_max=C.N_MAX, n_init=C.N_MAX)
        s = fresh.replace(env=s.env, resources=s.resources, energy=jnp.where(fresh.alive, s.energy.mean(), 0.0))
    cand = world.neighbors(s.pos, s.alive)
    obs, _ = H._sense(s, cand)
    a = np.asarray(s.alive)
    thr = {}
    for name, e in (("low", H.LOW), ("high", H.HIGH)):
        o = obs.at[:, H.E_IDX].set(math.tanh(e / C.E_OBS_SCALE))
        act, *_ = brain.step(s.w, s.h, o, s.genome.hid_mask)
        thr[name] = np.asarray(act[:, 0] * s.pheno.max_thrust)[a]
    d = thr["low"] - thr["high"]
    sd = float(np.std(thr["high"])) or 1.0
    resp = np.abs(d) > 0.05 * sd
    row = {"run": label, "seed": seed, "n": int(a.sum()),
           "pos": float(np.mean(d > 1e-6)), "neg": float(np.mean(d < -1e-6)), "zero": float(np.mean(np.abs(d) <= 1e-6)),
           "resp_pos": float(np.mean(d[resp] > 0)) if resp.any() else None, "n_resp": int(resp.sum()),
           "abs_rel": float(np.abs(d).mean() / sd)}
    print(json.dumps(row), flush=True)
    with out.open("a") as f:
        f.write(json.dumps(row) + "\n")
