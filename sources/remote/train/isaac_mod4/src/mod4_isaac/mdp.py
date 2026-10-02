"""MOD4 task terms: the 35-D deployment contract, its rewards and its domain randomisation.

The plant is the delivered USD (incoming/rm2025_mod4/isaac/robot.usd), NOT a re-import of the
MJCF.  PhysX closes the six loops and the four sprocket couplings itself; verified by
isaac/mod4/probe_mimic.py (closure error <= 0.5 mm, chain error <= 5e-5 rad).

Observation vector = the wheelbipe 35-D contract, see train/deploy/contract_rm2025_later.json:
  0..2   twist command (vx, 0, wz)
  3      target hip->wheel height x 5
  4..6   base angular velocity x 0.5
  7..9   projected gravity
  10..13 leg joint positions relative to default (biased encoders)
  14..15 wheel position slots, fixed 0
  16..19 leg joint velocities x 0.1
  20..21 wheel joint velocities x 0.1
  22..27 previous raw action
  28..34 mode one-hot (slot 0 = normal)
"""
from __future__ import annotations

from typing import TYPE_CHECKING

import torch

from isaaclab.envs.mdp.actions import (
    JointPositionAction,
    JointPositionActionCfg,
    JointVelocityAction,
    JointVelocityActionCfg,
)
from isaaclab.managers import ActionTerm, CommandTerm, CommandTermCfg, SceneEntityCfg
from isaaclab.utils.configclass import configclass

from .robot_cfg import IMPORT_CONTRACT

if TYPE_CHECKING:
    from isaaclab.envs import ManagerBasedRLEnv

# Contract order.  The exported slot order is a permutation of this, see
# export_action_permutation in train/deploy/contract_rm2025_later.json.
LEG_JOINTS = ("left_hip", "left_crank", "right_hip", "right_crank")
WHEEL_JOINTS = ("left_wheel_spin", "right_wheel_spin")
HEIGHT_BODIES = ("left_thigh", "left_wheel", "right_thigh", "right_wheel")


def _t(x):
    """ProxyArray -> torch, plain tensors unchanged."""
    return x.torch if hasattr(x, "torch") else x


def measured_height(env: "ManagerBasedRLEnv", body_names=HEIGHT_BODIES) -> torch.Tensor:
    """Hip->wheel vertical distance averaged over both legs: what the height command means."""
    robot = env.scene["robot"]
    ids = [robot.body_names.index(n) for n in body_names]
    z = _t(robot.data.body_pos_w)
    h_l = z[:, ids[0], 2] - z[:, ids[1], 2]
    h_r = z[:, ids[2], 2] - z[:, ids[3], 2]
    return (h_l + h_r) * 0.5


def _joint_ids(robot, names) -> list[int]:
    return [robot.joint_names.index(n) for n in names]


# --------------------------------------------------------------------------------------
# commands
# --------------------------------------------------------------------------------------
class HeightCommand(CommandTerm):
    cfg: HeightCommandCfg

    def __init__(self, cfg: HeightCommandCfg, env: "ManagerBasedRLEnv"):
        super().__init__(cfg, env)
        self.height = torch.zeros(self.num_envs, 1, device=self.device)
        self.metrics["error_height"] = torch.zeros(self.num_envs, device=self.device)

    def __str__(self) -> str:
        return "height"

    @property
    def command(self) -> torch.Tensor:
        return self.height

    def _resample_command(self, env_ids):
        lo, hi = self.cfg.ranges
        self.height[env_ids, 0] = torch.empty(len(env_ids), device=self.device).uniform_(lo, hi)

    def _update_metrics(self):
        self.metrics["error_height"] = (measured_height(self._env) - self.height[:, 0]).abs()

    def _update_command(self):
        pass

    def _set_debug_vis_impl(self, debug_vis: bool):
        pass


@configclass
class HeightCommandCfg(CommandTermCfg):
    """Uniform hip->wheel height command, metres.

    Declared after HeightCommand on purpose: a dataclass field default of None would
    shadow any later class-level assignment, so class_type has to be the real class here.
    """

    class_type: type[CommandTerm] = HeightCommand
    # Resampled by the reset event, never mid-episode.
    resampling_time_range: tuple[float, float] = (9.5e6, 9.5e6)
    ranges: tuple[float, float] = (0.18, 0.34)


