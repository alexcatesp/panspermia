import json
from pathlib import Path

BASE = {"node": "fase1d-w0", "seeds": [0, 1, 2, 3, 4], "epochs": 300, "n_max": 4096, "n_init": 512,
        "block": "ESC"}
OFF = {"attack_on": 0, "chem_on": 0, "signal_on": 0, "seasonal": 0}
rungs = [
    ("P0-feliz", "Mundo feliz: vivir es gratis, no hay comida y todos mueren a la misma edad (600 pasos). "
     "Nacen por edad con energía regalada. Control neutro: lo que hacen las medidas sin selección.",
     {**OFF, "metabolism": 0, "k_mean": 0.0, "repro_mode": "edad", "max_age": 600}, {}),
    ("P1-peaje", "Peaje a vivir: vivir, moverse, cada neurona y el tamaño cuestan energía; sigue sin haber "
     "comida y se nace por edad con energía regalada. ¿Funciona la selección? (menos empuje, menos neuronas)",
     {**OFF, "metabolism": 1, "k_mean": 0.0, "repro_mode": "edad"}, {}),
    ("P2-comida-quieta", "Comida que crece y se agota en manchas quietas. La reproducción sigue siendo por "
     "edad con energía regalada: la comida solo alarga la vida.",
     {**OFF, "repro_mode": "edad", "drift": 0.0}, {}),
    ("P3-hijos-pagados", "La reproducción pasa a costar: el padre necesita superar su umbral de energía y le "
     "cede una parte al hijo. La comida es ya la única fuente de energía (ciclo cerrado).",
     {**OFF, "drift": 0.0}, {}),
    ("P4-comida-movil", "Las manchas de comida se desplazan despacio, como en el mundo de siempre.",
     {**OFF}, {}),
    ("P5-veneno", "Comida buena y mala: el mismo tipo de alga es tóxico en todo el mundo y siempre "
     "(modo uniforme, factor 0,3, rampa de 40 épocas). Sin química, ataque ni señal: se compara con "
     "E1b-uniforme, que lo tiene todo.",
     {**{k: v for k, v in OFF.items() if k != "seasonal"}, "tox_mode": "uniforme"}, {"TOXIC_FACTOR": 0.3}),
]
queue = []
for name, desc, env, cfg in rungs:
    spec = {"name": name, **BASE, "description": desc, "env": env}
    if cfg:
        spec["config"] = cfg
    queue.append(spec)
out = Path("D:/Development/panspermia-escalera/experiments/fase1d/escalera.json")
out.write_text(json.dumps(queue, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
print(len(queue), "peldaños")
