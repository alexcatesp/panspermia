"""Alga por bicho: ¿el tiempo sobre su alga buena es experiencia o maduración? (responsable, 25-10, entre las 21:46 y las 21:52; solo observa).
Sustrato 3.4.0 (escalera-algabicho), con ALGA_PER_AGENT=1. Variante de madura.py con una cuarta crianza:
  X: su mundo, pero durante la crianza el alga que alimenta a cada bicho es la contraria (la tripa le enseña la equivocada).
Examen con el alga verdadera; además de la ingesta mide frac_buena = pasos sobre su alga buena / pasos sobre comida y
D_comer = P(comer | su buena) − P(comer | la otra).
Regla (fijada antes de ver datos): experiencia del alga si frac_buena(E) − frac_buena(X) ≥ 0,05 en ≥ 8/10 mundos;
maduración y reflejo si |E − X| < 0,05 en ≥ 8/10 y frac_buena(D) ≥ frac_buena(N) + ½ (frac_buena(E) − frac_buena(N)).

Con --scatter (primaria de las manchas, diseno.md v2.3), el examen empieza con las posiciones de los vivos barajadas
entre ellos (la misma baraja para los cinco cerebros): nadie parte de la mancha de su alga, que en el checkpoint ya ocupaba.

Lo que sigue es la cabecera de madura.py.

Desde el checkpoint de una época, todos los vivos vuelven a su cerebro de recién nacido (w = w0, h = 0) y
aprenden REAR pasos de dos maneras, sin nacimientos y sin coste de vivir (nadie muere de hambre: los mismos
bichos en las dos crianzas):
  E: su mundo de siempre;
  D: el mismo mundo sin comida (el campo de algas a 0 en cada paso).
Examen: los bichos vuelven al estado original (sitio, energía, comida) con uno de cuatro cerebros, congelado:
  N (recién nacido), E, D y A (el adulto real del checkpoint). TEST pasos sin nacimientos ni coste de vivir.
Índice M = (ingesta D − N) / (ingesta E − N): la parte de lo aprendido que aparece sin haber visto comida.
M ≈ 0: depende de la experiencia; M ≈ 1: maduración.
Uso: python madura.py <run> --seeds 0 1 --config K=V ... --jsonl salida.jsonl
"""
import argparse, json, shutil, tempfile
from pathlib import Path
import jax, jax.numpy as jnp, numpy as np
import orbax.checkpoint as ocp
from panspermia import config as C, island, world

FOOD_MIN = 0.05


def load(run, seed, epoch):
    template = island.init_island(seed, b"fase1d-w0", n_max=C.N_MAX, n_init=C.N_INIT)
    with tempfile.TemporaryDirectory() as tmp:
        shutil.copytree(run / f"s{seed}" / "checkpoints" / str(epoch), Path(tmp) / str(epoch))
        return ocp.CheckpointManager(Path(tmp)).restore(
            epoch, args=ocp.args.StandardRestore(jax.tree.map(ocp.utils.to_shape_dtype_struct, template)))


def with_brain(s, w):
    return s.replace(w=jnp.where(s.alive[:, None, None], w, s.w), h=jnp.zeros_like(s.h),
                     env=s.env.replace(metabolism=jnp.float32(0.0)))


def rear(s, steps, food, flip=False):
    orig = world.good_alga_a
    if flip:  # se traza con el sorteo invertido; island.py llama a world.good_alga_a
        world.good_alga_a = lambda env, uid: ~orig(env, uid)
    try:
        return _rear(s, steps, food)
    finally:
        world.good_alga_a = orig


def _rear(s, steps, food):
    def body(c, _):
        if not food:
            c = c.replace(resources=jnp.zeros_like(c.resources))
        c2, _ = island.world_step(c, plastic=True, births=False)
        return c2, None
    out, _ = jax.lax.scan(body, s, None, length=steps)
    return out.w


