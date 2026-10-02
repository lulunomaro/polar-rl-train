import math
import numpy as np
import mujoco
_p = print
def print(*a, **k):
    k.setdefault('flush', True)
    _p(*a, **k)

LEG = ["left_front1_joint", "left_rear1_joint", "right_front1_joint", "right_rear1_joint"]
WHL = ["left_wheel_joint", "right_wheel_joint"]
m = mujoco.MjModel.from_xml_path(r"D:/claude2/fangzhen/robot/out_cc/scene_cc.xml")
d = mujoco.MjData(m)
m.opt.timestep = 0.001
J = lambda n: mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, n)
qa = {n: m.jnt_qposadr[J(n)] for n in LEG + WHL}
va = {n: m.jnt_dofadr[J(n)] for n in LEG + WHL}
print("=== wheel collision geoms ===")
for i in range(m.ngeom):
    b = mujoco.mj_id2name(m, 1, m.geom_bodyid[i])
    if b and "wheel" in b:
        print("   %-28s type=%d size=%s group=%d contype=%d conaff=%d condim=%d" %
              (mujoco.mj_id2name(m, 5, i) or "?", m.geom_type[i], np.round(m.geom_size[i], 4),
               m.geom_group[i], m.geom_contype[i], m.geom_conaffinity[i], m.geom_condim[i]))
print("floor geom:", [(mujoco.mj_id2name(m, 5, i), m.geom_type[i], np.round(m.geom_size[i], 3))
                      for i in range(m.ngeom) if m.geom_bodyid[i] == 0])
d.qpos[:] = 0.0
d.qpos[2] = 0.075
d.qpos[3] = 1.0
tgt = {n: 0.0 for n in LEG}
wv = {n: 0.0 for n in WHL}
for k in range(4000):
    for n in LEG:
        d.qfrc_applied[va[n]] = np.clip(60.0 * (0.0 - d.qpos[qa[n]]) - 2.0 * d.qvel[va[n]], -40, 40)
    for n in WHL:
        d.qfrc_applied[va[n]] = np.clip(1.5 * (0.0 - d.qvel[va[n]]), -5.5, 5.5)
    mujoco.mj_step(m, d)
    if k in (0, 50, 200, 1000, 3999):
        ncon = d.ncon
        fz = 0.0
        cf = np.zeros((6, 1))
        for c in range(ncon):
            mujoco.mj_contactForce(m, d, c, cf)
            fz += float(abs(cf[0, 0]))
        print("  t=%4.1f ms  z=%.4f  ncon=%d  sum|fn|=%6.1f N  (weight %.1f N)  qvel_z=%+.3f" %
              (k, d.qpos[2], ncon, fz, 20.0 * 9.81, d.qvel[2]))
print("\n=== now command a wheel spin-up (what a gyro needs) ===")
for k in range(3000):
    for n in LEG:
        d.qfrc_applied[va[n]] = np.clip(60.0 * (0.0 - d.qpos[qa[n]]) - 2.0 * d.qvel[va[n]], -40, 40)
    for i, n in enumerate(WHL):
        w = 6.0 if i == 0 else -6.0
        d.qfrc_applied[va[n]] = np.clip(1.5 * (w - d.qvel[va[n]]), -5.5, 5.5)
    mujoco.mj_step(m, d)
print("  wheel rates: L=%+.2f R=%+.2f rad/s   yaw rate (body z) = %+.3f rad/s" %
      (d.qvel[va["left_wheel_joint"]], d.qvel[va["right_wheel_joint"]], d.qvel[5]))