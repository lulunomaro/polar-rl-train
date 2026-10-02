import io,ast
p=r"D:/claude2/fangzhen/scripts/export_sim2sim.py"
t=io.open(p,encoding="utf-8").read()
t=t.replace('    children[j["parent"]] = children.get(j["parent"], []) + [j]','    children[j["parent"]] = children.get(j["parent"], []) + [j["child"]]')
io.open(p,"w",encoding="utf-8").write(t); ast.parse(t); print("ok")
