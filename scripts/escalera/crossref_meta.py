import json, urllib.request
for d in ["10.1111/j.1461-0248.2009.01350.x", "10.1038/nature11879", "10.2307/2410305", "10.1177/105971239700500305",
          "10.1098/rstb.2012.0404", "10.1016/s0921-8890(97)00041-9"]:
    m = json.load(urllib.request.urlopen(f"https://api.crossref.org/works/{d}?mailto=noreply@example.org", timeout=30))["message"]
    au = " and ".join(f"{a.get('family','')}, {a.get('given','')}" for a in m.get("author", []))
    print(json.dumps({"doi": m["DOI"], "author": au, "title": m["title"][0], "journal": (m.get("container-title") or [""])[0],
                      "volume": m.get("volume"), "issue": m.get("issue"), "pages": m.get("page"),
                      "year": m["issued"]["date-parts"][0][0]}, ensure_ascii=False))
