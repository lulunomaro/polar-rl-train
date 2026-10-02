"""Load a MuJoCo model, dump its structure, and run a short free-fall sanity test."""
import sys
import numpy as np
import mujoco

path = sys.argv[1] if len(sys.argv) > 1 else r"D:/claude2/fangzhen/robot/out/scene.xml"
m = mujoco.MjModel.from_xml_path(path)
d = mujoco.MjData(m)
ntri = int(m.mesh_face.size // 3) if m.nmesh else 0
print("FILE   :", path)
print("nq=%d nv=%d nu=%d nbodey=%d ngeom=%d nmesh=%d ntri=%d nsensor=%d nkey=%d"
      % (m.nq, m.nv, m.nu, m.nbody, m.ngeom, m.nmesh, ntri, m.nsensor, m.nkey))
print("mass total = %.3f kg   timestep = %g s   gravity = %s"
      % (sum(m.body_mass), m.opt.timestep, m.opt.gravity))

print("\n-- bodies --")
for b in range(m.nbody):
    nm = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, b) or "world"
    eig = np.sort(np.linalg.eigvalsh(np.diag(m.body_inertia[b])))
    print("  %-2s %-10s m=%7.3f kg  ipos=%s  Ixyz=%s"
          % (b, nm, m.body_mass[b], np.round(m.body_ipos[b] * 1000, 1), np.round(eig, 5)))

print("\n-- joints --")
for j in range(m.njnt):
    nm = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, j)
    s, e = m.jnt_range[j]
    print("  %-2s %-14s type=%s axis=%s range=%s armature=%.4g damping=%.3g fric=%.3g"
          % (j, nm, m.jnt_type[j], np.round(m.jnt_axis[j], 2),
             ("[%.2f %.2f]" % (s, e)) if m.jnt_limited[j] else "free",
             m.dof_armature[m.jnt_dofadr[j]], m.dof_damping[j], m.dof_frictionloss[j]))

print("\n-- actuators --")
for u in range(m.nu):
    nm = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_ACTUATOR, u)
    print("  %-2s %-14s trntype=%s gain=%s ctrlrange=%s"
          % (u, nm, m.actuator_trntype[u], np.round(m.actuator_gainprm[u], 3),
             np.round(m.actuator_ctrlrange[u], 2)))

print("\n-- collision geoms (group<3) --")
for g in range(m.ngeom):
    if m.geom_group[g] != 4:
        continue
    nm = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, g) or "-"
    print("  %-2s %-14s body=%-9s type=%s size=%s pos=%s quat=%s ct=%-4d ca=%-4d mu=%s"
          % (g, nm, mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, m.geom_bodyid[g]),
             m.geom_type[g], np.round(m.geom_size[g], 4), np.round(m.geom_pos[g], 4), np.round(m.geom_quat[g], 3),
             m.geom_contype[g], m.geom_conaffinity[g],
             np.round(m.geom_friction[g], 3)))

print("\n-- meshes --")
for i in range(m.nmesh):
    nm = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_MESH, i)
    print("  %-2s %-14s vert=%d" % (i, nm, m.mesh_vertnum[i]))

print("\n-- site / body world pos @ qpos0 --")
mujoco.mj_forward(m, d)
for b in range(1, m.nbody):
    nm = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, b)
    print("  %-10s %s" % (nm, np.round(d.xpos[b], 4)))

if m.nkey:
    mujoco.mj_resetDataKeyframe(m, d, 0)
print("\nkeyframe qpos =", np.round(d.qpos, 4))
for _ in range(3000):
    mujoco.mj_step(m, d)
print("after 6 s free fall: z=%+.4f quat=%s q_joints=%s"
      % (d.qpos[2], np.round(d.qpos[3:7], 3), np.round(d.qpos[7:], 3)))
print("contacts:", [(mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, c.geom[0]),
                     mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, c.geom[1]),
                     round(float(c.dist), 4)) for c in d.contact] or "none")
print("model consistent (nq == nv+7):", m.nq == m.nv + 7)
