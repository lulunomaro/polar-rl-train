import io, ast
p = r"D:/claude2/fangzhen/sim2real/mock_h7.py"
t = io.open(p, encoding="utf-8").read()
a = """BASE = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "base_link")
IMU = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_SITE, "imu")"""
b = """BASE = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "base_link")
SID = {n: mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_SENSOR, n)
       for n in ("accelerometer", "gyro", "imu")}
assert all(v >= 0 for v in SID.values()), "sensors missing: %s" % SID
SADR = {k: int(m.sensor_adr[v]) for k, v in SID.items()}"""
assert a in t; t = t.replace(a, b)
a2 = """        # ---- IMU (body frame), MuJoCo quaternion is wxyz, the wire wants xyzw
        R = d.site_xmat[IMU].reshape(3, 3)
        grav = R.T @ np.array([0.0, 0.0, -1.0])
        acc = d.site_xacc[IMU]
        gyro = d.qvel[3:6]
        qw = d.qpos[3:7]
        imu = (list(acc) + list(gyro) + [qw[1], qw[2], qw[3], qw[0]])"""
b2 = """        # ---- IMU straight out of the MJCF sensors; the wire wants xyzw
        acc = [float(d.sensordata[SADR["accelerometer"] + i]) for i in range(3)]
        gyro = [float(d.sensordata[SADR["gyro"] + i]) for i in range(3)]
        qw = [float(d.sensordata[SADR["imu"] + i]) for i in range(4)]   # w x y z
        grav = np.array([2 * (qw[1] * qw[3] + qw[0] * qw[2]),
                         2 * (qw[2] * qw[3] - qw[0] * qw[1]),
                         1 - 2 * (qw[1] * qw[1] + qw[2] * qw[2])])
        imu = acc + gyro + [qw[1], qw[2], qw[3], qw[0]]"""
assert a2 in t; t = t.replace(a2, b2)
io.open(p, "w", encoding="utf-8").write(t); ast.parse(t); print("sensor-based IMU reads")
