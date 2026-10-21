"""Sonda de hambre (solo observa): ¿cambia la conducta según la energía que siente el bicho?

Para un mundo guardado (checkpoint), dos copias idénticas salvo la entrada de energía del cerebro
(canal `tanh(E / E_OBS_SCALE)` de las observaciones), fijada en "hambriento" (E = 5) o "saciado"
(E = 100). La energía real, la física, el azar y la plasticidad siguen igual: cualquier diferencia de
conducta la causa solo lo que el bicho siente de su energía.

1. Respuesta inmediata: acciones con las mismas observaciones salvo la energía (empuje y giro).
2. Conducta durante T pasos (sin nacimientos): recorrido, desplazamiento neto y velocidad,
   emparejados por bicho (solo los que siguen vivos en las dos copias).

Nulo: genomas al azar (`--azar`), sin selección; y P0 (la energía no cambia nunca, así que la
selección no puede usarla).

Lectura (bitácora, 21-10, 22:48): hay «hambre» si en ≥ 4 de 5 mundos más del 90 % de los bichos
responden en la misma dirección (frac_pos o frac_neg; frac_zero son los que no cambian), la dirección
coincide entre mundos e imm_dthrust_abs_rel supera a los dos nulos.

Uso: python scripts/hunger_probe.py runs/fase1d/P3-escaso --jsonl runs/fase1d/_hambre.jsonl
     (CPU: JAX_PLATFORMS=cpu; con comida dispersa, --kcut 1.5)
"""
import argparse, json, math, shutil, sys, tempfile
from pathlib import Path

import jax, jax.numpy as jnp, numpy as np
import orbax.checkpoint as ocp

from panspermia import brain, config as C, island, world

E_IDX = C.N_RAYS * C.RAY_CHANNELS  # primer canal propio: energía
LOW, HIGH = 5.0, 100.0
_sense = world.sense


def load(run: Path, seed: int, epoch: int, node: bytes):
    template = island.init_island(seed, node, n_max=C.N_MAX, n_init=C.N_INIT)
    with tempfile.TemporaryDirectory() as tmp:
        shutil.copytree(run / f"s{seed}" / "checkpoints" / str(epoch), Path(tmp) / str(epoch))
        return ocp.CheckpointManager(Path(tmp)).restore(
            epoch, args=ocp.args.StandardRestore(jax.tree.map(ocp.utils.to_shape_dtype_struct, template)))


def clamped(e: float):
    v = math.tanh(e / C.E_OBS_SCALE)
    def sense(state, cand):
        obs, n = _sense(state, cand)
        return obs.at[:, E_IDX].set(jnp.where(state.alive, v, 0.0)), n
    return sense


def immediate(s):
    cand = world.neighbors(s.pos, s.alive)
    obs, _ = _sense(s, cand)
    a = np.asarray(s.alive)
    assert np.allclose(np.asarray(obs[:, E_IDX])[a], np.tanh(np.asarray(s.energy)[a] / C.E_OBS_SCALE), atol=1e-5)
    out = {}
    for name, e in (("low", LOW), ("high", HIGH)):
        o = obs.at[:, E_IDX].set(math.tanh(e / C.E_OBS_SCALE))
        act, *_ = brain.step(s.w, s.h, o, s.genome.hid_mask)
        out[name] = (np.asarray(act[:, 0] * s.pheno.max_thrust)[a], np.asarray(act[:, 1])[a])
    dthr = out["low"][0] - out["high"][0]
    dturn = np.abs(out["low"][1]) - np.abs(out["high"][1])
    sd = float(np.std(out["high"][0])) or 1.0
    return {"n": int(a.sum()), "imm_thrust_low": float(out["low"][0].mean()), "imm_thrust_high": float(out["high"][0].mean()),
            "imm_dthrust": float(dthr.mean()), "imm_dthrust_frac_pos": float(np.mean(dthr > 1e-6)),
            "imm_dthrust_frac_neg": float(np.mean(dthr < -1e-6)), "imm_dthrust_frac_zero": float(np.mean(np.abs(dthr) <= 1e-6)),
            "imm_dthrust_abs": float(np.abs(dthr).mean()), "imm_dthrust_abs_rel": float(np.abs(dthr).mean() / sd),
            "imm_frac_sensitive": float(np.mean(np.abs(dthr) > 0.05 * sd)), "imm_dturn_abs": float(dturn.mean())}


def rollout(s, e: float, T: int):
    jax.clear_caches()
    world.sense = clamped(e)
    try:
        def body(c, _):
            c2, _ps = island.world_step(c, births=False)
            return c2, (c2.pos, c2.alive, jnp.linalg.norm(c2.vel, axis=-1))
        _, (pos, alive, speed) = jax.jit(lambda st: jax.lax.scan(body, st, None, length=T))(s)
    finally:
        world.sense = _sense
        jax.clear_caches()
    pos = np.concatenate([np.asarray(s.pos)[None], np.asarray(pos)])
    d = np.diff(pos, axis=0)
    d = (d + C.WORLD_L / 2) % C.WORLD_L - C.WORLD_L / 2  # toro
    path = np.linalg.norm(d, axis=-1).sum(0)
    net = np.linalg.norm(d.sum(0), axis=-1)
    return path, net, np.asarray(speed).mean(0), np.asarray(alive).all(0)


def probe(s, T: int):
    r = immediate(s)
    lo, hi = rollout(s, LOW, T), rollout(s, HIGH, T)
    ok = np.asarray(s.alive) & lo[3] & hi[3]
    dpath = lo[0][ok] - hi[0][ok]
    sd = float(np.std(hi[0][ok])) or 1.0
    r.update({"T": T, "n_roll": int(ok.sum()),
              "path_low": float(lo[0][ok].mean()), "path_high": float(hi[0][ok].mean()),
              "net_low": float(lo[1][ok].mean()), "net_high": float(hi[1][ok].mean()),
              "speed_low": float(lo[2][ok].mean()), "speed_high": float(hi[2][ok].mean()),
              "dpath_frac_pos": float(np.mean(dpath > 0)), "dpath_abs_rel": float(np.abs(dpath).mean() / sd)})
    return r


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("run", type=Path)
    p.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2, 3, 4])
    p.add_argument("--epoch", type=int, default=300)
    p.add_argument("--steps", type=int, default=200)
    p.add_argument("--node", default="fase1d-w0")
    p.add_argument("--kcut", type=float, default=None)
    p.add_argument("--azar", action="store_true", help="genomas al azar con el entorno del checkpoint (nulo)")
    p.add_argument("--jsonl", type=Path, required=True)
    a = p.parse_args()
    island.setup_determinism()
    if a.kcut is not None:
        C.K_CUT = a.kcut
    for seed in a.seeds:
        s = load(a.run, seed, a.epoch, a.node.encode())
        if a.azar:
            fresh = island.init_island(seed, a.node.encode(), n_max=C.N_MAX, n_init=C.N_MAX)
            s = fresh.replace(env=s.env, resources=s.resources, energy=jnp.where(fresh.alive, s.energy.mean(), 0.0))
        row = {"run": a.run.name + (" (azar)" if a.azar else ""), "seed": seed, "epoch": a.epoch, **probe(s, a.steps)}
        print(json.dumps({k: round(v, 4) if isinstance(v, float) else v for k, v in row.items()}), flush=True)
        with a.jsonl.open("a") as f:
            f.write(json.dumps(row) + "\n")
