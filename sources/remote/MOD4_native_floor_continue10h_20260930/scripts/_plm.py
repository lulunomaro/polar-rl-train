import io,ast
p=r"D:/claude2/fangzhen/sim_mujoco/onnx_play.py"
t=io.open(p,encoding="utf-8").read()
t=t.replace('ap.add_argument("--video", action="store_true")',
            'ap.add_argument("--video", action="store_true")\nap.add_argument("--effort-mode", default="ctrl", choices=["ctrl", "qfrc"],\n                    help="ctrl = <motor> actuators (training model); qfrc = the '\n                    'deployment path (mujoco_ros2_control)")')
a='''        for i in range(m.nu):
            jn = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, m.actuator_trnid[i, 0])
            lo, hi = m.actuator_ctrlrange[i]
            if jn in tgt:
                u = args.kp * (tgt[jn] - d.qpos[qa[jn]]) - args.kd * d.qvel[va[jn]]
            elif jn in wtgt:
                u = args.wk * (wtgt[jn] - d.qvel[va[jn]])
            else:
                u = 0.0
            d.ctrl[i] = float(np.clip(u, lo, hi))'''
b='''        d.qfrc_applied[:] = 0.0
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
                d.qfrc_applied[va[jn]] = u'''
assert a in t; t=t.replace(a,b)
io.open(p,"w",encoding="utf-8").write(t); ast.parse(t); print("effort modes added")
