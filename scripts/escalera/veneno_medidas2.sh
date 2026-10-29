# Medidas de P5-d (ADR-030, diseno.md v2.4), en GPU tras los 20 mundos. Solo observan.
# Primaria: trampa del alga invertida con examen barajado, por condición. Secundarias: sonda mixta y su nulo.
# H-control sobre el inmediato (regla 7 de ADR-030). F = 2,5 (calibración, 07:55).
R=/mnt/d/Development/panspermia/runs/fase1d
S=/mnt/c/Users/aleja/AppData/Local/Temp/claude/D--Development-panspermia/ddea0d1c-f251-40d2-8e99-9e07c65f2199/scratchpad
BASE="ALGA_PER_AGENT=1 ALGA_PATCH_FAMILIES=1 K_CUT=1.7 EAT_MOVE_FACTOR=0 EAT_MOVE_RAMP_STEPS=100000 K_MEAN_RAMP_STEPS=100000 K_MEAN_RAMP_FROM=2 POISON_FACTOR=2.5 POISON_RAMP_STEPS=100000"
source ~/.venvs/panspermia/bin/activate
export PYTHONPATH=/mnt/d/Development/panspermia-veneno/src
cd $S
# Reanudación (26-10, 21:2x): WSL se cerró entre las 19:46 y las 21:21 con el inmediato en la semilla 4; se sigue con lo que falta.
echo "== primaria inmediato (semillas 4-9): trampa del alga invertida, examen barajado $(date '+%F %H:%M')"
python madura_alga.py $R/P5-inmediato-manchas --seeds 4 5 6 7 8 9 --scatter --config $BASE POISON_DELAY=0 \
  --jsonl $R/_madura_alga_veneno_inmediato.jsonl 2>&1 | grep -E "^\{|Traceback|Error"
for c in diferido:30 inmediato:0; do
  n=${c%%:*}; d=${c##*:}
  echo "== sonda mixta $n $(date '+%F %H:%M')"
  python sonda_mixta.py $R/P5-$n-manchas --seeds 0 1 2 3 4 5 6 7 8 9 --steps 1500 --config $BASE POISON_DELAY=$d \
    --jsonl $R/_sonda_veneno_$n.jsonl 2>&1 | grep -E "^\{|Traceback|Error"
  echo "== nulo $n $(date '+%F %H:%M')"
  python sonda_mixta.py $R/P5-$n-manchas --seeds 0 1 2 --steps 1500 --null --config $BASE POISON_DELAY=$d \
    --jsonl $R/_sonda_veneno_${n}_nulo.jsonl 2>&1 | grep -E "^\{|Traceback|Error"
done
echo "== H-control sobre el inmediato $(date '+%F %H:%M')"
python madura_control.py $R/P5-inmediato-manchas --seeds 0 1 2 3 4 5 6 7 8 9 --config $BASE POISON_DELAY=0 \
  --jsonl $R/_control_veneno_inmediato.jsonl 2>&1 | grep -E "^\{|Traceback|Error"
touch $R/veneno_medidas_hechas
echo "== termina $(date '+%F %H:%M')"
