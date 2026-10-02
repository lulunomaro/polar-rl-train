import io, ast
p = r"D:/claude2/fangzhen/scripts/build_cc.py"
t = io.open(p, encoding="utf-8").read()
t = t.replace("""'  <compiler angle="radian" autolimits="true" balanceinertia="true" '
       'inertiafromgeom="false"/>',""",
              """'  <compiler angle="radian" meshdir="meshes/" autolimits="true" balanceinertia="true" '
       'inertiafromgeom="false"/>',""")
io.open(p, "w", encoding="utf-8", newline="\n").write(t); ast.parse(t); print("meshdir added")
