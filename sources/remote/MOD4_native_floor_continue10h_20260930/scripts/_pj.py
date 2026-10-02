import io,ast
p=r"D:/claude2/fangzhen/scripts/build_robot.py"
t=io.open(p,encoding="utf-8").read()
bad=t[t.index("    if not args.no_mesh:"):t.index("raw_total = sum(v[\"mass\"}")+len("raw_total = sum(v[\"mass\"}")]
good='''    if not args.no_mesh:
        json.dump({k: dict(files=v, nfaces=mesh_faces[k]) for k, v in mesh_index.items()},
                  open(idx_path, "w"), indent=1)
        print("wrote", idx_path)

raw_total = sum(v["mass"] for v in info.values())
'''
t=t.replace(bad,good)
ast.parse(t)
io.open(p,"w",encoding="utf-8").write(t)
print("fixed, syntax ok")
