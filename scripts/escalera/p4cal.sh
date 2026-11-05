# Calibración de P4 (semilla 0, 100 épocas): espera a que termine P3-coste (una sola carga en la GPU).
R=/mnt/d/Development/panspermia/runs/fase1d
source ~/.venvs/panspermia/bin/activate
export PYTHONPATH=src
cd /mnt/d/Development/panspermia-p4
while [ ! -f $R/p3coste_hecho ]; do sleep 60; done
echo "== empieza $(date '+%F %H:%M')"
python -m panspermia.experiment sweep /mnt/c/Users/<usuario>/AppData/Local/Temp/claude/D--Development-panspermia/ddea0d1c-f251-40d2-8e99-9e07c65f2199/scratchpad/p4cal.json --out $R/_calP4 >> $R/p4cal.log 2>&1 && touch $R/p4cal_hecho
echo "== termina $(date '+%F %H:%M')"
