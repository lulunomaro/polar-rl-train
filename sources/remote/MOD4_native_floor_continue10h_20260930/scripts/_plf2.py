import io, ast
p = r"D:/claude2/fangzhen/scripts/build_cc.py"
t = io.open(p, encoding="utf-8").read()
t = t.replace('''for (body, side), fn in sorted(MESH.items(), key=lambda kv: str(kv[0])):
    if body == "base":
        continue
    out.append('    <mesh name="%s_%s" file="%s" scale="0.001 0.001 0.001"/>'
               % (body, side.lower(), fn))''',
'''for key, fn in sorted(((k, v) for k, v in MESH.items() if k != "base"), key=lambda kv: str(kv[0])):
    body, side = key
    out.append('    <mesh name="%s_%s" file="%s" scale="0.001 0.001 0.001"/>'
               % (body, side.lower(), fn))''')
io.open(p, "w", encoding="utf-8", newline="\n").write(t); ast.parse(t); print("ok")
