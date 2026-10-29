"""Calibración de P2-buscar: comida solo donde z >= corte (fase1d-w0). Solo calcula el campo."""
import numpy as np, jax.numpy as jnp
from scipy import ndimage
from panspermia import world, config as C
env = world.make_env(b"fase1d-w0")
K0 = np.asarray(world.kmax_field(env, jnp.int32(0)))
c = (np.arange(128) + .5) / 128
cx, cy = np.meshgrid(c, c, indexing="ij")
wk, wp, wa = map(np.asarray, (env.wave_k, env.wave_phase, env.wave_amp))
z = sum(wa[i] * np.sin(2 * np.pi * (wk[i, 0] * cx + wk[i, 1] * cy) + wp[i]) for i in range(len(wa)))
z = z / np.sqrt(np.sum(wa ** 2) / 2)
km = float(env.k_mean)
assert np.allclose(km * np.maximum(0, 1 + C.K_CONTRAST * z), K0, atol=1e-3)
cell = C.WORLD_L / 128
print(f"k_mean {km:.2f}; ondas {wk.tolist()}")
for cut in (-9, 0.5, 1.0, 1.25, 1.5, 1.75, 2.0, 2.25):
    food = z >= cut
    K = np.where(food, K0, 0)
    tiled = np.tile(~food, (3, 3))  # toro
    d = ndimage.distance_transform_edt(tiled)[128:256, 128:256] * cell
    lab, n = ndimage.label(np.tile(food, (3, 3)))
    n_p = len(np.unique(lab[128:256, 128:256][food[:, :]]))
    print(f"corte {cut:5.2f}: suelo con comida {food.mean()*100:5.1f} % · comida total {K.sum()/K0.sum()*100:5.1f} % de P2 · "
          f"distancia media a comida {d[~food].mean() if (~food).any() else 0:6.1f} u · suelo a >60 u {np.mean(d > 60)*100:5.1f} % · "
          f"máx {d.max():6.1f} u · manchas {n_p}")
