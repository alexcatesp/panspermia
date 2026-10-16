"""Motor de isla: IslandState, world_step y epoch con lax.scan bajo jit (spec §Motor de isla).

Claves aleatorias: la clave de la isla no cambia; cada paso usa fold_in(key, step), así que el
resultado no depende de cómo se trocee la ejecución en épocas.
"""
from __future__ import annotations

import functools
import math

import jax
import jax.numpy as jnp
from flax import struct

from . import brain, metrics, world
from . import config as C
from . import genome as G
from .develop import Phenotype, develop, develop_batch
from .world import EnvParams

NO_PARENT = 2**32 - 1


@struct.dataclass
class Lineage:
    uid: jax.Array          # uint32[N], identificador de nacimiento dentro de la isla
    parent_uid: jax.Array   # uint32[N]
    birth_step: jax.Array   # int32[N]
    clade: jax.Array        # uint32[N], uid del fundador del clado (nuevo cada CLADE_DEPTH generaciones)


@struct.dataclass
class Behavior:
    """Acumuladores por agente desde su nacimiento para el descriptor conductual (solo observan)."""
    speed: jax.Array           # Σ |v|
    turn: jax.Array            # Σ |giro|
    intake: jax.Array          # Σ ingesta
    attack: jax.Array          # Σ intentos de ataque
    neighbors: jax.Array       # Σ vecinos en alcance (agregación)
    sig_hist: jax.Array        # f32[N, SIGNAL_BINS] histograma de la señal emitida
    disp: jax.Array            # f32[N, 2] desplazamiento acumulado (desenrollado en el toro)
    first_repro_age: jax.Array # int32[N], -1 si no se ha reproducido
    emitted: jax.Array         # f32[N, N_CHEM] Σ sustancias emitidas
    toxic_intake: jax.Array    # Σ alga tóxica ingerida


@struct.dataclass
class IslandState:
    step: jax.Array         # int32 (2^31 pasos ≈ 2·10^6 épocas)
    key: jax.Array          # PRNG de la isla (uint32[2])
    env: EnvParams
    resources: jax.Array    # f32[128, 128]
    chem: jax.Array         # f32[N_CHEM, 128, 128]: nutriente, toxina, feromona
    toxic_type: jax.Array   # int32: 0 = alga A tóxica, 1 = alga B tóxica
    alive: jax.Array        # bool[N]
    pos: jax.Array          # f32[N, 2]
    vel: jax.Array          # f32[N, 2]
    angle: jax.Array        # f32[N]
    energy: jax.Array       # f32[N]
    age: jax.Array          # int32[N]
    signal: jax.Array       # f32[N]
    genome: G.Genome        # eje N delante
    pheno: Phenotype        # f16[N, 134, 69] + escalares de cuerpo
    w: jax.Array            # f32[N, 134, 69]
    h: jax.Array            # f32[N, 64]
    lineage: Lineage
    behavior: Behavior
    comm_hist: jax.Array    # f32[SIGNAL_BINS, CONTEXT_BINS], se reinicia en cada época
    flags: jax.Array        # uint8[N]: 1 come · 2 ataca · 4 atacado (último paso; para el visor)
    next_uid: jax.Array     # uint32


@struct.dataclass
class StepStats:
    population: jax.Array
    births: jax.Array
    deaths_starvation: jax.Array
    deaths_age: jax.Array
    deaths_attack: jax.Array
    attacks: jax.Array
    drained: jax.Array
    intake: jax.Array
    deaths_poison: jax.Array
    toxic_intake: jax.Array
    nutrient_intake: jax.Array
    toxin_damage: jax.Array
    emitted: jax.Array       # f32[N_CHEM]
    toxic_type: jax.Array


def setup_determinism() -> None:
    """Flags de determinismo de la spec. Llamar antes de la primera operación de JAX.

    También desactiva la preasignación del 75 % de la VRAM (en Windows/WSL el escritorio ocupa
    parte de la GPU y la preasignación falla con avisos de OOM).
    """
    import os
    os.environ.setdefault("XLA_PYTHON_CLIENT_PREALLOCATE", "false")
    flags = os.environ.get("XLA_FLAGS", "")
    if "--xla_gpu_deterministic_ops" not in flags:
        os.environ["XLA_FLAGS"] = (flags + " --xla_gpu_deterministic_ops=true").strip()
    jax.config.update("jax_default_matmul_precision", "highest")


