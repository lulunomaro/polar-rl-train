import io
p = r"D:/claude2/fangzhen/scripts/build_cc.py"
s = io.open(p, encoding="utf-8").read()
s = s.replace("""for body, cfg in TOPO.items():
    items = [i for i in groups.get(body, []) if isinstance(i, tuple)]
    if not items:
        continue""",
"""for body in [b for b in groups if b != "base"]:
    items = [i for i in groups.get(body, []) if isinstance(i, tuple)]
    if not items:
        continue""", 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("fixed audit loop")