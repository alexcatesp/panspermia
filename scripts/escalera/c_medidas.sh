# Medidas de C (diseno.md v2.5), una semilla por proceso: la cadena c.sh se quedó sin memoria de GPU (27-10, 12:49–12:51)
# al encadenar semillas en un mismo proceso. Solo observan.
R=/mnt/d/Development/panspermia/runs/fase1d
S=/mnt/c/Users/aleja/AppData/Local/Temp/claude/D--Development-panspermia/ddea0d1c-f251-40d2-8e99-9e07c65f2199/scratchpad
source ~/.venvs/panspermia/bin/activate
BASE="ALGA_PER_AGENT=1 ALGA_PATCH_FAMILIES=1 K_CUT=1.7 EAT_MOVE_FACTOR=0 EAT_MOVE_RAMP_STEPS=100000 K_MEAN_RAMP_STEPS=100000 K_MEAN_RAMP_FROM=2 POISON_FACTOR=2.5 POISON_RAMP_STEPS=100000 POISON_DELAY=0 DELTA_K=8.65 DELTA_TAU=50"
export PYTHONPATH=/mnt/d/Development/panspermia-c/src
cd $S
each() {  # each <script> <run> <jsonl> <semillas> <args...>
  local sc=$1 run=$2 out=$3 seeds=$4; shift 4
  for s in $seeds; do
    python $sc $R/$run --seeds $s "$@" --jsonl $out 2>&1 | grep -E "^\{|Traceback|Error" | cut -c1-400
  done
}
for c in C:1 Cbar:2; do
  n=${c%%:*}; d=${c##*:}
  echo "== primaria $n $(date '+%F %H:%M')"
  each madura_alga.py P5-inmediato-$n $R/_madura_alga_c_$n.jsonl "0 1 2 3 4 5 6 7 8 9" --scatter --config $BASE DELTA_ON=$d
done
for c in C:1 Cbar:2; do
  n=${c%%:*}; d=${c##*:}
  echo "== sonda mixta $n $(date '+%F %H:%M')"
  each sonda_mixta.py P5-inmediato-$n $R/_sonda_c_$n.jsonl "0 1 2 3 4 5 6 7 8 9" --steps 1500 --config $BASE DELTA_ON=$d
  echo "== nulo $n $(date '+%F %H:%M')"
  each sonda_mixta.py P5-inmediato-$n $R/_sonda_c_${n}_nulo.jsonl "0 1 2" --steps 1500 --null --config $BASE DELTA_ON=$d
  echo "== signo de m $n $(date '+%F %H:%M')"
  each diag_signo_c.py P5-inmediato-$n $R/_diag_signo_c.jsonl "0 1 2 3 4 5 6 7 8 9" --config $BASE DELTA_ON=$d
done
echo "== H-control sobre C $(date '+%F %H:%M')"
each madura_control.py P5-inmediato-C $R/_control_c.jsonl "0 1 2 3 4 5 6 7 8 9" --config $BASE DELTA_ON=1
touch $R/c_medidas_hechas
echo "== termina $(date '+%F %H:%M')"
