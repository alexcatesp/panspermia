# P5-d, veneno diferido (ADR-030, panel 05, 26-10; sustrato 3.6.0, escalera-veneno): suite en GPU; calibración de F
# (2,5 y 1,5; si ninguna es viable, 1,25), con 2 semillas × 200 épocas y el criterio de diseno.md v2.3b; con la F más
# dañina viable, los 20 mundos (P5-diferido y P5-inmediato, 10 × 300 épocas). Las medidas se lanzan aparte.
R=/mnt/d/Development/panspermia/runs/fase1d
source ~/.venvs/panspermia/bin/activate
export PYTHONPATH=src
cd /mnt/d/Development/panspermia-veneno
echo "== suite en GPU (3.6.0) $(date '+%F %H:%M')"
python -m pytest -q > $R/veneno_tests.log 2>&1 || { echo "== la suite falla: se para $(date '+%F %H:%M')"; tail -5 $R/veneno_tests.log; exit 1; }
tail -1 $R/veneno_tests.log
viable() {
python -c "
import glob, json, sys
import pyarrow.parquet as pq
ok = True
for s in (0, 1):
    r = json.load(open('$R/_calVeneno$1/s%d/result.json' % s))
    rows = [x for f in sorted(glob.glob('$R/_calVeneno$1/s%d/stats/*.parquet' % s))
            for x in pq.read_table(f, columns=['epoch', 'population', 'mean_energy', 'deaths_poison', 'deaths_starvation']).to_pylist() if x['epoch'] >= 100]
    pm = sum(x['population'] for x in rows) / len(rows) if rows else 0
    em = sum(x['mean_energy'] for x in rows) / len(rows) if rows else 0
    dp = sum(x['deaths_poison'] for x in rows) / len(rows) if rows else 0
    ds = sum(x['deaths_starvation'] for x in rows) / len(rows) if rows else 0
    print('F$1 s%d' % s, r.get('extinct_at'), r.get('final_population'), 'media 100-199:', round(pm), 'energía:', round(em, 1),
          'muertes veneno/hambre por época:', round(dp), round(ds))
    ok &= r.get('extinct_at') is None and r.get('final_population', 0) >= 500 and bool(rows) and pm < 3900
sys.exit(0 if ok else 1)"
}
F=""
for tag in 25 15 125; do
  echo "== calibración F$tag $(date '+%F %H:%M')"
  python -m panspermia.experiment sweep experiments/fase1d/venenocal$tag.json --out $R >> $R/veneno.log 2>&1
  if viable $tag; then F=$tag; echo "== F$tag viable $(date '+%F %H:%M')"; break; else echo "== F$tag no viable"; fi
done
[ -z "$F" ] && { echo "== ninguna F viable: se para $(date '+%F %H:%M')"; exit 1; }
python - <<PY
import json
F = {"25": 2.5, "15": 1.5, "125": 1.25}["$F"]
base = json.load(open("experiments/fase1d/venenocal$F.json", encoding="utf-8"))[0]
out = []
for name, delay, what in (("P5-diferido-manchas", 30, "a los 30 pasos"), ("P5-inmediato-manchas", 0, "en el mismo paso (contraste)")):
    q = json.loads(json.dumps(base)); q["name"] = name; q["seeds"] = list(range(10)); q["epochs"] = 300
    q["config"]["POISON_DELAY"] = delay
    q["description"] = (f"P5-d (ADR-030, panel 05, 26-10): sobre las manchas, el alga equivocada alimenta y cobra {F} × lo que dio "
                        f"{what}; F calibrada (la más dañina viable), en rampa de 100 épocas. Sustrato 3.6.0. Criterio: diseno.md v2.4.")
    out.append(q)
json.dump(out, open("experiments/fase1d/veneno.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("cola veneno.json con F =", F)
PY
echo "== los 20 mundos empiezan $(date '+%F %H:%M')"
python -m panspermia.experiment sweep experiments/fase1d/veneno.json --out $R >> $R/veneno.log 2>&1 && touch $R/veneno_hecho
echo "== mundos terminados $(date '+%F %H:%M')"
