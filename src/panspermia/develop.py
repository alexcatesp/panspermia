"""Desarrollo genotipo→fenotipo: CPPN vectorizada sobre el sustrato neuronal (spec §Desarrollo).

Sustrato: las OBS_DIM entradas en y = -1 y las ACT_DIM salidas en y = +1 (x uniforme en [-1, 1]);
las ocultas en `hid_pos`. La CPPN se evalúa sobre los N_PRE × N_POST pares
(entrada ∪ oculta) → (oculta ∪ salida). Cálculo en f32, redondeo final a f16.
"""
from __future__ import annotations

import jax
import jax.numpy as jnp
import numpy as np
from flax import struct

from . import config as C
from .genome import Genome

F16 = jnp.float16

_OBS_POS = np.stack([np.linspace(-1, 1, C.OBS_DIM), -np.ones(C.OBS_DIM)], axis=1).astype(np.float32)
_ACT_POS = np.stack([np.linspace(-1, 1, C.ACT_DIM), np.ones(C.ACT_DIM)], axis=1).astype(np.float32)


@struct.dataclass
class Phenotype:
    """Parámetros fijos de un agente. Matrices de forma [N_PRE, N_POST] (con eje N delante en lote)."""
    w0: jax.Array
    A: jax.Array
    B: jax.Array
    C: jax.Array
    D: jax.Array
    eta: jax.Array
    g: jax.Array
    mask: jax.Array          # bool
    radius: jax.Array        # escalares de cuerpo (f32)
    max_thrust: jax.Array
    cone: jax.Array          # rad
    sensor_range: jax.Array
    color: jax.Array         # f32[3]
    attack: jax.Array
    mass: jax.Array
    repro_threshold: jax.Array
    offspring_frac: jax.Array
    n_hidden: jax.Array      # f32, neuronas ocultas expresadas (coste energético)


def _activation(act_id: jax.Array, x: jax.Array) -> jax.Array:
    """sin, gauss, tanh, sigmoide, abs, identidad (índices 0..5)."""
    candidates = jnp.stack([
        jnp.sin(x), jnp.exp(-x * x), jnp.tanh(x), jax.nn.sigmoid(x), jnp.abs(x), x,
    ])
    return jnp.take(candidates, act_id.astype(jnp.int32), axis=0)


def _to_range(raw: jax.Array, bounds: tuple[float, float]) -> jax.Array:
    lo, hi = bounds
    return lo + (hi - lo) * jax.nn.sigmoid(raw)


def eval_cppn(genome: Genome, inputs: jax.Array) -> jax.Array:
    """Evalúa la CPPN sobre un lote de entradas [P, CPPN_IN] → salidas [P, CPPN_OUT]."""
    W = genome.W.astype(jnp.float32)
    bias = genome.bias.astype(jnp.float32)
    P = inputs.shape[0]
    vals = jnp.zeros((P, C.CPPN_NODES), jnp.float32).at[:, :C.CPPN_IN].set(inputs)
    for j in range(C.CPPN_IN, C.CPPN_NODES):  # orden topológico por índice (estático)
        pre = jnp.sum(vals * W[:, j], axis=1) + bias[j]
        out = _activation(genome.act_id[j], pre)
        vals = vals.at[:, j].set(jnp.where(genome.node_mask[j], out, 0.0))
    return vals[:, C.CPPN_OUT_START:]


def develop(genome: Genome) -> Phenotype:
    """Devuelve w0, A, B, C, D, eta, g_mod y mask de forma [N_PRE, N_POST]. Pura y determinista."""
    hid_pos = genome.hid_pos.astype(jnp.float32)
    pre_pos = jnp.concatenate([jnp.asarray(_OBS_POS), hid_pos])    # [134, 2]
    post_pos = jnp.concatenate([hid_pos, jnp.asarray(_ACT_POS)])   # [69, 2]
    p1 = jnp.broadcast_to(pre_pos[:, None, :], (C.N_PRE, C.N_POST, 2))
    p2 = jnp.broadcast_to(post_pos[None, :, :], (C.N_PRE, C.N_POST, 2))
    d = jnp.sqrt(jnp.sum((p1 - p2) ** 2, axis=-1, keepdims=True))
    ones = jnp.ones_like(d)
    inputs = jnp.concatenate([p1, p2, d, ones], axis=-1).reshape(-1, C.CPPN_IN)

    o = eval_cppn(genome, inputs).reshape(C.N_PRE, C.N_POST, C.CPPN_OUT)

    pre_active = jnp.concatenate([jnp.ones(C.OBS_DIM, bool), genome.hid_mask])
    post_active = jnp.concatenate([genome.hid_mask, jnp.ones(C.ACT_DIM, bool)])
    mask = (o[..., 6] > 0) & pre_active[:, None] & post_active[None, :]

    def masked(x):
        return jnp.where(mask, x, 0.0).astype(F16)

    coef = lambda k: masked(C.PLAST_COEF_SCALE * jnp.tanh(o[..., k]))
    body = genome.body.astype(jnp.float32)
    life = genome.life.astype(jnp.float32)
    radius = _to_range(body[0], C.RADIUS_BOUNDS)
    return Phenotype(
        w0=masked(C.W_INIT_SCALE * jnp.tanh(o[..., 0])),
        A=coef(1), B=coef(2), C=coef(3), D=coef(4),
        eta=masked(C.ETA_MAX * jax.nn.sigmoid(o[..., 5])),
        g=masked(jnp.tanh(o[..., 7])),
        mask=mask,
        radius=radius,
        max_thrust=_to_range(body[1], C.THRUST_BOUNDS),
        cone=jnp.deg2rad(_to_range(body[2], C.CONE_BOUNDS_DEG)),
        sensor_range=_to_range(body[3], C.SENSOR_RANGE_BOUNDS),
        color=jax.nn.sigmoid(body[4:7]),
        attack=_to_range(body[7], C.ATTACK_BOUNDS),
        mass=(radius / C.RADIUS_REF) ** 2,
        repro_threshold=_to_range(life[0], C.REPRO_THRESHOLD_BOUNDS),
        offspring_frac=_to_range(life[1], C.OFFSPRING_ENERGY_FRAC_BOUNDS),
        n_hidden=jnp.sum(genome.hid_mask).astype(jnp.float32),
    )


def develop_batch(genomes: Genome) -> Phenotype:
    """develop sobre un lote con eje N delante, en tandas para acotar memoria."""
    return jax.lax.map(develop, genomes, batch_size=C.DEVELOP_BATCH)
