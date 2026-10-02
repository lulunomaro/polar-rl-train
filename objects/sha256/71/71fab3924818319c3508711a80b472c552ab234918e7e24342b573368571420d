import io,ast
p=r"D:/claude2/fangzhen/scripts/export_sim2sim.py"
t=io.open(p,encoding="utf-8").read()
t=t.replace("""' childclass="robot">'"","\"\">\n\"")  # no-op guard
t=t.replace('%s<body name="%s" pos="%s" childclass="robot">','%s<body name="%s" pos="%s">')
io.open(p,"w",encoding="utf-8").write(t); ast.parse(t); print("ok")
