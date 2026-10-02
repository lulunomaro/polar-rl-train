import json, io, os, collections
import numpy as np
paths = [r"D:/claude2/fangzhen/cad/out/manifest.json", r"D:/claude2/fangzhen/cad/out/manifests.json"]
p = next((x for x in paths if os.path.exists(x)), None)
print("manifest:", p)
if p is None:
    for dp, dn, fn in os.walk(r"D:/claude2/fangzhen/cad"):
        for f in fn:
            if f.endswith(".json"):
                print("   candidate:", os.path.join(dp, f))
    raise SystemExit
man = json.load(io.open(p, encoding="utf-8"))
sol = man["solids"]
print("total solids in manifest:", len(sol))
top = collections.Counter(s["path"].split("/")[1] if "/" in s["path"] else s["path"] for s in sol)
print("top-level branches (%d):" % len(top))
for k, v in top.most_common(14):
    print("   %5d  %s" % (v, k[:80]))
# where do the missing z-bands live? look at parts named like turret/gimbal/云台
KEY = ("云台", "gimbal", "炮", "管", "弹", "UWB", "uwb", "复活", "支撑", "碳板", "轴")
rows = []
for s in sol:
    nm = s["product"].strip()
    if any(k in nm for k in KEY):
        bb = s.get("bbox") or s.get("bounds")
        rows.append((nm, s["path"].split("/")[1] if "/" in s["path"] else "-", bb))
print("\nnamed turret/gimbal/uwb/support solids:", len(rows))
for nm, br, bb in rows[:18]:
    print("   %-28s | %-24s | %s" % (nm[:28], br[:24], bb if bb is None else np.round(bb, 1).tolist()))
print("\nsolids WITH bbox info:", sum(1 for s in sol if s.get("bbox")), "/", len(sol))
print("sample keys of a solid:", sorted(sol[0].keys()))