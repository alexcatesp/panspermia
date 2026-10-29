"""Diagnóstico de la tripa (diseno v1.5, secundarias; solo observa). Sustrato 3.0.0.

Por mundo y semilla (época 300):
  A. capacidad (como diag_aprender).
  G. peso de la tripa en las moduladoras: fracción de bichos con moduladora cuya sinapsis tripa→moduladora
     está expresada, y |w| tripa→mod frente a la media de |w| de las demás entradas expresadas hacia ellas.
  C2. 200 pasos plásticos sin nacimientos: correlación DENTRO de cada bicho (restando su media) entre la
     modulación m y (a) la tripa en bruto (suma de lo comido en 4 pasos, estado interno, exista o no la
     entrada) y (b) su sorpresa: tripa menos su media exponencial reciente (alfa 0,1) del propio bicho.
Uso: python diag_tripa.py <run> --config K=V ... --jsonl salida.jsonl
"""
import argparse, json
from pathlib import Path
import jax, jax.numpy as jnp, numpy as np
from panspermia import brain, config as C, island
import diag_aprender as D

GUT_IDX = C.OBS_DIM - 1


def gut_weight(s):
    a = np.asarray(s.alive)
    mod = (np.asarray(s.genome.hid_mask) & np.asarray(s.genome.hid_type))[a]       # [n, H]
    has = mod.any(1)
    w = np.abs(np.asarray(s.w, np.float32))[a][:, :C.OBS_DIM, :C.N_HIDDEN_MAX]       # [n, obs, H]
    mk = np.asarray(s.pheno.mask)[a][:, :C.OBS_DIM, :C.N_HIDDEN_MAX]
    g_on, ratio = [], []
    for i in np.flatnonzero(has):
        cols = np.flatnonzero(mod[i])
        g_on.append(mk[i, GUT_IDX, cols].any())
        other = w[i, :GUT_IDX, :][:, cols][mk[i, :GUT_IDX, :][:, cols]]
        if other.size and other.mean() > 0:
            ratio.append(w[i, GUT_IDX, cols].mean() / other.mean())
    return {"frac_gut_to_mod": float(np.mean(g_on)) if g_on else None,
            "gut_w_ratio_median": float(np.median(ratio)) if ratio else None}


def bite_gut(s, T=200, alpha=0.1):
    def body(c, _):
        c2, _ = island.world_step(c, births=False)
        m = brain.modulation(c2.h, c2.genome.hid_mask, c2.genome.hid_type)
        return c2, (c2.alive, jnp.sum(c2.gut, axis=-1), m)
    _, (alive, gut, m) = jax.jit(lambda st: jax.lax.scan(body, st, None, length=T))(s)
    alive, gut, m = np.asarray(alive), np.asarray(gut, np.float64), np.asarray(m, np.float64)
    has_mod = (np.asarray(s.genome.hid_mask) & np.asarray(s.genome.hid_type)).any(1)
    keep = alive.all(0) & has_mod                         # vivos los 200 pasos y con moduladora
    ema = np.zeros_like(gut)
    for t in range(1, T):
        ema[t] = (1 - alpha) * ema[t - 1] + alpha * gut[t - 1]
    surprise = gut - ema
    def within(x, y):
        x, y = x[:, keep], y[:, keep]
        x, y = x - x.mean(0), y - y.mean(0)
        den = np.sqrt((x ** 2).sum() * (y ** 2).sum())
        return float((x * y).sum() / den) if den > 0 else None
    return {"n_keep": int(keep.sum()), "corr_m_gut": within(m, gut), "corr_m_surprise": within(m, surprise),
            "frac_steps_gut_pos": float((gut[:, keep] > 0).mean()), "frac_steps_gut_neg": float((gut[:, keep] < 0).mean())}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("run", type=Path)
    p.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2, 3, 4])
    p.add_argument("--epoch", type=int, default=300)
    p.add_argument("--config", nargs="*", default=[])
    p.add_argument("--jsonl", type=Path, required=True)
    a = p.parse_args()
    island.setup_determinism()
    for kv in a.config:
        k, v = kv.split("=")
        setattr(C, k, type(getattr(C, k))(float(v)))
    for seed in a.seeds:
        s = D.load(a.run, seed, a.epoch)
        row = {"run": a.run.name, "seed": seed, "epoch": a.epoch}
        row.update(D.capacity(s)); row.update(gut_weight(s)); row.update(bite_gut(s))
        print(json.dumps({k: round(v, 4) if isinstance(v, float) else v for k, v in row.items()}), flush=True)
        with a.jsonl.open("a") as f:
            f.write(json.dumps(row) + "\n")
