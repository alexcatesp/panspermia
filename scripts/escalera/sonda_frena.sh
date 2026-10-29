# Comer frena con rampa (diseño v1.9; 25-10): sonda mixta en la época 300, 1.500 pasos, solo observa.
# Cada mundo con el código de su rama: 3.2.0 (escalera-frena) para la rampa, 3.0.0 (escalera-tripa) para el padre.
# Después, la comprobación de la manipulación (diag_comer.py) y un nulo de control en 3 semillas con freno.
source ~/.venvs/panspermia/bin/activate
S=/mnt/c/Users/aleja/AppData/Local/Temp/claude/D--Development-panspermia/ddea0d1c-f251-40d2-8e99-9e07c65f2199/scratchpad
R=/mnt/d/Development/panspermia/runs/fase1d
FRENA=/mnt/d/Development/panspermia-frena/src
TRIPA=/mnt/d/Development/panspermia-tripa/src
cd $S
SEEDS="0 1 2 3 4 5 6 7 8 9"
echo "== empieza $(date '+%F %H:%M')"
run() { PYTHONPATH=$1 python sonda_mixta.py $R/$2 --seeds $SEEDS --steps 1500 --config $3 --jsonl $R/_sonda_frena.jsonl 2>&1 | grep "^{"; echo "== $2 termina $(date '+%F %H:%M')"; }
run $FRENA P4-alga-tripa-frena-rampa "ALGA_SWAP_PERIOD=2000 EAT_MOVE_FACTOR=0 EAT_MOVE_RAMP_STEPS=100000"
run $TRIPA P4-alga-tripa "ALGA_SWAP_PERIOD=2000"
run $FRENA P4-alga-sin-tripa-frena-rampa "ALGA_SWAP_PERIOD=2000 EAT_MOVE_FACTOR=0 EAT_MOVE_RAMP_STEPS=100000"
run $FRENA P3-escaso-tripa-frena-rampa "EAT_MOVE_FACTOR=0 EAT_MOVE_RAMP_STEPS=100000"
touch $R/sonda_frena_hecha
echo "== comprobación de la manipulación $(date '+%F %H:%M')"
diag() { PYTHONPATH=$1:$S python diag_comer.py $R/$2 --seeds $SEEDS --epoch 300 --config $3 --jsonl $R/_diag_comer_frena.jsonl 2>&1 | grep "^{"; echo "== diag $2 termina $(date '+%F %H:%M')"; }
diag $FRENA P4-alga-tripa-frena-rampa "ALGA_SWAP_PERIOD=2000 EAT_MOVE_FACTOR=0 EAT_MOVE_RAMP_STEPS=100000"
diag $TRIPA P4-alga-tripa "ALGA_SWAP_PERIOD=2000"
diag $FRENA P4-alga-sin-tripa-frena-rampa "ALGA_SWAP_PERIOD=2000 EAT_MOVE_FACTOR=0 EAT_MOVE_RAMP_STEPS=100000"
touch $R/diag_frena_hecho
echo "== nulo $(date '+%F %H:%M')"
PYTHONPATH=$FRENA python sonda_mixta.py $R/P4-alga-tripa-frena-rampa --seeds 0 1 2 --steps 1500 --null \
  --config ALGA_SWAP_PERIOD=2000 EAT_MOVE_FACTOR=0 EAT_MOVE_RAMP_STEPS=100000 --jsonl $R/_sonda_frena_nulo.jsonl 2>&1 | grep "^{"
echo "== termina $(date '+%F %H:%M')"
