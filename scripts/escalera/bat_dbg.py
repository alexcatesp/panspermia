"""¿Por qué los genomas al azar aprueban la mancha y el laberinto (0,77)? Solo observa."""
import math, jax, jax.numpy as jnp, numpy as np
from panspermia import capability as K, config as C, genome as G
from panspermia.develop import develop_batch
p = 64
key = jax.random.PRNGKey(7)
g = jax.vmap(G.random_minimal)(jax.random.split(key, p)); ph = develop_batch(g); w = ph.w0.astype(jnp.float32)
v = jnp.ones((p,), bool); ang = jax.random.uniform(jax.random.PRNGKey(8), (p,), maxval=2 * math.pi)
food, walls = K.patch_layout()
print("celdas con comida:", int((food > 0).sum()), "total", float(food.sum()))
print("ocultas al azar:", np.asarray(g.hid_mask).sum(1).mean())
for name, (fd, wl) in {"patch": (food, walls), "vacío": (np.zeros_like(food), walls), "maze": K.maze_layout()}.items():
    env = K._probe_env(wl)
    it = np.asarray(K._run_probe(env, g, ph, w, v, ang, jnp.asarray(fd), C.PROBE_PATCH_STEPS))
    print(f"{name:6s} éxito {np.mean(it >= C.PROBE_SUCCESS_INTAKE):.3f} · ingesta mediana {np.median(it):.3f} máx {it.max():.2f}")
print("env de prueba: chem_on", float(K._probe_env(walls).chem_on), "attack_on", float(K._probe_env(walls).attack_on))
for name, (fd, wl) in {"patch": (food, walls), "vacío": (np.zeros_like(food), walls), "maze": K.maze_layout()}.items():
    env = K._probe_env(wl).replace(chem_on=jnp.float32(0.0))
    it = np.asarray(K._run_probe(env, g, ph, w, v, ang, jnp.asarray(fd), C.PROBE_PATCH_STEPS))
    print(f"chem_on=0 {name:6s} éxito {np.mean(it >= C.PROBE_SUCCESS_INTAKE):.3f} · ingesta mediana {np.median(it):.3f} máx {it.max():.2f}")
for (th, tu) in C.PROBE_CONTROLS:
    for chem in (1.0, 0.0):
        env = K._probe_env(walls).replace(chem_on=jnp.float32(chem))
        it = np.asarray(K._run_probe(env, g, ph, w, v, ang, jnp.asarray(food), C.PROBE_PATCH_STEPS, jnp.array([1.0, th, tu], jnp.float32)))
        print(f"control ({th},{tu}) chem_on={chem}: éxito {np.mean(it >= 1):.3f}")
