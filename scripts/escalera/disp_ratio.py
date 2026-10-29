import numpy as np, jax.numpy as jnp
from panspermia import world, config as C
env = world.make_env(b"fase1d-w0")
K0 = np.asarray(world.kmax_field(env, jnp.int32(0)))
c = (np.arange(128) + .5) / 128
cx, cy = np.meshgrid(c, c, indexing="ij")
wk, wp, wa = map(np.asarray, (env.wave_k, env.wave_phase, env.wave_amp))
z = sum(wa[i] * np.sin(2 * np.pi * (wk[i, 0] * cx + wk[i, 1] * cy) + wp[i]) for i in range(len(wa)))
z = z / np.sqrt(np.sum(wa ** 2) / 2)
r = K0[z >= 1.5].sum() / K0.sum()
print("fraccion", r, "k_mean igual total que 1.902:", 1.902 / r, "K max con ese k_mean", (1.902 / r) * (1 + C.K_CONTRAST * z.max()))
