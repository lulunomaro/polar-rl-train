"""Which way does a POSITIVE wheel velocity pitch this robot?

The stand-up balance law used in three places (the C++ IDLE/PREPARE loop, this repo's keyframe
generator and the parity harness) assumes  v_wheel > 0  pitches the chassis nose-UP, so
v = kp * asin(g_x) + kd * omega_y  with g_x>0 meaning nose-down.  The keyframe experiment shows
that loop converging to +20 deg of pitch for kp = 0, 3 and 8 alike - i.e. it is not correcting
anything.  Measure the sign instead of assuming it.
"""
import mujoco
import numpy as np
m = mujoco.MjModel.from_xml_path(r"D:/claude2/fangzhen/robot/out_cc/scene_cc.xml")
d = mujoco.MjData(m)
JN = {mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, i): i for i in range(m.njnt)}
QA = {k: int(m.jnt_qposadr[v]) for k, v in JN.items()}
VA = {k: int(m.jnt_dofadr[v]) for k, v in JN.items()}
AN = {mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_ACTUATOR, i): i for i in range(m.nu)}
root = int(m.jnt_dofadr[JN[[k for k in JN if "floating" in k][0]]])


def trial(vwheel, seconds=1.5):
    mujoco.mj_resetDataKeyframe(m, d, 0)
    for _ in range(int(seconds / m.opt.timestep)):
        for jn, tgt in (("left_front1_joint", 0.222), ("left_rear1_joint", 0.097),
                        ("right_front1_joint", 0.230), ("right_rear1_joint", 0.117)):
            d.ctrl[AN[jn.replace("_joint", "_ctrl")]] = float(np.clip(
                120.0 * (tgt - d.qpos[QA[jn]]) - 5.0 * d.qvel[VA[jn]], -60, 60))
        for jn in ("left_wheel_joint", "right_wheel_joint"):
            d.ctrl[AN[jn.replace("_joint", "_ctrl")]] = float(np.clip(
                1.5 * (vwheel - d.qvel[VA[jn]]), -5.5, 5.5))
        mujoco.mj_step(m, d)
    R = np.asarray(d.xmat[1], float).reshape(3, 3)
    g = R.T @ np.array([0.0, 0.0, -1.0])
    pitch = float(np.degrees(np.arcsin(np.clip(g[0], -1, 1))))
    print("  v_wheel=%+6.1f rad/s -> pitch(asin g_x)=%+7.2f deg   base_x=%+.3f  base_z=%.4f"
          % (vwheel, pitch, d.qpos[0], d.qpos[2]))


print("sign of the pitch response, measured:")
for v in (0.0, +8.0, -8.0, +20.0, -20.0):
    trial(v)
print("""
read: if a POSITIVE wheel velocity makes pitch(asin g_x) MORE positive, then g_x>0 is the
direction the wheels drive the chassis INTO, so the balance law must use v = -kp*pitch - kd*rate.""")
