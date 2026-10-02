"""Emit a wheelbipe_ros2_sim2sim compatible description of our STEP-derived robot.

The deployment framework fixes a contract (PARAMETERS.md sections 2/3/9/11):

  * eight ros2_control joints, in this order:
      left_front1, left_rear1, right_front1, right_rear1,
      left_wheel, right_wheel, left_spring2, right_spring2
  * MuJoCo body ``base_link``, sensors ``imu``/``gyro``/``accelerometer``
  * effort applied through ``qfrc_applied`` (the MJCF therefore needs no <actuator>)
  * obs float32[1,35] -> actions float32[1,6], policy at 50 Hz, control at 500 Hz

Our robot has six actuators (hip/knee/wheel per side) and no gas spring, so the two
spring slots become inert locked slide joints, and the leg joints are renamed:

  hip_L -> left_front1     knee_L -> left_rear1
  hip_R -> right_front1    knee_R -> right_rear1
  wheel_L -> left_wheel    wheel_R -> right_wheel

Outputs (under --out):
  mjcf/rm_vehicle.xml, mjcf/scene.xml, meshes/*.STL
  xacro/description.xacro, xacro/ros2control.xacro, xacro/robot_sim.xacro
  config/rm_vehicle.yaml
"""
import argparse, json, os, shutil
import numpy as np
import yaml

ap = argparse.ArgumentParser()
ap.add_argument("--spec", default=r"D:/claude2/fangzhen/robot/vehicle.spec.yaml")
ap.add_argument("--physics", default=r"D:/claude2/fangzhen/robot/out/link_physics.json")
ap.add_argument("--mesh-src", default=r"D:/claude2/fangzhen/robot/out/meshes")
ap.add_argument("--out", default=r"D:/claude2/fangzhen/sim2sim/rm_vehicle")
ap.add_argument("--prefix", default="rm_vehicle")
args = ap.parse_args()

spec = yaml.safe_load(open(args.spec, encoding="utf-8-sig"))
phys = json.load(open(args.physics, encoding="utf-8"))

# ---------------------------------------------------------------- contract naming
LINK_MAP = {"base": "base_link", "thigh_L": "left_front1_link", "shank_L": "left_rear1_link",
            "wheel_L": "left_wheel_link", "thigh_R": "right_front1_link",
            "shank_R": "right_rear1_link", "wheel_R": "right_wheel_link"}
JOINT_MAP = {"hip_L_joint": "left_front1_joint", "knee_L_joint": "left_rear1_joint",
             "hip_R_joint": "right_front1_joint", "knee_R_joint": "right_rear1_joint",
             "wheel_L_joint": "left_wheel_joint", "wheel_R_joint": "right_wheel_joint"}
CONTRACT_JOINTS = ["left_front1_joint", "left_rear1_joint", "right_front1_joint",
                   "right_rear1_joint", "left_wheel_joint", "right_wheel_joint",
                   "left_spring2_joint", "right_spring2_joint"]
LEG4 = ["left_front1_joint", "left_rear1_joint", "right_front1_joint", "right_rear1_joint"]
WHEEL2 = ["left_wheel_joint", "right_wheel_joint"]
SPRING2 = ["left_spring2_joint", "right_spring2_joint"]
STAND_Z = 0.075   # wheel radius + 2 mm

mj = os.path.join(args.out, "mjcf")
me = os.path.join(args.out, "meshes")
xc = os.path.join(args.out, "xacro")
cf = os.path.join(args.out, "config")
for d in (mj, me, xc, cf):
    os.makedirs(d, exist_ok=True)
for f in os.listdir(me):
    os.remove(os.path.join(me, f))
USED = [m for v in phys.values() for m in v["mesh"]]
for f in sorted(os.listdir(args.mesh_src)):
    if f.endswith(".stl") and f in USED:
        shutil.copy2(os.path.join(args.mesh_src, f),
                     os.path.join(me, f[:-4] + ".STL"))

def f3(v):
    return " ".join("%.6g" % x for x in np.atleast_1d(v))

