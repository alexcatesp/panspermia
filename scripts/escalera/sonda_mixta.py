"""¿Qué aprenden? Sonda mixta (responsable, 23-10, 23:20; solo observa). Sustrato 2.11.0 (escalera-masa).

Restaura un mundo y lo corre T pasos con plasticidad, pero devolviendo cada paso sus pesos de antes a la
mitad de los bichos (uid impar): media población aprende y media está congelada **en el mismo mundo**,
con la misma comida, vecinos y saltos. Los recién nacidos entran en un grupo u otro por su uid, sea cual
sea el de su padre. Así la ecología es común y la diferencia es del individuo, no demográfica.

Por grupo (0 plástico, 1 congelado) y tramo de edad:
  - ingesta por bicho y paso (la curva por edad separa «aprende en vida» de «nace distinto»);
  - P(comer | hay comida), P(comer | no hay), velocidad, giro;
  - hijos por bicho y paso (por el grupo del padre) y muertes por bicho y paso.
Solo cuentan los nacidos durante la sonda. Al final, en los vivos de 50 pasos o más: |w − w0| por bloque (entrada → oculta o acción),
para ver qué conexiones cambia la plasticidad.
Uso: python sonda_mixta.py <run> --seeds 0 1 --config K=V ... --jsonl salida.jsonl
"""
import argparse, json, shutil, tempfile
from pathlib import Path
import jax, jax.numpy as jnp, numpy as np
import orbax.checkpoint as ocp
from panspermia import config as C, island, world

AGE_EDGES = np.array([10, 25, 50, 100, 150, 200, 300], np.int32)   # tramos: <10, 10–25, …, ≥300
NB = len(AGE_EDGES) + 1
FOOD_MIN = 0.05


def load(run, seed, epoch):
    template = island.init_island(seed, b"fase1d-w0", n_max=C.N_MAX, n_init=C.N_INIT)
    with tempfile.TemporaryDirectory() as tmp:
        shutil.copytree(run / f"s{seed}" / "checkpoints" / str(epoch), Path(tmp) / str(epoch))
        return ocp.CheckpointManager(Path(tmp)).restore(
            epoch, args=ocp.args.StandardRestore(jax.tree.map(ocp.utils.to_shape_dtype_struct, template)))


def frozen_of(uid):
    return (uid % 2) == 1


NULL = False  # control nulo: las dos mitades congeladas (la etiqueta sigue siendo la paridad del uid)


def body(c, _, step0=0):
    c2, _ = island.world_step(c, plastic=True)
    same = (c2.lineage.uid == c.lineage.uid) & c.alive          # mismo bicho antes y después del paso
    fr = frozen_of(c.lineage.uid)
    c2 = c2.replace(w=jnp.where((same & (fr | NULL))[:, None, None], c.w, c2.w))
    # observaciones del paso, por el estado de antes (vivos al empezar)
    a = c.alive & (c.lineage.birth_step >= step0)   # solo los nacidos durante la sonda
    g = fr.astype(jnp.int32)
    b = jnp.searchsorted(jnp.asarray(AGE_EDGES), c.age, side="right")
    seg = jnp.where(a, g * NB + b, 2 * NB)
    sm = lambda x: jax.ops.segment_sum(jnp.where(a, x, 0.0).astype(jnp.float32), seg, num_segments=2 * NB + 1)[:-1]
    d = lambda f: jnp.where(same, f(c2.behavior) - f(c.behavior), 0.0)
    intake = d(lambda bh: bh.intake)
    speed = d(lambda bh: bh.speed)
    turn = d(lambda bh: bh.turn)
    eat = ((c2.flags & 1) > 0).astype(jnp.float32)
    food = (c.resources.ravel()[world._res_index(c2.pos)] > FOOD_MIN).astype(jnp.float32)
    died = (a & (~c2.alive | ~same)).astype(jnp.float32)
    newborn = c2.alive & ~same
    pg = frozen_of(c2.lineage.parent_uid).astype(jnp.int32)
    births = jax.ops.segment_sum(newborn.astype(jnp.float32), jnp.where(newborn, pg, 2), num_segments=3)[:2]
    out = dict(n=sm(jnp.ones_like(intake)), intake=sm(intake), speed=sm(speed), turn=sm(turn), eat=sm(eat),
               food=sm(food), eat_food=sm(eat * food), eat_nofood=sm(eat * (1 - food)), died=sm(died))
    if getattr(C, "ALGA_PER_AGENT", 0):  # 3.3 (ADR-026): ¿come su alga buena y deja la vacía? (diseño v2.0)
        on_a = world.algae_type_a(c.env, c.step).ravel()[world._res_index(c2.pos)]
        own = (on_a == world.good_alga_a(c.env, c.lineage.uid)).astype(jnp.float32)
        out.update(good=sm(food * own), bad=sm(food * (1 - own)), eat_good=sm(eat * food * own),
                   eat_bad=sm(eat * food * (1 - own)))
    return c2, (out, births)


