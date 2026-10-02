"""Ground-truth jump check: plain MuJoCo, the exported policy, and wheel-floor contacts
counted straight out of data.contact (no mjlab sensor involved)."""
import math, os
import numpy as np, mujoco, onnxruntime as ort
m = mujoco.MjModel.from_xml_path(r"D:/claude2/fangzhen/robot/out_cc/scene_cc.xml")
d = mujoco.MjData(m); m.opt.timestep = 0.001
def J(n): return mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, n)
def B(n): return mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, n)
LEG = ["left_front1_joint", "left_rear1_joint", "right_front1_joint", "right_rear1_joint"]
WHL = ["left_wheel_joint", "right_wheel_joint"]
qa = {n: m.jnt_qposadr[J(n)] for n in LEG + WHL}; va = {n: m.jnt_dofadr[J(n)] for n in LEG + WHL}
wb = {B("left_wheel"), B("right_wheel")}
site = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_SITE, "imu")
onx = r"D:/claude2/fangzhen/train/deploy/rm_cc_v6_3600.onnx"
s = ort.InferenceSession(onx, providers=["CPUExecutionProvider"]); iname = s.get_inputs()[0].name
print("policy", os.path.basename(onx))
R = 0.073; DEC = 20
d.qpos[:] = 0.0; d.qpos[2] = R + 0.002; d.qpos[3] = 1.0
mujoco.mj_forward(m, d)
last = np.zeros(6, np.float32); tgt = {}; jump = 0.0; height = 0.22
z0 = None; peak = -9e9; air_steps = 0; max_vz = 0.0; ncon_hist = []
def wheels_down():
    for c in d.contact:
        if m.geom_bodyid[c.geom1] in wb or m.geom_bodyid[c.geom2] in wb:
            return True
    return False
for k in range(6000):
    t = k * 0.001
    if k % DEC == 0:
        g = d.xmat[site].reshape(3, 3).T @ np.array([0.0, 0.0, -1.0])
        o = np.zeros(35, np.float32)
        o[0:3] = [0.0, 0.0, 0.0]; o[3] = height * 5.0
        o[4:7] = d.qvel[3:6] * 0.5; o[7:10] = g
        o[10:14] = [d.qpos[qa[n]] for n in LEG]
        o[16:20] = [d.qvel[va[n]] * 0.1 for n in LEG]
        o[20:22] = [d.qvel[va[n]] * 0.1 for n in WHL]
        o[22:28] = last; o[28] = 1.0; o[32] = jump
        a = s.run(None, {iname: o.reshape(1, 35)})[0][0].astype(np.float32); last = a
        tgt = {n: a[i] * 0.5 for i, n in enumerate(LEG)}
        tgt.update({n: a[4 + i] * 10.0 for i, n in enumerate(WHL)})
    if 3.0 <= t < 4.6:
        jump = 1.0
        if t < 3.02:
            z0 = float(d.qpos[2]); peak = z0; air_steps = 0; max_vz = 0.0
    else:
        jump = 0.0
    d.qfrc_applied[:] = 0.0
    for n in LEG:
        d.qfrc_applied[va[n]] = np.clip(60.0 * (tgt.get(n, 0.0) - d.qpos[qa[n]]) - 2.0 * d.qvel[va[n]], -50.9, 50.9)
    for n in WHL:
        d.qfrc_applied[va[n]] = np.clip(1.5 * (tgt.get(n, 0.0) - d.qvel[va[n]]), -10, 10)
    mujoco.mj_step(m, d)
    if z0 is not None and 3.0 <= t < 6.1:
        peak = max(peak, float(d.qpos[2])); max_vz = max(max_vz, float(d.qvel[2]))
        if not wheels_down(): air_steps += 1
        ncon_hist.append(len(d.contact))
print("jump window 3.0-4.6 s (flag on), measure to 6.1 s")
print("  base z at flag-on : %.4f m" % z0)
print("  peak rise         : %.1f cm" % ((peak - z0) * 100))
print("  peak vertical vel : %.2f m/s" % max_vz)
print("  airborne time     : %.3f s  (%d of %d steps with NO wheel contact)"
      % (air_steps * 0.001, air_steps, len(ncon_hist)))
print("  contacts while measuring: min %d max %d mean %.1f" % (min(ncon_hist), max(ncon_hist), np.mean(ncon_hist)))
