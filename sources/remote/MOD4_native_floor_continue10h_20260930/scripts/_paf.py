import io,ast
p=r"D:/claude2/fangzhen/train/rmvehicle/src/rmvehicle/mdp/rewards.py"
t=io.open(p,encoding="utf-8").read()
t=t.replace("  return ((h_l + h_r) * 0.5).unsqueeze(1)","  return (h_l + h_r) * 0.5")
t=t.replace('''  from .observations import height_command
  err = measured_height(env, asset_cfg) - height_command(env, command_name)''','''  from .observations import height_command
  err = measured_height(env, asset_cfg) - height_command(env, command_name).squeeze(-1)''')
t=t.replace("  return (found > 0).float().reshape(found.shape[0], -1).mean(dim=1, keepdim=True)","  out = (found > 0).float().reshape(found.shape[0], -1).mean(dim=1)\n  return out.unsqueeze(-1) if _OBS else out")
t=t.replace("_CACHE: dict = {}","_CACHE: dict = {}\n_OBS = True")
io.open(p,"w",encoding="utf-8").write(t); ast.parse(t); print("ok")
