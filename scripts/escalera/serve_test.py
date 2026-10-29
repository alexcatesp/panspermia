"""Panel de prueba en el puerto 8767: la escalera apunta a condiciones de E1 que ya tienen datos."""
import json
import sys
from http.server import ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, "D:/Development/panspermia/src")
from panspermia import panel  # noqa: E402

fake = Path(__file__).parent / "fake_repo"
(fake / "docs").mkdir(parents=True, exist_ok=True)
m = json.loads(Path("D:/Development/panspermia/docs/mapa.json").read_text(encoding="utf-8"))
conds = ["E1-fijo", "E1-aleatorio-T140", "E1-aleatorio-T560", "E1-periodico-T560", "E1-aleatorio-T2240", "E1-periodico-T140"]
for r, c in zip(m["escalera"], conds):
    r["condicion"] = c
(fake / "docs" / "mapa.json").write_text(json.dumps(m, ensure_ascii=False), encoding="utf-8")
orig = panel.estado
panel.estado = lambda runs: orig(runs, fake)
runs = Path("D:/Development/panspermia/runs/fase1d")
ThreadingHTTPServer(("127.0.0.1", 8767), panel.make_handler(runs)).serve_forever()
