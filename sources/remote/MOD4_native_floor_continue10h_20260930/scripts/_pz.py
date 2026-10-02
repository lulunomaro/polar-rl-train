import io
p=r"D:/claude2/fangzhen/train/rmvehicle/src/rmvehicle/mdp/observations.py"
t=io.open(p,encoding="utf-8").read()
t=t.replace('''def mode_onehot(env) -> torch.Tensor:''','''def randomize_height_command(env, env_ids=None, range=(0.18, 0.34)) -> None:
  """Event term: resample the commanded hip->wheel height for the given envs."""
  buf = height_command(env)
  n = env.num_envs if env_ids is None else (
    env_ids.numel() if hasattr(env_ids, "numel") else len(env_ids))
  if n >= env.num_envs:
    env_ids = None
    n = env.num_envs
  lo, hi = float(range[0]), float(range[1])
  new = torch.empty(n, 1, device=env.device).uniform_(lo, hi)
  if env_ids is None:
    buf.copy_(new)
  else:
    buf[env_ids] = new


def mode_onehot(env) -> torch.Tensor:''')
io.open(p,"w",encoding="utf-8").write(t)
import ast; ast.parse(t); print("ok")
