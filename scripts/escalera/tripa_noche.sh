# Noche del 22-10 (ADR-024, diseno v1.5): espera a P4-salto64, pasa la suite en GPU de escalera-tripa y lanza tripa.json.
R=/mnt/d/Development/panspermia/runs/fase1d
source ~/.venvs/panspermia/bin/activate
export PYTHONPATH=src
cd /mnt/d/Development/panspermia-tripa
echo "== espera a p4sitio_hecho $(date '+%F %H:%M')"
while [ ! -f $R/p4sitio_hecho ]; do sleep 60; done
echo "== tests $(date '+%F %H:%M')"
python -m pytest -q > $R/tripa_tests.log 2>&1
tail -2 $R/tripa_tests.log
if ! tail -1 $R/tripa_tests.log | grep -q "passed" || tail -1 $R/tripa_tests.log | grep -q "failed\|error"; then
  echo "== tests fallidos: no se lanza"; exit 1
fi
echo "== tripa empieza $(date '+%F %H:%M')"
python -m panspermia.experiment sweep experiments/fase1d/tripa.json --out $R >> $R/tripa.log 2>&1 && touch $R/tripa_hecho
echo "== tripa termina $(date '+%F %H:%M')"
