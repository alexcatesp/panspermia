from pathlib import Path

p = Path(r"D:\Development\panspermia-fase1b\src\panspermia\island.py")
t = p.read_text(encoding="utf-8")


def rep(old, new):
    global t
    assert t.count(old) == 1, (old[:70], t.count(old))
    t = t.replace(old, new)


rep('''    first_repro_age: jax.Array # int32[N], -1 si no se ha reproducido
''', '''    first_repro_age: jax.Array # int32[N], -1 si no se ha reproducido
    emitted: jax.Array         # f32[N, N_CHEM] Σ sustancias emitidas
    toxic_intake: jax.Array    # Σ alga tóxica ingerida
''')
rep('''    resources: jax.Array    # f32[128, 128]
''', '''    resources: jax.Array    # f32[128, 128]
    chem: jax.Array         # f32[N_CHEM, 128, 128]: nutriente, toxina, feromona
    toxic_type: jax.Array   # int32: 0 = alga A tóxica, 1 = alga B tóxica
''')
rep('''    attacks: jax.Array
    drained: jax.Array
    intake: jax.Array
''', '''    attacks: jax.Array
    drained: jax.Array
    intake: jax.Array
    deaths_poison: jax.Array
    toxic_intake: jax.Array
    nutrient_intake: jax.Array
    toxin_damage: jax.Array
    emitted: jax.Array       # f32[N_CHEM]
    toxic_type: jax.Array
''')
rep('''                    disp=jnp.zeros((n, 2), jnp.float32),
                    first_repro_age=jnp.full((n,), -1, jnp.int32))''', '''                    disp=jnp.zeros((n, 2), jnp.float32),
                    first_repro_age=jnp.full((n,), -1, jnp.int32),
                    emitted=jnp.zeros((n, C.N_CHEM), jnp.float32), toxic_intake=z)''')
rep('''        resources=world.init_resources(env, k[1]),
        alive=alive,''', '''        resources=world.init_resources(env, k[1]),
        chem=jnp.zeros((C.N_CHEM, C.RESOURCE_GRID, C.RESOURCE_GRID), jnp.float32),
        toxic_type=jnp.int32(0),
        alive=alive,''')

rep('''    """sensores → cerebro → física → comer/atacar → energía → muertes → nacimientos → plasticidad → recursos."""
    key = jax.random.fold_in(state.key, state.step)
    k_birth = jax.random.split(key, 2)[0]
    alive0 = state.alive
''', '''    """sensores → cerebro → física → comer/atacar/emitir/toxina → energía → muertes → nacimientos
    → plasticidad → recursos, química y estación."""
    key = jax.random.fold_in(state.key, state.step)
    k_birth, k_flip = jax.random.split(key, 2)
    alive0 = state.alive
''')
rep('''    intake, resources = world.eat(state.resources, pos, alive0, actions)
    signal = jnp.where(alive0, actions[:, 4], 0.0)
    state = state.replace(pos=pos, vel=vel, angle=angle, h=jnp.where(alive0[:, None], h_new, 0.0),
                          signal=signal)
    atk_delta, drained, attempt, resources = world.attack(state, actions, cand, resources)
    energy = world.energy_update(state, thrust, intake, atk_delta, attempt)
''', '''    toxic = world.toxic_cells(state.env, state.step, state.toxic_type)
    gain, intake, toxic_in, nutrient, resources, chem = world.eat(
        state.resources, state.chem, pos, alive0, actions, toxic)
    signal = jnp.where(alive0, actions[:, 4], 0.0)
    state = state.replace(pos=pos, vel=vel, angle=angle, h=jnp.where(alive0[:, None], h_new, 0.0),
                          signal=signal)
    atk_delta, drained, attempt, resources = world.attack(state, actions, cand, resources)
    emit_cost, emitted, chem = world.emit(chem, pos, alive0, actions)
    tox_dmg, chem, resources = world.toxin(chem, resources, pos, alive0, state.energy)
    energy = world.energy_update(state, thrust, gain - emit_cost - tox_dmg, atk_delta, attempt)
''')
rep('''    flags = ((alive0 & (actions[:, 2] > 0)).astype(jnp.uint8) | (attempt.astype(jnp.uint8) << 1)
             | ((drained > 0).astype(jnp.uint8) << 2))
    state = state.replace(
        resources=resources,
        flags=flags,''', '''    flags = ((alive0 & (actions[:, 2] > 0)).astype(jnp.uint8) | (attempt.astype(jnp.uint8) << 1)
             | ((drained > 0).astype(jnp.uint8) << 2) | ((emitted[:, 1] > 0).astype(jnp.uint8) << 3)
             | ((toxic_in > 0).astype(jnp.uint8) << 4))
    state = state.replace(
        resources=resources,
        chem=chem,
        flags=flags,''')
