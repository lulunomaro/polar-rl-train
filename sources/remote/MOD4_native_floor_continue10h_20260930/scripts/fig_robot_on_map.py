"""Final figure set: B1 CAD ramp patch (surface only), B2 our closed-chain robot standing
on that CAD-derived terrain, C the measured skill ladders, D the training curves."""
import glob, json, os
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
matplotlib.rcParams["font.sans-serif"] = ["Microsoft YaHei", "DejaVu Sans"]
matplotlib.rcParams["axes.unicode_minus"] = False
from scipy.ndimage import gaussian_filter, distance_transform_edt

MAP = r"D:/claude2/fangzhen/cad/out_map"; DOCS = r"D:/claude2/fangzhen/docs/crops"
dims = json.load(open(os.path.join(MAP, "field_dims.json"), encoding="utf-8"))
# measured drivable ramps: median 12.1 deg, per-cluster p10-p90 11.5-17.1 deg; faces above
# ~35 deg are structure bevels a wheeled robot cannot climb, so the training band is
# [measured low edge .. 25 deg] -> deliberately harder than the field.
dims["slope_deg"] = [9.4, 25.0]
dims["slope_measured_median_deg"] = 12.1
json.dump(dims, open(os.path.join(MAP, "field_dims.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)

V = np.load(os.path.join(MAP, "map_verts.npy")); F = np.load(os.path.join(MAP, "map_faces.npy")).astype(np.int64)
tri = V[F]
nrm = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]); ar = 0.5 * np.linalg.norm(nrm, axis=1)
k = ar > 1e-6; tri, nrm, ar = tri[k], nrm[k], ar[k]
up = 2; A, B = 0, 1; o = V.min(0)
Zc = (tri[:, :, up].mean(1) - o[up]) / 1000.0
XA = (tri[:, :, A].mean(1) - o[A]) / 1000.0; XB = (tri[:, :, B].mean(1) - o[B]) / 1000.0
u = np.array([0., 0., 1.])
tilt = np.degrees(np.arccos(np.clip(np.abs((nrm / (2 * ar)[:, None])) @ u, 0, 1)))

# ---------------------------------------------------------------- B1/B2: the ramp patch
cx, cy, half, gs = 13.8, 2.0, 3.4, 0.05
npix = int(2 * half / gs) + 1
inw = (np.abs(XA - cx) < half) & (np.abs(XB - cy) < half) & (Zc < 0.95)   # drop the towers
P = np.full((npix, npix), -np.inf)
ja = np.clip(((XA[inw] - (cx - half)) / gs).astype(int), 0, npix - 1)
jb = np.clip(((XB[inw] - (cy - half)) / gs).astype(int), 0, npix - 1)
np.maximum.at(P, (jb, ja), Zc[inw])
P[~np.isfinite(P)] = np.nan
idx = distance_transform_edt(~np.isfinite(P), return_distances=False, return_indices=True)
P = np.clip(P[tuple(idx)], 0, None); P = gaussian_filter(P, 0.7); P -= P.min()
hmax = float(P.max()); gy, gx = np.gradient(P, gs); slope = np.degrees(np.arctan(np.hypot(gx, gy)))
band = (slope > 6) & (slope < 40)
print("patch rise %.2f m, ramp area %.1f m2, incline median %.1f deg" % (hmax, band.sum() * gs * gs, np.median(slope[band])))
np.savetxt(os.path.join(MAP, "patch_height.txt"), P.ravel(), fmt="%.5f")
json.dump(dict(npix=npix, gs=gs, half=half, hmax=hmax), open(os.path.join(MAP, "patch_meta.json"), "w"))

# --- MuJoCo scene: the robot on this exact CAD surface (hfield written from the mesh)
import struct, mujoco
Pn = (P - P.min()) / max(1e-9, P.max() - P.min())          # MuJoCo hfield data is in [0,1]
Pn = np.clip(Pn, 1e-3, 1.0)
with open(os.path.join(r"D:/claude2/fangzhen/robot/out_cc/meshes", "patch.hf"), "wb") as fh:
    fh.write(struct.pack("<ii", npix, npix))                 # header: nrow, ncol (int32)
    fh.write(np.ascontiguousarray(Pn, dtype="<f4").tobytes())
    fh.flush()
scene = os.path.join(r"D:/claude2/fangzhen/robot/out_cc", "field_scene.xml")
open(scene, "w", encoding="utf-8", newline="\n").write(
  """<mujoco model="rm_vehicle_cc on RMUC2026 field patch">
  <include file="rm_vehicle_cc.xml"/>
  <asset>
    <hfield name="field" size="%.4f %.4f %.4f 0.0001" nrow="%d" ncol="%d" file="patch.hf"/>
    <texture type="skybox" builtin="gradient" rgb1="0.55 0.6 0.68" rgb2="0.25 0.28 0.33" width="256" height="256"/>
  </asset>
  <visual><global offwidth="1024" offheight="768"/></visual>
  <worldbody>
    <geom name="field" type="hfield" hfield="field" pos="0 0 0" contype="1" conaffinity="1"
          friction="1.6 0.02 0.002" rgba="0.62 0.66 0.72 1"/>
    <light pos="1 -2 3" dir="0 0.4 -1" diffuse="1 1 1" specular="0.2 0.2 0.2"/>
    <camera name="side" pos="0 -3.4 0.7" xyaxes="1 0 0 0 0 1"/>
  </worldbody>
</mujoco>
""" % (half, half, hmax, npix, npix))
m = mujoco.MjModel.from_xml_path(scene)
d = mujoco.MjData(m)
def J(n): return mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, n)
qa = {n: m.jnt_qposadr[J(n)] for n in ("left_front1_joint", "left_rear1_joint", "right_front1_joint",
                                        "right_rear1_joint", "left_wheel_joint", "right_wheel_joint")}
