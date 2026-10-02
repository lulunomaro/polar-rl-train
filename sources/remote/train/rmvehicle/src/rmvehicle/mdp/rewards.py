"""Task specific rewards for the dual wheel-leg robot."""
from __future__ import annotations

import math
import torch

from mjlab.entity import Entity
from mjlab.managers.scene_entity_config import SceneEntityCfg
from mjlab.sensor import ContactSensor

_CACHE: dict = {}


def _body_ids(env, names: tuple[str, ...]):
  key = (id(env), names)
  if key not in _CACHE:
    asset: Entity = env.scene["robot"]
    ids, _ = asset.find_bodies(tuple(names))
    _CACHE[key] = ids
  return _CACHE[key]


def measured_height(env, asset_cfg: SceneEntityCfg = SceneEntityCfg("robot"),
                    body_names=("thigh_L", "wheel_L", "thigh_R", "wheel_R")) -> torch.Tensor:
  """Vertical hip->wheel distance [B, 1]; the same quantity the deployment commands.

  `body_names` is (thigh_L, wheel_L, thigh_R, wheel_R) for the model variant in use.
  """
  asset: Entity = env.scene[asset_cfg.name]
  hip_l, whl_l, hip_r, whl_r = _body_ids(env, tuple(body_names))
  z = asset.data.body_link_pos_w
  h_l = z[:, hip_l, 2] - z[:, whl_l, 2]
  h_r = z[:, hip_r, 2] - z[:, whl_r, 2]
  return (h_l + h_r) * 0.5


def height_tracking(env, command_name: str = "height", std: float = 0.10,
                    asset_cfg: SceneEntityCfg = SceneEntityCfg("robot"),
                    body_names=("thigh_L", "wheel_L", "thigh_R", "wheel_R")) -> torch.Tensor:
  from .observations import height_command
  err = measured_height(env, asset_cfg, body_names) - height_command(env, command_name).squeeze(-1)
  return torch.exp(-(err / std) ** 2)


def wheel_contact_fraction(env, sensor_name: str) -> torch.Tensor:
  sensor = env.scene[sensor_name]
  assert isinstance(sensor, ContactSensor)
  found = sensor.data.found
  assert found is not None
  return (found > 0).float().reshape(found.shape[0], -1).mean(dim=1)


def wheel_contact_obs(env, sensor_name: str) -> torch.Tensor:
  """Same as :func:`wheel_contact_fraction` but shaped [B, 1] for observations."""
  return wheel_contact_fraction(env, sensor_name).unsqueeze(-1)


def wheel_slip(env, sensor_name: str, asset_cfg: SceneEntityCfg = SceneEntityCfg("robot"),
               wheel_joints=("wheel_L_joint", "wheel_R_joint")) -> torch.Tensor:
  """Squared difference between the two wheel speeds (drives yaw, keep it small)."""
  asset: Entity = env.scene[asset_cfg.name]
  ids, _ = asset.find_joints(tuple(wheel_joints))
  return (asset.data.joint_vel[:, ids[0]] - asset.data.joint_vel[:, ids[1]]) ** 2


def leg_symmetry(env, asset_cfg: SceneEntityCfg = SceneEntityCfg("robot"),
                 leg_joints=("hip_L_joint", "knee_L_joint", "hip_R_joint", "knee_R_joint")) -> torch.Tensor:
  """Left/right symmetry of the four policy-driven leg joints, in contract order."""
  asset: Entity = env.scene[asset_cfg.name]
  ids, _ = asset.find_joints(tuple(leg_joints))
  q = asset.data.joint_pos[:, ids] - asset.data.default_joint_pos[:, ids]
  return (q[:, 0] - q[:, 2]) ** 2 + (q[:, 1] - q[:, 3]) ** 2


def lin_vel_z_l2(env, asset_cfg: SceneEntityCfg = SceneEntityCfg("robot")) -> torch.Tensor:
  asset: Entity = env.scene[asset_cfg.name]
  return (asset.data.root_link_lin_vel_b[:, 2] ** 2)


def ang_vel_xy_l2(env, asset_cfg: SceneEntityCfg = SceneEntityCfg("robot")) -> torch.Tensor:
  asset: Entity = env.scene[asset_cfg.name]
  return (asset.data.root_link_ang_vel_b[:, :2] ** 2).sum(dim=1)


def joint_power(env, asset_cfg: SceneEntityCfg = SceneEntityCfg("robot")) -> torch.Tensor:
  asset: Entity = env.scene[asset_cfg.name]
  return (asset.data.qfrc_actuator * asset.data.joint_vel).abs().sum(dim=1)

def action_l2(env, action_slice: tuple[int, int] | None = None) -> torch.Tensor:
  """Penalise the raw policy action magnitude.

  The action-rate and second-difference terms only penalise CHANGES; a policy whose
  std grows without bound can still hold a huge constant action and dodge them.  This
  term is the direct counterweight to the entropy bonus.
  """
  a = env.action_manager.action
  if action_slice is not None:
    a = a[:, action_slice[0]:action_slice[1]]
  return torch.sum(torch.square(a), dim=1)


def gyro_track_wide(env, command_name: str = "twist", band_floor: float = 6.0,
                    max_tilt: float = 0.35) -> torch.Tensor:
    # Wide-band yaw tracking, shaped as a TRIANGULAR kernel instead of a Gaussian.
    #
    # WHY.  v14 measured the failure exactly: the commanded yaw window had opened to 13.2 rad/s
    # while the policy plateaued at 5.53 rad/s (0.88 rev/s), because the tracking reward is
    # exp(-err^2/std^2) and at err = 8.5 rad/s that is 1e-16 - literally no gradient, so PPO had
    # no reason to push the wheels harder.  Fudan's open-source wheel-leg project
    # (refs/fudan_rl_wheel_leg-main, plane/.../legged_robot.py:_reward_tracking_ang_vel_enhance)
    # hits the same wall and solves the same way: they run a SECOND, 10x wider yaw-tracking
    # kernel alongside the narrow one.  That is independent confirmation of the diagnosis.
    #
    # SHAPE.  score = clamp(1 - |wz_cmd - wz| / band, 0, 1), band = max(band_floor, |wz_cmd|).
    # Compared with a wide Gaussian it is bounded on [0,1], it keeps a CONSTANT slope right up to
    # the command (no flat tail at all), and - unlike a "spin as fast as you can" term - it is
    # maximised exactly at the commanded rate, so the robot is never paid to overshoot a small
    # command.  The narrow exp() term stays in place for precision near the target.
    #
    # GATE.  Only upright envs score: a falling chassis also produces yaw rate, and that is
    # precisely what fooled v14's command curriculum into widening the window.
    robot = env.scene["robot"]
    cmd = env.command_manager.get_command(command_name)[:, 2]
    w = robot.data.root_link_ang_vel_b[:, 2]
    g = robot.data.projected_gravity_b
    upright = ((-g[:, 2]) > math.cos(max_tilt)).to(w.dtype)
    band = torch.clamp(cmd.abs(), min=band_floor)
    return ((1.0 - (cmd - w).abs() / band).clamp(0.0, 1.0)) * upright
