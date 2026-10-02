import io,ast
p=r"D:/claude2/fangzhen/train/rmvehicle/src/rmvehicle/mdp/rewards.py"
t=io.open(p,encoding="utf-8").read()
t=t.replace("_CACHE: dict = {}\n_OBS = True","_CACHE: dict = {}")
t=t.replace('''  out = (found > 0).float().reshape(found.shape[0], -1).mean(dim=1)
  return out.unsqueeze(-1) if _OBS else out''','''  return (found > 0).float().reshape(found.shape[0], -1).mean(dim=1)


def wheel_contact_obs(env, sensor_name: str) -> torch.Tensor:
  """Same as :func:`wheel_contact_fraction` but shaped [B, 1] for observations."""
  return wheel_contact_fraction(env, sensor_name).unsqueeze(-1)''')
io.open(p,"w",encoding="utf-8").write(t); ast.parse(t)
p2=r"D:/claude2/fangzhen/train/rmvehicle/src/rmvehicle/mdp/__init__.py"
t2=io.open(p2,encoding="utf-8").read().replace("  wheel_contact_fraction,","  wheel_contact_fraction,\n  wheel_contact_obs,")
io.open(p2,"w",encoding="utf-8").write(t2); ast.parse(t2)
p3=r"D:/claude2/fangzhen/train/rmvehicle/src/rmvehicle/env_cfgs.py"
t3=io.open(p3,encoding="utf-8").read()
t3=t3.replace('''    "wheel_contact": ObservationTermCfg(
      func=mdp.wheel_contact_fraction, params={"sensor_name": "wheel_contact"}),''','''    "wheel_contact": ObservationTermCfg(
      func=mdp.wheel_contact_obs, params={"sensor_name": "wheel_contact"}),''')
io.open(p3,"w",encoding="utf-8").write(t3); ast.parse(t3)
print("split obs/reward contact terms")
