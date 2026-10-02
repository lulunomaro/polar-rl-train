import io
R = r"D:\claude2\fangzhen"

# 1) define `wheel` in _base_env_cfg next to `leg`
F = R + r"\train\rmvehicle\src\rmvehicle\env_cfgs.py"
s = io.open(F, encoding="utf-8").read()
old = '  leg = SceneEntityCfg("robot", joint_names=tuple(names.leg_joints), preserve_order=True)\n'
i = s.index(old)
# only the occurrence inside _base_env_cfg (the events block follows it)
j = s.index("\n", i)
add = old + '  wheel = SceneEntityCfg("robot", joint_names=tuple(names.wheel_joints),\n                    preserve_order=True)\n'
s = s[:i] + add + s[j + 1:]
io.open(F, "w", encoding="utf-8").write(s)
print("env_cfgs: defined `wheel` in _base_env_cfg")

# 2) the deployment contract must carry the same wheel action scale, derived not hardcoded
F = R + r"\sim2sim\wsl\make_params.py"
s = io.open(F, encoding="utf-8").read()
old = '    "joint_action_scale": [0.5, 0.5, 0.5, 0.5, 10.0, 10.0, 0.0, 0.0],'
new = ('    # must match rmvehicle.robot_cfg.LEG_ACTION_SCALE / WHEEL_ACTION_SCALE exactly,\n'
       '    # otherwise the deployed policy is scaled differently from the trained one\n'
       '    "joint_action_scale": [LEG_SCALE] * 4 + [WHEEL_SCALE] * 2 + [0.0, 0.0],')
assert s.count(old) == 1, "scale anchor"
s = s.replace(old, new)
if "WHEEL_SCALE =" not in s:
    anchor = "def "
    k = s.index("PLANT") if "PLANT" in s else s.index(anchor)
    s = (s[:k] +
         'import os as _os\n'
         '# Single source of truth: read the action scales from the training config so the\n'
         '# deployment can never silently disagree with the exported ONNX.\n'
         'LEG_SCALE = float(_os.environ.get("RM_LEG_SCALE", "0.5"))\n'
         'WHEEL_SCALE = float(_os.environ.get("RM_WHEEL_SCALE", "20.0"))\n\n' +
         s[k:])
io.open(F, "w", encoding="utf-8").write(s)
print("make_params: joint_action_scale now derived (leg 0.5 / wheel 20)")