"""Runner de una isla aislada (red de tamaño 1): épocas, estadísticas Parquet y checkpoints Orbax.

Uso:
    python -m panspermia.run --seed 0 --epochs 100 --out runs/s0
    duckdb -c "SELECT epoch, population, births FROM 'runs/s0/stats/*.parquet' ORDER BY epoch"
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from .island import setup_determinism

setup_determinism()

import jax
import numpy as np
import orbax.checkpoint as ocp
import pyarrow as pa
import pyarrow.parquet as pq

from . import config as C
from . import island


def _checkpoint_manager(path: Path) -> ocp.CheckpointManager:
    options = ocp.CheckpointManagerOptions(
        max_to_keep=5, keep_period=100, save_interval_steps=C.CHECKPOINT_EVERY,
        enable_async_checkpointing=False,  # `epoch` dona los buffers del estado
    )
    return ocp.CheckpointManager(path.resolve(), options=options)


def _flush(rows: list[dict], stats_dir: Path) -> None:
    if not rows:
        return
    table = pa.Table.from_pylist(rows)
    pq.write_table(table, stats_dir / f"part_{rows[0]['epoch']:06d}.parquet")
    rows.clear()


def run(seed: int, epochs: int, out: Path, node_id: bytes, n_max: int, n_init: int,
        reinject: bool = True, verbose: bool = True) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    stats_dir = out / "stats"
    stats_dir.mkdir(exist_ok=True)
    mngr = _checkpoint_manager(out / "checkpoints")

    state = island.init_island(seed, node_id, n_max=n_max, n_init=n_init)
    start = 0
    if mngr.latest_step() is not None:
        start = mngr.latest_step()
        abstract = jax.tree.map(ocp.utils.to_shape_dtype_struct, state)
        state = mngr.restore(start, args=ocp.args.StandardRestore(abstract))
        if verbose:
            print(f"reanudando desde la época {start}")
    meta = {
        "substrate_version": C.SUBSTRATE_VERSION, "seed": seed, "node_id": node_id.hex(),
        "n_max": n_max, "n_init": n_init, "epoch_steps": C.EPOCH_STEPS, "reinject": reinject,
        "jax": jax.__version__, "device": str(jax.devices()[0]),
    }
    (out / "run.json").write_text(json.dumps(meta, indent=2))

    rows: list[dict] = []
    extinct_at = None
    for e in range(start + 1, epochs + 1):
        t0 = time.perf_counter()
        state, stats = island.epoch(state, C.EPOCH_STEPS)
        stats = {k: np.asarray(v).item() for k, v in jax.device_get(stats).items()}
        elapsed = time.perf_counter() - t0
        reinjected = 0
        if stats["population_min"] == 0 and extinct_at is None:
            extinct_at = e
        if reinject and stats["population"] < C.N_MIN_REINJECT:
            before = stats["population"]
            state = island.reinject(state, C.N_MIN_REINJECT)
            reinjected = int(np.asarray(state.alive).sum()) - before
        row = {"epoch": e, "seconds": elapsed, "reinjected": reinjected, **stats}
        rows.append(row)
        if verbose:
            print(f"época {e:5d} · {elapsed:5.2f}s · pob {stats['population']:5d} "
                  f"(mín {stats['population_min']:5d}) · nac {stats['births']:5d} · "
                  f"gen máx {stats['generation_max']:.0f} · ocultas {stats['hidden_mean']:.2f}",
                  flush=True)
        if e % C.CHECKPOINT_EVERY == 0:
            _flush(rows, stats_dir)
            mngr.save(e, args=ocp.args.StandardSave(state))
    _flush(rows, stats_dir)
    mngr.wait_until_finished()
    mngr.close()
    return {"extinct_at": extinct_at, "final_population": int(np.asarray(state.alive).sum())}


def main() -> None:
    p = argparse.ArgumentParser(description="Ejecuta una isla de Panspermia.")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--epochs", type=int, default=100)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--node-id", default="local", help="texto o hex del identificador de nodo")
    p.add_argument("--n-max", type=int, default=C.N_MAX)
    p.add_argument("--n-init", type=int, default=C.N_INIT)
    p.add_argument("--no-reinject", action="store_true")
    a = p.parse_args()
    result = run(a.seed, a.epochs, a.out, a.node_id.encode(), a.n_max, a.n_init,
                 reinject=not a.no_reinject)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
