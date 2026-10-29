from pathlib import Path

ROOT = Path("D:/Development/panspermia-escalera")


def sub(p, old, new, count=1):
    f = ROOT / p
    s = f.read_text(encoding="utf-8")
    assert s.count(old) == count, (p, old[:70], s.count(old))
    f.write_text(s.replace(old, new), encoding="utf-8")


c = "src/panspermia/config.py"
sub(c, 'SUBSTRATE_VERSION = "2.0.0"  # major distinto => migrantes rechazados (2.x: química + algas estacionales, ADR-008)',
    'SUBSTRATE_VERSION = "2.1.0"  # major distinto => migrantes rechazados (2.x: química + algas estacionales, ADR-008;\n'
    '                             # 2.1: interruptores de la escalera de complejidad en EnvParams, ADR-014)')
sub(c, "# Curva de recuperación (diseño 1d v0.5)",
    """# Escalera de complejidad (ADR-014, docs/escalera/diseno.md): interruptores del mundo por condición.
# Sus valores por defecto dejan el mundo de siempre; cada peldaño enciende una sola cosa más.
REPRO_MODES = {"energia": 0, "edad": 1}
# energia: se reproduce quien supera su umbral de energía y le cede una fracción al hijo (spec).
# edad (peldaños 0 y 1, sin comida): todo adulto (edad >= MIN_REPRO_AGE) puede tener un hijo si hay
# hueco; el hijo nace con E_INIT nueva y el padre no paga nada.
NO_MAX_AGE = 2**30                    # sin vida máxima fija
LADDER_LIFESPAN = 600                 # peldaño 0: vida fija = la de un bicho quieto que solo paga el
                                      # gasto basal en el peldaño 1 (E_INIT / C_BASAL / DT)
# Curva de recuperación (diseño 1d v0.5)""")

w = "src/panspermia/world.py"
sub(w, "    clock_period: jax.Array  # f32: periodo del reloj interno de los agentes (pasos)\n",
    """    clock_period: jax.Array  # f32: periodo del reloj interno de los agentes (pasos)
    # Escalera de complejidad (ADR-014). Por defecto, el mundo de siempre. La comida se apaga con
    # k_mean = 0 y se deja quieta con drift = 0; el veneno, con seasonal = 0.
    metabolism: jax.Array  # f32: 1 = vivir y moverse cuestan energía; 0 = gratis (peldaño 0)
    max_age: jax.Array     # i32: muerte segura a esta edad (pasos); NO_MAX_AGE = sin límite
    repro_mode: jax.Array  # i32: C.REPRO_MODES
    attack_on: jax.Array   # f32: 0 = nadie puede atacar (ni paga por intentarlo)
    chem_on: jax.Array     # f32: 0 = no se emiten sustancias
    signal_on: jax.Array   # f32: 0 = la señal no se emite (todos ven y oyen 0)
""")
sub(w, "        clock_period=jnp.float32(C.CLOCK_PERIOD),\n    )",
    """        clock_period=jnp.float32(C.CLOCK_PERIOD),
        metabolism=jnp.float32(1.0),
        max_age=jnp.int32(C.NO_MAX_AGE),
        repro_mode=jnp.int32(C.REPRO_MODES["energia"]),
        attack_on=jnp.float32(1.0),
        chem_on=jnp.float32(1.0),
        signal_on=jnp.float32(1.0),
    )""")
sub(w, """    if "tox_period" in kw and not float(kw["tox_period"]) >= 2.0:
        raise ValueError("tox_period debe ser >= 2 pasos")
""", """    if "tox_period" in kw and not float(kw["tox_period"]) >= 2.0:
        raise ValueError("tox_period debe ser >= 2 pasos")
    if "repro_mode" in kw:
        mode = kw["repro_mode"]
        kw["repro_mode"] = C.REPRO_MODES.get(mode, -1) if isinstance(mode, str) else int(mode)
        if kw["repro_mode"] not in C.REPRO_MODES.values():
            raise ValueError(f"repro_mode inválido: {mode}")
    if "max_age" in kw and not 1 <= int(kw["max_age"]) <= C.NO_MAX_AGE:
        raise ValueError("max_age debe estar en [1, NO_MAX_AGE]")
    for k in ("metabolism", "attack_on", "chem_on", "signal_on"):
        if k in kw and float(kw[k]) not in (0.0, 1.0):
            raise ValueError(f"{k} debe ser 0 o 1")
    if "k_mean" in kw and not float(kw["k_mean"]) >= 0.0:
        raise ValueError("k_mean debe ser >= 0")
""")
sub(w, '''def emit(chem: jax.Array, pos: jax.Array, alive: jax.Array, actions: jax.Array):
    """Emisión en la celda propia. Devuelve (coste energético, emitido [N, N_CHEM], química)."""
    rate = jax.nn.relu(actions[:, 5:5 + C.N_CHEM]) * C.EMIT_RATE * C.DT
    amount = jnp.where(alive[:, None], rate, 0.0)''',
    '''def emit(chem: jax.Array, pos: jax.Array, alive: jax.Array, actions: jax.Array,
         on: jax.Array | float = 1.0):
    """Emisión en la celda propia. Devuelve (coste energético, emitido [N, N_CHEM], química).
    Con `on` = 0 (escalera) nadie emite ni paga."""
    rate = jax.nn.relu(actions[:, 5:5 + C.N_CHEM]) * C.EMIT_RATE * C.DT
    amount = jnp.where(alive[:, None] & (on > 0), rate, 0.0)''')
