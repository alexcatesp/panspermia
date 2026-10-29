"""¿Cuántas manchas de comida (K_CUT) tienen los dos tipos de alga? Solo observa, CPU, campos del paso 0."""
import numpy as np, jax.numpy as jnp
from scipy import ndimage
from panspermia import config as C, island, world
for cut in (1.0, 1.5):
    C.K_CUT = cut
    for seed in range(3):
        s = island.init_island(seed, b"fase1d-w0", n_max=512, n_init=64)
        env = s.env.replace(k_mean=jnp.float32(1.902))
        K = np.asarray(world.kmax_field(env, jnp.int32(0))); A = np.asarray(world.algae_type_a(env, jnp.int32(0)))
        lab, n = ndimage.label(K > 0, structure=np.ones((3, 3)))   # sin unir por los bordes del toro (aprox.)
        sizes = ndimage.sum(np.ones_like(K), lab, range(1, n + 1))
        fa = ndimage.mean(A.astype(float), lab, range(1, n + 1))
        mixed = ((fa > 0.1) & (fa < 0.9))
        cell = C.WORLD_L / K.shape[0]
        com = np.array(ndimage.center_of_mass(K > 0, lab, range(1, n + 1))) * cell
        big = sizes >= 4
        d = np.sqrt(((com[big, None] - com[None, big]) ** 2).sum(-1)); np.fill_diagonal(d, 1e9)
        print(f"K_CUT {cut} s{seed}: comida {np.mean(K>0)*100:.0f} % del suelo; manchas {n} (>=4 casillas: {big.sum()}); "
              f"tamaño medio {sizes[big].mean()*cell*cell**0:.0f} casillas ({np.sqrt(sizes[big].mean())*cell:.0f} u de lado); "
              f"mezcladas {mixed[big].mean()*100:.0f} % (por superficie {sizes[big & mixed].sum()/sizes[big].sum()*100:.0f} %); "
              f"distancia a la vecina {np.median(d.min(1)):.0f} u")