# ---------------------------------------------------------------- MJCF
links = {lk["name"]: lk for lk in spec["links"]}
children = {}
for j in spec["joints"]:
    children[j["parent"]] = children.get(j["parent"], []) + [j["child"]]

out = ['<mujoco model="%s_sim2sim">' % args.prefix,
       '  <compiler angle="radian" autolimits="true" '
       'balanceinertia="true" inertiafromgeom="false"/>',
       '  <option timestep="0.001" integrator="Euler" solver="Newton" iterations="100" '
       'tolerance="1e-8"/>',
       '  <default><geom condim="3" friction="1.2 0.01 0.001" solref="0.005 1" '
       'solimp="0.99 0.999 1e-5"/></default>',
       '  <asset>']
for name, v in phys.items():
    for m in v["mesh"]:
        out.append('    <mesh name="%s" file="../meshes/%s" scale="0.001 0.001 0.001"/>'
                   % (m[:-4] + ".STL", m[:-4] + ".STL"))
out.append('  </asset>')
out.append('  <worldbody>')

def emit(name, depth, parent_anchor):
    v, lk = phys[name], links[name]
    j = next((x for x in spec["joints"] if x["child"] == name), None)
    pad = "  " * depth
    anchor = np.array(lk["anchor"], float) / 1000.0
    body = LINK_MAP[name]
    if j is None:
        # The deployment has no keyframe: the root must start with the wheels on
        # the ground, otherwise MuJoCo ejects the robot on the first step.
        start = anchor + np.array([0.0, 0.0, STAND_Z])
        out.append('%s<body name="%s" pos="%s">' % (pad, body, f3(start)))
        out.append('%s  <freejoint name="floating_base"/>' % pad)
        # The IMU site MUST live on the base body: the deployment reads the sensors
        # named imu/gyro/accelerometer and a worldbody site would report a constant
        # identity pose, which silently blinds the policy.
        out.append('%s  <site name="imu" pos="0 0 0.3" size="0.01"/>' % pad)
    else:
        out.append('%s<body name="%s" pos="%s">' % (pad, body, f3(anchor - parent_anchor)))
        e = j["effort"]
        rng = j.get("range")
        extra = ' range="%s"' % f3(rng) if rng else ""
        out.append('%s  <joint name="%s" type="hinge" pos="0 0 0" axis="%s"%s '
                   'damping="%g" armature="%g" frictionloss="%g" limited="%s"/>'
                   % (pad, JOINT_MAP[j["name"]], f3(j["axis"]), extra,
                      j.get("damping", 0.0), j.get("armature", 0.0),
                      j.get("frictionloss", 0.0), "true" if rng else "false"))
        # effort is injected through qfrc_applied by mujoco_ros2_control, so the MJCF
        # deliberately carries no <actuator> block.
    com = np.array(v["com_mm"], float) / 1000.0 - anchor
    I = np.array(v["inertia_kg_m2"], float)
    out.append('%s  <inertial pos="%s" mass="%.4f" fullinertia="%s"/>'
               % (pad, f3(com), v["mass"], f3([I[0, 0], I[1, 1], I[2, 2],
                                               I[0, 1], I[0, 2], I[1, 2]])))
    for m in v["mesh"]:
        out.append('%s    <geom type="mesh" contype="0" conaffinity="0" group="2" '
                   'mesh="%s.STL" rgba="0.72 0.72 0.75 1"/>' % (pad, m[:-4]))
    if name.startswith("wheel"):
        side = "left" if name.endswith("L") else "right"
        out.append('%s    <geom name="%s_wheel_link_collision" type="cylinder" size="0.073 0.013" '
                   'quat="0.5 -0.5 0.5 0.5" contype="0" conaffinity="1" priority="1" '
                   'condim="6" group="1" rgba="0 0 0 0"/>' % (pad, side))
    elif name == "base":
        out.append('%s    <geom name="base_collision" type="box" size="0.357 0.196 0.1145" '
                   'pos="0 0 0.1685" contype="0" conaffinity="1" group="1" rgba="0 0 0 0"/>' % pad)
    else:
        r = 0.05 if name.startswith("thigh") else 0.038
        lk2 = links[name]
        cg = lk2["collision"]
        cg = cg[0] if isinstance(cg, list) else cg
        a = np.array(cg["from"], float) / 1000.0
        b = np.array(cg["to"], float) / 1000.0
        out.append('%s    <geom name="%s_collision" type="capsule" size="%g" fromto="%s %s" '
                   'contype="0" conaffinity="1" group="1" rgba="0 0 0 0"/>'
                   % (pad, LINK_MAP[name].replace("_link", ""), r, f3(a), f3(b)))
    for c in children.get(name, []):
        emit(c, depth + 1, anchor)
    if name.startswith("shank"):        # inert placeholder for the two spring slots
        side = "left" if name.endswith("L") else "right"
        out.append('%s  <body name="%s_spring2_link" pos="0 0 -0.02">' % (pad, side))
        out.append('%s    <joint name="%s_spring2_joint" type="slide" pos="0 0 0" '
                   'axis="0 0 1" range="-0.001 0.001" damping="200" '
                   'frictionloss="0" armature="0.001"/>' % (pad, side))
        out.append('%s    <inertial pos="0 0 0" mass="0.001" diaginertia="1e-6 1e-6 1e-6"/>' % pad)
        out.append('%s  </body>' % pad)
    out.append(pad + "</body>")

