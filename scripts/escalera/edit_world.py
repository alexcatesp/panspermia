from pathlib import Path

p = Path(r"D:\Development\panspermia-fase1b\src\panspermia\world.py")
t = p.read_text(encoding="utf-8")


def rep(old, new):
    global t
    assert t.count(old) == 1, (old[:70], t.count(old))
    t = t.replace(old, new)


rep('''    regrow: jax.Array      # f32: 1 en las islas; 0 congela el campo (entornos de prueba)
    walls: jax.Array       # bool[RES, RES]
''', '''    regrow: jax.Array      # f32: 1 en las islas; 0 congela el campo (entornos de prueba)
    walls: jax.Array       # bool[RES, RES]
    type_phase: jax.Array  # f32[K_WAVES]: fases del campo que decide el tipo de alga (A/B)
    seasonal: jax.Array    # f32: 1 en las islas; 0 desactiva las algas tóxicas (pruebas)
''')
rep('''        regrow=jnp.float32(1.0),
        walls=jnp.zeros((RES, RES), bool),
    )
''', '''        regrow=jnp.float32(1.0),
        walls=jnp.zeros((RES, RES), bool),
        type_phase=jax.random.uniform(k[6], (C.K_WAVES,), maxval=2 * math.pi),
        seasonal=jnp.float32(1.0),
    )
''')
rep('''def init_resources(env: EnvParams, key: jax.Array) -> jax.Array:''', '''def algae_type_a(env: EnvParams, step: jax.Array) -> jax.Array:
    """bool[RES, RES]: True donde el alga es de tipo A (manchas que derivan con el mundo)."""
    t = step.astype(jnp.float32) * C.DT
    cx, cy = jnp.meshgrid(_RES_CENTERS, _RES_CENTERS, indexing="ij")
    phase = (2 * math.pi * (env.wave_k[:, 0, None, None] * cx + env.wave_k[:, 1, None, None] * cy)
             + env.type_phase[:, None, None] + env.drift * env.wave_speed[:, None, None] * t)
    return jnp.sum(env.wave_amp[:, None, None] * jnp.sin(phase), axis=0) > 0


def toxic_cells(env: EnvParams, step: jax.Array, toxic_type: jax.Array) -> jax.Array:
    """bool[RES, RES]: celdas cuya alga es tóxica ahora (toxic_type 0 = A, 1 = B)."""
    a = algae_type_a(env, step)
    return (env.seasonal > 0) & jnp.where(toxic_type == 0, a, ~a)


def init_resources(env: EnvParams, key: jax.Array) -> jax.Array:''')

rep('''    res = state.resources.ravel()[_res_index(pts % L)]
    res = jnp.mean(res, axis=-1) / C.K_MEAN
''', '''    idx = _res_index(pts % L)
    sign = jnp.where(algae_type_a(state.env, state.step).ravel()[idx], 1.0, -1.0)
    res = jnp.mean(state.resources.ravel()[idx] * sign, axis=-1) / C.K_MEAN
''')
rep('''    obs = jnp.concatenate([rays, own], axis=-1)''',
    '''    obs = jnp.concatenate([rays, own, sense_chem(state.chem, state.pos, heading, lateral)], axis=-1)''')

rep('''# ---------------------------------------------------------------------------------------------
# Física
# ---------------------------------------------------------------------------------------------
''', '''def sense_chem(chem: jax.Array, pos: jax.Array, heading: jax.Array, lateral: jax.Array) -> jax.Array:
    """[N, 3·N_CHEM]: por sustancia, concentración local y gradientes adelante y lateral."""
    g = C.CHEM_GRAD_DIST
    flat = chem.reshape(C.N_CHEM, -1)

    def at(p):
        return flat[:, _res_index(p % L)]  # [N_CHEM, N]

    local = at(pos)
    fwd = at(pos + g * heading) - at(pos - g * heading)
    lat = at(pos + g * lateral) - at(pos - g * lateral)
    s = C.CHEM_OBS_SCALE
    return jnp.concatenate([jnp.tanh(local / s), jnp.tanh(fwd / s), jnp.tanh(lat / s)], axis=0).T


# ---------------------------------------------------------------------------------------------
# Física
# ---------------------------------------------------------------------------------------------
''')

