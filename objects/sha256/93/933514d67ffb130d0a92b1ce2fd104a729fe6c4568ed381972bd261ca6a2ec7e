"""Exact spawn-pose clearance of every collision geom to the floor plane (z=0)."""
import mujoco
import numpy as np
m = mujoco.MjModel.from_xml_path(r"D:/claude2/fangzhen/robot/out_cc/scene_cc.xml")
d = mujoco.MjData(m)
mujoco.mj_resetDataKeyframe(m, d, 0)
mujoco.mj_forward(m, d)
nm = lambda i: mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, i) or ""
print("spawn base z = %.4f" % d.qpos[2])
out = []
for i in range(m.ngeom):
    if int(m.geom_group[i]) != 3:
        continue
    t = int(m.geom_type[i])
    c = np.asarray(d.geom_xpos[i], float); R = np.asarray(d.geom_xmat[i], float).reshape(3, 3)
    sz = np.asarray(m.geom_size[i], float)
    if t == int(mujoco.mjtGeom.mjGEOM_CAPSULE) or t == int(mujoco.mjtGeom.mjGEOM_CYLINDER):
        ax = R[:, 2]
        z = [c[2] + ax[2] * sz[1] - sz[0], c[2] - ax[2] * sz[1] - sz[0]]
    elif t == int(mujoco.mjtGeom.mjGEOM_BOX):
        z = [c[2] - float(np.abs(R[2]) @ sz)]
    else:
        z = [c[2]]
    out.append((min(z), nm(i), int(m.geom_condim[i])))
out.sort()
for lo, name, cd in out:
    flag = "   <<< BELOW THE FLOOR" if lo < 0 else ("   <<< touching" if lo < 2e-4 else "")
    print("  z_low = %+8.5f m  %-26s condim=%d%s" % (lo, name, cd, flag))
