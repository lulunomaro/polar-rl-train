"""Voxel self-collision scan of the leg workspace.

Rotates the CAD point clouds of thigh/shank/wheel through the claimed joint limits and
checks them against the chassis voxels, so the joint ranges in vehicle.spec.yaml are
backed by geometry instead of guesswork.  Uses the coarse tessellation (defl 3.0).
"""
import json, os, re, collections
import numpy as np
import trimesh
import yaml

SPEC = r"D:/claude2/fangzhen/robot/vehicle.spec.yaml"
MAN = r"D:/claude2/fangzhen/cad/out/vehicle_coarse/manifest.json"
FINE = r"D:/claude2/fangzhen/cad/out/vehicle/manifest.json"
VOX = 0.010
CLEAR = 0.006          # treat closer than this as interference

spec = yaml.safe_load(open(SPEC, encoding="utf-8"))
R = np.array(spec["frame"]["rot"]); A = np.eye(4)
A[:3, :3] = R; A[:3, 3] = -R @ np.array(spec["frame"]["origin_cad"], float)
man = json.load(open(MAN, encoding="utf-8"))
fman = json.load(open(FINE, encoding="utf-8"))
key = {(s["path"], round(s["volume_mm3"], 1)): s["obj"] for s in man["solids"]}
mdir_c = os.path.dirname(MAN) + "/meshes"
mdir_f = os.path.dirname(FINE) + "/meshes"

def link_of(p):
    for lk in spec["links"]:
        if lk.get("all") and not all(re.search(x, p) for x in lk["all"]): continue
        if lk.get("any") and not any(re.search(x, p) for x in lk["any"]): continue
        if lk.get("not") and any(re.search(x, p) for x in lk["not"]): continue
        return lk["name"]
sel = collections.defaultdict(list)
for s in fman["solids"]:
    sel[link_of(s["path"])].append(s)

rng = np.random.default_rng(0)
def cloud(link, budget):
    ss = sel[link]
    tot = sum(s["ntris"] for s in ss) or 1
    out = []
    for s in ss:
        obj = key.get((s["path"], round(s["volume_mm3"], 1)), s["obj"])
        d = mdir_c if obj in os.listdir(mdir_c) and False else mdir_f
        try:
            m = trimesh.load(os.path.join(d, obj), process=False)
        except Exception:
            continue
        v = np.asarray(m.vertices, dtype=np.float64)
        keep = max(400, int(len(v) * budget / max(1, tot) * 6))
        if len(v) > keep:
            v = v[rng.choice(len(v), keep, replace=False)]
        out.append(v)
    V = np.vstack(out)
    W = (A[:3, :3] @ V.T).T + A[:3, 3]
    return W / 1000.0                      # metres, robot frame

def vox(P, origin, dims):
    idx = np.floor((P - origin) / VOX).astype(np.int64)
    ok = ((idx >= 0) & (idx < dims[:, None])).all(0)
    idx = idx[:, ok]
    lin = (idx[0] * dims[1] + idx[1]) * dims[2] + idx[2]
    return np.zeros(int(dims[0] * dims[1] * dims[2]), dtype=bool), lin

LO = np.array([-0.60, -0.45, -0.10]); HI = np.array([0.60, 0.45, 0.75])
DIMS = np.ceil((HI - LO) / VOX).astype(int)
def to_grid(P):
    i = np.floor((P - LO) / VOX).astype(np.int64)
    ok = ((i >= 0) & (i < DIMS[None, :])).all(1)
    i = i[ok]
    return (i[:, 0] * DIMS[1] + i[:, 1]) * DIMS[2] + i[:, 2]

base = cloud("base", 260000)
thigh = cloud("thigh_L", 90000); shank = cloud("shank_L", 45000); wheel = cloud("wheel_L", 14000)
Gb = np.zeros(int(DIMS.prod()), dtype=bool)
Gb[to_grid(base)] = True
print("voxel occupancy: base %d, thigh %d, shank %d, wheel %d cells"
      % (Gb.sum(), len(set(to_grid(thigh).tolist())), len(set(to_grid(shank).tolist())),
         len(set(to_grid(wheel).tolist()))))

hip_c = np.array([0.0, -0.22385, 0.2121]); knee_c = np.array([-0.2007, -0.22385, 0.1503])
def rot_about(axis_pt, axis, P, ang):
    d = np.asarray(axis, float); d /= np.linalg.norm(d)
    c, s = np.cos(ang), np.sin(ang)
    v = P - axis_pt
    return axis_pt + v * c + np.cross(v, d) * (-s) + np.outer(v @ d, d) * (1 - c)

