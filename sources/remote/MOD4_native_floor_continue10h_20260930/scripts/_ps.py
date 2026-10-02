import io,ast
p=r"D:/claude2/fangzhen/scripts/build_robot.py"
t=io.open(p,encoding="utf-8").read()
t=t.replace("""sc.append('    <quality shadowtype="soft"/>')\n""","")
t=t.replace("ap.add_argument(\"--kw\", type=float, default=6.0)","ap.add_argument(\"--kw\", type=float, default=0.0)")
t=t.replace("ap.add_argument(\"--bp\", type=float, default=3.0)","ap.add_argument(\"--bp\", type=float, default=4.0)")
t=t.replace("ap.add_argument(\"--bd\", type=float, default=0.30)","ap.add_argument(\"--bd\", type=float, default=0.45)")
io.open(p,"w",encoding="utf-8").write(t)
p2=r"D:/claude2/fangzhen/sim_mujoco/sim_baseline.py"
t2=io.open(p2,encoding="utf-8").read()
t2=t2.replace('ap.add_argument("--kw", type=float, default=6.0)','ap.add_argument("--kw", type=float, default=0.0)')
t2=t2.replace('ap.add_argument("--bp", type=float, default=3.0)','ap.add_argument("--bp", type=float, default=4.0)')
t2=t2.replace('ap.add_argument("--bd", type=float, default=0.30)','ap.add_argument("--bd", type=float, default=0.45)')
io.open(p2,"w",encoding="utf-8").write(t2)
ast.parse(t); ast.parse(t2); print("ok")
