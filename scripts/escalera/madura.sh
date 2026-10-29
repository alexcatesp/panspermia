# ¿Experiencia o maduración? (responsable, 25-10, 08:50; solo observa). Época 300, crianza 200 pasos, examen 500.
source ~/.venvs/panspermia/bin/activate
S=/mnt/c/Users/aleja/AppData/Local/Temp/claude/D--Development-panspermia/ddea0d1c-f251-40d2-8e99-9e07c65f2199/scratchpad
R=/mnt/d/Development/panspermia/runs/fase1d
FRENA=/mnt/d/Development/panspermia-frena/src
TRIPA=/mnt/d/Development/panspermia-tripa/src
cd $S
echo "== empieza $(date '+%F %H:%M')"
run() { PYTHONPATH=$1 python madura.py $R/$2 --seeds 0 1 2 3 4 5 6 7 8 9 --config $3 --jsonl $R/_madura.jsonl 2>&1 | grep -E "^\{|Traceback|Error"; echo "== $2 termina $(date '+%F %H:%M')"; }
run $FRENA P4-alga-tripa-frena-rampa "ALGA_SWAP_PERIOD=2000 EAT_MOVE_FACTOR=0 EAT_MOVE_RAMP_STEPS=100000"
run $FRENA P3-escaso-tripa-frena-rampa "EAT_MOVE_FACTOR=0 EAT_MOVE_RAMP_STEPS=100000"
run $TRIPA P4-alga-tripa "ALGA_SWAP_PERIOD=2000"
run $FRENA P4-alga-sin-tripa-frena-rampa "ALGA_SWAP_PERIOD=2000 EAT_MOVE_FACTOR=0 EAT_MOVE_RAMP_STEPS=100000"
touch $R/madura_hecho
echo "== termina $(date '+%F %H:%M')"
