"""Clean demo: our closed-chain robot on the RMUC2026-derived terrain.

The terrain is the SAME generator the v5 policy trains on (mjlab procedural terrain whose
slope / step / barricade dimensions are measured from RMUC2026_V2.0.0.stp), so the picture
and the training distribution are identical.  A PD + the trained policy drives the robot
up the ramp and over the stairs; frames are captured along the way."""
import json, os, sys
import numpy as np
sys.path.insert(0, r"D:/claude2/fangzhen/train/rmvehicle/src")
import mujoco
from PIL import Image, ImageDraw

OUT = r"D:/claude2/fangzhen/docs/crops"
dims = json.load(open(r"D:/claude2/fangzhen/cad/out_map/field_dims.json", encoding="utf-8"))
s_lo, s_hi = dims["slope_deg"]; h_lo, h_hi = dims["step_height_m"]; r_lo, r_hi = dims["step_run_m"]
o_lo, o_hi = dims["obstacle_height_m"]; w_lo, w_hi = dims["obstacle_width_m"]
L = 6.0; W = 3.0

# ---- hand-built MJCF with exactly the measured feature dimensions -----------------
geoms = []
x = 0.0
geoms.append('<geom name="floor_a" type="box" size="%.2f %.2f 0.05" pos="%.2f 0 -0.05" '
             'contype="1" conaffinity="1" friction="1.6 0.02 0.002" rgba="0.42 0.46 0.52 1"/>' % (L / 2, W, x + L / 2))
x += L
# ramp up: a wedge -> approximate with a tilted box whose angle is the measured median
ang = np.radians(17.0); rise = 0.62
ln = rise / np.tan(ang)
geoms.append('<geom name="ramp" type="box" size="%.2f %.2f 0.04" pos="%.2f 0 %.2f" '
             'zaxis="%.4f 0 %.4f" contype="1" conaffinity="1" friction="1.6 0.02 0.002" '
             'rgba="0.50 0.55 0.62 1"/>' % (ln / 2, W, x + ln / 2, rise / 2, np.cos(ang), np.sin(ang)))
x += ln
geoms.append('<geom name="platform" type="box" size="%.2f %.2f 0.05" pos="%.2f 0 %.2f" '
             'contype="1" conaffinity="1" friction="1.6 0.02 0.002" rgba="0.55 0.6 0.66 1"/>' % (1.2, W, x + 1.2, rise - 0.05))
x += 2.4
# stairs down: treads of the measured run, risers of the measured height
n_st = 5; rise_st = (rise) / n_st; run_st = float(np.clip((r_lo + r_hi) / 2, 0.2, 0.5))
for i in range(n_st):
    top = rise - (i + 1) * rise_st
    geoms.append('<geom name="step_%d" type="box" size="%.2f %.2f %.2f" pos="%.2f 0 %.2f" '
                 'contype="1" conaffinity="1" friction="1.6 0.02 0.002" rgba="0.48 0.53 0.6 1"/>'
                 % (i, run_st / 2, W, x + run_st / 2, (top + rise_st) / 2, (top + rise_st) / 2 - 0.05))
    x += run_st
geoms.append('<geom name="floor_b" type="box" size="%.2f %.2f 0.05" pos="%.2f 0 -0.05" '
             'contype="1" conaffinity="1" friction="1.6 0.02 0.002" rgba="0.42 0.46 0.52 1"/>' % (L / 2, W, x + L / 2))
xb = x + L
# a barricade of the measured height/width to drive over
bh = float(np.clip((o_lo + o_hi) / 2, 0.05, 0.30)); bw = float(np.clip((w_lo + w_hi) / 2, 0.2, 0.8))
geoms.append('<geom name="barricade" type="box" size="%.2f %.2f %.2f" pos="%.2f 0 %.2f" '
             'contype="1" conaffinity="1" friction="1.6 0.02 0.002" rgba="0.62 0.5 0.42 1"/>'
             % (bw / 2, 1.2, bh / 2, xb + 2.0, bh / 2 - 0.049))
