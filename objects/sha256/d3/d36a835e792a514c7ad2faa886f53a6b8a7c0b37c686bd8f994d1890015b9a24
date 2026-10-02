import io
F=r"D:\claude2\fangzhen\scripts\export_sim2sim_cc.py"
s=io.open(F,encoding="utf-8").read()
a='SOLVE_TRAIN = _os.environ.get("RM_DEPLOY_TRAIN_SOLVER", "1") == "1"'
b=('# Measured: with iterations=10 / impratio=50 the CPU Newton solver cannot hold the six\n'
   '# <connect> equalities and MuJoCo reports "Nan, Inf or huge value in QACC at DOF 4"\n'
   '# within 0.27 s.  mjlab only gets away with it because it runs mujoco-warp on the GPU.\n'
   '# Keep the plant\'s own stiff, accurate regime in the deployment.\n'
   'SOLVE_TRAIN = _os.environ.get("RM_DEPLOY_TRAIN_SOLVER", "0") == "1"')
assert s.count(a)==1
io.open(F,"w",encoding="utf-8").write(s.replace(a,b))
print("deployment solver -> plant default (stiff, stable on CPU)")