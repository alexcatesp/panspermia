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
b["texto"] += (" Decisión del responsable (25-10, entre las 09:10 y las 09:20; ADR-026): sorteo al azar al nacer, sin herencia, sobre P4-alga-tripa-frena-rampa y sin el cambio"
               " global del alga. Sustrato 3.3.0, rama escalera-algabicho. Primaria (diseno v2.0): discriminación aprendida con la sonda mixta, D(aprenden) − D(congelados) ≥ 0,10"
               " en ≥ 9/10. Suite, calibración y 10 mundos desde las 09:21 (scratchpad/algabicho.sh); fin hacia las 17:00.")
n = next(x for x in m["arbol"] if x["id"] == "P4atf")
n["principal"] = False
p.write_text(json.dumps(m, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print("ok")
