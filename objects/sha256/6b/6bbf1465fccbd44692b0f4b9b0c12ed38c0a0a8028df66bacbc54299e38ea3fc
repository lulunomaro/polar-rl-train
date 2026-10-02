"""Locate the REAL drivable ramps: spatially cluster the inclined faces and measure each
cluster's height range.  Tiny floor bevels are excluded by requiring a large rise."""
import json, os
import numpy as np
from scipy.ndimage import label, maximum_filter, gaussian_filter

MAP = r"D:/claude2/fangzhen/cad/out_map"
dims = json.load(open(os.path.join(MAP, "field_dims.json"), encoding="utf-8"))
V = np.load(os.path.join(MAP, "map_verts.npy")); F = np.load(os.path.join(MAP, "map_faces.npy")).astype(np.int64)
tri = V[F]
nrm = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
ar = 0.5 * np.linalg.norm(nrm, axis=1)
keep = ar > 1e-6
tri, nrm, ar = tri[keep], nrm[keep], ar[keep]
up = "xyz".index(dims["up_axis"]); plan = [i for i in range(3) if i != up]; A, B = plan
o = V.min(0)
Z = (tri[:, :, up].mean(1) - o[up]) / 1000.0
Zlo = (tri[:, :, up].min(1) - o[up]) / 1000.0
Zhi = (tri[:, :, up].max(1) - o[up]) / 1000.0
XA = (tri[:, :, A].mean(1) - o[A]) / 1000.0
XB = (tri[:, :, B].mean(1) - o[B]) / 1000.0
u = np.zeros(3); u[up] = 1.0
tilt = np.degrees(np.arccos(np.clip(np.abs((nrm / (2 * ar)[:, None])) @ u, 0, 1)))

inc = (tilt > 8) & (tilt <= 45) & (ar > 4e4)          # faces bigger than 0.04 m2
print("inclined faces >0.04 m2:", int(inc.sum()), "area %.1f m2" % (ar[inc].sum() / 1e6))
g = 0.4
na = int((V[:, A].max() - V[:, A].min()) / 1000 / g) + 1
nb = int((V[:, B].max() - V[:, B].min()) / 1000 / g) + 1
ia = np.clip((XA[inc] / g).astype(int), 0, na - 1); ib = np.clip((XB[inc] / g).astype(int), 0, nb - 1)
cnt = np.zeros((nb, na)); np.add.at(cnt, (ib, ia), ar[inc] / 1e6)
hi = np.full((nb, na), -np.inf); np.maximum.at(hi, (ib, ia), Zhi[inc])
lo = np.full((nb, na), np.inf); np.minimum.at(lo, (ib, ia), Zlo[inc])
rise = np.where(np.isfinite(hi) & np.isfinite(lo), hi - lo, 0.0)
sm = gaussian_filter(cnt, 1.5)
mask = sm > max(0.05, 0.25 * sm.max())
lab, n = label(mask)
print("clusters:", n)
rows = []
for i in range(1, n + 1):
    m = lab == i
    a = cnt[m].sum()
    if a < 0.5:
        continue
    ya, xa = np.nonzero(m)
    rows.append(dict(area_m2=float(a), rise_max=float(rise[m].max()), rise_med=float(np.median(rise[m][rise[m] > 0])),
                     cx=float(xa.mean() * g), cy=float(ya.mean() * g),
                     zmin=float(lo[m][np.isfinite(lo[m])].min()) if np.isfinite(lo[m]).any() else 0,
                     zmax=float(hi[m][np.isfinite(hi[m])].max()) if np.isfinite(hi[m]).any() else 0,
                     ncell=int(m.sum())))
rows.sort(key=lambda r: -r["area_m2"])
print("\ntop ramp clusters (area-weighted):")
print("   area m2 | rise_max | zmin  zmax | span_z | cells | centre (x,y)")
for r in rows[:14]:
    print("   %7.2f |   %5.2f  | %5.2f %5.2f | %6.2f | %4d | (%5.1f, %5.1f)"
          % (r["area_m2"], r["rise_max"], r["zmin"], r["zmax"], r["zmax"] - r["zmin"], r["ncell"], r["cx"], r["cy"]))
big = [r for r in rows if r["zmax"] - r["zmin"] > 0.15]
print("\nclusters that actually change height by >15 cm:", len(big))
if big:
    tot = sum(r["area_m2"] for r in big)
    w = [r["area_m2"] / tot for r in big]
    print("   total area %.1f m2, biggest %.1f m2 at (%.1f, %.1f) spanning z %.2f..%.2f"
          % (tot, max(r["area_m2"] for r in big),
             max(big, key=lambda r: r["area_m2"])["cx"], max(big, key=lambda r: r["area_m2"])["cy"],
             max(big, key=lambda r: r["area_m2"])["zmin"], max(big, key=lambda r: r["area_m2"])["zmax"]))
    best = max(big, key=lambda r: r["area_m2"])
    # incline of that cluster: face tilt area-weighted inside its cells
    m = (np.abs(XA[inc] - best["cx"]) < 2.5) & (np.abs(XB[inc] - best["cy"]) < 2.5)
    t = tilt[inc][m]; w2 = ar[inc][m]
    tt = np.argsort(t); cw = np.cumsum(w2[tt]) / max(1e-9, w2.sum())
    qq = lambda p: float(t[tt][np.searchsorted(cw, p)]) if w2.sum() else float("nan")
    print("   its incline distribution: p10=%.1f median=%.1f p90=%.1f deg over %.1f m2"
          % (qq(.1), qq(.5), qq(.9), w2.sum() / 1e6))
    json.dump(dict(best=best, slope=[round(qq(.1), 1), round(qq(.9), 1)],
                   rise=round(best["zmax"] - best["zmin"], 3)),
              open(os.path.join(MAP, "ramp_cluster.json"), "w"), indent=1)
    print("wrote ramp_cluster.json")
