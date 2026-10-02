import json, os, sys, re
m = json.load(open(os.path.join(sys.argv[1], "manifest.json"), encoding="utf8"))
pat = sys.argv[2] if len(sys.argv) > 2 else ""
out = []
for t in m["tree"]:
    if pat and not re.search(pat, t["path"]):
        continue
    T = [round(t["M"][i][3], 1) for i in range(3)]
    out.append("%s%s  T=%s  children=%d" % ("  " * t["depth"], t["name"][:44], T, t["n_children"]))
p = os.path.join(sys.argv[1], "tree.txt")
open(p, "w", encoding="utf8").write("\n".join(out))
print("\n".join(out[:200]))
print("... total", len(out))

