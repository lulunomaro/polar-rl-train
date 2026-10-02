import io,ast
p=r"D:/claude2/fangzhen/scripts/export_sim2sim.py"
t=io.open(p,encoding="utf-8").read()
t=t.replace('    com = v["com"] / 1000.0 - anchor','    com = np.array(v["com_mm"], float) / 1000.0 - anchor')
t=t.replace('''    I = np.array(v["inertia_kg_m2"] if "inertia_kg_m2" in v else
                 (np.array(v["inertia"]) / 1e6))''','    I = np.array(v["inertia_kg_m2"], float)')
t=t.replace("""        out.append('%s  <position joint="%s" kp="1" ctrlrange="-%g %g" forcerange="-%g %g"/>'
                   % (pad, JOINT_MAP[j["name"]], e, e, e, e))
""","""        # effort is injected through qfrc_applied by mujoco_ros2_control, so the MJCF
        # deliberately carries no <actuator> block.
""")
io.open(p,"w",encoding="utf-8").write(t); ast.parse(t); print("ok")
