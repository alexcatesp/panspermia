"""Experimentos declarativos y barridos (fase 1d, docs/fase1d/diseno.md).

Una especificación (JSON) describe una condición:

    {"name": "E1-aleatorio-T560", "description": "...", "node": "fase1d-w0", "seeds": [0, 1, 2, 3, 4],
     "epochs": 300, "n_max": 4096, "n_init": 512, "plastic": true,
     "env": {"tox_mode": "aleatorio", "tox_period": 560, "clock_period": 560},
     "config": {"TOXIC_FACTOR": 0.5}}

Una cola es una lista de especificaciones. El barrido ejecuta cada (condición, semilla) **de una en
una**, cada una en su propio proceso (así las sustituciones de `config` no se mezclan), y salta las
que ya tienen `result.json`. Los datos van a `<raíz>/<name>/s<semilla>/`.

Uso:
    python -m panspermia.experiment sweep experiments/fase1d/e0.json --out runs/fase1d
    python -m panspermia.experiment run experiments/fase1d/e0.json --name E0-fijo --seed 0 --out runs/fase1d
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

# Constantes que se leen al trazar (dentro de funciones), así que se pueden sustituir por proceso.
# Las que fijan formas o se copian al importar (rejillas, N_RAYS, dimensiones) NO están permitidas.
CONFIG_OVERRIDABLE = {
    "TOXIC_FACTOR", "TOXIC_RAMP_STEPS", "C_NEURON", "MIN_REPRO_AGE", "RESOURCE_R", "EMIT_COST",
    "FROZEN_PLASTICITY_TEST_EVERY", "CHECKPOINT_EVERY", "VIDEO_EVERY", "CAPABILITY_TEST_EVERY",
    "NEURON_MUTATION", "MUTATION_RATES", "CPPN_MUTATION", "REPRODUCTION", "BIRTH_PLACEMENT", "K_CUT", "REPRO_COST",
    "FOOD_JUMP_PERIOD", "ALGA_SWAP_PERIOD", "FOOD_JUMP_DIST", "EAT_MOVE_FACTOR", "EAT_MOVE_RAMP_STEPS",
}
SPEC_KEYS = {"name", "description", "node", "seeds", "epochs", "n_max", "n_init", "plastic", "env",
             "config", "block"}


def load_queue(path: Path) -> list[dict]:
    specs = json.loads(path.read_text(encoding="utf-8"))
    specs = specs if isinstance(specs, list) else [specs]
    names = [s["name"] for s in specs]
    if len(names) != len(set(names)):
        raise ValueError("nombres de condición repetidos en la cola")
    for s in specs:
        unknown = set(s) - SPEC_KEYS
        if unknown:
            raise ValueError(f"{s['name']}: claves desconocidas {sorted(unknown)}")
        bad = set(s.get("config", {})) - CONFIG_OVERRIDABLE
        if bad:
            raise ValueError(f"{s['name']}: constantes no sustituibles {sorted(bad)}")
    return specs


def run_one(spec: dict, seed: int, root: Path) -> dict:
    """Ejecuta una (condición, semilla) en ESTE proceso. Debe llamarse antes de compilar nada."""
    from . import config as C
    for k, v in spec.get("config", {}).items():
        setattr(C, k, tuple(v) if isinstance(v, list) else v)
    from . import run as runner
    out = root / spec["name"] / f"s{seed}"
    t0 = time.time()
    try:
        r = runner.run(seed, spec.get("epochs", 300), out, spec.get("node", "fase1d-w0").encode(),
                       spec.get("n_max", C.N_MAX), spec.get("n_init", C.N_INIT), verbose=True,
                       env_overrides=spec.get("env"), plastic=spec.get("plastic", True),
                       experiment=spec)
    except runner.CapabilityPause as exc:
        r = {"paused": True, "error": str(exc)}
    r.update({"name": spec["name"], "seed": seed, "hours": (time.time() - t0) / 3600})
    (out / "result.json").write_text(json.dumps(r, indent=2), encoding="utf-8")
    return r


def sweep(queue: Path, root: Path, only: set[str] | None = None) -> None:
    specs = load_queue(queue)
    jobs = [(s, seed) for s in specs if not only or s["name"] in only for seed in s["seeds"]]
    print(f"{len(jobs)} ejecuciones en la cola {queue}", flush=True)
    for i, (spec, seed) in enumerate(jobs, 1):
        done = root / spec["name"] / f"s{seed}" / "result.json"
        if done.exists():
            print(f"[{i}/{len(jobs)}] {spec['name']} s{seed}: hecha, se salta", flush=True)
            continue
        print(f"[{i}/{len(jobs)}] {spec['name']} s{seed}: empieza", flush=True)
        code = subprocess.call([sys.executable, "-m", "panspermia.experiment", "run", str(queue),
                                "--name", spec["name"], "--seed", str(seed), "--out", str(root)])
        print(f"[{i}/{len(jobs)}] {spec['name']} s{seed}: código {code}", flush=True)
        if done.exists():
            print("    " + done.read_text(encoding="utf-8").replace("\n", " "), flush=True)


def main() -> None:
    p = argparse.ArgumentParser(description="Experimentos y barridos de Panspermia.")
    p.add_argument("cmd", choices=["run", "sweep", "check"])
    p.add_argument("queue", type=Path)
    p.add_argument("--out", type=Path, default=Path("runs/fase1d"))
    p.add_argument("--name")
    p.add_argument("--seed", type=int)
    p.add_argument("--only", nargs="*", help="solo estas condiciones (sweep)")
    a = p.parse_args()
    if a.cmd == "check":
        specs = load_queue(a.queue)
        n = sum(len(s["seeds"]) for s in specs)
        ep = sum(len(s["seeds"]) * s.get("epochs", 300) for s in specs)
        print(f"{len(specs)} condiciones · {n} ejecuciones · {ep} épocas")
    elif a.cmd == "run":
        spec = next(s for s in load_queue(a.queue) if s["name"] == a.name)
        print(json.dumps(run_one(spec, a.seed, a.out)))
    else:
        sweep(a.queue, a.out, set(a.only) if a.only else None)


if __name__ == "__main__":
    main()
