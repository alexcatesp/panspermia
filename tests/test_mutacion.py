"""Física de la mutación del número de neuronas (ADR-015): sin selección, cada modo deriva como dice."""
import jax
import jax.numpy as jnp
import numpy as np
import pytest

from panspermia import config
from panspermia import genome as G


def _drift(mode: str, rounds: int = 300, n: int = 256) -> float:
    """Media de neuronas expresadas tras `rounds` mutaciones seguidas, sin selección."""
    old, config.NEURON_MUTATION = config.NEURON_MUTATION, mode
    try:
        mutate = jax.jit(jax.vmap(lambda g, k: G.mutate(g, k)))  # traza nueva con el modo elegido
        g = jax.vmap(G.random_minimal)(jax.random.split(jax.random.PRNGKey(0), n))
        for r in range(rounds):
            g = mutate(g, jax.random.split(jax.random.PRNGKey(r + 1), n))
        return float(jnp.mean(jnp.sum(g.hid_mask, axis=-1)))
    finally:
        config.NEURON_MUTATION = old


def test_each_mutation_physics_drifts_as_designed():
    start = config.N_HIDDEN_INIT
    nest, neutral, earth = _drift("nest"), _drift("neutral"), _drift("terrestre")
    assert nest > start + 3               # spec v1: crece hacia ~43
    assert abs(neutral - start) < 1.5     # sin rumbo
    assert earth < start - 2              # pierde más de lo que gana
    assert nest > neutral > earth


def test_unknown_mutation_physics_is_rejected():
    old, config.NEURON_MUTATION = config.NEURON_MUTATION, "inventada"
    try:
        g = G.random_minimal(jax.random.PRNGKey(0))
        with pytest.raises(ValueError):
            G.mutate(g, jax.random.PRNGKey(1))
    finally:
        config.NEURON_MUTATION = old


def test_defaults_are_the_ladder_physics():
    """ADR-019 (cierre de P0): la física de la herencia de toda la escalera, y determinista."""
    assert (config.NEURON_MUTATION, config.MUTATION_RATES, config.CPPN_MUTATION) == ("neutral", "fijas", "neutral_corregida")
    assert (config.REPRODUCTION, config.BIRTH_PLACEMENT, config.N_HIDDEN_INIT) == ("asexual", "cerca", 8)
    g = G.random_minimal(jax.random.PRNGKey(3))
    a = G.mutate(g, jax.random.PRNGKey(4))
    b = G.mutate(g, jax.random.PRNGKey(4))
    assert np.array_equal(np.asarray(a.hid_mask), np.asarray(b.hid_mask))


def _struct(rates: str, cppn: str, rounds: int = 200, n: int = 256):
    old = config.MUTATION_RATES, config.CPPN_MUTATION
    config.MUTATION_RATES, config.CPPN_MUTATION = rates, cppn
    try:
        mutate = jax.jit(jax.vmap(lambda g, k: G.mutate(g, k)))
        g = jax.vmap(G.random_minimal)(jax.random.split(jax.random.PRNGKey(0), n))
        for r in range(rounds):
            g = mutate(g, jax.random.split(jax.random.PRNGKey(r + 1), n))
        life = np.asarray(g.life, np.float32)
        nodes = float(np.mean(np.sum(np.asarray(g.node_mask), axis=-1)))
        edges = float(np.mean(np.sum(np.asarray(g.W_mask), axis=(-2, -1))))
        return life[:, 2], life[:, 3], nodes, edges
    finally:
        config.MUTATION_RATES, config.CPPN_MUTATION = old


def test_fixed_rates_do_not_drift():
    sig, rate, _, _ = _struct("fijas", "nest")
    assert np.allclose(sig, config.SIGMA_INIT, atol=1e-3) and np.allclose(rate, 1.0)
    sig_e, rate_e, _, _ = _struct("evolutivas", "nest")
    assert np.std(rate_e) > 0.1 and np.std(sig_e) > 0.01


def test_neutral_cppn_grows_less_than_nest():
    _, _, nest, _ = _struct("evolutivas", "nest")
    _, _, neutral, _ = _struct("evolutivas", "neutral")
    assert nest > neutral + 1


def test_corrected_cppn_keeps_its_edges():
    """ADR-019: sin selección, la neutral pierde aristas sola. En la corregida cada operador tiene su
    inverso: dividir suma un nodo y una arista y contraer los quita, así que aristas − nodos ocultos
    se queda en las 48 iniciales (los nodos solo se extienden desde 0, como un paseo con suelo)."""
    start, io = 48.0, config.CPPN_IN + config.CPPN_OUT
    _, _, n_neu, e_neu = _struct("fijas", "neutral", rounds=400)
    _, _, n_fix, e_fix = _struct("fijas", "neutral_corregida", rounds=400)
    assert abs((e_fix - (n_fix - io)) - start) < 1.5
    assert e_neu - (n_neu - io) < start - 3


def test_contracting_a_node_keeps_its_neighbours_joined():
    """Quitar un nodo k lo contrae: cada entrada y cada salida de k siguen unidas, con el mínimo de
    aristas (la primera entrada con cada salida y cada entrada con la primera salida)."""
    old = config.CPPN_MUTATION, config.MUTATION_RATES
    config.CPPN_MUTATION, config.MUTATION_RATES = "neutral_corregida", "fijas"
    try:
        g = G.random_minimal(jax.random.PRNGKey(0))
        mutate = jax.jit(G.mutate)
        hidden = np.zeros(config.CPPN_NODES, bool)
        hidden[config.CPPN_IN:config.CPPN_NODES - config.CPPN_OUT] = True
        seen = 0
        for r in range(4000):
            h = mutate(g, jax.random.PRNGKey(r))
            nm0, nm1 = np.asarray(g.node_mask), np.asarray(h.node_mask)
            if (nm1 & hidden).sum() == (nm0 & hidden).sum() - 1:  # se quitó un nodo
                gone = int(np.flatnonzero(nm0 & ~nm1)[0])
                w0, m0 = np.asarray(g.W, np.float32), np.asarray(g.W_mask)
                m1 = np.asarray(h.W_mask)
                ins, outs = np.flatnonzero(m0[:, gone]), np.flatnonzero(m0[gone, :])
                assert len(ins) >= 1 and len(outs) >= 1  # nunca hay nodos ocultos aislados
                for b in outs:
                    assert m1[ins[0], b], (ins[0], gone, b)
                for a in ins:
                    assert m1[a, outs[0]], (a, gone, outs[0])
                if len(ins) == 1 and len(outs) == 1 and not m0[ins[0], outs[0]]:  # inverso de dividir
                    w = float(np.asarray(h.W, np.float32)[ins[0], outs[0]])
                    a_k, k_b = w0[ins[0], gone], w0[gone, outs[0]]
                    # el producto se toma tras la perturbación σ = 0,05 de los dos pesos (≤ 4σ cada uno)
                    assert abs(w - a_k * k_b) < 0.2 * (abs(a_k) + abs(k_b)) + 0.05
                seen += 1
            g = h
        assert seen >= 3
    finally:
        config.CPPN_MUTATION, config.MUTATION_RATES = old


def test_unknown_rates_or_cppn_mode_is_rejected():
    g = G.random_minimal(jax.random.PRNGKey(0))
    for name in ("MUTATION_RATES", "CPPN_MUTATION"):
        old = getattr(config, name)
        setattr(config, name, "inventada")
        try:
            with pytest.raises(ValueError):
                G.mutate(g, jax.random.PRNGKey(1))
        finally:
            setattr(config, name, old)
