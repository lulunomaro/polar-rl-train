import io
p=r"D:/claude2/fangzhen/sim_mujoco/onnx_play.py"
L=io.open(p,encoding="utf-8").read().split("\n")
i=[k for k,l in enumerate(L) if l.strip().startswith('print("base euler')][0]
j=[k for k,l in enumerate(L) if l.strip().startswith("0.0)")][0]
del L[i:j+1]
t="\n".join(L)
import ast; ast.parse(t); io.open(p,"w",encoding="utf-8").write(t); print("diag cleaned")
