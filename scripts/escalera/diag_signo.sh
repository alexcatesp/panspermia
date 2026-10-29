# Diagnóstico D del panel 07 (ADR-032), GPU, un mundo cada vez. Solo observa.
R=/mnt/d/Development/panspermia/runs/fase1d
S=/mnt/c/Users/aleja/AppData/Local/Temp/claude/D--Development-panspermia/ddea0d1c-f251-40d2-8e99-9e07c65f2199/scratchpad
BASE="ALGA_PER_AGENT=1 ALGA_PATCH_FAMILIES=1 K_CUT=1.7 EAT_MOVE_FACTOR=0 EAT_MOVE_RAMP_STEPS=100000 K_MEAN_RAMP_STEPS=100000 K_MEAN_RAMP_FROM=2 POISON_FACTOR=2.5 POISON_RAMP_STEPS=100000"
source ~/.venvs/panspermia/bin/activate
export PYTHONPATH=/mnt/d/Development/panspermia-veneno/src
cd $S
SEEDS=${SEEDS:-"0 1 2 3 4 5 6 7 8 9"}
OUT=${OUT:-$R/_diag_signo.jsonl}
for c in inmediato:0 diferido:30; do
  n=${c%%:*}; d=${c##*:}
  echo "== diagnóstico $n $(date '+%F %H:%M')"
  python diag_signo.py $R/P5-$n-manchas --seeds $SEEDS --config $BASE POISON_DELAY=$d --jsonl $OUT --npz $R/_diag_signo \
    2>&1 | grep -E "^\{|Traceback|Error|line [0-9]"
done
[ "$OUT" = "$R/_diag_signo.jsonl" ] && touch $R/diag_signo_hecho
echo "== termina $(date '+%F %H:%M')"
