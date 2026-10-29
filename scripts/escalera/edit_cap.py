from pathlib import Path

base = Path(r"D:\Development\panspermia-fase1b")


def edit(rel, pairs):
    p = base / rel
    t = p.read_text(encoding="utf-8")
    for old, new in pairs:
        assert t.count(old) == 1, (rel, old[:70], t.count(old))
        t = t.replace(old, new)
    p.write_text(t, encoding="utf-8")
    print(rel, "ok")


edit("src/panspermia/capability.py", [
    ('''        step=jnp.int32(0), key=jax.random.PRNGKey(0), env=env, resources=resources,
''', '''        step=jnp.int32(0), key=jax.random.PRNGKey(0), env=env, resources=resources,
        chem=jnp.zeros((C.N_CHEM, C.RESOURCE_GRID, C.RESOURCE_GRID), jnp.float32),
        toxic_type=jnp.int32(0),
'''),
    ('''    return env.replace(regrow=jnp.float32(0.0), walls=jnp.asarray(walls))''',
     '''    return env.replace(regrow=jnp.float32(0.0), walls=jnp.asarray(walls), seasonal=jnp.float32(0.0))'''),
])

edit("tests/test_phase0_acceptance.py", [
    ('''def test_obs_dims_match_spec():
    assert config.OBS_DIM == 70
    assert config.N_PRE == 134 and config.N_POST == 69''',
     '''def test_obs_dims_match_spec():
    """Sustrato 2.x (ADR-008): 70 observaciones de la spec v1 + 9 químicas; 5 + 3 acciones."""
    assert config.OBS_DIM == 79 and config.ACT_DIM == 8
    assert config.N_PRE == 143 and config.N_POST == 72'''),
])

edit("tests/test_units.py", [
    ('''    actions = jnp.zeros((3, config.ACT_DIM)).at[:, 2].set(1.0)
    intake, res2 = world.eat(res, pos, jnp.array([True, True, True]), actions)
    eaten = np.asarray(res, np.float64) - np.asarray(res2, np.float64)
    assert np.isclose(eaten.sum(), float(jnp.sum(intake)), atol=1e-5)
    assert float(intake[0] + intake[1]) <= 0.3 + 1e-6''',
     '''    actions = jnp.zeros((3, config.ACT_DIM)).at[:, 2].set(1.0)
    chem = jnp.zeros((config.N_CHEM,) + res.shape)
    no_toxic = jnp.zeros(res.shape, bool)
    gain, intake, toxic_in, _, res2, _ = world.eat(res, chem, pos, jnp.array([True, True, True]),
                                                   actions, no_toxic)
    eaten = np.asarray(res, np.float64) - np.asarray(res2, np.float64)
    assert np.isclose(eaten.sum(), float(jnp.sum(intake)), atol=1e-5)
    assert float(intake[0] + intake[1]) <= 0.3 + 1e-6
    assert np.allclose(np.asarray(gain), np.asarray(intake)) and float(jnp.sum(toxic_in)) == 0.0'''),
])
