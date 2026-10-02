import json, collections, numpy as np
d = json.load(open(r"D:/claude2/fangzhen/cad/out/vehicle/manifest.json", encoding="utf-8"))
items = d["solids"]
print("manifest frame:", d.get("frame"), "| unit:", d.get("unit"))
# 1) how many DM8009 / M3508 motor instances, and in which leg sub-assembly
pat = collections.Counter()
for it in items:
    p = it["path"]
    if "DM8009" in p:
        leg = "24 髋腿" if p.split("/")[1].strip().startswith("24") else ("Mirror24 髋腿" if "Mirror" in p.split("/")[1] else "?")
        pat[("DM8009", leg, it["path"].split("/")[-1].strip())] += 1
    if "M3508" in p and it["volume_mm3"] > 5000:
        leg = "24 髋腿" if p.split("/")[1].strip().startswith("24") else ("Mirror24 髋腿" if "Mirror" in p.split("/")[1] else "?")
        pat[("M3508", leg, it["path"].split("/")[-1].strip())] += 1
for k, v in sorted(pat.items()):
    print("   %-8s %-14s %-34s x%d" % (k[0], k[1], k[2][:34], v))
dm = sum(v for k, v in pat.items() if k[0] == "DM8009" and "0001" in k[2])
print("\nDM_8116_0001 (the DM8009 housing) instances in the whole vehicle: %d  -> %d motors/leg"
      % (dm, dm // 2))
# 2) the two hip motors must be COAXIAL: check the axis of the two biggest bores at the hip
print("\nper-leg motor clamp blocks (电机涨块):")
for it in items:
    if "电机涨块" in it["path"]:
        print("   ", it["path"].split("/")[1].strip()[:16], "|", it["path"].split("/")[-1].strip(),
              "com_local=", np.round(it.get("com_local", [0]*3), 1))
