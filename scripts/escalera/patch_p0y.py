import json
from pathlib import Path

ROOT = Path("D:/Development/panspermia-p0y")


def sub(p, old, new):
    f = ROOT / p
    s = f.read_text(encoding="utf-8")
    assert s.count(old) == 1, (p, old[:70], s.count(old))
    f.write_text(s.replace(old, new), encoding="utf-8", newline="\n")


c = "src/panspermia/config.py"
sub(c, 'SUBSTRATE_VERSION = "2.3.0"', 'SUBSTRATE_VERSION = "2.4.0"')
sub(c, "                             # 2.3: tasas de mutación fijas y CPPN neutral elegibles, ADR-016)",
    "                             # 2.3: tasas de mutación fijas y CPPN neutral elegibles, ADR-016;\n"
    "                             # 2.4: reproducción sexual y lugar de nacimiento elegibles, ADR-017)")
sub(c, 'CPPN_NEUTRAL_RATES = {"add_edge": 0.035, "del_edge": 0.035, "split": 0.02, "del_node": 0.02}\n',
    '''CPPN_NEUTRAL_RATES = {"add_edge": 0.035, "del_edge": 0.035, "split": 0.02, "del_node": 0.02}
# Reproducción (ADR-017): "asexual" (spec v1) o "sexual": el hijo mezcla por índice (marcas
# históricas, como NEAT) los genes del padre y de una pareja adulta elegida al azar entre sus vecinos
# (rejilla 3 × 3); sin pareja cerca, se clona. La pareja solo aporta genes, no energía.
REPRODUCTION = "asexual"
# Dónde nace el hijo (ADR-017): "cerca" (spec v1: a 2 radios del padre) o "azar" (cualquier punto).
BIRTH_PLACEMENT = "cerca"
# Estructura espacial (solo observa, ADR-017): vecinos a menos de KIN_RADIUS cuentan para el
# parentesco local (fracción de vecinos del mismo clado).
KIN_RADIUS = 30.0
''')

g = "src/panspermia/genome.py"
sub(g, "def random_minimal(key: jax.Array) -> Genome:", '''def crossover(a: Genome, b: Genome, key: jax.Array) -> Genome:
    """Cruce uniforme por índice (ADR-017): cada nodo de la CPPN con sus aristas de entrada, cada hueco
    de neurona y cada gen de cuerpo y de vida vienen de `a` o de `b` al 50 %. Los índices actúan como
    marcas históricas (spec §Reproducción sexual, como las innovaciones de NEAT)."""
    k = jax.random.split(key, 4)
    n = jax.random.bernoulli(k[0], 0.5, (C.CPPN_NODES,))
    h = jax.random.bernoulli(k[1], 0.5, (C.N_HIDDEN_MAX,))
    bo = jax.random.bernoulli(k[2], 0.5, (C.BODY_GENES,))
    li = jax.random.bernoulli(k[3], 0.5, (C.LIFE_GENES,))

    def pick(m, x, y):
        return jnp.where(m, y, x)

    child = Genome(
        node_mask=pick(n, a.node_mask, b.node_mask), act_id=pick(n, a.act_id, b.act_id),
        bias=pick(n, a.bias, b.bias), W=pick(n[None, :], a.W, b.W), W_mask=pick(n[None, :], a.W_mask, b.W_mask),
        hid_mask=pick(h, a.hid_mask, b.hid_mask), hid_pos=pick(h[:, None], a.hid_pos, b.hid_pos),
        hid_type=pick(h, a.hid_type, b.hid_type), body=pick(bo, a.body, b.body), life=pick(li, a.life, b.life),
        generation=jnp.maximum(a.generation, b.generation),
    )
    return canonical(child)


def random_minimal(key: jax.Array) -> Genome:''')

i = "src/panspermia/island.py"
sub(i, '''        parent_g = jax.tree.map(lambda x: x[parents], state.genome)
        child_g = jax.vmap(G.mutate)(parent_g, jax.random.split(k[1], b))''',
    '''        parent_g = jax.tree.map(lambda x: x[parents], state.genome)
        if C.REPRODUCTION == "sexual":  # ADR-017: pareja adulta al azar entre los vecinos
            cand = world.neighbors(state.pos, state.alive)[parents]
            safe = jnp.maximum(cand, 0)
            ok = (cand >= 0) & state.alive[safe] & (state.age[safe] >= C.MIN_REPRO_AGE)
            k_mate = jax.random.split(jax.random.fold_in(key, 0x5E7), 2)
            pick = jnp.argmax(jnp.where(ok, jax.random.uniform(k_mate[0], cand.shape), -1.0), axis=1)
            mates = jnp.where(jnp.any(ok, axis=1), safe[jnp.arange(b), pick], parents)  # sin pareja: clon
            mate_g = jax.tree.map(lambda x: x[mates], state.genome)
            parent_g = jax.vmap(G.crossover)(parent_g, mate_g, jax.random.split(k_mate[1], b))
        elif C.REPRODUCTION != "asexual":
            raise ValueError(f"REPRODUCTION desconocida: {C.REPRODUCTION}")
        child_g = jax.vmap(G.mutate)(parent_g, jax.random.split(k[1], b))''')
