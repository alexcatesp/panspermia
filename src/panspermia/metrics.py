"""Métricas de observación: nunca realimentan la selección (spec §Métricas).

Fase 0: demografía y complejidad. Se calculan dentro de `epoch` (bajo jit) y se devuelven como
un diccionario de escalares que el runner vuelca a Parquet.
"""
from __future__ import annotations

import jax
import jax.numpy as jnp

from . import config as C


def _masked_mean(x: jax.Array, mask: jax.Array) -> jax.Array:
    x = x.astype(jnp.float32)
    return jnp.sum(jnp.where(mask, x, 0.0)) / jnp.maximum(jnp.sum(mask), 1)


def _masked_max(x: jax.Array, mask: jax.Array) -> jax.Array:
    return jnp.max(jnp.where(mask, x.astype(jnp.float32), 0.0))


def epoch_stats(state, per_step) -> dict[str, jax.Array]:
    alive = state.alive
    g = state.genome
    hidden = jnp.sum(g.hid_mask, axis=-1)
    synapses = jnp.sum(state.pheno.mask, axis=(-1, -2))
    cppn_nodes = jnp.sum(g.node_mask, axis=-1) - (C.CPPN_IN + C.CPPN_OUT)  # ocultos de la CPPN
    cppn_edges = jnp.sum(g.W_mask, axis=(-1, -2))
    out = {
        "step": state.step,
        "population": jnp.sum(alive).astype(jnp.int32),
        "population_min": jnp.min(per_step.population),
        "births": jnp.sum(per_step.births),
        "deaths_starvation": jnp.sum(per_step.deaths_starvation),
        "deaths_age": jnp.sum(per_step.deaths_age),
        "deaths_attack": jnp.int32(0),
        "intake": jnp.sum(per_step.intake),
        "mean_age": _masked_mean(state.age, alive),
        "mean_energy": _masked_mean(state.energy, alive),
        "resources_total": jnp.sum(state.resources),
        "generation_mean": _masked_mean(g.generation, alive),
        "generation_max": _masked_max(g.generation, alive),
    }
    for name, x in (("hidden", hidden), ("synapses", synapses),
                    ("cppn_nodes", cppn_nodes), ("cppn_edges", cppn_edges)):
        out[f"{name}_mean"] = _masked_mean(x, alive)
        out[f"{name}_max"] = _masked_max(x, alive)
    return out
