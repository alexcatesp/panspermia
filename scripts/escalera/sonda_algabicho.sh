# Alga por bicho (diseño v2.0–v2.2; 25-10): sonda mixta en la época 300, 1.500 pasos (primaria: D), nulo en 3 semillas
# y diagnóstico de maduración. Solo observa. Código de escalera-algabicho (3.4.0).
source ~/.venvs/panspermia/bin/activate
S=/mnt/c/Users/<usuario>/AppData/Local/Temp/claude/D--Development-panspermia/ddea0d1c-f251-40d2-8e99-9e07c65f2199/scratchpad
R=/mnt/d/Development/panspermia/runs/fase1d
export PYTHONPATH=/mnt/d/Development/panspermia-algabicho/src
CFG="ALGA_PER_AGENT=1 EAT_MOVE_FACTOR=0 EAT_MOVE_RAMP_STEPS=100000 K_MEAN_RAMP_STEPS=100000 K_MEAN_RAMP_FROM=2"
cd $S
echo "== sonda empieza $(date '+%F %H:%M')"
python sonda_mixta.py $R/P4-alga-bicho-frena-rampa --seeds 0 1 2 3 4 5 6 7 8 9 --steps 1500 --config $CFG \
  --jsonl $R/_sonda_algabicho.jsonl 2>&1 | grep -E "^\{|Traceback|Error"
echo "== nulo $(date '+%F %H:%M')"
python sonda_mixta.py $R/P4-alga-bicho-frena-rampa --seeds 0 1 2 --steps 1500 --null --config $CFG \
  --jsonl $R/_sonda_algabicho_nulo.jsonl 2>&1 | grep -E "^\{|Traceback|Error"
echo "== maduración $(date '+%F %H:%M')"
python madura.py $R/P4-alga-bicho-frena-rampa --seeds 0 1 2 3 4 5 6 7 8 9 --config $CFG \
  --jsonl $R/_madura_algabicho.jsonl 2>&1 | grep -E "^\{|Traceback|Error"
touch $R/sonda_algabicho_hecha
echo "== termina $(date '+%F %H:%M')"
