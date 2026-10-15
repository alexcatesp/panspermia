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


@struct.dataclass
class Lineage:
    uid: jax.Array          # uint32[N], identificador de nacimiento dentro de la isla
    parent_uid: jax.Array   # uint32[N]
    birth_step: jax.Array   # int32[N]


@struct.dataclass
class IslandState:
    step: jax.Array         # int32 (2^31 pasos ≈ 2·10^6 épocas)
    key: jax.Array          # PRNG de la isla (uint32[2])
    env: EnvParams
    resources: jax.Array    # f32[128, 128]
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
    next_uid: jax.Array     # uint32


@struct.dataclass
class StepStats:
    population: jax.Array
    births: jax.Array
    deaths_starvation: jax.Array
    deaths_age: jax.Array
    intake: jax.Array


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


@functools.partial(jax.jit, static_argnames=("n_max", "n_init"))
def _init(key: jax.Array, env: EnvParams, n_max: int, n_init: int) -> IslandState:
    k = jax.random.split(key, 5)
    genomes = jax.vmap(G.random_minimal)(jax.random.split(k[0], n_max))
    pheno = develop_batch(genomes)
    alive = jnp.arange(n_max) < n_init
    return IslandState(
        step=jnp.int32(0),
        key=k[4],
        env=env,
        resources=world.init_resources(env, k[1]),
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
        lineage=Lineage(
            uid=jnp.arange(n_max, dtype=jnp.uint32),
            parent_uid=jnp.full((n_max,), jnp.uint32(2**32 - 1)),
            birth_step=jnp.zeros((n_max,), jnp.int32),
        ),
        next_uid=jnp.uint32(n_init),
    )


def init_island(seed: int, node_id: bytes, n_max: int = C.N_MAX, n_init: int = C.N_INIT) -> IslandState:
    """Estado inicial: n_init genomas mínimos aleatorios en n_max slots."""
    if not 0 < n_init <= n_max:
        raise ValueError("se requiere 0 < n_init <= n_max")
    return _init(jax.random.PRNGKey(seed), world.make_env(node_id), n_max, n_init)


def _scatter(tree, idx, new):
    return jax.tree.map(lambda a, b: a.at[idx].set(b.astype(a.dtype), mode="drop"), tree, new)


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
        child_keys = jax.random.split(k[1], b)
        parent_g = jax.tree.map(lambda x: x[parents], state.genome)
        child_g = jax.vmap(G.mutate)(parent_g, child_keys)
        child_p = jax.vmap(develop)(child_g)
        e_child = jnp.where(valid, state.pheno.offspring_frac[parents] * state.energy[parents], 0.0)
        p_idx = jnp.where(valid, parents, n)
        energy = state.energy.at[p_idx].add(-e_child, mode="drop")
        theta = jax.random.uniform(k[2], (b,), maxval=2 * math.pi)
        offset = 2 * state.pheno.radius[parents][:, None] * jnp.stack([jnp.cos(theta), jnp.sin(theta)], -1)
        pos = (state.pos[parents] + offset) % C.WORLD_L
        c_idx = jnp.where(valid, slots, n)
        uid = state.next_uid + jnp.arange(b, dtype=jnp.uint32)
        set_ = lambda arr, val: arr.at[c_idx].set(val, mode="drop")
        return state.replace(
            alive=set_(state.alive, True),
            pos=set_(state.pos, pos),
            vel=set_(state.vel, 0.0),
            angle=set_(state.angle, jax.random.uniform(k[3], (b,), maxval=2 * math.pi)),
            energy=set_(energy, e_child),
            age=set_(state.age, 0),
            signal=set_(state.signal, 0.0),
            genome=_scatter(state.genome, c_idx, child_g),
            pheno=_scatter(state.pheno, c_idx, child_p),
            w=set_(state.w, child_p.w0.astype(jnp.float32)),
            h=set_(state.h, 0.0),
            lineage=Lineage(
                uid=set_(state.lineage.uid, uid),
                parent_uid=set_(state.lineage.parent_uid, state.lineage.uid[parents]),
                birth_step=set_(state.lineage.birth_step, state.step),
            ),
            next_uid=state.next_uid + n_births.astype(jnp.uint32),
        )

    newborn = jnp.zeros((n,), bool).at[jnp.where(valid, slots, n)].set(True, mode="drop")
    state = jax.lax.cond(n_births > 0, do, lambda s: s, state)
    return state, n_births, newborn


