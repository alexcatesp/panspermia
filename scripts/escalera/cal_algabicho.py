import glob, pyarrow.parquet as pq
for seed in (0, 1, 2):
    rows = [r for f in sorted(glob.glob(f"/mnt/d/Development/panspermia/runs/fase1d/_calAlgaBicho/s{seed}/stats/*.parquet"))
            for r in pq.read_table(f, columns=["epoch", "population", "population_min", "births", "mean_energy", "intake", "hidden_mean"]).to_pylist()]
    late = [r for r in rows if r["epoch"] >= 100]
    full = sum(r["population_min"] >= 4000 for r in late)
    print(seed, "épocas 100-149: pob mín", min(r["population_min"] for r in late), "· épocas con mín ≥ 4000:", full, "de", len(late),
          "· energía media", round(sum(r["mean_energy"] for r in late) / len(late), 1),
          "· ocultas", round(late[-1]["hidden_mean"], 2))
    for r in rows:
        if r["epoch"] in (20, 50, 80, 100, 120, 149):
            print("   ", r["epoch"], r["population"], r["population_min"], r["births"], round(r["mean_energy"], 1))
