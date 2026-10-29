"""¿b′ con ε = 0 es C bit a bit? Corre 120 pasos plásticos de un mundo de P5-inmediato-C (δ real) y guarda el estado."""
import sys, numpy as np, jax
sys.path.insert(0, sys.argv[2] + "/tests")
from panspermia import config as C, island
from ref_p5i import CFG
island.setup_determinism()
for k, v in {**CFG, "DELTA_ON": 1}.items():
    cur = getattr(C, k); setattr(C, k, float(v) if cur is None else type(cur)(v))
s = island.init_island(3, b"bitid", n_max=256, n_init=256)
step = jax.jit(lambda c: island.world_step(c)[0])
for _ in range(120):
    s = step(s)
np.savez(sys.argv[1], **{f: np.asarray(getattr(s, f)) for f in ("w", "rbar", "dacc", "energy", "pos", "alive")})
