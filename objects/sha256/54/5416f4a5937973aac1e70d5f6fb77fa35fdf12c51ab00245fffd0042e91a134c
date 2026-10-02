import io, json, os
import numpy as np
import yaml
ROOT = r"D:/claude2/fangzhen"
spec = yaml.safe_load(open(os.path.join(ROOT, "robot/vehicle.spec.yaml"), encoding="utf-8"))
R = np.array(spec["frame"]["rot"]); A4 = np.eye(4)
A4[:3, :3] = R; A4[:3, 3] = -R @ np.array(spec["frame"]["origin_cad"], float)
man = json.load(io.open(os.path.join(ROOT, "cad/out/vehicle/manifest.json"), encoding="utf-8"))
LEG = ("整车总装/24    髋腿", "整车总装/Mirror24    髋腿")
rows = []
for s in man["solids"]:
    if s["path"].startswith(LEG):
        continue
    bb = json.loads(s["bbox_world"]) if isinstance(s["bbox_world"], str) else list(s["bbox_world"])
    lo = A4[:3, :3] @ np.array(bb[:3], float) + A4[:3, 3]
    hi = A4[:3, :3] @ np.array(bb[3:], float) + A4[:3, 3]
    z0, z1 = min(lo[2], hi[2]), max(lo[2], hi[2])
    rows.append((s["product"].strip(), z0, z1, (s.get("volume_mm3") or 0) / 1000.0))
print("chassis solids:", len(rows), " z envelope %.1f..%.1f mm" % (min(r[1] for r in rows), max(r[2] for r in rows)))
for lo, hi in ((250, 420), (300, 380), (560, 650)):
    band = [r for r in rows if r[2] > lo and r[1] < hi]
    print("\n band %d..%d mm : %d solids" % (lo, hi, len(band)))
    for nm, a, b, v in sorted(band, key=lambda r: r[1])[:10]:
        print("    %-32s z %6.1f..%6.1f  %6.1f cm3" % (nm[:32], a, b, v))
iv = sorted([(r[1], r[2]) for r in rows])
cur, gaps = -1e9, []
for a, b in iv:
    if a > cur + 20:
        gaps.append((cur, a))
    cur = max(cur, b)
print("\nempty bands >20 mm:", ["%.0f..%.0f mm" % g for g in gaps])
print("\nwhat is directly above/below each gap:")
for a, b in gaps:
    below = sorted([r for r in rows if r[2] <= a], key=lambda r: -r[2])[:3]
    above = sorted([r for r in rows if r[1] >= b], key=lambda r: r[1])[:3]
    print("  gap %.0f..%.0f mm" % (a, b))
    for nm, x, y, v in below:
        print("      below: %-30s z %6.1f..%6.1f" % (nm[:30], x, y))
    for nm, x, y, v in above:
        print("      above: %-30s z %6.1f..%6.1f" % (nm[:30], x, y))