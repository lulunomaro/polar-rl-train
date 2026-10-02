"""Drive the RMUC2026-derived field features with the TRAINED policy (v5), deployment
control law, plain MuJoCo.  Captures a frame at each map feature."""
import math, os
import numpy as np, mujoco, onnxruntime as ort
from PIL import Image, ImageDraw

XML = os.environ.get("FIELD_XML", r"D:/claude2/fangzhen/sim2sim_cc/rm_vehicle_cc/mjcf/scene_field.xml")
ONNX = os.environ.get("FIELD_ONNX", r"D:/claude2/fangzhen/train/deploy/rm_cc_v6_field.onnx")
OUT = r"D:/claude2/fangzhen/docs/crops"
LEG = ["left_front1_joint", "left_rear1_joint", "right_front1_joint", "right_rear1_joint"]
WHL = ["left_wheel_joint", "right_wheel_joint"]
R = 0.073; DT = 0.001; DEC = 20
m = mujoco.MjModel.from_xml_path(XML); d = mujoco.MjData(m); m.opt.timestep = DT
def J(n): return mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, n)
qa = {n: m.jnt_qposadr[J(n)] for n in LEG + WHL}; va = {n: m.jnt_dofadr[J(n)] for n in LEG + WHL}
site = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_SITE, "imu")
sess = ort.InferenceSession(ONNX, providers=["CPUExecutionProvider"]); iname = sess.get_inputs()[0].name
print("scene:", XML)
print("policy:", os.path.basename(ONNX), sess.get_inputs()[0].shape, "->", sess.get_outputs()[0].shape)
d.qpos[:] = 0.0; d.qpos[0], d.qpos[1], d.qpos[2], d.qpos[3] = 1.6, 0.0, 0.085, 1.0
mujoco.mj_forward(m, d)
last = np.zeros(6, np.float32); tgt = {}; height = 0.24; cmd = np.zeros(3, np.float32)
rend = mujoco.Renderer(m, 500, 780); vopt = mujoco.MjvOption(); vopt.geomgroup[:] = (1, 1, 1, 1, 0, 1)
cam = mujoco.MjvCamera(); cam.type = mujoco.mjtCamera.mjCAMERA_FREE
def shot(az, el, dist, lbl):
    cam.lookat = [d.qpos[0], 0.0, d.qpos[2] + 0.12]; cam.distance = dist; cam.azimuth = az; cam.elevation = el
    rend.update_scene(d, camera=cam, scene_option=vopt); return (lbl, rend.render())
frames = []; hist = []; marks = [("1. 平地 (flat arena)", 3.0), ("2. 17° 坡道 (measured ramp)", 7.4),
                                 ("3. 坡顶平台 (top platform)", 9.8), ("4. 下实测台阶 (stairs)", 12.4),
                                 ("5. 冲过掩体 (barricade)", 17.0)]
done = set()
for k in range(30000):
    t = k * DT
    if k % DEC == 0:
        g = d.xmat[site].reshape(3, 3).T @ np.array([0.0, 0.0, -1.0])
        o = np.zeros(35, np.float32)
        o[0:3] = [cmd[0], 0.0, cmd[2]]; o[3] = height * 5.0
        o[4:7] = d.qvel[3:6] * 0.5; o[7:10] = g
        o[10:14] = [d.qpos[qa[n]] for n in LEG]; o[14:16] = 0.0
        o[16:20] = [d.qvel[va[n]] * 0.1 for n in LEG]; o[20:22] = [d.qvel[va[n]] * 0.1 for n in WHL]
        o[22:28] = last; o[28] = 1.0
        a = sess.run(None, {iname: o.reshape(1, 35)})[0][0].astype(np.float32); last = a
        tgt = {n: a[i] * 0.5 for i, n in enumerate(LEG)}
        tgt.update({n: a[4 + i] * 10.0 for i, n in enumerate(WHL)})
    cmd[0] = 0.0 if t < 1.5 else (0.55 if t < 5 else (0.85 if t < 12 else (0.6 if t < 20 else 0.9)))
    cmd[2] = 0.0
    d.qfrc_applied[:] = 0.0
    for n in LEG:
        d.qfrc_applied[va[n]] = np.clip(60.0 * (tgt.get(n, 0.0) - d.qpos[qa[n]]) - 2.0 * d.qvel[va[n]], -30, 30)
    for n in WHL:
        d.qfrc_applied[va[n]] = np.clip(1.5 * (tgt.get(n, 0.0) - d.qvel[va[n]]), -10, 10)
    mujoco.mj_step(m, d)
    g = d.xmat[site].reshape(3, 3).T @ np.array([0.0, 0.0, -1.0])
    pitch = math.degrees(math.asin(np.clip(g[0], -1, 1)))
    if k % 100 == 0: hist.append([t, d.qpos[0], d.qpos[2], pitch, d.qvel[0]])
    for lbl, xt in marks:
        if d.qpos[0] >= xt and lbl not in done:
            done.add(lbl); frames.append(shot(0, -13, 3.2, "%s  x=%.1f m  z=%.2f m  pitch=%.1f deg" % (lbl, d.qpos[0], d.qpos[2], pitch)))
    if d.qpos[2] < -0.5 or abs(pitch) > 45:
        frames.append(shot(0, -13, 3.2, "FELL at x=%.1f m t=%.1f s" % (d.qpos[0], t))); break
H = np.array(hist)
print("frames %d | final x=%.2f m  z=%.3f m  max|pitch|=%.1f deg  distance=%.2f m"
      % (len(frames), d.qpos[0], d.qpos[2], np.abs(H[:, 3]).max(), H[:, 1].max() - H[:, 1].min()))
tiles = [(l, Image.fromarray(a)) for l, a in frames]
Wd, Hd, cols = 780, 500, 2
rows = (len(tiles) + cols - 1) // cols
sheet = Image.new("RGB", (cols * (Wd + 8) + 8, rows * (Hd + 26) + 8), "white")
for i, (lbl, t) in enumerate(tiles):
    r, c = divmod(i, cols)
    sheet.paste(t, (8 + c * (Wd + 8), 26 + r * (Hd + 26)))
    ImageDraw.Draw(sheet).text((10 + c * (Wd + 8), 10 + r * (Hd + 26)), lbl, fill=(0, 0, 0))
fn = os.path.join(OUT, "fig_B2_robot_on_map.png"); sheet.save(fn); print("wrote", fn, sheet.size)
np.save(os.path.join(OUT, "field_run_hist.npy"), H)
