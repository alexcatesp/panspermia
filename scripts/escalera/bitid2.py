"""Huella de un mundo P2 pequeño tras 600 pasos (para comparar ramas bit a bit)."""
import hashlib, sys, jax, numpy as np
from panspermia import island
island.setup_determinism()
ov = {"attack_on": 0, "chem_on": 0, "signal_on": 0, "seasonal": 0, "repro_mode": sys.argv[2], "drift": 0.0}
s = island.init_island(0, b"fase1d-w0", n_max=256, n_init=64, env_overrides=ov)
for _ in range(4):
    s, st = island.epoch(s, 200)
h = hashlib.sha256()
for name in ("alive", "pos", "energy", "age", "resources", "w"):
    h.update(np.asarray(getattr(s, name)).tobytes())
for leaf in jax.tree.leaves(s.genome):
    h.update(np.asarray(leaf).tobytes())
print(sys.argv[1], sys.argv[2], h.hexdigest()[:16], int(st["population"]), float(st["intake"]))
