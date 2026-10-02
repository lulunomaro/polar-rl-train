"""Does the TRAINING backend (mujoco-warp) enforce the closed chain?
Gravity and contacts are switched off so this is a pure transmission test: drive the two
hip cranks with a PD and compare every passive joint with the validated analytic model.
MuJoCo hinges about +Y, leg2d measures x->z, so qpos_MJ = -qpos_analytic."""
import sys, io, os, numpy as np, mujoco, warp as wp
wp.config.quiet = True
import mujoco_warp as mjwarp
sys.path.insert(0, r"D:/claude2/fangzhen/scripts")
from leg2d import Kite2D, CAD
XML = r"D:/claude2/fangzhen/robot/out_cc/rm_vehicle_cc.xml"
m = mujoco.MjModel.from_xml_path(XML); m.opt.gravity[:] = 0.0
d = mujoco.MjData(m); L = Kite2D(CAD, "cc")
def J(n): return mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, n)
LEGS = ("front1", "rear1", "rear2", "front2", "front3", "front4", "spring1", "spring2")
adr, dof = {}, {}
for side in ("left", "right"):
    for k in LEGS:
        j = J("%s_%s_joint" % (side, k))
        if j >= 0: adr[(side, k)] = m.jnt_qposadr[j]; dof[(side, k)] = m.jnt_dofadr[j]
mw = mjwarp.put_model(m)
print("device %s | neq=%d eq_connect_adr=%s eq_active=%s"
      % (wp.get_device(), m.neq, np.array(mw.eq_connect_adr.numpy()),
         mjwarp.put_data(m, d, nworld=1).eq_active.numpy()[0, :3]))

def run(tc, th=0.0, steps=1200, kp=200.0, kd=20.0):
    mujoco.mj_resetData(m, d)
    dw = mjwarp.put_data(m, d, nworld=1)
    tgt = {("left", "front1"): tc, ("right", "front1"): tc,
           ("left", "rear1"): th, ("right", "rear1"): th}
    for _ in range(steps):
        f = np.zeros((1, m.nv))
        for (side, jn), a in dof.items():
            if (side, jn) in tgt:
                f[0, a] = kp * (tgt[(side, jn)] - dw.qpos.numpy()[0, adr[(side, jn)]]) - kd * dw.qvel.numpy()[0, a]
        dw.qfrc_applied.assign(f); mjwarp.step(mw, dw)
    return dw.qpos.numpy()[0]

def gaps(q):
    mujoco.mj_resetData(m, d)
    for key, a in adr.items(): d.qpos[a] = q[a]
    mujoco.mj_forward(m, d)
    g = []
    for e in range(m.neq):
        o1, o2 = int(m.eq_obj1id[e]), int(m.eq_obj2id[e]); ed = m.eq_data[e]
        p1 = d.xpos[o1] + d.xmat[o1].reshape(3, 3) @ ed[0:3]
        p2 = d.xpos[o2] + d.xmat[o2].reshape(3, 3) @ ed[3:6]
        g.append(1000 * np.linalg.norm(p1 - p2))
    return max(g)

print("\n  thigh crank |  knee   front2  front3  front4  spring1 (GPU qpos, deg)  | analytic diff | gap")
worst = 0.0
for th, tc in ((0.0, -0.6), (0.0, -0.3), (0.0, 0.0), (0.0, 0.3), (0.0, 0.6),
               (0.6, 0.0), (-0.6, 0.0), (0.9, 0.45), (-0.9, -0.45)):
    q = run(tc, th)
    # compare at the ACHIEVED driven angles: the PD droops under the 350 N gas spring,
    # so the commanded (th, tc) are not the actual joint positions.
    th_a, tc_a = -q[adr[("left", "rear1")]], -q[adr[("left", "front1")]]
    an = L.qpos_full(th_a, tc_a)
    keys = ("rear2", "front2", "front3", "front4", "spring1")
    got = np.array([np.degrees(q[adr[("left", k)]]) for k in keys])
    exp = np.array([np.degrees(-an[k]) for k in keys])
    g = gaps(q); worst = max(worst, np.abs(got - exp).max())
    print("   %+5.2f %+5.2f | " % (th_a, tc_a) + " ".join("%7.2f" % v for v in got)
          + "   | max diff %5.2f deg | %.3f mm" % (np.abs(got - exp).max(), g))
print("\nworst passive-joint disagreement GPU vs analytic = %.2f deg -> %s"
      % (worst, "GPU SIM ENFORCES THE CLOSED CHAIN" if worst < 5.0 else "NOT ENFORCED"))