sub(w, "    attempt = state.alive & (actions[:, 3] > 0)\n",
    "    attempt = state.alive & (actions[:, 3] > 0) & (state.env.attack_on > 0)\n")
sub(w, '''    """E += ingesta ± ataque − (c0·senescencia + cb·n_neuronas + cs·masa + cm·|empuje|² + ca·ataque)·dt."""''',
    '''    """E += ingesta ± ataque − (c0·senescencia + cb·n_neuronas + cs·masa + cm·|empuje|² + ca·ataque)·dt.
    Con env.metabolism = 0 (peldaño 0 de la escalera) vivir no cuesta nada."""''')
sub(w, "            + C.C_MOVE * thrust ** 2 + C.C_ATTACK * ph.attack * attempt)\n",
    "            + C.C_MOVE * thrust ** 2 + C.C_ATTACK * ph.attack * attempt) * state.env.metabolism\n")

i = "src/panspermia/island.py"
sub(i, """    eligible = (state.alive & (state.energy >= state.pheno.repro_threshold)
                & (state.age >= C.MIN_REPRO_AGE))""",
    """    by_age = state.env.repro_mode == C.REPRO_MODES["edad"]  # escalera, peldaños 0 y 1
    eligible = (state.alive & (by_age | (state.energy >= state.pheno.repro_threshold))
                & (state.age >= C.MIN_REPRO_AGE))""")
sub(i, """        e_child = jnp.where(valid, state.pheno.offspring_frac[parents] * state.energy[parents], 0.0)""",
    """        e_split = state.pheno.offspring_frac[parents] * state.energy[parents]
        e_child = jnp.where(valid, jnp.where(by_age, jnp.float32(C.E_INIT), e_split), 0.0)
        e_paid = jnp.where(by_age, 0.0, e_child)  # en modo «edad» el padre no paga""")
sub(i, '        state = state.replace(energy=state.energy.at[p_idx].add(-e_child, mode="drop"),',
    '        state = state.replace(energy=state.energy.at[p_idx].add(-e_paid, mode="drop"),')
sub(i, "    signal = jnp.where(alive0, actions[:, 4], 0.0)\n",
    "    signal = jnp.where(alive0 & (state.env.signal_on > 0), actions[:, 4], 0.0)\n")
sub(i, "    emit_cost, emitted, chem = world.emit(chem, pos, alive0, actions)\n",
    "    emit_cost, emitted, chem = world.emit(chem, pos, alive0, actions, state.env.chem_on)\n")
sub(i, """    died = alive0 & (energy <= 0)
    age_at_death = state.age
    by_attack = died & (drained > 0)""",
    """    old = alive0 & (state.age >= state.env.max_age)  # vida fija (escalera, peldaño 0)
    died = alive0 & ((energy <= 0) | old)
    age_at_death = state.age
    by_attack = died & ~old & (drained > 0)""")
sub(i, "    by_poison = died & ~by_attack & (energy + tox_dmg + toxic_loss > 0)\n"
       "    by_age = died & ~by_attack & ~by_poison & (state.age >= C.SENESCENCE_START)\n",
    "    by_poison = died & ~old & ~by_attack & (energy + tox_dmg + toxic_loss > 0)\n"
    "    by_age = died & ~by_attack & ~by_poison & (old | (state.age >= C.SENESCENCE_START))\n")
sub(i, "    recov_toxic: jax.Array    # f32[len(RECOVERY_EDGES) + 1]: alga tóxica ingerida, ídem\n",
    "    recov_toxic: jax.Array    # f32[len(RECOVERY_EDGES) + 1]: alga tóxica ingerida, ídem\n"
    "    thrust: jax.Array         # Σ |empuje| de los vivos (escalera: ¿dejan de moverse?)\n")
sub(i, "        recov_toxic=recov_toxic,\n    )",
    "        recov_toxic=recov_toxic,\n        thrust=jnp.sum(jnp.abs(thrust)),\n    )")

m = "src/panspermia/metrics.py"
sub(m, '        "recov_toxic": jnp.sum(per_step.recov_toxic, axis=0),\n',
    '''        "recov_toxic": jnp.sum(per_step.recov_toxic, axis=0),
        # escalera (ADR-014): movimiento real y cuerpo (solo observan)
        "thrust_mean": jnp.sum(per_step.thrust) / jnp.maximum(jnp.sum(per_step.population), 1),
        "mass_mean": _masked_mean(state.pheno.mass, alive),
        "max_thrust_mean": _masked_mean(state.pheno.max_thrust, alive),
''')
print("ok")
