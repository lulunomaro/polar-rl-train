import io, ast
p = r"D:/claude2/fangzhen/train/eval_robust.py"
t = io.open(p, encoding="utf-8").read()
t = t.replace("""    runner.load(args.checkpoint)
    runner.policy.eval()
    obs = env.reset()""",
"""    runner.load(args.checkpoint)
    policy = runner.get_inference_policy()
    obs = env.reset()[0]""")
t = t.replace("""        with torch.no_grad():
            action = runner.policy.act(obs["actor"] if "actor" in obs else obs["policy"],
                                       deterministic=True)
        obs, rew, dones, extras = env.step(action)""",
"""        with torch.no_grad():
            action = policy(obs)
        obs, rew, dones, extras = env.step(action)""")
io.open(p, "w", encoding="utf-8", newline="\n").write(t); ast.parse(t)
print("eval uses get_inference_policy()")
