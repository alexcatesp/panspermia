"""P2 completo (diseno v0.6): épocas 151–300, emparejado por semilla."""
import json
from pathlib import Path
R = Path("runs/fase1d")
def rows(c, s):
    rs = json.loads((R / c / f"s{s}" / "stats" / "summary.json").read_text(encoding="utf-8"))
    ep = [r["epoch"] for r in rs]
    assert ep == sorted(set(ep)), (c, s, "épocas repetidas o desordenadas")
    return rs
def late(rs, k, a=151, b=300):
    v = [r[k] for r in rs if a <= r["epoch"] <= b and isinstance(r.get(k), (int, float))]
    return sum(v) / len(v) if v else None
keys = ["lifespan_mean", "thrust_mean", "intake", "hidden_mean", "mass_mean", "va_intake", "va_log_intake",
        "cppn_edges_mean", "cppn_nodes_mean", "births", "deaths_starvation", "deaths_age", "mean_energy", "population", "generation_max",
        "cap_patch_gain", "cap_maze_gain", "cap_patch_success", "cap_patch_baseline_random"]
C = ["P1-escalera", "P2-escalera", "P2-escalera-tasas-gen", "P2-escalera-sexual"]
out = {}
for c in C:
    out[c] = []
    for s in range(5):
        rs = rows(c, s)
        d = {k: late(rs, k) for k in keys}
        d["epochs"] = len(rs); d["ec"] = (d["cppn_edges_mean"] or 0) - (d["cppn_nodes_mean"] or 0)
        d["hidden_e51_100"] = late(rs, "hidden_mean", 51, 100)
        out[c].append(d)
for k in keys + ["ec", "hidden_e51_100", "epochs"]:
    print(f"\n{k}")
    for c in C:
        print(f"  {c:24s}", " ".join("   -    " if x[k] is None else f"{x[k]:8.3f}" for x in out[c]))
def wins(a, b, k, sign=1):
    return sum(1 for x, y in zip(out[a], out[b]) if sign * (x[k] - y[k]) > 0)
print("\nPRIMARIA P2 lifespan > P1:", wins("P2-escalera", "P1-escalera", "lifespan_mean"), "/5")
print("secundaria thrust > P1:", wins("P2-escalera", "P1-escalera", "thrust_mean"), "/5")
print("sexual lifespan > base:", wins("P2-escalera-sexual", "P2-escalera", "lifespan_mean"), "/5",
      "· intake > base:", wins("P2-escalera-sexual", "P2-escalera", "intake"), "/5")
print("tasas-gen lifespan > base:", wins("P2-escalera-tasas-gen", "P2-escalera", "lifespan_mean"), "/5",
      "· intake > base:", wins("P2-escalera-tasas-gen", "P2-escalera", "intake"), "/5")
(R / "_analisis_P2int.json").write_text(json.dumps(out, indent=1))
