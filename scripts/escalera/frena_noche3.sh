# Comer frena (ADR-025; responsable, 23-10): tras la masa, suite en GPU de escalera-frena, calibración del
# factor (0 y 0,25; semilla 0, 30 épocas), los 30 mundos (10 semillas, diseno v1.8) con el factor viable más
# fuerte y, al final, el padre P4-alga-tripa con las semillas 5–9 (cola tripa10.json de escalera-tripa).
# Viable: sin extinción (extinct_at nulo) y población final >= 500. Si ninguno lo es, se para y espera al responsable.
R=/mnt/d/Development/panspermia/runs/fase1d
source ~/.venvs/panspermia/bin/activate
export PYTHONPATH=src
cd /mnt/d/Development/panspermia-frena
echo "== espera a masa_hecho y frena_ok (visto bueno del responsable tras la revisión bibliográfica) $(date '+%F %H:%M')"
while [ ! -f $R/masa_hecho ] || [ ! -f $R/frena_ok ]; do sleep 60; done
echo "== tests $(date '+%F %H:%M')"
python -m pytest -q > $R/frena_tests.log 2>&1
tail -2 $R/frena_tests.log
if ! tail -1 $R/frena_tests.log | grep -q "passed" || tail -1 $R/frena_tests.log | grep -q "failed\|error"; then
  echo "== tests fallidos: no se lanza"; exit 1
fi
echo "== calibración $(date '+%F %H:%M')"
python -m panspermia.experiment sweep experiments/fase1d/frenacal.json --out $R >> $R/frena.log 2>&1
viable() { python -c "
import json,sys; r=json.load(open('$R/_calFrena-$1/s0/result.json'))
sys.exit(0 if r.get('extinct_at') is None and r.get('final_population',0)>=500 else 1)"; }
if viable 0.0; then Q=frena.json; elif viable 0.25; then Q=frena025.json; else echo "== ningún factor viable: se para"; exit 1; fi
echo "== $Q empieza $(date '+%F %H:%M')"
python -m panspermia.experiment sweep experiments/fase1d/$Q --out $R >> $R/frena.log 2>&1 || exit 1
echo "== padre, semillas 5–9 $(date '+%F %H:%M')"
cd /mnt/d/Development/panspermia-tripa
python -m panspermia.experiment sweep experiments/fase1d/tripa10.json --out $R >> $R/frena.log 2>&1 && touch $R/frena_hecho
echo "== termina $(date '+%F %H:%M')"
