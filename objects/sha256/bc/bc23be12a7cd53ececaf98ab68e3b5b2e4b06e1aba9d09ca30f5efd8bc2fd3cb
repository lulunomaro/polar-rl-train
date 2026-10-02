import io
p = r"D:/claude2/fangzhen/scripts/export_sim2sim.py"
t = io.open(p, encoding="utf-8").read()
tail = '''

# ---------------------------------------------------------------- URDF (ros2_control host)
ACT_LEG = dict(kp=60.0, kd=2.0, effort=30.0, scale=0.5)
ACT_WHL = dict(kp=0.0, kd=1.5, effort=8.0, scale=10.0)

u = ['<?xml version="1.0"?>', '<robot name="%s">' % args.prefix]
u.append('  <link name="world"/>')
u.append('  <joint name="fixed_base" type="fixed"><parent link="world"/>'
         '<child link="base_link"/><origin xyz="0 0 0.6"/></joint>')

def emit_link(name):
    v, lk = phys[name], links[name]
    body = LINK_MAP[name]
    anchor = np.array(lk["anchor"], float) / 1000.0
    j = next((x for x in spec["joints"] if x["child"] == name), None)
    if j is None:
        parent, pxyz = "base_link" if False else None, None
    com = np.array(v["com_mm"], float) / 1000.0 - anchor
    I = np.array(v["inertia_kg_m2"], float)
    u.append('  <link name="%s">' % body)
    u.append('    <inertial><origin xyz="%s" rpy="0 0 0"/><mass value="%.4f"/>'
             '<inertia ixx="%.6f" ixy="%.6f" ixz="%.6f" iyy="%.6f" iyz="%.6f" '
             'izz="%.6f"/></inertial>'
             % (f3(com), v["mass"], I[0, 0], I[0, 1], I[0, 2], I[1, 1], I[1, 2], I[2, 2]))
    for m in v["mesh"]:
        u.append('    <visual><geometry><mesh filename="package://robot_descriptions/%s/'
                 'meshes/%s.STL" scale="0.001 0.001 0.001"/></geometry></visual>'
                 % (args.prefix, m[:-4]))
    u.append('    <collision><origin xyz="0 0 0"/><geometry><box size="0.02 0.02 0.02"/>'
             '</geometry></collision>' if False else '')
    u.append('  </link>')
    if j is not None:
        pa = np.array(links[j["parent"]]["anchor"], float) / 1000.0
        jn = JOINT_MAP[j["name"]]
        wheel = j.get("class") == "wheel"
        a = ACT_WHL if wheel else ACT_LEG
        rng = j.get("range") or [-6.28, 6.28]
        u.append('  <joint name="%s" type="revolute">' % jn)
        u.append('    <parent link="%s"/><child link="%s"/>' % (LINK_MAP[j["parent"]], body))
        u.append('    <origin xyz="%s" rpy="0 0 0"/><axis xyz="%s"/>'
                 % (f3(anchor - pa), f3(j["axis"])))
        u.append('    <limit lower="%.4f" upper="%.4f" effort="%.2f" velocity="40"/>'
                 '<dynamics damping="%.4f" friction="%.4f"/>'
                 % (rng[0], rng[1], a["effort"], j.get("damping", 0.0),
                    j.get("frictionloss", 0.0)))
        u.append('  </joint>')
    for c in children.get(name, []):
        emit_link(c)

emit_link("base")
for side in ("left", "right"):
    u.append('  <link name="%s_spring2_link"><inertial><mass value="0.001"/>'
             '<inertia ixx="1e-6" ixy="0" ixz="0" iyy="1e-6" iyz="0" izz="1e-6"/>'
             '</inertial></link>' % side)
    u.append('  <joint name="%s_spring2_joint" type="prismatic">' % side)
    u.append('    <parent link="%s_rear1_link"/><child link="%s_spring2_link"/>'
             % (side, side))
    u.append('    <origin xyz="0 0 -0.02"/><axis xyz="0 0 1"/>')
    u.append('    <limit lower="-0.001" upper="0.001" effort="50" velocity="0.01"/>'
             '<dynamics damping="2000" friction="0"/></joint>')
u.append('  <link name="imu_link"><inertial><mass value="0.01"/><inertia ixx="1e-6" '
         'ixy="0" ixz="0" iyy="1e-6" iyz="0" izz="1e-6"/></inertial></link>')
u.append('  <joint name="imu_joint" type="fixed"><parent link="base_link"/>'
         '<child link="imu_link"/><origin xyz="0 0 0.3"/></joint>')

# ---- ros2_control block
u.append('  <ros2_control name="RmVehicleControl" type="system">')
u.append('    <hardware><plugin>mujoco_ros2_control/MujocoSystem</plugin></hardware>')
for jn in CONTRACT_JOINTS:
    wheel = "wheel" in jn
    spring = "spring" in jn
    a = ACT_WHL if wheel else ACT_LEG
    lo, hi = (-5.0, 5.0) if spring else (-a["effort"], a["effort"])
    u.append('    <joint name="%s">' % jn)
    u.append('      <command_interface name="position"/>')
    u.append('      <command_interface name="velocity"/>')
    u.append('      <command_interface name="effort">'
             '<param name="min">%.1f</param><param name="max">%.1f</param>'
             '</command_interface>' % (lo, hi))
    u.append('      <command_interface name="kp"/><command_interface name="kd"/>')
    u.append('      <state_interface name="position"><param name="initial_value">0.0'
             '</param></state_interface>')
    u.append('      <state_interface name="velocity"/><state_interface name="effort"/>')
    u.append('    </joint>')
u.append('    <sensor name="imu">')
for k in ("orientation.w", "orientation.x", "orientation.y", "orientation.z",
          "angular_velocity.x", "angular_velocity.y", "angular_velocity.z",
          "linear_acceleration.x", "linear_acceleration.y", "linear_acceleration.z"):
    u.append('      <state_interface name="%s"/>' % k)
u.append('    </sensor>')
u.append('  </ros2_control>')
u.append('</robot>')
open(os.path.join(xc, "robot_sim.xacro"), "w", encoding="utf-8").write("\\n".join(u) + "\\n")

# ---- controller-manager config
def arr(vals):
    return "[" + ", ".join("%g" % x for x in vals) + "]"
y = """# ros2_control configuration for the STEP-derived dual wheel-leg robot.
# Joint order is the fixed eight-joint contract of wheelbipe_ros2_sim2sim.

/**:
  controller_manager:
    ros__parameters:
      update_rate: 500
      joint_state_broadcaster:
        type: joint_state_broadcaster/JointStateBroadcaster
      template_ros2_controller:
        type: robot_locomotion/TemplateRos2Controller

  joint_state_broadcaster:
    ros__parameters:
      update_rate: 500

  template_ros2_controller:
    ros__parameters:
      update_rate: 500
      joints:
""" + "".join("        - %s\\n" % n for n in CONTRACT_JOINTS) + """      command_interfaces:
        - position
        - velocity
        - effort
        - kp
        - kd
      state_interfaces:
        - position
        - velocity
        - effort
      sensors:
        - imu
      joint_stiffness: %s
      joint_damping: %s
      joint_action_scale: %s
      joint_output_max: %s
      joint_output_min: %s
      default_dof_pos: %s
      joint_bias: %s
      prepare_dof_pos: %s
      prepare_kp: [60.0, 60.0, 60.0, 60.0]
      prepare_kd: [2.0, 2.0, 2.0, 2.0]
      motion_linear_x_min: -1.0
      motion_linear_x_max: 1.8
      motion_angular_z_min: -1.0
      motion_angular_z_max: 1.0
      default_command_height: 0.22
      command_height_min: 0.18
      command_height_max: 0.34
      rl_inference_frequency: 50
      lowlevel_output_mode: "hardware_pd_vel"
""" % (arr([ACT_LEG["kp"]] * 4 + [0.0] * 4),
       arr([ACT_LEG["kd"]] * 4 + [ACT_WHL["kd"]] * 2 + [0.0] * 2),
       arr([ACT_LEG["scale"]] * 4 + [ACT_WHL["scale"]] * 2 + [0.0] * 2),
       arr([ACT_LEG["effort"]] * 4 + [ACT_WHL["effort"]] * 2 + [50.0] * 2),
       arr([-ACT_LEG["effort"]] * 4 + [-ACT_WHL["effort"]] * 2 + [-50.0] * 2),
       arr([0.0] * 8), arr([0.0] * 8), arr([0.0] * 4))
open(os.path.join(cf, "rm_vehicle.yaml"), "w", encoding="utf-8").write(y)
print("wrote xacro/robot_sim.xacro and config/rm_vehicle.yaml")
'''
t = t + tail
io.open(p, "w", encoding="utf-8").write(t)
import ast; ast.parse(t); print("appended")
