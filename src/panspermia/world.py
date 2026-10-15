"""Mundo 2D toroidal: física, recursos, sensores por rayos y energía (spec §Mundo).

Salvaguarda 1: este módulo es el ÚNICO interfaz de los agentes con algo externo, y solo expone
la simulación. No añadir aquí acceso a red, ficheros ni procesos.

Vecindad por rejilla espacial de tamaño fijo: celdas de GRID_CELL unidades con hasta CELL_CAP
agentes visibles cada una; cada agente consulta las 3 × 3 celdas que le rodean. El orden de la
rejilla se obtiene con `argsort` estable sobre enteros, que es determinista.
"""
from __future__ import annotations

import math

import blake3
import jax
import jax.numpy as jnp
from flax import struct

from . import config as C

L = C.WORLD_L
G = int(C.WORLD_L // C.GRID_CELL)          # celdas por lado de la rejilla de vecindad
RES = C.RESOURCE_GRID
RES_CELL = C.WORLD_L / C.RESOURCE_GRID
N_CELLS = G * G


@struct.dataclass
class EnvParams:
    """Biogeografía de la isla, derivada de su node_id (constante durante la ejecución)."""
    k_mean: jax.Array
    drift: jax.Array
    friction: jax.Array
    c_basal: jax.Array
    wave_k: jax.Array      # f32[K_WAVES, 2] números de onda enteros
    wave_phase: jax.Array  # f32[K_WAVES]
    wave_amp: jax.Array    # f32[K_WAVES]
    wave_speed: jax.Array  # f32[K_WAVES] (signo y magnitud relativa de la deriva)


def make_env(node_id: bytes) -> EnvParams:
    """Parámetros ambientales ±BIOGEO_SPREAD estables y reproducibles a partir del node_id."""
    seed = int.from_bytes(blake3.blake3(b"panspermia-env" + node_id).digest(length=4), "little")
    k = jax.random.split(jax.random.PRNGKey(seed), 8)
    s = C.BIOGEO_SPREAD
    jitter = jax.random.uniform(k[0], (4,), minval=1 - s, maxval=1 + s)
    kx = jax.random.randint(k[1], (C.K_WAVES,), -C.K_WAVE_MAX_FREQ, C.K_WAVE_MAX_FREQ + 1)
    ky = jax.random.randint(k[2], (C.K_WAVES,), 1, C.K_WAVE_MAX_FREQ + 1)
    return EnvParams(
        k_mean=C.K_MEAN * jitter[0],
        drift=C.K_DRIFT * jitter[1],
        friction=C.FRICTION * jitter[2],
        c_basal=C.C_BASAL * jitter[3],
        wave_k=jnp.stack([kx, ky], axis=1).astype(jnp.float32),
        wave_phase=jax.random.uniform(k[3], (C.K_WAVES,), maxval=2 * math.pi),
        wave_amp=jax.random.uniform(k[4], (C.K_WAVES,), minval=0.5, maxval=1.0),
        wave_speed=jax.random.uniform(k[5], (C.K_WAVES,), minval=-1.0, maxval=1.0),
    )


# ---------------------------------------------------------------------------------------------
# Recursos
# ---------------------------------------------------------------------------------------------

_RES_CENTERS = (jnp.arange(RES, dtype=jnp.float32) + 0.5) / RES


def kmax_field(env: EnvParams, step: jax.Array) -> jax.Array:
    """Kmax [RES, RES]: manchas por suma de ondas planas toroidales que derivan lentamente."""
    t = step.astype(jnp.float32) * C.DT
    cx, cy = jnp.meshgrid(_RES_CENTERS, _RES_CENTERS, indexing="ij")
    phase = (2 * math.pi * (env.wave_k[:, 0, None, None] * cx + env.wave_k[:, 1, None, None] * cy)
             + env.wave_phase[:, None, None] + env.drift * env.wave_speed[:, None, None] * t)
    z = jnp.sum(env.wave_amp[:, None, None] * jnp.sin(phase), axis=0)
    z = z / jnp.sqrt(jnp.sum(env.wave_amp ** 2) / 2)
    return env.k_mean * jnp.maximum(0.0, 1.0 + C.K_CONTRAST * z)


def init_resources(env: EnvParams, key: jax.Array) -> jax.Array:
    """Campo inicial de recursos: lleno hasta Kmax en el paso 0."""
    return kmax_field(env, jnp.int32(0))


def resources_step(resources: jax.Array, env: EnvParams, step: jax.Array) -> jax.Array:
    """Crecimiento logístico r·R·(1 − R/Kmax) más un aporte mínimo donde Kmax > 0."""
    K = kmax_field(env, step)
    safe_K = jnp.maximum(K, 1e-6)
    growth = C.RESOURCE_R * resources * (1.0 - resources / safe_K)
    growth = jnp.where(K > 0, growth + C.RESOURCE_SEED, -C.RESOURCE_R * resources)
    return jnp.maximum(resources + growth * C.DT, 0.0)


def _res_index(p: jax.Array) -> jax.Array:
    ij = jnp.floor(p / RES_CELL).astype(jnp.int32) % RES
    return ij[..., 0] * RES + ij[..., 1]


# ---------------------------------------------------------------------------------------------
# Vecindad
# ---------------------------------------------------------------------------------------------

def wrap_delta(d: jax.Array) -> jax.Array:
    """Imagen mínima en el toro."""
    return (d + L / 2) % L - L / 2


def neighbors(pos: jax.Array, alive: jax.Array) -> jax.Array:
    """Candidatos a vecino [N, 9·CELL_CAP] (índices de agente; -1 si vacío)."""
    n = pos.shape[0]
    cxy = jnp.floor(pos / C.GRID_CELL).astype(jnp.int32) % G
    cell = jnp.where(alive, cxy[:, 0] * G + cxy[:, 1], N_CELLS)
    order = jnp.argsort(cell, stable=True)
    sorted_cell = cell[order]
    ids = jnp.arange(N_CELLS)
    starts = jnp.searchsorted(sorted_cell, ids, side="left")
    ends = jnp.searchsorted(sorted_cell, ids, side="right")
    slot = starts[:, None] + jnp.arange(C.CELL_CAP)[None, :]
    table = jnp.where(slot < ends[:, None], order[jnp.clip(slot, 0, n - 1)], -1)  # [cells, CAP]
    d = jnp.array([-1, 0, 1])
    dx, dy = jnp.meshgrid(d, d, indexing="ij")
    nx = (cxy[:, 0, None] + dx.ravel()[None, :]) % G
    ny = (cxy[:, 1, None] + dy.ravel()[None, :]) % G
    cand = table[nx * G + ny].reshape(n, 9 * C.CELL_CAP)
    self_or_empty = (cand == jnp.arange(n)[:, None]) | ~alive[:, None]
    return jnp.where(self_or_empty, -1, cand)


def _gather_neighbors(cand, pos, vel, radius, alive):
    safe = jnp.maximum(cand, 0)
    valid = (cand >= 0) & alive[safe]
    rel = wrap_delta(pos[safe] - pos[:, None, :])
    return safe, valid, rel, vel[safe], radius[safe]


# ---------------------------------------------------------------------------------------------
# Sensores
# ---------------------------------------------------------------------------------------------

_RAY_FRAC = jnp.linspace(-0.5, 0.5, C.N_RAYS)
_SAMPLE_FRAC = (jnp.arange(C.RAY_SAMPLES, dtype=jnp.float32) + 1) / C.RAY_SAMPLES


def sense(state, cand: jax.Array) -> jax.Array:
    """Observaciones [N, OBS_DIM].

    Por rayo (16, en el cono del cuerpo): proximidad del agente más cercano (1 − d/alcance),
    recurso medio a lo largo del rayo (relativo a K_MEAN), parentesco del agente detectado
    (1 − distancia de color/√3) y su señal. Después: energía, velocidad (adelante, lateral),
    reloj (sen, cos) y señal recibida (media de los vecinos dentro del alcance).
    """
    ph = state.pheno
    safe, valid, rel, _, r_j = _gather_neighbors(cand, state.pos, state.vel, ph.radius, state.alive)
    rng = ph.sensor_range
    ang = state.angle[:, None] + ph.cone[:, None] * _RAY_FRAC[None, :]          # [N, R]
    u = jnp.stack([jnp.cos(ang), jnp.sin(ang)], axis=-1)                         # [N, R, 2]

    t = jnp.einsum("nmd,nrd->nmr", rel, u)                                       # [N, M, R]
    pp = jnp.sum(rel * rel, axis=-1)[..., None]
    r2 = (r_j * r_j)[..., None]
    perp2 = pp - t * t
    hit = valid[..., None] & (t > 0) & (perp2 < r2)
    dist = jnp.maximum(t - jnp.sqrt(jnp.maximum(r2 - perp2, 0.0)), 0.0)
    dist = jnp.where(hit & (dist < rng[:, None, None]), dist, jnp.inf)
    nearest = jnp.argmin(dist, axis=1)                                           # [N, R]
    dmin = jnp.min(dist, axis=1)
    seen = jnp.isfinite(dmin)
    j = jnp.take_along_axis(safe, nearest, axis=1)                               # [N, R]
    prox = jnp.where(seen, 1.0 - dmin / rng[:, None], 0.0)
    color_d = jnp.linalg.norm(ph.color[j] - ph.color[:, None, :], axis=-1)
    kin = jnp.where(seen, 1.0 - color_d / math.sqrt(3.0), 0.0)
    sig = jnp.where(seen, state.signal[j], 0.0)

    pts = state.pos[:, None, None, :] + (rng[:, None, None, None] * _SAMPLE_FRAC[None, None, :, None]
                                         * u[:, :, None, :])                    # [N, R, S, 2]
    res = state.resources.ravel()[_res_index(pts % L)]
    res = jnp.mean(res, axis=-1) / C.K_MEAN

    rays = jnp.stack([prox, res, kin, sig], axis=-1).reshape(state.pos.shape[0], -1)

    heading = jnp.stack([jnp.cos(state.angle), jnp.sin(state.angle)], axis=-1)
    lateral = jnp.stack([-heading[:, 1], heading[:, 0]], axis=-1)
    v_fwd = jnp.tanh(jnp.sum(state.vel * heading, axis=-1) / C.V_OBS_SCALE)
    v_lat = jnp.tanh(jnp.sum(state.vel * lateral, axis=-1) / C.V_OBS_SCALE)
    clock = 2 * math.pi * (state.step % C.CLOCK_PERIOD).astype(jnp.float32) / C.CLOCK_PERIOD
    n = state.pos.shape[0]
    in_range = valid & (pp[..., 0] < rng[:, None] ** 2)
    heard = jnp.sum(jnp.where(in_range, state.signal[safe], 0.0), axis=1)
    recv = heard / jnp.maximum(jnp.sum(in_range, axis=1), 1)
    own = jnp.stack([
        jnp.tanh(state.energy / C.E_OBS_SCALE), v_fwd, v_lat,
        jnp.full((n,), jnp.sin(clock)), jnp.full((n,), jnp.cos(clock)), recv,
    ], axis=-1)
    obs = jnp.concatenate([rays, own], axis=-1)
    return jnp.where(state.alive[:, None], obs, 0.0)


# ---------------------------------------------------------------------------------------------
# Física
# ---------------------------------------------------------------------------------------------

def physics(state, actions: jax.Array, cand: jax.Array):
    """Empuje, giro, fricción lineal y colisiones elásticas. Devuelve (pos, vel, angle, thrust)."""
    ph = state.pheno
    alive = state.alive
    thrust = actions[:, 0] * ph.max_thrust
    angle = (state.angle + actions[:, 1] * C.MAX_TURN_RATE * C.DT) % (2 * math.pi)
    heading = jnp.stack([jnp.cos(angle), jnp.sin(angle)], axis=-1)
    acc = (thrust / ph.mass)[:, None] * heading - state.env.friction * state.vel
    vel = state.vel + acc * C.DT

    safe, valid, rel, vel_j, r_j = _gather_neighbors(cand, state.pos, vel, ph.radius, alive)
    dist = jnp.sqrt(jnp.sum(rel * rel, axis=-1))
    overlap = ph.radius[:, None] + r_j - dist
    touching = valid & (overlap > 0) & (dist > 1e-6)
    normal = rel / jnp.maximum(dist, 1e-6)[..., None]
    vn = jnp.sum((vel[:, None, :] - vel_j) * normal, axis=-1)                   # >0: se acercan
    m_i, m_j = ph.mass[:, None], ph.mass[safe]
    impulse = jnp.where(touching & (vn > 0), 2 * m_j / (m_i + m_j) * vn, 0.0)
    vel = vel - jnp.sum(impulse[..., None] * normal, axis=1)
    push = jnp.where(touching, 0.5 * overlap, 0.0)
    correction = -jnp.sum(push[..., None] * normal, axis=1)

    pos = (state.pos + vel * C.DT + correction) % L
    alive2 = alive[:, None]
    return (jnp.where(alive2, pos, state.pos), jnp.where(alive2, vel, 0.0),
            jnp.where(alive, angle, state.angle), jnp.where(alive, thrust, 0.0))


def eat(resources: jax.Array, pos: jax.Array, alive: jax.Array, actions: jax.Array):
    """Ingesta en la celda de recursos bajo el centro; reparto proporcional si falta comida."""
    demand = jnp.where(alive & (actions[:, 2] > 0), C.EAT_RATE * C.DT, 0.0)
    cell = _res_index(pos)
    flat = resources.ravel()
    total = jax.ops.segment_sum(demand, cell, num_segments=RES * RES)
    scale = jnp.minimum(1.0, flat / jnp.maximum(total, 1e-9))
    intake = demand * scale[cell]
    eaten = jax.ops.segment_sum(intake, cell, num_segments=RES * RES)
    return intake, jnp.maximum(flat - eaten, 0.0).reshape(RES, RES)


def energy_update(state, thrust: jax.Array, intake: jax.Array) -> jax.Array:
    """E += ingesta − (c0·senescencia + cb·n_neuronas + cs·masa + cm·|empuje|² + ca·ataque)·dt."""
    ph = state.pheno
    senescence = 1.0 + C.SENESCENCE_RATE * jnp.maximum(0, state.age - C.SENESCENCE_START)
    cost = (state.env.c_basal * senescence + C.C_NEURON * ph.n_hidden + C.C_MASS * ph.mass
            + C.C_MOVE * thrust ** 2)
    return jnp.where(state.alive, state.energy + intake - cost * C.DT, 0.0)
