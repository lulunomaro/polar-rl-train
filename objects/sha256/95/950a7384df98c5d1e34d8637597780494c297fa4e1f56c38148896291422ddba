"""Is the 小陀螺 asymmetry a MECHANISM problem or a POLICY problem?

docs/HOWTO.md 29.2 reports that v14, commanded -14 rad/s of yaw, only produced +2.27: the
policy spins one way and ignores the other sign.  Two completely different causes, two
completely different fixes:

  (a) mechanism - the closed chain drags a link on the ground, or an asymmetric passive limit
      (front3 really is -0.28..+1.22) blocks one direction, so the other way is physically
      harder.  Fix: geometry/limits, and retrain.
  (b) policy - the mechanism is symmetric and the policy just never learned the other sign.
      Fix: reward/command sampling/DR, no geometry change.

This script decides it without any policy and without the GPU: it WELDS the chassis to the
world (so the balance problem is removed and only the drive + linkage remain), holds the hips
at the trained stance, drives the wheels differentially at +-V rad/s, and reports the sustained
yaw rate in both directions plus every passive joint that touched its limit.

Usage:  python scripts/spin_symmetry.py [--speeds 10,20,30,40,50]
"""
import argparse, math, os
import mujoco
import numpy as np

ROOT = r"D:/claude2/fangzhen"
STANCE = {"left_front1_joint": 0.222, "left_rear1_joint": 0.097,
          "right_front1_joint": 0.230, "right_rear1_joint": 0.117}
LEG_KP, LEG_KD, LEG_T = 60.0, 2.0, 40.0
WH_KD, WH_T, WH_NL = 0.6, 5.5, 63.4
R_W, HALF = 0.073, 0.270

ap = argparse.ArgumentParser()
ap.add_argument("--speeds", default="10,20,30,40,50,55")
ap.add_argument("--seconds", type=float, default=6.0)
a = ap.parse_args()

xml = os.path.join(ROOT, "robot/out_cc/scene_cc.xml")
m = mujoco.MjModel.from_xml_path(xml)
d = mujoco.MjData(m)
mujoco.mj_resetDataKeyframe(m, d, 0)
nm = lambda o, i: mujoco.mj_id2name(m, o, i) or ""
JN = {nm(mujoco.mjtObj.mjOBJ_JOINT, i): i for i in range(m.njnt)}
QA = {k: int(m.jnt_qposadr[v]) for k, v in JN.items()}
VA = {k: int(m.jnt_dofadr[v]) for k, v in JN.items()}
AN = {nm(mujoco.mjtObj.mjOBJ_ACTUATOR, i): i for i in range(m.nu)}
root_dof = int(m.jnt_dofadr[JN[[k for k in JN if "floating" in k or "base" in k][0]]])


def hold_base_level():
    """Pin every base DOF EXCEPT yaw, so the balance problem disappears but the drive, the
    linkage and the ground drag are all still real.  A weld equality would have constrained
    yaw too, and an MjSpec weld is not available through this binding."""
    d.qpos[0] = 0.0
    d.qpos[1] = 0.0
    d.qpos[3:7] = (1.0, 0.0, 0.0, 0.0)
    d.qvel[root_dof:root_dof + 5] = 0.0
    d.qfrc_applied[root_dof:root_dof + 5] = 0.0


print("base pinned level (yaw free); neq=%d, nu=%d" % (m.neq, m.nu))
print("welded base; neq=%d (was 6, +1 weld)" % m.neq)


def dc(u, w_, stall, noload):
    wc = max(-2 * noload, min(2 * noload, w_))
    top = min(stall * (1 - wc / noload), stall)
    bot = max(stall * (-1 - wc / noload), -stall)
    return float(max(bot, min(top, u)))


def run(vl, vr, seconds=a.seconds):
    d.qpos[:] = 0.0
    d.qpos[2] = 0.075
    d.qpos[3] = 1.0
    d.qvel[:] = 0.0
    mujoco.mj_forward(m, d)
    n = int(seconds / m.opt.timestep)
    wz = np.zeros(n); wl = np.zeros(n); wr = np.zeros(n); tl = np.zeros(n); tr = np.zeros(n)
    for k in range(n):
        for jn, tgt in STANCE.items():
            cn = jn.replace("_joint", "_ctrl")
            u = LEG_KP * (tgt - d.qpos[QA[jn]]) - LEG_KD * d.qvel[VA[jn]]
            d.ctrl[AN[cn]] = float(np.clip(u, -LEG_T, LEG_T))
        for jn, V, stall in (("left_wheel_joint", vl, WH_T), ("right_wheel_joint", vr, WH_T)):
            cn = jn.replace("_joint", "_ctrl")
            v = d.qvel[VA[jn]]
            d.ctrl[AN[cn]] = dc(WH_KD * (V - v), v, stall, WH_NL)
        mujoco.mj_step(m, d)
        hold_base_level()
        wz[k] = d.qvel[root_dof + 5]; wl[k] = d.qvel[VA["left_wheel_joint"]]
        wr[k] = d.qvel[VA["right_wheel_joint"]]
        tl[k] = d.ctrl[AN["left_wheel_ctrl"]]; tr[k] = d.ctrl[AN["right_wheel_ctrl"]]
    t = slice(int(0.75 * n), n)
    lim = {}
    for jn, j in JN.items():
        if not m.jnt_limited[j]:
            continue
        q = d.qpos[QA[jn]]
        lo, hi = m.jnt_range[j]
        if q <= lo + 1e-4 or q >= hi - 1e-4:
            lim[jn] = (round(float(q), 3), [round(float(x), 3) for x in (lo, hi)])
    return dict(wz=float(wz[t].mean()), wl=float(wl[t].mean()), wr=float(wr[t].mean()),
                tau=(round(float(abs(tl[t]).mean()), 2), round(float(abs(tr[t]).mean()), 2)),
                sat=int((np.abs(tl[t]) > 0.985 * WH_T).sum() + (np.abs(tr[t]) > 0.985 * WH_T).sum()),
                limits=lim)


print("\n  wheel cmd |   yaw rate achieved | rev/s | wheel v L/R | |tau| L/R | sat | limits hit")
for V in [float(x) for x in a.speeds.split(",")]:
    cw = V * HALF / R_W          # wheel speed needed for wz = V
    pos = run(+cw, -cw)
    neg = run(-cw, +cw)
    for tag, r in (("+dir", pos), ("-dir", neg)):
        print("  wz=%5.1f %s | %8.2f rad/s | %5.2f | %6.1f %6.1f | %5.2f %5.2f | %3d | %s"
              % (V, tag, r["wz"], abs(r["wz"]) / (2 * math.pi), r["wl"], r["wr"],
                 r["tau"][0], r["tau"][1], r["sat"], r["limits"] or "-"))
    asym = abs(pos["wz"]) - abs(neg["wz"])
    print("           asymmetry: %+.2f rad/s (%.1f%%)" % (asym, 100 * asym / max(1e-6, abs(pos["wz"]))))
