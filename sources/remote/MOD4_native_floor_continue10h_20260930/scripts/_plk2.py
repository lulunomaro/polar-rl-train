import io
io.open(r"D:/claude2/fangzhen/scripts/cmp_cc.py","w",encoding="utf-8",newline="\n").write("""import mujoco, numpy as np
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
    print("   eq_sol0:", np.round(m.eq_sol[0], 4))
    print("   armature:", np.round(m.dof_armature, 4))
    print("   damping :", np.round(m.dof_damping, 3))
""")
print("ok")
