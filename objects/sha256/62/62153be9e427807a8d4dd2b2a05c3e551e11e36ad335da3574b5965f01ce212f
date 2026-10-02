import io,ast
p=r"D:/claude2/fangzhen/train/rmvehicle/src/rmvehicle/env_cfgs.py"
t=io.open(p,encoding="utf-8").read()
t=t.replace('secondary=ContactMatch(mode="geom", pattern=".*"),','secondary=ContactMatch(mode="body", pattern="terrain"),')
io.open(p,"w",encoding="utf-8").write(t); ast.parse(t); print("secondary -> terrain")
