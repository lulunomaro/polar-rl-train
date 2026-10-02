"""At the spawn pose, which collision geoms already start BELOW the floor?

The CPU harness ejects the robot (base z: 0.075 -> -0.028 -> +0.267 within 0.5 s) the moment the
chassis box stops colliding, which is the first thing that kills the policy's observation.
An initial penetration of any of the leg capsules would explain it exactly: the solver has to
resolve it and throws the robot.
"""
import mujoco
import numpy as np
m = mujoco.MjModel.from_xml_path(r"D:/claude2/fangzhen/robot/out_cc/scene_cc.xml")
d = mujoco.MjData(m)
mujoco.mj_resetDataKeyframe(m, d, 0)
mujoco.mj_forward(m, d)
nm = lambda i: mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, i) or ""
print("spawn base z = %.4f" % d.qpos[2])
rows = []
for i in range(m.ngeom):
    if int(m.geom_group[i]) != 3:
        continue
    t = int(m.geom_type[i])
    if t == int(mujoco.mjtGeom.mjGEOM_CAPSULE):
        a, b = d.geom_xpos[i], None
        R = np.asarray(d.xmat[m.geom_bodyid[i]]).reshape(3, 3)
        lo = float(d.geom_xpos[i, 2] - (m.geom_size[i][1] * abs(R[2, 2]) + m.geom_size[i][0]))
        # conservative: centre z minus (half axis projection + radius)
        half = m.geom_size[i][1] * max(abs(R[2, 0]), abs(R[2, 1]), abs(R[2, 2])) + m.geom_size[i][0]
        lo = float(d.geom_xpos[i, 2] - half)
    elif t == int(mujoco.mjtGeom.mjGEOM_CYLINDER):
        lo = float(d.geom_xpos[i, 2] - m.geom_size[i][0])
    elif t == int(mujoco.mjtGeom.mjGEOM_BOX):
        R = np.asarray(d.xmat[m.geom_bodyid[i]]).reshape(3, 3)
        h = float(np.abs(R[2] ) @ m.geom_size[i])
        lo = float(d.geom_xpos[i, 2] - h)
    else:
        continue
    rows.append((lo, nm(i), int(m.geom_condim[i]), int(m.geom_conaffinity[i])))
rows.sort()
print("  lowest z      geom                              condim conaff")
for lo, name, cd, ca in rows[:8]:
    print("  %+8.4f   %-34s   %d     %d" % (lo, name, cd, ca))
below = [r for r in rows if r[0] < 0]
print("\ngeoms starting below the floor: %d" % len(below))
for lo, name, cd, ca in below:
    print("   %-34s %+.4f m  (conaffinity=%d)" % (name, lo, ca))
