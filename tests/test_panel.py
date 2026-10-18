"""Panel local (solo lee): estado de colas, sondas y árbol a partir de una carpeta de ejecuciones."""
import json
import os
import time

from panspermia import panel


def _world(root, cond, seed, result=None, rows=None):
    d = root / cond / f"s{seed}"
    (d / "stats").mkdir(parents=True)
    (d / "stats" / "summary.json").write_text(json.dumps(rows or [{"epoch": 10, "population": 100}]))
    if result is not None:
        (d / "result.json").write_text(json.dumps(result))
    return d


def test_estado_from_fake_tree(tmp_path):
    repo, runs = tmp_path / "panspermia", tmp_path / "panspermia" / "runs" / "fase1d"
    (repo / "experiments" / "fase1d").mkdir(parents=True)
    (repo / "docs").mkdir()
    runs.mkdir(parents=True)
    queue = [{"name": "E1-x", "seeds": [0, 1, 2], "epochs": 300}]
    (repo / "experiments" / "fase1d" / "e1.json").write_text(json.dumps(queue))
    _world(runs, "E1-x", 0, {"final_population": 10, "hours": 0.5},
           [{"epoch": e, "population": 100, "va_log_population": 0.2} for e in range(1, 301)])
    _world(runs, "E1-x", 1, {"stopped_extinct": True, "extinct_at": 52, "hours": 0.1})
    _world(runs, "E1-x", 2)  # recién escrito: en curso
    (runs / "e1.log").write_text("época    41 · 6.4s\népoca    42 · 6.5s\n", encoding="utf-8")
    (runs / "probe.jsonl").write_text('{"seconds": 600}\n{"seconds": 600}\n')
    mapa = {"actualizado": "hoy", "camino_principal": ["r", "a"], "arbol": [
        {"id": "r", "padre": None, "titulo": "raíz", "estado": "en curso"},
        {"id": "a", "padre": "r", "titulo": "E1", "estado": "auto", "cola": "e1.json"},
        {"id": "b", "padre": "r", "titulo": "sonda", "estado": "auto", "jsonl": "probe.jsonl", "total": 4},
        {"id": "c", "padre": "a", "titulo": "falló", "estado": "hecho", "resultado": "negativo"}]}
    (repo / "docs" / "mapa.json").write_text(json.dumps(mapa), encoding="utf-8")
    (repo / "docs" / "bitacora.md").write_text("## 18-10-2026\n\n### 09:00 · Algo\n", encoding="utf-8")

    e = panel.estado(runs, repo)
    nodes = {n["id"]: n for n in e["tree"]}
    q = nodes["a"]["progress"]
    assert (q["total"], q["done"], q["extinct"]) == (3, 2, 1)
    assert nodes["a"]["estado"] == "en curso"
    assert q["running"]["seed"] == 2 and q["running"]["epoch"] == 42
    assert q["eta_hours"] is not None
    assert nodes["b"]["progress"]["done"] == 2 and nodes["b"]["estado"] == "en curso"
    assert nodes["c"]["estado"] == "hecho"
    assert e["main_path"] == ["r", "a"]
    assert e["bitacora"][0] == {"day": "18-10-2026", "title": "09:00 · Algo"}
    cond = {c["condition"]: c for c in e["conditions"]}["E1-x"]
    assert cond["seeds"] == 3 and cond["survived"] == 2 and abs(cond["va_median"] - 0.2) < 1e-9


def test_ladder_verdict_is_paired_by_seed(tmp_path):
    """Escalera: el criterio compara cada semilla con la misma del peldaño anterior (5 de 5)."""
    for seed in range(3):
        for cond, thrust in (("P0-x", 1.0), ("P1-x", 0.5 if seed < 2 else 1.5)):
            rows = [{"epoch": e, "population": 100, "thrust_mean": thrust, "toxic_intake_frac": 0.5 - e / 1000}
                    for e in range(1, 301)]
            _world(tmp_path, cond, seed, {"hours": 0.1}, rows)
    rungs = [{"id": "P0", "condicion": "P0-x", "semillas": [0, 1, 2], "graficas": ["thrust_mean"]},
             {"id": "P1", "condicion": "P1-x", "semillas": [0, 1, 2],
              "primaria": {"medida": "thrust_mean", "vs": "P0", "signo": "<"}},
             {"id": "P5", "condicion": "P1-x", "semillas": [0, 1, 2],
              "primaria": {"medida": "toxic_intake_frac", "ventana_ref": [41, 50], "signo": "<"}}]
    out = {r["id"]: r for r in panel.ladder(rungs, tmp_path, time.time())}
    assert out["P0"]["verdict"] is None and out["P0"]["estado"] == "hecho"
    assert len(out["P0"]["worlds"][0]["series"]["thrust_mean"]) <= panel.SERIES_POINTS + 1
    v = out["P1"]["verdict"]
    assert [p["ok"] for p in v["per_seed"]] == [True, True, False]
    assert v["n_ok"] == 2 and v["result"] == "negativo"
    assert out["P5"]["verdict"]["result"] == "positivo"
    assert "rows" not in out["P1"]["worlds"][0]


def test_stale_world_is_interrupted(tmp_path):
    d = _world(tmp_path, "E1-x", 0)
    old = time.time() - 3600
    for p in (d, d / "stats"):
        os.utime(p, (old, old))
    assert panel.world_status(d, time.time())["state"] == "interrumpido"
