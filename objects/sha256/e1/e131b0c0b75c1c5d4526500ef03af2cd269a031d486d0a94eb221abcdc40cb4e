import io
F=r"D:\claude2\fangzhen\scripts\dump_mjlab_handover.py"
s=io.open(F,encoding="utf-8").read()
old="runner = runner_cls(env, asdict(agent_cfg), device=DEV)"
new="runner = runner_cls(RslRlVecEnvWrapper(env), asdict(agent_cfg), device=DEV)"
assert s.count(old)==1
io.open(F,"w",encoding="utf-8").write(s.replace(old,new))
print("wrapped the env as verify_skills.py does")