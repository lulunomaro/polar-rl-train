import io, ast
p = r"D:/claude2/fangzhen/sim_mujoco/onnx_play.py"
t = io.open(p, encoding="utf-8").read()
a = "print(\"RESULT:\", \"FELL\" if np.abs(h[:, 3]).max() > 45 else \"BALANCED\")"
b = ("print(\"RESULT:\", \"FELL\" if np.abs(h[:, 3]).max() > 45 else \"BALANCED\")\n"
     "print(\"\\nfinal joint pos:\", {n: round(float(d.qpos[qa[n]]), 3) for n in ORDER})\n"
     "print(\"final joint vel:\", {n: round(float(d.qvel[va[n]]), 3) for n in ORDER})\n"
     "print(\"contacts:\", [(mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, c.geom[0]),\n"
     "                      mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, c.geom[1]),\n"
     "                      round(float(c.dist), 4)) for c in d.contact][:8])\n"
     "print(\"base euler (xyz deg):\", np.round(mujoco.mju_quat2Vel(np.zeros(3), d.qpos[3:7],\n"
     "                                     np.array([1.0])) if False else\n"
     "                     np.degrees(mujoco.mju_quat2Vel(np.zeros(3), d.qpos[3:7])), 2))")
assert a in t
t = t.replace(a, b)
io.open(p, "w", encoding="utf-8").write(t)
ast.parse(t)
print("diag added")