def _empty_behavior(n: int) -> Behavior:
    z = jnp.zeros((n,), jnp.float32)
    return Behavior(speed=z, turn=z, intake=z, attack=z, neighbors=z,
                    sig_hist=jnp.zeros((n, C.SIGNAL_BINS), jnp.float32),
                    disp=jnp.zeros((n, 2), jnp.float32),
                    first_repro_age=jnp.full((n,), -1, jnp.int32),
                    emitted=jnp.zeros((n, C.N_CHEM), jnp.float32), toxic_intake=z)


def _place(state: IslandState, idx, genomes, pheno, pos, angle, energy, uid, parent_uid, clade):
    """Ocupa los slots `idx` (índice n = descartar) con agentes recién nacidos."""
    b = idx.shape[0]
    set_ = lambda arr, val: arr.at[idx].set(val, mode="drop")
    fresh = _empty_behavior(b)
    return state.replace(
        alive=set_(state.alive, True),
        pos=set_(state.pos, pos),
        vel=set_(state.vel, 0.0),
        angle=set_(state.angle, angle),
        energy=set_(state.energy, energy),
        age=set_(state.age, 0),
        signal=set_(state.signal, 0.0),
        genome=_scatter(state.genome, idx, genomes),
        pheno=_scatter(state.pheno, idx, pheno),
        w=set_(state.w, pheno.w0.astype(jnp.float32)),
        h=set_(state.h, 0.0),
        lineage=Lineage(
            uid=set_(state.lineage.uid, uid),
            parent_uid=set_(state.lineage.parent_uid, parent_uid),
            birth_step=set_(state.lineage.birth_step, state.step),
            clade=set_(state.lineage.clade, clade),
        ),
        behavior=_scatter(state.behavior, idx, fresh),
    )


def _scatter(tree, idx, new):
    return jax.tree.map(lambda a, b: a.at[idx].set(b.astype(a.dtype), mode="drop"), tree, new)


@functools.partial(jax.jit, static_argnames=("n_max", "n_init"))
def _init(key: jax.Array, env: EnvParams, n_max: int, n_init: int) -> IslandState:
    k = jax.random.split(key, 5)
    genomes = jax.vmap(G.random_minimal)(jax.random.split(k[0], n_max))
    pheno = develop_batch(genomes)
    alive = jnp.arange(n_max) < n_init
    uid = jnp.arange(n_max, dtype=jnp.uint32)
    return IslandState(
        step=jnp.int32(0),
        key=k[4],
        env=env,
        resources=world.init_resources(env, k[1]),
        chem=jnp.zeros((C.N_CHEM, C.RESOURCE_GRID, C.RESOURCE_GRID), jnp.float32),
        toxic_type=jnp.int32(0),
        alive=alive,
        pos=jax.random.uniform(k[2], (n_max, 2), maxval=C.WORLD_L),
        vel=jnp.zeros((n_max, 2)),
        angle=jax.random.uniform(k[3], (n_max,), maxval=2 * math.pi),
        energy=jnp.where(alive, jnp.float32(C.E_INIT), jnp.float32(0.0)),
        age=jnp.zeros((n_max,), jnp.int32),
        signal=jnp.zeros((n_max,)),
        genome=genomes,
        pheno=pheno,
        w=pheno.w0.astype(jnp.float32),
        h=jnp.zeros((n_max, C.N_HIDDEN_MAX)),
        lineage=Lineage(uid=uid, parent_uid=jnp.full((n_max,), jnp.uint32(NO_PARENT)),
                        birth_step=jnp.zeros((n_max,), jnp.int32), clade=uid),
        behavior=_empty_behavior(n_max),
        comm_hist=jnp.zeros((C.SIGNAL_BINS, C.CONTEXT_BINS), jnp.float32),
        flags=jnp.zeros((n_max,), jnp.uint8),
        next_uid=jnp.uint32(n_init),
    )


