# P4-alga (diseno v1.3): pasa la suite completa en GPU y lanza 5 mundos × 300 épocas.
R=/mnt/d/Development/panspermia/runs/fase1d
source ~/.venvs/panspermia/bin/activate
export PYTHONPATH=src
cd /mnt/d/Development/panspermia-p4
echo "== tests $(date '+%F %H:%M')"
python -m pytest -q > $R/p4_tests.log 2>&1
tail -2 $R/p4_tests.log
if ! tail -1 $R/p4_tests.log | grep -q "passed" || tail -1 $R/p4_tests.log | grep -q "failed\|error"; then
  echo "== tests fallidos: no se lanza"; exit 1
fi
echo "== P4-alga empieza $(date '+%F %H:%M')"
python -m panspermia.experiment sweep experiments/fase1d/p4.json --out $R >> $R/p4alga.log 2>&1 && touch $R/p4alga_hecho
echo "== P4-alga termina $(date '+%F %H:%M')"
