"""Visor local de una ejecución: reproduce las grabaciones y muestra las estadísticas.

Uso:
    python -m panspermia.viewer runs/s0            # abre http://127.0.0.1:8765
    python -m panspermia.viewer runs/s0 --port 9000 --no-browser

Solo escucha en 127.0.0.1 y solo sirve ficheros de la página del visor y de la carpeta de la
ejecución (sin listados de directorio ni rutas fuera de ella). No ejecuta nada de los agentes.
"""
from __future__ import annotations

import argparse
import json
import mimetypes
import webbrowser
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

STATIC = Path(__file__).parent / "viewer_static"


def _inside(root: Path, rel: str) -> Path | None:
    p = (root / rel).resolve()
    return p if p.is_file() and (p == root or root in p.parents) else None


def make_handler(run_dir: Path):
    run_dir = run_dir.resolve()

    class Handler(SimpleHTTPRequestHandler):
        def log_message(self, fmt, *args):  # silencioso
            pass

        def _send_bytes(self, data: bytes, ctype: str) -> None:
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            path = unquote(urlparse(self.path).path)
            if path in ("/", "/index.html"):
                return self._send_bytes((STATIC / "index.html").read_bytes(), "text/html; charset=utf-8")
            if path == "/api/run":
                recs = sorted(p.name[:-len(".json")] for p in (run_dir / "recordings").glob("*.json")) \
                    if (run_dir / "recordings").exists() else []
                meta = json.loads((run_dir / "run.json").read_text()) if (run_dir / "run.json").exists() else {}
                body = json.dumps({"name": run_dir.name, "meta": meta, "recordings": recs}).encode()
                return self._send_bytes(body, "application/json")
            if path.startswith("/data/"):
                f = _inside(run_dir, path[len("/data/"):])
                if f is not None:
                    ctype = "application/octet-stream" if f.suffix == ".gz" else (
                        mimetypes.guess_type(f.name)[0] or "application/octet-stream")
                    return self._send_file(f, ctype)
            self.send_error(HTTPStatus.NOT_FOUND)

        def _send_file(self, f: Path, ctype: str) -> None:
            # Por trozos: un único write de ~12 MB se cortaba en Windows (ERR_CONNECTION_RESET).
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(f.stat().st_size))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            with f.open("rb") as fh:
                while chunk := fh.read(1 << 20):
                    self.wfile.write(chunk)

    return Handler


def main() -> None:
    p = argparse.ArgumentParser(description="Visor local de Panspermia.")
    p.add_argument("run_dir", type=Path)
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--no-browser", action="store_true")
    a = p.parse_args()
    if not a.run_dir.is_dir():
        raise SystemExit(f"no existe la carpeta {a.run_dir}")
    server = ThreadingHTTPServer(("127.0.0.1", a.port), make_handler(a.run_dir))
    url = f"http://127.0.0.1:{a.port}/"
    print(f"Visor en {url} (Ctrl+C para salir)")
    if not a.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
