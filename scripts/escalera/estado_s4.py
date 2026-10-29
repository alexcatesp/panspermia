import glob, pyarrow.parquet as pq
rows = [r for f in sorted(glob.glob("/mnt/d/Development/panspermia/runs/fase1d/P4-alga-tripa-frena-rampa/s4/stats/*.parquet")) for r in pq.read_table(f, columns=["epoch","population","population_min","births","reinjected","hidden_mean","generation_max"]).to_pylist()]
for r in rows:
    if 110 <= r["epoch"] <= 135 or r["epoch"] in (150, 200, 250, 299):
        print(r)
print("reinyecciones totales", sum(r["reinjected"] for r in rows))
