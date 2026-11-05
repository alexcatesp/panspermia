# Sonda mixta en los peldaños anteriores (24-10, 02:25; solo observa, GPU libre porque comer frena se paró en
# la calibración). ¿Había aprendizaje individual escondido tras un VA de población ≈ 0? Código de escalera-masa
# (2.11.0, idéntico bit a bit a 2.6–2.10 con sus interruptores apagados).
source ~/.venvs/panspermia/bin/activate
S=/mnt/c/Users/<usuario>/AppData/Local/Temp/claude/D--Development-panspermia/ddea0d1c-f251-40d2-8e99-9e07c65f2199/scratchpad
R=/mnt/d/Development/panspermia/runs/fase1d
cd $S
export PYTHONPATH=/mnt/d/Development/panspermia-masa/src
echo "== empieza $(date '+%F %H:%M')"
run() { python sonda_mixta.py $R/$1 --seeds ${SEEDS:-0 1 2 3 4} --steps 1500 --config $2 --jsonl $R/_sonda_mixta.jsonl; echo "== $1 termina $(date '+%F %H:%M')"; }
run P4-salto64 "K_CUT=1.5 FOOD_JUMP_PERIOD=1000 FOOD_JUMP_DIST=64"
run P3-disperso "K_CUT=1.5"
run P3-escaso "ALGA_SWAP_PERIOD=0"
run P4-alga "ALGA_SWAP_PERIOD=2000"
touch $R/sonda_previos_hecha
