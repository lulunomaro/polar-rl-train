import io
p=r"D:/claude2/fangzhen/sim_mujoco/sim_baseline.py"
t=io.open(p,encoding="utf-8").read()
t=t.replace('for bp in (0.20, 0.32, 0.50, 0.80):','for bp in (1.5, 2.5, 4.0, 6.0):')
t=t.replace('for bd in (0.035, 0.055, 0.09):','for bd in (0.12, 0.25, 0.45):')
t=t.replace('hist, _, _, _ = run(12.0, 0.30, 1.2, bp, bd, 0.03, kw, 700.0, 45.0)','hist, _, _, _ = run(10.0, 0.30, 1.2, bp, bd, 0.03, kw, 700.0, 45.0)')
t=t.replace('ap.add_argument("--bp", type=float, default=0.32)','ap.add_argument("--bp", type=float, default=3.0)')
t=t.replace('ap.add_argument("--bd", type=float, default=0.055)','ap.add_argument("--bd", type=float, default=0.30)')
io.open(p,"w",encoding="utf-8").write(t)
print("ok")