def dilate(grid, r):
    """grow the chassis occupancy by r metres so near-misses count as interference"""
    k = max(1, int(round(r / VOX)))
    f = grid.reshape(DIMS)
    for _ in range(k):
        f = (f | np.roll(f, 1, 0) | np.roll(f, -1, 0)
                | np.roll(f, 1, 1) | np.roll(f, -1, 1)
                | np.roll(f, 1, 2) | np.roll(f, -1, 2))
    return f.ravel()

# The assembly is connected: leg and chassis clouds necessarily touch inside the joint
# bosses, so exclude a 30 mm cylinder around every joint axis before testing.
AXES = [(hip_c, (0, 1, 0)), (knee_c, (0, 1, 0)),
        (np.array([-0.0009, -0.27025, 0.0]), (0, 1, 0))]
def near_joint(P, r=0.030):
    m = np.zeros(len(P), dtype=bool)
    for c, a in AXES:
        a = np.asarray(a, float); v = P - c
        d = np.linalg.norm(v - np.outer(v @ a, a), axis=1)
        m |= (d < r)
    return m
base_f = base[~near_joint(base)]
thigh_f = thigh[~near_joint(thigh)]
shank_f = shank[~near_joint(shank)]
wheel_f = wheel[~near_joint(wheel)]
print("after removing 30 mm joint bosses: base %d->%d, thigh %d->%d, shank %d->%d, wheel %d->%d"
      % (len(base), len(base_f), len(thigh), len(thigh_f), len(shank), len(shank_f),
         len(wheel), len(wheel_f)))
Gb = np.zeros(int(DIMS.prod()), dtype=bool); Gb[to_grid(base_f)] = True
Gb_c = dilate(Gb, CLEAR)
hits, overlap = [], []
HIP = np.arange(-1.8, 1.85, 0.15)
KNEE = np.arange(-2.2, 2.25, 0.15)
for q1 in HIP:
    row = []
    for q2 in KNEE:
        th = rot_about(hip_c, (0, 1, 0), thigh, q1)
        sk0 = rot_about(knee_c, (0, 1, 0), shank, q2)
        wh0 = rot_about(knee_c, (0, 1, 0), wheel, q2)
        # knee rotation carries the shank/wheel through the hip rotation as well
        sk = rot_about(hip_c, (0, 1, 0), sk0, q1)
        wh = rot_about(hip_c, (0, 1, 0), wh0, q1)
        n = (int(Gb_c[to_grid(thigh_f)].any()) and 0)  # placeholder
        cnt = (Gb_c[to_grid(rot_about(hip_c, (0, 1, 0), thigh_f, q1))].sum()
               + Gb_c[to_grid(rot_about(hip_c, (0, 1, 0),
                    rot_about(knee_c, (0, 1, 0), shank_f, q2), q1))].sum()
               + Gb_c[to_grid(rot_about(hip_c, (0, 1, 0),
                    rot_about(knee_c, (0, 1, 0), wheel_f, q2), q1))].sum())
        row.append(cnt >= 5)
        overlap.append(cnt)
    hits.append(row)
hits = np.array(hits)
print("\nleg-vs-chassis interference map (rows = hip q1, cols = knee q2; '.' free, 'X' hits)")
print("        knee: " + "".join("%4.1f" % q for q in KNEE))
for i, q1 in enumerate(HIP):
    print("  hip %5.2f  " % q1 + "".join("   X " if hits[i, j] else "   . " for j in range(len(KNEE))))
hits = np.array(hits, dtype=bool)
free = ~hits
print("\nfree fraction: %.1f%%" % (100 * free.mean()))
if free.any():
    print("hip angles with >=1 free knee: [%.2f, %.2f] rad"
          % (HIP[free.any(1)].min(), HIP[free.any(1)].max()))
    print("knee angles with >=1 free hip: [%.2f, %.2f] rad"
          % (KNEE[free.any(0)].min(), KNEE[free.any(0)].max()))
ov = np.array(overlap).reshape(len(HIP), len(KNEE))
print("worst overlap (voxel count) at hip/knee = %.2f / %.2f : %d"
      % (HIP[np.unravel_index(ov.argmax(), ov.shape)[0]],
         KNEE[np.unravel_index(ov.argmax(), ov.shape)[1]], ov.max()))
print("overlap at the zero (CAD) pose: %d voxels" % ov[len(HIP)//2, np.argmin(abs(KNEE))])
np.save(r"D:/claude2/fangzhen/robot/out/workspace_scan.npy", hits)
