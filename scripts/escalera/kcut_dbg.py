import numpy as np, jax.numpy as jnp
from panspermia import island, world, config as C
s = island.init_island(0, b"fase1d-w0", n_max=64, n_init=16, env_overrides={"repro_mode": "edad", "drift": 0.0})
print("k_cut", float(s.env.k_cut), "K>0", float(np.mean(np.asarray(world.kmax_field(s.env, jnp.int32(0))) > 0)),
      "res>0", float(np.mean(np.asarray(s.resources) > 0)))