# start on the flat part of the patch (x = -2.4 m), lifted clear of the surface
d.qpos[0], d.qpos[1], d.qpos[2] = -2.3, 0.0, 0.62
d.qpos[3] = 1.0
mujoco.mj_forward(m, d)
def surf(x, y):
    i = int(np.clip((y + half) / gs, 0, npix - 1)); j = int(np.clip((x + half) / gs, 0, npix - 1))
    return float(P[i, j])
d.qpos[2] = max(d.qpos[2], surf(-2.3, 0.0) + 0.095)
for _ in range(600):
    for n in list(qa)[:4]:
        d.qfrc_applied[m.jnt_dofadr[J(n)]] = np.clip(60.0 * (0.0 - d.qpos[qa[n]]) - 2.0 * d.qvel[m.jnt_dofadr[J(n)]], -30, 30)
    for n in list(qa)[4:]:
        d.qfrc_applied[m.jnt_dofadr[J(n)]] = np.clip(1.5 * (0.0 - d.qvel[m.jnt_dofadr[J(n)]]), -10, 10)
    mujoco.mj_step(m, d)
bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "base_link")
pitch = np.degrees(np.arcsin(np.clip(d.xmat[bid].reshape(3, 3)[2, 0], -1, 1)))
print("settled: base (%.2f, %.2f, %.3f) pitch %.1f deg contacts %d"
      % (d.qpos[0], d.qpos[1], d.qpos[2], pitch, len(d.contact)))

rend = mujoco.Renderer(m, 460, 700)
cam = mujoco.MjvCamera(); cam.type = mujoco.mjtCamera.mjCAMERA_FREE
vopt = mujoco.MjvOption(); vopt.geomgroup[:] = (1, 1, 1, 1, 0, 1)
shots = []
for az, el, dist, lz, lbl in ((0, -12, 3.2, 0.25, "side"), (35, -22, 3.0, 0.35, "3/4")):
    cam.lookat = [d.qpos[0], 0.0, lz]; cam.distance = dist; cam.azimuth = az; cam.elevation = el
    rend.update_scene(d, camera=cam, scene_option=vopt)
    im = rend.render(); shots.append((lbl, im))
# drive toward the ramp under the same low-level PD, capture the climb
for k in range(1400):
    for n in list(qa)[:4]:
        d.qfrc_applied[m.jnt_dofadr[J(n)]] = np.clip(60.0 * (0.0 - d.qpos[qa[n]]) - 2.0 * d.qvel[m.jnt_dofadr[J(n)]], -30, 30)
    for n in list(qa)[4:]:
        v = 1.0 / 0.073
        d.qfrc_applied[m.jnt_dofadr[J(n)]] = np.clip(1.5 * (v - d.qvel[m.jnt_dofadr[J(n)]]), -10, 10)
    mujoco.mj_step(m, d)
    if k in (700, 1399):
        cam.lookat = [d.qpos[0], 0.0, 0.35]; cam.distance = 3.0; cam.azimuth = 0; cam.elevation = -12
        rend.update_scene(d, camera=cam, scene_option=vopt)
        shots.append(("climb%d" % k, rend.render()))
print("after climb: base (%.2f, %.2f, %.3f)  ground under it %.2f m" % (d.qpos[0], d.qpos[1], d.qpos[2], surf(d.qpos[0], d.qpos[1])))
from PIL import Image, ImageDraw
tiles = [Image.fromarray(im) for _, im in shots]
W = sum(t.width for t in tiles) + 10 * len(tiles); H = max(t.height for t in tiles)
sheet = Image.new("RGB", (W, H + 26), "white"); x = 0
for (lbl, _), t in zip(shots, tiles):
    sheet.paste(t, (x, 26)); ImageDraw.Draw(sheet).text((x + 6, 8), "closed-chain robot on CAD 7v7 terrain: " + lbl, fill=(0, 0, 0)); x += t.width + 10
fn = os.path.join(DOCS, "fig_B2_robot_on_map.png"); sheet.save(fn); print("wrote", fn)

fig, axs = plt.subplots(1, 3, figsize=(16, 4.9))
axs[0].imshow(P, cmap="terrain", origin="lower", extent=[-half, half, -half, half])
axs[0].set_title("CAD 截取的 7v7 场地块 %.1f×%.1f m\n落差 %.0f cm（去掉高塔，只留可行驶面）" % (2*half, 2*half, hmax*100))
im = axs[1].imshow(slope, cmap="inferno", origin="lower", extent=[-half, half, -half, half], vmin=0, vmax=30)
axs[1].set_title("实测坡度：中位 %.0f°，训练用 %.0f-%.0f°" % (np.median(slope[band]), dims["slope_deg"][0], dims["slope_deg"][1]))
fig.colorbar(im, ax=axs[1], shrink=.85, label="deg")
axs[2].imshow(P, cmap="terrain", origin="lower", extent=[-half, half, -half, half])
axs[2].contour(P, levels=14, colors="k", linewidths=.6, alpha=.55); axs[2].set_title("等高线")
for ax in axs: ax.set_xlabel("X [m]"); ax.set_ylabel("Y [m]")
fig.tight_layout(); fig.savefig(os.path.join(DOCS, "fig_B1_field_patch.png"), dpi=105); plt.close(fig)
print("wrote fig_B1_field_patch.png")
