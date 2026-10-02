import io
F=r"D:\claude2\fangzhen\scripts\hop_control_law.py"
src=io.open(F,encoding="utf-8").read()
old = "m = mujoco.MjModel.from_xml_path(XML)\nd = mujoco.MjData(m)\nm.opt.timestep = DT\n"
new = ("m = mujoco.MjModel.from_xml_path(XML)\n"
       "d = mujoco.MjData(m)\n"
       "m.opt.timestep = DT\n"
       "# Match the TRAINING solver regime, not just the plant.  env_cfgs.py builds the task with\n"
       "# timestep 0.002, iterations 10, ls_iterations 10, impratio 50, cone elliptic; the MJCF\n"
       "# ships iterations=100 / impratio=1 / pyramidal.  With six <connect> equalities those two\n"
       "# regimes are materially different plants, which is why the harness disagreed with mjlab.\n"
       "if os.environ.get(\"RM_HARNESS_TRAIN_SOLVER\", \"1\") == \"1\":\n"
       "    m.opt.iterations = 10\n"
       "    m.opt.ls_iterations = 10\n"
       "    m.opt.impratio = 50.0\n"
       "    m.opt.cone = mujoco.mjtCone.mjCONE_ELLIPTIC\n")
assert src.count(old)==1
io.open(F,"w",encoding="utf-8").write(src.replace(old,new))
print("harness5 patched (training solver regime)")