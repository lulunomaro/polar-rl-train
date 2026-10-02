import io, ast
p = r"D:/claude2/fangzhen/scripts/build_cc.py"
t = io.open(p, encoding="utf-8").read()
t = t.replace('''for k, v in groups.items():
    n = len(v)
    vol = sum((s["volume_mm3"] if isinstance(v[0], dict) else s[1]["volume_mm3"]) for s in v)
    print("  %-8s %4d solids  %8.1f cm3" % (k, n, vol / 1000))
un = sorted({s[1]["product"].strip() for s in groups.get("base", []) if not isinstance(s, dict)
             and s[1]["path"].startswith("整车总装/24    髋腿")})
print("  (leg parts kept chassis-side: %d distinct)" % len(un))''',
'''def vol_of(item):
    return item["volume_mm3"] if isinstance(item, dict) else item[1]["volume_mm3"]
def path_of(item):
    return item["path"] if isinstance(item, dict) else item[1]["path"]
for k, v in groups.items():
    print("  %-8s %4d solids  %8.1f cm3" % (k, len(v), sum(vol_of(s) for s in v) / 1000))
un = sorted({vol_of and (s[1]["product"].strip() if not isinstance(s, dict) else "")
             for s in groups.get("base", [])
             if not isinstance(s, dict) and path_of(s).startswith("整车总装/24    髋腿")})
print("  (leg parts kept chassis-side: %d distinct)" % len([u for u in un if u]))''')
io.open(p, "w", encoding="utf-8", newline="\n").write(t); ast.parse(t); print("ok")
