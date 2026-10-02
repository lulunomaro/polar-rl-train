"""How well does the DEPLOYED plant hold its six <connect> equalities while stepping?

Sweep dt / iterations / impratio / cone, drive the two hip joints with the same PD the
deployment uses toward a non-zero pose, and report the worst loop gap plus the stance height.
A gap of centimetres means the constraint solver is losing the closed chain, which makes every
published state off-manifold and any policy transfer test meaningless.
"""
import sys, numpy as np, mujoco
sys.path.insert(0, r"D:/claude2/fangzhen/scripts")
from leg2d import Kite2D, CAD

L = Kite2D(CAD, "t")
XML = r"D:/claude2/fangzhen/sim2sim_cc/rm_vehicle/mjcf/scene.xml"
KEYS = ("rear1", "front1", "rear2", "front2", "front3", "front4", "spring1", "spring2")
LEG = ["left_front1_joint", "left_rear1_joint", "right_front1_joint", "right_rear1_joint"]
WHL = ["left_wheel_joint", "right_wheel_joint"]
ORDER = LEG + WHL


def gaps(m, d):
    g = 0.0
    for e in range(m.neq):
        b1, b2 = int(m.eq_obj1id[e]), int(m.eq_obj2id[e]); ed = m.eq_data[e]
        p1 = d.xpos[b1] + d.xmat[b1].reshape(3, 3) @ ed[0:3]
        p2 = d.xpos[b2] + d.xmat[b2].reshape(3, 3) @ ed[3:6]
        g = max(g, 1000.0 * float(np.linalg.norm(p1 - p2)))
    return g


def run(dt, iters, impratio, cone, seconds=3.0, thigh=0.0, crank=0.45, kp=60.0, kd=2.0):
    m = mujoco.MjModel.from_xml_path(XML)
    d = mujoco.MjData(m)
    m.opt.timestep = dt; m.opt.iterations = iters
    m.opt.impratio = impratio; m.opt.cone = cone
    q = L.qpos_full(thigh, crank)
    assert q is not None, "pose outside workspace"
    qa = {n: m.jnt_qposadr[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, n)] for n in ORDER}
    va = {n: m.jnt_dofadr[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, n)] for n in ORDER}
    tgt = {n: -q["front1"] for n in LEG if "front1" in n}
    tgt.update({n: -q["rear1"] for n in LEG if "rear1" in n})
    tgt.update({n: 0.0 for n in WHL})
    mujoco.mj_resetData(m, d)
    for s in ("left", "right"):
        for k in KEYS:
            j = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, "%s_%s_joint" % (s, k))
            a = m.jnt_qposadr[j]; v = m.jnt_dofadr[j]
            d.qpos[a] = q[k] / 1000.0 if k == "spring2" else -q[k]
            d.qvel[v] = 0.0
    d.qpos[2] = 0.075
    d.qpos[3] = 1.0
    mujoco.mj_forward(m, d)
    g0 = gaps(m, d)
    worst = g0
    for _ in range(int(seconds / dt)):
        d.qfrc_applied[:] = 0.0
        for n in LEG:
            u = kp * (tgt[n] - d.qpos[qa[n]]) - kd * d.qvel[va[n]]
            d.qfrc_applied[va[n]] = float(np.clip(u, -40, 40))
        for n in WHL:
            u = 1.5 * (0.0 - d.qvel[va[n]])
            d.qfrc_applied[va[n]] = float(np.clip(u, -5.5, 5.5))
        mujoco.mj_step(m, d)
        worst = max(worst, gaps(m, d))
    return g0, worst, float(d.qpos[2]), float(np.abs(d.qvel[:]).max())


print("plant: DEPLOYED scene.xml (nq=25 neq=6)   drive: hips -> crank 0.45 rad, 3 s")
print("%-8s %-6s %-9s %-10s | %-12s %-12s %-10s %s" %
      ("dt", "iter", "impratio", "cone", "gap@t0(mm)", "worst(mm)", "base_z", "max|qvel|"))
for dt, iters, impr, cone, tag in [
        (0.001, 100, 1.0, mujoco.mjtCone.mjCONE_PYRAMIDAL, "plant default"),
        (0.002, 100, 1.0, mujoco.mjtCone.mjCONE_PYRAMIDAL, "dt=2ms (current deploy)"),
        (0.002, 200, 1.0, mujoco.mjtCone.mjCONE_PYRAMIDAL, "dt=2ms iter200"),
        (0.002, 100, 50.0, mujoco.mjtCone.mjCONE_ELLIPTIC, "dt=2ms warp-like"),
        (0.001, 100, 1.0, mujoco.mjtCone.mjCONE_ELLIPTIC, "dt=1ms elliptic")]:
    g0, gw, z, qv = run(dt, iters, impr, cone)
    print("%-8s %-6d %-9g %-10s | %-12.4f %-12.4f %-10.4f %.2f   %s" %
          (dt, iters, impr, "elliptic" if cone else "pyramidal", g0, gw, z, qv, tag))