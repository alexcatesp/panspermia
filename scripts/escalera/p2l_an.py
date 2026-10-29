"""P2 hasta 600 épocas: base y sexual, ventanas de 150 épocas."""
import json
from pathlib import Path
R = Path("runs/fase1d")
W = [(51, 150), (151, 300), (301, 450), (451, 600)]
keys = ["lifespan_mean", "intake", "thrust_mean", "hidden_mean", "cppn_nodes_mean", "mass_mean", "va_intake",
        "deaths_starvation", "deaths_age", "births", "mean_energy", "cap_patch_gain", "cap_maze_gain", "cap_patch_success", "genome_distance_struct", "clades_alive"]
out = {}
for c in ("P2-escalera-600", "P2-escalera-sexual-600"):
    out[c] = []
    for s in range(5):
        d = R / c / f"s{s}"
        rs = json.loads((d / "stats" / "summary.json").read_text(encoding="utf-8"))
        ep = [r["epoch"] for r in rs]; assert ep == list(range(1, 601)), (c, s, len(ep), ep[-1])
        res = json.loads((d / "result.json").read_text(encoding="utf-8"))
        row = {"paused": res.get("paused"), "extinct": res.get("extinct_at")}
        for k in keys:
            for a, b in W:
                v = [r[k] for r in rs if a <= r["epoch"] <= b and isinstance(r.get(k), (int, float))]
                row[f"{k}@{a}-{b}"] = sum(v) / len(v) if v else None
        row["hidden@600"] = rs[-1]["hidden_mean"]
        out[c].append(row)
for c, rows in out.items():
    print("==", c, [ (r["paused"], r["extinct"]) for r in rows])
    for k in keys:
        print(f"  {k:22s}", " | ".join(" ".join("   -   " if r[f"{k}@{a}-{b}"] is None else f"{r[f'{k}@{a}-{b}']:7.2f}" for r in rows) for a, b in W))
    print("  hidden@600", [round(r["hidden@600"], 2) for r in rows])
b, x = out["P2-escalera-600"], out["P2-escalera-sexual-600"]
for k in ("lifespan_mean", "intake", "deaths_starvation"):
    for a, bb in W:
        kk = f"{k}@{a}-{bb}"
        print(k, a, bb, "sexual > base:", sum(1 for p, q in zip(x, b) if p[kk] > q[kk]), "/5")
(R / "_analisis_P2largo.json").write_text(json.dumps(out, indent=1))
