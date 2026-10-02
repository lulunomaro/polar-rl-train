"""Where are the leg motors?  Prove/disprove 'two coaxial DM8009 per hip' from the CAD."""
import json, collections, numpy as np
d = json.load(open(r"D:/claude2/fangzhen/cad/out/vehicle/manifest.json", encoding="utf-8"))
items = d["solids"]
HIP_L = np.array([0.0, -223.85, 212.1]); HIP_R = np.array([0.0, 223.85, 212.1])
KNEE_L = np.array([-200.7, -223.85, 150.3]); AXLE_L = np.array([-0.8, -270.25, 0.1])
sel = [it for it in items if ("DM8009" in it["path"] or "8009" in it["path"] or
                              "M3508" in it["path"] or "轮腿电机" in it["path"])
       and it["volume_mm3"] > 3000]
print("big motor-family solids:", len(sel))
g = collections.defaultdict(list)
for it in sel:
    c = np.array(it["com_world"], float)
    leaf = it["path"].split("/")[-1].strip()
    side = "L" if c[1] < 0 else "R"
    # which joint is it nearest?
    dd = {"hipL": np.linalg.norm(c - HIP_L), "kneeL": np.linalg.norm(c - KNEE_L),
          "axleL": np.linalg.norm(c - AXLE_L)}
    dd2 = {"hipR": np.linalg.norm(c - HIP_R)}
    near = min(list(dd.items()) + list(dd2.items()), key=lambda kv: kv[1])[0]
    g[(leaf, side)].append((it["volume_mm3"], c, near, min(dd["hipL"], dd["hipR"] if "hipR" in dd else 9e9)))
for (leaf, side), lst in sorted(g.items()):
    v = sum(x[0] for x in lst) / 1000.0
    c = np.mean([x[1] for x in lst], axis=0)
    print("   %-26s side=%s x%d  vol=%7.1f cm3  com=(%+7.1f,%+7.1f,%+6.1f)  |to hip axis|=%6.1f mm -> %s"
          % (leaf, side, len(lst), v, c[0], c[1], c[2], lst[0][3], lst[0][2]))
print()
# count DM8009 rotor/housing instances per leg
for tag, H in (("LEFT", HIP_L), ("RIGHT", HIP_R)):
    near = [it for it in items if "DM8009" in it["path"] or ("8009" in it["path"] and "髋腿" in it["path"])]
    pick = [it for it in near if ((np.array(it["com_world"]) - H)[1] < 0) == (tag == "LEFT")
            and np.linalg.norm(np.array(it["com_world"])[:3] - H) < 260]
    names = collections.Counter(it["path"].split("/")[-1].strip() for it in pick)
    print("%s hip: %d DM8009-family solids" % (tag, len(pick)), dict(names))
