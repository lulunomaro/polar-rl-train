import io, ast
p = r"D:/claude2/fangzhen/train/eval_robust.py"
t = io.open(p, encoding="utf-8").read()
t = t.replace('        alive += (~dones).float()',
              '        alive += (torch.as_tensor(dones) == 0).float().flatten()')
t = t.replace('    cfg.events.pop("push_robot", None)\n', '')
t = t.replace('    if cond == "nominal":', '    if cond != "push":\n        cfg.events.pop("push_robot", None)\n    if cond == "nominal":')
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
ast.parse(t); print("fixed survival metric + push condition")
