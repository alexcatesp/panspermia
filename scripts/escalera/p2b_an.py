"""P2-buscar (diseno v0.8): examen limpio en la época 300 frente a P2; secundarias 151–300."""
import json
from pathlib import Path
R = Path("runs/fase1d")
P2_300 = [0.000, 0.031, 0.109, 0.016, 0.109]  # examen limpio de P2 en la época 300 (ADR-021)
def rows(c, s): return json.loads((R / c / f"s{s}" / "stats" / "summary.json").read_text(encoding="utf-8"))
def late(rs, k, a=151, b=300):
    v = [r[k] for r in rs if a <= r["epoch"] <= b and isinstance(r.get(k), (int, float))]
    return sum(v) / len(v) if v else None
keys = ["population", "population_min", "lifespan_mean", "thrust_mean", "intake", "hidden_mean", "va_intake", "births",
        "deaths_starvation", "deaths_age", "mean_energy", "resources_total", "mass_mean", "generation_max",
        "cap_patch_success", "cap_patch_gain", "cap_patch_baseline_random", "cap_patch_baseline_controls", "cap_maze_gain", "cap_maze_success"]
out = {"P2-escalera": [], "P2-buscar": []}
for c in out:
    for s in range(5):
        rs = rows(c, s); d = {k: late(rs, k) for k in keys}
        if c == "P2-buscar":
            ex = [r for r in rs if isinstance(r.get("cap_patch_success"), (int, float))]
            last = ex[-1]
            d["exam_epoch"] = last["epoch"]; d["exam300"] = last["cap_patch_success"]
            d["exam300_gain"] = last["cap_patch_gain"]; d["exam300_ctrl"] = last["cap_patch_baseline_controls"]
            d["exam300_rand"] = last["cap_patch_baseline_random"]; d["exam300_maze"] = last["cap_maze_success"]
            d["exam_series"] = [(r["epoch"], round(r["cap_patch_success"], 3), round(r["cap_patch_gain"], 3)) for r in ex[-8:]]
            d["hidden_300"] = rs[-1]["hidden_mean"]; d["pop_e1_50"] = late(rs, "population_min", 1, 50)
        out[c].append(d)
for k in keys:
    print(f"{k:28s}", " | ".join(" ".join("   -   " if x[k] is None else f"{x[k]:8.3f}" for x in out[c]) for c in out))
for s, d in enumerate(out["P2-buscar"]):
    print(s, "examen ep", d["exam_epoch"], "éxito", round(d["exam300"], 3), "vs P2", P2_300[s], "ganancia", round(d["exam300_gain"], 3),
          "ctrl", round(d["exam300_ctrl"], 3), "azar", round(d["exam300_rand"], 3), "laberinto", round(d["exam300_maze"], 3), "hidden300", round(d["hidden_300"], 2),
          "pop1-50", round(d["pop_e1_50"]))
    print("   serie", d["exam_series"])
print("PRIMARIA:", sum(1 for s, d in enumerate(out["P2-buscar"]) if d["exam300"] > P2_300[s]), "/5")
def w(k, sign=1): return sum(1 for a, b in zip(out["P2-buscar"], out["P2-escalera"]) if sign * (a[k] - b[k]) > 0)
print("buscar>P2: vida", w("lifespan_mean"), "empuje", w("thrust_mean"), "hidden", w("hidden_mean"), "intake", w("intake"))
(R / "_analisis_P2buscar.json").write_text(json.dumps(out, indent=1))
