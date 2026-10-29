import sys, time
from panspermia import island
island.setup_determinism()
import jax, numpy as np
from panspermia import genome as G, config as C

g = G.random_minimal(jax.random.PRNGKey(0))
for i in range(50):
    g = G.mutate(g, jax.random.PRNGKey(i + 1))
b = G.to_bytes(g)
g2, meta = G.from_bytes(b)
print("blob", len(b), "id", meta.id.hex())

n_max = int(sys.argv[1]) if len(sys.argv) > 1 else 1024
n_init = int(sys.argv[2]) if len(sys.argv) > 2 else 256
epochs = int(sys.argv[3]) if len(sys.argv) > 3 else 5
t = time.time()
s = island.init_island(0, b"node-0", n_max=n_max, n_init=n_init)
jax.block_until_ready(s.w); print("init", time.time() - t)
for e in range(epochs):
    t = time.time()
    s, st = island.epoch(s, C.EPOCH_STEPS)
    st = jax.device_get(st)
    dt = time.time() - t
    keys = ["population","population_min","births","deaths_starvation","deaths_attack","deaths_age","attacks","attack_gene_mean","clades_alive","comm_mi_bits","hidden_mean","generation_max"]
    print(e, f"{dt:.2f}s", {k: round(float(st[k]), 1) for k in keys}, flush=True)
