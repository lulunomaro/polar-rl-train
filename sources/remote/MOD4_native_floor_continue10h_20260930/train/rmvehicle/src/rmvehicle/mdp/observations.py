"""Observation terms that reproduce the wheelbipe_ros2_sim2sim 35-D policy contract.

Index map (see refs/wheelbipe_ros2_sim2sim-main/PARAMETERS.md section 2):

  0     cmd linear.x                 x 1.0
  1     reserved lateral command     fixed 0
  2     cmd angular.z                x 1.0
  3     target height                x 5.0
  4-6   body angular velocity xyz    x 0.5
  7-9   projected gravity xyz        x 1.0
  10-13 four leg joint positions (rel. default)
  14-15 two wheel joint position slots, fixed 0
  16-19 four leg joint velocities    x 0.1
  20-21 two wheel joint velocities   x 0.1
  22-27 previous 6-D raw action
  28-34 mode one-hot [normal, stair, slope, recover, jump, height_target, state_time]

Every term below emits exactly the slice named in it, so concatenating the terms in
`ORDER` yields the 35-D vector in the documented order.
"""
from __future__ import annotations

import torch

from mjlab.entity import Entity
from mjlab.managers.scene_entity_config import SceneEntityCfg

#: Joint-name patterns, ordered so that the concatenated leg block is
#: [hip_L, knee_L, hip_R, knee_R] and the wheel block is [wheel_L, wheel_R].
LEG_PATTERNS = ("hip_L_joint", "knee_L_joint", "hip_R_joint", "knee_R_joint")
WHEEL_PATTERNS = ("wheel_L_joint", "wheel_R_joint")

#: Nominal command height [m] used when the deployment does not publish one.
DEFAULT_HEIGHT = 0.22


def twist_commands(env, command_name: str = "twist") -> torch.Tensor:
  """[B, 3] = (linear.x, 0.0, angular.z) -- indices 0..2 of the contract."""
  cmd = env.command_manager.get_term(command_name)
  lin, ang = cmd.command[:, :2], cmd.command[:, 2:3]
  return torch.cat((lin[:, 0:1], torch.zeros_like(lin[:, 0:1]), ang), dim=1)


def height_command(env, command_name: str = "height") -> torch.Tensor:
  """[B, 1] target height, index 3.  Scale 5.0 is applied by the term."""
  if command_name in env.command_manager.active_terms:
    return env.command_manager.get_command(command_name)[:, 0:1]
  h = getattr(env, "_rm_height_cmd", None)
  if h is None:
    h = torch.full((env.num_envs, 1), DEFAULT_HEIGHT, device=env.device)
    env._rm_height_cmd = h
  return h


def leg_pos(env, asset_cfg: SceneEntityCfg) -> torch.Tensor:
  """[B, 4] biased encoder positions relative to default, indices 10..13.

  ``encoder_bias`` is episode-constant domain randomization.  Using the biased
  view here models a real zero-calibration error; per-sample white noise alone
  cannot teach the policy to tolerate that persistent offset.
  """
  asset: Entity = env.scene[asset_cfg.name]
  return asset.data.joint_pos_biased[:, asset_cfg.joint_ids] - \
         asset.data.default_joint_pos[:, asset_cfg.joint_ids]


def leg_vel(env, asset_cfg: SceneEntityCfg) -> torch.Tensor:
  """[B, 4] leg joint velocities, indices 16..19 (scale 0.1 applied by term)."""
  asset: Entity = env.scene[asset_cfg.name]
  return asset.data.joint_vel[:, asset_cfg.joint_ids] - \
         asset.data.default_joint_vel[:, asset_cfg.joint_ids]


def wheel_vel(env, asset_cfg: SceneEntityCfg) -> torch.Tensor:
  """[B, 2] wheel joint velocities, indices 20..21 (scale 0.1 applied by term)."""
  asset: Entity = env.scene[asset_cfg.name]
  return asset.data.joint_vel[:, asset_cfg.joint_ids] - \
         asset.data.default_joint_vel[:, asset_cfg.joint_ids]


def wheel_pos_slots(env, asset_cfg: SceneEntityCfg) -> torch.Tensor:
  """[B, 2] reserved wheel position slots, indices 14..15, contract says fixed 0."""
  asset: Entity = env.scene[asset_cfg.name]
  return torch.zeros(env.num_envs, len(asset_cfg.joint_ids), device=env.device)


def randomize_height_command(env, env_ids=None, range=(0.18, 0.34)) -> None:
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


def mode_onehot(env, jump: bool = True) -> torch.Tensor:
  """[B, 7] indices 28..34 = [normal, stair, slope, recover, JUMP, height, state_time].

  Slot 0 stays 1 (the normal-only block the deployment ships today).  When ``jump`` is
  enabled slot 4 carries the live jump request, which is the channel the DT7 ``cmd_state``
  drives on hardware, so the same 35-D contract asks for a hop.
  """
  v = torch.zeros(env.num_envs, 7, device=env.device)
  v[:, 0] = 1.0
  if jump and hasattr(env, "_rm_jump_flag"):
    v[:, 4] = env._rm_jump_flag.squeeze(-1)
  return v
