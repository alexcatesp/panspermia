# Cierre de b′ (auditoría 15-11, rec. 2; ADR-036): las 17 medidas que faltan, un proceso por semilla (WSL se cayó por memoria).
# Espera a wclip_c_hecho para no juntar dos trabajos en la GPU. Marca: bprima_medidas_hechas.
R=/mnt/d/Development/panspermia/runs/fase1d
E=/mnt/d/Development/panspermia/scripts/escalera
W=/mnt/d/Development/panspermia-bprima
source ~/.venvs/panspermia/bin/activate
export PYTHONPATH=$W/src:$E
while [ ! -f $R/wclip_c_hecho ]; do sleep 60; done
cd $E
BASEC="ALGA_PER_AGENT=1 ALGA_PATCH_FAMILIES=1 K_CUT=1.7 EAT_MOVE_FACTOR=0 EAT_MOVE_RAMP_STEPS=100000 K_MEAN_RAMP_STEPS=100000 K_MEAN_RAMP_FROM=2 POISON_FACTOR=2.5 POISON_RAMP_STEPS=100000 POISON_DELAY=0 DELTA_TAU=50 TRACE_ON=1 TRACE_TAU=40 DELTA_EVENT_EPS=0.05"
K=$(python -c "import json; print(json.load(open('$W/experiments/fase1d/bprima.json'))[0]['config']['DELTA_K'])")
BASE="$BASEC DELTA_K=$K"
G="grep -E ^\{|Traceback|Error"
echo "== empieza $(date '+%F %H:%M') k=$K"
for s in 3 4 5 6 7 8 9; do python madura_alga.py $R/P5-inmediato-bprima --seeds $s --scatter --config $BASE DELTA_ON=1 --jsonl $R/_madura_alga_bp_bprima.jsonl 2>&1 | grep -E "^\{|Traceback|Error" | cut -c1-300; done
for s in 0 1 2 3 4 5 6 7 8 9; do python madura_alga.py $R/P5-inmediato-bprimabar --seeds $s --scatter --config $BASE DELTA_ON=2 --jsonl $R/_madura_alga_bp_bprimabar.jsonl 2>&1 | grep -E "^\{|Traceback|Error" | cut -c1-300; done
echo "== H-control $(date '+%F %H:%M')"
for s in 0 1 2 3 4 5 6 7 8 9; do python madura_control.py $R/P5-inmediato-bprima --seeds $s --config $BASE DELTA_ON=1 --jsonl $R/_control_bp.jsonl 2>&1 | grep -E "^\{|Traceback|Error" | cut -c1-300; done
for c in bprima:1 bprimabar:2; do n=${c%%:*}; d=${c##*:}
  echo "== sonda mixta y wmax $n $(date '+%F %H:%M')"
  for s in 0 1 2 3 4 5 6 7 8 9; do
    python sonda_mixta.py $R/P5-inmediato-$n --seeds $s --steps 1500 --config $BASE DELTA_ON=$d --jsonl $R/_sonda_bp_$n.jsonl 2>&1 | grep -E "^\{|Traceback|Error" | cut -c1-300
    python wmax.py $R/P5-inmediato-$n --seeds $s --epoch 300 --config $BASE DELTA_ON=$d --jsonl $R/_wmax_bp.jsonl 2>&1 | grep -E "^\{|Traceback|Error" | cut -c1-300
  done
done
touch $R/bprima_medidas_hechas
echo "== termina $(date '+%F %H:%M')"