rep('''def eat(resources: jax.Array, pos: jax.Array, alive: jax.Array, actions: jax.Array):
    """Ingesta en la celda de recursos bajo el centro; reparto proporcional si falta comida."""
    demand = jnp.where(alive & (actions[:, 2] > 0), C.EAT_RATE * C.DT, 0.0)
    cell = _res_index(pos)
    flat = resources.ravel()
    total = jax.ops.segment_sum(demand, cell, num_segments=RES * RES)
    scale = jnp.minimum(1.0, flat / jnp.maximum(total, 1e-9))
    intake = demand * scale[cell]
    eaten = jax.ops.segment_sum(intake, cell, num_segments=RES * RES)
    return intake, jnp.maximum(flat - eaten, 0.0).reshape(RES, RES)
''', '''def _take(field: jax.Array, demand: jax.Array, cell: jax.Array):
    """Reparto proporcional de un campo [RES, RES] entre demandas por agente."""
    flat = field.ravel()
    total = jax.ops.segment_sum(demand, cell, num_segments=RES * RES)
    scale = jnp.minimum(1.0, flat / jnp.maximum(total, 1e-9))
    got = demand * scale[cell]
    taken = jax.ops.segment_sum(got, cell, num_segments=RES * RES)
    return got, jnp.maximum(flat - taken, 0.0).reshape(RES, RES)


def eat(resources: jax.Array, chem: jax.Array, pos: jax.Array, alive: jax.Array,
        actions: jax.Array, toxic: jax.Array):
    """Comer: alga y nutriente de la celda bajo el centro, con reparto proporcional.

    El alga tóxica resta TOXIC_FACTOR × lo ingerido en vez de sumarlo (no conservativo: es veneno).
    Devuelve (ganancia de energía, alga ingerida, alga tóxica ingerida, nutriente, recursos, química).
    """
    demand = jnp.where(alive & (actions[:, 2] > 0), C.EAT_RATE * C.DT, 0.0)
    cell = _res_index(pos)
    algae, resources = _take(resources, demand, cell)
    nutrient, nut_field = _take(chem[0], demand, cell)
    toxic_in = jnp.where(toxic.ravel()[cell], algae, 0.0)
    gain = algae - (1.0 + C.TOXIC_FACTOR) * toxic_in + nutrient
    return gain, algae, toxic_in, nutrient, resources, chem.at[0].set(nut_field)


def emit(chem: jax.Array, pos: jax.Array, alive: jax.Array, actions: jax.Array):
    """Emisión en la celda propia. Devuelve (coste energético, emitido [N, N_CHEM], química)."""
    rate = jax.nn.relu(actions[:, 5:5 + C.N_CHEM]) * C.EMIT_RATE * C.DT
    amount = jnp.where(alive[:, None], rate, 0.0)
    cell = _res_index(pos)
    added = jax.vmap(lambda a: jax.ops.segment_sum(a, cell, num_segments=RES * RES))(amount.T)
    cost = amount @ jnp.asarray(C.EMIT_COST, jnp.float32)
    return cost, amount, chem + added.reshape(C.N_CHEM, RES, RES)


def toxin(chem: jax.Array, resources: jax.Array, pos: jax.Array, alive: jax.Array,
          energy: jax.Array):
    """La toxina drena energía de los agentes de su celda y se consume en la misma cantidad.

    Lo drenado y la toxina consumida se depositan como alga (energía conservada).
    Devuelve (daño [N], química, recursos).
    """
    cell = _res_index(pos)
    t_here = chem[1].ravel()[cell]
    want = jnp.minimum(C.TOXIN_DAMAGE * t_here * C.DT, jnp.maximum(energy, 0.0))
    damage, t_left = _take(chem[1], jnp.where(alive, want, 0.0), cell)
    dealt = jax.ops.segment_sum(damage, cell, num_segments=RES * RES).reshape(RES, RES)
    return damage, chem.at[1].set(t_left), resources + 2.0 * dealt


def chem_step(chem: jax.Array, resources: jax.Array):
    """Difusión (laplaciano de 5 puntos en el toro) y degradación. Nutriente y toxina degradados
    vuelven al campo como alga; la feromona se disipa."""
    lap = (jnp.roll(chem, 1, 1) + jnp.roll(chem, -1, 1) + jnp.roll(chem, 1, 2)
           + jnp.roll(chem, -1, 2) - 4 * chem)
    diff = jnp.asarray(C.CHEM_DIFFUSION, jnp.float32)[:, None, None]
    decay = jnp.asarray(C.CHEM_DECAY, jnp.float32)[:, None, None]
    chem = jnp.maximum(chem + diff * lap * C.DT, 0.0)
    lost = chem * decay * C.DT
    return chem - lost, resources + lost[0] + lost[1]
''')
p.write_text(t, encoding="utf-8")
print("world ok")
