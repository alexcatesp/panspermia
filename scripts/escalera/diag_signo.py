"""Diagnóstico D del panel 07 (ADR-032): ¿lleva la modulación m el signo del resultado? Solo observa. Sustrato 3.6.0.

Sobre el checkpoint de la época 300:
  (a) f_mod: fracción de vivos con >= 1 oculta moduladora expresada (hid_mask & hid_type).
  (b) recorrido de 500 pasos con plasticidad y sin nacimientos (el mundo de siempre); 200 vivos al azar (PRNGKey(30000 + s)).
      Por bicho, Spearman entre m(t + 1) y el resultado en t (bocado − cobro) en los pasos con bocado o cobro.
      Estadístico del mundo: mediana de ρ. Nulo: 1.000 desplazamientos circulares de m dentro de cada bicho (>= 40 pasos;
      default_rng(7000 + s)), mediana por mundo. Señal: mediana > p97,5 del nulo y >= 0,2.
  (c) lo mismo con el indicador «resultado > 0» frente a «< 0» (solo hay negativos con cobro).
  Se informa también solo entre los bichos con moduladora. Bichos con menos de 100 pasos vivos o 10 sucesos: fuera.
Uso: python diag_signo.py <run> --seeds 0 1 ... --config K=V ... --jsonl salida.jsonl [--npz carpeta]
"""
import argparse, json
from pathlib import Path
import jax, jax.numpy as jnp, numpy as np
from scipy.stats import rankdata
from panspermia import config as C, brain, island
from madura_alga import load

T, K_AGENTS, N_NULL, MIN_SHIFT = 500, 200, 1000, 40


def rollout(s, idx):
    def body(c, _):
        c2, _ = island.world_step(c, plastic=True, births=False)
        m = brain.modulation(c2.h, c2.genome.hid_mask, c2.genome.hid_type)[idx]
        bite = c2.gut[idx, c.step % C.GUT_WINDOW]
        due = c.poison[idx, c.step % C.POISON_BUFFER]
        return c2, (m, bite, due, c2.alive[idx])
    _, out = jax.lax.scan(body, s, None, length=T)
    return out


def spearman(x, y):
    if np.ptp(x) == 0 or np.ptp(y) == 0:
        return 0.0
    rx, ry = rankdata(x), rankdata(y)
    return float(np.corrcoef(rx, ry)[0, 1])


def analyse(m, outc, alive, rng, binary):
    """m, outc, alive: [T, K]. Devuelve (mediana real, nulo de medianas, rho por bicho, usados)."""
    agents = []
    for k in range(m.shape[1]):
        L = int(np.argmin(alive[:, k])) if not alive[:, k].all() else T  # pasos vivo desde el principio
        if L < 100:
            continue
        mk, ok = m[:L, k], outc[:L, k]
        ev = np.nonzero(ok[:-1] != 0)[0]
        if len(ev) < 10:
            continue
        y = (ok[ev] > 0).astype(float) if binary else ok[ev]
        if binary and (y.min() == y.max()):
            continue
        agents.append((k, mk, ev, y, L))
    if not agents:
        return None, None, [], []
    real = [spearman(mk[ev + 1], y) for _, mk, ev, y, _ in agents]
    shifts = [rng.integers(MIN_SHIFT, max(L - MIN_SHIFT, MIN_SHIFT + 1), N_NULL) for *_, L in agents]
    null = np.empty(N_NULL)
    for p in range(N_NULL):
        null[p] = np.median([spearman(np.roll(mk, int(sh[p]))[ev + 1], y)
                             for (_, mk, ev, y, _), sh in zip(agents, shifts)])
    return float(np.median(real)), null, real, [a[0] for a in agents]


def verdict(med, null):
    if med is None:
        return {"mediana": None, "p975": None, "senal": False}
    p975 = float(np.percentile(null, 97.5))
    return {"mediana": round(med, 4), "p975": round(p975, 4), "senal": bool(med > p975 and med >= 0.2)}


if __name__ == "__main__":
    pa = argparse.ArgumentParser()
    pa.add_argument("run", type=Path)
    pa.add_argument("--seeds", type=int, nargs="+", default=list(range(10)))
    pa.add_argument("--epoch", type=int, default=300)
    pa.add_argument("--config", nargs="*", default=[])
    pa.add_argument("--jsonl", type=Path, required=True)
    pa.add_argument("--npz", type=Path, default=None)
    a = pa.parse_args()
    island.setup_determinism()
    for kv in a.config:
        k, v = kv.split("=")
        cur = getattr(C, k)
        setattr(C, k, float(v) if cur is None else type(cur)(float(v)))
    roll_j = jax.jit(rollout)
    for seed in a.seeds:
        s = load(a.run, seed, a.epoch)
        alive0 = np.asarray(s.alive)
        has_mod = np.asarray(jnp.any(s.genome.hid_mask & s.genome.hid_type, axis=-1))
        f_mod = float(has_mod[alive0].mean())
        n_mod = np.asarray(jnp.sum(s.genome.hid_mask & s.genome.hid_type, axis=-1))[alive0]
        cand = np.nonzero(alive0)[0]
        pick = np.asarray(jax.random.choice(jax.random.PRNGKey(30_000 + seed), jnp.asarray(cand), (K_AGENTS,), replace=False))
        m, bite, due, alive = (np.asarray(x) for x in roll_j(s, jnp.asarray(pick)))
        outc = bite - due
        if a.npz:
            a.npz.mkdir(parents=True, exist_ok=True)
            np.savez_compressed(a.npz / f"{a.run.name}_s{seed}.npz", m=m, bite=bite, due=due, alive=alive, pick=pick)
        res = {}
        for tag, binary in (("b", False), ("c", True)):
            for sub, mask in (("todos", np.ones(K_AGENTS, bool)), ("con_mod", has_mod[pick])):
                rng = np.random.default_rng(7000 + seed)
                med, null, real, used = analyse(m[:, mask], outc[:, mask], alive[:, mask], rng, binary)
                res[f"{tag}_{sub}"] = {**verdict(med, null), "n": len(used),
                                       "rho_q": [round(float(q), 3) for q in np.percentile(real, [10, 50, 90])] if real else None}
        row = {"run": a.run.name, "seed": seed, "epoch": a.epoch, "n_vivos": int(alive0.sum()), "f_mod": round(f_mod, 4),
               "n_mod_media": round(float(n_mod.mean()), 3), "m_std": round(float(m[alive].std()), 5),
               "sucesos_por_bicho": round(float((outc[:-1] != 0).sum(0).mean()), 1),
               "frac_negativos": round(float((outc < 0).sum() / max((outc != 0).sum(), 1)), 4), **res}
        print(json.dumps(row, ensure_ascii=False), flush=True)
        with a.jsonl.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
