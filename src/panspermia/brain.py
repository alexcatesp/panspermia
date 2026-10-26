"""Red recurrente con plasticidad hebbiana ABCD modulada (spec §Cerebro). Sin retropropagación.

Todas las funciones operan sobre lotes con eje N delante. Neuronas presinápticas: [obs; h]
(N_PRE = 144); postsinápticas: [h; acciones] (N_POST = 72). La matriz de pesos vivos `w` es f32.

Paso: h' = tanh(W_hid^T [o; h]) ⊙ hid_mask, a = tanh(W_out^T [o; h']). Las conexiones directas
obs→acción del sustrato se usan junto con h'. En la fase 0 no hay sesgo neuronal (b = 0, ADR-005).
Las neuronas moduladoras también proyectan como ocultas normales; además definen m_t.
"""
from __future__ import annotations

import jax
import jax.numpy as jnp

from . import config as C

H = C.N_HIDDEN_MAX


def step(w: jax.Array, h: jax.Array, obs: jax.Array, hid_mask: jax.Array):
    """Un paso neuronal: devuelve (acciones, h_nuevo, actividades pre, actividades post)."""
    pre = jnp.concatenate([obs, h], axis=-1)                                   # [N, 134]
    h_new = jnp.tanh(jnp.einsum("np,npq->nq", pre, w[:, :, :H])) * hid_mask    # [N, 64]
    pre_out = jnp.concatenate([obs, h_new], axis=-1)
    actions = jnp.tanh(jnp.einsum("np,npq->nq", pre_out, w[:, :, H:]))        # [N, 5]
    post = jnp.concatenate([h_new, actions], axis=-1)                          # [N, 69]
    return actions, h_new, pre, post


def modulation(h: jax.Array, hid_mask: jax.Array, hid_type: jax.Array) -> jax.Array:
    """m_t: media de la activación de las ocultas moduladoras expresadas (0 si no hay)."""
    mod = (hid_mask & hid_type).astype(h.dtype)
    return jnp.sum(h * mod, axis=-1) / jnp.maximum(jnp.sum(mod, axis=-1), 1.0)


def plasticity(pheno, w: jax.Array, pre: jax.Array, post: jax.Array, m: jax.Array) -> jax.Array:
    """Δw = η·g·m·(A·xi·xj + B·xi + C·xj + D), recortado a |w| <= W_MAX.

    η y g son cero fuera de la máscara de expresión, así que las sinapsis no expresadas siguen en 0.
    """
    f32 = lambda x: x.astype(jnp.float32)
    xi = pre[:, :, None]
    xj = post[:, None, :]
    hebb = f32(pheno.A) * xi * xj + f32(pheno.B) * xi + f32(pheno.C) * xj + f32(pheno.D)
    dw = f32(pheno.eta) * f32(pheno.g) * m[:, None, None] * hebb
    return jnp.clip(w + dw, -C.W_MAX, C.W_MAX)


def plasticity_trace(pheno, w: jax.Array, trace: jax.Array, pre: jax.Array, post: jax.Array, m: jax.Array,
                     lam: float) -> tuple[jax.Array, jax.Array]:
    """Con trazas de elegibilidad (ADR-031): e ← λ·e + (1 − λ)·hebb y Δw = η·g·m·e. Devuelve (w, e).

    La traza es una media ponderada del término hebbiano, acotada por su máximo; con λ = 0 es la regla de siempre.
    """
    f32 = lambda x: x.astype(jnp.float32)
    xi = pre[:, :, None]
    xj = post[:, None, :]
    hebb = f32(pheno.A) * xi * xj + f32(pheno.B) * xi + f32(pheno.C) * xj + f32(pheno.D)
    trace = lam * trace + (1.0 - lam) * hebb
    dw = f32(pheno.eta) * f32(pheno.g) * m[:, None, None] * trace
    return jnp.clip(w + dw, -C.W_MAX, C.W_MAX), trace
