import json, os, sys, collections
import numpy as np
d = sys.argv[1]
m = json.load(open(os.path.join(d, "manifest.json"), encoding="utf8"))
S = m["solids"]
sel = [s for s in S if s["path"].startswith("整车总装/24    髋腿/")]
print("solids in L leg:", len(sel))
g = collections.OrderedDict()
for s in sel:
    parts = s["path"].split("/")
    key = parts[2] if len(parts) > 2 else "?"
    g.setdefault(key, []).append(s)
rows = []
for k, ss in g.items():
    lo = np.array([min(x["bbox_world"][i] for x in ss) for i in range(3)])
    hi = np.array([max(x["bbox_world"][i+3] for x in ss) for i in range(3)])
    vol = sum(x["volume_mm3"] for x in ss)
    rows.append((vol, k, len(ss), lo, hi))
rows.sort(reverse=True)
print("%-34s %4s %9s  %-26s %-26s" % ("child", "n", "vol_cm3", "lo(x,y,z)", "hi(x,y,z)"))
for vol, k, n, lo, hi in rows:
    print("%-34s %4d %9.1f  [%7.1f %7.1f %7.1f] [%7.1f %7.1f %7.1f]" % (k[:34], n, vol/1000, lo[0],lo[1],lo[2], hi[0],hi[1],hi[2]))
