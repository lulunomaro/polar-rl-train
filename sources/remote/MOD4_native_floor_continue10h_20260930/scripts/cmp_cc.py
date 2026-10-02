import mujoco, numpy as np
for tag, x in (("SJTU reference", r"D:/claude2/fangzhen/refs/wheelbipe_ros2_sim2sim-main/src/resources/robot_descriptions/wheelbipeV14_2/mjcf/scene.xml"),
               ("ours", r"D:/claude2/fangzhen/robot/out_cc/scene_cc.xml")):
    m = mujoco.MjModel.from_xml_path(x); d = mujoco.MjData(m)
    bad = -1
    for i in range(6000):
        mujoco.mj_step(m, d)
        if not np.isfinite(d.qpos).all():
            bad = i; break
    print("%-14s nq=%d nv=%d nu=%d neq=%d mass=%.2f solver=%d iter=%d dt=%g -> %s z=%.4f"
          % (tag, m.nq, m.nv, m.nu, m.neq, sum(m.body_mass), m.opt.solver, m.opt.iterations,
             m.opt.timestep, ("NaN@%d" % bad) if bad >= 0 else "6s STABLE", d.qpos[2]))
    print("   eq_solref0:", np.round(m.eq_solref[0], 4), " eq_solimp0:", np.round(m.eq_solimp[0], 5))
    names = [mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, j) for j in range(m.njnt)]
    for j in range(m.njnt):
        k = m.jnt_dofadr[j]
        print("     %-24s arm=%-8.4f damp=%-7.3f fric=%-6.3f mass_of_body=%.4f"
              % (names[j], m.dof_armature[k], m.dof_damping[k], m.dof_frictionloss[k],
                 m.body_mass[m.jnt_bodyid[j]]))
