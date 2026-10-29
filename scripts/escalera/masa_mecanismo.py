"""¿Por qué los mundos de cuerpos grandes aprenden? (solo observa) Tamaño de las manchas de comida frente a
la distancia a la que nace el hijo (2 radios del padre), y cuántos vivos están sobre comida."""
import json, shutil, tempfile
from pathlib import Path
import jax, jax.numpy as jnp, numpy as np
import orbax.checkpoint as ocp
from scipy import ndimage
from panspermia import config as C, island, world
island.setup_determinism()
C.K_CUT = 1.5; C.FOOD_JUMP_PERIOD = 1000; C.FOOD_JUMP_DIST = 64.0
R = Path("/mnt/d/Development/panspermia/runs/fase1d")
for s in range(5):
    template = island.init_island(s, b"fase1d-w0", n_max=C.N_MAX, n_init=C.N_INIT)
    with tempfile.TemporaryDirectory() as tmp:
        shutil.copytree(R / "P4-salto64" / f"s{s}" / "checkpoints" / "300", Path(tmp) / "300")
        st = ocp.CheckpointManager(Path(tmp)).restore(300, args=ocp.args.StandardRestore(jax.tree.map(ocp.utils.to_shape_dtype_struct, template)))
    K = np.asarray(world.kmax_field(st.env, st.step))
    food = K > 0
    lab, n = ndimage.label(food, structure=np.ones((3, 3)))
    # en el toro: unir etiquetas de bordes opuestos (aproximación: se ignora; manchas que cruzan el borde cuentan partidas)
    sizes = np.bincount(lab.ravel())[1:] * world.RES_CELL ** 2
    req = np.sqrt(sizes / np.pi)                        # radio equivalente (u)
    a = np.asarray(st.alive); r = np.asarray(st.pheno.radius)[a]; pos = np.asarray(st.pos)[a]
    cell = (pos // world.RES_CELL).astype(int) % K.shape[0]
    on = food[cell[:, 0], cell[:, 1]]
    dist = ndimage.distance_transform_edt(~food) * world.RES_CELL
    d_food = dist[cell[:, 0], cell[:, 1]]
    row = dict(seed=s, food_frac=float(food.mean()), n_patches=int(n), patch_r_median=float(np.median(req)),
               patch_r_p90=float(np.percentile(req, 90)), radius_mean=float(r.mean()), birth_offset=float(2 * r.mean()),
               frac_on_food=float(on.mean()), dist_to_food_mean=float(d_food.mean()),
               sensor_range=float(np.asarray(st.pheno.sensor_range)[a].mean()), thrust=float(np.asarray(st.pheno.max_thrust)[a].mean()))
    print(json.dumps({k: round(v, 3) if isinstance(v, float) else v for k, v in row.items()}), flush=True)