emit("base", 2, np.zeros(3))
out.append('  </worldbody>')
out.append('  <sensor>')
out.append('    <framequat name="imu" objtype="site" objname="imu"/>')
out.append('    <gyro name="gyro" site="imu"/>')
out.append('    <accelerometer name="accelerometer" site="imu"/>')
out.append('  </sensor>')
out.append('</mujoco>')
open(os.path.join(mj, "rm_vehicle.xml"), "w", encoding="utf-8").write("\n".join(out) + "\n")

sc = ['<?xml version="1.0" encoding="utf-8"?>', '<mujoco model="rm_vehicle scene">',
      '  <include file="rm_vehicle.xml"/>',
      '  <statistic center="0 0 0.4" extent="0.8"/>',
      '  <visual><headlight diffuse="0.6 0.6 0.6" ambient="0.1 0.1 0.1" '
      'specular="0.9 0.9 0.9"/><global azimuth="-140" elevation="-20"/></visual>',
      '  <asset><texture type="skybox" builtin="flat" rgb1="0 0 0" rgb2="0 0 0" '
      'width="512" height="3072"/>',
      '    <texture type="2d" name="groundplane" builtin="checker" mark="edge" '
      'rgb1="0.2 0.3 0.4" rgb2="0.1 0.2 0.3" markrgb="0.8 0.8 0.8" width="300" '
      'height="300"/>',
      '    <material name="groundplane" texture="groundplane" texuniform="true" '
      'texrepeat="5 5" reflectance="0.2"/></asset>',
      '  <worldbody><light pos="1 0 3.5" dir="0 0 -1" directional="true"/>',
      '    <geom name="floor" size="0 0 0.05" type="plane" material="groundplane" '
      'friction="1 0.01 0.01"/></worldbody>', '</mujoco>']
open(os.path.join(mj, "scene.xml"), "w", encoding="utf-8").write("\n".join(sc) + "\n")
print("wrote MJCF")


# ---------------------------------------------------------------- URDF (ros2_control host)
ACT_HIP = dict(kp=60.0, kd=2.0, effort=24.0, scale=0.5)
ACT_KNEE = dict(kp=60.0, kd=2.0, effort=30.0, scale=0.5)
ACT_LEG = ACT_KNEE   # default when a joint is neither
ACT_WHL = dict(kp=0.0, kd=1.5, effort=10.0, scale=10.0)

u = ['<?xml version="1.0"?>', '<robot name="%s">' % args.prefix]
u.append('  <link name="world"/>')
u.append('  <joint name="fixed_base" type="fixed"><parent link="world"/>'
         '<child link="base_link"/><origin xyz="0 0 %.3f"/></joint>' % (STAND_Z + 0.2121))

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
             '<dynamics damping="200" friction="0"/></joint>')
