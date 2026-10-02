import io, ast
p = r"D:/claude2/fangzhen/train/eval_robust.py"
L = io.open(p, encoding="utf-8").read().split("\n")
assert L[88].strip() == "runner.policy.eval()", repr(L[88])
L[88] = "    policy = runner.get_inference_policy()"
assert L[90].strip().startswith("obs = env.reset()"), repr(L[90])
L[90] = "    obs = env.reset()[0]"
i = next(k for k, l in enumerate(L) if "runner.policy.act" in l)
assert "deterministic=True" in L[i + 1], repr(L[i + 1])
L[i] = "            action = policy(obs)"
del L[i + 1]
t = "\n".join(L)
ast.parse(t)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("eval_robust patched")