def init_island(seed: int, node_id: bytes, n_max: int = C.N_MAX, n_init: int = C.N_INIT) -> IslandState:
    """Estado inicial: n_init genomas mínimos aleatorios en n_max slots."""
    if not 0 < n_init <= n_max:
        raise ValueError("se requiere 0 < n_init <= n_max")
    return _init(jax.random.PRNGKey(seed), world.make_env(node_id), n_max, n_init)


def _births(state: IslandState, key: jax.Array):
    """Nacimientos asexuales en slots libres. Devuelve (estado, nº nacimientos, máscara de recién nacidos)."""
    n = state.alive.shape[0]
    b = min(C.MAX_BIRTHS_PER_STEP, n)
    k = jax.random.split(key, 4)
    eligible = (state.alive & (state.energy >= state.pheno.repro_threshold)
                & (state.age >= C.MIN_REPRO_AGE))
    scores = jnp.where(eligible, jax.random.uniform(k[0], (n,)), -1.0)
    top, parents = jax.lax.top_k(scores, b)                        # orden aleatorio determinista
    slots = jnp.nonzero(~state.alive, size=b, fill_value=n)[0]
    valid = (top >= 0) & (slots < n)                               # ambos son prefijos
    n_births = jnp.sum(valid).astype(jnp.int32)

    def do(state: IslandState):
        parent_g = jax.tree.map(lambda x: x[parents], state.genome)
        child_g = jax.vmap(G.mutate)(parent_g, jax.random.split(k[1], b))
        child_p = jax.vmap(develop)(child_g)
        e_child = jnp.where(valid, state.pheno.offspring_frac[parents] * state.energy[parents], 0.0)
        p_idx = jnp.where(valid, parents, n)
        theta = jax.random.uniform(k[2], (b,), maxval=2 * math.pi)
        offset = 2 * state.pheno.radius[parents][:, None] * jnp.stack([jnp.cos(theta), jnp.sin(theta)], -1)
        uid = state.next_uid + jnp.arange(b, dtype=jnp.uint32)
        new_clade = (child_g.generation % C.CLADE_DEPTH) == 0
        clade = jnp.where(new_clade, uid, state.lineage.clade[parents])
        first = state.behavior.first_repro_age
        first = first.at[p_idx].set(jnp.where(first[parents] < 0, state.age[parents], first[parents]),
                                    mode="drop")
        state = state.replace(energy=state.energy.at[p_idx].add(-e_child, mode="drop"),
                              behavior=state.behavior.replace(first_repro_age=first))
        state = _place(state, jnp.where(valid, slots, n), child_g, child_p,
                       (state.pos[parents] + offset) % C.WORLD_L,
                       jax.random.uniform(k[3], (b,), maxval=2 * math.pi), e_child, uid,
                       state.lineage.uid[parents], clade)
        return state.replace(next_uid=state.next_uid + n_births.astype(jnp.uint32))

    newborn = jnp.zeros((n,), bool).at[jnp.where(valid, slots, n)].set(True, mode="drop")
    state = jax.lax.cond(n_births > 0, do, lambda s: s, state)
    return state, n_births, newborn


def _signal_bin(signal: jax.Array) -> jax.Array:
    return jnp.clip(jnp.floor((signal + 1) / 2 * C.SIGNAL_BINS), 0, C.SIGNAL_BINS - 1).astype(jnp.int32)


def _context(obs: jax.Array) -> jax.Array:
    """0 nada · 1 comida delante · 2 pariente visto · 3 no pariente visto."""
    rays = obs[:, :C.N_RAYS * C.RAY_CHANNELS].reshape(-1, C.N_RAYS, C.RAY_CHANNELS)
    kin = jnp.max(rays[..., 2], axis=1)
    mid = C.N_RAYS // 2
    food = jnp.mean(rays[:, mid - 1:mid + 1, 1], axis=1) >= C.FOOD_AHEAD_THRESHOLD
    return jnp.where(kin >= C.KIN_THRESHOLD, 2, jnp.where(kin > 0, 3, jnp.where(food, 1, 0)))


