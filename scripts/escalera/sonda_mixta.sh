# Sonda mixta (responsable, 23-10, 23:20): ¿qué aprenden los grandes? CPU, una copia del mundo cada vez.
source ~/.venvs/panspermia/bin/activate
S=/mnt/c/Users/aleja/AppData/Local/Temp/claude/D--Development-panspermia/ddea0d1c-f251-40d2-8e99-9e07c65f2199/scratchpad
R=/mnt/d/Development/panspermia/runs/fase1d
cd $S
export JAX_PLATFORMS=cpu PYTHONPATH=/mnt/d/Development/panspermia-masa/src
echo "== empieza $(date '+%F %H:%M')"
for c in "grande 6.6" "chico 2.25"; do
  set -- $c
  taskset -c 0-7 python sonda_mixta.py $R/P4-salto64-$1 --seeds 0 1 2 3 4 --steps 1500 \
    --config K_CUT=1.5 FOOD_JUMP_PERIOD=1000 FOOD_JUMP_DIST=64 BODY_RADIUS_FIXED=$2 --jsonl $R/_sonda_mixta.jsonl
  echo "== $1 termina $(date '+%F %H:%M')"
done
touch $R/sonda_mixta_hecha
