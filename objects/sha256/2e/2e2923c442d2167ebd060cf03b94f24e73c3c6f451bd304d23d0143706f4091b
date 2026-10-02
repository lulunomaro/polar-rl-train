import io,ast
p=r"D:/claude2/fangzhen/scripts/build_robot.py"
L=io.open(p,encoding="utf-8").read().split("\n")
assert L[238].strip()=="if not args.no_mesh:", repr(L[238])
assert L[242].strip()=='print("wrote", idx_path)', repr(L[242])
del L[238:243]
assert L[239].startswith("raw_total"), repr(L[239])
ins=['if not args.no_mesh:',
     '    json.dump({k: dict(files=v, nfaces=mesh_faces[k]) for k, v in mesh_index.items()},',
     '              open(idx_path, "w"), indent=1)',
     '    print("wrote", idx_path)',
     '']
L=L[:239]+ins+L[239:]
t="\n".join(L); ast.parse(t)
io.open(p,"w",encoding="utf-8").write(t)
print("fixed, syntax ok")
