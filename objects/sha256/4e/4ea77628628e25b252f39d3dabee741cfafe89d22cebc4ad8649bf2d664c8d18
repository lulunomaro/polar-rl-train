"""Diagnose the closed-chain viewer data (docs/viz/model.json + parts.bin).

Checks exactly the two things that make a mesh look "detached / orbiting":
  1. units   - are the stored vertices metres or millimetres, and is mesh_scale applied?
  2. frame   - are the stored vertices in the owning BODY's local frame, or already
               baked in the world frame (then any joint rotation orbits them)?
"""
import json, os, sys
import numpy as np

VIZ = r"D:/claude2/fangzhen/docs/viz"
M = json.load(open(os.path.join(VIZ, "model.json"), encoding="utf-8"))
raw = np.fromfile(os.path.join(VIZ, "parts.bin"), dtype="<f4")


def tr3(x, y, z):
    o = np.eye(4); o[0, 3], o[1, 3], o[2, 3] = x, y, z
    return o


def rotq(w, x, y, z):
    n = np.sqrt(w*w + x*x + y*y + z*z)
    w, x, y, z = w/n, x/n, y/n, z/n
    return np.array([[1-2*(y*y+z*z), 2*(x*y-z*w),   2*(x*z+y*w),   0],
                     [2*(x*y+z*w),   1-2*(x*x+z*z), 2*(y*z-x*w),   0],
                     [2*(x*z-y*w),   2*(y*z+x*w),   1-2*(x*x+y*y), 0],
                     [0, 0, 0, 1]])


B = {b["id"]: b for b in M["bodies"]}
root = M["poses"][0]["q"]["__root__"]
W = {}
for b in M["bodies"]:
    if b["parent"] < 0:
        W[b["id"]] = tr3(*root[:3]) @ rotq(*root[3:])
    else:
        q = b["quat"] or [1, 0, 0, 0]
        W[b["id"]] = W[b["parent"]] @ tr3(*b["pos"]) @ rotq(*q)

print("root qpos      :", root)
print("body world @q=0 (m):")
for i in sorted(W):
    print(f"  {i:2d} {B[i]['name']:16s} {np.round(W[i][:3,3], 4)}")

print("\n=== 1. UNITS")
allv = []
for p in M["parts"]:
    v = raw[p["start"]*6:(p["start"]+p["count"])*6].reshape(-1, 6)
    if p["kind"] == "mesh":
        allv.append(v[:, :3])
allv = np.vstack(allv)
print(f"  mesh vertex extent (stored units): {np.round(allv.min(0),2)} .. {np.round(allv.max(0),2)}")
print(f"  robot body-frame extent is ~0.7 m  ->  stored numbers are ~1000x larger")
print(f"  mesh_scale present in model.json   : {M['parts'][0].get('mesh_scale')}")
html = open(os.path.join(VIZ, "model_viewer.html"), encoding="utf-8").read()
print(f"  viewer applies mesh_scale anywhere : {'mesh_scale' in html}")
print(f"  viewer multiplies any 0.001 scale  : {'uScale' in html or 'scale' in html.split('// ================= GL')[1]}")

print("\n=== 2. FRAME of each stored mesh")
print("  a mesh baked in the BODY frame must be centred near the body origin;")
print("  a mesh baked in the WORLD frame will sit ~|body origin| away -> it orbits.")
bad = []
for p in M["parts"]:
    if p["kind"] != "mesh":
        continue
    v = raw[p["start"]*6:(p["start"]+p["count"])*6].reshape(-1, 6)[:, :3]
    ctr_mm = (v.min(0) + v.max(0)) / 2
    ctr_m = ctr_mm * 1e-3
    bo = W[p["body"]][:3, 3]
    d = np.linalg.norm(ctr_m - bo)
    flag = "" if d < 0.25 else "   <-- far from its body origin"
    if d >= 0.25:
        bad.append(p["name"])
    print(f"  {p['name']:18s} body={B[p['body']]['name']:14s} "
          f"centre(m)={np.round(ctr_m,3)} body_origin={np.round(bo,3)} dist={d:.3f}{flag}")
print(f"\n  parts whose baked centre is >0.25 m from their body origin: {len(bad)}")

print("\n=== 3. primitive collision geoms (generated in metres, for scale contrast)")
for p in M["parts"]:
    if p["kind"] != "mesh":
        print(f"  {p['name']:20s} {p['kind']:9s} pos={np.round(p['pos'],4)} "
              f"size={p.get('size') or p.get('fromto') or p.get('radius')}")
