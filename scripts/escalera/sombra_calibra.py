"""Calibra la sombra neutral (apertura 6) desde el checkpoint 5000 de ap4-largo. Solo observa.
Imprime NEUTRAL_POP y los riesgos por paso (menores de MIN_REPRO_AGE, adultos) que reproducen,
en equilibrio, la misma población y la misma proporción de menores con B = MAX_BIRTHS_PER_STEP."""
import sys, json, numpy as np, jax
from pathlib import Path
import orbax.checkpoint as ocp
from panspermia import island, config as C

seed = int(sys.argv[1]); src = Path(sys.argv[2]).resolve()
state = island.init_island(seed, b"fase1d-w0", n_max=4096, n_init=512)
mngr = ocp.CheckpointManager(src / "checkpoints")
st = mngr.restore(5000, args=ocp.args.StandardRestore(jax.tree.map(ocp.utils.to_shape_dtype_struct, state)))
alive = np.asarray(st.alive); age = np.asarray(st.age)[alive]
P = int(alive.sum()); J = int((age < C.MIN_REPRO_AGE).sum()); A = P - J
B = float(C.MAX_BIRTHS_PER_STEP); L = float(C.MIN_REPRO_AGE)
lo, hi = 1e-6, 1.0   # resolver J*h = B*(1-exp(-L*h)) para el riesgo juvenil h
for _ in range(200):
    h = (lo + hi) / 2
    if J * h < B * (1 - np.exp(-L * h)): lo = h
    else: hi = h
s = float(np.exp(-L * h)); ha = B * s / max(A, 1)
print(json.dumps({"seed": seed, "pop": P, "juveniles": J, "adults": A, "NEUTRAL_POP": P,
                  "NEUTRAL_DEATH_JUV": round(h, 6), "NEUTRAL_DEATH_ADULT": round(ha, 6), "surv_to_adult": round(s, 4)}))
