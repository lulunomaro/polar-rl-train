"""Stance calibration + 小陀螺 physical ceiling, measured on the validated plant.

WHY THIS EXISTS
v11 plateaued at 5.35 rad/s and v12 at ~5.7 rad/s of yaw rate while the yaw *command* range
was +-6.  Those numbers sit almost exactly on the ceiling implied by the wheel velocity-action
scale, because a yaw rate wz needs a wheel speed wz*half_track/wheel_r = 3.70*wz:

    WHEEL_ACTION_SCALE 10 -> +-10 rad/s wheel per unit action ->  2.71 rad/s yaw
    WHEEL_ACTION_SCALE 20 ->                          20 ->      5.41 rad/s yaw  == v11 5.35!
    WHEEL_ACTION_SCALE 55 ->                          55 ->     14.9 rad/s yaw  (motor 63.4)

So the policy was never "failing to learn to spin": it was handed an action unit ~6x too small
and was already at the end of its usable output range.  This script measures the real ceiling of
the plant, with the same DcMotor torque-speed curve mjlab uses, so the action scale and
RM_WZ_MAX come from physics instead of guesswork.

Two phases:
  1. stance calibration -- grid-search the (front1, rear1) hip targets for a pose where the
     robot stands on its two WHEELS only: chassis clear of the floor, tilt small, load on the
     wheels.  (qpos 0 is the CAD pose; it is NOT a stance that clears the floor, which is why
     an open-loop test that holds the legs at zero reads as "the robot lies on the ground".)
  2. ceiling sweep -- hold that stance, command DIFFERENTIAL wheel velocity +-V, and report the
     sustained yaw rate, wheel-torque saturation, tilt, and any leg geom that drags on the floor.
"""
import argparse, json, math, os, sys

import mujoco
import numpy as np

ROOT = r"D:/claude2/fangzhen"
XML = os.path.join(ROOT, "robot/out_cc/scene_cc.xml")

LEG_KP, LEG_KD, LEG_EFFORT = 60.0, 2.0, 40.0
WHEEL_KD, WHEEL_EFFORT, WHEEL_NOLOAD = 1.5, 5.5, 63.4
R_WHEEL, HALF_TRACK = 0.073, 0.270

ap = argparse.ArgumentParser()
ap.add_argument("--mode", default="both", choices=["stance", "spin", "both"])
ap.add_argument("--targets", default="8,14,20,26,32,38,44,50,56,62")
ap.add_argument("--seconds", type=float, default=4.0)
ap.add_argument("--settle", type=float, default=1.5)
ap.add_argument("--policy-dt", type=float, default=0.02, help="50 Hz policy, as in training")
ap.add_argument("--stance", default="", help='"front1,rear1" hip targets; default = search')
ap.add_argument("--json", default=os.path.join(ROOT, "docs/audit/gyro_ceiling.json"))
a = ap.parse_args()

m = mujoco.MjModel.from_xml_path(XML)
d = mujoco.MjData(m)
print("model nq=%d nv=%d nu=%d timestep=%.4f mass=%.3f kg"
      % (m.nq, m.nv, m.nu, m.opt.timestep, float(m.body_mass.sum())))


def _nm(obj, i):
    return mujoco.mj_id2name(m, obj, i)


J = {_nm(mujoco.mjtObj.mjOBJ_JOINT, i): i for i in range(m.njnt)}
A = {_nm(mujoco.mjtObj.mjOBJ_ACTUATOR, i): i for i in range(m.nu)}
LEG_CTRL = ["left_front1_ctrl", "left_rear1_ctrl", "right_front1_ctrl", "right_rear1_ctrl"]
WH_CTRL = ["left_wheel_ctrl", "right_wheel_ctrl"]
LEG_JOINTS = ["left_front1_joint", "left_rear1_joint", "right_front1_joint", "right_rear1_joint"]
WHEEL_JOINTS = ["left_wheel_joint", "right_wheel_joint"]
assert all(n in A for n in LEG_CTRL + WH_CTRL) and all(n in J for n in LEG_JOINTS + WHEEL_JOINTS)
root_j = next(n for n in J if int(m.jnt_type[J[n]]) == int(mujoco.mjtJoint.mjJNT_FREE))
RQA, RVA = int(m.jnt_qposadr[J[root_j]]), int(m.jnt_dofadr[J[root_j]])


def qa(n):
    return int(m.jnt_qposadr[J[n]])


def va(n):
    return int(m.jnt_dofadr[J[n]])


def geom_names_of(body):
    out = []
    for i in range(m.ngeom):
        b = _nm(mujoco.mjtObj.mjOBJ_BODY, i)
        if mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, body) == int(m.geom_bodyid[i]):
            out.append(_nm(mujoco.mjtObj.mjOBJ_GEOM, i) or str(i))
    return out


