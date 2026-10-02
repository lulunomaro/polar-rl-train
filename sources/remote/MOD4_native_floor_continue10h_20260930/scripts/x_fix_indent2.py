import io
F=r"D:\claude2\fangzhen\sim_mujoco\onnx_play.py"
lines=io.open(F,encoding="utf-8").read().split(chr(10))
# collapse the broken --train-solver argument block into one clean line
out=[]; i=0
while i < len(lines):
    if "--train-solver" in lines[i]:
        out.append('ap.add_argument("--train-solver", action="store_true")')
        i += 1
        while i < len(lines) and ("mjlab solver regime" in lines[i] or "impratio 50, cone elliptic" in lines[i] or lines[i].strip().startswith('"')):
            i += 1
        continue
    out.append(lines[i]); i += 1
io.open(F,"w",encoding="utf-8").write(chr(10).join(out))
print("cleaned")