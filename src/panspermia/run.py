"""Runner de una isla aislada (red de tamaño 1).

Por época: avanza la isla, vuelca estadísticas (Parquet + `stats/summary.json` para el visor) y
calcula en el host el descriptor conductual, la novedad, los grupos conductuales y la actividad
de Bedau-Packard. Además:
- cada FROZEN_PLASTICITY_TEST_EVERY épocas, prueba emparejada con plasticidad congelada;
- cada VIDEO_EVERY épocas, graba la época para el visor (`recordings/`);
- cada CAPABILITY_TEST_EVERY épocas, batería de capacidad; si supera un umbral, PAUSA (ADR-007);
- cada CHECKPOINT_EVERY épocas, checkpoint Orbax (+ archivo de novedad y actividad).

Uso:
    python -m panspermia.run --seed 0 --epochs 100 --out runs/s0
    duckdb -c "SELECT epoch, population, births FROM 'runs/s0/stats/*.parquet' ORDER BY epoch"

Pausa por capacidad: se escribe `CAPABILITY_PAUSE.json` y el proceso termina con código 3. Para
continuar, una persona revisa el informe y crea `CAPABILITY_REVIEW.json` con
{"reviewed_by": "...", "notes": "...", "thresholds": {...umbrales nuevos...}}.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from .island import setup_determinism

setup_determinism()

import jax
import jax.numpy as jnp
import numpy as np
import orbax.checkpoint as ocp
import pyarrow as pa
import pyarrow.parquet as pq

from . import capability, island, metrics, record
from . import config as C

PAUSE_FILE = "CAPABILITY_PAUSE.json"
REVIEW_FILE = "CAPABILITY_REVIEW.json"
EXIT_PAUSED = 3


class CapabilityPause(Exception):
    pass


def _checkpoint_manager(path: Path) -> ocp.CheckpointManager:
    options = ocp.CheckpointManagerOptions(
        max_to_keep=5, keep_period=100, save_interval_steps=C.CHECKPOINT_EVERY,
        enable_async_checkpointing=False,  # `epoch` dona los buffers del estado
    )
    return ocp.CheckpointManager(path.resolve(), options=options)


def _flush(rows: list[dict], all_rows: list[dict], stats_dir: Path) -> None:
    if rows:
        pq.write_table(pa.Table.from_pylist(rows), stats_dir / f"part_{rows[0]['epoch']:06d}.parquet")
        rows.clear()
    (stats_dir / "summary.json").write_text(json.dumps(all_rows))


def _thresholds(out: Path) -> dict[str, float]:
    """Umbrales vigentes. Bloquea si hay una pausa sin revisión posterior."""
    pause, review = out / PAUSE_FILE, out / REVIEW_FILE
    thresholds = dict(C.CAPABILITY_PAUSE_THRESHOLDS)
    if review.exists():
        thresholds.update(json.loads(review.read_text()).get("thresholds", {}))
    if pause.exists():
        if not review.exists() or review.stat().st_mtime < pause.stat().st_mtime:
            raise CapabilityPause(
                f"isla en pausa por capacidad: revisa {pause} y crea {review} para continuar")
        pause.rename(out / f"CAPABILITY_PAUSE.reviewed.{int(pause.stat().st_mtime)}.json")
    return thresholds


def _clean(d: dict) -> dict:
    return {k: (v.item() if isinstance(v, np.generic) else v) for k, v in d.items()}


def next_extinct_streak(streak: int, population: int) -> int:
    """Épocas seguidas que acaban por debajo de N_MIN_REINJECT. No basta con exigir población 0:
    en E0 un superviviente suelto de la reinyección reiniciaba la cuenta y la parada no actuaba."""
    return streak + 1 if population < C.N_MIN_REINJECT else 0


def run(seed: int, epochs: int, out: Path, node_id: bytes, n_max: int, n_init: int,
        reinject: bool = True, verbose: bool = True, env_overrides: dict | None = None,
        plastic: bool = True, experiment: dict | None = None) -> dict:
    """Ejecuta una isla. `env_overrides` sustituye campos del entorno; `plastic=False` desactiva la
    plasticidad durante toda la evolución (gemelo de control, fase 1d); `experiment` se guarda en
    run.json para trazabilidad."""
    out.mkdir(parents=True, exist_ok=True)
    stats_dir = out / "stats"
    stats_dir.mkdir(exist_ok=True)
    thresholds = _thresholds(out)
    mngr = _checkpoint_manager(out / "checkpoints")

    state = island.init_island(seed, node_id, n_max=n_max, n_init=n_init, env_overrides=env_overrides)
    start = 0
    archive = metrics.NoveltyArchive()
    activity = metrics.ActivityTracker()
    all_rows: list[dict] = []
    if mngr.latest_step() is not None:
        start = mngr.latest_step()
        abstract = jax.tree.map(ocp.utils.to_shape_dtype_struct, state)
        state = mngr.restore(start, args=ocp.args.StandardRestore(abstract))
        if (out / "novelty_archive.npy").exists():
            archive = metrics.NoveltyArchive(np.load(out / "novelty_archive.npy"))
        if (out / "activity.json").exists():
            activity = metrics.ActivityTracker(
                {int(k): v for k, v in json.loads((out / "activity.json").read_text()).items()})
        if (stats_dir / "summary.json").exists():
            all_rows = [r for r in json.loads((stats_dir / "summary.json").read_text())
                        if r["epoch"] <= start]
        for f in stats_dir.glob("part_*.parquet"):  # partes posteriores al checkpoint
            if int(f.stem.split("_")[1]) > start:
                f.unlink()
        if verbose:
            print(f"reanudando desde la época {start}")
    meta = {
        "substrate_version": C.SUBSTRATE_VERSION, "seed": seed, "node_id": node_id.hex(),
        "n_max": n_max, "n_init": n_init, "epoch_steps": C.EPOCH_STEPS, "reinject": reinject,
        "world_l": C.WORLD_L, "jax": jax.__version__, "device": str(jax.devices()[0]),
        "capability_thresholds": thresholds,
        "plastic": plastic, "env_overrides": env_overrides or {}, "experiment": experiment or {},
    }
    (out / "run.json").write_text(json.dumps(meta, indent=2))

    rows: list[dict] = []
    extinct_at = None
    extinct_streak = 0  # épocas seguidas que acaban por debajo de N_MIN_REINJECT (la reinyección no prende)
    stopped_extinct = False
    paused = None
    for e in range(start + 1, epochs + 1):
        t0 = time.perf_counter()
        frozen_test = plastic and e % C.FROZEN_PLASTICITY_TEST_EVERY == 0
        if frozen_test:
            uid0, alive0 = jax.device_get((state.lineage.uid, state.alive))
            clone = jax.tree.map(jnp.copy, state)
        if e % C.VIDEO_EVERY == 0:
            state, stats, frames, res = record.record_epoch(state, C.EPOCH_STEPS, plastic=plastic)
            record.save_recording(out / "recordings" / f"epoch_{e:06d}", frames, res,
                                  {"epoch": e, "seed": seed, "steps": C.EPOCH_STEPS,
                                   "stride": C.RECORD_STRIDE, "res_stride": C.RECORD_RES_STRIDE,
                                   "world_l": C.WORLD_L, "n_max": n_max})
        else:
            state, stats = island.epoch(state, C.EPOCH_STEPS, plastic=plastic)
        stats = jax.device_get(stats)
        series = {k[7:]: np.asarray(stats.pop(k)) for k in list(stats) if k.startswith("series_")}
        stats = {k: np.asarray(v).item() for k, v in stats.items()}

        row: dict = {"epoch": e, "reinjected": 0, **stats}
        row.update(metrics.temporal_metrics(series, state.env, int(state.step) - C.EPOCH_STEPS))
        view = metrics.host_view(state)
        desc = metrics.descriptors(view)
        rng = np.random.default_rng([seed, e])
        sample = desc[rng.choice(len(desc), min(len(desc), C.NOVELTY_SAMPLE), replace=False)] \
            if len(desc) else desc
        row.update(archive.update(sample))
        row.update(metrics.behavior_groups(sample, seed * 1_000_003 + e))
        row.update(activity.update(view["clade"], view["alive"]))
        if len(desc):
            row.update({f"desc_{n}": float(v) for n, v in zip(metrics.DESCRIPTOR_NAMES, desc.mean(0))})

        if frozen_test:
            clone, st_f = island.epoch(clone, C.EPOCH_STEPS, plastic=False)
            uid_f, alive_f = jax.device_get((clone.lineage.uid, clone.alive))
            st_f = {k: np.asarray(v).item() for k, v in jax.device_get(st_f).items()
                    if not k.startswith("series_")}
            del clone
            s_plastic = metrics.learning_survival(uid0, alive0, view["uid"], view["alive"])
            s_frozen = metrics.learning_survival(uid0, alive0, uid_f, alive_f)
            row.update({"survival_plastic": s_plastic, "survival_frozen": s_frozen,
                        "learning_value": s_plastic - s_frozen})
            # sonda emparejada a nivel de población (ADR-010, fase 1d): misma época, mismo azar
            row.update(metrics.paired_learning_value(stats, st_f))

        if e % C.CAPABILITY_TEST_EVERY == 0:
            battery = capability.run_battery(state, stats["comm_mi_bits"])
            row.update({f"cap_{k}": v for k, v in battery.items()})
            hit = capability.exceeded(battery, thresholds)
            if hit:
                paused = {"epoch": e, "exceeded": hit, "metrics": battery, "thresholds": thresholds,
                          "seed": seed, "node_id": node_id.hex()}

        if stats["population_min"] == 0 and extinct_at is None:
            extinct_at = e
        extinct_streak = next_extinct_streak(extinct_streak, stats["population"])
        stopped_extinct = extinct_streak >= C.EXTINCT_STOP_EPOCHS
        if reinject and stats["population"] < C.N_MIN_REINJECT:
            before = stats["population"]
            state = island.reinject(state, C.N_MIN_REINJECT)
            row["reinjected"] = int(np.asarray(state.alive).sum()) - before
        row["seconds"] = time.perf_counter() - t0
        row = _clean(row)
        rows.append(row)
        all_rows.append(row)
        if verbose:
            extra = f" · VA {row['va_population']:+.3f}" if frozen_test else ""
            print(f"época {e:5d} · {row['seconds']:5.2f}s · pob {stats['population']:5d} "
                  f"(mín {stats['population_min']:5d}) · nac {stats['births']:5d} · "
                  f"ataques† {stats['deaths_attack']:4d} · gen máx {stats['generation_max']:.0f} · "
                  f"ocultas {stats['hidden_mean']:.2f} · archivo {row['archive_size']} · "
                  f"silueta {row['groups_silhouette']:.2f} (k={row['groups_k']}){extra}", flush=True)

        if e % C.CHECKPOINT_EVERY == 0 or paused or stopped_extinct:
            _flush(rows, all_rows, stats_dir)
            # vía host: tras un restore, la ruta de Orbax por memoria fija (pinned) se agota en
            # WSL2 con N = 4096 (RESOURCE_EXHAUSTED en el primer guardado); device_get es exacto
            mngr.save(e, args=ocp.args.StandardSave(jax.device_get(state)),
                      force=bool(paused) or stopped_extinct)
            np.save(out / "novelty_archive.npy", archive.archive)
            (out / "activity.json").write_text(json.dumps(activity.activity))
        if paused:
            (out / PAUSE_FILE).write_text(json.dumps(paused, indent=2))
            if verbose:
                print(f"PAUSA por capacidad en la época {e}: {paused['exceeded']}", flush=True)
            break
        if stopped_extinct:
            if verbose:
                print(f"PARADA: {C.EXTINCT_STOP_EPOCHS} épocas seguidas extinta (la reinyección no prende)",
                      flush=True)
            break
    _flush(rows, all_rows, stats_dir)
    mngr.wait_until_finished()
    mngr.close()
    return {"extinct_at": extinct_at, "final_population": int(np.asarray(state.alive).sum()),
            "paused": paused is not None, "stopped_extinct": stopped_extinct}


def main() -> None:
    p = argparse.ArgumentParser(description="Ejecuta una isla de Panspermia.")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--epochs", type=int, default=100)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--node-id", default="local", help="identificador de nodo (texto)")
    p.add_argument("--n-max", type=int, default=C.N_MAX)
    p.add_argument("--n-init", type=int, default=C.N_INIT)
    p.add_argument("--no-reinject", action="store_true")
    a = p.parse_args()
    try:
        result = run(a.seed, a.epochs, a.out, a.node_id.encode(), a.n_max, a.n_init,
                     reinject=not a.no_reinject)
    except CapabilityPause as exc:
        print(exc, file=sys.stderr)
        sys.exit(EXIT_PAUSED)
    print(json.dumps(result))
    if result["paused"]:
        sys.exit(EXIT_PAUSED)


if __name__ == "__main__":
    main()
