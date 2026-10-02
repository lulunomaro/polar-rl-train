import io
p=r"D:/claude2/fangzhen/sim_mujoco/sim_baseline.py"
t=io.open(p,encoding="utf-8").read()
old='''act = {}
for i in range(m.nu):
    bid = m.actuator_trnid[i, 0]
    for n, j in Q.items():
        if m.jnt_bodyid[j] == bid:
            act[i] = n'''
new='''act = {}
for i in range(m.nu):
    an = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_ACTUATOR, i)
    if m.actuator_trntype[i] == mujoco.mjtTrn.mjTRN_JOINT:
        act[i] = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, m.actuator_trnid[i, 0])
    else:
        act[i] = an'''
assert old in t
t=t.replace(old,new)
io.open(p,"w",encoding="utf-8").write(t)
print("ok")
