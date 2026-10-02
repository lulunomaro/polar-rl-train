"""Clean figures of the RMUC2026 7v7 map + our closed-chain robot on a CAD-cropped ramp.
Uses exact barycentric triangle rasterisation (no centroid splatting artefacts)."""
import json, math, os, struct
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
matplotlib.rcParams["font.sans-serif"] = ["Microsoft YaHei", "DejaVu Sans"]
matplotlib.rcParams["axes.unicode_minus"] = False
from scipy.ndimage import median_filter, gaussian_filter, binary_dilation, distance_transform_edt

MAP = r"D:/claude2/fangzhen/cad/out_map"; DOCS = r"D:/claude2/fangzhen/docs/crops"
RC = r"D:/claude2/fangzhen/robot/out_cc"
dims = json.load(open(os.path.join(MAP, "field_dims.json"), encoding="utf-8"))
V = np.load(os.path.join(MAP, "map_verts.npy")); F = np.load(os.path.join(MAP, "map_faces.npy")).astype(np.int64)
tri = V[F]
nrm = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]); ar = 0.5 * np.linalg.norm(nrm, axis=1)
k = ar > 1e-6; tri, nrm, ar = tri[k], nrm[k], ar[k]
o = V.min(0)
X = (tri[:, :, 0] - o[0]) / 1000.0; Y = (tri[:, :, 1] - o[1]) / 1000.0; Z = (tri[:, :, 2] - o[2]) / 1000.0
u = np.array([0., 0., 1.])
tilt = np.degrees(np.arccos(np.clip(np.abs((nrm / (2 * ar)[:, None])) @ u, 0, 1)))
print("usable faces:", len(ar))


def raster(x, y, z, nx, ny, span, off=(0.0, 0.0)):
    """max-z heightfield by barycentric fill; x/y are (N,3) world coords in metres."""
    H = np.full((ny, nx), -np.inf)
    px = (x - off[0]) / span; py = (y - off[1]) / span
    i0 = np.floor(px.min(1)).astype(int); i1 = np.ceil(px.max(1)).astype(int)
    j0 = np.floor(py.min(1)).astype(int); j1 = np.ceil(py.max(1)).astype(int)
    order = np.argsort((i1 - i0) * (j1 - j0))
    for t in order:
        a, b = i0[t], j0[t]
        w, h = i1[t] - a + 1, j1[t] - b + 1
        if w * h > 6000 or w <= 0 or h <= 0:
            continue
        gi = a + np.arange(w); gj = b + np.arange(h)
        gi = gi[(gi >= 0) & (gi < nx)]; gj = gj[(gj >= 0) & (gj < ny)]
        if not len(gi) or not len(gj):
            continue
        I, J = np.meshgrid(gi + 0.5, gj + 0.5)
        x0, y0 = px[t, 0], py[t, 0]; dx1 = px[t, 1] - x0; dy1 = py[t, 1] - y0
        dx2 = px[t, 2] - x0; dy2 = py[t, 2] - y0
        det = dx1 * dy2 - dx2 * dy1
        if abs(det) < 1e-12:
            continue
        a1 = ((I - x0) * dy2 - (J - y0) * dx2) / det
        a2 = ((J - y0) * dx1 - (I - x0) * dy1) / det
        inside = (a1 >= -0.02) & (a2 >= -0.02) & (a1 + a2 <= 1.02)
        if not inside.any():
            continue
        zz = z[t]
        idx = (J[inside] - gj[0]).astype(np.intp); idy = (I[inside] - gi[0]).astype(np.intp)
        cur = H[gj[0] + idx, gi[0] + idy]
        H[gj[0] + idx, gi[0] + idy] = np.maximum(cur, zz)
    H[~np.isfinite(H)] = np.nan
    if np.isnan(H).any():
        idxs = distance_transform_edt(np.isnan(H), return_distances=False, return_indices=True)
        H = H[tuple(idxs)]
    return np.nan_to_num(H, nan=float(np.nanmin(H)) if np.isfinite(H).any() else 0.0)


# ------------------------------------------------------------------ A. whole field
span = 0.10
nx = int((X.max() - X.min()) / span) + 1; ny = int((Y.max() - Y.min()) / span) + 1
print("whole-field heightmap at %.0f cm -> %dx%d (vectorised splat of face corners+"
      "centroid, then median filter)" % (span * 100, nx, ny))
# only faces whose centre is below 1.3 m: that is the WALKABLE surface (floor, ramps,
# steps, low barricades); the towers/stands above it would otherwise hide everything
walk = Z.mean(1) < 1.30
Xw, Yw, Zw = X[walk], Y[walk], Z[walk]
print("walkable faces (<1.3 m): %d of %d" % (walk.sum(), len(walk)))
HA = np.full((ny, nx), -np.inf)
for s_i in range(3):
    ii = np.clip(((Xw[:, s_i] - 0) / span).astype(np.intp), 0, nx - 1)
    jj = np.clip(((Yw[:, s_i] - 0) / span).astype(np.intp), 0, ny - 1)
    np.maximum.at(HA, (jj, ii), Zw[:, s_i])
