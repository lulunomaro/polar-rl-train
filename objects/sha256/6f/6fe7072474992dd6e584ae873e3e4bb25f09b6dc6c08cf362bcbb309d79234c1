# -*- coding: utf-8 -*-
"""Render skill demo videos of an exported policy.

Same deployment control law as scripts/verify_skills_mujoco.py (leg PD 60/2 clipped by the
plant's torque limit, wheel velocity PD, 50 Hz policy on 1 kHz physics, qfrc injection),
but it renders and writes an mp4 with per-phase captions.

  python scripts/skills_video.py --onnx train/deploy/rm_cc_v10_final.onnx \
    --model robot/out_cc_legacy54/scene_cc.xml --leg-eff 50.9 --wheel-eff 10 \
    --phases run,gyro,jump --out docs/videos/v10_skills_legacy.mp4

  --model robot/out_cc/scene_cc.xml --leg-eff 40 --wheel-eff 5.5    honest DM8009 plant
  --model sim2sim_cc/rm_vehicle_cc/mjcf/scene_field.xml --phases field   2026 map
"""
import argparse
import math
import os

import mujoco
import numpy as np
import onnxruntime as ort

ap = argparse.ArgumentParser()
ap.add_argument("--onnx", required=True)
ap.add_argument("--model", default=r"D:/claude2/fangzhen/robot/out_cc_legacy54/scene_cc.xml")
ap.add_argument("--out", default=r"D:/claude2/fangzhen/docs/videos/skills.mp4")
ap.add_argument("--phases", default="run,gyro,jump")
ap.add_argument("--leg-eff", type=float, default=50.9)
ap.add_argument("--wheel-eff", type=float, default=10.0)
ap.add_argument("--obs-order", default="contract", choices=["contract", "model"])
ap.add_argument("--height", type=float, default=0.22)
ap.add_argument("--seconds", type=float, default=6.0)
ap.add_argument("--fps", type=int, default=30)
ap.add_argument("--width", type=int, default=960)
ap.add_argument("--height-px", type=int, default=540)
a = ap.parse_args()

LEG = ["left_front1_joint", "left_rear1_joint", "right_front1_joint", "right_rear1_joint"]
WHL = ["left_wheel_joint", "right_wheel_joint"]
OBS_LEG = (["left_rear1_joint", "left_front1_joint", "right_rear1_joint", "right_front1_joint"]
           if a.obs_order == "model" else LEG)
R = 0.073  # wheel radius [m]
DT = 0.001
DEC = 20
KP, KD, WKD = 60.0, 2.0, 1.5
SCALE_LEG, SCALE_WHL = 0.5, 10.0

m = mujoco.MjModel.from_xml_path(a.model)
d = mujoco.MjData(m)
m.opt.timestep = DT
J = lambda n: mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, n)
B = lambda n: mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, n)
qa = {n: m.jnt_qposadr[J(n)] for n in LEG + WHL}
va = {n: m.jnt_dofadr[J(n)] for n in LEG + WHL}
wb = {B("left_wheel"), B("right_wheel")}
site = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_SITE, "imu")
sess = ort.InferenceSession(a.onnx, providers=["CPUExecutionProvider"])
iname = sess.get_inputs()[0].name
UP = np.array([0.0, 0.0, -1.0])
st = {"last": np.zeros(6, np.float32), "tgt": {}, "k": 0}


def reset(x=0.0):
    d.qpos[:] = 0.0
    d.qvel[:] = 0.0
    d.qpos[0] = x
    d.qpos[2] = R + 0.002
    d.qpos[3] = 1.0
    mujoco.mj_forward(m, d)
    st["last"][:] = 0.0
    st["tgt"] = {}
    st["k"] = 0


def grav():
    return d.xmat[site].reshape(3, 3).T @ UP


def infer(cmd, height, jump):
    o = np.zeros(35, np.float32)
    o[0] = cmd[0]
    o[1] = 0.0
    o[2] = cmd[1]
    o[3] = height * 5.0
    o[4:7] = d.qvel[3:6] * 0.5
    o[7:10] = grav()
    o[10:14] = [d.qpos[qa[n]] for n in OBS_LEG]
    o[16:20] = [d.qvel[va[n]] * 0.1 for n in OBS_LEG]
    o[20:22] = [d.qvel[va[n]] * 0.1 for n in WHL]
    o[22:28] = st["last"]
    o[28] = 1.0
    o[32] = jump
    act = sess.run(None, {iname: o.reshape(1, 35)})[0][0].astype(np.float32)
    st["last"] = act
    tgt = {n: act[i] * SCALE_LEG for i, n in enumerate(LEG)}
    tgt.update({n: act[4 + i] * SCALE_WHL for i, n in enumerate(WHL)})
    st["tgt"] = tgt


def control_step(cmd, height, jump, n=1):
    # mjlab's native <position>/<velocity> actuators hold the SETPOINT between policy
    # steps but re-evaluate kp*(q_des-q) - kd*qvel at EVERY physics substep.  Clipping
    # the resulting torque once per 20 substeps (what this used to do) is a different,
    # far softer controller, and made the policy look like it fell over.
    for _ in range(n):
        if st["k"] % DEC == 0:
            infer(np.array(cmd, np.float32), height, jump)
        st["k"] += 1
        d.qfrc_applied[:] = 0.0
        for nm in LEG:
            d.qfrc_applied[va[nm]] = np.clip(
                KP * (st["tgt"].get(nm, 0.0) - d.qpos[qa[nm]]) - KD * d.qvel[va[nm]],
                -a.leg_eff, a.leg_eff)
        for nm in WHL:
            d.qfrc_applied[va[nm]] = np.clip(
                WKD * (st["tgt"].get(nm, 0.0) - d.qvel[va[nm]]), -a.wheel_eff, a.wheel_eff)
        mujoco.mj_step(m, d)


