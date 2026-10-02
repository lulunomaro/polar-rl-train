"""Cross-validate the analytic 2-D closed-chain solver against MuJoCo's equality solver.

MuJoCo rotates about +Y, scripts/leg2d.py measures angles in the x->z sense, so the two
conventions differ by a sign:  theta_MJ = -theta_analytic  (positions are identical).
Passive limits and actuator forces are switched off so this is a pure kinematics test.
"""
import sys, numpy as np, mujoco
sys.path.insert(0, r"D:/claude2/fangzhen/scripts")
from leg2d import Kite2D, CAD, REF

MODELS = [
 dict(tag="REF ", xml=r"D:/claude2/fangzhen/refs/wheelbipe_ros2_sim2sim-main/src/resources/robot_descriptions/wheelbipeV14_2/mjcf/wheelbipeV14_2.xml",
      sfx="_link", pts=REF),
 dict(tag="OURS", xml=r"D:/claude2/fangzhen/robot/out_cc/rm_vehicle_cc.xml", sfx="", pts=CAD),
]
def J(m, n): return mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, n)
def B(m, n): return mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, n)

for cfg in MODELS:
    m = mujoco.MjModel.from_xml_path(cfg["xml"]); d = mujoco.MjData(m)
    L = Kite2D(cfg["pts"], cfg["tag"])
    sfx = cfg["sfx"]
    print("\n===== %s  (%s) =====" % (cfg["tag"], L.name))
    L.selfcheck()
    mujoco.mj_resetData(m, d); mujoco.mj_forward(m, d)
    print("  [gap@qpos0]  (a nonzero gap means MuJoCo silently rewired the linkage)")
    for e in range(m.neq):
        o1, o2 = int(m.eq_obj1id[e]), int(m.eq_obj2id[e]); ed = m.eq_data[e]
        n2 = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, o2)
        if not n2.startswith("left"): continue
        R1 = d.xmat[o1].reshape(3, 3); R2 = d.xmat[o2].reshape(3, 3)
        p1 = d.xpos[o1] + R1 @ ed[0:3]; p2 = d.xpos[o2] + R2 @ ed[3:6]
        print("      %-18s %-18s anchor1=%s anchor2=%s gap=%.4f mm"
              % (mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, o1), n2,
                 np.round(ed[0:3], 5), np.round(ed[3:6], 5), 1000 * np.linalg.norm(p1 - p2)))
    saved_lim = m.jnt_limited.copy(); m.jnt_limited[:] = 0
    bp, gp = m.actuator_biasprm.copy(), m.actuator_gainprm.copy()
    m.actuator_biasprm[:] = 0; m.actuator_gainprm[:] = 0
    kc, kt, kk = J(m, "left_front1" + sfx + "_joint"), J(m, "left_rear1" + sfx + "_joint"), J(m, "left_rear2" + sfx + "_joint")
    hip, axl = B(m, "left_rear1" + sfx), B(m, "left_wheel" + sfx)
    pj = dict(knee=kk, front2=J(m, "left_front2" + sfx + "_joint"),
              front3=J(m, "left_front3" + sfx + "_joint"), front4=J(m, "left_front4" + sfx + "_joint"),
              spring1=J(m, "left_spring1" + sfx + "_joint"), spring2=J(m, "left_spring2" + sfx + "_joint"))
    def settle(tc, th=0.0, n=2500):
        mujoco.mj_resetData(m, d); g = m.opt.gravity.copy(); m.opt.gravity[:] = 0
        d.qpos[m.jnt_qposadr[kt]] = th; d.qpos[m.jnt_qposadr[kc]] = tc
        for _ in range(n):
            d.qvel[:] = 0.0; mujoco.mj_step(m, d)
        m.opt.gravity[:] = g
        rel = d.xpos[axl][[0, 2]] - d.xpos[hip][[0, 2]]
        return d.qpos[m.jnt_qposadr[kk]], rel, {k: d.qpos[m.jnt_qposadr[v]] for k, v in pj.items() if v >= 0}
    print("  [analytic vs MuJoCo]  crank sweep (theta_MJ = -theta_analytic)")
    print("     crank_MJ  knee_MJ  knee_analytic   diff(deg)  axle_MJ(mm)      axle_analytic   ext")
    worst = 0.0
    for tc in np.arange(-0.6, 0.65, 0.15):
        r = L.solve(0.0, -tc); kn, ax, js = settle(tc)
        if r is None: print("     %+7.2f   analytic unreachable" % tc); continue
        dd = np.degrees(abs(kn + r["shank"]))
        dp = np.linalg.norm(1000 * ax - r["axle"])
        worst = max(worst, dd, dp)
        print("     %+7.2f  %+8.4f    %+8.4f     %5.2f    (%+6.1f,%+6.1f)  (%+6.1f,%+6.1f) %6.1f"
              % (tc, kn, -r["shank"], dd, 1000 * ax[0], 1000 * ax[1], r["axle"][0], r["axle"][1], r["ext"]))
    print("     worst disagreement = %.3f (deg / mm) -> %s"
          % (worst, "MATCH" if worst < 1.0 else "MISMATCH"))
    print("  [passive workspace] min/max of every passive joint over thigh x crank = +-1.2 rad")
    acc = {}
    for th in np.linspace(-1.2, 1.2, 13):
        for tc in np.linspace(-1.2, 1.2, 13):
            _, _, js = settle(tc, th, n=1500)
            for k, v in js.items(): acc.setdefault(k, []).append(v)
    for k, v in sorted(acc.items()):
        print("     %-8s [%+.3f, %+.3f] rad  = [%+.1f, %+.1f] deg"
              % (k, min(v), max(v), np.degrees(min(v)), np.degrees(max(v))))
    m.jnt_limited[:] = saved_lim; m.actuator_biasprm[:] = bp; m.actuator_gainprm[:] = gp
