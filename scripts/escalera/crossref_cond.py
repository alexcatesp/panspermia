import json, sys, urllib.parse, urllib.request
Q = [
 ("Pontes2020", "Pontes Mobley Ofria Adami Dyer 2020 The evolutionary origin of associative learning American Naturalist"),
 ("Risi2010", "Risi Hughes Stanley 2010 Evolving plastic neural networks with novelty search Adaptive Behavior"),
 ("Eliassen2007", "Eliassen Jorgensen Mangel Giske 2007 Exploration or exploitation: life expectancy changes the value of learning in foraging strategies"),
 ("Dridi2016", "Dridi Lehmann 2016 Environmental complexity favors the evolution of learning Behavioral Ecology"),
 ("Izquierdo2007", "Izquierdo Harvey 2007 Hebbian learning using fixed weight evolved dynamical neural networks"),
 ("Tonelli2013", "Tonelli Mouret 2013 On the relationships between generative encodings, regularity, and learning abilities when evolving plastic artificial neural networks"),
 ("Floreano2000", "Floreano Urzelai 2000 Evolutionary robots with on-line self-organization and behavioral fitness Neural Networks"),
 ("Mayley1996", "Mayley 1996 Landscapes, learning costs, and genetic assimilation Evolutionary Computation"),
 ("Nolfi1996", "Nolfi Parisi 1996 Learning to adapt to changing environments in evolving neural networks Adaptive Behavior"),
 ("Dunlap2019", "Dunlap Austin Figueiredo 2019 Components of change and the evolution of learning in theory and experiment Animal Behaviour"),
 ("Snell2013", "Snell-Rood 2013 An overview of the evolutionary causes and consequences of behavioural plasticity Animal Behaviour"),
]
for key, q in Q:
    url = "https://api.crossref.org/works?rows=2&query.bibliographic=" + urllib.parse.quote(q)
    import subprocess
    import time
    for t in range(5):
        out = subprocess.run(["curl", "-s", "--ssl-no-revoke", "-A", "panspermia-bib/1.0", url], capture_output=True, text=True, encoding="utf-8").stdout
        try:
            items = json.loads(out)["message"]["items"]; break
        except Exception:
            time.sleep(3)
    else:
        print(key, "SIN RESPUESTA", out[:200]); continue
    for it in items[:1]:
        au = "; ".join(f"{a.get('family','')} {a.get('given','')[:1]}" for a in it.get("author", [])[:6])
        yr = (it.get("published-print") or it.get("published-online") or it.get("issued"))["date-parts"][0][0]
        print(f"{key}: {au} ({yr}). {' '.join(it['title'][0].split())}. {it.get('container-title',[''])[0]} {it.get('volume','')}:{it.get('page','')}. doi:{it['DOI']} score={it.get('score',0):.0f}")

