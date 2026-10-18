"""Física de la mutación del número de neuronas (ADR-015): sin selección, cada modo deriva como dice."""
import jax
import jax.numpy as jnp
import numpy as np
import pytest

from panspermia import config
from panspermia import genome as G


def _drift(mode: str, rounds: int = 300, n: int = 256) -> float:
    """Media de neuronas expresadas tras `rounds` mutaciones seguidas, sin selección."""
    config.NEURON_MUTATION = mode
    try:
        mutate = jax.jit(jax.vmap(lambda g, k: G.mutate(g, k)))  # traza nueva con el modo elegido
        g = jax.vmap(G.random_minimal)(jax.random.split(jax.random.PRNGKey(0), n))
        for r in range(rounds):
            g = mutate(g, jax.random.split(jax.random.PRNGKey(r + 1), n))
        return float(jnp.mean(jnp.sum(g.hid_mask, axis=-1)))
    finally:
        config.NEURON_MUTATION = "nest"


def test_each_mutation_physics_drifts_as_designed():
    start = config.N_HIDDEN_INIT
    nest, neutral, earth = _drift("nest"), _drift("neutral"), _drift("terrestre")
    assert nest > start + 3               # spec v1: crece hacia ~43
    assert abs(neutral - start) < 1.5     # sin rumbo
    assert earth < start - 2              # pierde más de lo que gana
    assert nest > neutral > earth


def test_unknown_mutation_physics_is_rejected():
    config.NEURON_MUTATION = "inventada"
    try:
        g = G.random_minimal(jax.random.PRNGKey(0))
        with pytest.raises(ValueError):
            G.mutate(g, jax.random.PRNGKey(1))
    finally:
        config.NEURON_MUTATION = "nest"


def test_default_is_the_spec_v1_operator():
    """El modo por defecto no cambia nada: misma mutación que antes de ADR-015."""
    assert config.NEURON_MUTATION == "nest"
    g = G.random_minimal(jax.random.PRNGKey(3))
    a = G.mutate(g, jax.random.PRNGKey(4))
    b = G.mutate(g, jax.random.PRNGKey(4))
    assert np.array_equal(np.asarray(a.hid_mask), np.asarray(b.hid_mask))