COLLIDERS = [i for i in range(m.ngeom)
             if m.geom_contype[i] or m.geom_conaffinity[i]]
print("colliding geoms:", [(_nm(mujoco.mjtObj.mjOBJ_GEOM, i), m.geom_type[i]) for i in COLLIDERS][:24])


def dc_clip(tau, w):
    v_corner = WHEEL_NOLOAD * 2.0
    wc = np.clip(w, -v_corner, v_corner)
    top = np.minimum(WHEEL_EFFORT * (1.0 - wc / WHEEL_NOLOAD), WHEEL_EFFORT)
    bot = np.maximum(WHEEL_EFFORT * (-1.0 - wc / WHEEL_NOLOAD), -WHEEL_EFFORT)
    return np.clip(tau, bot, top)


def step_control(qleg, wv_l, wv_r):
    for cn, jn in zip(LEG_CTRL, LEG_JOINTS):
        a_, b_ = qa(jn), va(jn)
        tau = LEG_KP * (qleg[jn] - d.qpos[a_]) - LEG_KD * d.qvel[b_]
        d.ctrl[A[cn]] = float(np.clip(tau, -LEG_EFFORT, LEG_EFFORT))
    for cn, jn, V in zip(WH_CTRL, WHEEL_JOINTS, (wv_l, wv_r)):
        b_ = va(jn)
        d.ctrl[A[cn]] = float(dc_clip(WHEEL_KD * (V - d.qvel[b_]), d.qvel[b_]))


def floor_forces():
    out = {}
    buf = np.zeros(6)
    for i in range(d.ncon):
        c = d.contact[i]
        g1 = _nm(mujoco.mjtObj.mjOBJ_GEOM, c.geom1) or str(c.geom1)
        g2 = _nm(mujoco.mjtObj.mjOBJ_GEOM, c.geom2) or str(c.geom2)
        if "floor" not in (g1, g2):
            continue
        other = g2 if g1 == "floor" else g1
        mujoco.mj_contactForce(m, d, i, buf)
        out[other] = out.get(other, 0.0) + float(abs(buf[0]))
    return out


def tilt():
    q = d.qpos[RQA + 3:RQA + 7]
    R = np.zeros(9)
    mujoco.mju_quat2Mat(R, q)
    return math.degrees(math.acos(float(np.clip(R.reshape(3, 3)[2, 2], -1.0, 1.0))))


def hold(qleg, seconds, wl=0.0, wr=0.0, pol_dt=0.02):
    n = int(seconds / m.opt.timestep)
    pol = max(1, int(round(pol_dt / m.opt.timestep)))
    for k in range(n):
        if k % pol == 0:
            step_control(qleg, wl, wr)
        else:
            for cn, jn in zip(LEG_CTRL, LEG_JOINTS):
                pass  # legs keep the same targets; effort is recomputed below anyway
            step_control(qleg, wl, wr)
        mujoco.mj_step(m, d)


def reset(q0):
    d.qpos[:] = q0
    d.qvel[:] = 0.0
    mujoco.mj_forward(m, d)


def target_pose(base_z=R_WHEEL + 0.002):
    q0 = np.zeros(m.nq); q0[2] = base_z; q0[3] = 1.0
    return q0


# ---------------------------------------------------------------- phase 1: stance
def body_z(name):
    b = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, name)
    return float(d.xpos[b, 2])


def find_stance():
    """Hold hip-angle targets and report the resulting stance: chassis height, tilt, and
    whether the robot stands on its WHEELS only.  A PD leg controller with kp=60 sags under
    the 20 kg load, so qpos 0 is NOT a static pose -- this table is what a "standing" target
    pair actually has to be."""
    rows = []
    print("\n-- phase 1: stance calibration --")
    print("  front1 rear1 | root_z  hip-wheel  tilt  wheelN  otherN | other contacts")
    for th in np.arange(-0.6, 0.65, 0.15):        # rear1 = thigh drive
        for tc in np.arange(-0.6, 0.65, 0.15):    # front1 = crank drive
            qleg = {"left_front1_joint": float(tc), "right_front1_joint": float(tc),
                    "left_rear1_joint": float(th), "right_rear1_joint": float(th)}
            reset(target_pose())
            hold(qleg, a.settle)
            cw = floor_forces()
            wn = sum(f for g, f in cw.items() if "wheel" in g)
            oth = {g: f for g, f in cw.items() if "wheel" not in g}
            r = dict(front1=float(tc), rear1=float(th), root_z=float(d.qpos[RQA + 2]),
                     hw=body_z("left_rear1") - body_z("left_wheel"),
                     tilt=tilt(), wheelN=wn, otherN=sum(oth.values()),
                     other=sorted(oth))
            rows.append(r)
            flag = "STAND" if (wn > 150 and r["otherN"] < 2.0) else ""
            print("  %+6.2f %+6.2f | %6.3f  %6.3f   %5.1f  %6.1f  %6.1f | %-22s %s"
                  % (tc, th, r["root_z"], r["hw"], r["tilt"], wn, r["otherN"],
                     ",".join(r["other"]) or "-", flag))
    ok = [r for r in rows if r["wheelN"] > 150 and r["otherN"] < 2.0]
    best = max(ok, key=lambda r: r["root_z"]) if ok else dict(front1=0.0, rear1=0.0)
    print("   chosen stance:", {k: best[k] for k in best if k != "other"})
    return best


