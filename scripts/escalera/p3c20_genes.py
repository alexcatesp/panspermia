"""P3: genes de reproducción (umbral, fracción al hijo) en los vivos. Solo observa."""
import json, shutil, tempfile
from pathlib import Path
import jax, jax.numpy as jnp, numpy as np
import orbax.checkpoint as ocp
from panspermia import island
from panspermia import config as C
island.setup_determinism()
R = Path("/mnt/d/Development/panspermia/runs/fase1d")
res = {}
for s in range(5):
    d = R / "P3-coste20" / f"s{s}" / "checkpoints"
    for ep in sorted(int(p.name) for p in d.iterdir() if p.name.isdigit()):
        if ep not in (100, 200, 300): continue
        template = island.init_island(s, b"fase1d-w0", n_max=C.N_MAX, n_init=C.N_INIT)
        with tempfile.TemporaryDirectory() as tmp:
            shutil.copytree(d / str(ep), Path(tmp) / str(ep))
            st = ocp.CheckpointManager(Path(tmp)).restore(ep, args=ocp.args.StandardRestore(jax.tree.map(ocp.utils.to_shape_dtype_struct, template)))
        a = np.asarray(st.alive); th = np.asarray(st.pheno.repro_threshold)[a]; fr = np.asarray(st.pheno.offspring_frac)[a]
        e = np.asarray(st.energy)[a]
        row = dict(seed=s, epoch=ep, n=int(a.sum()), thr_mean=float(th.mean()), thr_p10=float(np.percentile(th, 10)), thr_p90=float(np.percentile(th, 90)),
                   frac_mean=float(fr.mean()), frac_p10=float(np.percentile(fr, 10)), frac_p90=float(np.percentile(fr, 90)),
                   energy_mean=float(e.mean()), above_thr=float((e >= th).mean()))
        print(json.dumps({k: round(v, 3) if isinstance(v, float) else v for k, v in row.items()}), flush=True)
        res[f"{s}/{ep}"] = row
(R / "_genes_P3coste20.json").write_text(json.dumps(res, indent=1))
