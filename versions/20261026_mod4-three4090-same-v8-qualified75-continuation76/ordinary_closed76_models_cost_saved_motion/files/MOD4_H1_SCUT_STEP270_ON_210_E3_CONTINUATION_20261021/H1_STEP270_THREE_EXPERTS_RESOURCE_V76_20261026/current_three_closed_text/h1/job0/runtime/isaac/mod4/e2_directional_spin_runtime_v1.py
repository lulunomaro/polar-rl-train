"""Undeployed SDK candidate: world progress, pure yaw, and actual transitions.

References remain a three-value BODY twist: projected vx, zero vy, signed yaw.
World progress is a complete-cycle requirement, not an instantaneous velocity.
No mass/PD/spring/reward/PPO changes. Real Isaac/PPO acceptance is pending.
"""
import math
import os

import torch
from isaaclab.envs.mdp.commands.velocity_command import UniformVelocityCommand
from spin_translation_math import body_command


def transition_yaw(elapsed, target):
    """12s start/hold/brake/stop/reverse/hold/brake/stop command profile."""
    scale = torch.where(elapsed < 1., elapsed,
             torch.where(elapsed < 4., 1.,
             torch.where(elapsed < 5., 5. - elapsed,
             torch.where(elapsed < 6., 0.,
             torch.where(elapsed < 7., -(elapsed - 6.),
             torch.where(elapsed < 10., -1.,
             torch.where(elapsed < 11., elapsed - 11., 0.)))))))
    return target * scale


class DirectionalSpinCommand(UniformVelocityCommand):
    def __init__(self, cfg, env):
        if cfg.heading_command or cfg.rel_heading_envs != 0:
            raise ValueError('Disable heading correction before directional spin')
        super().__init__(cfg, env)
        self.pure_fraction = float(os.environ.get('RM_PURE_SPIN_FRACTION', '.30'))
        self.moving_fraction = float(os.environ.get('RM_MOVING_SPIN_FRACTION', '.20'))
        self.transition_within_pure = float(os.environ.get('RM_SPIN_TRANSITION_WITHIN_PURE', str(1 / 3)))
        self.progress_goal = float(os.environ.get('RM_SPIN_WORLD_PROGRESS_M_S', '.15'))
        self.body_limit = float(os.environ.get('RM_SPIN_BODY_SPEED_LIMIT_M_S', '1.5'))
        self.pure_max = float(os.environ.get('RM_SPIN_MAX_RAD_S', str(4*math.pi)))
        if not 0 < self.progress_goal <= .5 or not 2 * self.progress_goal <= self.body_limit <= 1.5:
            raise ValueError('World progress .15/.3/.5 requires an unclipped feasible body projection')
        if not 2 <= self.pure_max <= 4*math.pi or not 0 < self.transition_within_pure < 1:
            raise ValueError('Preserved pure spin cap must remain within verified 4pi')
        if not 0 < self.pure_fraction or not 0 < self.moving_fraction:
            raise ValueError('Both pure and moving samples must remain')
        if self.pure_fraction + self.moving_fraction >= 1 - cfg.rel_standing_envs:
            raise ValueError('Retain standing and straight samples')
        if cfg.resampling_time_range[0] < 12:
            raise ValueError('A transition must complete before command resampling')
        self.is_pure_spin = torch.zeros(self.num_envs, dtype=torch.bool, device=self.device)
        self.is_moving_spin = torch.zeros_like(self.is_pure_spin)
        self.is_transition_spin = torch.zeros_like(self.is_pure_spin)
        self.world_direction = torch.zeros(self.num_envs, device=self.device)
        self.signed_yaw = torch.zeros_like(self.world_direction)
        self.phase_elapsed = torch.zeros_like(self.world_direction)
        self._mode_rng = torch.Generator(device=self.device)
        self._mode_rng.manual_seed(int(env.cfg.seed or 0) + 15485863)
        self._dt = float(env.step_dt)
        self.manual_evaluation_mode = False

    def set_manual_evaluation_mode(self):
        """Frozen probes own their command references; never override them."""
        self.manual_evaluation_mode = True
        self.is_pure_spin[:] = False
        self.is_moving_spin[:] = False
        self.is_transition_spin[:] = False

    def _resample_command(self, env_ids):
        super()._resample_command(env_ids)
        ids = torch.as_tensor(env_ids, dtype=torch.long, device=self.device)
        u = torch.rand((len(ids), 5), generator=self._mode_rng, device=self.device)
        available = ~self.is_standing_env[ids]
        pure_end = self.pure_fraction / (1 - self.cfg.rel_standing_envs)
        moving_end = pure_end + self.moving_fraction / (1 - self.cfg.rel_standing_envs)
        pure = available & (u[:, 0] < pure_end)
        moving = available & (u[:, 0] >= pure_end) & (u[:, 0] < moving_end)
        transition = pure & (u[:, 4] < self.transition_within_pure)
        self.is_pure_spin[ids] = pure
        self.is_moving_spin[ids] = moving
        self.is_transition_spin[ids] = transition
        self.is_heading_env[ids] = False
        sign = torch.where(u[:, 2] < .5, -1., 1.)
        rate = torch.where(moving, torch.full_like(u[:, 1], 4.0), 1 + (self.pure_max - 1) * u[:, 1])
        self.signed_yaw[ids] = torch.where(pure | moving, sign * rate, 0.)
        self.world_direction[ids] = 2 * math.pi * u[:, 3] - math.pi
        self.phase_elapsed[ids] = 0.
        self.vel_command_b[ids, 2] = self.signed_yaw[ids]
        self.vel_command_b[ids[pure], :2] = 0.
        self._write_dynamic(ids)

    def _write_dynamic(self, ids):
        moving = ids[self.is_moving_spin[ids]]
        heading = self.robot.data.heading_w.torch[moving]
        vx, vy = body_command(self.progress_goal, self.world_direction[moving], heading, self.body_limit)
        self.vel_command_b[moving, 0] = vx
        self.vel_command_b[moving, 1] = vy
        self.vel_command_b[moving, 2] = self.signed_yaw[moving]
        transitions = ids[self.is_transition_spin[ids]]
        self.vel_command_b[transitions, 2] = transition_yaw(self.phase_elapsed[transitions], self.signed_yaw[transitions])
        self.vel_command_b[self.is_standing_env, :] = 0.

    def _update_command(self):
        super()._update_command()
        if not self.manual_evaluation_mode:
            self._write_dynamic(torch.arange(self.num_envs, device=self.device))
            self.phase_elapsed += self._dt


