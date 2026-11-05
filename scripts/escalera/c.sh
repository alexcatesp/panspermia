# C, modulación con signo de resultado (ADR-033, panel 08, 26-10; sustrato 3.8.0, escalera-c): suite en GPU;
# calibración de k (8,65 y, si no es viable, 4,325) con 2 semillas × 200 épocas y el criterio de diseno.md v2.3b;
# los 20 mundos (P5-inmediato-C y P5-inmediato-Cbar, 10 × 300 épocas); y las medidas de diseno.md v2.5.
R=/mnt/d/Development/panspermia/runs/fase1d
S=/mnt/c/Users/<usuario>/AppData/Local/Temp/claude/D--Development-panspermia/ddea0d1c-f251-40d2-8e99-9e07c65f2199/scratchpad
source ~/.venvs/panspermia/bin/activate
export PYTHONPATH=src
cd /mnt/d/Development/panspermia-c
echo "== suite en GPU (3.8.0) $(date '+%F %H:%M')"
python -m pytest -q > $R/c_tests.log 2>&1 || { echo "== la suite falla: se para $(date '+%F %H:%M')"; tail -5 $R/c_tests.log; exit 1; }
tail -1 $R/c_tests.log
viable() {
python -c "
import glob, json, sys
import pyarrow.parquet as pq
ok = True
for s in (0, 1):
    r = json.load(open('$R/_calC$1/s%d/result.json' % s))
    rows = [x for f in sorted(glob.glob('$R/_calC$1/s%d/stats/*.parquet' % s))
            for x in pq.read_table(f, columns=['epoch', 'population', 'mean_energy', 'deaths_poison', 'deaths_starvation']).to_pylist() if x['epoch'] >= 100]
    pm = sum(x['population'] for x in rows) / len(rows) if rows else 0
    em = sum(x['mean_energy'] for x in rows) / len(rows) if rows else 0
    dp = sum(x['deaths_poison'] for x in rows) / len(rows) if rows else 0
    ds = sum(x['deaths_starvation'] for x in rows) / len(rows) if rows else 0
    print('k$1 s%d' % s, r.get('extinct_at'), r.get('final_population'), 'media 100-199:', round(pm), 'energía:', round(em, 1),
          'muertes veneno/hambre por época:', round(dp), round(ds))
    ok &= r.get('extinct_at') is None and r.get('final_population', 0) >= 500 and bool(rows) and pm < 3900
sys.exit(0 if ok else 1)"
}
K=""
for tag in 865 433; do
  echo "== calibración k$tag $(date '+%F %H:%M')"
  python -m panspermia.experiment sweep experiments/fase1d/ccal$tag.json --out $R >> $R/c.log 2>&1
  if viable $tag; then K=$tag; echo "== k$tag viable $(date '+%F %H:%M')"; break; else echo "== k$tag no viable"; fi
done
[ -z "$K" ] && { echo "== ningún k viable: se para $(date '+%F %H:%M')"; exit 1; }
python - <<PY
import json
base = json.load(open("experiments/fase1d/ccal$K.json", encoding="utf-8"))[0]
k = base["config"]["DELTA_K"]
out = []
for name, on, what in (("P5-inmediato-C", 1, "δ real"), ("P5-inmediato-Cbar", 2, "δ barajado en el tiempo (control)")):
    q = json.loads(json.dumps(base)); q["name"] = name; q["seeds"] = list(range(10)); q["epochs"] = 300
    q["config"]["DELTA_ON"] = on
    q["description"] = (f"C (ADR-033, panel 08, 26-10): P5-inmediato (F = 2,5) con m_eff = clip(m + {k}·δ_acc, −1, 1), {what}. "
                        "Sustrato 3.8.0. Criterio: diseno.md v2.5.")
    out.append(q)
json.dump(out, open("experiments/fase1d/c.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("cola c.json con k =", k)
PY
echo "== los 20 mundos empiezan $(date '+%F %H:%M')"
python -m panspermia.experiment sweep experiments/fase1d/c.json --out $R >> $R/c.log 2>&1 && touch $R/c_hecho
echo "== mundos terminados $(date '+%F %H:%M')"
[ -f $R/c_hecho ] || { echo "== faltan mundos: medidas no lanzadas"; exit 1; }
KV=$(python -c "import json; print(json.load(open('experiments/fase1d/c.json'))[0]['config']['DELTA_K'])")
BASE="ALGA_PER_AGENT=1 ALGA_PATCH_FAMILIES=1 K_CUT=1.7 EAT_MOVE_FACTOR=0 EAT_MOVE_RAMP_STEPS=100000 K_MEAN_RAMP_STEPS=100000 K_MEAN_RAMP_FROM=2 POISON_FACTOR=2.5 POISON_RAMP_STEPS=100000 POISON_DELAY=0 DELTA_K=$KV DELTA_TAU=50"
export PYTHONPATH=/mnt/d/Development/panspermia-c/src
cd $S
for c in C:1 Cbar:2; do
  n=${c%%:*}; d=${c##*:}
  echo "== primaria $n: trampa del alga invertida, examen barajado $(date '+%F %H:%M')"
  python madura_alga.py $R/P5-inmediato-$n --seeds 0 1 2 3 4 5 6 7 8 9 --scatter --config $BASE DELTA_ON=$d \
    --jsonl $R/_madura_alga_c_$n.jsonl 2>&1 | grep -E "^\{|Traceback|Error"
done
for c in C:1 Cbar:2; do
  n=${c%%:*}; d=${c##*:}
  echo "== sonda mixta $n $(date '+%F %H:%M')"
  python sonda_mixta.py $R/P5-inmediato-$n --seeds 0 1 2 3 4 5 6 7 8 9 --steps 1500 --config $BASE DELTA_ON=$d \
    --jsonl $R/_sonda_c_$n.jsonl 2>&1 | grep -E "^\{|Traceback|Error"
  echo "== nulo $n $(date '+%F %H:%M')"
  python sonda_mixta.py $R/P5-inmediato-$n --seeds 0 1 2 --steps 1500 --null --config $BASE DELTA_ON=$d \
    --jsonl $R/_sonda_c_${n}_nulo.jsonl 2>&1 | grep -E "^\{|Traceback|Error"
  echo "== signo de m $n $(date '+%F %H:%M')"
  python diag_signo_c.py $R/P5-inmediato-$n --seeds 0 1 2 3 4 5 6 7 8 9 --config $BASE DELTA_ON=$d \
    --jsonl $R/_diag_signo_c.jsonl 2>&1 | grep -E "^\{|Traceback|Error"
done
echo "== H-control sobre C $(date '+%F %H:%M')"
python madura_control.py $R/P5-inmediato-C --seeds 0 1 2 3 4 5 6 7 8 9 --config $BASE DELTA_ON=1 \
  --jsonl $R/_control_c.jsonl 2>&1 | grep -E "^\{|Traceback|Error"
touch $R/c_medidas_hechas
echo "== termina $(date '+%F %H:%M')"
