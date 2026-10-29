import json
from pathlib import Path
p = Path("/mnt/d/Development/panspermia/docs/mapa.json")
m = json.loads(p.read_text(encoding="utf-8"))
m["actualizado"] = "2026-10-25 09:21"
b = next(x for x in m["arbol"] if x["id"] == "P4atfb")
b["estado"] = "en curso"
b["principal"] = True
b["cola"] = "algabicho.json"
b["condicion"] = "P4-alga-bicho-frena-rampa"
b["ref"] = "docs/decisiones.md"
n = next(x for x in m["arbol"] if x["id"] == "P4atf")
n["principal"] = True
p.write_text(json.dumps(m, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print("ok")

