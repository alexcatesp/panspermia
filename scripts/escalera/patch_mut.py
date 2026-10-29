import json
from pathlib import Path

ROOT = Path("D:/Development/panspermia-mut")


def sub(p, old, new):
    f = ROOT / p
    s = f.read_text(encoding="utf-8")
    assert s.count(old) == 1, (p, old[:70], s.count(old))
    f.write_text(s.replace(old, new), encoding="utf-8", newline="\n")


sub("src/panspermia/config.py",
    'SUBSTRATE_VERSION = "2.1.0"  # major distinto => migrantes rechazados (2.x: química + algas estacionales, ADR-008;\n'
    '                             # 2.1: interruptores de la escalera de complejidad en EnvParams, ADR-014)',
    'SUBSTRATE_VERSION = "2.2.0"  # major distinto => migrantes rechazados (2.x: química + algas estacionales, ADR-008;\n'
    '                             # 2.1: interruptores de la escalera de complejidad en EnvParams, ADR-014;\n'
    '                             # 2.2: física de la mutación de neuronas elegible, ADR-015)')
sub("src/panspermia/config.py", "NEURON_MOVE_SIGMA = 0.05\n", """NEURON_MOVE_SIGMA = 0.05
# Física de la mutación del número de neuronas (ADR-015, docs/bibliografia/escalera/):
# - "nest" (spec v1, por defecto): «expresar o silenciar» invierte un hueco elegido al azar entre los
#   64 y «duplicar» solo suma. Sin selección deriva hacia ~43 neuronas (sesgo entrópico, visto en P0).
# - "neutral": primero se decide encender o apagar (mitad y mitad) y luego a qué neurona; «perder
#   neurona» compensa a «duplicar» con la misma tasa. Sin selección, el tamaño no tiene rumbo.
# - "terrestre": se pierde el doble de lo que se gana, como el sesgo de deleción de la Tierra
#   (Kuo y Ochman 2009): 1/3 de los cambios encienden y «perder» es el doble de «duplicar».
NEURON_MUTATION = "nest"
NEURON_MUTATION_P_ON = {"neutral": 0.5, "terrestre": 1 / 3}
P_DEL_NEURON = {"neutral": 0.01, "terrestre": 0.02}
""")

sub("src/panspermia/genome.py", """    # Expresar o silenciar neurona oculta
    kk = jax.random.split(ks[20], 8)
    h = jax.random.randint(kk[0], (), 0, C.N_HIDDEN_MAX)
    do = happens(kk[1], C.P_TOGGLE_NEURON)
    hid_mask = hid_mask.at[h].set(jnp.where(do, ~hid_mask[h], hid_mask[h]))
""", """    # Expresar o silenciar neurona oculta (física elegible, ADR-015; "nest" es la de la spec v1)
    kk = jax.random.split(ks[20], 8)
    mode = C.NEURON_MUTATION
    if mode == "nest":  # invierte un hueco al azar: deriva hacia la mitad sin selección
        h = jax.random.randint(kk[0], (), 0, C.N_HIDDEN_MAX)
        do = happens(kk[1], C.P_TOGGLE_NEURON)
        hid_mask = hid_mask.at[h].set(jnp.where(do, ~hid_mask[h], hid_mask[h]))
    elif mode in C.NEURON_MUTATION_P_ON:  # primero encender o apagar; después a qué neurona
        kn = jax.random.split(jax.random.fold_in(ks[20], 0x6E6575), 3)
        on = jax.random.uniform(kn[0]) < C.NEURON_MUTATION_P_ON[mode]
        h_off, ok_off = _choose(kn[1], ~hid_mask)
        h_on, ok_on = _choose(kn[2], hid_mask)
        h = jnp.where(on, h_off, h_on)
        do = happens(kk[1], C.P_TOGGLE_NEURON) & jnp.where(on, ok_off, ok_on)
        hid_mask = hid_mask.at[h].set(jnp.where(do, on, hid_mask[h]))
    else:
        raise ValueError(f"NEURON_MUTATION desconocida: {mode}")
""")
sub("src/panspermia/genome.py", """    hid_type = hid_type.at[dst].set(jnp.where(do, hid_type[src], hid_type[dst]))
""", """    hid_type = hid_type.at[dst].set(jnp.where(do, hid_type[src], hid_type[dst]))

    if mode != "nest":  # perder neurona: la otra cara de duplicar (Lynch y Conery 2000)
        kd = jax.random.split(jax.random.fold_in(ks[20], 0x64656C), 2)
        victim, ok_v = _choose(kd[0], hid_mask)
        do = happens(kd[1], C.P_DEL_NEURON[mode]) & ok_v
        hid_mask = hid_mask.at[victim].set(jnp.where(do, False, hid_mask[victim]))
""")
sub("src/panspermia/experiment.py", '"FROZEN_PLASTICITY_TEST_EVERY", "CHECKPOINT_EVERY", "VIDEO_EVERY", "CAPABILITY_TEST_EVERY",',
    '"FROZEN_PLASTICITY_TEST_EVERY", "CHECKPOINT_EVERY", "VIDEO_EVERY", "CAPABILITY_TEST_EVERY",\n    "NEURON_MUTATION",')

esc = json.loads((ROOT / "experiments/fase1d/escalera.json").read_text(encoding="utf-8"))
base = {s["name"]: s for s in esc}
names = {"neutral": "mutación neutral (encender o apagar mitad y mitad; perder = duplicar)",
         "terrestre": "mutación terrestre (se pierde el doble de lo que se gana)"}
queue = []
for rung, src in (("P0", "P0-feliz"), ("P1", "P1-peaje")):
    for mode in ("neutral", "terrestre"):
        s = json.loads(json.dumps(base[src]))
        s["name"] = f"{src}-{mode}"
        s["block"] = "MUT"
        s["description"] = f"{base[src]['description']} Rama ADR-015: {names[mode]}."
        s["config"] = {**s.get("config", {}), "NEURON_MUTATION": mode}
        queue.append(s)
(ROOT / "experiments/fase1d/mutacion.json").write_text(json.dumps(queue, indent=1, ensure_ascii=False) + "\n",
                                                       encoding="utf-8", newline="\n")
print("ok", [q["name"] for q in queue])
