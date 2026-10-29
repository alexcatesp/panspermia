cd /mnt/d/Development/panspermia/runs/fase1d
date
pgrep -af 'frena_rampa|experiment' | grep -v pgrep
echo "--- cadena"; tail -n 8 frena_rampa_cadena.log
ls -la frena_hecho 2>/dev/null
for d in P3-escaso-tripa-frena-rampa P4-alga-tripa; do
  [ -d "$d" ] || continue
  echo "== $d"
  for s in "$d"/s*; do
    if [ -f "$s/result.json" ]; then
      python3 -c "import json,os; r=json.load(open('$s/result.json')); print('$s', r['extinct_at'], r['final_population'], r['paused'], round(r.get('hours',0),2))"
    else
      echo "$s en curso"
    fi
  done
done
