import glob,pyarrow.parquet as pq
R='/mnt/d/Development/panspermia/runs/fase1d/'
fs=sorted(glob.glob(R+'P5-inmediato-C/s0/stats/*.parquet'))
t=pq.read_table(fs[0]); print(t.num_rows); print(t.column_names)
