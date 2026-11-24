# Apertura parte 6: modelo sombra neutral. Bifurca ap4-largo (s30–s32) en la época 5000 y corre 500
# épocas con selección (sombra-real) y en modo neutral (sombra-neutral), mismo checkpoint y archivo.
# Marca: sombra_hecho. Rama del sustrato: apertura-sombra (worktree panspermia-sombra, 2.10.1).
R=/mnt/d/Development/panspermia/runs/fase1d
E=/mnt/d/Development/panspermia/scripts/escalera
source ~/.venvs/panspermia/bin/activate
export PYTHONPATH=/mnt/d/Development/panspermia-sombra/src
cd /mnt/d/Development/panspermia-sombra
for seed in 30 31 32; do
  for name in sombra-real sombra-neutral; do
    D=$R/$name/s$seed
    if [ ! -d $D/checkpoints/5000 ]; then
      mkdir -p $D/checkpoints
      cp -r $R/ap4-largo/s$seed/checkpoints/5000 $D/checkpoints/5000
      cp $R/ap4-largo/s$seed/novelty_archive.npy $R/ap4-largo/s$seed/activity.json $D/
    fi
    for try in 1 2 3 4 5 6; do
      echo "== $name s$seed intento $try $(date '+%F %H:%M')"
      python -m panspermia.experiment sweep $E/sombra_$seed.json --out $R --only $name >> $R/sombra_mundos.log 2>&1
      grep -q '"final_population"\|"paused": true' $D/result.json 2>/dev/null && break
      sleep 120
    done
  done
done
touch $R/sombra_hecho
echo "== termina $(date '+%F %H:%M')"
