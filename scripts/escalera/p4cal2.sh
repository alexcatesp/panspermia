# Calibración de P4 (semilla 0, 100 épocas): segunda tanda: salto corto y doble de algas.
R=/mnt/d/Development/panspermia/runs/fase1d
source ~/.venvs/panspermia/bin/activate
export PYTHONPATH=src
cd /mnt/d/Development/panspermia-p4

echo "== empieza $(date '+%F %H:%M')"
python -m panspermia.experiment sweep /mnt/c/Users/aleja/AppData/Local/Temp/claude/D--Development-panspermia/ddea0d1c-f251-40d2-8e99-9e07c65f2199/scratchpad/p4cal2.json --out $R/_calP4b >> $R/p4cal2.log 2>&1 && touch $R/p4cal2_hecho
echo "== termina $(date '+%F %H:%M')"
