# Alga por bicho: ¿el tiempo sobre su alga buena es experiencia o maduración? (responsable, 25-10, entre las 21:46 y las 21:52; solo observa)
source ~/.venvs/panspermia/bin/activate
S=/mnt/c/Users/aleja/AppData/Local/Temp/claude/D--Development-panspermia/ddea0d1c-f251-40d2-8e99-9e07c65f2199/scratchpad
R=/mnt/d/Development/panspermia/runs/fase1d
export PYTHONPATH=/mnt/d/Development/panspermia-algabicho/src
cd $S
echo "== empieza $(date '+%F %H:%M')"
python madura_alga.py $R/P4-alga-bicho-frena-rampa --seeds 0 1 2 3 4 5 6 7 8 9 \
  --config ALGA_PER_AGENT=1 EAT_MOVE_FACTOR=0 EAT_MOVE_RAMP_STEPS=100000 K_MEAN_RAMP_STEPS=100000 K_MEAN_RAMP_FROM=2 \
  --jsonl $R/_madura_alga.jsonl 2>&1 | grep -E "^\{|Traceback|Error"
echo "== termina $(date '+%F %H:%M')"
