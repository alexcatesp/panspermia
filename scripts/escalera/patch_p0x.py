import json
from pathlib import Path

ROOT = Path("D:/Development/panspermia-p0x")


def sub(p, old, new):
    f = ROOT / p
    s = f.read_text(encoding="utf-8")
    assert s.count(old) == 1, (p, old[:70], s.count(old))
    f.write_text(s.replace(old, new), encoding="utf-8", newline="\n")


sub("src/panspermia/config.py", 'SUBSTRATE_VERSION = "2.2.0"', 'SUBSTRATE_VERSION = "2.3.0"')
sub("src/panspermia/config.py", "                             # 2.2: física de la mutación de neuronas elegible, ADR-015)",
    "                             # 2.2: física de la mutación de neuronas elegible, ADR-015;\n"
    "                             # 2.3: tasas de mutación fijas y CPPN neutral elegibles, ADR-016)")
sub("src/panspermia/config.py", 'P_DEL_NEURON = {"neutral": 0.01, "terrestre": 0.02}\n', '''P_DEL_NEURON = {"neutral": 0.01, "terrestre": 0.02}
# Tasas de mutación (ADR-016): "evolutivas" (spec v1: σ autoadaptativa y tasa estructural como gen,
# que sin selección deriva hacia arriba por el suelo en 0) o "fijas" (σ = SIGMA_INIT y tasa = 1,
# constantes del mundo; los genes no cambian).
MUTATION_RATES = "evolutivas"
# Física de la mutación de la CPPN (ADR-016): "nest" (spec v1: añadir arista 5 %, quitar 2 %, dividir
# 3 %, quitar nodo 1 %: crece sin selección) o "neutral" (ganar y perder con la misma tasa; el total
# de cambios estructurales por hijo, 11 %, no cambia).
CPPN_MUTATION = "nest"
CPPN_NEUTRAL_RATES = {"add_edge": 0.035, "del_edge": 0.035, "split": 0.02, "del_node": 0.02}
''')

g = "src/panspermia/genome.py"
sub(g, """    sigma = life[2] * jnp.exp(C.SIGMA_TAU * jax.random.normal(ks[0]))
    sigma = jnp.clip(sigma, *C.SIGMA_BOUNDS)
    rate = jnp.clip(life[3], *C.STRUCT_RATE_BOUNDS)
""", """    sigma = life[2] * jnp.exp(C.SIGMA_TAU * jax.random.normal(ks[0]))
    sigma = jnp.clip(sigma, *C.SIGMA_BOUNDS)
    rate = jnp.clip(life[3], *C.STRUCT_RATE_BOUNDS)
    if C.MUTATION_RATES == "fijas":  # ADR-016: constantes del mundo, no genes
        sigma, rate = jnp.float32(C.SIGMA_INIT), jnp.float32(1.0)
    elif C.MUTATION_RATES != "evolutivas":
        raise ValueError(f"MUTATION_RATES desconocida: {C.MUTATION_RATES}")
    if C.CPPN_MUTATION == "nest":
        p_add, p_del, p_split, p_del_node = C.P_ADD_EDGE, C.P_DEL_EDGE, C.P_SPLIT_EDGE, C.P_DEL_NODE
    elif C.CPPN_MUTATION == "neutral":
        r = C.CPPN_NEUTRAL_RATES
        p_add, p_del, p_split, p_del_node = r["add_edge"], r["del_edge"], r["split"], r["del_node"]
    else:
        raise ValueError(f"CPPN_MUTATION desconocida: {C.CPPN_MUTATION}")
""")
sub(g, "    life_new = life_new.at[3].add(noise(ks[5], ()))\n",
    "    if C.MUTATION_RATES == \"evolutivas\":\n        life_new = life_new.at[3].add(noise(ks[5], ()))\n")