rep('''            disp=bh.disp + f[:, None] * vel * C.DT,
        ),
    )
''', '''            disp=bh.disp + f[:, None] * vel * C.DT,
            emitted=bh.emitted + emitted,
            toxic_intake=bh.toxic_intake + toxic_in,
        ),
    )
''')
rep('''    by_age = died & ~by_attack & (state.age >= C.SENESCENCE_START)
''', '''    by_poison = died & ~by_attack & ((tox_dmg > 0) | (toxic_in > 0))
    by_age = died & ~by_attack & ~by_poison & (state.age >= C.SENESCENCE_START)
''')
rep('''    resources = world.resources_step(state.resources, state.env, state.step)
    state = state.replace(w=w, resources=resources, step=state.step + 1)
''', '''    resources = world.resources_step(state.resources, state.env, state.step)
    chem, resources = world.chem_step(state.chem, resources)
    flip = jax.random.uniform(k_flip) < C.TOXIC_FLIP_PROB
    state = state.replace(w=w, resources=resources, chem=chem, step=state.step + 1,
                          toxic_type=jnp.where(flip, 1 - state.toxic_type, state.toxic_type))
''')
rep('''        deaths_starvation=jnp.sum(died & ~by_attack & ~by_age).astype(jnp.int32),''',
    '''        deaths_starvation=jnp.sum(died & ~by_attack & ~by_age & ~by_poison).astype(jnp.int32),''')
rep('''        drained=jnp.sum(drained),
        intake=jnp.sum(intake),
    )
    return state, stats''', '''        drained=jnp.sum(drained),
        intake=jnp.sum(intake),
        deaths_poison=jnp.sum(by_poison).astype(jnp.int32),
        toxic_intake=jnp.sum(toxic_in),
        nutrient_intake=jnp.sum(nutrient),
        toxin_damage=jnp.sum(tox_dmg),
        emitted=jnp.sum(emitted, axis=0),
        toxic_type=state.toxic_type,
    )
    return state, stats''')
p.write_text(t, encoding="utf-8")
print("island ok")

# --- metrics
p = Path(r"D:\Development\panspermia-fase1b\src\panspermia\metrics.py")
t = p.read_text(encoding="utf-8")
rep('''        "attack_gene_mean": _masked_mean(state.pheno.attack, alive),
    }''', '''        "attack_gene_mean": _masked_mean(state.pheno.attack, alive),
        "deaths_poison": jnp.sum(per_step.deaths_poison),
        "toxic_intake": jnp.sum(per_step.toxic_intake),
        "toxic_intake_frac": jnp.sum(per_step.toxic_intake) / jnp.maximum(jnp.sum(per_step.intake), 1e-9),
        "nutrient_intake": jnp.sum(per_step.nutrient_intake),
        "toxin_damage": jnp.sum(per_step.toxin_damage),
        "toxic_flips": jnp.sum(jnp.abs(jnp.diff(per_step.toxic_type))),
        **{f"emit_{n}": jnp.sum(per_step.emitted[:, i]) for i, n in enumerate(C.CHEM_NAMES)},
        **{f"chem_{n}_total": jnp.sum(state.chem[i]) for i, n in enumerate(C.CHEM_NAMES)},
    }''')
rep('''DESCRIPTOR_NAMES = ("speed", "turn", "intake", "attacks", "signal_entropy", "dispersion",
                    "aggregation", "repro_age")''', '''DESCRIPTOR_NAMES = ("speed", "turn", "intake", "attacks", "signal_entropy", "dispersion",
                    "aggregation", "repro_age", "emit_nutrient", "emit_toxin", "emit_pheromone",
                    "toxic_frac")''')
rep('''        "first_repro_age": b.first_repro_age,
    })''', '''        "first_repro_age": b.first_repro_age, "emitted": b.emitted, "toxic_intake": b.toxic_intake,
    })''')
rep('''        v["neighbors"][m] / age / 10.0,
        repro,
    ], axis=1)''', '''        v["neighbors"][m] / age / 10.0,
        repro,
        *(v["emitted"][m][:, i] / age / (C.EMIT_RATE * C.DT) for i in range(C.N_CHEM)),
        v["toxic_intake"][m] / np.maximum(v["intake"][m], 1e-9),
    ], axis=1)''')
p.write_text(t, encoding="utf-8")
print("metrics ok")
