# Manchas lejanas de un solo tipo (ADR-027; responsable, 25-10; sustrato 3.5.0, escalera-manchas): suite en GPU;
# calibración (semillas 0–2, 150 épocas; viable: las 3 sin extinción, >= 500 bichos al final y población media de las
# épocas 100–149 < 3.900); si lo es, los 10 mundos; después, la primaria (trampa del alga invertida con el examen
# barajado, diseno.md v2.3) y las secundarias (sonda mixta y su nulo). Las medidas solo observan.
R=/mnt/d/Development/panspermia/runs/fase1d
S=/mnt/c/Users/aleja/AppData/Local/Temp/claude/D--Development-panspermia/ddea0d1c-f251-40d2-8e99-9e07c65f2199/scratchpad
CFG="ALGA_PER_AGENT=1 ALGA_PATCH_FAMILIES=1 K_CUT=1.7 EAT_MOVE_FACTOR=0 EAT_MOVE_RAMP_STEPS=100000 K_MEAN_RAMP_STEPS=100000 K_MEAN_RAMP_FROM=2"
source ~/.venvs/panspermia/bin/activate
export PYTHONPATH=src
cd /mnt/d/Development/panspermia-manchas
echo "== suite en GPU (3.5.0) $(date '+%F %H:%M')"
python -m pytest -q > $R/manchas_tests.log 2>&1 || { echo "== la suite falla: se para $(date '+%F %H:%M')"; tail -5 $R/manchas_tests.log; exit 1; }
tail -1 $R/manchas_tests.log
echo "== calibración $(date '+%F %H:%M')"
python -m panspermia.experiment sweep experiments/fase1d/manchascal.json --out $R >> $R/manchas.log 2>&1
python -c "
import glob, json, sys
import pyarrow.parquet as pq
ok = True
for s in (0, 1, 2):
    r = json.load(open('$R/_calManchas/s%d/result.json' % s))
    rows = [x for f in sorted(glob.glob('$R/_calManchas/s%d/stats/*.parquet' % s))
            for x in pq.read_table(f, columns=['epoch', 'population', 'mean_energy']).to_pylist() if x['epoch'] >= 100]
    pm = sum(x['population'] for x in rows) / len(rows) if rows else 0
    em = sum(x['mean_energy'] for x in rows) / len(rows) if rows else 0
    print(s, r.get('extinct_at'), r.get('final_population'), 'media 100-149:', round(pm), 'energía:', round(em, 1))
    ok &= r.get('extinct_at') is None and r.get('final_population', 0) >= 500 and bool(rows) and pm < 3900
sys.exit(0 if ok else 1)" || { echo "== no viable: se para $(date '+%F %H:%M')"; exit 1; }
echo "== viable; manchas.json empieza $(date '+%F %H:%M')"
python -m panspermia.experiment sweep experiments/fase1d/manchas.json --out $R >> $R/manchas.log 2>&1 && touch $R/manchas_hecho
echo "== mundos terminados $(date '+%F %H:%M')"
export PYTHONPATH=/mnt/d/Development/panspermia-manchas/src
cd $S
echo "== primaria: trampa del alga invertida, examen barajado $(date '+%F %H:%M')"
python madura_alga.py $R/P4-manchas-bicho-frena-rampa --seeds 0 1 2 3 4 5 6 7 8 9 --scatter --config $CFG \
  --jsonl $R/_madura_alga_manchas.jsonl 2>&1 | grep -E "^\{|Traceback|Error"
echo "== sonda mixta $(date '+%F %H:%M')"
python sonda_mixta.py $R/P4-manchas-bicho-frena-rampa --seeds 0 1 2 3 4 5 6 7 8 9 --steps 1500 --config $CFG \
  --jsonl $R/_sonda_manchas.jsonl 2>&1 | grep -E "^\{|Traceback|Error"
echo "== nulo $(date '+%F %H:%M')"
python sonda_mixta.py $R/P4-manchas-bicho-frena-rampa --seeds 0 1 2 --steps 1500 --null --config $CFG \
  --jsonl $R/_sonda_manchas_nulo.jsonl 2>&1 | grep -E "^\{|Traceback|Error"
touch $R/manchas_medidas_hechas
echo "== termina $(date '+%F %H:%M')"
