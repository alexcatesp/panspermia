"""ADR-020: firma las pausas de P2 que solo exceden mancha o laberinto y deja listos para reanudar
los mundos pausados con revisión. Una pausa por otra prueba (comunicación) queda para el responsable."""
import json, sys
from pathlib import Path
R = Path("/mnt/d/Development/panspermia/runs/fase1d")
rev = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
for res in sorted(R.glob("P2-escalera*/s*/result.json")):
    d = res.parent
    if not json.loads(res.read_text(encoding="utf-8")).get("paused"):
        continue
    pause, review = d / "CAPABILITY_PAUSE.json", d / "CAPABILITY_REVIEW.json"
    if pause.exists() and not review.exists():
        ex = json.loads(pause.read_text(encoding="utf-8"))["exceeded"]
        if set(ex) <= {"patch_gain", "maze_gain"}:
            review.write_text(json.dumps(rev, ensure_ascii=False, indent=2), encoding="utf-8")
            print("firmado", d, ex, flush=True)
        else:
            print("NO firmado (otra prueba):", d, ex, flush=True)
            continue
    if review.exists():
        res.rename(d / "result.paused.json")
        print("listo para reanudar", d, flush=True)
