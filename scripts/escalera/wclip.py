"""Prueba del tope de w0 (auditoría 15-11, H2/recomendación 1a; solo observa). Reglas fijadas ANTES de ver datos.

Pregunta: ¿la «ventaja de aprender»/D de C depende de pesos adultos fuera de ±W_INIT_SCALE (=1), que el genoma
no puede escribir al nacer? Se restaura un checkpoint, se recorta a ±CLIP el vector w de los bichos de uid impar
(grupo «congelado» de sonda_mixta) y se deja a los pares intactos; **las dos mitades van congeladas** (NULL=True),
en el mismo mundo. Cuentan todos los vivos desde el paso 0 (step0=0). Compara por grupo la ingesta por paso y
D = P(comer | alga buena) − P(comer | alga vacía).
  - Si el recorte no cambia nada, o solo en los bichos con w fuera de ±1, hay que mirar `frac_fuera` por bicho.
  - Regla: el tope explica la maduración si, con CLIP=1, D_recortado ≤ 0,5·D_intacto y la ingesta cae ≥ 20 %
    en ≥ 8/10 semillas. Control negativo: --clip 4 (no recorta nada; los dos grupos deben coincidir).
Uso: python wclip.py <run> --seeds 0 1 --clip 1 --config K=V ... --jsonl salida.jsonl
"""
import argparse, json
from pathlib import Path
import jax.numpy as jnp, numpy as np
from panspermia import config as C, island
import sonda_mixta as S

if __name__ == "__main__":
    pa = argparse.ArgumentParser()
    pa.add_argument("run", type=Path)
    pa.add_argument("--seeds", type=int, nargs="+", default=list(range(10)))
    pa.add_argument("--epoch", type=int, default=300)
    pa.add_argument("--steps", type=int, default=1500)
    pa.add_argument("--clip", type=float, default=1.0)
    pa.add_argument("--config", nargs="*", default=[])
    pa.add_argument("--jsonl", type=Path, required=True)
    a = pa.parse_args()
    S.NULL = True
    island.setup_determinism()
    for kv in a.config:
        k, v = kv.split("=")
        cur = getattr(C, k)
        setattr(C, k, float(v) if cur is None else type(cur)(float(v)))
    for seed in a.seeds:
        s = S.load(a.run, seed, a.epoch)
        odd = np.asarray(S.frozen_of(s.lineage.uid)) & np.asarray(s.alive)
        w = np.asarray(s.w)
        fuera = (np.abs(w) > a.clip + 1e-6) & np.asarray(s.pheno.mask)
        frac_fuera = float(fuera.reshape(len(w), -1).any(1)[np.asarray(s.alive)].mean())
        s = s.replace(w=jnp.where(S.frozen_of(s.lineage.uid)[:, None, None], jnp.clip(s.w, -a.clip, a.clip), s.w))
        row = {"run": a.run.name, "seed": seed, "epoch": a.epoch, "steps": a.steps, "clip": a.clip,
               "frac_bichos_con_w_fuera": round(frac_fuera, 4), "n_recortados": int(odd.sum())}
        row.update(S.probe(s, a.steps, step0=0))
        i, r = row["plastico"], row["congelado"]   # «plastico» = intactos (pares); «congelado» = recortados (impares)
        print(json.dumps({"seed": seed, "fuera": row["frac_bichos_con_w_fuera"],
                          "ingesta_intacto_recortado": [round(i["ingesta_por_paso"], 4), round(r["ingesta_por_paso"], 4)],
                          **({"D_intacto_recortado": [round(i["D"], 3), round(r["D"], 3)]} if "D" in i else {})}), flush=True)
        with a.jsonl.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
