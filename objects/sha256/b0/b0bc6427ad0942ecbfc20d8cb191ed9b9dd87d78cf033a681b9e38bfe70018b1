import io, ast
p=r"D:/claude2/fangzhen/train/eval_robust.py"
t=io.open(p,encoding="utf-8").read()
t=t.replace("import argparse\nfrom copy import deepcopy","import argparse\nfrom copy import deepcopy\nfrom dataclasses import asdict")
t=t.replace('runner = MjlabOnPolicyRunner(env, agent_cfg.__dict__ | {"experiment_name": "eval"},\n                                 log_dir=None, device="cuda:0")',
            'acfg = asdict(agent_cfg)\n    acfg["experiment_name"] = "eval"\n    acfg["logger"] = "tensorboard"\n    runner = MjlabOnPolicyRunner(env, acfg, log_dir=None, device="cuda:0")')
io.open(p,"w",encoding="utf-8",newline="\n").write(t); ast.parse(t); print("ok")