sub(i, '''        state = _place(state, jnp.where(valid, slots, n), child_g, child_p,
                       (state.pos[parents] + offset) % C.WORLD_L,''',
    '''        if C.BIRTH_PLACEMENT == "cerca":
            child_pos = (state.pos[parents] + offset) % C.WORLD_L
        elif C.BIRTH_PLACEMENT == "azar":  # ADR-017: sin vecindarios de parientes
            child_pos = jax.random.uniform(jax.random.fold_in(key, 0xD15), (b, 2), maxval=C.WORLD_L)
        else:
            raise ValueError(f"BIRTH_PLACEMENT desconocido: {C.BIRTH_PLACEMENT}")
        state = _place(state, jnp.where(valid, slots, n), child_g, child_p, child_pos,''')
sub(i, '    """Nacimientos asexuales en slots libres.', '    """Nacimientos (asexuales o sexuales, ADR-017) en slots libres.')

m = "src/panspermia/metrics.py"
sub(m, "from . import config as C\n", "from . import config as C\nfrom . import world\n")
sub(m, '''        "mass_mean": _masked_mean(state.pheno.mass, alive),''', '''        "mass_mean": _masked_mean(state.pheno.mass, alive),
        "kin_local": kin_local(state),''')
sub(m, "def epoch_stats(state, per_step) -> dict[str, jax.Array]:", '''def kin_local(state) -> jax.Array:
    """Parentesco local (ADR-017, solo observa): fracción media de vecinos a menos de KIN_RADIUS que
    son del mismo clado. Se compara con `kin_global` (índice de Simpson de los clados)."""
    alive = state.alive
    cand = world.neighbors(state.pos, alive)
    safe = jnp.maximum(cand, 0)
    d = world.wrap_delta(state.pos[safe] - state.pos[:, None, :])
    near = (cand >= 0) & (jnp.sum(d * d, axis=-1) <= C.KIN_RADIUS ** 2)
    same = near & (state.lineage.clade[safe] == state.lineage.clade[:, None])
    n_near = jnp.sum(near, axis=1)
    has = alive & (n_near > 0)
    frac = jnp.sum(same, axis=1) / jnp.maximum(n_near, 1)
    return jnp.sum(jnp.where(has, frac, 0.0)) / jnp.maximum(jnp.sum(has), 1)


def simpson(clade: np.ndarray, alive: np.ndarray) -> float:
    """Probabilidad de que dos vivos al azar sean del mismo clado (referencia de `kin_local`)."""
    c = clade[alive]
    if len(c) < 2:
        return 0.0
    _, counts = np.unique(c, return_counts=True)
    p = counts / counts.sum()
    return float(np.sum(p * p))


def epoch_stats(state, per_step) -> dict[str, jax.Array]:''')
sub("src/panspermia/run.py", '        row.update(activity.update(view["clade"], view["alive"]))',
    '        row.update(activity.update(view["clade"], view["alive"]))\n'
    '        row["kin_global"] = metrics.simpson(view["clade"], view["alive"])')
sub("src/panspermia/experiment.py", '    "NEURON_MUTATION", "MUTATION_RATES", "CPPN_MUTATION",',
    '    "NEURON_MUTATION", "MUTATION_RATES", "CPPN_MUTATION", "REPRODUCTION", "BIRTH_PLACEMENT",')

esc = json.loads((ROOT / "experiments/fase1d/escalera.json").read_text(encoding="utf-8"))
p0 = next(s for s in esc if s["name"] == "P0-feliz")
queue = []
for name, desc, cfg in (
    ("P0-feliz-sexual", "Reproducción sexual (ADR-017): pareja adulta al azar entre los vecinos; cruce uniforme por índice.", {"REPRODUCTION": "sexual"}),
    ("P0-feliz-nacer-azar", "El hijo nace en un punto al azar del mundo, no junto al padre (ADR-017).", {"BIRTH_PLACEMENT": "azar"}),
    ("P0-feliz-control-kin", "Control idéntico a P0-feliz con la medida de parentesco local (ADR-017); debe coincidir bit a bit en la dinámica.", {}),
):
    s = json.loads(json.dumps(p0))
    s.update({"name": name, "block": "P0Y", "description": f"{p0['description']} {desc}"})
    if cfg:
        s["config"] = {**s.get("config", {}), **cfg}
    if name.endswith("control-kin"):
        s["seeds"] = [0]  # basta una semilla para comprobar que la dinámica es idéntica bit a bit
    queue.append(s)
(ROOT / "experiments/fase1d/p0y.json").write_text(json.dumps(queue, indent=1, ensure_ascii=False) + "\n",
                                                  encoding="utf-8", newline="\n")
print("ok", [q["name"] for q in queue])
