import io
p=r"D:/claude2/fangzhen/sim_mujoco/sim_baseline.py"
t=io.open(p,encoding="utf-8").read()
t=t.replace("Q = {n: mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, n) for n in jn if n}\nqadr = {n: Q[n].qposadr for n in Q}\nvadr = {n: Q[n].qveladr for n in Q}",
"Q = {n: mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, n) for n in jn if n}\nqadr = {n: m.jnt_qposadr[j] for n, j in Q.items()}\nvadr = {n: m.jnt_dofadr[j] for n, j in Q.items()}")
t=t.replace("    c = (r * r - L1 * L2 and (r * r - L1 * L1 - L2 * L2) / (2 * L1 * L2))",
            "    c = (r * r - L1 * L1 - L2 * L2) / (2 * L1 * L2)")
io.open(p,"w",encoding="utf-8").write(t)
print("ok")
