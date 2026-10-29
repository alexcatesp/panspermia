import json
from pathlib import Path
R = Path("/mnt/d/Development/panspermia/runs/fase1d")
rows = {}
for l in (R / "_diag_comer_frena.jsonl").open():
    r = json.loads(l)
    rows[(r["run"], r["seed"])] = r
for run in ("P4-alga-tripa-frena-rampa", "P4-alga-tripa", "P4-alga-sin-tripa-frena-rampa"):
    print("==", run)
    clear = 0
    for s in range(10):
        r = rows.get((run, s))
        if not r:
            continue
        d = r["p_eat_good"] - r["p_eat_nofood"]
        clear += d >= 0.1
        print(f"  s{s}: come {r['frac_eat']:.2f}  buena {r['p_eat_good']:.2f}  nada {r['p_eat_nofood']:.2f}  vacía {r['p_eat_bad']:.2f}  buena−nada {d:+.2f}")
    fe = sorted(rows[(run, s)]["frac_eat"] for s in range(10) if (run, s) in rows)
    print(f"  come {fe[0]:.2f}–{fe[-1]:.2f}; buena − nada ≥ 0,10 en {clear}/10")
