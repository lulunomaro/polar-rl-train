"""UNDEPLOYED candidate for gradual world-directed spin translation.

Default first goal is .15 m/s mean world progress, not the final .5 goal.
Uses the inspected target SDK's heading_w.torch API and 3-D body command.
Runtime Isaac, contact, reward and PPO acceptance are still required.
"""
import math
import os
import torch
from isaaclab.envs.mdp.commands.velocity_command import UniformVelocityCommand
from spin_translation_math import body_command


class DirectionalSpinMixCommand(UniformVelocityCommand):
    def __init__(self, cfg, env):
        if cfg.heading_command or cfg.rel_heading_envs != 0:
            raise ValueError('Heading correction must be disabled')
        super().__init__(cfg, env)
        self.pure_fraction = float(os.environ.get('RM_PURE_SPIN_FRACTION', '.30'))
        self.moving_fraction = float(os.environ.get('RM_MOVING_SPIN_FRACTION', '.20'))
        self.progress_goal = float(os.environ.get('RM_SPIN_WORLD_PROGRESS_M_S', '.15'))
        self.body_limit = float(os.environ.get('RM_SPIN_BODY_SPEED_LIMIT_M_S', '1.5'))
        if not 0 < self.progress_goal <= .5:
            raise ValueError('User scope caps this candidate world progress goal at .5 m/s')
        if not 0 < self.body_limit <= 1.5:
            raise ValueError('Cannot widen the retained body command range')
        if self.pure_fraction <= 0 or self.moving_fraction <= 0:
            raise ValueError('Retain both pure and moving spin samples')
        if self.pure_fraction + self.moving_fraction >= 1 - cfg.rel_standing_envs:
            raise ValueError('Retain nonempty stand and straight samples')
        self.is_pure_spin = torch.zeros(self.num_envs, dtype=torch.bool, device=self.device)
        self.is_moving_spin = torch.zeros_like(self.is_pure_spin)
        self.world_direction = torch.zeros(self.num_envs, device=self.device)
        self.signed_yaw = torch.zeros_like(self.world_direction)
        self._mode_rng = torch.Generator(device=self.device)
        self._mode_rng.manual_seed(int(env.cfg.seed or 0) + 15485863)

    def _resample_command(self, env_ids):
        super()._resample_command(env_ids)
        ids = torch.as_tensor(env_ids, dtype=torch.long, device=self.device)
        random = torch.rand((len(ids), 4), generator=self._mode_rng, device=self.device)
        available = ~self.is_standing_env[ids]
        p_pure = self.pure_fraction / (1 - self.cfg.rel_standing_envs)
        p_moving = self.moving_fraction / (1 - self.cfg.rel_standing_envs)
        pure = available & (random[:, 0] < p_pure)
        moving = available & (random[:, 0] >= p_pure) & (random[:, 0] < p_pure + p_moving)
        self.is_pure_spin[ids] = pure
        self.is_moving_spin[ids] = moving
        self.is_heading_env[ids] = False
        spin = pure | moving
        yaw = (1 + random[:, 1]) * torch.where(random[:, 2] < .5, -1., 1.)
        self.signed_yaw[ids] = torch.where(spin, yaw, 0.)
        self.world_direction[ids] = 2 * math.pi * random[:, 3] - math.pi
        self.vel_command_b[ids, 2] = self.signed_yaw[ids]
        self.vel_command_b[ids[pure], :2] = 0.
        self._write_moving(ids[moving])

    def _write_moving(self, ids):
        # Exact API from the inspected target SDK; runtime readback remains pending.
        heading = self.robot.data.heading_w.torch[ids]
        vx, vy = body_command(self.progress_goal, self.world_direction[ids], heading, self.body_limit)
        self.vel_command_b[ids, 0] = vx
        self.vel_command_b[ids, 1] = vy
        self.vel_command_b[ids, 2] = self.signed_yaw[ids]

    def _update_command(self):
        super()._update_command()
        self._write_moving(self.is_moving_spin.nonzero(as_tuple=False).flatten())
        # Standing cannot be overwritten by any moving mode.
        self.vel_command_b[self.is_standing_env, :] = 0.


def configure(cfg):
    term = cfg.commands.twist
    term.class_type = DirectionalSpinMixCommand
    term.heading_command = False
    term.rel_heading_envs = 0.
    term.ranges.heading = None
    term.ranges.ang_vel_z = (-2., 2.)
    term.rel_standing_envs = .1
    term.resampling_time_range = (8., 12.)
    cfg.curriculum.gyro_window = None
