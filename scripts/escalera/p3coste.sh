# P3-coste (ADR-023): espera a P3-disperso, pasa la suite completa en GPU y lanza los costes 10, 20 y 5.
R=/mnt/d/Development/panspermia/runs/fase1d
source ~/.venvs/panspermia/bin/activate
export PYTHONPATH=src
cd /mnt/d/Development/panspermia-coste
while [ ! -f $R/p3disperso_hecho ]; do sleep 60; done
echo "== tests $(date '+%F %H:%M')"
python -m pytest -q > $R/p3coste_tests.log 2>&1
tail -2 $R/p3coste_tests.log
if ! tail -1 $R/p3coste_tests.log | grep -q "passed" || tail -1 $R/p3coste_tests.log | grep -q "failed\|error"; then
  echo "== tests fallidos: no se lanza"; exit 1
fi
for c in 10 20 5; do
  echo "== coste $c empieza $(date '+%F %H:%M')"
  python -m panspermia.experiment sweep experiments/fase1d/p3coste.json --out $R --only P3-coste$c >> $R/p3coste.log 2>&1
  touch $R/p3coste${c}_hecho
  echo "== coste $c termina $(date '+%F %H:%M')"
done
touch $R/p3coste_hecho
