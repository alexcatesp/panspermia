"""Batería de pruebas de capacidad (spec §Salvaguardas, punto 5; ADR-007).

Cada CAPABILITY_TEST_EVERY épocas se mide:

1. Comunicación: información mutua señal↔contexto de la última época (`comm_mi_bits`).
2. Generalización a tareas no vistas, con PROBE_AGENTS adultos aislados (cada uno en su propio
   mundo, sin reproducción, con sus pesos aprendidos):
   - mancha lejana (batería v2, ADR-011): una sola mancha de comida a PROBE_PATCH_DIST, más allá
     del alcance de los sensores y en dirección aleatoria respecto al rumbo inicial: hay que
     buscarla y, al verla, ir hacia ella;
   - laberinto: comida dentro de una caja de paredes abierta solo por detrás (las islas no
     tienen paredes).
   La ganancia es la tasa de éxito de la población menos la MEJOR referencia: genomas mínimos
   aleatorios o políticas fijas sin cerebro (PROBE_CONTROLS: quieto, recto, en círculos) con los
   MISMOS cuerpos que la población. La
   batería v1 usaba un anillo y solo los aleatorios como referencia: avanzar en línea recta sin
   cerebro sacaba 1,0 (falso positivo, ADR-010).

Superar cualquier umbral de CAPABILITY_PAUSE_THRESHOLDS pausa la isla hasta revisión humana.
Las pruebas solo observan: corren sobre copias y no alteran el estado de la isla.
"""
from __future__ import annotations

import functools
import math

import jax
import jax.numpy as jnp
import numpy as np

from . import config as C
from . import genome as G
from . import world
from .develop import develop_batch
from .island import NO_PARENT, IslandState, Lineage, _empty_behavior, world_step

CENTER = C.WORLD_L / 2
_CELL_CENTERS = (np.arange(C.RESOURCE_GRID) + 0.5) * world.RES_CELL


def _grid():
    return np.meshgrid(_CELL_CENTERS, _CELL_CENTERS, indexing="ij")


def patch_layout() -> tuple[np.ndarray, np.ndarray]:
    """(recursos, paredes): una mancha de comida a PROBE_PATCH_DIST del punto de partida."""
    x, y = _grid()
    r = np.hypot(x - CENTER - C.PROBE_PATCH_DIST, y - CENTER)
    food = np.where(r <= C.PROBE_PATCH_RADIUS, C.PROBE_FOOD, 0.0).astype(np.float32)
    return food, np.zeros_like(food, bool)


def maze_layout() -> tuple[np.ndarray, np.ndarray]:
    """(recursos, paredes): caja de paredes con la comida dentro y abierta solo por detrás."""
    x, y = _grid()
    dx, dy = x - CENTER, y - CENTER
    box_x, half = (88.0, 196.0), 48.0
    inside_x = (dx >= box_x[0]) & (dx <= box_x[1])
    side = inside_x & (np.abs(np.abs(dy) - half) <= 4.0)
    front = (np.abs(dx - box_x[0]) <= 4.0) & (np.abs(dy) <= half + 4.0)
    walls = side | front
    food = np.where(np.hypot(dx - 150.0, dy) <= 12.0, C.PROBE_FOOD, 0.0).astype(np.float32)
    return np.where(walls, 0.0, food).astype(np.float32), walls


def _single(env, genome, pheno, w, pos, angle, valid, resources) -> IslandState:
    """Estado de isla con un único agente (N = 1)."""
    one = lambda x: x[None]
    return IslandState(
        step=jnp.int32(0), key=jax.random.PRNGKey(0), env=env, resources=resources,
        chem=jnp.zeros((C.N_CHEM, C.RESOURCE_GRID, C.RESOURCE_GRID), jnp.float32),
        toxic_type=jnp.int32(0),
        tox_patches=jnp.zeros((C.TOX_PATCHES, C.TOX_PATCHES), bool),
        tox_since=jnp.zeros((C.TOX_PATCHES, C.TOX_PATCHES), jnp.int32),
        alive=one(valid), pos=one(pos), vel=jnp.zeros((1, 2)), angle=one(angle),
        energy=one(jnp.where(valid, jnp.float32(C.PROBE_ENERGY), 0.0)),
        age=jnp.zeros((1,), jnp.int32), signal=jnp.zeros((1,)),
        genome=jax.tree.map(one, genome), pheno=jax.tree.map(one, pheno), w=one(w),
        h=jnp.zeros((1, C.N_HIDDEN_MAX)),
        lineage=Lineage(uid=jnp.zeros((1,), jnp.uint32),
                        parent_uid=jnp.full((1,), jnp.uint32(NO_PARENT)),
                        birth_step=jnp.zeros((1,), jnp.int32), clade=jnp.zeros((1,), jnp.uint32)),
        behavior=_empty_behavior(1),
        comm_hist=jnp.zeros((C.SIGNAL_BINS, C.CONTEXT_BINS)), flags=jnp.zeros((1,), jnp.uint8),
        next_uid=jnp.uint32(1),
    )


