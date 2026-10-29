import os
os.environ["XLA_PYTHON_CLIENT_PREALLOCATE"] = "false"
from panspermia import island
island.setup_determinism()
import jax

s = island.init_island(0, b"n", n_max=64, n_init=16)
a = jax.tree_util.tree_flatten_with_path(s)[0]
before = {jax.tree_util.keystr(p): (x.dtype, x.shape, getattr(x, "weak_type", None) or x.aval.weak_type) for p, x in a}
s, _ = island.epoch(s, 10)
b = jax.tree_util.tree_flatten_with_path(s)[0]
for p, x in b:
    k = jax.tree_util.keystr(p)
    now = (x.dtype, x.shape, x.aval.weak_type)
    if before[k] != now:
        print(k, before[k], "->", now)
print("done")
