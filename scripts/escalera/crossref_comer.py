import json, sys, urllib.parse, urllib.request
Q = [
 ("Holling1959", "Holling 1959 Some characteristics of simple types of predation and parasitism Canadian Entomologist"),
 ("Niv2002", "Niv Joel Meilijson Ruppin 2002 Evolution of reinforcement learning in uncertain environments: a simple explanation for complex foraging behaviors"),
 ("Mery2002", "Mery Kawecki 2002 Experimental evolution of learning ability in fruit flies"),
 ("Mery2003", "Mery Kawecki 2003 A fitness cost of learning ability in Drosophila melanogaster"),
 ("Todd1991", "Todd Miller 1991 Exploring adaptive agency II: simulating the evolution of associative learning"),
 ("Yaeger1994", "Yaeger 1994 Computational genetics, physiology, metabolism, neural systems, learning, vision, and behavior or PolyWorld"),
 ("Stephens1986", "Stephens Krebs 1986 Foraging theory"),
 ("Kawecki2010", "Kawecki 2010 Evolutionary ecology of learning: insights from fruit flies"),
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

