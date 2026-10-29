import sys
from pathlib import Path
import panspermia  # noqa: F401
from panspermia import island
island.setup_determinism()
import jax, numpy as np
import orbax.checkpoint as ocp
from panspermia import metrics, config as C

run = Path(sys.argv[1]).resolve()
step = int(sys.argv[2])
state = island.init_island(0, b"x")
abstract = jax.tree.map(ocp.utils.to_shape_dtype_struct, state)
mngr = ocp.CheckpointManager(run / "checkpoints")
state = mngr.restore(step, args=ocp.args.StandardRestore(abstract))
v = metrics.host_view(state)
d = metrics.descriptors(v)
rng = np.random.default_rng(0)
s = d[rng.choice(len(d), min(512, len(d)), replace=False)]
np.set_printoptions(precision=2, suppress=True)
print("n", len(d), "media", d.mean(0), "\nstd  ", d.std(0))
print("frac nunca reproducido", (s[:, 7] >= 1.0).mean())
for cols, name in ((slice(None), "todas"), (slice(0, 7), "sin repro_age")):
    x = s[:, cols]
    for k in (2, 3):
        lab = metrics.kmeans(x, k, np.random.default_rng(1))
        print(name, "k", k, "silueta", round(metrics.silhouette(x, lab), 3),
              "centros", [x[lab == j].mean(0).round(2).tolist() for j in range(k)])
