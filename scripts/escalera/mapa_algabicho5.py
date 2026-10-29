import json
from pathlib import Path
p = Path("/mnt/d/Development/panspermia/docs/mapa.json")
m = json.loads(p.read_text(encoding="utf-8"))
m["actualizado"] = "2026-10-25 15:53"
b = next(x for x in m["arbol"] if x["id"] == "P4atfb")
b["texto"] = b["texto"].replace("fin hacia las 21:30.", "fin hacia las 21:30.") + (" Calibración con rampa viable en 3/3 (15:53; 2.443–2.940 bichos, sin tope, energía 8–16)."
               " Los 10 mundos empezaron a las 15:53; fin hacia las 22:00.")
p.write_text(json.dumps(m, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print("ok")
