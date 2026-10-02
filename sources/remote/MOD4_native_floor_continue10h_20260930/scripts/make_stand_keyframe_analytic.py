"""Analytic stand keyframe: upright base + the trained hip stance + the solver's passive joints.

Why not the settle-based generator (scripts/make_stand_keyframe.py): holding the hips with a PD for
seconds lets the chassis pitch ~20 deg before it is captured, and the balance law cannot pull it
back (a velocity-targeted wheel servo with a 5.5 N*m ceiling gives zero torque at any constant
wheel speed, so a constant tilt has no constant correction).  A keyframe with 20 deg of pitch
baked in is out of distribution for a policy that is spawned upright - that is exactly what
docs/HOWTO.md 36.3 measured.

So build the state directly: identity quaternion (pitch/roll = 0 by construction), hips at the
measured stance, and every passive joint from the SAME analytic 2D solver that scripts/cc_gaps.py
validated to 0.0000 mm over 81 poses.  Then let MuJoCo itself verify: all six connect gaps, the
wheel bottoms, and the attitude.
"""
import json, os, sys
import mujoco
import numpy as np
sys.path.insert(0, r"D:/claude2/fangzhen/scripts")
from leg2d import Kite2D, CAD  # noqa: E402

ROOT = r"D:/claude2/fangzhen"
STANCE = dict(zip(["left_front1", "left_rear1", "right_front1", "right_rear1"],
                  [float(x) for x in os.environ.get(
                      "RM_STANCE", "0.222,0.097,0.230,0.117").split(",")]))
PLANT = os.path.join(ROOT, "robot/out_cc/scene_cc.xml")
m = mujoco.MjModel.from_xml_path(PLANT)
d = mujoco.MjData(m)
nm = lambda o, i: mujoco.mj_id2name(m, o, i) or ""
JN = {nm(mujoco.mjtObj.mjOBJ_JOINT, i): i for i in range(m.njnt)}
QA = {k: int(m.jnt_qposadr[v]) for k, v in JN.items()}
kite = Kite2D(CAD, "CAD")
errs = kite.selfcheck(verbose=False)
print("analytic solver selfcheck:", "ok" if not errs else errs)

q = np.zeros(m.nq)
q[0:2] = 0.0
q[3:7] = (1.0, 0.0, 0.0, 0.0)          # upright, no yaw: exactly what training spawns
for side in ("left", "right"):
    # cc_gaps.py writes qpos = -angle, so to land the hips at the POSITIVE stance the
    # policy actually holds in training, the solver has to be driven with the negatives.
    crank = -STANCE["%s_front1" % side]     # front1 = the crank driving the passive knee
    thigh = -STANCE["%s_rear1" % side]      # rear1  = the thigh drive
    full = kite.qpos_full(thigh, crank)
    assert full is not None, "the chain cannot close for this stance"
    for key, jn in (("rear1", "%s_rear1_joint" % side), ("front1", "%s_front1_joint" % side),
                    ("rear2", "%s_rear2_joint" % side), ("front2", "%s_front2_joint" % side),
                    ("front3", "%s_front3_joint" % side), ("front4", "%s_front4_joint" % side),
                    ("spring1", "%s_spring1_joint" % side)):
        q[QA[jn]] = -full[key]
    q[QA["%s_spring2_joint" % side]] = full["spring2"] / 1000.0
# drop the base until both wheels just touch the floor
for _ in range(200):
    d.qpos[:] = q
    mujoco.mj_forward(m, d)
    zb = min(float(d.geom_xpos[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_GEOM,
               "%s_wheel_col" % s), 2] - m.geom_size[
        mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_GEOM, "%s_wheel_col" % s), 0])
        for s in ("left", "right"))
    q[2] -= zb - 0.0
d.qpos[:] = q
d.qvel[:] = 0.0
mujoco.mj_forward(m, d)
gaps = []
for i in range(m.neq):
    if int(m.eq_type[i]) != int(mujoco.mjtEq.mjEQ_CONNECT):
        continue
    b1, b2 = int(m.eq_obj1id[i]), int(m.eq_obj2id[i])
    a1 = np.asarray(m.eq_data[i][0:3], float); a2 = np.asarray(m.eq_data[i][3:6], float)
    p1 = np.asarray(d.xpos[b1]) + np.asarray(d.xmat[b1]).reshape(3, 3) @ a1
    p2 = np.asarray(d.xpos[b2]) + np.asarray(d.xmat[b2]).reshape(3, 3) @ a2
    gaps.append(float(np.linalg.norm(p1 - p2)))
R = np.asarray(d.xmat[1], float).reshape(3, 3)
g = R.T @ np.array([0.0, 0.0, -1.0])
pitch = float(np.degrees(np.arcsin(np.clip(g[0], -1, 1))))
roll = float(np.degrees(np.arcsin(np.clip(-g[1], -1, 1))))
wb = [float(d.geom_xpos[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_GEOM, "%s_wheel_col" % s), 2]
           - m.geom_size[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_GEOM,
                                           "%s_wheel_col" % s), 0])
      for s in ("left", "right")]
lim = {jn: [round(float(q[QA[jn]]), 4), [round(float(x), 3) for x in m.jnt_range[j]]]
       for jn, j in JN.items() if m.jnt_limited[j]
       and (q[QA[jn]] <= m.jnt_range[j][0] + 1e-4 or q[QA[jn]] >= m.jnt_range[j][1] - 1e-4)}
res = dict(source="analytic (leg2d.Kite2D.qpos_full, validated 0.0000 mm by cc_gaps.py)",
           stance=STANCE, base_z=round(float(q[2]), 5), pitch_deg=round(pitch, 3),
           roll_deg=round(roll, 3), eq_gap_max_mm=round(1000 * max(gaps), 5),
           wheel_bottom_z=[round(x, 5) for x in wb],
           achieved_hips={k: round(float(q[QA[k + "_joint"]]), 4)
                          for k in ("left_front1", "left_rear1", "right_front1", "right_rear1")},
           passive_at_limit=lim, qpos=[round(float(x), 6) for x in q], qvel=[0.0] * m.nv)
print(json.dumps({k: v for k, v in res.items() if k not in ("qpos", "qvel")}, indent=1))
assert max(gaps) * 1000 < 0.1, "connectors do not close: %.4f mm" % (1000 * max(gaps))
assert abs(pitch) < 1.0 and abs(roll) < 1.0, "not upright"
assert not lim, "a passive joint is on its limit: %s" % lim
# The measured stance is not perfectly symmetric (left 0.222/0.097 vs right 0.230/0.117),
# which leaves the higher wheel ~1.2 mm off the floor; the robot rolls 0.3 deg to pick it
# up.  Tolerate that instead of pretending the stance is symmetric.
assert max(abs(x) for x in wb) < 3e-3, "wheels too far off the floor: %s" % wb
json.dump(res, open(os.path.join(ROOT, "docs/audit/stand_keyframe.json"), "w"), indent=1)
print("wrote docs/audit/stand_keyframe.json (analytic, upright, closed)")
