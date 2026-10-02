import io, json, os
import numpy as np
import yaml
import trimesh

ROOT = r"D:/claude2/fangzhen"
spec = yaml.safe_load(open(os.path.join(ROOT, "robot/vehicle.spec.yaml"), encoding="utf-8"))
R = np.array(spec["frame"]["rot"]); A4 = np.eye(4)
A4[:3, :3] = R; A4[:3, 3] = -R @ np.array(spec["frame"]["origin_cad"], float)
print("frame rot=\n", np.round(R, 3), "\norigin_cad=", spec["frame"]["origin_cad"])

man = json.load(io.open(os.path.join(ROOT, "cad/out/vehicle/manifest.json"), encoding="utf-8"))
sol = man["solids"]
LEG_PREFIX = ("整车总装/24    髋腿", "整车总装/Mirror24    髋腿")
rows = []
for s in sol:
    p = s["path"]
    if p.startswith(LEG_PREFIX):
        continue                      # chassis-side by the build's own rule
    c = np.array(json.loads(s["com_world"]) if isinstance(s["com_world"], str) else s["com_world"], float)
    q = A4[:3, :3] @ c + A4[:3, 3]
    bb = json.loads(s["bbox_world"]) if isinstance(s["bbox_world"], str) else list(s["bbox_world"])
    b0 = A4[:3, :3] @ np.array(bb[:3], float) + A4[:3, 3]
    b1 = A4[:3, :3] @ np.array(bb[3:], float) + A4[:3, 3]
    z0, z1 = min(b0[2], b1[2]), max(b0[2], b1[2])
    rows.append((s["product"].strip(), q, z0, z1, (s.get("volume_mm3") or 0) / 1000.0))
rows.sort(key=lambda r: -r[2])
print("\nchassis-side solids: %d" % len(rows))
print("\n--- what occupies the model z-band 250..420 mm (the visible gap)? ---")
band = [r for r in rows if r[3] > 0.250 and r[2] < 0.420]
for nm, q, z0, z1, v in band[:20]:
    print("   %-30s z %6.1f..%6.1f mm  vol %7.1f cm3" % (nm[:30], z0 * 1000, z1 * 1000, v))
print("   -> %d chassis solids cross that band" % len(band))
print("\n--- the 12 highest and the 12 lowest chassis solids (mm) ---")
for nm, q, z0, z1, v in rows[:12]:
    print("   hi %-30s z %6.1f..%6.1f  vol %7.1f" % (nm[:30], z0 * 1000, z1 * 1000, v))
for nm, q, z0, z1, v in rows[-12:]:
    print("   lo %-30s z %6.1f..%6.1f  vol %7.1f" % (nm[:30], z0 * 1000, z1 * 1000, v))
gaps = []
zs = sorted([(r[2], r[3], r[0]) for r in rows])
cur = -1e9
for z0, z1, nm in zs:
    if z0 > cur + 0.02:
        gaps.append((cur, z0))
    cur = max(cur, z1)
print("\nempty bands > 20 mm inside the chassis envelope:", ["%.0f..%.0f mm" % (a * 1000, b * 1000) for a, b in gaps])