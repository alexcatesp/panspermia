"""Deriva de la CPPN sin selección (ADR-019): linajes independientes que solo mutan.

Mide el cambio medio de aristas y nodos ocultos por generación con cada física de la CPPN.
Con una física neutral, la media no debe tener rumbo propio (salvo el efecto de los bordes).
Uso: python scripts/cppn_drift.py [--gens 1000] [--lineages 512] [--physics nest neutral ...]
"""
import argparse
import json

import jax
import jax.numpy as jnp
import numpy as np

from panspermia import config as C
from panspermia import genome as G


def run(physics: str, gens: int, lineages: int, every: int) -> list[dict]:
    C.CPPN_MUTATION, C.MUTATION_RATES = physics, "fijas"
    keys = jax.random.split(jax.random.PRNGKey(0), lineages)
    pop = jax.vmap(G.random_minimal)(keys)
    step = jax.jit(lambda p, k: jax.vmap(G.mutate)(p, jax.random.split(k, lineages)))
    hidden = np.zeros(C.CPPN_NODES, bool)
    hidden[C.CPPN_IN:C.CPPN_NODES - C.CPPN_OUT] = True
    rows, key = [], jax.random.PRNGKey(1)
    for g in range(gens + 1):
        if g % every == 0:
            nm, wm = np.asarray(pop.node_mask), np.asarray(pop.W_mask)
            e = wm.reshape(lineages, -1).sum(1)
            free = G.VALID_EDGE[None] & ~wm & nm[:, :, None] & nm[:, None, :]
            rows.append({"gen": g, "edges": float(e.mean()), "edges_p5": float(np.percentile(e, 5)),
                         "nodes": float((nm & hidden).sum(1).mean()),
                         "frac_sin_hueco": float(np.mean(free.reshape(lineages, -1).sum(1) == 0))})
        key, k = jax.random.split(key)
        pop = step(pop, k)
    return rows


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--gens", type=int, default=1000)
    ap.add_argument("--lineages", type=int, default=512)
    ap.add_argument("--every", type=int, default=100)
    ap.add_argument("--physics", nargs="+", default=["nest", "neutral", "neutral_corregida"])
    a = ap.parse_args()
    out = {p: run(p, a.gens, a.lineages, a.every) for p in a.physics}
    for p, rows in out.items():
        print(p, " ".join(f"{r['gen']}:{r['edges']:.1f}/{r['nodes']:.1f}/{r['frac_sin_hueco']:.2f}" for r in rows), flush=True)
    print(json.dumps(out))
