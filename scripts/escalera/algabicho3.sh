# Alga por bicho con rampa de comida (responsable, 25-10, 13:30; sustrato 3.4.0): suite en GPU; calibración (semillas
# 0–2, 150 épocas). Viable: las 3 sin extinción, con >= 500 bichos al final y población media de las épocas 100–149
# < 3.900. Si lo es, los 10 mundos.
R=/mnt/d/Development/panspermia/runs/fase1d
source ~/.venvs/panspermia/bin/activate
export PYTHONPATH=src
cd /mnt/d/Development/panspermia-algabicho
echo "== suite en GPU (3.4.0) $(date '+%F %H:%M')"
python -m pytest -q > $R/algabicho_tests.log 2>&1 || { echo "== la suite falla: se para $(date '+%F %H:%M')"; tail -5 $R/algabicho_tests.log; exit 1; }
tail -1 $R/algabicho_tests.log
echo "== tercera calibración (rampa de comida) $(date '+%F %H:%M')"
python -m panspermia.experiment sweep experiments/fase1d/algabichocal3.json --out $R >> $R/algabicho.log 2>&1
python -c "
import glob, json, sys
import pyarrow.parquet as pq
ok = True
for s in (0, 1, 2):
    r = json.load(open('$R/_calAlgaBicho3/s%d/result.json' % s))
    rows = [x for f in sorted(glob.glob('$R/_calAlgaBicho3/s%d/stats/*.parquet' % s))
            for x in pq.read_table(f, columns=['epoch', 'population', 'mean_energy']).to_pylist() if x['epoch'] >= 100]
    pm = sum(x['population'] for x in rows) / len(rows) if rows else 0
    em = sum(x['mean_energy'] for x in rows) / len(rows) if rows else 0
    print(s, r.get('extinct_at'), r.get('final_population'), 'media 100-149:', round(pm), 'energía:', round(em, 1))
    ok &= r.get('extinct_at') is None and r.get('final_population', 0) >= 500 and bool(rows) and pm < 3900
sys.exit(0 if ok else 1)" || { echo "== no viable: se para $(date '+%F %H:%M')"; exit 1; }
echo "== viable; algabicho.json empieza $(date '+%F %H:%M')"
python -m panspermia.experiment sweep experiments/fase1d/algabicho.json --out $R >> $R/algabicho.log 2>&1 && touch $R/algabicho_hecho
echo "== termina $(date '+%F %H:%M')"
