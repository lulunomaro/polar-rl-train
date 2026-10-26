"""MOD4 first spin specialist: sustained pure yaw mixed with stand/straight.

No translation during spin in stage one. Existing 3-D body twist observation,
hardware/rewards/PPO and closed-chain pose library remain intact. The independent
selector RNG does not consume the pose library's RNG. This is a MOD4 curriculum,
not a claim of byte-identical SCUT special-mode implementation.
"""
import os
import torch
from isaaclab.envs.mdp.commands.velocity_command import UniformVelocityCommand


class PureYawMixCommand(UniformVelocityCommand):
    def __init__(self, cfg, env):
        if cfg.heading_command or cfg.rel_heading_envs != 0:
            raise ValueError('Pure-yaw stage must disable heading correction')
        super().__init__(cfg, env)
        self.spin_fraction = float(os.environ.get('RM_SPIN_FRACTION', '.30'))
        self.spin_min = float(os.environ.get('RM_SPIN_MIN_RAD_S', '1.0'))
        self.spin_max = float(os.environ.get('RM_SPIN_MAX_RAD_S', '2.0'))
        if not 0 < self.spin_fraction < 1-cfg.rel_standing_envs:
            raise ValueError('Spin/run/stand fractions must be nonempty')
        if not 0 < self.spin_min <= self.spin_max <= 4*torch.pi:
            raise ValueError('Rate curriculum cannot exceed two revolutions per second')
        self.is_spin_env = torch.zeros(self.num_envs, dtype=torch.bool, device=self.device)
        self._spin_rng = torch.Generator(device=self.device)
        self._spin_rng.manual_seed(int(env.cfg.seed or 0) + 7919)

    def _resample_command(self, env_ids):
        super()._resample_command(env_ids)
        ids = torch.as_tensor(env_ids, device=self.device, dtype=torch.long)
        probability = self.spin_fraction / (1-self.cfg.rel_standing_envs)
        u = torch.rand((len(ids), 3), device=self.device, generator=self._spin_rng)
        spin = (~self.is_standing_env[ids]) & (u[:, 0] < probability)
        self.is_spin_env[ids] = spin
        self.is_heading_env[ids] = False
        self.vel_command_b[ids, 2] = 0
        spin_ids = ids[spin]
        self.vel_command_b[spin_ids, :2] = 0
        rate = self.spin_min + (self.spin_max-self.spin_min)*u[spin, 1]
        sign = torch.where(u[spin, 2] < .5, -1., 1.)
        self.vel_command_b[spin_ids, 2] = sign*rate


def configure(cfg):
    if os.environ.get('RM_SPIN_STAGE') == 'world_directional_v1':
        from directional_spin_runtime import configure as world_configure
        return world_configure(cfg)
    term = cfg.commands.twist
    term.class_type = PureYawMixCommand
    term.heading_command = False
    term.rel_heading_envs = 0.
    term.ranges.heading = None
    limit = float(os.environ.get('RM_SPIN_MAX_RAD_S', '3.'))
    term.ranges.ang_vel_z = (-limit, limit)
    term.rel_standing_envs = .1
    term.resampling_time_range = (4., 8.)
    cfg.curriculum.gyro_window = None


def audit(env):
    if os.environ.get('RM_SPIN_STAGE') == 'world_directional_v1':
        from directional_spin_runtime import audit as world_audit
        return world_audit(env)
    term = env.command_manager.get_term('twist')
    cmd = term.command
    yaw = cmd[:, 2]
    spin = yaw.abs() > 1e-6
    if term.cfg.heading_command or term.is_heading_env.any():
        raise RuntimeError('Heading correction overrides the spin command')
    if yaw.abs().max() > float(os.environ['RM_SPIN_MAX_RAD_S']) + .00001:
        raise RuntimeError('Unexpected widening beyond the current registered yaw limit')
    if spin.any() and cmd[spin, :2].abs().max() > 1e-6:
        raise RuntimeError('Stage one only admits PURE spin, no mixed-frame translation')
    return {'stage': 'pure_yaw_rate_v1', 'registered_limit_rad_s': float(os.environ['RM_SPIN_MAX_RAD_S']), 'heading_correction': False,
            'yaw_abs_max': float(yaw.abs().max()),
            'spin_fraction_actual': float(spin.float().mean()),
            'stand_fraction_actual': float((cmd.abs().sum(1)<1e-6).float().mean()),
            'spin_positive_fraction': float((yaw>1e-6).float().mean()),
            'spin_negative_fraction': float((yaw< -1e-6).float().mean()),
            'spin_command_body_translation_max': float(cmd[spin,:2].abs().max()) if spin.any() else 0.}
