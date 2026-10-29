# Comprobación temprana de la manipulación (solo observa): ¿comer se vuelve una decisión con el freno total?
source ~/.venvs/panspermia/bin/activate
S=/mnt/c/Users/aleja/AppData/Local/Temp/claude/D--Development-panspermia/ddea0d1c-f251-40d2-8e99-9e07c65f2199/scratchpad
R=/mnt/d/Development/panspermia/runs/fase1d
cd $S
JAX_PLATFORMS=cpu PYTHONPATH=/mnt/d/Development/panspermia-frena/src:$S taskset -c 0-7 python diag_comer.py $R/_calFrenaRampa --seeds 0 1 2 --epoch 150 \
  --config ALGA_SWAP_PERIOD=2000 EAT_MOVE_FACTOR=0 EAT_MOVE_RAMP_STEPS=100000 --jsonl $R/_diag_comer.jsonl 2>&1 | grep "^{"
