# Prueba del tope de w0 (auditoría 15-11, rec. 1a) sobre los genomas de C; solo observa. GPU ligera; una semilla por proceso.
# Control negativo primero (--clip 4), luego --clip 1. Lanzar con: setsid nohup bash wclip_c.sh > .../wclip_c.log &
source ~/.venvs/panspermia/bin/activate
R=/mnt/d/Development/panspermia/runs/fase1d
cd /mnt/d/Development/panspermia/scripts/escalera
BASE="ALGA_PER_AGENT=1 ALGA_PATCH_FAMILIES=1 K_CUT=1.7 EAT_MOVE_FACTOR=0 EAT_MOVE_RAMP_STEPS=100000 K_MEAN_RAMP_STEPS=100000 K_MEAN_RAMP_FROM=2 POISON_FACTOR=2.5 POISON_RAMP_STEPS=100000 POISON_DELAY=0 DELTA_K=8.65 DELTA_TAU=50"
export PYTHONPATH=/mnt/d/Development/panspermia-c/src:/mnt/d/Development/panspermia/scripts/escalera
echo "== empieza $(date '+%F %H:%M')"
for clip in 4 1; do
  for s in 0 1 2 3 4 5 6 7 8 9; do
    python wclip.py $R/P5-inmediato-C --seeds $s --clip $clip --config $BASE DELTA_ON=1 --jsonl $R/_wclip_c.jsonl 2>&1 | grep -E "^\{|Traceback|Error" | cut -c1-300
  done
done
touch $R/wclip_c_hecho
echo "== termina $(date '+%F %H:%M')"