# --------------------------------------------------------------------------------------
# action terms: contract order, drive-side effort noise, biased encoder coordinate
# --------------------------------------------------------------------------------------
class LegPositionAction(JointPositionAction):
    """Leg position servo, including the two drive-side randomisations we train against."""

    def process_actions(self, actions: torch.Tensor):
        cfg: LegPositionActionCfg = self.cfg  # type: ignore[assignment]
        if cfg.effort_noise_scale:
            noise = 1.0 + (torch.rand_like(actions) * 2.0 - 1.0) * cfg.effort_noise_scale
            actions = actions * noise
        super().process_actions(actions)
        bias = getattr(self._env, "_mod4_encoder_bias", None)
        if bias is not None:
            # The firmware commands the servo in encoder coordinates and does not know the
            # zero-calibration error, so the physical target it reaches is (target - bias).
            self._processed_actions = self._processed_actions - bias[:, self._joint_ids]


class WheelVelocityAction(JointVelocityAction):
    """Wheel velocity servo (a position zero error does not shift a velocity command)."""

    def process_actions(self, actions: torch.Tensor):
        cfg: WheelVelocityActionCfg = self.cfg  # type: ignore[assignment]
        if cfg.effort_noise_scale:
            noise = 1.0 + (torch.rand_like(actions) * 2.0 - 1.0) * cfg.effort_noise_scale
            actions = actions * noise
        super().process_actions(actions)


@configclass
class LegPositionActionCfg(JointPositionActionCfg):
    class_type: type[ActionTerm] = LegPositionAction
    effort_noise_scale: float = 0.03


@configclass
class WheelVelocityActionCfg(JointVelocityActionCfg):
    class_type: type[ActionTerm] = WheelVelocityAction
    effort_noise_scale: float = 0.02


# --------------------------------------------------------------------------------------
# observations
# --------------------------------------------------------------------------------------
def twist_commands(env: "ManagerBasedRLEnv", command_name: str = "twist") -> torch.Tensor:
    cmd = env.command_manager.get_command(command_name)
    return torch.cat((cmd[:, 0:1], torch.zeros_like(cmd[:, 0:1]), cmd[:, 2:3]), dim=1)


def height_command_obs(env: "ManagerBasedRLEnv", command_name: str = "height") -> torch.Tensor:
    return env.command_manager.get_command(command_name)[:, 0:1]


def mode_onehot(env: "ManagerBasedRLEnv") -> torch.Tensor:
    v = torch.zeros(env.num_envs, 7, device=env.device)
    v[:, 0] = 1.0
    return v


def leg_pos_biased(env: "ManagerBasedRLEnv", asset_cfg: SceneEntityCfg) -> torch.Tensor:
    robot = env.scene[asset_cfg.name]
    ids = _joint_ids(robot, LEG_JOINTS)
    q = _t(robot.data.joint_pos)[:, ids]
    default = _t(robot.data.default_joint_pos)[:, ids]
    bias = getattr(env, "_mod4_encoder_bias", None)
    if bias is not None:
        q = q + bias[:, ids]
    return q - default


def wheel_pos_slots(env: "ManagerBasedRLEnv", asset_cfg: SceneEntityCfg) -> torch.Tensor:
    return torch.zeros(env.num_envs, len(WHEEL_JOINTS), device=env.device)


def leg_vel(env: "ManagerBasedRLEnv", asset_cfg: SceneEntityCfg) -> torch.Tensor:
    robot = env.scene[asset_cfg.name]
    ids = _joint_ids(robot, LEG_JOINTS)
    return _t(robot.data.joint_vel)[:, ids] - _t(robot.data.default_joint_vel)[:, ids]


def wheel_vel(env: "ManagerBasedRLEnv", asset_cfg: SceneEntityCfg) -> torch.Tensor:
    robot = env.scene[asset_cfg.name]
    ids = _joint_ids(robot, WHEEL_JOINTS)
    return _t(robot.data.joint_vel)[:, ids] - _t(robot.data.default_joint_vel)[:, ids]


# --------------------------------------------------------------------------------------
# rewards
# --------------------------------------------------------------------------------------
def height_tracking(env: "ManagerBasedRLEnv", std: float = 0.06,
                    command_name: str = "height") -> torch.Tensor:
    err = measured_height(env) - env.command_manager.get_command(command_name)[:, 0]
    return torch.exp(-(err / std) ** 2)


def wheel_contact_fraction(env: "ManagerBasedRLEnv", sensor_name: str = "wheel_contact",
                           force_threshold: float = 1.0) -> torch.Tensor:
    sensor = env.scene[sensor_name]
    forces = _filtered_forces(sensor)
    found = (forces.norm(dim=-1) > force_threshold).float()
    return found.flatten(start_dim=1).mean(dim=1)


