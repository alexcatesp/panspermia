import json
from pathlib import Path

P = Path("D:/Development/panspermia/docs/mapa.json")
m = json.loads(P.read_text(encoding="utf-8"))
G = ["population", "thrust_mean", "hidden_mean", "mass_mean", "lifespan_mean", "va_log_population"]
COMMON = ["sin ataque", "sin química", "sin señal"]
m["escalera"] = [
    {"id": "P0", "condicion": "P0-feliz", "titulo": "Mundo feliz",
     "anade": "Punto de partida: vivir es gratis, no hay comida, todos mueren a los 600 pasos y se nace por edad con energía regalada.",
     "anade_corto": "punto de partida, sin selección",
     "pregunta": "¿Qué hacen las medidas cuando no hay selección?",
     "prediccion": "El mundo se llena (≥ 95 % de 4.096). Cerebro, cuerpo y movimiento derivan al azar, sin tendencia; aprender no aporta nada (VA ≈ 0).",
     "primaria": None, "secundarias": ["hidden_mean", "thrust_mean", "mass_mean", "va_log_population"],
     "interruptores": ["vivir gratis", "sin comida", "vida fija 600 pasos", "nacer por edad", *COMMON], "graficas": G},
    {"id": "P1", "condicion": "P1-peaje", "titulo": "Peaje a vivir",
     "anade": "Vivir, moverse, cada neurona y el tamaño cuestan energía; ya no hay edad máxima.",
     "anade_corto": "vivir cuesta energía",
     "pregunta": "¿Funciona la selección? ¿Ganan los que gastan menos?",
     "prediccion": "Se mueven menos, tienen menos neuronas y cuerpos más pequeños que en P0. Aprender sigue sin servir (no hay nada que aprender).",
     "primaria": {"medida": "thrust_mean", "vs": "P0", "signo": "<"},
     "secundarias": ["hidden_mean", "mass_mean", "va_log_population"],
     "interruptores": ["+vivir cuesta", "sin comida", "nacer por edad", *COMMON], "graficas": G},
    {"id": "P2", "condicion": "P2-comida-quieta", "titulo": "Comida quieta",
     "anade": "Comida que crece y se agota, en manchas que no se mueven. Se sigue naciendo por edad con energía regalada.",
     "anade_corto": "comida en manchas quietas",
     "pregunta": "¿Sirve la comida? ¿Van a por ella?",
     "prediccion": "Viven más que en P1 y se mueven más (ir hacia la comida compensa).",
     "primaria": {"medida": "lifespan_mean", "vs": "P1", "signo": ">"},
     "secundarias": ["thrust_mean", "intake", "va_log_population"],
     "interruptores": ["vivir cuesta", "+comida quieta", "nacer por edad", *COMMON], "graficas": [*G, "intake"]},
    {"id": "P3", "condicion": "P3-hijos-pagados", "titulo": "Hijos pagados",
     "anade": "Tener un hijo cuesta: hay que superar el umbral de energía y cederle una parte. La comida pasa a ser la única fuente de energía.",
     "anade_corto": "los hijos se pagan con energía",
     "pregunta": "¿Limita la comida a la población?",
     "prediccion": "Menos población que en P2: ya no se llena el mundo.",
     "primaria": {"medida": "population", "vs": "P2", "signo": "<"},
     "secundarias": ["hidden_mean", "va_log_population"],
     "interruptores": ["vivir cuesta", "comida quieta", "+hijos pagados", *COMMON], "graficas": [*G, "intake"]},
    {"id": "P4", "condicion": "P4-comida-movil", "titulo": "Comida móvil",
     "anade": "Las manchas de comida se desplazan despacio, como en el mundo de siempre.",
     "anade_corto": "la comida se desplaza",
     "pregunta": "¿Obliga la comida móvil a moverse más?",
     "prediccion": "Más empuje que en P3. La deriva es lenta respecto a una vida, así que aprender probablemente aún no compensa.",
     "primaria": {"medida": "thrust_mean", "vs": "P3", "signo": ">"},
     "secundarias": ["va_log_population"],
     "interruptores": ["vivir cuesta", "+comida móvil", "hijos pagados", *COMMON], "graficas": [*G, "intake"]},
    {"id": "P5", "condicion": "P5-veneno", "titulo": "Comida buena y mala",
     "anade": "Un tipo de alga es tóxico: el mismo en todo el mundo y siempre (factor 0,3, rampa de 40 épocas).",
     "anade_corto": "un alga es venenosa",
     "pregunta": "¿Aprenden a evitar el veneno? ¿Empieza aquí a compensar aprender?",
     "prediccion": "La fracción tóxica baja respecto al final de la rampa (épocas 41–50). Esperamos VA > 0 por primera vez. Se compara con E1b-uniforme, que además tiene química, ataque y señal.",
     "primaria": {"medida": "toxic_intake_frac", "ventana_ref": [41, 50], "signo": "<"},
     "secundarias": ["va_log_population", "va_log_intake"],
     "interruptores": ["vivir cuesta", "comida móvil", "hijos pagados", "+veneno uniforme", *COMMON],
     "graficas": ["population", "toxic_intake_frac", "thrust_mean", "hidden_mean", "va_log_population", "va_log_intake"]},
]

