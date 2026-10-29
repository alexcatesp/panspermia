import time
import panspermia  # noqa: F401  (flags antes de JAX)
from panspermia import island
island.setup_determinism()
import jax
from panspermia import genome as G
from panspermia.develop import develop

for b in (16, 32):
    g = jax.vmap(G.random_minimal)(jax.random.split(jax.random.PRNGKey(0), b))
    f = jax.jit(jax.vmap(develop))
    jax.block_until_ready(f(g))
    t = time.perf_counter()
    for _ in range(50):
        out = f(g)
    jax.block_until_ready(out)
    print(b, f"{(time.perf_counter() - t) / 50 * 1e3:.2f} ms por lote")
