import json
from pathlib import Path
p = Path("/mnt/d/Development/panspermia/docs/mapa.json")
m = json.loads(p.read_text(encoding="utf-8"))
m["actualizado"] = "2026-10-25 13:02"
b = next(x for x in m["arbol"] if x["id"] == "P4atfb")
b["texto"] += (" Suite en GPU correcta (88). Primera calibración (k_mean 3,804) en el tope: 4.096 bichos y energía de sobra, porque cada alga alimenta a la mitad"
               " de los bichos y la comida útil se duplica. Responsable (hacia las 13:00): parar y recalibrar con la mitad de algas (k_mean 1,902; diseno v2.1), desde las 13:02.")
p.write_text(json.dumps(m, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print("ok")
