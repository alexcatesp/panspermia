"""Métricas de observación: nunca realimentan la selección (spec §Métricas).

Dos niveles:
- `epoch_stats`: escalares calculados dentro de `epoch` (bajo jit): demografía, complejidad,
  diversidad, ataque y comunicación.
- Análisis en el host (numpy) entre épocas: descriptor conductual de 8 dimensiones, archivo de
  novedad k-NN, grupos conductuales (k-means + silueta) y actividad evolutiva de Bedau-Packard.
"""
from __future__ import annotations

import math

import jax
import jax.numpy as jnp
import numpy as np

from . import config as C

# ---------------------------------------------------------------------------------------------
# Bajo jit
# ---------------------------------------------------------------------------------------------


def _masked_mean(x: jax.Array, mask: jax.Array) -> jax.Array:
    x = x.astype(jnp.float32)
    return jnp.sum(jnp.where(mask, x, 0.0)) / jnp.maximum(jnp.sum(mask), 1)


def _masked_max(x: jax.Array, mask: jax.Array) -> jax.Array:
    return jnp.max(jnp.where(mask, x.astype(jnp.float32), 0.0))


def mutual_information(hist: jax.Array) -> tuple[jax.Array, jax.Array]:
    """(I(señal; contexto) en bits, nº efectivo de símbolos = 2^H(señal)) de un histograma conjunto."""
    p = hist / jnp.maximum(jnp.sum(hist), 1e-9)
    ps = jnp.sum(p, axis=1, keepdims=True)
    pc = jnp.sum(p, axis=0, keepdims=True)
    mi = jnp.sum(jnp.where(p > 0, p * jnp.log2(p / jnp.maximum(ps * pc, 1e-12)), 0.0))
    h = -jnp.sum(jnp.where(ps > 0, ps * jnp.log2(jnp.maximum(ps, 1e-12)), 0.0))
    return jnp.maximum(mi, 0.0), 2.0 ** h


def _clade_diversity(clade: jax.Array, alive: jax.Array) -> tuple[jax.Array, jax.Array]:
    """(nº de clados vivos, índice de Shannon por clado)."""
    n = clade.shape[0]
    sentinel = jnp.uint32(2**32 - 1)
    ids, counts = jnp.unique(jnp.where(alive, clade, sentinel), size=n, fill_value=sentinel,
                             return_counts=True)
    counts = jnp.where(ids == sentinel, 0, counts).astype(jnp.float32)
    total = jnp.maximum(jnp.sum(counts), 1.0)
    p = counts / total
    shannon = -jnp.sum(jnp.where(p > 0, p * jnp.log(jnp.maximum(p, 1e-12)), 0.0))
    return jnp.sum(counts > 0).astype(jnp.int32), shannon


def _genome_vectors(g, idx):
    f32 = lambda x: x[idx].astype(jnp.float32).reshape(idx.shape[0], -1)
    cont = jnp.concatenate([f32(g.W), f32(g.bias), f32(g.body), f32(g.life)[:, :2],
                            f32(g.hid_pos) * f32(g.hid_mask).repeat(2, axis=1)], axis=1)
    struct_ = jnp.concatenate([f32(g.node_mask), f32(g.W_mask), f32(g.hid_mask), f32(g.hid_type)], 1)
    return cont, struct_


def _genome_distance(state) -> tuple[jax.Array, jax.Array]:
    """Distancia genómica media entre pares aleatorios de vivos: (euclídea de genes continuos,
    Hamming de máscaras estructurales)."""
    n = state.alive.shape[0]
    key = jax.random.fold_in(jax.random.fold_in(state.key, 0xD15), state.step)
    alive_f = state.alive.astype(jnp.float32)
    p = alive_f / jnp.maximum(jnp.sum(alive_f), 1.0)
    p = jnp.where(jnp.sum(alive_f) > 0, p, jnp.full((n,), 1.0 / n))
    ka, kb = jax.random.split(key)
    a = jax.random.choice(ka, n, (C.GENOME_DISTANCE_PAIRS,), p=p)
    b = jax.random.choice(kb, n, (C.GENOME_DISTANCE_PAIRS,), p=p)
    ca, sa = _genome_vectors(state.genome, a)
    cb, sb = _genome_vectors(state.genome, b)
    return (jnp.mean(jnp.linalg.norm(ca - cb, axis=1)), jnp.mean(jnp.sum(jnp.abs(sa - sb), axis=1)))