ii = np.clip((Xw.mean(1) / span).astype(np.intp), 0, nx - 1)
jj = np.clip((Yw.mean(1) / span).astype(np.intp), 0, ny - 1)
np.maximum.at(HA, (jj, ii), Zw.mean(1))
HA = np.where(np.isfinite(HA), HA, np.nan)
HA = median_filter(np.nan_to_num(HA, nan=float(np.nanmin(HA))), 3)
gy, gx = np.gradient(HA, span); slopeA = np.degrees(np.arctan(np.hypot(gx, gy)))
fig, axs = plt.subplots(1, 3, figsize=(19, 5.4), gridspec_kw={"width_ratios": [2.0, 2.0, 1]})
im = axs[0].imshow(HA, cmap="terrain", origin="lower", extent=[0, nx * span, 0, ny * span])
axs[0].set_title("RMUC2026 7v7 地图（由 CAD 精确栅格化，%.1f x %.1f m）" % (nx * span, ny * span))
fig.colorbar(im, ax=axs[0], shrink=.85, label="height [m]")
im2 = axs[1].imshow(np.where((slopeA > 6) & (slopeA < 40), slopeA, np.nan), cmap="inferno",
                    origin="lower", extent=[0, nx * span, 0, ny * span], vmin=6, vmax=40)
axs[1].set_title("可行驶坡面（实测 6-40°）共 %.1f m²" % ((np.isfinite(np.where((slopeA > 6) & (slopeA < 40), slopeA, np.nan))).sum() * span * span))
fig.colorbar(im2, ax=axs[1], shrink=.85, label="incline [deg]")
bins = np.arange(0, 46, 2)
tw, aw = tilt[walk], ar[walk]
m = (tw > 3) & (tw < 45)
axs[2].hist(np.clip(tw[m], 0, 45), bins=bins, weights=aw[m] / 1e6, color="tab:blue")
axs[2].axvspan(dims["slope_deg"][0], dims["slope_deg"][1], color="tab:orange", alpha=.25,
               label="训练坡角 %.0f-%.0f°" % tuple(dims["slope_deg"]))
axs[2].set_title("坡面倾角面积分布"); axs[2].set_xlabel("incline [deg]"); axs[2].set_ylabel("area [m²]")
axs[2].legend(fontsize=9)
for a in (axs[0], axs[1]): a.set_xlabel("X [m]"); a.set_ylabel("Y [m]")
fig.tight_layout(); fig.savefig(os.path.join(DOCS, "fig_A_map_2026.png"), dpi=105); plt.close(fig)
print("wrote fig_A_map_2026.png")

# ------------------------------------------------------------------ B. the ramp patch
half, gs = 3.4, 0.04
cx, cy = 13.8, 2.0
inw = (np.abs(X.mean(1) - cx) < half) & (np.abs(Y.mean(1) - cy) < half) & (Z.mean(1) < 0.95)
n = int(2 * half / gs) + 1
P = raster(X[inw], Y[inw], Z[inw].mean(1), n, n, gs, off=(cx - half, cy - half))
P = median_filter(P, 3); P -= P.min()
hmax = float(P.max())
gy2, gx2 = np.gradient(P, gs); slope = np.degrees(np.arctan(np.hypot(gx2, gy2)))
band = (slope > 6) & (slope < 40)
print("patch: rise %.2f m, ramp area %.1f m2, median incline %.1f deg"
      % (hmax, band.sum() * gs * gs, np.median(slope[band]) if band.any() else 0))
fig, axs = plt.subplots(1, 3, figsize=(16.5, 4.9))
axs[0].imshow(P, cmap="terrain", origin="lower", extent=[-half, half, -half, half])
axs[0].set_title("CAD 截取的场地块 %.1f×%.1f m\n落差 %.0f cm（只保留可行驶面）" % (2 * half, 2 * half, hmax * 100))
im3 = axs[1].imshow(slope, cmap="inferno", origin="lower", extent=[-half, half, -half, half], vmin=0, vmax=32)
axs[1].set_title("实测坡度：中位 %.0f°（训练用 %.0f-%.0f°）"
                 % (np.median(slope[band]) if band.any() else 0, *dims["slope_deg"]))
fig.colorbar(im3, ax=axs[1], shrink=.85, label="deg")
axs[2].imshow(P, cmap="terrain", origin="lower", extent=[-half, half, -half, half])
axs[2].contour(P, levels=14, colors="k", linewidths=.6, alpha=.55); axs[2].set_title("等高线")
for a in axs: a.set_xlabel("X [m]"); a.set_ylabel("Y [m]")
fig.tight_layout(); fig.savefig(os.path.join(DOCS, "fig_B1_field_patch.png"), dpi=105); plt.close(fig)
print("wrote fig_B1_field_patch.png")

