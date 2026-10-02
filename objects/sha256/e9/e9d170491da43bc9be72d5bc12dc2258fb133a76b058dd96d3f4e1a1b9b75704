import io, ast
p = r"D:/claude2/fangzhen/scripts/export_sim2sim.py"
t = io.open(p, encoding="utf-8").read()
a = """'axis="0 0 1" range="-0.001 0.001" stiffness="100000" damping="2000" '
                   'frictionloss="0" armature="0.001"/>'"""
b = """'axis="0 0 1" range="-0.001 0.001" damping="200" '
                   'frictionloss="0" armature="0.001"/>'"""
assert a in t
t = t.replace(a, b)
a2 = """u.append('    <limit lower="-0.001" upper="0.001" effort="50" velocity="0.01"/>'
             '<dynamics damping="2000" friction="0"/></joint>')"""
b2 = """u.append('    <limit lower="-0.001" upper="0.001" effort="50" velocity="0.01"/>'
             '<dynamics damping="200" friction="0"/></joint>')"""
assert a2 in t
t = t.replace(a2, b2)
io.open(p, "w", encoding="utf-8").write(t)
ast.parse(t)
print("spring placeholder now damping-only")
