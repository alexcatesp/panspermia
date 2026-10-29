source ~/.venvs/panspermia/bin/activate
cd /mnt/d/Development/panspermia
python -c "
import pyarrow.parquet as pq, glob
fs=sorted(glob.glob('runs/fase1d/P2-escalera-600/s0/stats/*.parquet'))
t=pq.read_table(fs[-1]); print(len(fs), t.num_rows); print(t.column_names)
"
