# Calibración de viabilidad de ap6-quimica y ap6-toxica (150 épocas, s30). Marca: apertura6cal_hecho.
R=/mnt/d/Development/panspermia/runs/fase1d
source ~/.venvs/panspermia/bin/activate
export PYTHONPATH=/mnt/d/Development/panspermia-p4/src
cd /mnt/d/Development/panspermia-p4
python -m panspermia.experiment sweep /mnt/d/Development/panspermia/scripts/escalera/apertura6cal.json --out $R/_cal6 >> $R/apertura6cal.log 2>&1
touch $R/apertura6cal_hecho
