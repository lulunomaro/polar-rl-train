"""(1) re-derive slope_deg from the real ramp clusters, (2) rasterise a CAD-cropped ramp
patch, (3) render our closed-chain robot standing on that patch in MuJoCo."""
import json, os
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
matplotlib.rcParams["font.sans-serif"] = ["Microsoft YaHei", "DejaVu Sans"]
matplotlib.rcParams["axes.unicode_minus"] = False
from scipy.ndimage import label, gaussian_filter, distance_transform_edt

MAP = r"D:/claude2/fangzhen/cad/out_map"; DOCS = r"D:/claude2/fangzhen/docs/crops"
dims = json.load(open(os.path.join(MAP, "field_dims.json"), encoding="utf-8"))
V = np.load(os.path.join(MAP, "map_verts.npy")); F = np.load(os.path.join(MAP, "map_faces.npy")).astype(np.int64)
tri = V[F]
nrm = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]); ar = 0.5 * np.linalg.norm(nrm, axis=1)
k = ar > 1e-6; tri, nrm, ar = tri[k], nrm[k], ar[k]
up = "xyz".index(dims["up_axis"]); plan = [i for i in range(3) if i != up]; A, B = plan
o = V.min(0)
Zc = (tri[:, :, up].mean(1) - o[up]) / 1000.0
Zlo = (tri[:, :, up].min(1) - o[up]) / 1000.0; Zhi = (tri[:, :, up].max(1) - o[up]) / 1000.0
XA = (tri[:, :, A].mean(1) - o[A]) / 1000.0; XB = (tri[:, :, B].mean(1) - o[B]) / 1000.0
u = np.zeros(3); u[up] = 1.0
tilt = np.degrees(np.arccos(np.clip(np.abs((nrm / (2 * ar)[:, None])) @ u, 0, 1)))

# ---- 1. slope range from the real ramp clusters (rise > 15 cm)
inc = (tilt > 8) & (tilt <= 45) & (ar > 4e4)
g = 0.4
na = int((V[:, A].max() - V[:, A].min()) / 1000 / g) + 1; nb = int((V[:, B].max() - V[:, B].min()) / 1000 / g) + 1
ia = np.clip((XA[inc] / g).astype(int), 0, na - 1); ib = np.clip((XB[inc] / g).astype(int), 0, nb - 1)
cnt = np.zeros((nb, na)); np.add.at(cnt, (ib, ia), ar[inc] / 1e6)
hi = np.full((nb, na), -np.inf); np.maximum.at(hi, (ib, ia), Zhi[inc])
lo = np.full((nb, na), np.inf); np.minimum.at(lo, (ib, ia), Zlo[inc])
span = np.where(np.isfinite(hi) & np.isfinite(lo), hi - lo, 0.0)
lab, n = label(gaussian_filter(cnt, 1.5) > max(0.05, 0.25 * gaussian_filter(cnt, 1.5).max()))
keepf = np.zeros(len(tilt), bool)
for i in range(1, n + 1):
    cm = lab == i
    if cm.sum() == 0 or span[cm].max() < 0.15:
        continue
    sel = inc.copy()
    inside = np.zeros((nb, na), bool); inside[cm] = True
    cell_ok = inside[np.clip((XB[inc] / g).astype(int), 0, nb - 1), np.clip((XA[inc] / g).astype(int), 0, na - 1)]
    idx = np.nonzero(inc)[0][cell_ok]
    keepf[idx] = True
w = ar[keepf]; t = tilt[keepf]
order = np.argsort(t); cw = np.cumsum(w[order]) / w.sum()
qq = lambda p: float(t[order][np.searchsorted(cw, p)])
slope_lo, slope_med, slope_hi = qq(0.05), qq(0.5), qq(0.95)
print("REAL ramp faces: %d, %.1f m2, incline p5=%.1f median=%.1f p95=%.1f deg"
      % (keepf.sum(), w.sum() / 1e6, slope_lo, slope_med, slope_hi))
dims["slope_deg"] = [round(slope_lo, 1), round(slope_hi, 1)]
dims["slope_median_deg"] = round(slope_med, 1)
dims["ramp_area_m2"] = round(float(w.sum() / 1e6), 1)
json.dump(dims, open(os.path.join(MAP, "field_dims.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("field_dims.json updated:", dims["slope_deg"])

# ---- 2. rasterise the biggest ramp cluster into a square patch
best = None
for i in range(1, n + 1):
    cm = lab == i
    if cm.sum() == 0: continue
    a = cnt[cm].sum()
    if best is None or a > best[0]: best = (a, cm)
a, cm = best
ya, xa = np.nonzero(cm)
cx, cy = float(xa.mean() * g), float(ya.mean() * g)
half = 3.4; gs = 0.05; npix = int(2 * half / gs) + 1
inw = (np.abs(XA - cx) < half) & (np.abs(XB - cy) < half)
P = np.full((npix, npix), -np.inf)
ja = np.clip(((XA[inw] - (cx - half)) / gs).astype(int), 0, npix - 1)
jb = np.clip(((XB[inw] - (cy - half)) / gs).astype(int), 0, npix - 1)
np.maximum.at(P, (jb, ja), Zc[inw])
P[~np.isfinite(P)] = np.nan
idx = distance_transform_edt(~np.isfinite(P), return_distances=False, return_indices=True)
P = np.clip(P[tuple(idx)], 0, None); P = gaussian_filter(P, 0.7); P -= P.min()
hmax = float(P.max())
gy, gx = np.gradient(P, gs); slope = np.degrees(np.arctan(np.hypot(gx, gy)))
print("patch centre (%.1f, %.1f): rise %.2f m, incline median %.1f deg over %.1f m2"
      % (cx, cy, hmax, np.median(slope[(slope > 6) & (slope < 45)]), ((slope > 6) & (slope < 45)).sum() * gs * gs))
np.savetxt(os.path.join(MAP, "patch_height.txt"), P.ravel(), fmt="%.5f")
json.dump(dict(npix=npix, gs=gs, half=half, hmax=hmax), open(os.path.join(MAP, "patch_meta.json"), "w"))

fig, axs = plt.subplots(1, 3, figsize=(16, 4.9))
axs[0].imshow(P, cmap="terrain", origin="lower", extent=[-half, half, -half, half])
axs[0].set_title("CAD 截取的 7v7 场地块\n%.1f×%.1f m，落差 %.0f cm" % (2 * half, 2 * half, hmax * 100))
im = axs[1].imshow(slope, cmap="inferno", origin="lower", extent=[-half, half, -half, half], vmin=0, vmax=35)
axs[1].set_title("实测坡度（训练用坡角 %.0f-%.0f°）" % (dims["slope_deg"][0], dims["slope_deg"][1]))
fig.colorbar(im, ax=axs[1], shrink=.85, label="deg")
axs[2].imshow(P, cmap="terrain", origin="lower", extent=[-half, half, -half, half])
axs[2].contour(P, levels=14, colors="k", linewidths=.6, alpha=.55); axs[2].set_title("等高线")
for ax in axs: ax.set_xlabel("X [m]"); ax.set_ylabel("Y [m]")
fig.tight_layout(); fig.savefig(os.path.join(DOCS, "fig_B1_field_patch.png"), dpi=105); plt.close(fig)
print("wrote fig_B1_field_patch.png")
