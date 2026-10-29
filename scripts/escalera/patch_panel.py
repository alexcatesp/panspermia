from pathlib import Path
f = Path("D:/Development/panspermia/src/panspermia/panel.py")
s = f.read_text(encoding="utf-8")
old = '''        "debts": mapa.get("deudas", []),'''
new = '''        "debts": mapa.get("deudas", []),
        "ladder": ladder(mapa.get("escalera", []), runs, now) if runs.is_dir() else [],'''
assert s.count(old) == 1; s = s.replace(old, new)
old = '''            if path == "/api/estado":
                return self._send(json.dumps(estado(runs)).encode(), "application/json")
'''
new = '''            if path == "/api/estado":
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
'''
assert s.count(old) == 1; s = s.replace(old, new)
old = '''        def _send(self, data: bytes, ctype: str) -> None:
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", ctype)'''
new = '''        def _send(self, data: bytes, ctype: str, gzip: bool = False) -> None:
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", ctype)
            if gzip:
                self.send_header("Content-Encoding", "gzip")'''
assert s.count(old) == 1; s = s.replace(old, new)
s = s.replace("from urllib.parse import urlparse", "from urllib.parse import parse_qs, urlparse")
s = s.replace('''- las cabeceras de `docs/bitacora.md`;''', '''- las cabeceras de `docs/bitacora.md`;
- la escalera de complejidad (`escalera` en mapa.json): planteamiento, medidas por semilla, veredicto
  provisional y, en `/api/video`, un vídeo compacto de cada época grabada;''')
f.write_text(s, encoding="utf-8", newline="\n")
print("ok")