def world_step(state: IslandState, _=None):
    """sensores → cerebro → física → comer/atacar → energía → muertes → nacimientos → plasticidad → recursos."""
    key = jax.random.fold_in(state.key, state.step)
    k_birth = jax.random.split(key, 2)[0]

    cand = world.neighbors(state.pos, state.alive)
    obs = world.sense(state, cand)
    actions, h_new, pre, post = brain.step(state.w, state.h, obs, state.genome.hid_mask)
    pos, vel, angle, thrust = world.physics(state, actions, cand)
    intake, resources = world.eat(state.resources, pos, state.alive, actions)
    state = state.replace(pos=pos, vel=vel, angle=angle, h=jnp.where(state.alive[:, None], h_new, 0.0),
                          signal=jnp.where(state.alive, actions[:, 4], 0.0), resources=resources)
    energy = world.energy_update(state, thrust, intake)

    died = state.alive & (energy <= 0)
    old = state.age >= C.SENESCENCE_START
    alive = state.alive & ~died
    state = state.replace(energy=jnp.where(alive, energy, 0.0), alive=alive,
                          age=jnp.where(alive, state.age + 1, 0))

    state, n_births, newborn = _births(state, k_birth)

    def plastic(w):
        m = brain.modulation(h_new, state.genome.hid_mask, state.genome.hid_type)
        m = jnp.where(state.alive & ~newborn, m, 0.0)
        return brain.plasticity(state.pheno, w, pre, post, m)

    w = jax.lax.cond(state.step % C.PLASTICITY_EVERY == 0, plastic, lambda w: w, state.w)
    resources = world.resources_step(state.resources, state.env, state.step)
    state = state.replace(w=w, resources=resources, step=state.step + 1)

    stats = StepStats(
        population=jnp.sum(state.alive).astype(jnp.int32),
        births=n_births,
        deaths_starvation=jnp.sum(died & ~old).astype(jnp.int32),
        deaths_age=jnp.sum(died & old).astype(jnp.int32),
        intake=jnp.sum(intake),
    )
    return state, stats


@functools.partial(jax.jit, static_argnames=("k",), donate_argnums=(0,))
def epoch(state: IslandState, k: int = C.EPOCH_STEPS):
    """Ejecuta k pasos y devuelve (state, EpochStats)."""
    state, per_step = jax.lax.scan(world_step, state, None, length=k)
    return state, metrics.epoch_stats(state, per_step)


@functools.partial(jax.jit, static_argnames=("count",), donate_argnums=(0,))
def reinject(state: IslandState, count: int = C.N_MIN_REINJECT) -> IslandState:
    """Reinyecta hasta `count` genomas mínimos en slots libres (fase 0: sin archivo todavía)."""
    n = state.alive.shape[0]
    key = jax.random.fold_in(jax.random.fold_in(state.key, 0xFFFFFFFF), state.step)
    k = jax.random.split(key, 4)
    slots = jnp.nonzero(~state.alive, size=count, fill_value=n)[0]
    valid = slots < n
    idx = jnp.where(valid, slots, n)
    g = jax.vmap(G.random_minimal)(jax.random.split(k[0], count))
    p = develop_batch(g)
    uid = state.next_uid + jnp.arange(count, dtype=jnp.uint32)
    set_ = lambda arr, val: arr.at[idx].set(val, mode="drop")
    return state.replace(
        alive=set_(state.alive, True),
        pos=set_(state.pos, jax.random.uniform(k[1], (count, 2), maxval=C.WORLD_L)),
        vel=set_(state.vel, 0.0),
        angle=set_(state.angle, jax.random.uniform(k[2], (count,), maxval=2 * math.pi)),
        energy=set_(state.energy, C.E_INIT),
        age=set_(state.age, 0),
        signal=set_(state.signal, 0.0),
        genome=_scatter(state.genome, idx, g),
        pheno=_scatter(state.pheno, idx, p),
        w=set_(state.w, p.w0.astype(jnp.float32)),
        h=set_(state.h, 0.0),
        lineage=Lineage(
            uid=set_(state.lineage.uid, uid),
            parent_uid=set_(state.lineage.parent_uid, jnp.uint32(2**32 - 1)),
            birth_step=set_(state.lineage.birth_step, state.step),
        ),
        next_uid=state.next_uid + jnp.sum(valid).astype(jnp.uint32),
    )
