# Alga por bicho (ADR-026; responsable, 25-10): suite en GPU; calibración (semillas 0–2, 150 épocas). Viable: las 3
# sin extinción y con >= 500 bichos al final. Si lo es, los 10 mundos (diseño v2.0).
R=/mnt/d/Development/panspermia/runs/fase1d
source ~/.venvs/panspermia/bin/activate
export PYTHONPATH=src
cd /mnt/d/Development/panspermia-algabicho
echo "== suite en GPU $(date '+%F %H:%M')"
python -m pytest -q > $R/algabicho_tests.log 2>&1 || { echo "== la suite falla: se para $(date '+%F %H:%M')"; tail -5 $R/algabicho_tests.log; exit 1; }
tail -1 $R/algabicho_tests.log
echo "== calibración $(date '+%F %H:%M')"
python -m panspermia.experiment sweep experiments/fase1d/algabichocal.json --out $R >> $R/algabicho.log 2>&1
python -c "
import json,sys
ok=True
for s in (0,1,2):
    r=json.load(open('$R/_calAlgaBicho/s%d/result.json'%s)); print(s, r.get('extinct_at'), r.get('final_population'))
    ok &= r.get('extinct_at') is None and r.get('final_population',0)>=500
sys.exit(0 if ok else 1)" || { echo "== no viable: se para $(date '+%F %H:%M')"; exit 1; }
echo "== viable; algabicho.json empieza $(date '+%F %H:%M')"
python -m panspermia.experiment sweep experiments/fase1d/algabicho.json --out $R >> $R/algabicho.log 2>&1 && touch $R/algabicho_hecho
echo "== termina $(date '+%F %H:%M')"