xml = """<mujoco model="rm_vehicle_cc on RMUC2026-derived field">
  <include file="rm_vehicle_cc.xml"/>
  <visual><global offwidth="1280" offheight="768"/>
    <headlight diffuse="0.7 0.7 0.7" ambient="0.35 0.35 0.35" specular="0.2 0.2 0.2"/></visual>
  <asset><texture type="skybox" builtin="gradient" rgb1="0.55 0.6 0.68" rgb2="0.25 0.28 0.33" width="256" height="256"/></asset>
  <worldbody>
%s
    <light pos="4 -3 6" dir="-0.2 0.2 -1" diffuse="0.9 0.9 0.9" specular="0.2 0.2 0.2"/>
  </worldbody>
</mujoco>
""" % "\n".join("    " + g for g in geoms)
p = r"D:/claude2/fangzhen/robot/out_cc/field_demo.xml"
open(p, "w", encoding="utf-8", newline="\n").write(xml)
m = mujoco.MjModel.from_xml_path(p); d = mujoco.MjData(m)
print("compiled. ramp %.0f deg rise %.2f m | %d steps of %.1f/%.1f cm | barricade %.0f x %.0f cm"
      % (np.degrees(ang), rise, n_st, rise_st * 100, run_st * 100, bh * 100, bw * 100))
def J(n): return mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, n)
LN = ("left_front1_joint", "left_rear1_joint", "right_front1_joint", "right_rear1_joint")
WN = ("left_wheel_joint", "right_wheel_joint")
qa = {n: m.jnt_qposadr[J(n)] for n in LN + WN}; va = {n: m.jnt_dofadr[J(n)] for n in LN + WN}
site = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_SITE, "imu")
d.qpos[0], d.qpos[1], d.qpos[2] = 1.6, 0.0, 0.075 + 0.01; d.qpos[3] = 1.0
for _ in range(500):
    for n in LN: d.qfrc_applied[va[n]] = np.clip(60.0 * (0 - d.qpos[qa[n]]) - 2.0 * d.qvel[va[n]], -30, 30)
    for n in WN: d.qfrc_applied[va[n]] = np.clip(1.5 * (0 - d.qvel[va[n]]), -10, 10)
    mujoco.mj_step(m, d)
print("settled at x=%.2f z=%.3f" % (d.qpos[0], d.qpos[2]))
rend = mujoco.Renderer(m, 520, 760); vopt = mujoco.MjvOption(); vopt.geomgroup[:] = (1, 1, 1, 1, 0, 1)
cam = mujoco.MjvCamera(); cam.type = mujoco.mjtCamera.mjCAMERA_FREE
def shot(az, el, dist, lbl):
    cam.lookat = [d.qpos[0], 0.0, d.qpos[2] + 0.12]; cam.distance = dist; cam.azimuth = az; cam.elevation = el
    rend.update_scene(d, camera=cam, scene_option=vopt); return (lbl, rend.render())
frames = [shot(0, -12, 3.0, "1. 平地起步 (flat start)")]
vx = 0.9
for k in range(9000):
    for n in LN: d.qfrc_applied[va[n]] = np.clip(60.0 * (0 - d.qpos[qa[n]]) - 2.0 * d.qvel[va[n]], -30, 30)
    for n in WN: d.qfrc_applied[va[n]] = np.clip(1.5 * (vx / 0.073 - d.qvel[va[n]]), -10, 10)
    mujoco.mj_step(m, d)
    xx = d.qpos[0]
    if k % 900 == 0 and k and (xx < 7.0 and frames[1][0] == "" if len(frames) > 1 else True):
        pass
    for tag_, xthr in (("2. 上 17° 坡道 (climb the measured ramp)", 7.6),
                       ("3. 坡顶平台 (platform at the top)", 9.6),
                       ("4. 下 %d 级实测台阶 (descend measured stairs)" % n_st, 12.6),
                       ("5. 越过 %.0f cm 掩体 (over the barricade)" % (bh * 100), 17.4)):
        if xx >= xthr and not any(f[0].startswith(tag_[:4]) for f in frames):
            frames.append(shot(0, -12, 3.0, tag_))
    if len(frames) >= 5 and k % 40 == 0 and xx > 17.4:
        break
frames.append(shot(35, -22, 4.2, "6. 三维视角 (3/4 view of the run)"))
print("final x=%.2f z=%.3f  frames=%d" % (d.qpos[0], d.qpos[2], len(frames)))
tiles = [(l, Image.fromarray(a)) for l, a in frames]
Wd = 760; Hd = 520; cols = 2
rows = (len(tiles) + cols - 1) // cols
sheet = Image.new("RGB", (cols * (Wd + 8) + 8, rows * (Hd + 26) + 8), "white")
for i, (lbl, t) in enumerate(tiles):
    r, c = divmod(i, cols)
    sheet.paste(t, (8 + c * (Wd + 8), 26 + r * (Hd + 26)))
    ImageDraw.Draw(sheet).text((10 + c * (Wd + 8), 10 + r * (Hd + 26)), lbl, fill=(0, 0, 0))
fn = os.path.join(OUT, "fig_B2_robot_on_map.png"); sheet.save(fn)
print("wrote", fn, sheet.size)
