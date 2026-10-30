# Solo las medidas de b′ (ADR-035), tras la caída de WSL del 30-10 a las 20:16; los 20 mundos ya están (bprima_hecho).
R=/mnt/d/Development/panspermia/runs/fase1d
S=/mnt/c/Users/aleja/AppData/Local/Temp/claude/D--Development-panspermia/ddea0d1c-f251-40d2-8e99-9e07c65f2199/scratchpad
W=/mnt/d/Development/panspermia-bprima
source ~/.venvs/panspermia/bin/activate
export PYTHONPATH=$W/src
cd $W
BASEC="ALGA_PER_AGENT=1 ALGA_PATCH_FAMILIES=1 K_CUT=1.7 EAT_MOVE_FACTOR=0 EAT_MOVE_RAMP_STEPS=100000 K_MEAN_RAMP_STEPS=100000 K_MEAN_RAMP_FROM=2 POISON_FACTOR=2.5 POISON_RAMP_STEPS=100000 POISON_DELAY=0 DELTA_TAU=50 TRACE_ON=1 TRACE_TAU=40 DELTA_EVENT_EPS=0.05"
K=$(python -c "import json; print(json.load(open(\"experiments/fase1d/bprima.json\"))[0][\"config\"][\"DELTA_K\"])")
echo "== medidas de b′ con k = $K $(date "+%F %H:%M")"
BASE="$BASEC DELTA_K=$K"
cd $S
for c in bprima:1 bprimabar:2; do
  n=${c%%:*}; d=${c##*:}
  echo "== primaria $n: trampa del alga invertida, examen barajado $(date '+%F %H:%M')"
  python madura_alga.py $R/P5-inmediato-$n --seeds 0 1 2 3 4 5 6 7 8 9 --scatter --config $BASE DELTA_ON=$d \
    --jsonl $R/_madura_alga_bp_$n.jsonl 2>&1 | grep -E "^\{|Traceback|Error"
done
echo "== H-control sobre b′ $(date '+%F %H:%M')"
python madura_control.py $R/P5-inmediato-bprima --seeds 0 1 2 3 4 5 6 7 8 9 --config $BASE DELTA_ON=1 \
  --jsonl $R/_control_bp.jsonl 2>&1 | grep -E "^\{|Traceback|Error"
for c in bprima:1 bprimabar:2; do
  n=${c%%:*}; d=${c##*:}
  echo "== sonda mixta $n $(date '+%F %H:%M')"
  python sonda_mixta.py $R/P5-inmediato-$n --seeds 0 1 2 3 4 5 6 7 8 9 --steps 1500 --config $BASE DELTA_ON=$d \
    --jsonl $R/_sonda_bp_$n.jsonl 2>&1 | grep -E "^\{|Traceback|Error"
  echo "== saturación de pesos $n $(date '+%F %H:%M')"
  python wmax.py $R/P5-inmediato-$n --seeds 0 1 2 3 4 5 6 7 8 9 --epoch 300 --config $BASE DELTA_ON=$d \
    --jsonl $R/_wmax_bp.jsonl 2>&1 | grep -E "^\{|Traceback|Error"
done
echo "== nulo b′ $(date '+%F %H:%M')"
python sonda_mixta.py $R/P5-inmediato-bprima --seeds 0 1 2 --steps 1500 --null --config $BASE DELTA_ON=1 \
  --jsonl $R/_sonda_bp_bprima_nulo.jsonl 2>&1 | grep -E "^\{|Traceback|Error"
touch $R/bprima_medidas_hechas
echo "== termina $(date '+%F %H:%M')"
