import io
F=r"D:\claude2\fangzhen\sim_mujoco\onnx_play.py"
s=io.open(F,encoding="utf-8").read()
a='ap.add_argument("--roll-fric", type=float, default=-1.0)'
b=('ap.add_argument("--roll-fric", type=float, default=-1.0)\n'
   '    ap.add_argument("--train-solver", action="store_true",\n'
   '                    help="apply mjlab\'s exact solver regime (dt 2 ms, iterations 10, "\n'
   '                         "ls_iterations 10, impratio 50, cone elliptic) on CPU")')
assert s.count(a)==1
s=s.replace(a,b)
a2="m.opt.timestep = args.dt"
b2=("m.opt.timestep = args.dt\n"
    "if getattr(args, \"train_solver\", False):\n"
    "    m.opt.iterations = 10\n"
    "    m.opt.ls_iterations = 10\n"
    "    m.opt.impratio = 50.0\n"
    "    m.opt.cone = mujoco.mjtCone.mjCONE_ELLIPTIC\n"
    "    print(\"solver: mjlab regime (dt=%g iter=10 ls=10 impratio=50 cone=elliptic)\" % m.opt.timestep)")
assert s.count(a2)==1
s=s.replace(a2,b2,1)
io.open(F,"w",encoding="utf-8").write(s)
print("train-solver flag added")