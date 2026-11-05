# Control nulo de la sonda mixta (24-10, 09:15): las dos mitades congeladas; la diferencia debe ser ≈ 0.
source ~/.venvs/panspermia/bin/activate
S=/mnt/c/Users/<usuario>/AppData/Local/Temp/claude/D--Development-panspermia/ddea0d1c-f251-40d2-8e99-9e07c65f2199/scratchpad
R=/mnt/d/Development/panspermia/runs/fase1d
cd $S; export PYTHONPATH=/mnt/d/Development/panspermia-masa/src
echo "== empieza $(date '+%F %H:%M')"
python sonda_mixta.py $R/P4-salto64 --null --seeds 1 4 --steps 1500 --config K_CUT=1.5 FOOD_JUMP_PERIOD=1000 FOOD_JUMP_DIST=64 --jsonl $R/_sonda_mixta_nulo.jsonl
python sonda_mixta.py $R/P3-disperso --null --seeds 3 4 --steps 1500 --config K_CUT=1.5 --jsonl $R/_sonda_mixta_nulo.jsonl
python sonda_mixta.py $R/P4-alga --null --seeds 2 4 --steps 1500 --config ALGA_SWAP_PERIOD=2000 --jsonl $R/_sonda_mixta_nulo.jsonl
python sonda_mixta.py $R/P4-salto64-chico --null --seeds 3 --steps 1500 --config K_CUT=1.5 FOOD_JUMP_PERIOD=1000 FOOD_JUMP_DIST=64 BODY_RADIUS_FIXED=2.25 --jsonl $R/_sonda_mixta_nulo.jsonl
touch $R/sonda_nulo_hecha; echo "== termina $(date '+%F %H:%M')"
