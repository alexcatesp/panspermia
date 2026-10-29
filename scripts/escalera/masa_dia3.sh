# (3.ª vez, 23-10 10:55: sin tests, ya pasaron; tras la caída de WSL de las 10:49)
# Pruebas de la masa (responsable, 22-10, 23:45): tras la tripa, suite en GPU de escalera-masa, P4-salto64 s1 y s2
# hasta la época 50, 6 ramas con otro azar y la cola masa.json (grande, chico, ramas, hijo a 8 u).
R=/mnt/d/Development/panspermia/runs/fase1d
source ~/.venvs/panspermia/bin/activate
export PYTHONPATH=src
cd /mnt/d/Development/panspermia-masa
echo "== e50 $(date '+%F %H:%M')"
python -m panspermia.experiment sweep experiments/fase1d/masa_e50.json --out $R >> $R/masa.log 2>&1 || exit 1
for r in 1 2 3; do for s in 1 2; do
  python scripts/branch_run.py $R/P4-salto64-e50/s$s --epoch 50 --salt $r --out $R/P4-salto64-rama$r/s$s >> $R/masa.log 2>&1 || exit 1
done; done
echo "== masa empieza $(date '+%F %H:%M')"
python -m panspermia.experiment sweep experiments/fase1d/masa.json --out $R >> $R/masa.log 2>&1 && touch $R/masa_hecho
echo "== masa termina $(date '+%F %H:%M')"