def weight_change(s, step0):
    a = np.asarray(s.alive) & (np.asarray(s.age) >= 50) & (np.asarray(s.lineage.birth_step) >= step0)
    fr = np.asarray(frozen_of(s.lineage.uid))
    dw = np.abs(np.asarray(s.w) - np.asarray(s.pheno.w0, np.float32))
    w0 = np.abs(np.asarray(s.pheno.w0, np.float32))
    H = C.N_HIDDEN_MAX
    pre = {"rayo_prox": slice(0, 64, 4), "rayo_comida": slice(1, 64, 4), "rayo_parentesco": slice(2, 64, 4),
           "rayo_señal": slice(3, 64, 4), "energia": slice(64, 65), "velocidad": slice(65, 67),
           "reloj": slice(67, 69), "señal_oida": slice(69, 70), "quimica": slice(70, 79),
           "oculta": slice(C.OBS_DIM, C.OBS_DIM + H)}
    if C.OBS_DIM == 80:  # sustrato 3.x: la tripa es la última entrada (ADR-024)
        pre["tripa"] = slice(79, 80)
    post = {"oculta": slice(0, H), "empuje": slice(H, H + 1), "giro": slice(H + 1, H + 2), "comer": slice(H + 2, H + 3)}
    res = {}
    for grp, m in (("plastico", a & ~fr), ("congelado", a & fr)):
        if not m.any():
            continue
        D, W = dw[m], w0[m]
        res[grp] = {"n": int(m.sum()), "frac_cambia": float((D.reshape(D.shape[0], -1).max(1) > 1e-3).mean())}
        blk = {}
        for pk, ps in pre.items():
            for qk, qs in post.items():
                blk[f"{pk}→{qk}"] = [float(D[:, ps, qs].sum((1, 2)).mean()), float(W[:, ps, qs].sum((1, 2)).mean())]
        res[grp]["bloques"] = blk  # [Σ|Δw| medio por bicho, Σ|w0| medio por bicho]
    return res


def probe(s, T):
    step0 = int(s.step)
    f = lambda c, x: body(c, x, step0)
    s2, (acc, births) = jax.jit(lambda st: jax.lax.scan(f, st, None, length=T))(s)
    acc = {k: np.asarray(v).sum(0).reshape(2, NB) for k, v in acc.items()}
    births = np.asarray(births).sum(0)
    row = {}
    for gi, gname in enumerate(("plastico", "congelado")):
        n = acc["n"][gi]
        tot = lambda k: float(acc[k][gi].sum())
        N = tot("n")
        row[gname] = {
            "pasos_bicho": N, "ingesta_por_paso": tot("intake") / N, "hijos_por_paso": float(births[gi]) / N,
            "muertes_por_paso": tot("died") / N, "p_comer_comida": tot("eat_food") / max(tot("food"), 1),
            "p_comer_sin": tot("eat_nofood") / max(N - tot("food"), 1), "frac_sobre_comida": tot("food") / N,
            "velocidad": tot("speed") / N, "giro": tot("turn") / N,
            "por_edad": {k: (acc[k][gi] / np.maximum(n, 1)).round(4).tolist() for k in ("intake", "food", "speed", "turn")},
            "pasos_por_edad": n.tolist(),
            "p_comer_comida_edad": (acc["eat_food"][gi] / np.maximum(acc["food"][gi], 1)).round(3).tolist(),
        }
        if "good" in acc:
            pg, pb = tot("eat_good") / max(tot("good"), 1), tot("eat_bad") / max(tot("bad"), 1)
            row[gname].update(p_comer_buena=pg, p_comer_vacia=pb, D=pg - pb, pasos_buena=tot("good"), pasos_vacia=tot("bad"),
                              D_edad=(acc["eat_good"][gi] / np.maximum(acc["good"][gi], 1)
                                      - acc["eat_bad"][gi] / np.maximum(acc["bad"][gi], 1)).round(3).tolist())
    row["pesos"] = weight_change(s2, step0)
    return row


if __name__ == "__main__":
    pa = argparse.ArgumentParser()
    pa.add_argument("run", type=Path)
    pa.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2, 3, 4])
    pa.add_argument("--epoch", type=int, default=300)
    pa.add_argument("--steps", type=int, default=2000)
    pa.add_argument("--config", nargs="*", default=[])
    pa.add_argument("--jsonl", type=Path, required=True)
    pa.add_argument("--null", action="store_true")
    a = pa.parse_args()
    NULL = a.null
    island.setup_determinism()
    for kv in a.config:
        k, v = kv.split("=")
        cur = getattr(C, k)
        setattr(C, k, float(v) if cur is None else type(cur)(float(v)))
    for seed in a.seeds:
        s = load(a.run, seed, a.epoch)
        row = {"run": a.run.name, "seed": seed, "null": a.null, "epoch": a.epoch, "steps": a.steps, "edades": AGE_EDGES.tolist()}
        row.update(probe(s, a.steps))
        p, f = row["plastico"], row["congelado"]
        print(json.dumps({"run": a.run.name, "seed": seed,
                          "ingesta": [round(p["ingesta_por_paso"], 4), round(f["ingesta_por_paso"], 4)],
                          "hijos": [round(p["hijos_por_paso"], 5), round(f["hijos_por_paso"], 5)],
                          "muertes": [round(p["muertes_por_paso"], 5), round(f["muertes_por_paso"], 5)],
                          "p_comer_comida": [round(p["p_comer_comida"], 3), round(f["p_comer_comida"], 3)],
                          "p_comer_sin": [round(p["p_comer_sin"], 3), round(f["p_comer_sin"], 3)],
                          **({"D": [round(p["D"], 3), round(f["D"], 3)]} if "D" in p else {})}), flush=True)
        with a.jsonl.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
