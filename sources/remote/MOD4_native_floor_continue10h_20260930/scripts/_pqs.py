import io, ast, os, shutil, glob
# --- 1) mjlab robot_cfg: split hip/knee effort, wheel 10 Nm
p = r"D:/claude2/fangzhen/train/rmvehicle/src/rmvehicle/robot_cfg.py"
t = io.open(p, encoding="utf-8").read()
t = t.replace("""LEG_KP, LEG_KD, LEG_EFFORT = 60.0, 2.0, 30.0
DAMPING_WHEEL, WHEEL_EFFORT = 1.5, 8.0""",
"""# Torque budget taken from the SJTU serial-leg note: a DM8009P16 gives ~24 Nm at the
# hip (direct sprocket) and the 0.1134/0.21 = 0.54 similar-linkage multiplies the knee
# by 1.85x, budgeted at 30 Nm.  Wheel limit matches the wheelbipe deployment (+-10 Nm).
HIP_KP, HIP_KD, HIP_EFFORT = 60.0, 2.0, 24.0
KNEE_KP, KNEE_KD, KNEE_EFFORT = 60.0, 2.0, 30.0
LEG_KP, LEG_KD, LEG_EFFORT = HIP_KP, HIP_KD, KNEE_EFFORT   # back-compat
DAMPING_WHEEL, WHEEL_EFFORT = 1.5, 10.0""")
t = t.replace("""LEG_PATTERNS = (r"^(hip|knee)_(L|R)_joint$",)""",
              """HIP_PATTERNS = (r"^hip_(L|R)_joint$",)
KNEE_PATTERNS = (r"^knee_(L|R)_joint$",)
LEG_PATTERNS = (r"^(hip|knee)_(L|R)_joint$",)""")
t = t.replace("""LEG_ACTUATOR_CFG = BuiltinPositionActuatorCfg(
  target_names_expr=LEG_PATTERNS,
  stiffness=LEG_KP, damping=LEG_KD, effort_limit=LEG_EFFORT,
)""",
"""HIP_ACTUATOR_CFG = BuiltinPositionActuatorCfg(
  target_names_expr=HIP_PATTERNS,
  stiffness=HIP_KP, damping=HIP_KD, effort_limit=HIP_EFFORT,
)
KNEE_ACTUATOR_CFG = BuiltinPositionActuatorCfg(
  target_names_expr=KNEE_PATTERNS,
  stiffness=KNEE_KP, damping=KNEE_KD, effort_limit=KNEE_EFFORT,
)""")
t = t.replace("actuators=(LEG_ACTUATOR_CFG, WHEEL_ACTUATOR_CFG)",
              "actuators=(HIP_ACTUATOR_CFG, KNEE_ACTUATOR_CFG, WHEEL_ACTUATOR_CFG)")
io.open(p, "w", encoding="utf-8", newline="\n").write(t); ast.parse(t)
print("robot_cfg: hip/knee/wheel efforts 24/30/10")

# --- 2) refresh the trained model assets
src = r"D:/claude2/fangzhen/robot/out"
dst = r"D:/claude2/fangzhen/train/rmvehicle/src/rmvehicle/assets"
shutil.copy2(os.path.join(src, "rm_vehicle.xml"), os.path.join(dst, "rm_vehicle.xml"))
msh = os.path.join(dst, "meshes")
idx = __import__("json").load(open(os.path.join(src, "mesh_index.json"), encoding="utf-8"))
keep = {f for v in idx.values() for f in v["files"]}
for f in os.listdir(msh):
    if f not in keep:
        os.remove(os.path.join(msh, f))
for f in keep:
    shutil.copy2(os.path.join(src, "meshes", f), os.path.join(msh, f))
print("assets refreshed:", len(keep), "meshes")

# --- 3) deployment config: same torque budget
p3 = r"D:/claude2/fangzhen/scripts/export_sim2sim.py"
t3 = io.open(p3, encoding="utf-8").read()
t3 = t3.replace('ACT_LEG = dict(kp=60.0, kd=2.0, effort=30.0, scale=0.5)',
                'ACT_HIP = dict(kp=60.0, kd=2.0, effort=24.0, scale=0.5)\n'
                'ACT_KNEE = dict(kp=60.0, kd=2.0, effort=30.0, scale=0.5)\n'
                'ACT_LEG = ACT_KNEE   # default when a joint is neither')
t3 = t3.replace('ACT_WHL = dict(kp=0.0, kd=1.5, effort=8.0, scale=10.0)',
                'ACT_WHL = dict(kp=0.0, kd=1.5, effort=10.0, scale=10.0)')
t3 = t3.replace("""    for jn in CONTRACT_JOINTS:
        wheel, spring = "wheel" in jn, "spring" in jn
        a = ACT_WHL if wheel else ACT_LEG""",
"""    for jn in CONTRACT_JOINTS:
        wheel, spring = "wheel" in jn, "spring" in jn
        a = ACT_WHL if wheel else (ACT_HIP if "front1" in jn else ACT_KNEE)""")
t3 = t3.replace("""    "joint_stiffness": [60.0, 60.0, 60.0, 60.0, 0.0, 0.0, 0.0, 0.0],""",
                """    "joint_stiffness": [60.0, 60.0, 60.0, 60.0, 0.0, 0.0, 0.0, 0.0],""")
t3 = t3.replace("""      joint_output_max: %s
      joint_output_min: %s""", """      joint_output_max: %s
      joint_output_min: %s""")
t3 = t3.replace("""arr([ACT_LEG["effort"]] * 4 + [ACT_WHL["effort"]] * 2 + [50.0] * 2),
       arr([-ACT_LEG["effort"]] * 4 + [-ACT_WHL["effort"]] * 2 + [-50.0] * 2),""",
"""arr([24.0, 30.0, 24.0, 30.0] + [ACT_WHL["effort"]] * 2 + [50.0] * 2),
       arr([-24.0, -30.0, -24.0, -30.0] + [-ACT_WHL["effort"]] * 2 + [-50.0] * 2),""")
io.open(p3, "w", encoding="utf-8", newline="\n").write(t3); ast.parse(t3)
print("export_sim2sim: per-joint effort budget")