u.append('  <link name="imu_link"><inertial><mass value="0.01"/><inertia ixx="1e-6" '
         'ixy="0" ixz="0" iyy="1e-6" iyz="0" izz="1e-6"/></inertial></link>')
u.append('  <joint name="imu_joint" type="fixed"><parent link="base_link"/>'
         '<child link="imu_link"/><origin xyz="0 0 0.3"/></joint>')

# ---- URDF body finished; the ros2_control block is appended below
u.append("</robot>")
BODY = list(u)

open(os.path.join(xc, "robot_sim.xacro"), "w", encoding="utf-8").write("\n".join(u) + "\n")

# ---- controller-manager config
def arr(vals):
    # ROS parameter files require homogeneous sequences: always emit doubles.
    return "[" + ", ".join("%.6f" % float(x) for x in vals) + "]"
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
""" + "".join("        - %s\n" % n for n in CONTRACT_JOINTS) + """      command_interfaces:
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
       arr([24.0, 30.0, 24.0, 30.0] + [ACT_WHL["effort"]] * 2 + [50.0] * 2),
       arr([-24.0, -30.0, -24.0, -30.0] + [-ACT_WHL["effort"]] * 2 + [-50.0] * 2),
       arr([0.0] * 8), arr([0.0] * 8), arr([0.0] * 4))
open(os.path.join(cf, "rm_vehicle.yaml"), "w", encoding="utf-8").write(y)

# ---------------------------------------------------------------- ros2_control blocks
def ros2control_block(plugin, with_dt7):
    r = ['  <ros2_control name="RmVehicleControl" type="system">',
         '    <hardware>',
         '      <plugin>%s</plugin>' % plugin]
    if with_dt7:
        r.append('      <param name="serial_port">/dev/wheelbipe_h7</param>')
        r.append('      <param name="baudrate">2000000</param>')
        r.append('      <param name="serial_reconnect_interval_ms">1000</param>')
        r.append('      <param name="state_timeout_ms">100</param>')
    r.append('    </hardware>')
    for jn in CONTRACT_JOINTS:
        wheel, spring = "wheel" in jn, "spring" in jn
        a = ACT_WHL if wheel else (ACT_HIP if "front1" in jn else ACT_KNEE)
        lo, hi = (-5.0, 5.0) if spring else (-a["effort"], a["effort"])
        r.append('    <joint name="%s">' % jn)
        for ci in ("position", "velocity"):
            r.append('      <command_interface name="%s"/>' % ci)
        r.append('      <command_interface name="effort">'
                 '<param name="min">%.1f</param><param name="max">%.1f</param>'
                 '</command_interface>' % (lo, hi))
        r.append('      <command_interface name="kp"/>')
        r.append('      <command_interface name="kd"/>')
        r.append('      <state_interface name="position">'
                 '<param name="initial_value">0.0</param></state_interface>')
        for si in ("velocity", "effort"):
            r.append('      <state_interface name="%s"/>' % si)
        r.append('    </joint>')
    r.append('    <sensor name="imu">')
    for s in ("orientation.w", "orientation.x", "orientation.y", "orientation.z",
              "angular_velocity.x", "angular_velocity.y", "angular_velocity.z",
              "linear_acceleration.x", "linear_acceleration.y", "linear_acceleration.z"):
        r.append('      <state_interface name="%s"/>' % s)
    r.append('    </sensor>')
    if with_dt7:
        r.append('    <sensor name="dt7">')
        for s in ("cmd_state", "cmd_vel_x", "cmd_omega_z", "cmd_height"):
            r.append('      <state_interface name="%s"/>' % s)
        r.append('    </sensor>')
    r.append('  </ros2_control>')
    return r


def write_robot(path, plugin, with_dt7):
    lines = BODY[:-1] + ros2control_block(plugin, with_dt7) + ["</robot>"]
    open(path, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("wrote", path)


write_robot(os.path.join(xc, "robot_sim.xacro"), "mujoco_ros2_control/MujocoSystem", False)
write_robot(os.path.join(xc, "robot_real.xacro"), "template_real_ros2_ctrl::RealBridge", True)

print("wrote xacros and config/rm_vehicle.yaml")
