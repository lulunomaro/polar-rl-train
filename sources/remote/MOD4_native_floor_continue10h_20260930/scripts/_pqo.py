import io, ast
p=r"D:/claude2/fangzhen/scripts/verify_axes.py"
t=io.open(p,encoding="utf-8").read()
t=t.replace("    D = D * np.sign(D @ np.array([0, 1.0 if \"R\" not in tag else -1, 0]))",
            "    D = D * np.sign(D @ np.array([0.0, 1.0, 0.0]))[:, None]")
io.open(p,"w",encoding="utf-8",newline="\n").write(t); ast.parse(t); print("ok")