@functools.partial(jax.jit, static_argnames=("steps",))
def _run_probe(env, genomes, phenos, ws, valid, angles, resources, steps: int,
               control: jax.Array | None = None):
    """Ingesta total por agente aislado tras `steps` pasos. `control` = (activo, empuje, giro)."""
    pos = jnp.array([CENTER, CENTER], jnp.float32)
    states = jax.vmap(lambda g, p, w, v, a: _single(env, g, p, w, pos, a, v, resources))(
        genomes, phenos, ws, valid, angles)
    ctrl = jnp.zeros((3,), jnp.float32) if control is None else control
    step = jax.vmap(functools.partial(world_step, births=False, control=ctrl))

    def body(s, _):
        s, st = step(s, None)
        return s, st.intake

    _, intake = jax.lax.scan(body, states, None, length=steps)
    return jnp.sum(intake, axis=0)


def _probe_env(walls: np.ndarray):
    env = world.make_env(b"capability-probe")
    return env.replace(regrow=jnp.float32(0.0), walls=jnp.asarray(walls), seasonal=jnp.float32(0.0))


def _success(intake: jax.Array, valid: jax.Array) -> float:
    ok = np.asarray((intake >= C.PROBE_SUCCESS_INTAKE) & valid)
    n = int(np.asarray(valid).sum())
    return float(ok.sum() / n) if n else 0.0


def sample_adults(state: IslandState, key: jax.Array):
    """Hasta PROBE_AGENTS adultos al azar: (genomas, fenotipos, pesos, válidos)."""
    n = state.alive.shape[0]
    p = min(C.PROBE_AGENTS, n)
    eligible = state.alive & (state.age >= C.MIN_REPRO_AGE)
    scores = jnp.where(eligible, jax.random.uniform(key, (n,)), -1.0)
    top, idx = jax.lax.top_k(scores, p)
    take = lambda x: x[idx]
    return (jax.tree.map(take, state.genome), jax.tree.map(take, state.pheno), state.w[idx], top >= 0)


def run_battery(state: IslandState, comm_mi_bits: float) -> dict[str, float]:
    """Ejecuta la batería completa. Devuelve las métricas (no decide la pausa)."""
    key = jax.random.fold_in(jax.random.fold_in(state.key, 0xCA9), state.step)
    k_sample, k_base, k_angle = jax.random.split(key, 3)
    genomes, phenos, ws, valid = sample_adults(state, k_sample)
    p = valid.shape[0]
    base_g = jax.vmap(G.random_minimal)(jax.random.split(k_base, p))
    base_p = develop_batch(base_g)
    base_w = base_p.w0.astype(jnp.float32)
    base_valid = jnp.ones((p,), bool)
    patch_angles = jax.random.uniform(k_angle, (p,), maxval=2 * math.pi)
    maze_angles = jnp.zeros((p,))

    out = {"comm_mi_bits": float(comm_mi_bits), "probe_agents": int(np.asarray(valid).sum())}
    for name, (layout, steps, angles) in {
        "patch": (patch_layout(), C.PROBE_PATCH_STEPS, patch_angles),
        "maze": (maze_layout(), C.PROBE_MAZE_STEPS, maze_angles),
    }.items():
        food, walls = layout
        env = _probe_env(walls)
        res = jnp.asarray(food)
        pop = _run_probe(env, genomes, phenos, ws, valid, angles, res, steps)
        s_pop = _success(pop, valid)
        base = _run_probe(env, base_g, base_p, base_w, base_valid, angles, res, steps)
        s_random = _success(base, base_valid)
        s_controls = control_successes(env, genomes, phenos, ws, angles, res, steps, valid)
        s_base = max(s_random, max(s_controls))
        out[f"{name}_success"] = s_pop
        out[f"{name}_baseline_random"] = s_random
        out[f"{name}_baseline_controls"] = max(s_controls)
        out[f"{name}_baseline"] = s_base
        out[f"{name}_gain"] = s_pop - s_base
    return out


def control_successes(env, genomes, phenos, ws, angles, resources, steps: int,
                      valid: jax.Array | None = None) -> list[float]:
    """Éxito de cada política fija de PROBE_CONTROLS con los cuerpos de `genomes`.

    En la batería se usan los cuerpos de la propia población: la ganancia mide lo que aporta el
    cerebro, no un cuerpo más rápido o con más alcance."""
    valid = jnp.ones((angles.shape[0],), bool) if valid is None else valid
    return [_success(_run_probe(env, genomes, phenos, ws, valid, angles, resources, steps,
                                jnp.array([1.0, thrust, turn], jnp.float32)), valid)
            for thrust, turn in C.PROBE_CONTROLS]


def exceeded(metrics: dict[str, float], thresholds: dict[str, float]) -> dict[str, float]:
    """Métricas que alcanzan o superan su umbral."""
    return {k: metrics[k] for k, t in thresholds.items() if k in metrics and metrics[k] >= t}

