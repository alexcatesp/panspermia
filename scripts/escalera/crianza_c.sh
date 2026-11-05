# Diagnóstico de la crianza invertida en C (crianza_c.py; solo observa). Una semilla por proceso.
R=/mnt/d/Development/panspermia/runs/fase1d
S=/mnt/c/Users/<usuario>/AppData/Local/Temp/claude/D--Development-panspermia/ddea0d1c-f251-40d2-8e99-9e07c65f2199/scratchpad
source ~/.venvs/panspermia/bin/activate
BASE="ALGA_PER_AGENT=1 ALGA_PATCH_FAMILIES=1 K_CUT=1.7 EAT_MOVE_FACTOR=0 EAT_MOVE_RAMP_STEPS=100000 K_MEAN_RAMP_STEPS=100000 K_MEAN_RAMP_FROM=2 POISON_FACTOR=2.5 POISON_RAMP_STEPS=100000 POISON_DELAY=0 DELTA_K=8.65 DELTA_TAU=50"
export PYTHONPATH=/mnt/d/Development/panspermia-c/src
cd $S
OUT=$R/_crianza_c.jsonl
v() {  # v <run> <variante> <args...>
  local run=$1 name=$2; shift 2
  echo "== $name $(date '+%F %H:%M')"
  for s in 0 1 2 3 4 5 6 7 8 9; do
    python crianza_c.py $R/$run --seeds $s --variant $name "$@" --config $BASE --jsonl $OUT 2>&1 | grep -E "^\{|Traceback|Error" | cut -c1-300
  done
}
v P5-inmediato-C C_delta1 --load-delta 1 --delta 1
v P5-inmediato-C C_delta0 --load-delta 1 --delta 0
v P5-inmediato-C C_congelado --load-delta 1 --frozen
v P5-inmediato-Cbar Cbar_delta2 --load-delta 2 --delta 2
v P5-inmediato-Cbar Cbar_delta1 --load-delta 2 --delta 1
touch $R/crianza_c_hecha
echo "== termina $(date '+%F %H:%M')"
