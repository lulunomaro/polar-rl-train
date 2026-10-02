import io,ast
p=r"D:/claude2/fangzhen/scripts/build_robot.py"
L=io.open(p,encoding="utf-8").read().split("\n")
# lines are 0-based here; file line 239 -> index 238
assert L[238].strip()=="if not args.no_mesh:", repr(L[238])
del L[238]
for i in (239,240,241,242):
    L[i]="    "+L[i]
t="\n".join(L)
ast.parse(t)
io.open(p,"w",encoding="utf-8").write(t)
print("fixed indentation, syntax ok")