def configure(cfg):
    term = cfg.commands.twist
    term.class_type = DirectionalSpinCommand
    term.heading_command = False
    term.rel_heading_envs = 0.
    term.ranges.heading = None
    limit = float(os.environ.get('RM_SPIN_MAX_RAD_S', '3.'))
    term.ranges.ang_vel_z = (-limit, limit)
    term.ranges.lin_vel_y = (0., 0.)
    term.rel_standing_envs = .1
    # Explicit new curriculum: complete turns and full train-time transitions.
    term.resampling_time_range = (12., 16.)
    cfg.curriculum.gyro_window = None


def audit(env):
    term = env.command_manager.get_term('twist')
    if not isinstance(term, DirectionalSpinCommand):
        raise RuntimeError('Directional stage must install its actual SDK command class')
    c = term.command
    if term.cfg.heading_command or term.is_heading_env.any() or not torch.isfinite(c).all():
        raise RuntimeError('Heading override or nonfinite command')
    pure, moving = term.is_pure_spin, term.is_moving_spin
    if (pure & moving).any() or (moving & term.is_standing_env).any():
        raise RuntimeError('Command modes overlap')
    if pure.any() and c[pure, :2].abs().max() > 1e-6:
        raise RuntimeError('Preserved pure spin may not translate')
    if c[:, 1].abs().max() > 1e-6 or c[:, 2].abs().max() > term.pure_max + 1e-5:
        raise RuntimeError('Lateral body motion or yaw beyond admitted cap')
    projection_error = 0.
    if moving.any() and not term.manual_evaluation_mode:
        vx, _ = body_command(term.progress_goal, term.world_direction[moving],
                             term.robot.data.heading_w.torch[moving], term.body_limit)
        projection_error = float((vx - c[moving, 0]).abs().max())
        if projection_error > 1e-6 or c[moving, 2].abs().max() > 4.00001:
            raise RuntimeError('World-to-body reference or moving yaw bound mismatch')
    return {'stage': 'directional_spin_v1', 'command_frame': 'body',
            'manual_frozen_evaluation': term.manual_evaluation_mode,
            'world_progress_goal_m_s': term.progress_goal, 'projection_error_m_s': projection_error,
            'pure_fraction_actual': float(pure.float().mean()),
            'moving_fraction_actual': float(moving.float().mean()),
            'transition_fraction_actual': float(term.is_transition_spin.float().mean()),
            'stand_fraction_actual': float(term.is_standing_env.float().mean()),
            'pure_max_rad_s': term.pure_max, 'moving_yaw_max_rad_s': 4.,
            'world_progress_achieved': 'unmeasured; actual displacement and complete cycles required'}
