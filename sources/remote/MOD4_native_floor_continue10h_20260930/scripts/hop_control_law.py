# -*- coding: utf-8 -*-
"""Does the policy still hop when the leg PD is evaluated like the HARDWARE does?

Training (mjlab DcMotorActuator = IdealPdActuator) computes the torque once per 50 Hz
policy step and holds it across the physics substeps.  The deployment recomputes the PD
at 500 Hz from the same 50 Hz setpoint.  For a fast movement like a hop those are
effectively different plants, so measure the hop under both.

Variants:  flag (jump only) | flag+walk (vx=1) | flag+crouch (height cmd lowered)
"""
import os
import sys
import numpy as np
import mujoco
import onnxruntime as ort

XML = r"D:/claude2/fangzhen/robot/out_cc/scene_cc.xml"
ONNX = sys.argv[1] if len(sys.argv) > 1 else r"D:/claude2/fangzhen/train/deploy/rm_cc_v11_final.onnx"
LEG_EFF, WHEEL_EFF = 40.0, 5.5
LEG = ["left_front1_joint", "left_rear1_joint", "right_front1_joint", "right_rear1_joint"]
WHL = ["left_wheel_joint", "right_wheel_joint"]
# mjlab trains with dt = 2 ms and decimation 10 (policy at 50 Hz).  The harness used to
# run at 1 ms, which is a different plant for a 0.5 s hop, and it clipped the leg torque
# at a flat +-40 N*m.  A real DM-J8009 has a linear torque-speed envelope: the PD setpoint
# is unreachable once the rotor approaches no-load speed, so the ceiling must collapse to
# zero as |omega| -> vlim.  Without this the legs are far stronger than reality and the
# hop diverges, which is why the old harness numbers were unusable.
DT = float(os.environ.get("RM_HARNESS_DT", "0.002"))
LEG_VLIM, WHEEL_VLIM = 17.0, 63.4        # rad/s no-load at 24 V (docs/MOTOR_PARAMS.md)
ENVELOPE = os.environ.get("RM_HARNESS_ENVELOPE", "1") == "1"
def cap_for(eff, vlim, omega):
    if not ENVELOPE:
        return eff
    return eff * max(0.0, 1.0 - abs(omega) / vlim)
KP, KD, WKD = 60.0, 2.0, 1.5
S_LEG, S_WHL = 0.5, 10.0

m = mujoco.MjModel.from_xml_path(XML)
d = mujoco.MjData(m)
m.opt.timestep = DT
# Match the TRAINING solver regime, not just the plant.  env_cfgs.py builds the task with
# timestep 0.002, iterations 10, ls_iterations 10, impratio 50, cone elliptic; the MJCF
# ships iterations=100 / impratio=1 / pyramidal.  With six <connect> equalities those two
# regimes are materially different plants, which is why the harness disagreed with mjlab.
if os.environ.get("RM_HARNESS_TRAIN_SOLVER", "0") == "1":   # explodes on CPU MuJoCo
    m.opt.iterations = 10
    m.opt.ls_iterations = 10
    m.opt.impratio = 50.0
    m.opt.cone = mujoco.mjtCone.mjCONE_ELLIPTIC
J = lambda n: mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, n)
BD = lambda n: mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, n)
qa = {n: m.jnt_qposadr[J(n)] for n in LEG + WHL}
va = {n: m.jnt_dofadr[J(n)] for n in LEG + WHL}
wb = {BD("left_wheel"), BD("right_wheel")}
# ACTION ORDER is [4 legs, 2 wheels]: the deployed controller's joint_action_scale is
# [0.5, 0.5, 0.5, 0.5, 10.0, 10.0], so a[0..3] are the leg position targets and a[4..5]
# the wheel velocity targets.  This is NOT the <actuator> block order of the MJCF.
ACT_J = LEG + WHL
assert m.nu == 6, m.nu
LEGSET = set(LEG)
site = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_SITE, "imu")
GSAD = {n: m.sensor_adr[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_SENSOR, n)]
        for n in ("gyro", "framequat")}
sess = ort.InferenceSession(ONNX, providers=["CPUExecutionProvider"])
inp = sess.get_inputs()[0].name
UP = np.array([0.0, 0.0, -1.0])


def wheels_down():
    for c in range(d.ncon):
        ct = d.contact[c]
        if m.geom_bodyid[ct.geom1] in wb or m.geom_bodyid[ct.geom2] in wb:
            return True
    return False


