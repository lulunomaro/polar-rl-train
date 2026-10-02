import io, ast
p = r"D:/claude2/fangzhen/scripts/build_cc.py"
t = io.open(p, encoding="utf-8").read()
t = t.replace('''def body_of(path, product):
    p = product.strip()
    if not path.startswith("整车总装/24    髋腿"):
        return "base"''',
'''def body_of(path, product):
    p = product.strip()
    if not (path.startswith("整车总装/24    髋腿")
            or path.startswith("整车总装/Mirror24    髋腿")):
        return "base"''')
t = t.replace('''un = sorted({vol_of and (s[1]["product"].strip() if not isinstance(s, dict) else "")
             for s in groups.get("base", [])
             if not isinstance(s, dict) and path_of(s).startswith("整车总装/24    髋腿")})''',
'''un = sorted({s[1]["product"].strip() for s in groups.get("base", [])
             if isinstance(s, tuple)})''')
io.open(p, "w", encoding="utf-8", newline="\n").write(t); ast.parse(t); print("right-leg classification fixed")
