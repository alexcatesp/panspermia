import sys; sys.path.insert(0,"scripts")
from analyze_1d import seed_summary
from pathlib import Path
R=Path("D:/Development/panspermia/runs/fase1d")
for c in ["E0-fijo-N4096","E0-aleatorio-T560-N4096","E0b-fijo-tf03","E0b-aleatorio-T200-tf03","E0b-aleatorio-T800-tf03"]:
    for s in sorted((R/c).glob("s*")):
        v=seed_summary(s)
        f=lambda k,fmt: format(v[k],fmt) if v[k] is not None else "-"
        print(c[:26].ljust(26), s.name, "ext", int(v['extinct']), "pob", f('population_late','.0f'), "vida", f('lifespan','.0f'), "tgen", f('tau_gen','.0f'), "va_pob", f('va_population','+.2f'), "va_ing", f('va_intake','+.2f'), "tox", f('toxic_frac','.2f'), "ocultas", f('hidden','.1f'))
