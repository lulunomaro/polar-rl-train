import io, ast
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
    print("   eq_solref0:", np.round(m.eq_solref[0], 4), " eq_solimp0:", np.round(m.eq_solimp[0], 5))
    names = [mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, j) for j in range(m.njnt)]
    for j in range(m.njnt):
        k = m.jnt_dofadr[j]
        print("     %-24s arm=%-8.4f damp=%-7.3f fric=%-6.3f mass_of_body=%.4f"
              % (names[j], m.dof_armature[k], m.dof_damping[k], m.dof_frictionloss[k],
                 m.body_mass[m.jnt_bodyid[j]]))
""")
p = r"D:/claude2/fangzhen/scripts/build_cc.py"
t = io.open(p, encoding="utf-8").read()
t = t.replace("""       '  <option timestep="0.002" iterations="50" ls_iterations="20" integrator="Euler" '
       'solver="Newton"/>',""",
"""       '  <option timestep="0.001" iterations="100" ls_iterations="50" integrator="Euler" '
       'solver="Newton" tolerance="1e-8"/>',""")
t = t.replace("""        rng = PASSIVE_RNG.get(body, (-2.5, 2.5))
        out.append('%s  <joint name="%s_joint" type="hinge" pos="0 0 0" axis="0 1 0" '
                   'range="%s" damping="0.02" armature="0.001" frictionloss="0.1"/>'
                   % (pad, nm, f3(rng)))""",
"""        rng = PASSIVE_RNG.get(body, (-2.5, 2.5))
        out.append('%s  <joint name="%s_joint" type="hinge" pos="0 0 0" axis="0 1 0" '
                   'range="%s" damping="0.05" armature="0.01" frictionloss="0.2"/>'
                   % (pad, nm, f3(rng)))""")
t = t.replace("""'range="-0.02 0.06" damping="2.0" frictionloss="50" armature="0.001"/>'""",
              """'range="-0.02 0.06" damping="5.0" frictionloss="50" armature="0.01"/>'""")
io.open(p, "w", encoding="utf-8", newline="\n").write(t); ast.parse(t)
print("build_cc: dt=1ms, iter=100, passive armature/damping raised")
