"""Hash del estado tras 3 épocas (comprobación bit a bit entre sustratos; solo observa)."""
import hashlib
import jax
import numpy as np
from panspermia import island

island.setup_determinism()
s = island.init_island(1, b"bit", n_max=256, n_init=64, env_overrides={"attack_on": 1, "signal_on": 1})
for _ in range(3):
    s, _ = island.epoch(s, 200)
h = hashlib.sha256()
for x in jax.tree.leaves(jax.device_get(s)):
    h.update(np.asarray(x).tobytes())
print(h.hexdigest())
