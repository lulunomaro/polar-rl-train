import io,ast
p=r"D:/claude2/fangzhen/scripts/export_sim2sim.py"
t=io.open(p,encoding="utf-8").read()
a = 'pos="%s" childclass="robot"'
assert a in t
t = t.replace(a, 'pos="%s"')
io.open(p,"w",encoding="utf-8").write(t); ast.parse(t); print("removed childclass")
