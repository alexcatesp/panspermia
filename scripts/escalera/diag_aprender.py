"""Diagnóstico del aprendizaje (solo observa; decisión del responsable, 22-10, 20:57).

Para un mundo guardado (época dada), por semilla:
  A. ¿Quién puede aprender? Fracción de vivos con alguna oculta expresada, con alguna moduladora
     expresada (sin ella m = 0 y no hay plasticidad) y con sinapsis plásticas (η·g ≠ 0).
  B. Suelo de ruido del VA: una época plástica (P) y una congelada (F) desde el mismo estado, como el
     runner, y tres congeladas con una mariposa (un bicho desplazado 0,001 u). VA = (P − F) / F;
     ruido = (F_k − F) / F.
  C. ¿Nota el cerebro un bocado? 200 pasos plásticos sin nacimientos: cambio del canal de energía
     por paso cuando la energía sube, frente al cambio típico de los canales de los rayos; y
     correlación entre la modulación m y la subida de energía.

Uso: python diag_aprender.py <run> --config K=V ... --jsonl salida.jsonl [--seeds 0 1] [--epoch 300]
"""
import argparse, json, math, shutil, tempfile
from pathlib import Path

import jax, jax.numpy as jnp, numpy as np
import orbax.checkpoint as ocp

from panspermia import brain, config as C, island, world

E_IDX = C.N_RAYS * C.RAY_CHANNELS


def load(run: Path, seed: int, epoch: int):
    template = island.init_island(seed, b"fase1d-w0", n_max=C.N_MAX, n_init=C.N_INIT)
    with tempfile.TemporaryDirectory() as tmp:
        shutil.copytree(run / f"s{seed}" / "checkpoints" / str(epoch), Path(tmp) / str(epoch))
        return ocp.CheckpointManager(Path(tmp)).restore(
            epoch, args=ocp.args.StandardRestore(jax.tree.map(ocp.utils.to_shape_dtype_struct, template)))


def capacity(s):
    a = np.asarray(s.alive)
    mask = np.asarray(s.genome.hid_mask)[a]
    mod = mask & np.asarray(s.genome.hid_type)[a]
    eg = np.abs(np.asarray(s.pheno.eta, np.float32) * np.asarray(s.pheno.g, np.float32))[a]
    plastic_syn = eg.reshape(eg.shape[0], -1).max(1) > 0
    return {"n": int(a.sum()), "frac_hidden": float(mask.any(1).mean()), "frac_mod": float(mod.any(1).mean()),
            "mod_mean": float(mod.sum(1).mean()), "frac_can_learn": float((mod.any(1) & plastic_syn).mean())}


def copy(s):
    return jax.tree.map(jnp.copy, s)


def noise_floor(s):
    _, st_p = island.epoch(copy(s), C.EPOCH_STEPS, plastic=True)
    _, st_f = island.epoch(copy(s), C.EPOCH_STEPS, plastic=False)
    p, f = float(st_p["intake"]), float(st_f["intake"])
    idx = np.flatnonzero(np.asarray(s.alive))
    noise = []
    for k in (1, 2, 3):
        i = int(idx[k * len(idx) // 4])
        sk = copy(s)
        sk = sk.replace(pos=sk.pos.at[i, 0].add(1e-3))
        _, st_k = island.epoch(sk, C.EPOCH_STEPS, plastic=False)
        noise.append((float(st_k["intake"]) - f) / f)
    return {"va_intake": (p - f) / f, "noise_frozen": noise, "noise_abs_max": float(np.max(np.abs(noise)))}


def bite(s, T=200):
    def body(c, _):
        c2, _ps = island.world_step(c, births=False)
        obs, _n = world.sense(c2, world.neighbors(c2.pos, c2.alive))
        m = brain.modulation(c2.h, c2.genome.hid_mask, c2.genome.hid_type)
        return c2, (c2.energy, c2.alive, obs, m)
    obs0, _ = world.sense(s, world.neighbors(s.pos, s.alive))
    _, (E, alive, obs, m) = jax.jit(lambda st: jax.lax.scan(body, st, None, length=T))(s)
    E = np.concatenate([np.asarray(s.energy)[None], np.asarray(E)])
    alive = np.concatenate([np.asarray(s.alive)[None], np.asarray(alive)])
    obs = np.concatenate([np.asarray(obs0)[None], np.asarray(obs)])
    m = np.asarray(m)
    both = alive[1:] & alive[:-1]
    dE = (E[1:] - E[:-1])[both]
    dobs = np.abs(obs[1:] - obs[:-1])
    d_energy = dobs[..., E_IDX][both]
    rays = dobs[..., :E_IDX][both]
    up = dE > 0
    has_mod = (np.asarray(s.genome.hid_mask) & np.asarray(s.genome.hid_type)).any(1)
    sel = both & has_mod[None]
    mm, de = m[sel], (E[1:] - E[:-1])[sel]
    corr = float(np.corrcoef(mm, de)[0, 1]) if sel.sum() > 10 and mm.std() > 0 else None
    return {"frac_steps_energy_up": float(up.mean()), "dE_up_mean": float(dE[up].mean()) if up.any() else 0.0,
            "dobs_energy_up_mean": float(d_energy[up].mean()) if up.any() else 0.0,
            "dobs_energy_up_p99": float(np.percentile(d_energy[up], 99)) if up.any() else 0.0,
            "dobs_rays_mean": float(rays.mean()), "dobs_rays_p99": float(np.percentile(rays, 99)),
            "corr_m_dE": corr, "n_mod_steps": int(sel.sum())}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("run", type=Path)
    p.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2, 3, 4])
    p.add_argument("--epoch", type=int, default=300)
    p.add_argument("--config", nargs="*", default=[])
    p.add_argument("--jsonl", type=Path, required=True)
    p.add_argument("--parts", default="ABC")
    a = p.parse_args()
    island.setup_determinism()
    for kv in a.config:
        k, v = kv.split("=")
        setattr(C, k, type(getattr(C, k))(float(v)) if not isinstance(getattr(C, k), str) else v)
    for seed in a.seeds:
        s = load(a.run, seed, a.epoch)
        row = {"run": a.run.name, "seed": seed, "epoch": a.epoch, "config": a.config}
        if "A" in a.parts: row.update(capacity(s))
        if "C" in a.parts: row.update(bite(s))
        if "B" in a.parts: row.update(noise_floor(s))
        print(json.dumps({k: round(v, 5) if isinstance(v, float) else v for k, v in row.items()}), flush=True)
        with a.jsonl.open("a") as f:
            f.write(json.dumps(row) + "\n")