def ground_contact(env: "ManagerBasedRLEnv", sensor_name: str = "chassis_contact",
                   threshold: float = 1.0) -> torch.Tensor:
    """Terminate only on chassis<->ground contact; legs brushing the chassis does not count."""
    sensor = env.scene[sensor_name]
    forces = _filtered_forces(sensor)
    return (forces.norm(dim=-1) > threshold).flatten(start_dim=1).any(dim=1)
def _filtered_forces(sensor):
    """Contact forces against the sensor filter (the ground), not against everything."""
    matrix = getattr(sensor.data, "force_matrix_w", None)
    if matrix is not None:
        return _t(matrix)  # (num_envs, num_sensors, num_filters, 3)
    return _t(sensor.data.net_forces_w).unsqueeze(2)


def leg_symmetry(env: "ManagerBasedRLEnv", asset_cfg: SceneEntityCfg = SceneEntityCfg("robot")) -> torch.Tensor:
    robot = env.scene[asset_cfg.name]
    ids = _joint_ids(robot, LEG_JOINTS)
    q = _t(robot.data.joint_pos)[:, ids] - _t(robot.data.default_joint_pos)[:, ids]
    return (q[:, 0] - q[:, 2]) ** 2 + (q[:, 1] - q[:, 3]) ** 2


def lin_vel_z_l2(env: "ManagerBasedRLEnv", asset_cfg: SceneEntityCfg = SceneEntityCfg("robot")) -> torch.Tensor:
    robot = env.scene[asset_cfg.name]
    return _t(robot.data.root_lin_vel_b)[:, 2] ** 2


def ang_vel_xy_l2(env: "ManagerBasedRLEnv", asset_cfg: SceneEntityCfg = SceneEntityCfg("robot")) -> torch.Tensor:
    robot = env.scene[asset_cfg.name]
    return (_t(robot.data.root_ang_vel_b)[:, :2] ** 2).sum(dim=1)


def joint_power(env: "ManagerBasedRLEnv", asset_cfg: SceneEntityCfg = SceneEntityCfg("robot")) -> torch.Tensor:
    robot = env.scene[asset_cfg.name]
    torque = _t(robot.data.applied_torque)
    vel = _t(robot.data.joint_vel)
    return (torque * vel).abs().sum(dim=1)


def action_l2(env: "ManagerBasedRLEnv", action_slice: tuple[int, int] | None = None) -> torch.Tensor:
    a = env.action_manager.action
    if action_slice is not None:
        a = a[:, action_slice[0]:action_slice[1]]
    return torch.sum(torch.square(a), dim=1)


def action_acc_l2(env: "ManagerBasedRLEnv") -> torch.Tensor:
    """Second difference of the raw action, kept from the mjlab task (wheel chatter)."""
    a = env.action_manager.action
    if not hasattr(env, "_mod4_prev_prev_action") or env._mod4_prev_prev_action is None:
        env._mod4_prev_prev_action = a.clone()
    acc = a - 2.0 * env.action_manager.prev_action + env._mod4_prev_prev_action
    env._mod4_prev_prev_action = a.clone()
    return torch.sum(torch.square(acc), dim=1)


# --------------------------------------------------------------------------------------
# events: resets and domain randomisation
# --------------------------------------------------------------------------------------
def randomize_height_command(env: "ManagerBasedRLEnv", env_ids,
                             command_name: str = "height", range=(0.18, 0.34)) -> None:
    term = env.command_manager.get_term(command_name)
    lo, hi = range
    term.height[env_ids, 0] = torch.empty(len(env_ids), device=term.device).uniform_(lo, hi)


def randomize_encoder_bias(env: "ManagerBasedRLEnv", env_ids, offset: float = 0.01) -> None:
    """Episode-constant zero-calibration error on the four leg encoders [rad]."""
    robot = env.scene["robot"]
    if getattr(env, "_mod4_encoder_bias", None) is None:
        env._mod4_encoder_bias = torch.zeros(env.num_envs, len(robot.joint_names), device=env.device)
    ids = _joint_ids(robot, LEG_JOINTS)
    env._mod4_encoder_bias[env_ids] = 0.0
    env._mod4_encoder_bias[env_ids.unsqueeze(1), torch.tensor(ids, device=env.device).unsqueeze(0)] = \
        (torch.rand(len(env_ids), len(ids), device=env.device) * 2.0 - 1.0) * offset


