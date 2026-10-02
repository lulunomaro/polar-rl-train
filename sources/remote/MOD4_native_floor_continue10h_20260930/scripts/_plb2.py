import io, ast
p = r"D:/claude2/fangzhen/scripts/build_cc.py"
t = io.open(p, encoding="utf-8").read()
t = t.replace("    I = balance(I)[0]\n", "    I = balance(I)\n")
t = t.replace('BODIES["base"] = dict(mass=m, com=com, inertia=balance(I)[0], n=len(ss))',
              'BODIES["base"] = dict(mass=m, com=com, inertia=balance(I), n=len(ss))')
io.open(p, "w", encoding="utf-8", newline="\n").write(t); ast.parse(t); print("ok")
