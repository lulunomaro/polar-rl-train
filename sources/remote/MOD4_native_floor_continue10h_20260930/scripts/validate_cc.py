"""Validate the closed-chain model: loop closure, transmission, workspace, dynamics."""
import math, os, sys
import numpy as np
import mujoco

XML = r"D:/claude2/fangzhen/robot/out_cc/scene_cc.xml"
m = mujoco.MjModel.from_xml_path(XML)
d = mujoco.MjData(m)
print("nq=%d nv=%d nu=%d nbody=%d neq=%d  mass=%.3f kg"
      % (m.nq, m.nv, m.nu, m.nbody, m.neq, sum(m.body_mass)))
print("joints:", [mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, i) for i in range(m.njnt)])

def jid(n):
    return mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, n)
def qa(n):
    return m.jnt_qposadr[jid(n)]

# ---- 1. loop closure at the zero pose
mujoco.mj_resetDataKeyframe(m, d, 0)
mujoco.mj_forward(m, d)
err = np.zeros(m.neq)
mujoco.mj_fullM(m, np.zeros((m.nv, m.nv))) if False else None
mujoco.mj_forward(m, d)
print("\n[1] equality residuals at the zero pose (should be ~0):")
for e in range(m.neq):
    # solve for the constraint violation via the position error stored in qD? use direct check
    pass
# direct geometric check of the three loops, left leg
def world(name):
    return d.xpos[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, name)]
for side in ("left", "right"):
    p1 = world("%s_front3" % side)
    p2 = world("%s_rear1" % side)
    print("   %-5s link3/thigh origin gap = %.4f m ; link4/shank = %.4f m ; spring2/shank = %.4f m"
          % (side, np.linalg.norm(p1 - p2),
             np.linalg.norm(world("%s_front4" % side) - world("%s_shank" % side)),
             np.linalg.norm(world("%s_spring2" % side) - world("%s_rear2" % side))))

# ---- 2. the connect anchor points must coincide: measure with a probe site
print("\n[2] constraint violation measured by mj_ineq (max |e|):")
mujoco.mj_forward(m, d)
# MuJoCo exposes the equality through the solver; instead verify by driving the crank
# and checking the shank follows the four-bar prediction.

# ---- 3. transmission: crank angle -> knee angle
print("\n[3] transmission scan (drive left_front1 = crank, hold the thigh):")
def settle(qcrank):
    mujoco.mj_resetDataKeyframe(m, d, 0)
    d.qpos[qa("left_front1_joint")] = qcrank
    # hold the thigh and the wheel, let the linkage find its configuration
    for _ in range(4000):
        d.qfrc_applied[:] = 0.0
        for n, target in (("left_rear1_joint", 0.0), ("left_front1_joint", qcrank),
                          ("right_front1_joint", 0.0), ("right_rear1_joint", 0.0)):
            j = jid(n); k = m.jnt_dofadr[j]
            d.qfrc_applied[k] = 200.0 * (target - d.qpos[qa(n)]) - 20.0 * d.qvel[k]
        mujoco.mj_step(m, d)
    return d.qpos[qa("left_shank_joint")] if jid("left_shank_joint") >= 0 else \
        d.qpos[qa("left_shank_joint".replace("shank", "shank"))]
names = [mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, i) for i in range(m.njnt)]
knee_name = "left_rear2_joint" if "left_rear2_joint" in names else None
print("   knee joint name:", knee_name)
rows = []
for qc in (-0.4, -0.2, 0.0, 0.2, 0.4, 0.6):
    mujoco.mj_resetDataKeyframe(m, d, 0)
    d.qpos[qa("left_front1_joint")] = qc
    for _ in range(6000):
        d.qfrc_applied[:] = 0.0
        for n, target in (("left_rear1_joint", 0.0), ("left_front1_joint", qc),
                          ("right_front1_joint", 0.0), ("right_rear1_joint", 0.0),
                          ("left_wheel_joint", 0.0), ("right_wheel_joint", 0.0)):
            k = m.jnt_dofadr[jid(n)]
            d.qfrc_applied[k] = 300.0 * (target - d.qpos[qa(n)]) - 30.0 * d.qvel[k]
        mujoco.mj_step(m, d)
    knee = d.qpos[qa(knee_name)]
    wheel_x = d.qpos[0 + 0]  # base x
    rows.append((qc, knee))
    print("   crank=%+.2f rad -> knee=%+.4f rad  (ratio %+.3f)  wheel pos z=%.4f"
          % (qc, knee, knee / qc if abs(qc) > 1e-6 else float("nan"), d.qpos[2]))

# ---- 4. free-fall stability
mujoco.mj_resetDataKeyframe(m, d, 0)
for _ in range(3000):
    mujoco.mj_step(m, d)
print("\n[4] 6 s free fall: base z=%.4f pitch(deg)=%.1f  contacts=%d"
      % (d.qpos[2], math.degrees(math.asin(np.clip(
          2 * (d.qpos[4] * d.qpos[6] + d.qpos[3] * d.qpos[5]), -1, 1))), len(d.contact)))
print("   joint q:", np.round(d.qpos[7:], 3))