arbol = m["arbol"]
by = {n["id"]: n for n in arbol}
for n in arbol:
    n["principal"] = False
# el primer intento: la fase 0 también encendió varias cosas a la vez
by["f0"].update({"padre": "raiz", "salto": True,
                 "anade": "mundo 2D determinista con comida, gasto, hambre, reproducción pagada y plasticidad, todo a la vez"})
new = [
    {"id": "escalera", "padre": "raiz", "titulo": "Escalera de complejidad (un interruptor cada vez)", "corto": "Escalera",
     "estado": "en curso", "resultado": None, "anade": "rehacer el camino de un interruptor en un interruptor",
     "texto": "Decisión del responsable tras la retrospectiva del 18-10: cada fase había encendido muchas cosas a la vez y nunca se probó un control sin selección. Orden en la GPU: E2 → escalera → E9 → E1b.",
     "ref": "ADR-014 · docs/escalera/diseno.md", "recurso": "GPU"},
]
prev = "escalera"
for r in m["escalera"]:
    new.append({"id": r["id"], "padre": prev, "titulo": f"{r['id']} · {r['titulo']}", "corto": f"{r['id']} · {r['titulo']}",
                "estado": "auto", "resultado": None, "anade": r["anade_corto"], "texto": r["pregunta"] + " " + r["prediccion"],
                "cola": "escalera.json", "condicion": r["condicion"], "ref": "docs/escalera/diseno.md", "recurso": "GPU"})
    prev = r["id"]
new.append({"id": "P6", "padre": "P5", "titulo": "Siguientes peldaños (según lo que salga)", "corto": "Siguiente peldaño",
            "estado": "decision", "resultado": None, "anade": "una sola cosa más, elegida según el resultado de P5",
            "texto": "Árbol binario: si un peldaño sale bien, el siguiente construye sobre esa variable; si sale mal, se descarta y se prueba otra. Candidatos: veneno que cambia en el tiempo (E1), química, ataque, señal."})
arbol[1:1] = new
by = {n["id"]: n for n in arbol}
by["larga"]["padre"] = "P6"
by["lenguaje"]["padre"] = "raiz"
main = ["raiz", "escalera", "P0", "P1", "P2", "P3", "P4", "P5", "P6", "larga", "fuga", "red", "robot"]
for i in main:
    by[i]["principal"] = True
m["camino_principal"] = main
m["actualizado"] = "2026-10-18 18:45"
m["hipotesis"].append({"id": "ESC", "texto": "Escalera: ¿en qué peldaño empieza a compensar aprender en vida (VA > 0)?",
                       "resultado": None, "detalle": "Predicción: ni en P0 ni en P1; probablemente en P5."})
P.write_text(json.dumps(m, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
print(len(arbol), "nodos")
