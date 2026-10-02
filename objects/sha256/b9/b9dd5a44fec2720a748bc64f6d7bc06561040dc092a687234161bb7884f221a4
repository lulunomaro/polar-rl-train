import io, ast
p = r"D:/claude2/fangzhen/scripts/scan_workspace.py"
t = io.open(p, encoding="utf-8").read()
t = t.replace("    return axis_pt + v * c + np.cross(d, v) * s + np.outer(d @ v, d) * (1 - c)",
              "    return axis_pt + v * c + np.cross(v, d) * (-s) + np.outer(v @ d, d) * (1 - c)")
t = t.replace("        keep = max(1, int(len(v) * budget / max(1, tot) * 3))",
              "        keep = max(400, int(len(v) * budget / max(1, tot) * 6))")
io.open(p, "w", encoding="utf-8", newline="\n").write(t); ast.parse(t)
print("rodrigues + sampling fixed")
