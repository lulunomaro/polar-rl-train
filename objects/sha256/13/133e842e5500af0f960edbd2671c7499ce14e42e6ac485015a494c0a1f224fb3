"""Empirical crank->knee transmission, reference vs ours (projection trick:
gravity off, qvel zeroed, let the equality solver pull the passive joints onto the
constraint manifold).  This is the ground truth for 'is the linkage wired right?'."""
import numpy as np, mujoco, sys

CASES = {
 "REF (wheelbipeV14_2)": (r"D:/claude2/fangzhen/refs/wheelbipe_ros2_sim2sim-main/src/resources/robot_descriptions/wheelbipeV14_2/mjcf/wheelbipeV14_2.xml",
                          "left_front1_joint", "left_rear1_joint", "left_rear2_joint",
                          "left_wheel_link", "left_rear1_link"),
 "OURS (rm_vehicle_cc)": (r"D:/claude2/fangzhen/robot/out_cc/rm_vehicle_cc.xml",
                          "left_front1_joint", "left_rear1_joint", "left_rear2_joint",
                          "left_wheel", "left_thigh"),
}

def load(tag, xml, crank, thigh, knee, wheel_body, thigh_body):
    m = mujoco.MjModel.from_xml_path(xml); d = mujoco.MjData(m)
    def J(n):
        i = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, n)
        return -1 if i < 0 else i
    ids = dict(crank=J(crank), thigh=J(thigh), knee=J(knee))
    wb = J(wheel_body)
    def qa(i): return m.jnt_qposadr[i]
    names = [mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, j) for j in range(m.njnt)]
    print("\n===== %s  nq=%d nv=%d nu=%d neq=%d njnt=%d =====" % (tag, m.nq, m.nv, m.nu, m.neq, m.njnt))
    print("   joints:", " ".join(n for n in names if n and not n.startswith("right")))
    def solve(th, tc):
        mujoco.mj_resetData(m, d)
        m.opt.timestep = 0.002
        g = m.opt.gravity.copy(); m.opt.gravity[0] = m.opt.gravity[1] = m.opt.gravity[2] = 0.0
        if ids["thigh"] >= 0: d.qpos[qa(ids["thigh"])] = th
        if ids["knee"] >= 0:  d.qpos[qa(ids["knee"])]  = 0.0
        d.qpos[qa(ids["crank"])] = tc
        for _ in range(4000):
            d.qvel[:] = 0.0
            mujoco.mj_step(m, d)
        m.opt.gravity[:] = g
        out = dict(crank=tc, thigh=th,
                   knee=d.qpos[qa(ids["knee"])] if ids["knee"] >= 0 else np.nan,
                   wheel=d.xpos[wb].copy() if wb >= 0 else None)
        for jn in ("left_front2_joint","left_front3_joint","left_front4_joint","left_spring2_joint"):
            j = J(jn)
            if j >= 0: out[jn] = d.qpos[qa(j)]
        return out
    return m, d, ids, solve

for tag, args in CASES.items():
    try:
        m, d, ids, solve = load(tag, *args)
    except Exception as ex:
        print("  !! failed:", type(ex).__name__, ex); continue
    base = solve(0.0, 0.0)
    print("   nominal (all driven joints 0): knee=%+.4f front2=%s front3=%s front4=%s" %
          (base["knee"], *["%+.3f" % base[k] if k in base else "  n/a"
                           for k in ("left_front2_joint","left_front3_joint","left_front4_joint")]))
    if base["wheel"] is not None:
        print("   wheel body world pos:", np.round(base["wheel"], 4))
    print("   crank sweep (thigh held at 0):    crank     knee     ratio d(knee)/d(crank)")
    prev = None
    for tc in np.arange(-0.8, 0.85, 0.2):
        r = solve(0.0, tc)
        rr = float("nan")
        if prev is not None and abs(tc - prev["crank"]) > 1e-9:
            rr = (r["knee"] - prev["knee"]) / (tc - prev["crank"])
        print("                                 %+6.2f  %+8.4f   %+6.3f   (1/ratio=%5.2f)"
              % (tc, r["knee"], rr, 1/rr if rr == rr and abs(rr) > 1e-9 else float("nan")))
        prev = r
    print("   thigh sweep (crank held at 0):    thigh     knee     wheel(z)   knee-range")
    for tt in np.arange(-0.9, 0.95, 0.3):
        r = solve(tt, 0.0)
        wz = r["wheel"][2] if r["wheel"] is not None else float("nan")
        print("                                 %+6.2f  %+8.4f   %7.4f" % (tt, r["knee"], wz))
