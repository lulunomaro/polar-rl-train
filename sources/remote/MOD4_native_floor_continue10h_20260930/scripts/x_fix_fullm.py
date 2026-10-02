import io
F=r"D:\claude2\fangzhen\scripts\wheel_servo_stability.py"
s=io.open(F,encoding="utf-8").read()
old = """    n = m.nv
    return float(d.qM[dof * n + dof]) if dof * n + dof < len(d.qM) else float(d.qM[dof])"""
new = """    n = m.nv
    full = np.zeros(n * n)
    mujoco.mj_fullM(m, full, d.M)
    return float(full[dof * n + dof])"""
assert s.count(old)==1
io.open(F,"w",encoding="utf-8").write(s.replace(old,new))
print("ok")