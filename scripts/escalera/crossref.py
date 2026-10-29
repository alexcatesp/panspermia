import json, sys, urllib.parse, urllib.request
Q = [
 ("Berg1972", "Berg Brown 1972 Chemotaxis in Escherichia coli analysed by three-dimensional tracking"),
 ("Hills2004", "Hills Brockie Maricq 2004 Dopamine and glutamate control area-restricted search behavior in Caenorhabditis elegans"),
 ("Hills2006", "Hills 2006 Animal foraging and the evolution of goal-directed cognition"),
 ("Humphries2010", "Humphries 2010 Environmental context explains Levy and Brownian movement patterns of marine predators"),
 ("SmithFretwell1974", "Smith Fretwell 1974 The optimal balance between size and number of offspring"),
 ("Stephens1991", "Stephens 1991 Change, regularity, and value in the evolution of animal learning"),
 ("DunlapStephens2009", "Dunlap Stephens 2009 Components of change in the evolution of learning and unlearned preference"),
 ("Mitchell2009", "Mitchell 2009 Adaptive prediction of environmental changes by microorganisms"),
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