sub(g, "    do = happens(ks[7], C.P_ADD_EDGE) & ok", "    do = happens(ks[7], p_add) & ok")
sub(g, "    do = happens(ks[10], C.P_DEL_EDGE) & ok", "    do = happens(ks[10], p_del) & ok")
sub(g, "    do = happens(ks[13], C.P_SPLIT_EDGE) & ok & ok_k", "    do = happens(ks[13], p_split) & ok & ok_k")
sub(g, "    do = happens(ks[16], C.P_DEL_NODE) & ok", "    do = happens(ks[16], p_del_node) & ok")
sub("src/panspermia/experiment.py", '    "NEURON_MUTATION",', '    "NEURON_MUTATION", "MUTATION_RATES", "CPPN_MUTATION",')

esc = json.loads((ROOT / "experiments/fase1d/escalera.json").read_text(encoding="utf-8"))
p0 = next(s for s in esc if s["name"] == "P0-feliz")
queue = []
for name, desc, cfg, extra in (
    ("P0-feliz-N1024", "Población máxima 1.024 en vez de 4.096 (ADR-016): ¿cambia la deriva neutral con el tamaño?", {}, {"n_max": 1024}),
    ("P0-feliz-tasas-fijas", "σ y tasa estructural constantes (ADR-016): ¿depende el crecimiento de la deriva de la tasa de mutación?", {"MUTATION_RATES": "fijas"}, {}),
    ("P0-feliz-cppn-neutral", "Mutación de la CPPN neutral: ganar y perder con la misma tasa (ADR-016).", {"CPPN_MUTATION": "neutral"}, {}),
):
    s = json.loads(json.dumps(p0))
    s.update({"name": name, "block": "P0X", "description": f"{p0['description']} {desc}", **extra})
    if cfg:
        s["config"] = {**s.get("config", {}), **cfg}
    queue.append(s)
(ROOT / "experiments/fase1d/p0x.json").write_text(json.dumps(queue, indent=1, ensure_ascii=False) + "\n",
                                                  encoding="utf-8", newline="\n")

# tests
t = ROOT / "tests/test_mutacion.py"
s = t.read_text(encoding="utf-8")
s += '''

def _struct(rates: str, cppn: str, rounds: int = 200, n: int = 256):
    config.MUTATION_RATES, config.CPPN_MUTATION = rates, cppn
    try:
        mutate = jax.jit(jax.vmap(lambda g, k: G.mutate(g, k)))
        g = jax.vmap(G.random_minimal)(jax.random.split(jax.random.PRNGKey(0), n))
        for r in range(rounds):
            g = mutate(g, jax.random.split(jax.random.PRNGKey(r + 1), n))
        life = np.asarray(g.life, np.float32)
        nodes = float(np.mean(np.sum(np.asarray(g.node_mask), axis=-1)))
        return life[:, 2], life[:, 3], nodes
    finally:
        config.MUTATION_RATES, config.CPPN_MUTATION = "evolutivas", "nest"


def test_fixed_rates_do_not_drift():
    sig, rate, _ = _struct("fijas", "nest")
    assert np.allclose(sig, config.SIGMA_INIT, atol=1e-3) and np.allclose(rate, 1.0)
    sig_e, rate_e, _ = _struct("evolutivas", "nest")
    assert np.std(rate_e) > 0.1 and np.std(sig_e) > 0.01


def test_neutral_cppn_grows_less_than_nest():
    _, _, nest = _struct("evolutivas", "nest")
    _, _, neutral = _struct("evolutivas", "neutral")
    assert nest > neutral + 1


def test_unknown_rates_or_cppn_mode_is_rejected():
    g = G.random_minimal(jax.random.PRNGKey(0))
    for name in ("MUTATION_RATES", "CPPN_MUTATION"):
        old = getattr(config, name)
        setattr(config, name, "inventada")
        try:
            with pytest.raises(ValueError):
                G.mutate(g, jax.random.PRNGKey(1))
        finally:
            setattr(config, name, old)
'''
t.write_text(s, encoding="utf-8", newline="\n")
print("ok", [q["name"] for q in queue])
