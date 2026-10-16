"""Grabación de épocas para el visor (spec §Persistencia: vídeo cada 50 épocas).

`record_epoch` avanza la isla exactamente igual que `island.epoch` (mismo `world_step`, misma
clave por paso) y además devuelve fotogramas cuantizados. `save_recording` los escribe como un
binario gzip + cabecera JSON que el visor web lee directamente.

Formato: `<nombre>.json` describe cada array (dtype, forma, desplazamiento en bytes) dentro de
`<nombre>.bin.gz` (arrays C-contiguos, little-endian, concatenados).
"""
from __future__ import annotations

import functools
import gzip
import json
import math
from pathlib import Path

import jax
import jax.numpy as jnp
import numpy as np

from . import config as C
from . import metrics
from .island import IslandState, world_step


def snapshot(state: IslandState) -> dict[str, jax.Array]:
    """Fotograma cuantizado de los N slots."""
    ph = state.pheno
    alive = state.alive.astype(jnp.uint8) << 7
    return {
        "pos": jnp.round(state.pos / C.WORLD_L * 65535).astype(jnp.uint16),
        "angle": jnp.round(state.angle / (2 * math.pi) * 255).astype(jnp.uint8),
        "energy": jnp.clip(state.energy / C.REPRO_THRESHOLD_BOUNDS[1] * 255, 0, 255).astype(jnp.uint8),
        "signal": jnp.round((state.signal + 1) / 2 * 255).astype(jnp.uint8),
        "color": jnp.round(ph.color * 255).astype(jnp.uint8),
        "radius": jnp.round(ph.radius * 16).astype(jnp.uint8),
        "flags": state.flags | alive,
        "clade": state.lineage.clade,
        "uid": state.lineage.uid,
    }


def _resource_frame(state: IslandState) -> jax.Array:
    g = C.RECORD_RES_GRID
    f = C.RESOURCE_GRID // g
    r = state.resources.reshape(g, f, g, f).mean(axis=(1, 3))
    return jnp.clip(r / (2 * C.K_MEAN) * 255, 0, 255).astype(jnp.uint8)


def _chem_frame(state: IslandState) -> jax.Array:
    g = C.RECORD_RES_GRID
    f = C.RESOURCE_GRID // g
    c = state.chem.reshape(C.N_CHEM, g, f, g, f).mean(axis=(2, 4))
    return jnp.clip(jnp.tanh(c / C.CHEM_OBS_SCALE) * 255, 0, 255).astype(jnp.uint8)


@functools.partial(jax.jit, static_argnames=("k",), donate_argnums=(0,))
def record_epoch(state: IslandState, k: int = C.EPOCH_STEPS):
    """Como `island.epoch`, pero devuelve también los fotogramas (cada RECORD_STRIDE pasos)."""
    state = state.replace(comm_hist=jnp.zeros_like(state.comm_hist))

    def body(s, _):
        s, st = world_step(s, None)
        return s, (st, snapshot(s), _resource_frame(s), _chem_frame(s))

    state, (per_step, frames, res, chem) = jax.lax.scan(body, state, None, length=k)
    frames = jax.tree.map(lambda x: x[C.RECORD_STRIDE - 1::C.RECORD_STRIDE], frames)
    frames["chem"] = chem[C.RECORD_RES_STRIDE - 1::C.RECORD_RES_STRIDE]
    res = res[C.RECORD_RES_STRIDE - 1::C.RECORD_RES_STRIDE]
    return state, metrics.epoch_stats(state, per_step), frames, res


def save_recording(path: Path, frames: dict, resources, meta: dict) -> None:
    """Escribe `path.json` + `path.bin.gz`."""
    arrays = {**{k: np.ascontiguousarray(np.asarray(v)) for k, v in jax.device_get(frames).items()},
              "resources": np.ascontiguousarray(np.asarray(jax.device_get(resources)))}
    header = {"meta": meta, "arrays": {}}
    offset = 0
    chunks = []
    for name, a in arrays.items():
        a = a.astype(a.dtype.newbyteorder("<"))
        header["arrays"][name] = {"dtype": a.dtype.str.lstrip("<|"), "shape": list(a.shape),
                                  "offset": offset}
        chunks.append(a.tobytes())
        offset += a.nbytes
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path.with_suffix(".bin.gz"), "wb", compresslevel=6) as f:
        for c in chunks:
            f.write(c)
    path.with_suffix(".json").write_text(json.dumps(header))
