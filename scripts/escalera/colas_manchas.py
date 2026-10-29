import json
from pathlib import Path

D = Path("/mnt/d/Development/panspermia-manchas/experiments/fase1d")
env = {"attack_on": 0, "chem_on": 0, "signal_on": 0, "seasonal": 0, "repro_mode": "energia", "drift": 0.0,
       "k_mean": 8.792, "gut_sense": 1}
cfg = {"ALGA_PER_AGENT": 1, "ALGA_PATCH_FAMILIES": 1, "K_CUT": 1.7, "EAT_MOVE_FACTOR": 0.0, "EAT_MOVE_RAMP_STEPS": 100000,
       "K_MEAN_RAMP_STEPS": 100000, "K_MEAN_RAMP_FROM": 2.0}
base = {"node": "fase1d-w0", "n_max": 4096, "n_init": 512, "block": "MANCHAS", "env": env, "config": cfg}
cal = [{"name": "_calManchas", **base, "seeds": [0, 1, 2], "epochs": 150,
        "description": "Calibración de las manchas de un solo tipo (ADR-027; responsable, 25-10, entre las 21:54 y las 21:59): "
                       "sobre el alga por bicho, comida en 18 manchas de ~71 u a ~177 u (K_CUT 1,7, 9 % del suelo), cada una de "
                       "un tipo (dos familias de ondas, sustrato 3.5.0). k_mean 8,792: la misma comida total que el padre, con la "
                       "rampa del doble a la mitad. Viable si las 3 terminan sin extinción, con 500 bichos o más y con la "
                       "población media de las épocas 100–149 por debajo de 3.900."}]
q = [{"name": "P4-manchas-bicho-frena-rampa", **base, "seeds": list(range(10)), "epochs": 300,
      "description": "Manchas lejanas de un solo tipo (ADR-027; decisión del responsable, 25-10): sobre P4-alga-bicho-frena-rampa "
                     "(padre), la comida se reparte en manchas separadas, cada una de un tipo de alga que se ve de lejos; ir a la "
                     "equivocada cuesta el viaje. Sustrato 3.5.0. Criterio: diseno.md v2.3."}]
(D / "manchascal.json").write_text(json.dumps(cal, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
(D / "manchas.json").write_text(json.dumps(q, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print("ok")
