import json
from pathlib import Path
ROOT = Path("D:/Development/panspermia")
m = ROOT / "docs/mapa.json"
d = json.loads(m.read_text(encoding="utf-8"))
d["actualizado"] = "2026-10-19 03:08"
for n in d["arbol"]:
    if n["id"] == "p0f-A1":
        n.update(estado="decision", resultado="positivo",
                 texto="Neuronas tardías: nest 21–29 y crecen; neutral ≈ 8 (se queda en el punto de partida, solo se ensancha); terrestre 0,8–1,9 (en la época 300, entre el 51 y el 67 % sin neuronas ocultas). 5/5 en las dos comparaciones. Falta que el responsable elija la física.")
    if n["id"] == "mut":
        n.update(estado="decision", resultado="positivo",
                 texto="P0 con las tres físicas (19-10, 02:56): nest infla el cerebro (21–29 neuronas), neutral lo deja en 8 y terrestre lo vacía (≈ 1). 5/5 en ambos contrastes. P1n y P1t, canceladas con la decisión de 100 % P0, esperan a que se elija la física.")
m.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
b = ROOT / "docs/bitacora.md"
b.write_text(b.read_text(encoding="utf-8").rstrip("\n") + """

## 19-10-2026

### 02:56–03:08 · A1: P0 con mutación neutral y terrestre (10 mundos, 5/5)

- **Qué:** P0-feliz-neutral y P0-feliz-terrestre, 5 semillas × 300 épocas cada uno (rama `escalera-mut`, `1cd481d`, sustrato 2.2.0), con la cola `scratchpad/p0_solo.sh`. Entre 0,36 y 0,5 h por mundo. Población llena y sin extinciones.
- **Datos:** `runs/fase1d/P0-feliz-{neutral,terrestre}/s0–s4`; análisis en `runs/fase1d/_analisis_A1.json`, `_host_P0-feliz-{neutral,terrestre}.json` y `_dist_neuronas.json`.
- **Resultado (neuronas ocultas, media de las épocas 151–300):**
  - nest: 21–29, y siguen creciendo;
  - neutral: 7,9–8,8;
  - terrestre: 0,8–1,9. En la época 300, entre el 51 y el 67 % de los bichos no tienen ninguna neurona oculta.
  - Contrastes prerregistrados: neutral < nest y terrestre < neutral, los dos **5/5** (p = 0,031).
- **Control:** la CPPN, el cuerpo, las tasas, el redondeo f16 y los nacimientos salen idénticos en las tres físicas. Solo cambian las neuronas.
- **Conclusión:** firme. La física de la mutación decide sola el tamaño del cerebro cuando no hay selección:
  - nest lo infla;
  - neutral lo conserva y solo lo dispersa;
  - terrestre lo vacía.
- **Pendiente:** el responsable elige la física (A1, y con ella A6). Detalle en `docs/escalera/p0_factores.md` § Resultados.
""", encoding="utf-8", newline="\n")
print("ok")
