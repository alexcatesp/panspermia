# b′, δ solo en sucesos + trazas (ADR-035, panel 10, 28-10; sustrato 3.9.0, escalera-bprima; intento 15):
# espera a la suite en GPU; calibración solo de viabilidad (3 mundos × 100 épocas, k 8,65 y, si no es viable, k/2 una vez);
# los 20 mundos (P5-inmediato-bprima y -bprimabar, semillas 0–9 × 300 épocas); y las medidas de diseno.md v2.7.
R=/mnt/d/Development/panspermia/runs/fase1d
S=/mnt/c/Users/aleja/AppData/Local/Temp/claude/D--Development-panspermia/ddea0d1c-f251-40d2-8e99-9e07c65f2199/scratchpad
W=/mnt/d/Development/panspermia-bprima
source ~/.venvs/panspermia/bin/activate
export PYTHONPATH=$W/src
cd $W
echo "== espera a la suite $(date '+%F %H:%M')"
while [ ! -f $R/suite_bprima_hecha ]; do sleep 60; done
tail -3 $R/suite_bprima.log
if grep -qE "failed|error" $R/suite_bprima.log || ! grep -q "passed" $R/suite_bprima.log; then
  echo "== la suite falla: se para $(date '+%F %H:%M')"; exit 1
fi
BASEC="ALGA_PER_AGENT=1 ALGA_PATCH_FAMILIES=1 K_CUT=1.7 EAT_MOVE_FACTOR=0 EAT_MOVE_RAMP_STEPS=100000 K_MEAN_RAMP_STEPS=100000 K_MEAN_RAMP_FROM=2 POISON_FACTOR=2.5 POISON_RAMP_STEPS=100000 POISON_DELAY=0 DELTA_TAU=50 TRACE_ON=1 TRACE_TAU=40 DELTA_EVENT_EPS=0.05"
viable() {  # $1 = 865 | 433; $2 = k
  rm -f $R/_wmax_calBp$1.jsonl
  (cd $S && python wmax.py $R/_calBp$1 --seeds 0 1 2 --epoch 100 --config $BASEC DELTA_K=$2 DELTA_ON=1 \
     --jsonl $R/_wmax_calBp$1.jsonl 2>&1 | grep -E "^\{|Traceback|Error")
  python -c "
import glob, json, statistics as st, sys
import pyarrow.parquet as pq
ok = True
for s in (0, 1, 2):
    r = json.load(open('$R/_calBp$1/s%d/result.json' % s))
    rows = [x for f in sorted(glob.glob('$R/_calBp$1/s%d/stats/*.parquet' % s))
            for x in pq.read_table(f, columns=['epoch', 'population']).to_pylist() if x['epoch'] >= 50]
    pm = sum(x['population'] for x in rows) / len(rows) if rows else 0
    print('k$1 s%d' % s, 'extinción', r.get('extinct_at'), 'final', r.get('final_population'), 'media 50-100:', round(pm))
    ok &= r.get('extinct_at') is None and bool(rows) and pm >= 1000
wm = [json.loads(l)['frac_wmax'] for l in open('$R/_wmax_calBp$1.jsonl') if l.strip()]
print('k$1 fracción en W_MAX (época 100):', wm, 'mediana', st.median(wm) if wm else None)
ok &= len(wm) == 3 and st.median(wm) < 0.5
sys.exit(0 if ok else 1)"
}
K=""
for kv in 865:8.65 433:4.325; do
  tag=${kv%%:*}; k=${kv##*:}
  echo "== calibración de viabilidad k$tag $(date '+%F %H:%M')"
  python -m panspermia.experiment sweep experiments/fase1d/bprimacal$tag.json --out $R >> $R/bprima.log 2>&1
  if viable $tag $k; then K=$k; echo "== k$tag viable $(date '+%F %H:%M')"; break; else echo "== k$tag no viable"; fi
done
[ -z "$K" ] && { echo "== ningún k viable: se para $(date '+%F %H:%M')"; exit 1; }
python - <<PY
import json, copy
base = json.load(open("experiments/fase1d/bprimacal865.json", encoding="utf-8"))[0]
out = []
for name, on, what in (("P5-inmediato-bprima", 1, "δ real"), ("P5-inmediato-bprimabar", 2, "δ barajado en el tiempo, ya filtrado (control)")):
    q = copy.deepcopy(base); q["name"] = name; q["seeds"] = list(range(10)); q["epochs"] = 300
    q["config"]["DELTA_ON"] = on; q["config"]["DELTA_K"] = $K
    q["description"] = (f"b′ (ADR-035, panel 10, 28-10; intento 15): P5-inmediato (F = 2,5) con trazas (τ 40) y δ solo en "
                        f"sucesos (|r| > 0,05), m_eff = clip(m + $K·δ_acc, −1, 1), {what}. Sustrato 3.9.0. Criterio: diseno.md v2.7.")
    out.append(q)
json.dump(out, open("experiments/fase1d/bprima.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("cola bprima.json con k =", $K)
PY
echo "== los 20 mundos empiezan $(date '+%F %H:%M')"
python -m panspermia.experiment sweep experiments/fase1d/bprima.json --out $R >> $R/bprima.log 2>&1 && touch $R/bprima_hecho
echo "== mundos terminados $(date '+%F %H:%M')"
[ -f $R/bprima_hecho ] || { echo "== faltan mundos: medidas no lanzadas"; exit 1; }
BASE="$BASEC DELTA_K=$K"
cd $S
for c in bprima:1 bprimabar:2; do
  n=${c%%:*}; d=${c##*:}
  echo "== primaria $n: trampa del alga invertida, examen barajado $(date '+%F %H:%M')"
  python madura_alga.py $R/P5-inmediato-$n --seeds 0 1 2 3 4 5 6 7 8 9 --scatter --config $BASE DELTA_ON=$d \
    --jsonl $R/_madura_alga_bp_$n.jsonl 2>&1 | grep -E "^\{|Traceback|Error"
done
echo "== H-control sobre b′ $(date '+%F %H:%M')"
python madura_control.py $R/P5-inmediato-bprima --seeds 0 1 2 3 4 5 6 7 8 9 --config $BASE DELTA_ON=1 \
  --jsonl $R/_control_bp.jsonl 2>&1 | grep -E "^\{|Traceback|Error"
for c in bprima:1 bprimabar:2; do
  n=${c%%:*}; d=${c##*:}
  echo "== sonda mixta $n $(date '+%F %H:%M')"
  python sonda_mixta.py $R/P5-inmediato-$n --seeds 0 1 2 3 4 5 6 7 8 9 --steps 1500 --config $BASE DELTA_ON=$d \
    --jsonl $R/_sonda_bp_$n.jsonl 2>&1 | grep -E "^\{|Traceback|Error"
  echo "== saturación de pesos $n $(date '+%F %H:%M')"
  python wmax.py $R/P5-inmediato-$n --seeds 0 1 2 3 4 5 6 7 8 9 --epoch 300 --config $BASE DELTA_ON=$d \
    --jsonl $R/_wmax_bp.jsonl 2>&1 | grep -E "^\{|Traceback|Error"
done
echo "== nulo b′ $(date '+%F %H:%M')"
python sonda_mixta.py $R/P5-inmediato-bprima --seeds 0 1 2 --steps 1500 --null --config $BASE DELTA_ON=1 \
  --jsonl $R/_sonda_bp_bprima_nulo.jsonl 2>&1 | grep -E "^\{|Traceback|Error"
touch $R/bprima_medidas_hechas
echo "== termina $(date '+%F %H:%M')"
