"""Deriva neutral de los genes de la mutación (σ y tasa estructural) en P0, desde checkpoints."""
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, "/mnt/d/Development/panspermia-escalera/scripts")
import jax
from reward_probe import restore

for seed in (0, 1):
    run = Path(f"/mnt/d/Development/panspermia/runs/fase1d/P0-feliz/s{seed}")
    for ep in (100, 200, 300):
        _, st = restore(run, ep)
        alive = np.asarray(st.alive)
        life = np.asarray(st.genome.life, dtype=np.float32)[alive]
        hid = np.asarray(st.genome.hid_mask)[alive].sum(1)
        sig, rate = life[:, 2], life[:, 3]
        print(f"s{seed} ép {ep}: σ mediana {np.median(sig):.4f} media {sig.mean():.4f} (p10 {np.percentile(sig,10):.4f} p90 {np.percentile(sig,90):.4f}) · "
              f"tasa estructural mediana {np.median(rate):.2f} media {rate.mean():.2f} (p10 {np.percentile(rate,10):.2f} p90 {np.percentile(rate,90):.2f}) · neuronas {hid.mean():.1f}", flush=True)
