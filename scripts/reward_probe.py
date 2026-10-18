"""Sonda de recompensa (solo observa; diseño 1d v0.6): ¿ha inventado la evolución una señal de
premio o castigo en las neuronas moduladoras?

Restaura un checkpoint y corre `--steps` pasos normales (con plasticidad y nacimientos) grabando,
por agente y paso, la modulación m (`brain.modulation`, la misma que usa la plasticidad), el alga
ingerida, la parte tóxica y el tipo de alga del bocado (A o B). Nada de esto vuelve a la dinámica.

Bocado = paso con alga ingerida > EPS. Tóxico si la parte tóxica supera la mitad; bueno si es 0.
Primaria: solo bocados que abren una comida (sin bocado en los PRE = 8 pasos previos). Respuesta en
el desfase L (1–8 pasos): m(t+L) descontada linealmente de m(t) (ANCOVA), mientras siga vivo el
mismo agente (uid); así la vuelta a la media de un m(t) alto no pasa por respuesta. Tamaño del
efecto: d_L = (media | tóxico − media | bueno) / desviación. También se da con todos los bocados.

Control de percepción: como las dos algas se ven distintas, se calcula también d_L **dentro de cada
tipo de alga** (bocados de A tóxica frente a A buena, ídem B) y se combina ponderando por el número
de bocados. Si m solo respondiera a lo que ve, ese d «dentro del tipo» sería ≈ 0.

Nulo: se barajan las etiquetas tóxico/bueno entre los bocados de cada (agente, tipo de alga) y se
toma max_L |d_L| en cada permutación (corrige por los 8 desfases).

Uso: python scripts/reward_probe.py runs/fase1d/E1-aleatorio-T560/s0 --epoch 300 [--steps 1000]
     [--jsonl runs/fase1d/reward_probe.jsonl]
"""
from __future__ import annotations

import argparse
import json
import shutil
import tempfile
import time
from pathlib import Path

import jax
import jax.numpy as jnp
import numpy as np
import orbax.checkpoint as ocp

from panspermia import brain, island, world
from panspermia import config as C

EPS = 1e-3
LAGS = range(1, 9)
N_PERM = 200
PRE = 8  # pasos sin bocado previos que definen el inicio de una comida


def restore(run: Path, epoch: int):
    spec = json.loads((run / "run.json").read_text())
    for k, v in spec.get("experiment", {}).get("config", {}).items():  # p. ej. TOXIC_FACTOR = 0.3
        setattr(C, k, tuple(v) if isinstance(v, list) else v)
    template = island.init_island(spec["seed"], bytes.fromhex(spec["node_id"]), n_max=spec["n_max"],
                                  n_init=spec["n_init"], env_overrides=spec.get("env_overrides"))
    with tempfile.TemporaryDirectory() as tmp:  # copia: no tocar la carpeta de una ejecución viva
        shutil.copytree(run / "checkpoints" / str(epoch), Path(tmp) / str(epoch))
        abstract = jax.tree.map(ocp.utils.to_shape_dtype_struct, template)
        state = ocp.CheckpointManager(Path(tmp)).restore(epoch, args=ocp.args.StandardRestore(abstract))
    return spec, state


@jax.jit
def _record_step(s: island.IslandState, _):
    uid0, tox0, food0 = s.lineage.uid, s.behavior.toxic_intake, s.behavior.intake
    type_a = world.algae_type_a(s.env, s.step)
    s2, _ = island.world_step(s)
    m = brain.modulation(s2.h, s2.genome.hid_mask, s2.genome.hid_type)
    same = s.alive & s2.alive & (s2.lineage.uid == uid0)
    bite_a = type_a.ravel()[world._res_index(s2.pos)]
    return s2, (jnp.where(s2.alive, s2.lineage.uid, 0), m, s2.behavior.intake - food0,
                s2.behavior.toxic_intake - tox0, bite_a, same)


def record(state, steps: int):
    out = []
    for _ in range(steps):  # paso a paso: la grabación [pasos, N] cabe en memoria del host
        state, rec = _record_step(state, None)
        out.append(jax.device_get(rec))
    return [np.stack(x) for x in zip(*out, strict=True)]


def _d(r, lab):
    """Diferencia de medias tóxico − bueno estandarizada (r: respuestas, lab: True = tóxico)."""
    if lab.sum() < 10 or (~lab).sum() < 10:
        return np.nan
    sd = r.std()
    return (r[lab].mean() - r[~lab].mean()) / sd if sd > 0 else np.nan


def _shuffle_within(groups, lab, rng):
    """Baraja `lab` dentro de cada grupo (mismo agente y tipo de alga)."""
    order = np.lexsort((rng.random(len(lab)), groups))
    out = lab.copy()
    sorted_groups = groups[order]
    starts = np.flatnonzero(np.r_[True, sorted_groups[1:] != sorted_groups[:-1]])
    perm = np.empty_like(order)
    for a, b in zip(starts, np.r_[starts[1:], len(order)], strict=True):
        perm[a:b] = order[a:b][rng.permutation(b - a)]
    out[order] = lab[perm]
    return out


