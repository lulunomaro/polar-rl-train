import io, ast, re
p = r"D:/claude2/fangzhen/scripts/export_sim2sim.py"
t = io.open(p, encoding="utf-8").read()
i = t.index("# ---- ros2_control block")
j = t.index('open(os.path.join(xc, "robot_sim.xacro")')
seg = t[i:j]
new = '''# ---- URDF body finished; the ros2_control block is appended below
u.append("</robot>")
BODY = list(u)

'''
t = t[:i] + new + t[j:]
# now fix the trailing generator: rebuild sim/real from BODY
k = t.index("# ---------------------------------------------------------------- real backend xacro")
tail = '''# ---------------------------------------------------------------- ros2_control blocks
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
    open(path, "w", encoding="utf-8").write("\\n".join(lines) + "\\n")
    print("wrote", path)


write_robot(os.path.join(xc, "robot_sim.xacro"), "mujoco_ros2_control/MujocoSystem", False)
write_robot(os.path.join(xc, "robot_real.xacro"), "template_real_ros2_ctrl::RealBridge", True)

'''
t = t[:k] + tail + t[t.index('print("wrote xacro/robot_sim.xacro and config/rm_vehicle.yaml")'):]
t = t.replace('print("wrote xacro/robot_sim.xacro and config/rm_vehicle.yaml")',
              'print("wrote xacros and config/rm_vehicle.yaml")')
io.open(p, "w", encoding="utf-8").write(t)
try:
    ast.parse(t); print("syntax ok")
except SyntaxError as e:
    print("SYNTAX", e)
