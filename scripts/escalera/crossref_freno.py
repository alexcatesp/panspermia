import json, urllib.request, urllib.parse
Q = ["Evolutionary rescue can prevent extinction following environmental change Bell Gonzalez",
     "Evolutionary rescue from extinction is contingent on a lower rate of environmental change Lindsey",
     "When does evolution by natural selection prevent extinction Gomulkiewicz Holt",
     "Incremental evolution of complex general behavior Gomez Miikkulainen",
     "Some characteristics of simple types of predation and parasitism Holling",
     "Evolutionary rescue: an emerging focus at the intersection between ecology and evolution Gonzalez",
     "Optimal foraging, the marginal value theorem Charnov",
     "Evolving learning abilities of hopfield networks environmental change gradual",
     "Shaping robot behavior using principles from instrumental conditioning Saksida",
     "The evolution of learning in a changing environment rate of environmental change",
     ]
for q in Q:
    u = "https://api.crossref.org/works?" + urllib.parse.urlencode({"query.bibliographic": q, "rows": 2, "mailto": "noreply@example.org"})
    for it in json.load(urllib.request.urlopen(u, timeout=30))["message"]["items"]:
        a = ", ".join(x.get("family", "") for x in it.get("author", [])[:3])
        y = (it.get("issued", {}).get("date-parts") or [[None]])[0][0]
        print(f"{it['DOI']} | {y} | {a} | {it.get('title', [''])[0][:90]} | {(it.get('container-title') or [''])[0][:40]}")
    print()
