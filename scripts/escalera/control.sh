# H-control (ADR-028): control positivo y negativo de la trampa del alga invertida sobre el alga por bicho, época 300.
# CPU ligera (taskset 0-5) mientras la GPU corre las manchas. Solo observa.
source ~/.venvs/panspermia/bin/activate
cd /mnt/c/Users/aleja/AppData/Local/Temp/claude/D--Development-panspermia/ddea0d1c-f251-40d2-8e99-9e07c65f2199/scratchpad
R=/mnt/d/Development/panspermia/runs/fase1d
echo "== control empieza $(date '+%F %H:%M')"
JAX_PLATFORMS=cpu PYTHONPATH=/mnt/d/Development/panspermia-algabicho/src taskset -c 0-5 python madura_control.py \
  $R/P4-alga-bicho-frena-rampa --seeds 0 1 2 3 4 5 6 7 8 9 \
  --config ALGA_PER_AGENT=1 EAT_MOVE_FACTOR=0 EAT_MOVE_RAMP_STEPS=100000 K_MEAN_RAMP_STEPS=100000 K_MEAN_RAMP_FROM=2 \
  --jsonl $R/_control_algabicho.jsonl 2>&1 | grep -E "^\{|Error|Traceback|line [0-9]"
touch $R/control_hecho
echo "== control termina $(date '+%F %H:%M')"
