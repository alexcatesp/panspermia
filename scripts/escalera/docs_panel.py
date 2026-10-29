from pathlib import Path
p = Path("CLAUDE.md"); s = p.read_text(encoding="utf-8")
old = "- `docs/caminos.md`: registro de caminos descartados"
new = ("- `docs/mapa.json`: **árbol de posibilidades** para el panel local. Cada nodo tiene su padre, lo que añade respecto a él "
       "(«escalera de complejidad»: idealmente una sola cosa por paso) y su resultado (✓ positivo, ◐ indicio, ✗ negativo o descartado, "
       "~ no concluyente, ⏸ aparcado). Actualizarlo con cada experimento, resultado o decisión, junto con la bitácora. "
       "Se ve con `python -m panspermia.panel` (http://127.0.0.1:8766; desde Windows, `PYTHONPATH=src`), que relee cada minuto "
       "colas, mundos, sondas y GPU.\n" + old)
assert old in s; p.write_text(s.replace(old, new, 1), encoding="utf-8")
p = Path("README.md"); s = p.read_text(encoding="utf-8")
old = "python scripts/compare_runs.py runs/phase1 runs/phase1b --to 100 # compara dos lotes"
new = old + "\nPYTHONPATH=src python -m panspermia.panel runs/fase1d          # panel en vivo: árbol de posibilidades y avance (127.0.0.1:8766)"
assert old in s; p.write_text(s.replace(old, new, 1), encoding="utf-8")
