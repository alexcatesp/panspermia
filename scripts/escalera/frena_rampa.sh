# Comer frena con rampa (responsable, 24-10, 09:15): calibración (semillas 0–2, 150 épocas; el freno llega a 0 en
# la época 100). Viable: las 3 sin extinción y con >= 500 bichos al final. Si lo es, y cuando el criterio v1.9 esté
# escrito (marca frena_v19_ok), los 30 mundos y después el padre P4-alga-tripa con las semillas 5–9.
R=/mnt/d/Development/panspermia/runs/fase1d
source ~/.venvs/panspermia/bin/activate
export PYTHONPATH=src
cd /mnt/d/Development/panspermia-frena
echo "== calibración con rampa $(date '+%F %H:%M')"
python -m panspermia.experiment sweep experiments/fase1d/frenacal_rampa.json --out $R >> $R/frena.log 2>&1
python -c "
import json,sys
ok=True
for s in (0,1,2):
    r=json.load(open('$R/_calFrenaRampa/s%d/result.json'%s)); print(s, r.get('extinct_at'), r.get('final_population'))
    ok &= r.get('extinct_at') is None and r.get('final_population',0)>=500
sys.exit(0 if ok else 1)" || { echo "== rampa no viable: se para $(date '+%F %H:%M')"; exit 1; }
echo "== rampa viable; espera a frena_v19_ok $(date '+%F %H:%M')"
while [ ! -f $R/frena_v19_ok ]; do sleep 60; done
echo "== frena_rampa.json empieza $(date '+%F %H:%M')"
python -m panspermia.experiment sweep experiments/fase1d/frena_rampa.json --out $R >> $R/frena.log 2>&1 || exit 1
echo "== padre, semillas 5–9 $(date '+%F %H:%M')"
cd /mnt/d/Development/panspermia-tripa
python -m panspermia.experiment sweep experiments/fase1d/tripa10.json --out $R >> $R/frena.log 2>&1 && touch $R/frena_hecho
echo "== termina $(date '+%F %H:%M')"
