"""Build the leg's kinematic graph from the STEP: part <-> shared revolute axis."""
import json, os, collections
import numpy as np
import yaml
exec(open(r"D:/claude2/fangzhen/scripts/extract_joints.py", encoding="utf-8").read()
     .split("# left leg subtree only")[0])          # reuse the reader/walker

walk(free.Value(1), np.eye(4), [], 0)
left = [f for f in faces if f[3].startswith("24    髋腿")]
print("lateral cylindrical faces in the left leg:", len(left))

# cluster axes
clusters = []
for xz, y, r, sub, part in left:
    for c in clusters:
        if np.linalg.norm(np.array(c["xz"]) - xz) < 4.0:
            c["r"].add(round(r, 1)); c["parts"].add(part); c["sub"].add(sub); break
    else:
        clusters.append({"xz": list(xz), "r": {round(r, 1)},
                         "parts": {part}, "sub": {sub}})

spec = yaml.safe_load(open(r"D:/claude2/fangzhen/robot/vehicle.spec.yaml", encoding="utf-8"))
def link_of(p):
    for lk in spec["links"]:
        if lk.get("all") and not all(re.search(x, p) for x in lk["all"]): continue
        if lk.get("any") and not any(re.search(x, p) for x in lk["any"]): continue
        if lk.get("not") and any(re.search(x, p) for x in lk["not"]): continue
        return lk["name"]
    return None
import re
man = json.load(open(r"D:/claude2/fangzhen/cad/out/vehicle/manifest.json", encoding="utf-8"))
part2link = {}
for s in man["solids"]:
    if s["path"].startswith("整车总装/24    髋腿"):
        part2link[s["product"].strip()] = link_of(s["path"])

HIP = np.array([0.0, 212.1]); KNEE = np.array([-200.7, 150.3]); WHEEL = np.array([-0.8, 0.1])
print("\naxes where >=2 distinct parts meet (radius >= 4 mm), sorted by importance:")
print("  x-z(mm)        dist(hip/knee/wheel)   parts -> current link assignment")
rows = []
for c in clusters:
    if len(c["parts"]) < 2:
        continue
    if max(c["r"]) < 4.0:
        continue
    xz = np.array(c["xz"])
    rows.append((len(c["parts"]), xz, c))
rows.sort(key=lambda t: -t[0])
for n, xz, c in rows[:22]:
    d = (np.linalg.norm(xz - HIP), np.linalg.norm(xz - KNEE), np.linalg.norm(xz - WHEEL))
    lab = min(zip(("hip", "knee", "wheel"), d))[0] if min(d) < 14 else "free"
    pl = sorted(c["parts"])
    asg = collections.Counter(part2link.get(p, "?") for p in pl)
    print("  (%7.1f,%6.1f) d_h=%5.1f d_k=%5.1f d_w=%5.1f [%s] n=%d r=%s  %s"
          % (xz[0], xz[1], d[0], d[1], d[2], lab, n,
             ",".join(str(x) for x in sorted(c["r"])[:3]),
             " ".join("%s:%d" % (k, v) for k, v in asg.items())))
    print("        parts:", ", ".join(pl)[:150])

print("\n=== the two cranks of the similar-linkage (doc 0.1134 / 0.133) ===")
for name, p in (("pinL", (-110.0, 178.2)), ("pinR", (109.7, 177.3)),
                ("apex", (-0.5, 95.9))):
    print("  %-5s %-16s |hip|=%6.1f |knee|=%6.1f |wheel|=%6.1f"
          % (name, p, np.linalg.norm(np.array(p) - HIP),
             np.linalg.norm(np.array(p) - KNEE), np.linalg.norm(np.array(p) - WHEEL)))
print("  hip->pinL = %.1f mm   hip->pinR = %.1f mm   (doc: 113.4)"
      % (np.linalg.norm(np.array([-110, 178.2]) - HIP),
         np.linalg.norm(np.array([109.7, 177.3]) - HIP)))
print("  pinL->apex = %.1f mm  pinR->apex = %.1f mm  (doc: 133)"
      % (np.linalg.norm(np.array([-110, 178.2]) - np.array([-0.5, 95.9])),
         np.linalg.norm(np.array([109.7, 177.3]) - np.array([-0.5, 95.9]))))
print("  similarity ratio 113.4/210.0 = %.3f  (doc: 0.54)" % (113.4 / 210.0))
