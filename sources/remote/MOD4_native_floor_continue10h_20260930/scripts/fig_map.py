"""Effect figures: (A) the 2026 7v7 map measured from CAD, (B) our closed-chain robot on
a CAD-cropped piece of that map, (C) the measured skill ladders, (D) training curves."""
import json, os, sys
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
matplotlib.rcParams["font.sans-serif"] = ["Microsoft YaHei", "DejaVu Sans"]
matplotlib.rcParams["axes.unicode_minus"] = False

MAP = r"D:/claude2/fangzhen/cad/out_map"
DOCS = r"D:/claude2/fangzhen/docs/crops"
os.makedirs(DOCS, exist_ok=True)
dims = json.load(open(os.path.join(MAP, "field_dims.json"), encoding="utf-8"))
V = np.load(os.path.join(MAP, "map_verts.npy")); F = np.load(os.path.join(MAP, "map_faces.npy")).astype(np.int64)
tri = V[F]
nrm = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
ar = 0.5 * np.linalg.norm(nrm, axis=1)
keep = ar > 1e-9
tri = tri[keep]; nrm = nrm[keep]; ar = ar[keep]
up = "xyz".index(dims["up_axis"])
plan = [i for i in range(3) if i != up]
A, B = plan
o = V.min(0)
Z = (tri[:, :, up].mean(1) - o[up]) / 1000.0
XA = (tri[:, :, A].mean(1) - o[A]) / 1000.0
XB = (tri[:, :, B].mean(1) - o[B]) / 1000.0
u = np.zeros(3); u[up] = 1.0
tilt = np.degrees(np.arccos(np.clip(np.abs((nrm / (2 * ar)[:, None])) @ u, 0, 1)))

res = 0.06
na = int((V[:, A].max() - V[:, A].min()) / 1000 / res) + 1
nb = int((V[:, B].max() - V[:, B].min()) / 1000 / res) + 1
ia = np.clip(((XA - o[A] / 1000.0) / res).astype(int), 0, na - 1)
ib = np.clip(((XB - o[B] / 1000.0) / res).astype(int), 0, nb - 1)
H = np.full((nb, na), -np.inf)      # -inf, not NaN: np.maximum.at would keep NaN
np.maximum.at(H, (ib, ia), Z)                       # top surface per cell
from scipy.ndimage import binary_dilation, distance_transform_edt, gaussian_filter
bad = ~np.isfinite(H)
idx = distance_transform_edt(bad, return_distances=False, return_indices=True)
Hf = H[tuple(idx)]; Hf[~np.isfinite(Hf)] = 0.0
Hs = gaussian_filter(Hf, 1.0)
gy, gx = np.gradient(Hs, res)
slope_map = np.degrees(np.arctan(np.hypot(gx, gy)))
sh = np.clip((Hs[1:, :-1] - Hs[:-1, 1:]) / (2 * res * 1.41), -1, 1)
hill = np.zeros_like(Hs); hill[1:, :-1] = 0.5 + 0.5 * sh

fig, axs = plt.subplots(1, 3, figsize=(19, 5.6), gridspec_kw={"width_ratios": [1.9, 1, 1]})
ax = axs[0]; ax.imshow(hill * (1.0 + 0.0) + 0.02, cmap="gray", origin="lower",
                       extent=[0, na * res, 0, nb * res])
im = ax.imshow(Hs, cmap="terrain", alpha=0.72, origin="lower", extent=[0, na * res, 0, nb * res])
ax.set_title("RMUC2026 7v7 地图（CAD 栅格化，%.1f x %.1f m）" % (na * res, nb * res), fontsize=11)
ax.set_xlabel("X [m]"); ax.set_ylabel("Y [m]"); fig.colorbar(im, ax=ax, shrink=.8, label="height [m]")
ramp = (tilt > 8) & (tilt <= 40) & (Z < 1.3) & (ar > 1e4)
ax2 = axs[1]; m2 = (slope_map > 6) & (slope_map < 45)
ax2.imshow(m2, cmap="hot_r", origin="lower", extent=[0, na * res, 0, nb * res])
ax2.set_title("可行驶坡道区域（6-45°）%.1f m²" % (m2.sum() * res * res), fontsize=11)
ax3 = axs[2]
bins = np.arange(0, 46, 2)
w = ar[(tilt > 3) & (tilt < 45) & (Z < 1.3)]
ax3.hist(np.clip(tilt[(tilt > 3) & (tilt < 45) & (Z < 1.3)], 0, 45), bins=bins, weights=w, color="tab:blue")
ax3.set_title("坡面倾角面积分布（低处 <1.3 m）", fontsize=11)
ax3.set_xlabel("incline [deg]"); ax3.set_ylabel("surface area [m²]")
ax3.axvspan(dims["slope_deg"][0], dims["slope_deg"][1], color="tab:orange", alpha=.25,
            label="训练用 %.0f-%.0f°" % tuple(dims["slope_deg"])); ax3.legend(fontsize=9)
