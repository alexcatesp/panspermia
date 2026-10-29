"""Diagnóstico de C (ADR-033; solo observa): ¿la mejor supervivencia en la crianza invertida viene del aprendizaje guiado por δ?
Desde el checkpoint, todos los vivos vuelven a su cerebro de recién nacido y se crían REAR pasos como en madura_alga.py
(E: su mundo; X: con el alga que alimenta invertida), sin nacimientos ni metabolismo; solo mata el cobro del veneno.
Variantes (una por proceso; DELTA_ON se lee al trazar):
  --delta 1            crianza plástica con δ real
  --delta 0            crianza plástica sin δ (m propia)
  --frozen             crianza sin plasticidad (el cerebro de recién nacido: lo innato)
--load-delta es el DELTA_ON con el que se guardó el mundo (2 en Cbar: su búfer es [N, 64]); al criar se ajusta el búfer.
Regla (fijada antes de ver datos, 27-10, 18:30): «la supervivencia es aprendizaje guiado por δ» si X/E con δ real supera a
X/E sin δ en ≥ 9/10 semillas con mediana de la diferencia ≥ 0,10, y la crianza congelada no supera a la de δ real en ninguna.
Uso: python crianza_c.py <run> --seeds 0 --variant nombre --config K=V ... [--delta D | --frozen] --jsonl salida.jsonl
"""
import argparse, json
from pathlib import Path
import jax, jax.numpy as jnp, numpy as np
from panspermia import config as C, island, world
import madura_alga as M


def _rear(s, steps, plastic):
    def body(c, _):
        c2, _ = island.world_step(c, plastic=plastic, births=False)
        return c2, None
    return jax.lax.scan(body, s, None, length=steps)[0]


def rear(s, steps, flip, plastic):
    orig = world.good_alga_a
    if flip:
        world.good_alga_a = lambda env, uid: ~orig(env, uid)
    try:
        return _rear(s, steps, plastic)
    finally:
        world.good_alga_a = orig


if __name__ == "__main__":
    pa = argparse.ArgumentParser()
    pa.add_argument("run", type=Path)
    pa.add_argument("--seeds", type=int, nargs="+", default=list(range(10)))
    pa.add_argument("--epoch", type=int, default=300)
    pa.add_argument("--rear", type=int, default=200)
    pa.add_argument("--config", nargs="*", default=[])
    pa.add_argument("--load-delta", type=int, required=True)
    pa.add_argument("--delta", type=int, default=0)
    pa.add_argument("--frozen", action="store_true")
    pa.add_argument("--variant", required=True)
    pa.add_argument("--jsonl", type=Path, required=True)
    a = pa.parse_args()
    island.setup_determinism()
    for kv in a.config:
        k, v = kv.split("=")
        cur = getattr(C, k)
        setattr(C, k, float(v) if cur is None else type(cur)(float(v)))
    assert C.ALGA_PER_AGENT
    for seed in a.seeds:
        C.DELTA_ON = a.load_delta
        s = M.load(a.run, seed, a.epoch)
        C.DELTA_ON = a.delta
        nb = 64 if a.delta == 2 else 1
        s = s.replace(dbuf=jnp.zeros((s.dbuf.shape[0], nb), jnp.float32), rbar=jnp.zeros_like(s.rbar), dacc=jnp.zeros_like(s.dacc))
        newborn = M.with_brain(s, s.pheno.w0.astype(jnp.float32))
        rear_j = jax.jit(rear, static_argnums=(1, 2, 3))
        n0 = float(np.asarray(newborn.alive).sum())
        viv = {k: float(np.asarray(rear_j(newborn, a.rear, flip, not a.frozen).alive).sum()) / n0
               for k, flip in (("E", False), ("X", True))}
        row = {"run": a.run.name, "seed": seed, "variant": a.variant, "delta": a.delta, "frozen": a.frozen,
               "rear": a.rear, "n": n0, "vivos": viv, "X_E": viv["X"] / viv["E"] if viv["E"] else None}
        print(json.dumps(row), flush=True)
        with a.jsonl.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row) + "\n")
