from panspermia import island
island.setup_determinism()
import jax, numpy as np
from panspermia import metrics

s = island.init_island(0, b"node-0", n_max=1024, n_init=512)
s, st = island.epoch(s, 300)
print("hist\n", np.asarray(s.comm_hist))
print("mi", metrics.mutual_information(s.comm_hist))
sig = np.asarray(s.signal)[np.asarray(s.alive)]
print("signal pct", np.percentile(sig, [0, 10, 50, 90, 100]))
