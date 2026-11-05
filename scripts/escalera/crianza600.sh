# Diagnóstico de crianza larga (panel 05, 26-10): trampa del alga invertida con 600 pasos de crianza sobre las manchas.
source ~/.venvs/panspermia/bin/activate
S=/mnt/c/Users/<usuario>/AppData/Local/Temp/claude/D--Development-panspermia/ddea0d1c-f251-40d2-8e99-9e07c65f2199/scratchpad
R=/mnt/d/Development/panspermia/runs/fase1d
export PYTHONPATH=/mnt/d/Development/panspermia-manchas/src
CFG="ALGA_PER_AGENT=1 ALGA_PATCH_FAMILIES=1 K_CUT=1.7 EAT_MOVE_FACTOR=0 EAT_MOVE_RAMP_STEPS=100000 K_MEAN_RAMP_STEPS=100000 K_MEAN_RAMP_FROM=2"
cd $S
echo "== crianza 600 empieza $(date '+%F %H:%M')"
python madura_alga.py $R/P4-manchas-bicho-frena-rampa --seeds 0 1 2 3 4 5 6 7 8 9 --rear 600 --scatter --config $CFG \
  --jsonl $R/_madura_alga_manchas_rear600.jsonl 2>&1 | grep -E "^\{|Traceback|Error"
touch $R/crianza600_hecha
echo "== crianza 600 termina $(date '+%F %H:%M')"
