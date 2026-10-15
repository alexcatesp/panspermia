"""Red recurrente con plasticidad hebbiana ABCD modulada (spec §Cerebro). Sin retropropagación."""

def step(pheno, w, h, obs):
    """Un paso neuronal: devuelve (acciones, h_nuevo, actividades pre/post)."""
    raise NotImplementedError

def plasticity(pheno, w, pre, post, m):
    """Δw = η·g·m·(A·xi·xj + B·xi + C·xj + D), recortado a |w| <= W_MAX."""
    raise NotImplementedError