def run(policy_hz, mode, seconds=8.0, t_trigger=2.0, hold=1.2):
    dec = max(1, int(round((1.0 / policy_hz) / DT)))
    last = np.zeros(6, np.float32)
    tgt = {n: 0.0 for n in LEG + WHL}
    d.qpos[:] = 0.0
    d.qpos[2] = 0.075
    d.qpos[3] = 1.0
    d.qvel[:] = 0.0
    mujoco.mj_forward(m, d)

    def infer(jump, height, vx):
        nonlocal last
        g = d.xmat[site].reshape(3, 3).T @ UP
        o = np.zeros(35, np.float32)
        o[0], o[1], o[2], o[3] = vx, 0.0, 0.0, height * 5.0
        # body-frame angular velocity straight from the model's gyro sensor, matching
        # robot_state.body_state.ang_vel_b in state_rl.cpp
        o[4:7] = d.sensordata[GSAD["gyro"]:GSAD["gyro"] + 3] * 0.5
        o[7:10] = g
        o[10:14] = [d.qpos[qa[n]] for n in LEG]
        o[16:20] = [d.qvel[va[n]] * 0.1 for n in LEG]
        o[20:22] = [d.qvel[va[n]] * 0.1 for n in WHL]
        o[22:28] = last
        o[28] = 1.0
        o[32] = jump
        a = sess.run(None, {inp: o.reshape(1, 35)})[0][0].astype(np.float32)
        last = a
        for i, jn in enumerate(ACT_J):
            tgt[jn] = a[i] * (S_LEG if jn in LEGSET else S_WHL)

    frozen = dict(tgt)
    z0 = None
    hop = 0.0
    cr = 0.0
    air = 0.0
    tilt = 0.0
    tilt_at_hop = 0.0
    for k in range(int(seconds / DT)):
        t = k * DT
        jump = 1.0 if (t_trigger <= t < t_trigger + hold) else 0.0
        height = 0.16 if (mode == "flag+crouch" and jump > 0) else 0.22
        vx = 1.0 if (mode == "flag+walk") else 0.0
        if k % dec == 0:
            infer(jump, height, vx)
            frozen = dict(tgt)
        d.qfrc_applied[:] = 0.0
        for nm in LEG:
            w = d.qvel[va[nm]]
            c = cap_for(LEG_EFF, LEG_VLIM, w)
            tau = KP * (frozen.get(nm, 0.0) - d.qpos[qa[nm]]) - KD * w
            d.qfrc_applied[va[nm]] = float(np.clip(tau, -c, c))
        for nm in WHL:
            w = d.qvel[va[nm]]
            c = cap_for(WHEEL_EFF, WHEEL_VLIM, w)
            d.qfrc_applied[va[nm]] = float(np.clip(WKD * (frozen.get(nm, 0.0) - w), -c, c))
        mujoco.mj_step(m, d)
        if z0 is None and t > t_trigger - 0.4:
            z0 = float(d.qpos[2])
        qu = d.qpos[3:7]
        uw = np.array([2 * (qu[1] * qu[3] - qu[0] * qu[2]),
                       2 * (qu[2] * qu[3] + qu[0] * qu[1]),
                       1 - 2 * (qu[1] * qu[1] + qu[2] * qu[2])])
        tl = float(np.degrees(np.arccos(np.clip(np.dot(uw, UP), -1.0, 1.0))))
        tilt = max(tilt, tl)
        if z0 is not None:
            dz = float(d.qpos[2]) - z0
            if dz > hop:
                hop, tilt_at_hop = dz, tl
            cr = min(cr, dz)
            if not wheels_down():
                air += DT
    return hop * 100.0, cr * 100.0, air * 1000.0, tilt, tilt_at_hop


print("policy:", ONNX.split("/")[-1],
      "| plant: honest dm8009 (40 / 5.5 N*m) | dt=%.4f s | torque-speed envelope=%s"
      % (DT, "ON (vlim 17 / 63.4 rad/s)" if ENVELOPE else "OFF"))
print("%-16s %-12s %8s %10s %8s %9s %10s" % ("control law", "variant", "hop cm",
      "crouch cm", "air ms", "tilt max", "tilt@hop"))
for hz, lab in ((50, "50 Hz (train)"), (500, "500 Hz (hw)"), (1000, "1 kHz (ideal)")):
    for mode in ("flag", "flag+walk", "flag+crouch"):
        hop, cr, air, tl, tlh = run(hz, mode)
        print("%-16s %-12s %8.1f %10.1f %8.0f %9.1f %10.1f %s"
              % (lab, mode, hop, cr, air, tl, tlh,
                 "UPRIGHT" if tl < 25 else "TOPPLED - not a hop"))