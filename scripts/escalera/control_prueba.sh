# Prueba ligera en CPU del control positivo y negativo (pocos pasos; la GPU está ocupada con las manchas)
source ~/.venvs/panspermia/bin/activate
cd /mnt/c/Users/aleja/AppData/Local/Temp/claude/D--Development-panspermia/ddea0d1c-f251-40d2-8e99-9e07c65f2199/scratchpad
rm -f /tmp/prueba_control.jsonl
date '+%T'
JAX_PLATFORMS=cpu PYTHONPATH=/mnt/d/Development/panspermia-algabicho/src taskset -c 0-5 python madura_control.py \
  /mnt/d/Development/panspermia/runs/fase1d/P4-alga-bicho-frena-rampa --seeds 0 --rear 5 --test 60 \
  --config ALGA_PER_AGENT=1 EAT_MOVE_FACTOR=0 EAT_MOVE_RAMP_STEPS=100000 K_MEAN_RAMP_STEPS=100000 K_MEAN_RAMP_FROM=2 \
  --jsonl /tmp/prueba_control.jsonl 2>&1 | grep -E "^\{|Error|Traceback|line [0-9]" | tail -8
date '+%T'
