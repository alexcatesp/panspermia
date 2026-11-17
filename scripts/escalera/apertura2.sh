# Apertura en un mundo que cambia (ADR-036; apertura.md, parte 2). Rama escalera-p4 (sustrato 2.10.0): P4-salto64 con plasticidad,
# el mismo mundo con plasticidad apagada, y el nulo P0 en el mismo sustrato; semillas 30–32 × 2.000 épocas. Marca: apertura2_hecho.
R=/mnt/d/Development/panspermia/runs/fase1d
E=/mnt/d/Development/panspermia/scripts/escalera
source ~/.venvs/panspermia/bin/activate
export PYTHONPATH=/mnt/d/Development/panspermia-p4/src
cd /mnt/d/Development/panspermia-p4
for seed in 30 31 32; do
  for name in ap2-salto ap2-salto-fijo ap2-P0; do
    for try in 1 2 3 4 5 6; do
      echo "== $name s$seed intento $try $(date '+%F %H:%M')"
      python -m panspermia.experiment sweep $E/apertura2_$seed.json --out $R --only $name >> $R/apertura2_mundos.log 2>&1
      grep -q '"final_population"\|"paused": true' $R/$name/s$seed/result.json 2>/dev/null && break
      sleep 120
    done
  done
done
touch $R/apertura2_hecho
echo "== termina $(date '+%F %H:%M')"
