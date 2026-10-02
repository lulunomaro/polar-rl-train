import io, ast
p = r"D:/claude2/fangzhen/train/eval_robust.py"
L = io.open(p, encoding="utf-8").read().split("\n")
for k, l in enumerate(L):
    if l.strip() == "runner.policy.eval()":
        L[k] = "    policy = runner.get_inference_policy()"; print("patched eval line", k + 1)
    if l.strip() == "obs = env.reset()":
        L[k] = "    obs = env.reset()[0]"; print("patched reset line", k + 1)
i = next(k for k, l in enumerate(L) if "runner.policy.act" in l)
L[i] = "            action = policy(obs)"
if "deterministic=True" in L[i + 1]:
    del L[i + 1]
t = "\n".join(L)
ast.parse(t)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("done")
