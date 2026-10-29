import json
from pathlib import Path

D = Path("/mnt/d/Development/panspermia-algabicho/experiments/fase1d")
env = {"attack_on": 0, "chem_on": 0, "signal_on": 0, "seasonal": 0, "repro_mode": "energia", "drift": 0.0,
       "k_mean": 1.902, "gut_sense": 1}
cfg = {"ALGA_PER_AGENT": 1, "EAT_MOVE_FACTOR": 0.0, "EAT_MOVE_RAMP_STEPS": 100000,
       "K_MEAN_RAMP_STEPS": 100000, "K_MEAN_RAMP_FROM": 2.0}
base = {"node": "fase1d-w0", "n_max": 4096, "n_init": 512, "block": "ALGABICHO", "env": env, "config": cfg}
cal = [{"name": "_calAlgaBicho3", **base, "seeds": [0, 1, 2], "epochs": 150,
        "description": "Tercera calibración del alga por bicho (responsable, 25-10, entre las 13:25 y las 14:25): con el doble de algas viven en el tope y con la "
                       "mitad se extinguen al arrancar. Rampa de comida (sustrato 3.4.0): de 3,804 a 1,902 en las mismas 100 épocas que "
                       "el freno. Viable si las 3 terminan sin extinción, con 500 bichos o más y con la población media de las épocas "
                       "100–149 por debajo de 3.900."}]
q = [{"name": "P4-alga-bicho-frena-rampa", **base, "seeds": list(range(10)), "epochs": 300,
      "description": "Alga por bicho (ADR-026; decisión del responsable, 25-10): cada bicho nace con su alga buena sorteada, sin "
                     "herencia; la otra se come pero no alimenta. Sobre P4-alga-tripa-frena-rampa (padre), sin el cambio global del "
                     "alga; la comida baja del doble a la mitad en 100 épocas (k_mean final 1,902: la misma comida útil). Sustrato "
                     "3.4.0. Criterio: diseno.md v2.0–v2.2 (discriminación aprendida, ≥ 9/10)."}]
(D / "algabichocal3.json").write_text(json.dumps(cal, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
(D / "algabicho.json").write_text(json.dumps(q, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print("ok")
