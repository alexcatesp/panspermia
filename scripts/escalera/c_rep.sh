# Réplica de C (panel 09, ADR-034). Espera a la ablación de δ en la sonda; solo sigue si confirma (regla fijada a las 21:40).
# Después: determinismo (C s0, 100 épocas, contra el checkpoint 100 original), 10 mundos nuevos (semillas 10–19) y sonda mixta.
R=/mnt/d/Development/panspermia/runs/fase1d
S=/mnt/c/Users/<usuario>/AppData/Local/Temp/claude/D--Development-panspermia/ddea0d1c-f251-40d2-8e99-9e07c65f2199/scratchpad
source ~/.venvs/panspermia/bin/activate
export PYTHONPATH=/mnt/d/Development/panspermia-c/src
cd /mnt/d/Development/panspermia-c
echo "== espera a la ablación $(date '+%F %H:%M')"
until [ -f $R/sonda_ablacion_hecha ]; do sleep 30; done
python - <<PY || { echo "== la ablación no confirma: no se lanza la réplica $(date '+%F %H:%M')"; touch $R/c_rep_no; exit 0; }
import json, statistics as st, sys
d = lambda r: r["plastico"]["D"] - r["congelado"]["D"]
real = {r["seed"]: d(r) for r in map(json.loads, open("$R/_sonda_c_C.jsonl")) if not r.get("null")}
off = {r["seed"]: d(r) for r in map(json.loads, open("$R/_sonda_c_C_sin_delta.jsonl")) if not r.get("null")}
below = sum(off[s] < real[s] for s in off); med = st.median(off.values())
print("ablación: ΔD sin δ", [round(off[s], 3) for s in sorted(off)], "mediana", round(med, 3), "por debajo de δ real", below, "/", len(off))
sys.exit(0 if len(off) == 10 and below >= 9 and med <= 0.088 else 1)
PY
echo "== la ablación confirma $(date '+%F %H:%M')"
python - <<PY
import json; q = json.load(open("experiments/fase1d/c_rep.json"))[0]
q.update(name="P5-inmediato-C-det", seeds=[0], epochs=100, description="Determinismo antes de la réplica (panel 09)")
json.dump([q], open("$S/c_det.json", "w"), indent=1, ensure_ascii=False)
PY
echo "== determinismo $(date '+%F %H:%M')"
python -m panspermia.experiment sweep $S/c_det.json --out $R >> $R/c_rep_mundos.log 2>&1
python - <<PY || { echo "== determinismo FALLA: se para $(date '+%F %H:%M')"; exit 1; }
import shutil, tempfile, sys, jax, numpy as np
from pathlib import Path
import orbax.checkpoint as ocp
from panspermia import config as C, island
island.setup_determinism()
def load(run):
    t = island.init_island(0, b"fase1d-w0", n_max=C.N_MAX, n_init=C.N_INIT)
    with tempfile.TemporaryDirectory() as tmp:
        shutil.copytree(Path(run) / "s0/checkpoints/100", Path(tmp) / "100")
        return ocp.CheckpointManager(Path(tmp)).restore(100, args=ocp.args.StandardRestore(jax.tree.map(ocp.utils.to_shape_dtype_struct, t)))
a, b = load("$R/P5-inmediato-C"), load("$R/P5-inmediato-C-det")
la, lb = jax.tree.leaves(a), jax.tree.leaves(b)
bad = sum(not np.array_equal(np.asarray(x), np.asarray(y)) for x, y in zip(la, lb))
print("hojas distintas:", bad, "de", len(la)); sys.exit(1 if bad else 0)
PY
echo "== determinismo bit a bit correcto; 10 mundos nuevos $(date '+%F %H:%M')"
python -m panspermia.experiment sweep experiments/fase1d/c_rep.json --out $R >> $R/c_rep_mundos.log 2>&1 && touch $R/c_rep_hecho
BASE="ALGA_PER_AGENT=1 ALGA_PATCH_FAMILIES=1 K_CUT=1.7 EAT_MOVE_FACTOR=0 EAT_MOVE_RAMP_STEPS=100000 K_MEAN_RAMP_STEPS=100000 K_MEAN_RAMP_FROM=2 POISON_FACTOR=2.5 POISON_RAMP_STEPS=100000 POISON_DELAY=0 DELTA_K=8.65 DELTA_TAU=50"
cd $S
echo "== sonda mixta $(date '+%F %H:%M')"
for s in 10 11 12 13 14 15 16 17 18 19; do
  python sonda_mixta.py $R/P5-inmediato-C --seeds $s --steps 1500 --config $BASE DELTA_ON=1 --jsonl $R/_sonda_c_rep.jsonl 2>&1 | grep -E "^\{|Traceback|Error" | cut -c1-300
done
echo "== nulo $(date '+%F %H:%M')"
for s in 10 11 12; do
  python sonda_mixta.py $R/P5-inmediato-C --seeds $s --steps 1500 --null --config $BASE DELTA_ON=1 --jsonl $R/_sonda_c_rep_nulo.jsonl 2>&1 | grep -E "^\{|Traceback|Error" | cut -c1-300
done
touch $R/c_rep_medidas_hechas
echo "== termina $(date '+%F %H:%M')"
