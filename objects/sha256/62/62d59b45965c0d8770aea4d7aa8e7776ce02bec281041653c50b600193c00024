import io,ast
p=r"D:/claude2/fangzhen/train/export_onnx.py"
t=io.open(p,encoding="utf-8").read()
t=t.replace("import argparse, json, os\nfrom pathlib import Path","import argparse, json, os\nfrom dataclasses import asdict\nfrom pathlib import Path")
t=t.replace('env_cfg = load_env_cfg(args.task, play=True)','env_cfg = load_env_cfg(args.task, play=True)')
t=t.replace('runner = MjlabOnPolicyRunner(env, agent_cfg.to_dict(), log_dir=None, device="cuda:0")',
            'runner = MjlabOnPolicyRunner(env, asdict(agent_cfg), device="cuda:0")')
t=t.replace('''torch_out = runner.policy.act_inference({"actor": torch.from_numpy(o).to("cuda:0")}) \\
    if hasattr(runner, "policy") else None
a_onnx = sess.run(None, {"obs": o})[0]''','''a_onnx = sess.run(None, {"obs": o})[0]''')
io.open(p,"w",encoding="utf-8").write(t); ast.parse(t); print("ok")