def _resid(y, x):
    """Residuo de la regresión lineal de y sobre x (ANCOVA: descuenta m en el bocado)."""
    if len(y) < 3 or x.std() == 0:
        return y - y.mean()
    b, a = np.polyfit(x, y, 1)
    return y - (a + b * x)


def analyze(rec, seed: int = 0, onset: bool = True) -> dict:
    """`onset`: solo bocados que abren una comida (sin bocado del mismo agente en los PRE pasos
    anteriores), para que m(t) no arrastre la respuesta a bocados previos."""
    uid, m, food, tox, bite_a, same = rec
    steps = m.shape[0]
    bite = (food > EPS) & same
    toxic = bite & (tox > 0.5 * food)
    good = bite & (tox <= 0)
    t_idx, a_idx = np.nonzero(toxic | good)
    keep = (t_idx >= PRE) & (t_idx + max(LAGS) < steps)
    t_idx, a_idx = t_idx[keep], a_idx[keep]
    agent = uid[t_idx, a_idx].astype(np.int64)
    ok = np.ones(len(t_idx), bool)
    if onset:
        for back in range(1, PRE + 1):
            prev_same = uid[t_idx - back, a_idx] == agent
            ok &= ~(prev_same & bite[t_idx - back, a_idx])
    resp = []
    for lag in LAGS:  # solo mientras sigue vivo el mismo agente
        ok &= same[t_idx + lag, a_idx] & (uid[t_idx + lag, a_idx] == agent)
        resp.append(m[t_idx + lag, a_idx])
    t_idx, a_idx, agent = t_idx[ok], a_idx[ok], agent[ok]
    m0 = m[t_idx, a_idx]
    lab = toxic[t_idx, a_idx]
    kind = bite_a[t_idx, a_idx]
    groups = agent * 2 + kind
    resp = np.stack(resp)[:, ok]
    # respuesta = m(t+L) descontada linealmente de m(t), por separado en cada tipo de alga
    res = np.empty_like(resp)
    for k in (True, False):
        sel = kind == k
        for i in range(len(resp)):
            res[i, sel] = _resid(resp[i, sel], m0[sel])

    def stats(lab_):
        d_type = []
        for r in res:
            parts = [(_d(r[kind == k], lab_[kind == k]), (kind == k).sum()) for k in (True, False)]
            parts = [(x, w) for x, w in parts if not np.isnan(x)]
            d_type.append(sum(x * w for x, w in parts) / sum(w for _, w in parts) if parts else np.nan)
        return np.array(d_type)

    d_type = stats(lab)
    rng = np.random.default_rng(seed)  # solo el análisis (fuera del núcleo de la simulación)
    null = [np.nanmax(np.abs(stats(_shuffle_within(groups, lab, rng)))) for _ in range(N_PERM)]
    obs = float(np.nanmax(np.abs(d_type))) if np.isfinite(d_type).any() else float("nan")
    alive = uid[0] > 0
    return {
        "onset": onset,
        "bites_toxic": int(lab.sum()), "bites_good": int((~lab).sum()),
        "d_at_bite": float(_d(m0, lab)),
        "d_within_type": [round(float(x), 4) for x in d_type],
        "max_abs_d": obs,
        "p": float((1 + sum(x >= obs for x in null)) / (1 + N_PERM)),
        "m_sd_within_agent": float(np.nanmean([m[:, i][same[:, i]].std() for i in np.flatnonzero(alive)
                                               if same[:, i].sum() > 10])),
        "m_abs_mean": float(np.abs(m[same]).mean()),
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("run", type=Path)
    p.add_argument("--epoch", type=int, required=True)
    p.add_argument("--steps", type=int, default=1000)
    p.add_argument("--jsonl", type=Path, help="añade una línea JSON con el resultado")
    a = p.parse_args()
    island.setup_determinism()
    spec, state = restore(a.run, a.epoch)
    g = jax.device_get(state.genome)
    alive = np.asarray(jax.device_get(state.alive))
    n_mod = (g.hid_mask & g.hid_type)[alive].sum(axis=1)
    t0 = time.time()
    rec = record(state, a.steps)
    res = analyze(rec, spec["seed"], onset=True)
    res["all_bites"] = analyze(rec, spec["seed"], onset=False)
    res.update({"run": str(a.run), "epoch": a.epoch, "steps": a.steps, "population": int(alive.sum()),
                "frac_with_modulators": float((n_mod > 0).mean()), "modulators_mean": float(n_mod.mean()),
                "seconds": round(time.time() - t0, 1), "backend": jax.default_backend()})
    if a.jsonl:
        with a.jsonl.open("a") as f:
            f.write(json.dumps(res) + "\n")
    print(json.dumps(res, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
