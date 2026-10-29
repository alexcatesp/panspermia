"""H-control (hoja de ruta, ADR-028): control positivo y negativo de las medidas de la trampa del alga invertida.
Solo observa. Sustrato 3.4.0 (escalera-algabicho) o 3.5.0 (escalera-manchas), con ALGA_PER_AGENT=1.

Se crían E y X como en madura_alga.py y después se les impone a mano el aprendizaje que buscamos:
  E+ = E + taxia hacia SU alga: del canal de recurso de cada rayo (con signo según el tipo de alga) al giro
       (k · s · fracción angular del rayo) y al empuje (k · s en los rayos centrales), con s = +1 si su alga es A, −1 si B;
  X− = X con la taxia contraria (−s): hacia el alga que no le alimenta.
Dos dosis, fijadas antes de la ejecución completa: k = 4 (fuerte) y k/4 = 1 (débil); k = 4 se fijó tras una prueba de 60 pasos con k = 1 que dio señales débiles y mezcladas (frac_buena +0,053, sel_entrada −0,047 en s0). Examen barajado y congelado, igual que la primaria de las manchas.
Control negativo: los cerebros E+ y X− se reparten al azar entre dos grupos, bicho a bicho (moneda con clave fija).

Regla (fijada antes de ver datos, 25-10):
  positivo: frac_buena(E+) − frac_buena(X−) ≥ 0,05 y sel_entrada(E+) − sel_entrada(X−) ≥ 0,05, cada una en ≥ 9/10;
  negativo: |diferencia| < 0,05 en las dos medidas en ≥ 9/10 con los cerebros barajados;
  la dosis débil y el ruido de la segunda baraja (E+ frente a E+ con otra baraja) se informan sin umbral.
Si el positivo falla, las medidas no ven el aprendizaje y la primaria de las manchas queda en suspenso.
Uso: python madura_control.py <run> --seeds 0 1 ... --config K=V ... --jsonl salida.jsonl
"""
import argparse, json
from pathlib import Path
import jax, jax.numpy as jnp, numpy as np
from panspermia import config as C, island, world
from madura_alga import load, with_brain, rear, exam, scatter, summary

H = C.N_HIDDEN_MAX
RES = jnp.arange(C.N_RAYS) * C.RAY_CHANNELS + 1           # canal de recurso de cada rayo
FRAC = jnp.linspace(-0.5, 0.5, C.N_RAYS)                  # posición angular del rayo (world._RAY_FRAC)
CENTRAL = (jnp.abs(FRAC) <= 0.2).astype(jnp.float32)
KEYS = ("frac_buena", "sel_entrada", "D_comer", "primer_contacto_buena", "ingesta")


def inject(w, s, k):
    """Suma la taxia hacia el alga propia (k > 0) o hacia la contraria (k < 0) a los pesos obs→acción."""
    sgn = jnp.where(world.good_alga_a(s.env, s.lineage.uid), 1.0, -1.0)[:, None]
    w = w.at[:, RES, H + 1].add(k * sgn * FRAC[None, :])
    return w.at[:, RES, H].add(k * sgn * CENTRAL[None, :])


def shuffle(a, b, seed):
    coin = jax.random.bernoulli(jax.random.PRNGKey(20_000 + seed), 0.5, a.shape[:1])[:, None, None]
    return jnp.where(coin, a, b), jnp.where(coin, b, a)


if __name__ == "__main__":
    pa = argparse.ArgumentParser()
    pa.add_argument("run", type=Path)
    pa.add_argument("--seeds", type=int, nargs="+", default=list(range(10)))
    pa.add_argument("--epoch", type=int, default=300)
    pa.add_argument("--rear", type=int, default=200)
    pa.add_argument("--test", type=int, default=500)
    pa.add_argument("--k", type=float, default=4.0)
    pa.add_argument("--config", nargs="*", default=[])
    pa.add_argument("--jsonl", type=Path, required=True)
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
        newborn = with_brain(s, s.pheno.w0.astype(jnp.float32))
        E, X = rear_j(newborn, a.rear, True), rear_j(newborn, a.rear, True, True)
        brains = {"E": E, "X": X, "E+": inject(E, s, a.k), "X-": inject(X, s, -a.k),
                  "E+d": inject(E, s, a.k / 4), "X-d": inject(X, s, -a.k / 4)}
        brains["mezcla1"], brains["mezcla2"] = shuffle(brains["E+"], brains["X-"], seed)
        s_ex = scatter(s, seed)
        res = {k: summary(exam_j(with_brain(s_ex, w), a.test)) for k, w in brains.items()}
        res["E+2"] = summary(exam_j(with_brain(scatter(s, seed + 777), brains["E+"]), a.test))
        diff = lambda p, q: {m: res[p][m] - res[q][m] for m in KEYS}
        d = {"positivo": diff("E+", "X-"), "debil": diff("E+d", "X-d"), "negativo": diff("mezcla1", "mezcla2"),
             "ruido": diff("E+", "E+2"), "sin_inyectar": diff("E", "X")}
        row = {"run": a.run.name, "seed": seed, "epoch": a.epoch, "rear": a.rear, "test": a.test, "k": a.k,
               "n": int(np.asarray(s.alive).sum()), "dif": d, **res}
        print(json.dumps({"run": a.run.name, "seed": seed,
                          **{g: {m: round(v[m], 3) for m in ("frac_buena", "sel_entrada")} for g, v in d.items()}}),
              flush=True)
        with a.jsonl.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
