# Sonda mixta, parte de los chicos (23-10, 23:40). La memoria de Windows va justa (commit 56 de 64 GB):
# no se solapa con la suite de tests de comer frena. Al acabar los grandes, para sonda_mixta.sh (que iba a
# seguir con los chicos) y espera a que la cadena de frena pase de los tests a la calibración.
source ~/.venvs/panspermia/bin/activate
S=/mnt/c/Users/aleja/AppData/Local/Temp/claude/D--Development-panspermia/ddea0d1c-f251-40d2-8e99-9e07c65f2199/scratchpad
R=/mnt/d/Development/panspermia/runs/fase1d
until grep -q "== grande termina" $R/sonda_mixta.log; do sleep 20; done
pkill -f "bash -l $S/sonda_mixta.sh"; pkill -f "sonda_mixta.py $R/P4-salto64-chico"
echo "== grandes hechos; chicos en espera de los tests de frena $(date '+%F %H:%M')"
until grep -q "== calibración\|tests fallidos\|== termina" $R/frena_cadena.log; do sleep 60; done
echo "== chicos empiezan $(date '+%F %H:%M')"
cd $S
JAX_PLATFORMS=cpu PYTHONPATH=/mnt/d/Development/panspermia-masa/src taskset -c 0-7 python sonda_mixta.py \
  $R/P4-salto64-chico --seeds 0 1 2 3 4 --steps 1500 \
  --config K_CUT=1.5 FOOD_JUMP_PERIOD=1000 FOOD_JUMP_DIST=64 BODY_RADIUS_FIXED=2.25 --jsonl $R/_sonda_mixta.jsonl \
  && touch $R/sonda_mixta_hecha
echo "== chicos terminan $(date '+%F %H:%M')"
