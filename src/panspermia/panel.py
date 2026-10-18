"""Panel local en vivo: avance de las tareas de la fase 1d (solo lee; nada de los agentes).

Uso:
    python -m panspermia.panel runs/fase1d            # abre http://127.0.0.1:8766
    python -m panspermia.panel runs/fase1d --port 9001 --no-browser

Cada consulta a /api/estado vuelve a leer, sin caché:
- `docs/mapa.json` (árbol de posibilidades, hipótesis y deudas; se mantiene a mano);
- las colas `experiments/fase1d/*.json` de este repositorio y de sus worktrees hermanos
  (`../panspermia*`);
- los mundos de `runs/fase1d` (`run.json`, `result.json`, `stats/summary.json`, los logs);
- las sondas en CPU (`*.jsonl`);
- las cabeceras de `docs/bitacora.md`;
- la escalera de complejidad (`escalera` en mapa.json): planteamiento, medidas por semilla, veredicto
  provisional y, en `/api/video`, un vídeo compacto de cada época grabada;
- y la GPU, con `nvidia-smi` si está disponible.

Solo escucha en 127.0.0.1 y solo sirve la página y ese JSON. Usa solo la biblioteca estándar,
así que desde Windows basta `PYTHONPATH=src python -m panspermia.panel ...`.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import subprocess
import time
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

STATIC = Path(__file__).parent / "viewer_static" / "panel.html"
REPO = Path(__file__).resolve().parents[2]
RUNNING_FRESH_S = 15 * 60  # un mundo sin result.json se da por vivo si escribió hace menos de esto
_EPOCH_RE = re.compile(r"época\s+(\d+)")


def _read_json(p: Path, default=None):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def _mean(xs):
    xs = [x for x in xs if isinstance(x, (int, float)) and not math.isnan(x)]
    return sum(xs) / len(xs) if xs else None


def _median(xs):
    xs = sorted(x for x in xs if isinstance(x, (int, float)) and not math.isnan(x))
    n = len(xs)
    if not n:
        return None
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2


def find_queue(name: str, repo: Path = REPO) -> Path | None:
    """La cola `name` en este repositorio o en un worktree hermano (`../panspermia*`)."""
    for root in [repo, *sorted(repo.parent.glob("panspermia*"))]:
        p = root / "experiments" / "fase1d" / name
        if p.is_file():
            return p
    return None


def _log_epoch(log: Path) -> int | None:
    """Última «época N» del log de una cola (lee solo el final)."""
    try:
        with log.open("rb") as f:
            f.seek(max(0, log.stat().st_size - 4096))
            tail = f.read().decode("utf-8", "replace")
    except OSError:
        return None
    found = _EPOCH_RE.findall(tail)
    return int(found[-1]) if found else None


def world_status(d: Path, now: float) -> dict:
    """Estado de un mundo (condición, semilla) a partir de su carpeta."""
    res = _read_json(d / "result.json")
    if res is not None:
        extinct = bool(res.get("stopped_extinct")) or res.get("extinct_at") is not None
        return {"state": "extinto" if extinct else "hecho", "hours": res.get("hours"),
                "extinct_at": res.get("extinct_at")}
    if not d.exists():
        return {"state": "pendiente"}
    mtimes = [p.stat().st_mtime for p in (d, d / "stats", d / "activity.json") if p.exists()]
    fresh = mtimes and now - max(mtimes) < RUNNING_FRESH_S
    return {"state": "en curso" if fresh else "interrumpido"}


def queue_progress(queue: Path, runs: Path, now: float, only: str | None = None) -> dict:
    """Avance de una cola; con `only`, solo de esa condición (un peldaño de la escalera)."""
    specs = _read_json(queue, [])
    specs = specs if isinstance(specs, list) else [specs]
    specs = [s for s in specs if only is None or s.get("name") == only]
    worlds, current = [], None
    for s in specs:
        for seed in s.get("seeds", []):
            d = runs / s["name"] / f"s{seed}"
            st = world_status(d, now)
            worlds.append(st)
            if st["state"] == "en curso":
                rows = _read_json(d / "stats" / "summary.json", [])
                epoch = _log_epoch(runs / f"{queue.stem}.log") or (rows[-1]["epoch"] if rows else 0)
                current = {"condition": s["name"], "seed": seed, "epoch": epoch,
                           "epochs": s.get("epochs"),
                           "series": [{"epoch": r["epoch"], "population": r.get("population"),
                                       "toxic": r.get("toxic_intake_frac")} for r in rows]}
    done = sum(w["state"] in ("hecho", "extinto") for w in worlds)
    hours = _mean([w.get("hours") for w in worlds])
    eta_h = None
    if hours is not None and done < len(worlds):
        left = len(worlds) - done
        if current and current["epochs"]:
            left -= min(current["epoch"] / current["epochs"], 1.0)
        eta_h = left * hours
    return {"queue": queue.name, "total": len(worlds), "done": done,
            "extinct": sum(w["state"] == "extinto" for w in worlds),
            "interrupted": sum(w["state"] == "interrumpido" for w in worlds),
            "running": current, "hours_per_world": hours, "eta_hours": eta_h}


def jsonl_progress(p: Path, total: int | None, now: float) -> dict:
    try:
        lines = [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]
        mtime = p.stat().st_mtime
    except (OSError, ValueError):
        lines, mtime = [], None
    secs = _mean([x.get("seconds") for x in lines])
    done = len(lines)
    eta_h = (total - done) * secs / 3600 if total and secs and done < total else None
    fresh = mtime is not None and now - mtime < 2 * (secs or 900) + 600
    return {"done": done, "total": total, "eta_hours": eta_h, "fresh": bool(fresh and total and done < total)}


def resolve_tasks(tasks: list[dict], runs: Path, now: float, repo: Path = REPO) -> list[dict]:
    out = []
    for t in tasks:
        t = dict(t)
        prog = None
        if t.get("cola"):
            q = find_queue(t["cola"], repo)
            prog = queue_progress(q, runs, now, t.get("condicion")) if q else None
            t["progress"] = prog
        elif t.get("jsonl"):
            prog = jsonl_progress(runs / t["jsonl"], t.get("total"), now)
            t["progress"] = prog
        if t.get("estado", "auto") == "auto":
            if prog is None:
                t["estado"] = "pendiente"
            elif prog["total"] and prog["done"] >= prog["total"]:
                t["estado"] = "hecho"
            elif prog.get("running") or prog.get("fresh"):
                t["estado"] = "en curso"
            elif prog["done"] > 0:
                t["estado"] = "parado"
            else:
                t["estado"] = "pendiente"
        out.append(t)
    return out


def condition_summary(runs: Path) -> list[dict]:
    """Por condición: semillas, supervivientes y medianas tardías (épocas > última/2)."""
    table = []
    for cond in sorted(d for d in runs.iterdir() if d.is_dir() and not d.name.startswith("_")):
        seeds = []
        for s in sorted(cond.glob("s*")):
            rows = _read_json(s / "stats" / "summary.json", [])
            if not rows:
                continue
            res = _read_json(s / "result.json", {})
            last = rows[-1]["epoch"]
            late = [r for r in rows if r["epoch"] > last / 2]
            seeds.append({
                "finished": bool(res), "epoch": last,
                "extinct": bool(res.get("stopped_extinct")) or res.get("extinct_at") is not None,
                "va": _mean([r.get("va_log_population") for r in late]),
                "toxic": _mean([r.get("toxic_intake_frac") for r in late]),
                "population": _mean([r.get("population") for r in late]),
            })
        if not seeds:
            continue
        alive = [x for x in seeds if not x["extinct"]]
        table.append({
            "condition": cond.name, "block": cond.name.split("-")[0], "seeds": len(seeds),
            "finished": sum(x["finished"] for x in seeds), "survived": len(alive),
            "va_median": _median([x["va"] for x in alive]),
            "va_seeds": [x["va"] for x in alive],
            "toxic_median": _median([x["toxic"] for x in alive]),
            "population_median": _median([x["population"] for x in alive]),
        })
    return table


# --- Escalera de complejidad (ADR-014, docs/escalera/diseno.md) ---------------------------------

LADDER_MEASURES = ("population", "thrust_mean", "desc_speed", "hidden_mean", "mass_mean",
                   "max_thrust_mean", "lifespan_mean", "intake", "toxic_intake_frac",
                   "va_log_population", "va_log_intake")
LATE_FROM = 151          # ventana tardía prerregistrada: épocas 151–300
SERIES_POINTS = 100      # puntos máximos por serie (las sondas VA se guardan todas)


def _window_mean(rows: list[dict], key: str, lo: int, hi: int | None = None):
    return _mean([r.get(key) for r in rows if r["epoch"] >= lo and (hi is None or r["epoch"] <= hi)])


def _series(rows: list[dict], key: str) -> list[list]:
    pts = [[r["epoch"], r[key]] for r in rows if isinstance(r.get(key), (int, float))]
    if key.startswith("va_") or len(pts) <= SERIES_POINTS:
        return pts
    step = math.ceil(len(pts) / SERIES_POINTS)
    return pts[::step] if pts[-1] in pts[::step] else [*pts[::step], pts[-1]]


def rung_worlds(cond: str, seeds: list[int], runs: Path, now: float, graphs: list[str]) -> list[dict]:
    out = []
    for seed in seeds:
        d = runs / cond / f"s{seed}"
        rows = _read_json(d / "stats" / "summary.json", [])
        rec = sorted(int(p.stem.split("_")[1].split(".")[0]) for p in (d / "recordings").glob("epoch_*.json")) \
            if (d / "recordings").is_dir() else []
        last = rows[-1]["epoch"] if rows else 0
        out.append({
            "seed": seed, **world_status(d, now), "epoch": last, "recordings": rec,
            "late": {k: _window_mean(rows, k, LATE_FROM) for k in LADDER_MEASURES} if last >= LATE_FROM else {},
            "rows": rows,  # se quita antes de enviar
            "series": {k: _series(rows, k) for k in graphs},
        })
    return out


def _verdict(prim: dict, worlds: list[dict], ref: list[dict] | None) -> dict | None:
    """Criterio prerregistrado: el signo predicho en todas las semillas (5 de 5). Provisional: el
    resultado oficial lo fija el análisis en `docs/mapa.json` (campo `resultado`)."""
    if not prim:
        return None
    key, sign = prim["medida"], prim.get("signo", "<")
    per = []
    for w in worlds:
        if "ventana_ref" in prim:  # dentro del mismo peldaño: tardía frente a una ventana anterior
            lo, hi = prim["ventana_ref"]
            a = w["late"].get(key)
            b = _window_mean(w["rows"], key, lo, hi) if a is not None else None
        else:
            r = next((x for x in ref or [] if x["seed"] == w["seed"]), None)
            a, b = w["late"].get(key), (r["late"].get(key) if r else None)
        diff = None if a is None or b is None else a - b
        ok = None if diff is None else (diff < 0 if sign == "<" else diff > 0)
        per.append({"seed": w["seed"], "value": a, "ref": b, "diff": diff, "ok": ok,
                    "final": w["state"] in ("hecho", "extinto")})
    n_ok = sum(p["ok"] is True for p in per)
    complete = all(w["state"] in ("hecho", "extinto") for w in worlds)  # un mundo extinto cuenta como fallo
    ref_done = ref is None or all(x["state"] in ("hecho", "extinto") for x in ref)
    result = None
    if complete and ref_done:
        result = "positivo" if n_ok == len(per) else "negativo"
    return {"medida": key, "signo": sign, "per_seed": per, "n_ok": n_ok, "n": len(per), "result": result}


def ladder(rungs: list[dict], runs: Path, now: float) -> list[dict]:
    """Peldaños con su planteamiento (de mapa.json), mundos, series y veredicto provisional."""
    done: dict[str, list[dict]] = {}
    out = []
    for r in rungs:
        graphs = list(dict.fromkeys(r.get("graficas", ["population", "thrust_mean", "hidden_mean"])))
        seeds = r.get("semillas", [0, 1, 2, 3, 4])
        worlds = rung_worlds(r["condicion"], seeds, runs, now, graphs)
        done[r["id"]] = worlds
        prim = r.get("primaria")
        ref = done.get(prim.get("vs")) if prim and prim.get("vs") else None
        if prim and prim.get("vs") and ref is None:  # el peldaño de referencia va después en la lista
            ref_r = next((x for x in rungs if x["id"] == prim["vs"]), None)
            ref = rung_worlds(ref_r["condicion"], seeds, runs, now, []) if ref_r else None
        verdict = _verdict(prim, worlds, ref)
        states = [w["state"] for w in worlds]
        estado = ("hecho" if all(s in ("hecho", "extinto") for s in states)
                  else "en curso" if "en curso" in states else
                  "parado" if any(s in ("hecho", "extinto", "interrumpido") for s in states) else "pendiente")
        out.append({**r, "estado": estado, "verdict": verdict, "worlds": worlds})
    for r in out:
        for w in r["worlds"]:
            w.pop("rows", None)
    return out


def video(runs: Path, cond: str, seed: int, epoch: int, every: int = 5) -> bytes | None:
    """Vídeo compacto de una época grabada, para el panel (solo biblioteca estándar).

    Formato: u32 (longitud de la cabecera JSON) + cabecera + pos (F×N×2, u8: byte alto de la
    posición cuantizada) + flags (F×N, u8; bit 7 = vivo) + color (F×N, u8 en 3-3-2) + recursos
    (R×64×64, u8). Toma 1 de cada `every` fotogramas (100 de 500: un fotograma cada 10 pasos)."""
    import gzip
    if cond not in {d.name for d in runs.iterdir() if d.is_dir()}:
        return None
    base = runs / cond / f"s{int(seed)}" / "recordings" / f"epoch_{int(epoch):06d}"
    head = _read_json(base.with_suffix(".json"))
    if head is None:
        return None
    key = (str(base), base.with_suffix(".bin.gz").stat().st_mtime, every)
    if key in _VIDEO_CACHE:
        return _VIDEO_CACHE[key]
    raw = gzip.decompress(base.with_suffix(".bin.gz").read_bytes())
    arr = head["arrays"]
    frames, n = arr["pos"]["shape"][0], arr["pos"]["shape"][1]
    idx = range(every - 1, frames, every)

    def frame(name: str, i: int, size: int) -> bytes:
        o = arr[name]["offset"] + i * n * size
        return raw[o:o + n * size]

    tr = {s: bytes(((v >> s[0]) << s[1]) for v in range(256)) for s in ((5, 5), (5, 2), (6, 0))}
    pos, flags, color = [], [], []
    for i in idx:
        pos.append(frame("pos", i, 4)[1::2])          # byte alto (u16 little-endian) de x, y
        flags.append(frame("flags", i, 1))
        c = frame("color", i, 3)
        rr, gg, bb = c[0::3].translate(tr[(5, 5)]), c[1::3].translate(tr[(5, 2)]), c[2::3].translate(tr[(6, 0)])
        color.append((int.from_bytes(rr, "little") | int.from_bytes(gg, "little")
                      | int.from_bytes(bb, "little")).to_bytes(n, "little"))
    res = arr["resources"]
    o = res["offset"]
    res_bytes = raw[o:o + math.prod(res["shape"])]
    meta = head["meta"]
    header = json.dumps({"frames": len(pos), "n": n, "frame_steps": meta.get("stride", 2) * every,
                         "res_frames": res["shape"][0], "res_grid": res["shape"][1],
                         "res_steps": meta.get("res_stride", 20), "epoch": meta.get("epoch"),
                         "seed": meta.get("seed")}).encode()
    body = len(header).to_bytes(4, "little") + header + b"".join(pos) + b"".join(flags) \
        + b"".join(color) + res_bytes
    data = gzip.compress(body, compresslevel=5)
    if len(_VIDEO_CACHE) >= 16:
        _VIDEO_CACHE.pop(next(iter(_VIDEO_CACHE)))
    _VIDEO_CACHE[key] = data
    return data


_VIDEO_CACHE: dict[tuple, bytes] = {}


def bitacora(path: Path, n: int = 14) -> list[dict]:
    """Últimas `n` entradas (### hora · título) con su fecha (## dd-mm-aaaa)."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    out, day = [], None
    for ln in lines:
        if ln.startswith("## "):
            day = ln[3:].strip()
        elif ln.startswith("### "):
            out.append({"day": day, "title": ln[4:].strip()})
    return out[-n:][::-1]


def gpu_info() -> dict | None:
    try:
        r = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,utilization.gpu,memory.used,memory.total,temperature.gpu",
             "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=4, check=True)
        name, util, used, total, temp = [x.strip() for x in r.stdout.splitlines()[0].split(",")]
        return {"name": name, "util": float(util), "mem_used": float(used), "mem_total": float(total),
                "temp": float(temp)}
    except (OSError, subprocess.SubprocessError, ValueError, IndexError):
        return None


def estado(runs: Path, repo: Path = REPO) -> dict:
    now = time.time()
    mapa = _read_json(repo / "docs" / "mapa.json", {})
    return {
        "now": now, "runs": str(runs),
        "updated": mapa.get("actualizado"),
        "tree": resolve_tasks(mapa.get("arbol", []), runs, now, repo),
        "hypotheses": mapa.get("hipotesis", []),
        "main_path": mapa.get("camino_principal", []),
        "debts": mapa.get("deudas", []),
        "ladder": ladder(mapa.get("escalera", []), runs, now) if runs.is_dir() else [],
        "conditions": condition_summary(runs) if runs.is_dir() else [],
        "bitacora": bitacora(repo / "docs" / "bitacora.md"),
        "gpu": gpu_info(),
    }


def make_handler(runs: Path):
    runs = runs.resolve()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):  # silencioso
            pass

        def _send(self, data: bytes, ctype: str, gzip: bool = False) -> None:
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", ctype)
            if gzip:
                self.send_header("Content-Encoding", "gzip")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            for i in range(0, len(data), 1 << 16):  # por trozos: un write grande se cortaba en Windows
                self.wfile.write(data[i:i + (1 << 16)])

        def do_GET(self):
            path = urlparse(self.path).path
            if path in ("/", "/index.html"):
                return self._send(STATIC.read_bytes(), "text/html; charset=utf-8")
            if path == "/api/estado":
                return self._send(json.dumps(estado(runs)).encode(), "application/json")
            if path == "/api/video":
                q = parse_qs(urlparse(self.path).query)
                try:
                    data = video(runs, q["cond"][0], int(q["seed"][0]), int(q["epoch"][0]))
                except (KeyError, ValueError, OSError):
                    data = None
                if data is None:
                    return self.send_error(HTTPStatus.NOT_FOUND)
                return self._send(data, "application/octet-stream", gzip=True)
            self.send_error(HTTPStatus.NOT_FOUND)

    return Handler


def main() -> None:
    p = argparse.ArgumentParser(description="Panel local en vivo de Panspermia.")
    p.add_argument("runs", type=Path, nargs="?", default=REPO / "runs" / "fase1d")
    p.add_argument("--port", type=int, default=8766)
    p.add_argument("--no-browser", action="store_true")
    a = p.parse_args()
    if not a.runs.is_dir():
        raise SystemExit(f"no existe la carpeta {a.runs}")
    server = ThreadingHTTPServer(("127.0.0.1", a.port), make_handler(a.runs))
    url = f"http://127.0.0.1:{a.port}/"
    print(f"Panel en {url} (Ctrl+C para salir)")
    if not a.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
