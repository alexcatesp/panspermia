"""Manchas con dos familias de ondas (3.5.0): suelo con comida, manchas mezcladas, separación y k_mean para la misma
comida total que el padre (sin corte, k_mean 1,902). Solo observa, CPU, campos del paso 0."""
import numpy as np, jax.numpy as jnp
from scipy import ndimage
from panspermia import config as C, island, world
s = island.init_island(0, b"fase1d-w0", n_max=512, n_init=64)
env = s.env.replace(k_mean=jnp.float32(1.902))
C.K_CUT = None; C.ALGA_PATCH_FAMILIES = 0
K0 = np.asarray(world.kmax_field(env, jnp.int32(0)))
for fam in (1,):
    for cut in (1.55, 1.6, 1.65, 1.7):
        C.K_CUT = cut; C.ALGA_PATCH_FAMILIES = fam
        K = np.asarray(world.kmax_field(env, jnp.int32(0))); A = np.asarray(world.algae_type_a(env, jnp.int32(0)))
        lab, n = ndimage.label(K > 0, structure=np.ones((3, 3)))
        idx = range(1, n + 1)
        sizes = np.asarray(ndimage.sum(np.ones_like(K), lab, idx)); fa = np.asarray(ndimage.mean(A.astype(float), lab, idx))
        big = sizes >= 4; mixed = (fa > 0.1) & (fa < 0.9)
        cell = C.WORLD_L / K.shape[0]
        com = np.array(ndimage.center_of_mass(K > 0, lab, idx)) * cell
        d = np.sqrt(((com[big, None] - com[None, big]) ** 2).sum(-1)); np.fill_diagonal(d, 1e9)
        food_a = (K * A).sum() / K.sum()
        print(f"familias {fam} K_CUT {cut}: comida {np.mean(K>0)*100:.1f} % del suelo; manchas {big.sum()}; lado medio "
              f"{np.sqrt(sizes[big].mean())*cell:.0f} u; mezcladas {mixed[big].mean()*100:.0f} % (superficie "
              f"{sizes[big & mixed].sum()/sizes[big].sum()*100:.0f} %); vecina a {np.median(d.min(1)):.0f} u; comida A {food_a*100:.0f} %; "
              f"k_mean para la misma comida total: {1.902 * K0.sum() / K.sum():.3f}")
