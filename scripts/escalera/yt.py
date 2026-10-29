import re, json, sys
h = open(sys.argv[1], encoding="utf-8").read()
i = h.find('"shortDescription":')
s = h[i+len('"shortDescription":'):]
dec = json.JSONDecoder()
print(dec.raw_decode(s)[0])
for k in ["publishDate", "lengthSeconds", "viewCount"]:
    m = re.search('"' + k + '":"?([^",]+)', h); print(k, m.group(1) if m else None)