def _sel(env: "ManagerBasedRLEnv", env_ids, robot, names):
    # int32, not int64: Isaac Lab 3 routes the index arrays straight into warp kernels.
    env_ids_t = torch.as_tensor(env_ids, device=env.device).flatten().to(torch.int32)
    joint_ids = torch.tensor(_joint_ids(robot, names), device=env.device, dtype=torch.int32)
    return env_ids_t, joint_ids


def _uniform(env, rows: int, cols: int, lo_hi) -> torch.Tensor:
    return torch.empty(rows, cols, device=env.device).uniform_(lo_hi[0], lo_hi[1])


def randomize_effort_scale(env: "ManagerBasedRLEnv", env_ids,
                           joint_names=LEG_JOINTS + WHEEL_JOINTS,
                           scale_range=(0.75, 1.25),
                           asset_cfg: SceneEntityCfg = SceneEntityCfg("robot")) -> None:
    """Actuator output strength: what the drive can actually deliver that episode."""
    robot = env.scene[asset_cfg.name]
    base = getattr(env, "_mod4_base_effort_limit", None)
    if base is None:
        base = _t(robot.data.joint_effort_limits).clone()
        env._mod4_base_effort_limit = base
    env_ids_t, joint_ids = _sel(env, env_ids, robot, joint_names)
    rows, cols = env_ids_t.unsqueeze(1), joint_ids.unsqueeze(0)
    limits = base[rows, cols] * _uniform(env, env_ids_t.numel(), joint_ids.numel(), scale_range)
    robot.write_joint_effort_limit_to_sim_index(limits=limits, joint_ids=joint_ids, env_ids=env_ids_t)


def randomize_gas_spring(env: "ManagerBasedRLEnv", env_ids,
                         stiffness_range=(0.85, 1.15), damping_range=(0.7, 1.3),
                         asset_cfg: SceneEntityCfg = SceneEntityCfg("robot")) -> None:
    """Nitrogen spring: the least identified part of the plant, so it gets the widest DR."""
    robot = env.scene[asset_cfg.name]
    base_s = getattr(env, "_mod4_base_stiffness", None)
    base_d = getattr(env, "_mod4_base_damping", None)
    if base_s is None:
        base_s = _t(robot.data.joint_stiffness).clone()
        base_d = _t(robot.data.joint_damping).clone()
        env._mod4_base_stiffness, env._mod4_base_damping = base_s, base_d
    env_ids_t, joint_ids = _sel(env, env_ids, robot, ("left_gas_slide", "right_gas_slide"))
    rows, cols = env_ids_t.unsqueeze(1), joint_ids.unsqueeze(0)
    stiffness = base_s[rows, cols] * _uniform(env, env_ids_t.numel(), joint_ids.numel(), stiffness_range)
    damping = base_d[rows, cols] * _uniform(env, env_ids_t.numel(), joint_ids.numel(), damping_range)
    robot.write_joint_stiffness_to_sim_index(stiffness=stiffness, joint_ids=joint_ids, env_ids=env_ids_t)
    robot.write_joint_damping_to_sim_index(damping=damping, joint_ids=joint_ids, env_ids=env_ids_t)


def randomize_gas_spring_friction(env: "ManagerBasedRLEnv", env_ids, friction_range=(0.0, 0.60),
                                  asset_cfg: SceneEntityCfg = SceneEntityCfg("robot")) -> None:
    """Seal friction of the nitrogen spring, delivered as an absolute value (0..0.6 N)."""
    robot = env.scene[asset_cfg.name]
    base = getattr(env, "_mod4_base_friction", None)
    if base is None:
        base = _t(robot.data.joint_friction_coeff).clone()
        env._mod4_base_friction = base
    env_ids_t, joint_ids = _sel(env, env_ids, robot, ("left_gas_slide", "right_gas_slide"))
    rows, cols = env_ids_t.unsqueeze(1), joint_ids.unsqueeze(0)
    coeff = base[rows, cols] + _uniform(env, env_ids_t.numel(), joint_ids.numel(), friction_range)
    robot.write_joint_friction_coefficient_to_sim_index(joint_friction_coeff=coeff, joint_ids=joint_ids, env_ids=env_ids_t)

def nan_detection(env: "ManagerBasedRLEnv", asset_cfg: SceneEntityCfg = SceneEntityCfg("robot")) -> torch.Tensor:
    robot = env.scene[asset_cfg.name]
    bad = ~torch.isfinite(_t(robot.data.joint_pos)).all(dim=1)
    bad |= ~torch.isfinite(_t(robot.data.joint_vel)).all(dim=1)
    return bad