# ---------------------------------------------------------------- phase 2: ceiling
def spin(V, qleg, q0):
    reset(q0)
    hold(qleg, a.settle)
    n = int(a.seconds / m.opt.timestep)
    pol = max(1, int(round(a.policy_dt / m.opt.timestep)))
    wz = np.zeros(n); h = np.zeros(n); tl = np.zeros(n); ww = np.zeros(n)
    nsat = 0; drag = {}; wn_last = 0.0
    for k in range(n):
        if k % pol == 0:
            step_control(qleg, +V, -V)          # DIFFERENTIAL: this is what a spin is
        mujoco.mj_step(m, d)
        wz[k] = d.qvel[RVA + 5]
        h[k] = d.qpos[RQA + 2]
        tl[k] = tilt()
        ww[k] = 0.5 * (abs(d.qvel[va(WHEEL_JOINTS[0])]) + abs(d.qvel[va(WHEEL_JOINTS[1])]))
        if min(abs(d.ctrl[A[WH_CTRL[0]]]), abs(d.ctrl[A[WH_CTRL[1]]])) > WHEEL_EFFORT * 0.985:
            nsat += 1
        if k % 200 == 0 and k > 0.6 * n:
            cw = floor_forces()
            wn_last = sum(f for g, f in cw.items() if "wheel" in g)
            for g, fz in cw.items():
                if "wheel" not in g:
                    drag[g] = max(drag.get(g, 0.0), fz)
    t = slice(int(0.75 * n), n)
    return dict(V=float(V), wz=abs(float(np.mean(wz[t]))), wz_pk=float(np.max(np.abs(wz))),
                wz_sd=float(np.std(wz[t])), wheel_rad_s=float(np.mean(ww[t])),
                sat_pct=100.0 * nsat / n, height=float(np.mean(h[t])),
                tilt_deg=float(np.mean(tl[t])), wheel_N=round(wn_last, 1),
                drag={k: round(v, 2) for k, v in sorted(drag.items())})


def main():
    out = {}
    if a.stance:
        f, r = [float(x) for x in a.stance.split(",")]
        st = dict(front1=f, rear1=r)
    else:
        st = find_stance() or dict(front1=0.0, rear1=0.0)
        if not st:
            st = dict(front1=0.0, rear1=0.0)
    out["stance"] = st
    qleg = {n: 0.0 for n in LEG_JOINTS}
    qleg["left_front1_joint"] = qleg["right_front1_joint"] = st["front1"]
    qleg["left_rear1_joint"] = qleg["right_rear1_joint"] = st["rear1"]
    q0 = target_pose()
    if a.mode in ("spin", "both"):
        print("\n-- phase 2: ceiling sweep, wheels commanded +-V (in-place spin) --")
        print("   kinematic ceiling %.1f rad/s wheel -> %.2f rad/s yaw"
              % (WHEEL_NOLOAD, WHEEL_NOLOAD * R_WHEEL / HALF_TRACK))
        rows = []
        for V in [float(x) for x in a.targets.split(",")]:
            r = spin(V, qleg, q0)
            rows.append(r)
            print("   V=%5.1f -> |wz|=%6.2f (pk %6.2f sd %5.2f) wheel %5.1f sat %5.1f%% "
                  "h %.3f tilt %5.1f WhlN %6.1f drag %s"
                  % (V, r["wz"], r["wz_pk"], r["wz_sd"], r["wheel_rad_s"], r["sat_pct"],
                     r["height"], r["tilt_deg"], r["wheel_N"], sorted(r["drag"]) or "-"))
        out["sweep"] = rows
        best = max(rows, key=lambda r: r["wz"])
        print("   best sustained yaw %.2f rad/s at wheel target %.0f rad/s" % (best["wz"], best["V"]))
        for tgt in (8.0, 10.0, 12.0, 14.0, 16.0):
            v_need = tgt * HALF_TRACK / R_WHEEL
            print("   hold %+5.1f rad/s yaw -> wheel %5.1f rad/s -> action +-1 scale >= %5.1f"
                  % (tgt, v_need, v_need))
    os.makedirs(os.path.dirname(a.json), exist_ok=True)
    json.dump(out, open(a.json, "w"), indent=1)
    print("wrote", a.json)


main()