def exam(s, steps):
    a0 = s.alive

    def body(c, _):
        food = (c.resources.ravel()[world._res_index(c.pos)] > FOOD_MIN).astype(jnp.float32)
        c2, _ = island.world_step(c, plastic=False, births=False)
        m = (a0 & c.alive).astype(jnp.float32)
        eat = ((c2.flags & 1) > 0).astype(jnp.float32)
        intake = c2.behavior.intake - c.behavior.intake
        speed = jnp.linalg.norm(c2.vel, axis=-1)
        on_a = world.algae_type_a(c.env, c.step).ravel()[world._res_index(c.pos)]
        own = (on_a == world.good_alga_a(c.env, c.lineage.uid)).astype(jnp.float32)
        return c2, jnp.stack([m, m * intake, m * eat, m * food, m * eat * food, m * speed,
                              m * food * own, m * eat * food * own])
    _, acc = jax.lax.scan(body, s, None, length=steps)
    return acc.sum((0, 2))


def scatter(s, seed):
    """Baraja las posiciones de los vivos entre ellos (los muertos se quedan donde estaban)."""
    alive = s.alive
    r = jnp.where(alive, jax.random.uniform(jax.random.PRNGKey(10_000 + seed), alive.shape), 2.0)
    order = jnp.argsort(r)                                      # vivos primero, en orden al azar
    slots = jnp.argsort(jnp.where(alive, 0, 1), stable=True)    # vivos primero, en su orden
    return s.replace(pos=s.pos.at[slots].set(s.pos[order]))


def summary(tot):
    n, it, eat, food, eatf, sp, good, eatg = [float(x) for x in np.asarray(tot)]
    bad, eatb = food - good, eatf - eatg
    return {"frac_buena": good / max(food, 1), "D_comer": eatg / max(good, 1) - eatb / max(bad, 1), "ingesta": it / n, "come": eat / n, "sobre_comida": food / n,
            "p_comer_comida": eatf / max(food, 1), "p_comer_sin": (eat - eatf) / max(n - food, 1), "velocidad": sp / n}


if __name__ == "__main__":
    pa = argparse.ArgumentParser()
    pa.add_argument("run", type=Path)
    pa.add_argument("--seeds", type=int, nargs="+", default=list(range(10)))
    pa.add_argument("--epoch", type=int, default=300)
    pa.add_argument("--rear", type=int, default=200)
    pa.add_argument("--test", type=int, default=500)
    pa.add_argument("--config", nargs="*", default=[])
    pa.add_argument("--jsonl", type=Path, required=True)
    pa.add_argument("--scatter", action="store_true")
    a = pa.parse_args()
    island.setup_determinism()
    for kv in a.config:
        k, v = kv.split("=")
        cur = getattr(C, k)
        setattr(C, k, float(v) if cur is None else type(cur)(float(v)))
    assert C.ALGA_PER_AGENT, "hace falta ALGA_PER_AGENT=1"
    rear_j = jax.jit(rear, static_argnums=(1, 2, 3))
    exam_j = jax.jit(exam, static_argnums=(1,))
    for seed in a.seeds:
        s = load(a.run, seed, a.epoch)
        w0 = s.pheno.w0.astype(jnp.float32)
        newborn = with_brain(s, w0)
        brains = {"N": w0, "E": rear_j(newborn, a.rear, True), "D": rear_j(newborn, a.rear, False),
                  "X": rear_j(newborn, a.rear, True, True), "A": s.w}
        s_ex = scatter(s, seed) if a.scatter else s
        res = {k: summary(exam_j(with_brain(s_ex, w), a.test)) for k, w in brains.items()}
        gain = res["E"]["ingesta"] - res["N"]["ingesta"]
        M = (res["D"]["ingesta"] - res["N"]["ingesta"]) / gain if abs(gain) > 1e-9 else None
        row = {"run": a.run.name, "seed": seed, "epoch": a.epoch, "rear": a.rear, "test": a.test, "scatter": a.scatter,
               "n": int(np.asarray(s.alive).sum()), "M": M, **res}
        print(json.dumps({"run": a.run.name, "seed": seed, "M": None if M is None else round(M, 3),
                          **{k: round(v["ingesta"], 4) for k, v in res.items()},
                          "come": {k: round(v["come"], 3) for k, v in res.items()},
                          "vel": {k: round(v["velocidad"], 2) for k, v in res.items()},
                          "frac_buena": {k: round(v["frac_buena"], 3) for k, v in res.items()},
                          "D_comer": {k: round(v["D_comer"], 3) for k, v in res.items()}}), flush=True)
        with a.jsonl.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
