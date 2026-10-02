import io
F = r"D:\claude2\fangzhen\train\rmvehicle\src\rmvehicle\env_cfgs.py"
lines = io.open(F, encoding="utf-8").read().split("\n")
# undo the misplaced insert (the two-line `wheel = ...` copy that landed in the actions block)
bad = '  wheel = SceneEntityCfg("robot", joint_names=tuple(names.wheel_joints),\n                    preserve_order=True)'
s = "\n".join(lines)
assert s.count(bad) == 1, "misplaced block not found"
s = s.replace(bad + "\n", "", 1)
lines = s.split("\n")
# insert right after the `leg` definition inside _base_env_cfg (the one followed by commands/rewards)
tgt = None
for i, l in enumerate(lines):
    if l.strip().startswith('leg = SceneEntityCfg("robot", joint_names=tuple(names.leg_joints)') and i > 90:
        tgt = i
        break
assert tgt is not None, "leg anchor in _base_env_cfg not found"
lines.insert(tgt + 1,
             '  wheel = SceneEntityCfg("robot", joint_names=tuple(names.wheel_joints),\n'
             '                    preserve_order=True)')
io.open(F, "w", encoding="utf-8").write("\n".join(lines))
print("placed `wheel` inside _base_env_cfg at line", tgt + 2)