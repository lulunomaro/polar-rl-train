import io
p=r"D:/claude2/fangzhen/sim_mujoco/onnx_play.py"
t=io.open(p,encoding="utf-8").read()
t=t.replace("np.degrees(mujoco.mju_quat2Vel(np.zeros(3), d.qpos[3:7])), 2))","0.0)")
io.open(p,"w",encoding="utf-8").write(t)
print("ok")
