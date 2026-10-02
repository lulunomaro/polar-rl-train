import io, ast
p = r"D:/claude2/fangzhen/scripts/export_sim2sim.py"
t = io.open(p, encoding="utf-8").read()
a = """    if j is None:
        # The deployment has no keyframe: the root must start with the wheels on
        # the ground, otherwise MuJoCo ejects the robot on the first step.
        start = anchor + np.array([0.0, 0.0, STAND_Z])
        out.append('%s<body name="%s" pos="%s">' % (pad, body, f3(start)))
        out.append('%s  <freejoint name="floating_base"/>' % pad)"""
b = """    if j is None:
        # The deployment has no keyframe: the root must start with the wheels on
        # the ground, otherwise MuJoCo ejects the robot on the first step.
        start = anchor + np.array([0.0, 0.0, STAND_Z])
        out.append('%s<body name="%s" pos="%s">' % (pad, body, f3(start)))
        out.append('%s  <freejoint name="floating_base"/>' % pad)
        # The IMU site MUST live on the base body: the deployment reads the sensors
        # named imu/gyro/accelerometer and a worldbody site would report a constant
        # identity pose, which silently blinds the policy.
        out.append('%s  <site name="imu" pos="0 0 0.3" size="0.01"/>' % pad)"""
assert a in t
t = t.replace(a, b)
a2 = """emit("base", 2, np.zeros(3))
out.append('    <site name="imu" pos="0 0 0.3" size="0.01"/>')
out.append('  </worldbody>')"""
b2 = """emit("base", 2, np.zeros(3))
out.append('  </worldbody>')"""
assert a2 in t
t = t.replace(a2, b2)
io.open(p, "w", encoding="utf-8").write(t)
ast.parse(t)
print("imu site moved onto base_link")
