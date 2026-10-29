import json
from pathlib import Path
ROOT = Path("D:/Development/panspermia-p0z")
def sub(p, old, new):
    f = ROOT / p; s = f.read_text(encoding="utf-8")
    assert s.count(old) == 1, (p, old[:70], s.count(old))
    f.write_text(s.replace(old, new), encoding="utf-8", newline="\n")

c = "src/panspermia/config.py"
sub(c, 'SUBSTRATE_VERSION = "2.4.0"', 'SUBSTRATE_VERSION = "2.5.0"')
sub(c, "                             # 2.4: reproducción sexual y lugar de nacimiento elegibles, ADR-017)",
    "                             # 2.4: reproducción sexual y lugar de nacimiento elegibles, ADR-017;\n"
    "                             # 2.5: el cruce hereda la CPPN entera de un progenitor, ADR-018)")
sub(c, '''# Reproducción (ADR-017): "asexual" (spec v1) o "sexual": el hijo mezcla por índice (marcas
# históricas, como NEAT) los genes del padre y de una pareja adulta elegida al azar entre sus vecinos
# (rejilla 3 × 3); sin pareja cerca, se clona. La pareja solo aporta genes, no energía.''',
'''# Reproducción (ADR-017, corregida en ADR-018): "asexual" (spec v1) o "sexual": el hijo mezcla los
# genes del padre y de una pareja adulta elegida al azar entre sus vecinos (rejilla 3 × 3); sin pareja
# cerca, se clona. La pareja solo aporta genes, no energía. La CPPN se hereda entera de uno de los dos
# (bloque ligado); los huecos de neurona y los genes de cuerpo y de vida se mezclan uno a uno.''')

g = "src/panspermia/genome.py"
sub(g, '''    """Cruce uniforme por índice (ADR-017): cada nodo de la CPPN con sus aristas de entrada, cada hueco
    de neurona y cada gen de cuerpo y de vida vienen de `a` o de `b` al 50 %. Los índices actúan como
    marcas históricas (spec §Reproducción sexual, como las innovaciones de NEAT)."""
    k = jax.random.split(key, 4)
    n = jax.random.bernoulli(k[0], 0.5, (C.CPPN_NODES,))''',
'''    """Cruce (ADR-017, corregido en ADR-018): la CPPN entera viene de `a` o de `b` al 50 % (un bloque
    ligado, como un cromosoma); cada hueco de neurona y cada gen de cuerpo y de vida, de uno u otro.

    La versión 2.4 cruzaba la CPPN nodo a nodo por índice, como si los índices fueran marcas históricas.
    No lo son: el mismo índice nace de divisiones distintas en cada linaje, y un nodo heredaba sus
    aristas de entrada de un progenitor y las de salida del otro (83–88 % de nodos sin salida en P0;
    "convenciones en competencia", Stanley y Miikkulainen 2002). Los huecos de neurona no tienen ese
    problema: no guardan aristas, sus pesos salen de la CPPN según su posición."""
    k = jax.random.split(key, 4)
    n = jax.random.bernoulli(k[0], 0.5)''')
sub(g, "W=pick(n[None, :], a.W, b.W), W_mask=pick(n[None, :], a.W_mask, b.W_mask),",
    "W=pick(n, a.W, b.W), W_mask=pick(n, a.W_mask, b.W_mask),")

t = "tests/test_p0y.py"
sub(t, "def test_sexual_children_mix_two_parents():", '''def _evolved(seed, rounds=300):
    """Genoma con una CPPN propia: muchas mutaciones con la tasa estructural alta."""
    g = G.random_minimal(jax.random.PRNGKey(seed))
    g = g.replace(life=g.life.at[3].set(5.0))
    mut = jax.jit(G.mutate)
    for i in range(rounds):
        g = mut(g, jax.random.PRNGKey(1000 * seed + i))
    return g


def _dead_nodes(g):
    hidden = np.zeros(config.CPPN_NODES, bool)
    hidden[config.CPPN_IN:config.CPPN_NODES - config.CPPN_OUT] = True
    nm, wm = np.asarray(g.node_mask), np.asarray(g.W_mask)
    return int(np.sum(nm & hidden & ~wm.any(axis=1))), int(np.sum(nm & hidden & ~wm.any(axis=0)))


def test_crossover_keeps_the_cppn_whole():
    """ADR-018: la CPPN del hijo es entera la de un progenitor, y no deja nodos sin salida nuevos."""
    a, b = _evolved(1), _evolved(2)
    assert int(np.sum(np.asarray(a.node_mask) != np.asarray(b.node_mask))) > 0  # CPPN distintas
    fields = ("node_mask", "act_id", "bias", "W", "W_mask")
    seen = set()
    for i in range(16):
        c = G.crossover(a, b, jax.random.PRNGKey(100 + i))
        from_a = all(np.array_equal(np.asarray(getattr(c, f)), np.asarray(getattr(G.canonical(a), f))) for f in fields)
        from_b = all(np.array_equal(np.asarray(getattr(c, f)), np.asarray(getattr(G.canonical(b), f))) for f in fields)
        assert from_a or from_b
        seen.add("a" if from_a else "b")
        assert _dead_nodes(c) in (_dead_nodes(a), _dead_nodes(b))
    assert seen == {"a", "b"}


def test_sexual_children_mix_two_parents():''')

esc = json.loads((ROOT / "experiments/fase1d/p0y.json").read_text(encoding="utf-8"))
s = next(x for x in esc if x["name"] == "P0-feliz-sexual")
s = json.loads(json.dumps(s))
s["name"] = "P0-feliz-sexual-bloques"
s["block"] = "P0Z"
s["description"] = s["description"].replace("cruce uniforme por índice.", "cruce con la CPPN entera de un progenitor (corrige ADR-017, ADR-018).")
(ROOT / "experiments/fase1d/p0z.json").write_text(json.dumps([s], indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
print("ok", s["name"], s["config"], s["description"][-90:])