def epoch_stats(state, per_step) -> dict[str, jax.Array]:
    alive = state.alive
    g = state.genome
    hidden = jnp.sum(g.hid_mask, axis=-1)
    synapses = jnp.sum(state.pheno.mask, axis=(-1, -2))
    cppn_nodes = jnp.sum(g.node_mask, axis=-1) - (C.CPPN_IN + C.CPPN_OUT)  # ocultos de la CPPN
    cppn_edges = jnp.sum(g.W_mask, axis=(-1, -2))
    clades, shannon = _clade_diversity(state.lineage.clade, alive)
    gd_cont, gd_struct = _genome_distance(state)
    mi, symbols = mutual_information(state.comm_hist)
    out = {
        "step": state.step,
        "population": jnp.sum(alive).astype(jnp.int32),
        "population_min": jnp.min(per_step.population),
        "births": jnp.sum(per_step.births),
        "deaths_starvation": jnp.sum(per_step.deaths_starvation),
        "deaths_age": jnp.sum(per_step.deaths_age),
        "deaths_attack": jnp.sum(per_step.deaths_attack),
        "attacks": jnp.sum(per_step.attacks),
        "energy_drained": jnp.sum(per_step.drained),
        "intake": jnp.sum(per_step.intake),
        "mean_age": _masked_mean(state.age, alive),
        "mean_energy": _masked_mean(state.energy, alive),
        "resources_total": jnp.sum(state.resources),
        "generation_mean": _masked_mean(g.generation, alive),
        "generation_max": _masked_max(g.generation, alive),
        "clades_alive": clades,
        "clade_shannon": shannon,
        "genome_distance": gd_cont,
        "genome_distance_struct": gd_struct,
        "comm_mi_bits": mi,
        "comm_effective_symbols": symbols,
        "attack_gene_mean": _masked_mean(state.pheno.attack, alive),
    }
    for name, x in (("hidden", hidden), ("synapses", synapses),
                    ("cppn_nodes", cppn_nodes), ("cppn_edges", cppn_edges)):
        out[f"{name}_mean"] = _masked_mean(x, alive)
        out[f"{name}_max"] = _masked_max(x, alive)
    return out


# ---------------------------------------------------------------------------------------------
# En el host (numpy), entre épocas
# ---------------------------------------------------------------------------------------------

DESCRIPTOR_NAMES = ("speed", "turn", "intake", "attacks", "signal_entropy", "dispersion",
                    "aggregation", "repro_age")


def host_view(state) -> dict[str, np.ndarray]:
    """Copia al host solo lo necesario para el análisis entre épocas."""
    b = state.behavior
    return jax.device_get({
        "alive": state.alive, "age": state.age, "clade": state.lineage.clade,
        "uid": state.lineage.uid, "speed": b.speed, "turn": b.turn, "intake": b.intake,
        "attack": b.attack, "neighbors": b.neighbors, "sig_hist": b.sig_hist, "disp": b.disp,
        "first_repro_age": b.first_repro_age,
    })


def descriptors(v: dict[str, np.ndarray]) -> np.ndarray:
    """Descriptor conductual [n, 8] en [0, 1] de los vivos con edad >= DESCRIPTOR_MIN_AGE."""
    m = v["alive"] & (v["age"] >= C.DESCRIPTOR_MIN_AGE)
    age = np.maximum(v["age"][m], 1).astype(np.float64)
    hist = v["sig_hist"][m].astype(np.float64)
    p = hist / np.maximum(hist.sum(1, keepdims=True), 1e-9)
    entropy = -np.sum(np.where(p > 0, p * np.log(np.maximum(p, 1e-12)), 0.0), 1) / math.log(C.SIGNAL_BINS)
    # Edad a la primera reproducción; si aún no se ha reproducido, dato censurado: se usa su edad
    # actual como cota inferior (un valor fijo de relleno creaba un grupo artificial, ADR-007).
    repro = v["first_repro_age"][m].astype(np.float64)
    repro = np.where(repro < 0, age, repro) / C.SENESCENCE_START
    d = np.stack([
        v["speed"][m] / age / C.V_OBS_SCALE,
        v["turn"][m] / age,
        v["intake"][m] / age / (C.EAT_RATE * C.DT),
        v["attack"][m] / age,
        entropy,
        np.linalg.norm(v["disp"][m], axis=1) / C.WORLD_L,
        v["neighbors"][m] / age / 10.0,
        repro,
    ], axis=1)
    return np.clip(d, 0.0, 1.0)


