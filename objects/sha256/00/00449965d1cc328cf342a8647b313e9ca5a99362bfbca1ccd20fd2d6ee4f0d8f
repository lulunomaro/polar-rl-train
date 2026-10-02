"""Why does the DEPLOYMENT plant throw the robot when the training plant does not?

The two MJCF files look identical wherever I read them by eye, so compare every
physics-relevant array of the COMPILED models positionally and print what differs.
"""
import mujoco
import numpy as np
ROOT = r"D:/claude2/fangzhen"
A = mujoco.MjModel.from_xml_path(ROOT + r"/robot/out_cc/scene_cc.xml")
B = mujoco.MjModel.from_xml_path(ROOT + r"/sim2sim_cc/rm_vehicle/mjcf/scene.xml")
BO = mujoco.mjtObj
nm = lambda m, o, i: (mujoco.mj_id2name(m, o, i) or "#%d" % i)


def cmp(label, x, y, keys=None):
    x = np.asarray(x, float); y = np.asarray(y, float)
    if x.shape != y.shape:
        print("%-24s SHAPE %s vs %s" % (label, x.shape, y.shape)); return
    d = np.abs(x - y)
    n = int((d.reshape(len(x), -1).max(axis=1) > 1e-6).sum()) if x.ndim else int(d > 1e-6)
    print("%-24s entries differ: %d" % (label, n))
    if n:
        for i in range(len(x)):
            if np.abs(x[i] - y[i]).max() > 1e-6:
                k = keys[i] if keys else i
                print("     %-38s train %s   deploy %s"
                      % (k, np.round(np.asarray(x[i]).ravel(), 5),
                         np.round(np.asarray(y[i]).ravel(), 5)))


jn = [nm(A, BO.mjOBJ_JOINT, i) for i in range(A.njnt)]
gn = [nm(A, BO.mjOBJ_GEOM, i) for i in range(A.ngeom)]
gn_b = [nm(B, BO.mjOBJ_GEOM, i) for i in range(B.ngeom)]
dn = []
for i in range(A.nv):
    j = int(A.dofid2jntid[i]) if hasattr(A, "dofid2jntid") else -1
    dn.append(nm(A, BO.mjOBJ_JOINT, j) if j >= 0 else "dof%d" % i)
cmp("jnt_stiffness", A.jnt_stiffness, B.jnt_stiffness, jn)
cmp("jnt_range", A.jnt_range, B.jnt_range, jn)
cmp("dof_damping", A.dof_damping, B.dof_damping, dn)
cmp("dof_armature", A.dof_armature, B.dof_armature, dn)
cmp("dof_frictionloss", A.dof_frictionloss, B.dof_frictionloss, dn)
cmp("geom_size", A.geom_size, B.geom_size, gn)
cmp("geom_pos", A.geom_pos, B.geom_pos, gn)
cmp("geom_quat", A.geom_quat, B.geom_quat, gn)
cmp("geom_type", A.geom_type, B.geom_type, gn)
cmp("geom_group", A.geom_group, B.geom_group, gn)
cmp("geom_condim", A.geom_condim, B.geom_condim, gn)
cmp("geom_priority", A.geom_priority, B.geom_priority, gn)
cmp("geom_friction", A.geom_friction, B.geom_friction, gn)
cmp("geom_solimp", A.geom_solimp, B.geom_solimp, gn)
cmp("geom_solref", A.geom_solref, B.geom_solref, gn)
cmp("geom_contype/affinity", np.c_[A.geom_contype, A.geom_conaffinity],
    np.c_[B.geom_contype, B.geom_conaffinity], gn)
cmp("geom_bodyid", A.geom_bodyid, B.geom_bodyid, gn)
cmp("eq_data", A.eq_data, B.eq_data, [nm(A, BO.mjOBJ_EQUALITY, i) for i in range(A.neq)])
cmp("eq_obj", A.eq_obj1id, B.eq_obj1id, [nm(A, BO.mjOBJ_EQUALITY, i) for i in range(A.neq)])
cmp("eq_type", A.eq_type, B.eq_type, [nm(A, BO.mjOBJ_EQUALITY, i) for i in range(A.neq)])
print("\noption: timestep %.5f/%.5f iterations %d/%d ls %d/%d solver %d/%d cone %d/%d "
      "tolerance %.1e/%.1e impratio %.1f/%.1f gravity %.2f/%.2f"
      % (A.opt.timestep, B.opt.timestep, A.opt.iterations, B.opt.iterations,
         A.opt.ls_iterations, B.opt.ls_iterations, A.opt.solver, B.opt.solver,
         A.opt.cone, B.opt.cone, A.opt.tolerance, B.opt.tolerance,
         A.opt.impratio, B.opt.impratio, A.opt.gravity[2], B.opt.gravity[2]))
print("nkey %d/%d  qpos0 base %s / %s" % (A.nkey, B.nkey, np.round(A.qpos0[:4], 4),
                                          np.round(B.qpos0[:4], 4)))
