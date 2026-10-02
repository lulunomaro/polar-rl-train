"""Pin down the SJTU/SCUT reference leg topology numerically from the MJCF itself."""
import numpy as np, mujoco
P = r"D:/claude2/fangzhen/refs/wheelbipe_ros2_sim2sim-main/src/resources/robot_descriptions/wheelbipeV14_2/mjcf/scene.xml"
m = mujoco.MjModel.from_xml_path(P); d = mujoco.MjData(m)
def bid(n): return mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, n)
def jid(n): return mujoco.mj_id2name and mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, n)
print("nq=%d nv=%d nu=%d neq=%d nkey=%d" % (m.nq, m.nv, m.nu, m.neq, m.nkey))
print("keyframe qpos:", np.round(m.key_qpos[0], 4) if m.nkey else None)
if m.nkey: mujoco.mj_resetDataKeyframe(m, d, 0)
mujoco.mj_forward(m, d)
print("\n-- joint tree (body / parent body / axis / type) --")
for j in range(m.njnt):
    n = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, j)
    b = m.jnt_bodyid[j]; pb = m.body_parentid[b]
    print("   %-24s body=%-22s parent=%-22s type=%d range=%s"
          % (n, mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, b),
             mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, pb), m.jnt_type[j],
             np.round(m.jnt_range[j], 3)))
print("\n-- equality (connect) details, world points at the initial qpos --")
for e in range(m.neq):
    t = m.eq_type[e]; o1 = int(m.eq_obj1id[e]); o2 = int(m.eq_obj2id[e])
    nm = lambda i: mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, i)
    ed = m.eq_data[e]
    pass
    R1 = np.eye(3) if o1 < 0 else d.xmat[o1].reshape(3, 3)
    x1 = np.zeros(3) if o1 < 0 else d.xpos[o1]
    p1 = x1 + R1 @ ed[0:3]
    R2 = np.eye(3) if o2 < 0 else d.xmat[o2].reshape(3, 3)
    x2 = np.zeros(3) if o2 < 0 else d.xpos[o2]
    p2 = x2 + R2 @ ed[3:6]
    print("   eq%d type=%d body1=%-22s body2=%-22s" % (e, t, nm(o1), nm(o2)))
    print("        eq_data=%s" % np.round(ed, 5))
    print("        pt1(world)=%s  pt2(world)=%s  gap=%.5f m" % (np.round(p1, 4), np.round(p2, 4), np.linalg.norm(p1 - p2)))
print("\n-- key landmarks in the initial pose (left leg, base frame) --")
base = d.xpos[bid("base_link")]
def rel(name): return d.xpos[bid(name)] - base
for n in ("left_front1_link", "left_rear1_link", "left_rear2_link", "left_wheel_link",
          "left_spring1_link", "left_spring2_link"):
    print("   %-20s rel-base=%s" % (n, np.round(rel(n), 4)))
# crank tip and APEX
f1 = bid("left_front1_link"); f2 = bid("left_front2_link"); f3 = bid("left_front3_link"); f4 = bid("left_front4_link")
hip = d.xpos[bid("left_rear1_link")]
for lbl, b in (("front1(crank)", f1), ("front2", f2), ("front3", f3), ("front4", f4)):
    print("   %-14s origin - hip = %s  |.|=%.4f" % (lbl, np.round(d.xpos[b] - hip, 4), np.linalg.norm(d.xpos[b] - hip)))
print("\n-- measured link lengths in the reference (from body offsets) --")
print("   hip->P2 (front2 pos in front1)      = %.4f" % np.linalg.norm(d.xpos[f2] - hip))
print("   P2->APEX (front3 pos in front2)     = %.4f" % np.linalg.norm(d.xpos[f3] - d.xpos[f2]))
print("   hip->knee (rear2 pos in rear1)      = %.4f" % np.linalg.norm(d.xpos[bid('left_rear2_link')] - hip))
print("   knee->axle (wheel pos in rear2)     = %.4f" % np.linalg.norm(d.xpos[bid('left_wheel_link')] - d.xpos[bid('left_rear2_link')]))
print("   hip->axle                           = %.4f" % np.linalg.norm(d.xpos[bid('left_wheel_link')] - hip))