def world_step(state: IslandState, _=None, *, plastic: bool = True, births: bool = True,
               control: jax.Array | None = None):
    """sensores → cerebro → física → comer/atacar/emitir/toxina → energía → muertes → nacimientos
    → plasticidad → recursos, química y estación.

    `control` (solo pruebas de capacidad, ADR-011): f32[3] = (activo, empuje, giro). Si activo > 0,
    las acciones del cerebro se sustituyen por una política fija sin cerebro (empuje y giro
    constantes, comer siempre, sin atacar, señalizar ni emitir). Con None la dinámica no cambia."""
    key = jax.random.fold_in(state.key, state.step)
    k_birth, k_flip = jax.random.split(key, 2)
    alive0 = state.alive

    cand = world.neighbors(state.pos, alive0)
    obs, n_near = world.sense(state, cand)
    actions, h_new, pre, post = brain.step(state.w, state.h, obs, state.genome.hid_mask)
    if control is not None:
        fixed = jnp.zeros_like(actions).at[:, 0].set(control[1]).at[:, 1].set(control[2]).at[:, 2].set(1.0)
        actions = jnp.where(control[0] > 0, fixed, actions)
    pos, vel, angle, thrust = world.physics(state, actions, cand)
    toxic = world.toxic_cells(state.env, state.step, state.toxic_type)
    toxicity = jnp.clip(state.step.astype(jnp.float32) / C.TOXIC_RAMP_STEPS, 0.0, 1.0)
    gain, intake, toxic_in, nutrient, resources, chem = world.eat(
        state.resources, state.chem, pos, alive0, actions, toxic, toxicity)
    signal = jnp.where(alive0, actions[:, 4], 0.0)
    state = state.replace(pos=pos, vel=vel, angle=angle, h=jnp.where(alive0[:, None], h_new, 0.0),
                          signal=signal)
    atk_delta, drained, attempt, resources = world.attack(state, actions, cand, resources)
    emit_cost, emitted, chem = world.emit(chem, pos, alive0, actions)
    tox_dmg, chem, resources = world.toxin(chem, resources, pos, alive0, state.energy)
    energy = world.energy_update(state, thrust, gain - emit_cost - tox_dmg, atk_delta, attempt)

    # Observación (no afecta a la dinámica): conducta acumulada y comunicación
    f = alive0.astype(jnp.float32)
    bh = state.behavior
    sbin = _signal_bin(signal)
    joint = sbin * C.CONTEXT_BINS + _context(obs)
    comm = jax.ops.segment_sum(f, joint, num_segments=C.SIGNAL_BINS * C.CONTEXT_BINS)
    flags = ((alive0 & (actions[:, 2] > 0)).astype(jnp.uint8) | (attempt.astype(jnp.uint8) << 1)
             | ((drained > 0).astype(jnp.uint8) << 2) | ((emitted[:, 1] > 0).astype(jnp.uint8) << 3)
             | ((toxic_in > 0).astype(jnp.uint8) << 4))
    state = state.replace(
        resources=resources,
        chem=chem,
        flags=flags,
        comm_hist=state.comm_hist + comm.reshape(C.SIGNAL_BINS, C.CONTEXT_BINS),
        behavior=bh.replace(
            speed=bh.speed + f * jnp.linalg.norm(vel, axis=-1),
            turn=bh.turn + f * jnp.abs(actions[:, 1]),
            intake=bh.intake + intake,
            attack=bh.attack + attempt.astype(jnp.float32),
            neighbors=bh.neighbors + f * n_near,
            sig_hist=bh.sig_hist + f[:, None] * jax.nn.one_hot(sbin, C.SIGNAL_BINS),
            disp=bh.disp + f[:, None] * vel * C.DT,
            emitted=bh.emitted + emitted,
            toxic_intake=bh.toxic_intake + toxic_in,
        ),
    )

    died = alive0 & (energy <= 0)
    by_attack = died & (drained > 0)
    # veneno: sin la toxina ni la pérdida neta por alga tóxica de este paso habría sobrevivido
    # (la intoxicación lenta, repartida en muchos pasos, cuenta como hambre)
    toxic_loss = jnp.maximum(toxic_in * (toxicity * (1.0 + C.TOXIC_FACTOR) - 1.0), 0.0)
    by_poison = died & ~by_attack & (energy + tox_dmg + toxic_loss > 0)
    by_age = died & ~by_attack & ~by_poison & (state.age >= C.SENESCENCE_START)
    alive = alive0 & ~died
    state = state.replace(energy=jnp.where(alive, energy, 0.0), alive=alive,
                          age=jnp.where(alive, state.age + 1, 0))

    if births:
        state, n_births, newborn = _births(state, k_birth)
    else:
        n_births, newborn = jnp.int32(0), jnp.zeros_like(alive)

    if plastic:
        def plastic_fn(w):
            m = brain.modulation(h_new, state.genome.hid_mask, state.genome.hid_type)
            m = jnp.where(state.alive & ~newborn, m, 0.0)
            return brain.plasticity(state.pheno, w, pre, post, m)

        w = jax.lax.cond(state.step % C.PLASTICITY_EVERY == 0, plastic_fn, lambda w: w, state.w)
    else:
        w = state.w
    resources = world.resources_step(state.resources, state.env, state.step)
    chem, resources = world.chem_step(state.chem, resources)
    flip = jax.random.uniform(k_flip) < C.TOXIC_FLIP_PROB
    state = state.replace(w=w, resources=resources, chem=chem, step=state.step + 1,
                          toxic_type=jnp.where(flip, 1 - state.toxic_type, state.toxic_type))

    stats = StepStats(
        population=jnp.sum(state.alive).astype(jnp.int32),
        births=n_births,
        deaths_starvation=jnp.sum(died & ~by_attack & ~by_age & ~by_poison).astype(jnp.int32),
        deaths_age=jnp.sum(by_age).astype(jnp.int32),
        deaths_attack=jnp.sum(by_attack).astype(jnp.int32),
        attacks=jnp.sum(attempt).astype(jnp.int32),
        drained=jnp.sum(drained),
        intake=jnp.sum(intake),
        deaths_poison=jnp.sum(by_poison).astype(jnp.int32),
        toxic_intake=jnp.sum(toxic_in),
        nutrient_intake=jnp.sum(nutrient),
        toxin_damage=jnp.sum(tox_dmg),
        emitted=jnp.sum(emitted, axis=0),
        toxic_type=state.toxic_type,
    )
    return state, stats