def _pairwise(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return np.sqrt(np.maximum(((a[:, None, :] - b[None, :, :]) ** 2).sum(-1), 0.0))


class NoveltyArchive:
    """Archivo histórico de descriptores. Novedad = distancia media a los k vecinos más cercanos
    en archivo ∪ muestra actual (Lehman y Stanley). Entra quien supera NOVELTY_THRESHOLD."""

    def __init__(self, archive: np.ndarray | None = None):
        self.archive = archive if archive is not None else np.zeros((0, len(DESCRIPTOR_NAMES)))

    def update(self, sample: np.ndarray) -> dict[str, float]:
        if len(sample) == 0:
            return {"novelty_mean": 0.0, "novelty_added": 0, "archive_size": len(self.archive)}
        ref = np.concatenate([self.archive, sample]) if len(self.archive) else sample
        d = _pairwise(sample, ref)
        k = min(C.NOVELTY_K, ref.shape[0] - 1)
        # cada muestra está en ref a distancia 0: se descarta con k + 1
        nov = np.sort(d, axis=1)[:, 1:k + 1].mean(1) if k > 0 else np.zeros(len(sample))
        order = np.argsort(-nov, kind="stable")
        add = order[nov[order] >= C.NOVELTY_THRESHOLD][:C.NOVELTY_MAX_ADD]
        if len(add):
            self.archive = np.concatenate([self.archive, sample[add]])
        return {"novelty_mean": float(nov.mean()), "novelty_added": len(add),
                "archive_size": len(self.archive)}


def kmeans(x: np.ndarray, k: int, rng: np.random.Generator, iters: int = 50) -> np.ndarray:
    """k-means con inicialización k-means++; devuelve etiquetas."""
    centers = [x[rng.integers(len(x))]]
    for _ in range(1, k):
        d2 = np.min(_pairwise(x, np.array(centers)) ** 2, axis=1)
        p = d2 / d2.sum() if d2.sum() > 0 else np.full(len(x), 1 / len(x))
        centers.append(x[rng.choice(len(x), p=p)])
    centers = np.array(centers)
    labels = np.zeros(len(x), int)
    for _ in range(iters):
        labels = np.argmin(_pairwise(x, centers), axis=1)
        new = np.array([x[labels == j].mean(0) if np.any(labels == j) else centers[j] for j in range(k)])
        if np.allclose(new, centers):
            break
        centers = new
    return labels


def silhouette(x: np.ndarray, labels: np.ndarray) -> float:
    """Silueta media (Rousseeuw, 1987)."""
    ks = np.unique(labels)
    if len(ks) < 2:
        return 0.0
    d = _pairwise(x, x)
    s = np.zeros(len(x))
    for i in range(len(x)):
        same = labels == labels[i]
        n_same = same.sum() - 1
        if n_same == 0:
            continue
        a = d[i, same].sum() / n_same
        b = min(d[i, labels == k].mean() for k in ks if k != labels[i])
        s[i] = (b - a) / max(a, b) if max(a, b) > 0 else 0.0
    return float(s.mean())


def behavior_groups(sample: np.ndarray, seed: int) -> dict[str, float]:
    """Mejor k (silueta máxima) en CLUSTER_K_RANGE sobre la muestra de descriptores."""
    if len(sample) < 2 * C.CLUSTER_K_RANGE[1]:
        return {"groups_k": 0, "groups_silhouette": 0.0}
    rng = np.random.default_rng(seed)
    best = (0, 0.0)
    for k in range(C.CLUSTER_K_RANGE[0], C.CLUSTER_K_RANGE[1] + 1):
        s = silhouette(sample, kmeans(sample, k, rng))
        if s > best[1]:
            best = (k, s)
    return {"groups_k": best[0], "groups_silhouette": best[1]}


class ActivityTracker:
    """Actividad evolutiva de Bedau-Packard por clado: actividad acumulada = Σ población del clado
    por época. Componentes con actividad > ACTIVITY_THRESHOLD cuentan como «actividad nueva»
    la época en que la superan. Versión simplificada sin modelo sombra (ADR-007)."""

    def __init__(self, activity: dict[int, float] | None = None):
        self.activity = activity or {}

    def update(self, clade: np.ndarray, alive: np.ndarray) -> dict[str, float]:
        ids, counts = np.unique(clade[alive], return_counts=True)
        new = 0
        for c, n in zip(ids.tolist(), counts.tolist()):
            before = self.activity.get(c, 0.0)
            after = before + n
            self.activity[c] = after
            new += before < C.ACTIVITY_THRESHOLD <= after
        alive_act = [self.activity[c] for c in ids.tolist()]
        return {"bp_new_activity": int(new),
                "bp_total_activity": float(sum(alive_act)),
                "bp_mean_activity": float(np.mean(alive_act)) if alive_act else 0.0,
                "bp_components": len(self.activity)}


def learning_survival(uid_start: np.ndarray, alive_start: np.ndarray, uid_end: np.ndarray,
                      alive_end: np.ndarray) -> float:
    """Fracción de los agentes vivos al inicio que siguen vivos al final (mismo uid en su slot)."""
    if alive_start.sum() == 0:
        return 0.0
    survived = alive_start & alive_end & (uid_start == uid_end)
    return float(survived.sum() / alive_start.sum())
