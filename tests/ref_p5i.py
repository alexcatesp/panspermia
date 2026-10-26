"""Genera (o compara con) la referencia de 3.6.0 para el test bit a bit de C apagado (ADR-033).
Se ejecuta con el código de `escalera-veneno` (3.6.0) para escribir tests/data/p5i_360_<backend>.npz; el test de
`test_c.py` lo reproduce con 3.8.0 y DELTA_ON = 0. Condiciones de P5-inmediato sin rampas, para que el veneno actúe."""
import sys
import jax
import numpy as np

CFG = dict(ALGA_PER_AGENT=1, ALGA_PATCH_FAMILIES=1, K_CUT=1.7, EAT_MOVE_FACTOR=0.0, EAT_MOVE_RAMP_STEPS=0,
           K_MEAN_RAMP_STEPS=0, POISON_FACTOR=2.5, POISON_DELAY=0, POISON_RAMP_STEPS=0)
FIELDS = ("w", "h", "energy", "pos", "alive", "gut")


def run(config, island, steps=60, apply=True):
    """Con apply=False la configuración ya la ha puesto quien llama (en los tests, con monkeypatch, para no contaminar)."""
    for k, v in (CFG.items() if apply else ()):
        cur = getattr(config, k)
        setattr(config, k, float(v) if cur is None else type(cur)(v))
    jax.clear_caches()
    s = island.init_island(0, b"c-test", n_max=64, n_init=64)
    step = jax.jit(lambda c: island.world_step(c)[0])
    for _ in range(steps):
        s = step(s)
    return {f: np.asarray(getattr(s, f)) for f in FIELDS}


if __name__ == "__main__":
    from panspermia import config, island
    island.setup_determinism()  # como en conftest.py
    assert config.SUBSTRATE_VERSION == "3.6.0", config.SUBSTRATE_VERSION
    out = sys.argv[1]
    np.savez(out, **run(config, island))
    print(out, jax.default_backend())