def base_height_obs(env: "ManagerBasedRLEnv") -> torch.Tensor:
    """[B, 1] measured hip->wheel height, critic only."""
    return measured_height(env).unsqueeze(-1)


def leg_encoder_bias_obs(env: "ManagerBasedRLEnv", asset_cfg: SceneEntityCfg) -> torch.Tensor:
    """[B, 4] the episode-constant zero-calibration error itself, critic only."""
    robot = env.scene[asset_cfg.name]
    ids = _joint_ids(robot, LEG_JOINTS)
    bias = getattr(env, "_mod4_encoder_bias", None)
    if bias is None:
        return torch.zeros(env.num_envs, len(ids), device=env.device)
    return bias[:, ids]


def applied_torque_legs(env: "ManagerBasedRLEnv", asset_cfg: SceneEntityCfg) -> torch.Tensor:
    robot = env.scene[asset_cfg.name]
    ids = _joint_ids(robot, LEG_JOINTS)
    return _t(robot.data.applied_torque)[:, ids]


def commands_vel_range_curriculum(env: "ManagerBasedRLEnv", env_ids, command_name: str = "twist",
                                  vx_range=(-1.5, 2.8), wz_range=(-14.0, 14.0),
                                  start_step: int = 4000, ramp_steps: int = 16000) -> dict:
    """Open the command window once velocity tracking exists, not before.

    The mjlab task learned this the hard way: handing a fresh policy a 2.8 m/s / 14 rad/s
    window made falling over the best return.  Here the configured window is the start
    point and the contract window is the target.
    """
    term = env.command_manager.get_term(command_name)
    key = "_mod4_curriculum_base_ranges"
    if not hasattr(env, key):
        r = term.cfg.ranges
        setattr(env, key, {"lin_vel_x": tuple(r.lin_vel_x), "ang_vel_z": tuple(r.ang_vel_z)})
    base = getattr(env, key)
    t = float(getattr(env, "common_step_counter", 0))
    s = 0.0 if t <= start_step else min(1.0, (t - start_step) / float(max(1, ramp_steps)))
    r = term.cfg.ranges
    r.lin_vel_x = (base["lin_vel_x"][0] + (vx_range[0] - base["lin_vel_x"][0]) * s,
                   base["lin_vel_x"][1] + (vx_range[1] - base["lin_vel_x"][1]) * s)
    r.ang_vel_z = (base["ang_vel_z"][0] + (wz_range[0] - base["ang_vel_z"][0]) * s,
                   base["ang_vel_z"][1] + (wz_range[1] - base["ang_vel_z"][1]) * s)
    return {"command_window_scale": s}


CLOSURES = IMPORT_CONTRACT["closures"]


def closure_max_error(env: "ManagerBasedRLEnv", asset_cfg: SceneEntityCfg = SceneEntityCfg("robot")) -> torch.Tensor:
    """Per-pair anchor separation of the six delivered loop closures, in metres.

    This is the delivery guard (isaac/mod4/probe_mimic.py fixed its quaternion order): PhysX has
    to hold every closure, otherwise training converges on a machine that is not the real one.
    Isaac Lab 3 stores body_quat_w as (x, y, z, w), which quat_apply expects.
    """
    from isaaclab.utils.math import quat_apply

    robot = env.scene[asset_cfg.name]
    pos = _t(robot.data.body_pos_w)
    quat = _t(robot.data.body_quat_w)
    errors = []
    for spec in CLOSURES.values():
        a = robot.body_names.index(spec["body0"])
        b = robot.body_names.index(spec["body1"])
        pa = torch.tensor(spec["anchor0_m"], device=env.device).expand(env.num_envs, 3)
        pb = torch.tensor(spec["anchor1_m"], device=env.device).expand(env.num_envs, 3)
        wa = pos[:, a] + quat_apply(quat[:, a], pa)
        wb = pos[:, b] + quat_apply(quat[:, b], pb)
        errors.append((wa - wb).norm(dim=-1))
    return torch.stack(errors, dim=1)


def closure_break(env: "ManagerBasedRLEnv", tolerance: float = 0.005,
                  asset_cfg: SceneEntityCfg = SceneEntityCfg("robot")) -> torch.Tensor:
    """Terminate an environment whose closed chain has come apart (acceptance limit is 2 mm)."""
    return (closure_max_error(env, asset_cfg) > tolerance).any(dim=1)