@functools.partial(jax.jit, static_argnames=("k", "plastic"), donate_argnums=(0,))
def epoch(state: IslandState, k: int = C.EPOCH_STEPS, plastic: bool = True):
    """Ejecuta k pasos y devuelve (state, EpochStats). `plastic=False` congela el aprendizaje."""
    state = state.replace(comm_hist=jnp.zeros_like(state.comm_hist))
    step = functools.partial(world_step, plastic=plastic)
    state, per_step = jax.lax.scan(step, state, None, length=k)
    return state, metrics.epoch_stats(state, per_step)


@functools.partial(jax.jit, static_argnames=("count",), donate_argnums=(0,))
def reinject(state: IslandState, count: int = C.N_MIN_REINJECT) -> IslandState:
    """Reinyecta hasta `count` genomas mínimos en slots libres (fase 0: sin archivo todavía)."""
    n = state.alive.shape[0]
    key = jax.random.fold_in(jax.random.fold_in(state.key, 0xFFFFFFFF), state.step)
    k = jax.random.split(key, 4)
    slots = jnp.nonzero(~state.alive, size=count, fill_value=n)[0]
    valid = slots < n
    g = jax.vmap(G.random_minimal)(jax.random.split(k[0], count))
    uid = state.next_uid + jnp.arange(count, dtype=jnp.uint32)
    state = _place(state, jnp.where(valid, slots, n), g, develop_batch(g),
                   jax.random.uniform(k[1], (count, 2), maxval=C.WORLD_L),
                   jax.random.uniform(k[2], (count,), maxval=2 * math.pi),
                   jnp.full((count,), C.E_INIT, jnp.float32), uid,
                   jnp.full((count,), jnp.uint32(NO_PARENT)), uid)
    return state.replace(next_uid=state.next_uid + jnp.sum(valid).astype(jnp.uint32))
