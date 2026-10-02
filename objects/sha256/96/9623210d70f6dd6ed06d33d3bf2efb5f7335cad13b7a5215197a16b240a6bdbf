import json, os, re, sys
import numpy as np
d = sys.argv[1]
S = json.load(open(os.path.join(d, "solids_classified.json"), encoding="utf8"))
pat = sys.argv[2] if len(sys.argv) > 2 else r"8009|M3508|GM6020|2006|RS02|电机|马达|轮组|轮胎|轮圈|轮子"
rows = [s for s in S if re.search(pat, s["product"], re.I) and "pca" in s]
rows.sort(key=lambda s: -s["volume_mm3"])
lines = []
lines.append("%-6s %-30s %8s %8s %8s  %-30s %s" % ("id","product","r_max","thick","vol_cm3","axis","center"))
for s in rows:
    p = s["pca"]
    a = np.array(p["axis"])
    if np.dot(a, [0,0,1]) < 0: a = -a
    lines.append("%-6s %-30s %8.1f %8.1f %8.1f  [%6.2f %6.2f %6.2f] [%8.1f %8.1f %8.1f]  %s" % (
        s["id"], s["product"][:30], p["r_max"], p["axial_len"], s["volume_mm3"]/1000,
        a[0], a[1], a[2], p["center"][0], p["center"][1], p["center"][2], s["path"][:70]))
open(os.path.join(d, "motors.txt"), "w", encoding="utf8").write("\n".join(lines))
print("\n".join(lines[:70]))
print("total", len(rows))
