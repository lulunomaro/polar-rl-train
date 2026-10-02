import json, sys, collections
m = json.load(open(sys.argv[1], encoding="utf8"))
R = m["root_bbox"]
S = m["solids"]
bad = [s for s in S if any(s["bbox_world"][i] < R[i]-2 for i in range(3)) or any(s["bbox_world"][i+3] > R[i+3]+2 for i in range(3))]
print("bad", len(bad), "of", len(S))
g = collections.OrderedDict()
for s in bad:
    k = "/".join(s["path"].split("/")[:2])
    g.setdefault(k, []).append(s)
out = []
for k, ss in sorted(g.items(), key=lambda kv: -sum(x["volume_mm3"] for x in kv[1])):
    lo = [min(x["bbox_world"][i] for x in ss) for i in range(3)]
    hi = [max(x["bbox_world"][i+3] for x in ss) for i in range(3)]
    out.append("%-46s n=%-4d vol=%8.0fcm3 [%8.1f %8.1f %8.1f] [%8.1f %8.1f %8.1f]" % (k[:46], len(ss), sum(x["volume_mm3"] for x in ss)/1000, lo[0],lo[1],lo[2],hi[0],hi[1],hi[2]))
open(sys.argv[1]+".bad.txt","w",encoding="utf8").write("\n".join(out))
print("\n".join(x[:120] for x in out[:25]))
