import io,ast
p=r"D:/claude2/fangzhen/sim_mujoco/sim_baseline.py"
t=io.open(p,encoding="utf-8").read()
t=t.replace('ap.add_argument("--kw", type=float, default=0.015)','ap.add_argument("--kw", type=float, default=0.0)')
io.open(p,"w",encoding="utf-8").write(t); ast.parse(t); print("kw default 0")
