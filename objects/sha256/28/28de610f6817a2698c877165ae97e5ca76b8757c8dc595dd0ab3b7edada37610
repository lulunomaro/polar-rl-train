import io, ast
p = r"D:/claude2/fangzhen/scripts/export_sim2sim.py"
t = io.open(p, encoding="utf-8").read()
anchor = "print(\"wrote xacro/robot_sim.xacro and config/rm_vehicle.yaml\")"
assert anchor in t
extra = '''
# ---------------------------------------------------------------- real backend xacro
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
        a = ACT_WHL if wheel else ACT_LEG
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
    for k in ("orientation.w", "orientation.x", "orientation.y", "orientation.z",
              "angular_velocity.x", "angular_velocity.y", "angular_velocity.z",
              "linear_acceleration.x", "linear_acceleration.y", "linear_acceleration.z"):
        r.append('      <state_interface name="%s"/>' % k)
    r.append('    </sensor>')
    if with_dt7:
        r.append('    <sensor name="dt7">')
        for k in ("cmd_state", "cmd_vel_x", "cmd_omega_z", "cmd_height"):
            r.append('      <state_interface name="%s"/>' % k)
        r.append('    </sensor>')
    r.append('  </ros2_control>')
    return r


real = ['<?xml version="1.0"?>',
        '<robot xmlns:xacro="http://www.ros.org/wiki/xacro" name="%s">' % args.prefix]
real += [ln for ln in u if not ln.startswith("  <ros2_control")]
real = real[:-1]                       # drop the closing </robot> of the sim file
real += ros2control_block("template_real_ros2_ctrl::RealBridge", True)
real.append("</robot>")
open(os.path.join(xc, "robot_real.xacro"), "w", encoding="utf-8").write("\\n".join(real))

# rewrite the sim file with the shared helper (single source of truth)
sim = ['<?xml version="1.0"?>',
       '<robot xmlns:xacro="http://www.ros.org/wiki/xacro" name="%s">' % args.prefix]
sim += [ln for ln in u if not ln.startswith("  <ros2_control")]
sim = sim[:-1]
sim += ros2control_block("mujoco_ros2_control/MujocoSystem", False)
sim.append("</robot>")
open(os.path.join(xc, "robot_sim.xacro"), "w", encoding="utf-8").write("\\n".join(sim))

'''
t = t.replace(anchor, extra + anchor)
io.open(p, "w", encoding="utf-8").write(t); ast.parse(t)
print("real xacro generation added")
