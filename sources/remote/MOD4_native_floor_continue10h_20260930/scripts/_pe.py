import io
p=r"D:/claude2/fangzhen/sim_mujoco/sim_baseline.py"
t=io.open(p,encoding="utf-8").read()
old='''imu = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_SITE, "imu")'''
new='''if m.nkey:
    mujoco.mj_resetDataKeyframe(m, d, 0)
mujoco.mj_forward(m, d)
imu = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_SITE, "imu")'''
assert old in t
t=t.replace(old,new,1)
io.open(p,"w",encoding="utf-8").write(t)
print("ok")
