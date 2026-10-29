"""¿Comen siempre? (responsable, 23-10, 12:30; solo observa). Sustrato 3.0.0.

Por mundo y semilla (época 300), 200 pasos plásticos sin nacimientos. Por paso y bicho vivo los 200 pasos:
salida de comer encendida (flags bit 0), alga disponible en su casilla antes de comer, si esa alga es la
que no alimenta (P4-alga) y su energía. Mide:
  - fracción de pasos con la salida de comer encendida y bichos que la tienen encendida siempre;
  - P(comer | hay alga que alimenta), P(comer | no hay alga), P(comer | alga que no alimenta);
  - saciedad: P(comer) en el cuartil alto de energía del propio bicho frente al bajo.
Uso: python diag_comer.py <run> --config K=V ... --jsonl salida.jsonl
"""
import argparse, json
from pathlib import Path
import jax, jax.numpy as jnp, numpy as np
from panspermia import config as C, island, world
import diag_aprender as D

FOOD_MIN = 0.05  # alga en la casilla por encima de la cual cuenta como «hay comida»


def probe(s, T=200):
    swap = C.ALGA_SWAP_PERIOD > 0
    def body(c, _):
        c2, _ = island.world_step(c, births=False)
        cell = world._res_index(c2.pos)
        food = c.resources.ravel()[cell]
        if swap:
            empty = world.algae_type_a(c.env, c.step) != world.nourishing_is_a(c.env, c.step)
            bad = empty.ravel()[cell]
        else:
            bad = jnp.zeros_like(c2.alive)
        return c2, (c2.alive, (c2.flags & 1) > 0, food, bad, c2.energy)
    _, (alive, eat, food, bad, E) = jax.jit(lambda st: jax.lax.scan(body, st, None, length=T))(s)
    alive, eat, food, bad, E = map(np.asarray, (alive, eat, food, bad, E))
    keep = alive.all(0)
    eat, food, bad, E = eat[:, keep], food[:, keep], bad[:, keep], E[:, keep]
    has = food > FOOD_MIN
    good, nofood, badf = has & ~bad, ~has, has & bad
    p = lambda m: float(eat[m].mean()) if m.any() else None
    q1, q3 = np.percentile(E, 25, axis=0), np.percentile(E, 75, axis=0)
    lo, hi = E <= q1, E >= q3
    return {"n_keep": int(keep.sum()), "frac_eat": float(eat.mean()),
            "frac_always_eat": float(eat.all(0).mean()), "frac_never_eat": float((~eat).all(0).mean()),
            "frac_steps_good": float(good.mean()), "frac_steps_nofood": float(nofood.mean()),
            "frac_steps_bad": float(badf.mean()),
            "p_eat_good": p(good), "p_eat_nofood": p(nofood), "p_eat_bad": p(badf),
            "p_eat_E_low": p(lo & good), "p_eat_E_high": p(hi & good),
            "E_mean": float(E.mean()), "E_p90": float(np.percentile(E, 90))}


if __name__ == "__main__":
    pa = argparse.ArgumentParser()
    pa.add_argument("run", type=Path)
    pa.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2, 3, 4])
    pa.add_argument("--epoch", type=int, default=300)
    pa.add_argument("--config", nargs="*", default=[])
    pa.add_argument("--jsonl", type=Path, required=True)
    a = pa.parse_args()
    island.setup_determinism()
    for kv in a.config:
        k, v = kv.split("=")
        setattr(C, k, type(getattr(C, k))(float(v)))
    for seed in a.seeds:
        s = D.load(a.run, seed, a.epoch)
        row = {"run": a.run.name, "seed": seed, "epoch": a.epoch}
        row.update(probe(s))
        print(json.dumps({k: round(v, 3) if isinstance(v, float) else v for k, v in row.items()}), flush=True)
        with a.jsonl.open("a") as f:
            f.write(json.dumps(row) + "\n")
