import io, ast
p = r"D:/claude2/fangzhen/sim_mujoco/onnx_play.py"
t = io.open(p, encoding="utf-8").read()
old = """        d.qfrc_applied[:] = 0.0
        for jn in ORDER:
            lo, hi = (-30.0, 30.0) if jn in tgt else (-8.0, 8.0)
            if jn in tgt:
                u = args.kp * (tgt[jn] - d.qpos[qa[jn]]) - args.kd * d.qvel[va[jn]]
            else:
                u = args.wk * (wtgt[jn] - d.qvel[va[jn]])
            u = float(np.clip(u, lo, hi))
            if args.effort_mode == "ctrl":
                for i in range(m.nu):
                    if (mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT,
                                          m.actuator_trnid[i, 0]) == jn):
                        d.ctrl[i] = u
            else:
                d.qfrc_applied[va[jn]] = u"""
new = """        TARGET.update(tgt)
        TARGET.update(wtgt)"""
assert old in t
t = t.replace(old, new)
t = t.replace("last_action = np.zeros(6, dtype=np.float32)",
              "last_action = np.zeros(6, dtype=np.float32)\nTARGET = {}")
old2 = """    mujoco.mj_step(m, d)"""
new2 = """    # ---- low-level PD, every physics step (mirrors mujoco_ros2_control::write)
    d.qfrc_applied[:] = 0.0
    for i in range(m.nu):
        d.ctrl[i] = 0.0
    for jn in ORDER:
        if jn not in TARGET:
            continue
        leg = jn in LEG
        lo, hi = (-30.0, 30.0) if leg else (-8.0, 8.0)
        if leg:
            u = args.kp * (TARGET[jn] - d.qpos[qa[jn]]) - args.kd * d.qvel[va[jn]]
        else:
            u = args.wk * (TARGET[jn] - d.qvel[va[jn]])
        u = float(np.clip(u, lo, hi))
        if args.effort_mode == "ctrl":
            for i in range(m.nu):
                if (mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT,
                                      m.actuator_trnid[i, 0]) == jn):
                    d.ctrl[i] = u
        else:
            d.qfrc_applied[va[jn]] = u
    mujoco.mj_step(m, d)"""
assert old2 in t
t = t.replace(old2, new2, 1)
io.open(p, "w", encoding="utf-8").write(t)
ast.parse(t)
print("PD now runs every physics step")
