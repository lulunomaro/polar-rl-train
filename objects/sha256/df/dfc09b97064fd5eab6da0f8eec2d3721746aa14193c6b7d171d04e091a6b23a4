import io, ast
p = r"D:/claude2/fangzhen/sim_mujoco/onnx_play.py"
t = io.open(p, encoding="utf-8").read()
a = "ap.add_argument(\"--video\", action=\"store_true\")"
b = ("ap.add_argument(\"--video\", action=\"store_true\")\n"
     "ap.add_argument(\"--effort-mode\", default=\"ctrl\", choices=[\"ctrl\", \"qfrc\"])\n"
     "ap.add_argument(\"--roll-fric\", type=float, default=-1.0)")
assert a in t
t = t.replace(a, b, 1)
old = """        for i in range(m.nu):
            jn = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, m.actuator_trnid[i, 0])
            lo, hi = m.actuator_ctrlrange[i]
            if jn in tgt:
                u = args.kp * (tgt[jn] - d.qpos[qa[jn]]) - args.kd * d.qvel[va[jn]]
            elif jn in wtgt:
                u = args.wk * (wtgt[jn] - d.qvel[va[jn]])
            else:
                u = 0.0
            d.ctrl[i] = float(np.clip(u, lo, hi))"""
new = """        d.qfrc_applied[:] = 0.0
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
assert old in t, "ctrl block not found"
t = t.replace(old, new)
c = "mujoco.mj_forward(m, d)\n"
add = ("mujoco.mj_forward(m, d)\n"
       "if args.roll_fric >= 0:\n"
       "    for g in range(m.ngeom):\n"
       "        if \"wheel\" in (mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, g) or \"\"):\n"
       "            m.geom_friction[g] = (m.geom_friction[g][0], args.roll_fric,\n"
       "                                  args.roll_fric / 10.0)\n"
       "    print(\"wheel friction set to\", m.geom_friction[9])\n")
assert c in t
t = t.replace(c, add, 1)
io.open(p, "w", encoding="utf-8").write(t)
ast.parse(t)
print("patched")
