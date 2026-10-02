"""Per-environment terrain-type queries for skill rewards and commands."""
from __future__ import annotations

import torch


def terrain_mask(env, key: str) -> torch.Tensor:
  """[B] bool mask of the envs currently assigned to the named terrain column.

  The terrain curriculum keeps each env's COLUMN fixed (only the difficulty row moves),
  so this is stable across resets.  Plane terrains have no terrain_types tensor; there the
  mask is all False and the caller's term is simply inactive.
  """
  try:
    terrain = env.scene["terrain"]
  except KeyError:
    return torch.zeros(env.num_envs, dtype=torch.bool, device=env.device)
  types = getattr(terrain, "terrain_types", None)
  gen = getattr(getattr(terrain, "cfg", None), "terrain_generator", None)
  if types is None or gen is None:
    return torch.zeros(env.num_envs, dtype=torch.bool, device=env.device)
  keys = list(gen.sub_terrains.keys())
  if key not in keys:
    return torch.zeros(env.num_envs, dtype=torch.bool, device=env.device)
  return types == keys.index(key)