# ------------------------------------------------------------------ B2. robot on it
Pn = np.clip((P - P.min()) / max(1e-9, P.max() - P.min()), 1e-3, 1.0)
with open(os.path.join(RC, "meshes", "patch.hf"), "wb") as fh:
    fh.write(struct.pack("<ii", n, n)); fh.write(np.ascontiguousarray(Pn, dtype="<f4").tobytes()); fh.flush()
open(os.path.join(RC, "field_scene.xml"), "w", encoding="utf-8", newline="\n").write(
  """<mujoco model="rm_vehicle_cc on RMUC2026 field patch">
  <include file="rm_vehicle_cc.xml"/>
  <visual><global offwidth="1024" offheight="768"/></visual>
  <asset>
    <hfield name="field" size="%.4f %.4f %.4f 0.0001" nrow="%d" ncol="%d" file="patch.hf"/>
    <texture type="skybox" builtin="gradient" rgb1="0.55 0.6 0.68" rgb2="0.25 0.28 0.33" width="256" height="256"/>
  </asset>
  <worldbody>
    <geom name="field" type="hfield" hfield="field" pos="0 0 0" contype="1" conaffinity="1"
          friction="1.6 0.02 0.002" rgba="0.60 0.64 0.70 1"/>
    <light pos="1 -2 3" dir="0 0.4 -1" diffuse="1 1 1" specular="0.2 0.2 0.2"/>
  </worldbody>
</mujoco>
""" % (half, half, hmax, n, n))
import mujoco
m = mujoco.MjModel.from_xml_path(os.path.join(RC, "field_scene.xml")); d = mujoco.MjData(m)
def J(nm): return mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, nm)
LN = ("left_front1_joint", "left_rear1_joint", "right_front1_joint", "right_rear1_joint")
WN = ("left_wheel_joint", "right_wheel_joint")
qa = {n_: m.jnt_qposadr[J(n_)] for n_ in LN + WN}
va = {n_: m.jnt_dofadr[J(n_)] for n_ in LN + WN}
def surf(x, y):
    i = int(np.clip((y - (cy - half)) / gs, 0, n - 1)); j = int(np.clip((x - (cx - half)) / gs, 0, n - 1))
    return float(P[i, j])
def hold(vw):
    for nm in LN:
        d.qfrc_applied[va[nm]] = float(np.clip(60.0 * (0.0 - d.qpos[qa[nm]]) - 2.0 * d.qvel[va[nm]], -30, 30))
    for nm in WN:
        d.qfrc_applied[va[nm]] = float(np.clip(1.5 * (vw - d.qvel[va[nm]]), -10, 10))
start = (-2.6, 0.0)
d.qpos[0], d.qpos[1], d.qpos[2] = start[0], start[1], surf(*start) + 0.075 + 0.02
d.qpos[3] = 1.0
for _ in range(400):
    hold(0.0); mujoco.mj_step(m, d)
rend = mujoco.Renderer(m, 470, 640); vopt = mujoco.MjvOption(); vopt.geomgroup[:] = (1, 1, 1, 1, 0, 1)
cam = mujoco.MjvCamera(); cam.type = mujoco.mjtCamera.mjCAMERA_FREE
def shot(az, el, dist, lbl):
    cam.lookat = [d.qpos[0], 0.0, d.qpos[2] + 0.15]; cam.distance = dist
    cam.azimuth = az; cam.elevation = el
    rend.update_scene(d, camera=cam, scene_option=vopt)
    return lbl, rend.render()
shots = [shot(0, -10, 2.6, "start on the flat")]
for k in range(2600):
    hold(1.2 / 0.073)
    mujoco.mj_step(m, d)
    if k in (900, 1800, 2599):
        shots.append(shot(0, -10, 2.6, "drive %0.1f m, ground %0.2f m" % (d.qpos[0] - start[0], surf(d.qpos[0], d.qpos[1]))))
        shots.append(shot(38, -24, 2.9, "3/4 view"))
from PIL import Image, ImageDraw
tiles = [Image.fromarray(a) for _, a in shots]
W = 640; H = 470; cols = 3
sheet = Image.new("RGB", (cols * (W + 8) + 8, ((len(tiles) + cols - 1) // cols) * (H + 26) + 8), "white")
for i, ((lbl, _), t) in enumerate(zip(shots, tiles)):
    r, c = divmod(i, cols)
    sheet.paste(t.resize((W, H)), (8 + c * (W + 8), 26 + r * (H + 26)))
    ImageDraw.Draw(sheet).text((10 + c * (W + 8), 10 + r * (H + 26)), "closed-chain robot on CAD 7v7 terrain - " + lbl, fill=(0, 0, 0))
fn = os.path.join(DOCS, "fig_B2_robot_on_map.png"); sheet.save(fn)
print("wrote", fn, sheet.size, "| final base (%.2f, %.2f, %.3f)" % (d.qpos[0], d.qpos[1], d.qpos[2]))
