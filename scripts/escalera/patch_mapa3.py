import json
from pathlib import Path

P = Path("D:/Development/panspermia/docs/mapa.json")
m = json.loads(P.read_text(encoding="utf-8"))
esc = {r["id"]: r for r in m["escalera"]}
G = esc["P0"]["graficas"]
M = {"neutral": "mutación neutral: encender o apagar mitad y mitad; perder neurona = duplicar (1 %)",
     "terrestre": "mutación terrestre: se pierde el doble de lo que se gana (sesgo de deleción de la Tierra)"}
nuevos = [
    {"id": "P0n", "condicion": "P0-feliz-neutral", "titulo": "Mundo feliz · mutación neutral", "rama": "mutación",
     "anade": "Igual que P0, con una mutación que no empuja al cerebro ni a crecer ni a encoger.",
     "anade_corto": "P0 con mutación neutral",
     "pregunta": "¿Desaparece el crecimiento del cerebro sin selección?",
     "prediccion": "Las neuronas se quedan cerca de 8, por debajo de P0 (que deriva hacia ~43).",
     "primaria": {"medida": "hidden_mean", "vs": "P0", "signo": "<"}, "secundarias": ["thrust_mean", "mass_mean"],
     "interruptores": ["como P0", "+mutación neutral"], "graficas": G},
    {"id": "P0t", "condicion": "P0-feliz-terrestre", "titulo": "Mundo feliz · mutación terrestre", "rama": "mutación",
     "anade": "Igual que P0, con una mutación que pierde neuronas el doble de a menudo de lo que las gana, como en la Tierra.",
     "anade_corto": "P0 con mutación terrestre",
     "pregunta": "¿Se encogen los cerebros solos?",
     "prediccion": "Menos neuronas que con la mutación neutral; tienden a 0.",
     "primaria": {"medida": "hidden_mean", "vs": "P0n", "signo": "<"}, "secundarias": ["thrust_mean"],
     "interruptores": ["como P0", "+mutación terrestre"], "graficas": G},
    {"id": "P1n", "condicion": "P1-peaje-neutral", "titulo": "Peaje · mutación neutral", "rama": "mutación",
     "anade": "P1 (vivir cuesta) con la mutación neutral.", "anade_corto": "P1 con mutación neutral",
     "pregunta": "¿Funciona la selección también con esta mutación?",
     "prediccion": "Menos empuje que P0-neutral, como en P1 frente a P0.",
     "primaria": {"medida": "thrust_mean", "vs": "P0n", "signo": "<"}, "secundarias": ["hidden_mean", "mass_mean"],
     "interruptores": ["como P1", "+mutación neutral"], "graficas": G},
    {"id": "P1t", "condicion": "P1-peaje-terrestre", "titulo": "Peaje · mutación terrestre", "rama": "mutación",
     "anade": "P1 (vivir cuesta) con la mutación terrestre.", "anade_corto": "P1 con mutación terrestre",
     "pregunta": "¿Funciona la selección también con esta mutación?",
     "prediccion": "Menos empuje que P0-terrestre.",
     "primaria": {"medida": "thrust_mean", "vs": "P0t", "signo": "<"}, "secundarias": ["hidden_mean", "mass_mean"],
     "interruptores": ["como P1", "+mutación terrestre"], "graficas": G},
]
m["escalera"] = [r for r in m["escalera"] if r.get("rama") != "mutación"] + nuevos
arbol = [n for n in m["arbol"] if n["id"] not in {"mut", "P0n", "P0t", "P1n", "P1t"}]
i = next(k for k, n in enumerate(arbol) if n["id"] == "P1") + 1
arbol[i:i] = [
    {"id": "mut", "padre": "P0", "titulo": "Rama: física de la mutación (ADR-015)", "corto": "¿Qué mutación?",
     "estado": "pendiente", "resultado": None, "anade": "otra forma de mutar el número de neuronas",
     "texto": "P0 mostró que los cerebros crecen solos (de 8 a 29 neuronas) por cómo está programada la mutación. Se repiten P0 y P1 con mutación neutral y terrestre justo después de la escalera.",
     "ref": "ADR-015 · docs/bibliografia/escalera/"},
    *[{"id": r["id"], "padre": "mut", "titulo": r["titulo"], "corto": r["anade_corto"], "estado": "auto",
       "resultado": None, "anade": r["anade_corto"], "texto": r["pregunta"] + " " + r["prediccion"],
       "cola": "mutacion.json", "condicion": r["condicion"], "ref": "ADR-015", "recurso": "GPU"} for r in nuevos],
]
m["arbol"] = arbol
m["actualizado"] = "2026-10-18 21:58"
P.write_text(json.dumps(m, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
print("ok", len(arbol), len(m["escalera"]))
