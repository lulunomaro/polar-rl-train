import sys, numpy as np, mujoco
sys.path.insert(0, r"D:/claude2/fangzhen/scripts")
from leg2d import Kite2D, CAD
m = mujoco.MjModel.from_xml_path(r"D:/claude2/fangzhen/robot/out_cc/rm_vehicle_cc.xml")
d = mujoco.MjData(m); L = Kite2D(CAD, "ours")
def J(n): return mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, n)
names = ["rear1","front1","rear2","front2","front3","front4","spring1","spring2"]
adr = {k: m.jnt_qposadr[J("left_%s_joint" % k)] for k in names}
print("addresses:", adr)
print("nq", m.nq, "axis front1/rear1/rear2:", m.jnt_axis[J("left_front1_joint")], m.jnt_axis[J("left_rear1_joint")], m.jnt_axis[J("left_rear2_joint")])
q = L.qpos_full(0.0, 0.3)
print("\nanalytic qpos:", {k: round(q[k], 4) for k in names})
mujoco.mj_resetData(m, d)
for k, v in q.items():
    a = adr[k]; d.qpos[a] = -v if k != "spring2" else v
mujoco.mj_forward(m, d)
print("qpos written:", np.round([d.qpos[adr[k]] for k in names], 4))
base = d.xpos[J("left_rear1_joint") if False else mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "base_link")]
print("base xpos", np.round(base, 4))
for e in range(m.neq):
    o1, o2 = int(m.eq_obj1id[e]), int(m.eq_obj2id[e]); ed = m.eq_data[e]
    n1 = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, o1); n2 = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, o2)
    if not n2.startswith("left"): continue
    p1 = d.xpos[o1] + d.xmat[o1].reshape(3,3) @ ed[0:3]
    p2 = d.xpos[o2] + d.xmat[o2].reshape(3,3) @ ed[3:6]
    print("  %-14s %-14s p1=%s p2=%s gap=%.1f mm" % (n1, n2, np.round(p1,4), np.round(p2,4), 1000*np.linalg.norm(p1-p2)))
    print("      eq_type=%d eq_data=%s" % (m.eq_type[e], np.round(ed,4)))
# what does MuJoCo think the points are vs the analytic prediction?
hip = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "left_rear1")
print("\nMJ hip world:", np.round(d.xpos[hip],4), " analytic hip (mm, base frame):", CAD["knee"]*0)
for bn in ("left_front1","left_front2","left_front3","left_front4","left_rear2","left_wheel","left_spring1","left_spring2"):
    b = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, bn)
    print("   %-14s world=%s  rel-hip(mm)=%s" % (bn, np.round(d.xpos[b],4), np.round(1000*(d.xpos[b]-d.xpos[hip]),1)))
r = q["pts"]
print("\nanalytic (mm, hip frame): knee", np.round(r["knee"],1), " axle", np.round(r["axle"],1),
      " P3", np.round(r["P3"],1), " Q", np.round(r["Q"],1), " apex", np.round(r["apex"],1), " P1", np.round(r["P1"],1))
