"""P3-disperso (diseno v1.0) frente a P3-escaso."""
import json
from pathlib import Path
R = Path("runs/fase1d")
def rows(c, s):
    rs = json.loads((R / c / f"s{s}" / "stats" / "summary.json").read_text(encoding="utf-8"))
    return rs
def late(rs, k, a=151, b=300):
    v = [r[k] for r in rs if a <= r["epoch"] <= b and isinstance(r.get(k), (int, float))]
    return sum(v) / len(v) if v else None
def mn(rs, k, a=151, b=300):
    v = [r[k] for r in rs if a <= r["epoch"] <= b and isinstance(r.get(k), (int, float))]
    return min(v) if v else None
keys = ["population", "lifespan_mean", "thrust_mean", "intake", "hidden_mean", "va_intake", "va_log_intake",
        "births", "deaths_starvation", "deaths_age", "mean_energy", "generation_max",
        "cap_patch_success", "cap_patch_gain", "cap_maze_gain", "cap_patch_baseline_random", "cap_patch_baseline_controls", "mass_mean", "resources_total"]
C = ["P3-escaso", "P3-disperso"]
out = {}
for c in C:
    out[c] = []
    for s in range(5):
        rs = rows(c, s)
        d = {k: late(rs, k) for k in keys}
        d["pop_min"] = mn(rs, "population"); d["epochs"] = len(rs)
        d["pop_e1_50"] = late(rs, "population", 1, 50)
        out[c].append(d)
for k in keys + ["pop_min", "pop_e1_50", "epochs"]:
    print(f"\n{k}")
    for c in C:
        print(f"  {c:14s}", " ".join("   -    " if x[k] is None else f"{x[k]:9.3f}" for x in out[c]))
print("\nPRIMARIA pop < 4096:", sum(1 for x in out["P3-escaso"] if x["population"] < 4096), "/5")
print("claves r0:", sorted(rows("P3-disperso", 0)[-1].keys()))
(R / "_analisis_P3disperso.json").write_text(json.dumps(out, indent=1))
