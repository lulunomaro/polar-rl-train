import io,re
F=r"D:\claude2\fangzhen\sim_mujoco\onnx_play.py"
s=io.open(F,encoding="utf-8").read()
bad = ('ap.add_argument("--roll-fric", type=float, default=-1.0)\n'
       '    ap.add_argument("--train-solver", action="store_true",\n'
       '                    help="apply mjlab\'s exact solver regime (dt 2 ms, iterations 10, "\n'
       '                         "ls_iterations 10, impratio 50, cone elliptic) on CPU")')
good = ('ap.add_argument("--roll-fric", type=float, default=-1.0)\n'
        'ap.add_argument("--train-solver", action="store_true",\n'
        '                help="apply mjlab solver regime (dt 2 ms, iterations 10, ls 10,\n'
        '                      impratio 50, cone elliptic) on the CPU solver")')
assert s.count(bad)==1, "anchor missing"
io.open(F,"w",encoding="utf-8").write(s.replace(bad,good))
print("indentation fixed")