fig.tight_layout(); fn = os.path.join(DOCS, "fig_A_map_2026.png")
fig.savefig(fn, dpi=105); plt.close(fig); print("wrote", fn)
np.save(os.path.join(MAP, "field_height.npy"), Hs)

# ---------------------------------------------------------------- B. crop a real ramp patch
half = 3.2
ramp_all = (tilt > 8) & (tilt <= 40) & (Z < 1.3) & (ar > 1e4)
print("ramp-like faces in the whole map:", int(ramp_all.sum()))
cands = [(float(np.median(XA[ramp_all])), float(np.median(XB[ramp_all])))]
best = None
for cx, cy in cands + [(float(np.percentile(XA[ramp_all], q)), float(np.percentile(XB[ramp_all], q)))
                       for q in (10, 25, 50, 75, 90)]:
    w = ramp_all & (np.abs(XA - cx) < half) & (np.abs(XB - cy) < half)
    if w.sum() and (best is None or w.sum() > best[2]):
        best = (cx, cy, int(w.sum()))
cx, cy, nrf = best
inwin = (np.abs(XA - cx) < half) & (np.abs(XB - cy) < half)
print("chosen patch centre (%.2f, %.2f): %d ramp faces, %d faces total" % (cx, cy, nrf, int(inwin.sum())))
g = 0.05
n = int(2 * half / g) + 1
P2 = np.full((n, n), -np.inf)
ja2 = np.clip(((tri[inwin][:, :, A].mean(1) - (cx - half)) / g).astype(int), 0, n - 1)
jb2 = np.clip(((tri[inwin][:, :, B].mean(1) - (cy - half)) / g).astype(int), 0, n - 1)
np.maximum.at(P2, (jb2, ja2), Z[inwin])
if np.isinf(P2).all():
    raise SystemExit("patch rasterisation produced nothing")
P2 = P2 - np.nanmin(np.where(np.isfinite(P2), P2, np.nan))
P2[~np.isfinite(P2)] = np.nan
idx2 = distance_transform_edt(~np.isfinite(P2), return_distances=False, return_indices=True)
P = np.clip(P2[tuple(idx2)], 0, None)
P = gaussian_filter(P, 0.8)
hmax = float(P.max())
gy2, gx2 = np.gradient(P, g)
patch_slope = np.degrees(np.arctan(np.hypot(gx2, gy2)))
print("patch height %.3f m, max incline %.1f deg, mean incline over 6-45 deg cells: %.1f"
      % (hmax, patch_slope.max(), patch_slope[(patch_slope > 6) & (patch_slope < 45)].mean()))
fig, axs = plt.subplots(1, 3, figsize=(16, 5.0))
axs[0].imshow(P, cmap="terrain", origin="lower", extent=[-half, half, -half, half])
axs[0].set_title("CAD 截取的真实场地块 %.1f x %.1f m\n落差 %.0f cm" % (2 * half, 2 * half, hmax * 100))
im2 = axs[1].imshow(patch_slope, cmap="inferno", origin="lower", extent=[-half, half, -half, half],
                    vmin=0, vmax=45)
axs[1].set_title("该块地形的坡度（来自 CAD 实测）")
fig.colorbar(im2, ax=axs[1], shrink=.85, label="incline [deg]")
axs[2].imshow(P, cmap="terrain", origin="lower", extent=[-half, half, -half, half])
axs[2].contour(P, levels=12, colors="k", linewidths=.5, alpha=.5)
axs[2].set_title("等高线图")
np.savetxt(os.path.join(MAP, "patch_height.txt"), P.ravel(), fmt="%.5f")
json.dump(dict(n=n, g=g, half=half, hmax=hmax, cx=cx, cy=cy), open(os.path.join(MAP, "patch_meta.json"), "w"))
fig.tight_layout(); fn = os.path.join(DOCS, "fig_B1_field_patch.png"); fig.savefig(fn, dpi=105)
plt.close(fig); print("wrote", fn)
