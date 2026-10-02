import math
import numpy as np
import mujoco
import onnxruntime as ort

LEG = ["left_front1_joint", "left_rear1_joint", "right_front1_joint", "right_rear1_joint"]
WHL = ["left_wheel_joint", "right_wheel_joint"]
DT, DEC, KP, KD, WKD = 0.001, 20, 60.0, 2.0, 1.5
for plant, eff, weff, xml in (
        ("legacy54 (v10 plant)", 50.9, 10.0, r"D:/claude2/fangzhen/robot/out_cc_legacy54/scene_cc.xml"),
        ("dm8009 (honest)", 40.0, 5.5, r"D:/claude2/fangzhen/robot/out_cc/scene_cc.xml")):
    m = mujoco.MjModel.from_xml_path(xml)
    d = mujoco.MjData(m)
    m.opt.timestep = DT
    J = lambda n: mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, n)
    qa = {n: m.jnt_qposadr[J(n)] for n in LEG + WHL}
    va = {n: m.jnt_dofadr[J(n)] for n in LEG + WHL}
    wb = {mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, n) for n in ("left_wheel", "right_wheel")}
    site = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_SITE, "imu")
    sess = ort.InferenceSession(r"D:/claude2/fangzhen/train/deploy/rm_cc_v10_final.onnx",
                                providers=["CPUExecutionProvider"])
    inp = sess.get_inputs()[0].name
    st = {"last": np.zeros(6, np.float32), "tgt": {n: 0.0 for n in LEG + WHL}, "k": 0}
    hist = []

    def wheels_down():
        for c in range(d.ncon):
            ct = d.contact[c]
            if m.geom_bodyid[ct.geom1] in wb or m.geom_bodyid[ct.geom2] in wb:
                return True
        return False

    def infer(vx, h, jump=0.0):
        g = d.xmat[site].reshape(3, 3).T @ np.array([0.0, 0.0, -1.0])
        o = np.zeros(35, np.float32)
        o[0], o[1], o[2], o[3] = vx, 0.0, 0.0, h * 5.0
        o[4:7] = d.qvel[3:6] * 0.5
        o[7:10] = g
        o[10:14] = [d.qpos[qa[n]] for n in LEG]
        o[16:20] = [d.qvel[va[n]] * 0.1 for n in LEG]
        o[20:22] = [d.qvel[va[n]] * 0.1 for n in WHL]
        o[22:28] = st["last"]
        o[28] = 1.0
        o[32] = jump
        a = sess.run(None, {inp: o.reshape(1, 35)})[0][0].astype(np.float32)
        st["last"] = a
        for i, n in enumerate(LEG):
            st["tgt"][n] = a[i] * 0.5
        for i, n in enumerate(WHL):
            st["tgt"][n] = a[4 + i] * 10.0

    d.qpos[:] = 0.0
    d.qpos[2] = 0.075
    d.qpos[3] = 1.0
    mujoco.mj_forward(m, d)
    print("\n#### plant = %s   cmd vx = 1.0 m/s, height cmd = 0.22 m" % plant)
    print("    t[s]    z[m]   vx_body   wz_rad   wheelL  wheelR  ncon  ground  pitch")
    for step in range(8000):
        if st["k"] % DEC == 0:
            infer(1.0, 0.22)
        st["k"] += 1
        d.qfrc_applied[:] = 0.0
        for n in LEG:
            d.qfrc_applied[va[n]] = np.clip(KP * (st["tgt"][n] - d.qpos[qa[n]]) - KD * d.qvel[va[n]], -eff, eff)
        for n in WHL:
            d.qfrc_applied[va[n]] = np.clip(WKD * (st["tgt"][n] - d.qvel[va[n]]), -weff, weff)
        mujoco.mj_step(m, d)
        hist.append((d.qpos[2], d.qvel[0], wheels_down()))
        if step % 1000 == 0:
            gg = d.xmat[site].reshape(3, 3).T @ np.array([0.0, 0.0, -1.0])
            print("   %5.2f  %.4f  %+7.3f  %+7.3f  %+6.2f %+6.2f  %4d   %s    %+6.1f" %
                  (step * DT, d.qpos[2], d.qvel[0], d.qvel[5], d.qvel[va[WHL[0]]], d.qvel[va[WHL[1]]],
                   d.ncon, "yes" if wheels_down() else "NO ",
                   math.degrees(math.asin(np.clip(gg[0], -1, 1)))))
    H = np.array(hist)
    last2 = H[-2000:]
    print("   -> travelled %.2f m | mean z=%.3f | mean |vx| last2s=%.3f m/s | ground contact %.0f%% of the time"
          % (d.qpos[0], H[:, 0].mean(), float(np.mean(np.abs(last2[:, 1]))), 100.0 * H[:, 2].mean()))