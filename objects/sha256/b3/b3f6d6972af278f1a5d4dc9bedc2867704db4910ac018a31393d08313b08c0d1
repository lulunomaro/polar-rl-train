"""DECISIVE topology test: write the ANALYTIC closed-chain solution into the MJCF and
measure the equality-constraint gaps.  If the MJCF really implements the linkage the
analytic model describes, every gap must be ~0 for every driven pose."""
import sys, numpy as np, mujoco
sys.path.insert(0, r"D:/claude2/fangzhen/scripts")
from leg2d import Kite2D, CAD

REF = dict(knee=np.array([-210.0, 0.0]), axle=np.array([6.61, -124.83]),
           P2=np.array([112.65, 13.05]), P1=np.array([-113.40, -0.01]),
           apex=np.array([3.86, -66.90]), P3=np.array([-161.19, 46.97]),
           Q=np.array([-257.79, 46.97]), S1=np.array([2.36, -44.94]),
           S2=np.array([-162.42, -22.92]))
MODELS = [
 dict(tag="REF ", sfx="_link", pts=REF,
      xml=r"D:/claude2/fangzhen/refs/wheelbipe_ros2_sim2sim-main/src/resources/robot_descriptions/wheelbipeV14_2/mjcf/wheelbipeV14_2.xml"),
 dict(tag="OURS", sfx="", pts=CAD, xml=r"D:/claude2/fangzhen/robot/out_cc/rm_vehicle_cc.xml"),
]
def J(m, n): return mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, n)

for cfg in MODELS:
    m = mujoco.MjModel.from_xml_path(cfg["xml"]); d = mujoco.MjData(m)
    L = Kite2D(cfg["pts"], cfg["tag"]); L.selfcheck()
    sfx = cfg["sfx"]
    adr = {k: m.jnt_qposadr[J(m, "left_" + k + sfx + "_joint")]
          for k in ("rear1", "front1", "rear2", "front2", "front3", "front4", "spring1", "spring2")}
    print("  [%s] joint qpos addresses ok: %s" % (cfg["tag"], all(v >= 0 for v in adr.values())))
    print("     thigh   crank |  max connect gap (mm)  [hinges negated for MuJoCo's +Y; the slide is mm -> m]")
    worst = 0.0; nbad = 0; ntot = 0
    for th in np.arange(-1.2, 1.25, 0.3):
        row = []
        for tc in np.arange(-1.2, 1.25, 0.3):
            q = L.qpos_full(th, tc)
            if q is None:
                row.append("  n/a "); continue
            mujoco.mj_resetData(m, d)
            for k, a in adr.items():
                d.qpos[a] = q[k] / 1000.0 if k == "spring2" else -q[k]
            mujoco.mj_forward(m, d)
            gaps = []
            for e in range(m.neq):
                o1, o2 = int(m.eq_obj1id[e]), int(m.eq_obj2id[e]); ed = m.eq_data[e]
                p1 = d.xpos[o1] + d.xmat[o1].reshape(3, 3) @ ed[0:3]
                p2 = d.xpos[o2] + d.xmat[o2].reshape(3, 3) @ ed[3:6]
                gaps.append(1000 * np.linalg.norm(p1 - p2))
            g = max(gaps); ntot += 1
            worst = max(worst, g); nbad += g > 1.0
            row.append("%6.2f" % g)
        print("     %+5.2f  " % th + "".join(row))
    print("     => worst gap over %d poses = %.4f mm, %d poses above 1 mm  -> %s"
          % (ntot, worst, nbad, "MJCFC == ANALYTIC LINKAGE" if worst < 1.0 else "LINKAGE MISMATCH"))
