# Ablación de δ en la sonda mixta sobre los genomas de C (panel 09, propuesta de Método; solo observa). Una semilla por proceso.
# Regla (27-10, 21:40, antes de ver datos): el ΔD de C es aprendizaje en vida guiado por δ si, con δ apagado (DELTA_ON=0),
# ΔD < ΔD con δ real en ≥ 9/10 semillas y la mediana con δ apagado es ≤ la mitad de la de δ real (+0,176 → ≤ 0,088).
R=/mnt/d/Development/panspermia/runs/fase1d
S=/mnt/c/Users/<usuario>/AppData/Local/Temp/claude/D--Development-panspermia/ddea0d1c-f251-40d2-8e99-9e07c65f2199/scratchpad
source ~/.venvs/panspermia/bin/activate
BASE="ALGA_PER_AGENT=1 ALGA_PATCH_FAMILIES=1 K_CUT=1.7 EAT_MOVE_FACTOR=0 EAT_MOVE_RAMP_STEPS=100000 K_MEAN_RAMP_STEPS=100000 K_MEAN_RAMP_FROM=2 POISON_FACTOR=2.5 POISON_RAMP_STEPS=100000 POISON_DELAY=0 DELTA_K=8.65 DELTA_TAU=50"
export PYTHONPATH=/mnt/d/Development/panspermia-c/src
cd $S
echo "== sonda C con δ apagado $(date '+%F %H:%M')"
for s in 0 1 2 3 4 5 6 7 8 9; do
  python sonda_mixta.py $R/P5-inmediato-C --seeds $s --steps 1500 --config $BASE DELTA_ON=0 --jsonl $R/_sonda_c_C_sin_delta.jsonl 2>&1 | grep -E "^\{|Traceback|Error" | cut -c1-300
done
touch $R/sonda_ablacion_hecha
echo "== termina $(date '+%F %H:%M')"