def wheels_down():
    for c in range(d.ncon):
        ct = d.contact[c]
        if m.geom_bodyid[ct.geom1] in wb or m.geom_bodyid[ct.geom2] in wb:
            return True
    return False


def roll_deg():
    return math.degrees(math.asin(np.clip(-grav()[1], -1, 1)))


os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
rend = mujoco.Renderer(m, a.height_px, a.width)
cam = mujoco.MjvCamera()
cam.distance = 2.6
cam.elevation = -16
cam.azimuth = 145
vopt = mujoco.MjvOption()
# keep MuJoCo's default group mask: visual meshes are group 2, collision
# proxies are group 3 (hidden), so the CAD geometry is what you see.
import imageio.v2 as iio
w = iio.get_writer(a.out, fps=a.fps, codec="libx264", quality=8,
                   pixelformat="yuv420p", macro_block_size=16)
from PIL import Image, ImageDraw
nframes = [0]


def shoot(label, sub=""):
    rend.update_scene(d, camera=cam, scene_option=vopt)
    im = Image.fromarray(rend.render())
    dr = ImageDraw.Draw(im)
    dr.rectangle([0, 0, im.width, 30], fill=(0, 0, 0))
    dr.text((8, 8), label, fill=(255, 255, 255))
    if sub:
        dr.rectangle([0, im.height - 26, im.width, im.height], fill=(0, 0, 0))
        dr.text((8, im.height - 20), sub, fill=(255, 225, 120))
    w.append_data(np.asarray(im.convert("RGB")))
    nframes[0] += 1


def follow():
    cam.lookat[:] = d.qpos[0:3]
    cam.lookat[2] = max(0.12, float(d.qpos[2]))


def phase_run(dur):
    reset(0.0)
    for i in range(int(dur / DT)):
        t = i * DT
        vx = 2.8 * min(1.0, t / 2.0)
        control_step((vx, 0.0), a.height, 0.0)
        if i % DEC == 0:
            follow()
            shoot("SKILL 1/3  RUN  (cmd vx=%.1f m/s)" % vx,
                  "measured vx=%5.2f m/s   body z=%5.3f m   roll=%5.1f deg" % (d.qvel[0], d.qpos[2], roll_deg()))


def phase_gyro(dur):
    reset(0.0)
    for i in range(int(dur / DT)):
        control_step((0.0, 6.0), a.height, 0.0)
        if i % DEC == 0:
            cam.azimuth = 145 + math.degrees(float(d.qpos[6]))
            follow()
            shoot("SKILL 2/3  GYRO / xiao tui luo  (cmd wz=6.0 rad/s)",
                  "measured wz=%5.2f rad/s   yaw=%6.1f deg" % (d.qvel[5], math.degrees(float(d.qpos[6]))))


def phase_jump(dur):
    reset(0.0)
    z0 = None
    air = 0.0
    apex = 0.0
    for i in range(int(dur / DT)):
        t = i * DT
        jump = 1.0 if 1.0 < t < 2.4 else 0.0
        control_step((0.0, 0.0), a.height, jump)
        if z0 is None and t > 0.7:
            z0 = float(d.qpos[2])
        if z0 is not None:
            apex = max(apex, float(d.qpos[2]) - z0)
            if not wheels_down():
                air += DT
        if i % DEC == 0:
            cam.elevation = -22
            follow()
            shoot("SKILL 3/3  JUMP  (jump_cmd=%d)" % int(jump > 0),
                  "rise=%5.1f cm   airborne=%4.0f ms   vz=%5.2f m/s" % (apex * 100, air * 1000, d.qvel[2]))


def phase_field(dur):
    reset(1.0)
    cam.distance = 4.2
    cam.elevation = -30
    cam.azimuth = 115
    for i in range(int(dur / DT)):
        t = i * DT
        control_step((1.2 if t > 1.0 else 0.3, 0.0), a.height, 1.0 if 6.0 < t < 7.0 else 0.0)
        if i % DEC == 0:
            cam.lookat[:] = d.qpos[0:3]
            shoot("RMUC2026 7v7 MAP  (hfield built from the STEP map)",
                  "x=%5.2f m   z=%5.3f m   vx=%5.2f m/s   wheels_down=%d" % (d.qpos[0], d.qpos[2], d.qvel[0], int(wheels_down())))


FUN = {"run": phase_run, "gyro": phase_gyro, "jump": phase_jump, "field": phase_field}
print("policy:", os.path.basename(a.onnx))
print("plant :", a.model, "leg_eff=%.1f wheel_eff=%.1f obs=%s" % (a.leg_eff, a.wheel_eff, a.obs_order))
for p in [x.strip() for x in a.phases.split(",")]:
    if p in FUN:
        print("  render:", p)
        FUN[p](a.seconds)
    else:
        print("  skip unknown phase:", p)
w.close()
rend.close()
print("wrote", a.out, "frames:", nframes[0], "bytes:", os.path.getsize(a.out))
