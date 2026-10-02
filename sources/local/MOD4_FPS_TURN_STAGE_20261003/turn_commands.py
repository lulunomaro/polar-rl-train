"""Isolated low-speed BODY-frame arc candidate, not a world-motion controller.

Keep 10% stand, 45% straight, 30% pure spin; introduce only 15% low-speed
forward/reverse turns. Hardware, observations, reward and PPO stay unchanged.
The added selector uses an independent RNG, preserving the reset-bank sequence.
"""
import os
import torch
from spin_commands import PureYawMixCommand, configure as configure_pure


class TurnMixCommand(PureYawMixCommand):
    def __init__(self, cfg, env):
        super().__init__(cfg, env)
        self.turn_fraction = float(os.environ.get('RM_TURN_FRACTION', '.15'))
        self.turn_speed_min = .15
        self.turn_speed_max = float(os.environ.get('RM_TURN_SPEED_MAX', '.6'))
        self.turn_yaw_min = .2
        self.turn_yaw_max = float(os.environ.get('RM_TURN_YAW_MAX', '.8'))
        if not 0 < self.turn_fraction < 1-cfg.rel_standing_envs-self.spin_fraction:
            raise ValueError('The old stand, straight and spin courses must remain nonempty')
        if not .15 <= self.turn_speed_max <= .6 or not .2 <= self.turn_yaw_max <= .8:
            raise ValueError('First arc candidate must stay within conservative bounds')
        self.is_turn_env = torch.zeros(self.num_envs, dtype=torch.bool, device=self.device)
        self._turn_rng = torch.Generator(device=self.device)
        self._turn_rng.manual_seed(int(env.cfg.seed or 0) + 15401)

    def _resample_command(self, env_ids):
        super()._resample_command(env_ids)
        ids = torch.as_tensor(env_ids, dtype=torch.long, device=self.device)
        u = torch.rand((len(ids), 5), device=self.device, generator=self._turn_rng)
        probability = self.turn_fraction / (1-self.cfg.rel_standing_envs-self.spin_fraction)
        turn = (~self.is_standing_env[ids]) & (~self.is_spin_env[ids]) & (u[:, 0] < probability)
        self.is_turn_env[ids] = turn
        selected = ids[turn]
        speed = self.turn_speed_min + (self.turn_speed_max-self.turn_speed_min)*u[turn, 1]
        yaw = self.turn_yaw_min + (self.turn_yaw_max-self.turn_yaw_min)*u[turn, 2]
        self.vel_command_b[selected, 0] = speed*torch.where(u[turn, 3] < .5, -1., 1.)
        self.vel_command_b[selected, 1] = 0.
        self.vel_command_b[selected, 2] = yaw*torch.where(u[turn, 4] < .5, -1., 1.)


def configure(cfg):
    configure_pure(cfg)
    cfg.commands.twist.class_type = TurnMixCommand


def audit(env):
    term = env.command_manager.get_term('twist')
    c = term.command
    if term.cfg.heading_command or term.is_heading_env.any() or not torch.isfinite(c).all():
        raise RuntimeError('Unexpected heading override or nonfinite turn command')
    spin = (c[:, 2].abs() > 1e-6) & (c[:, 0].abs() <= 1e-6)
    turn = (c[:, 2].abs() > 1e-6) & (c[:, 0].abs() > 1e-6)
    if c[:, 1].abs().max() > 1e-6:
        raise RuntimeError('This BODY-frame arc course does not request lateral sliding')
    if spin.any() and c[spin, 2].abs().max() > term.spin_max + 1e-5:
        raise RuntimeError('Pure yaw exceeded the separately registered cap')
    if turn.any() and (c[turn, 0].abs().max() > term.turn_speed_max + 1e-5
                       or c[turn, 2].abs().max() > term.turn_yaw_max + 1e-5):
        raise RuntimeError('Low-speed turn bounds exceeded')
    return {'stage': 'body_turn_v1', 'command_frame': 'body', 'heading_correction': False,
            'stand_fraction': float((c.abs().sum(1) < 1e-6).float().mean()),
            'turn_fraction': float(turn.float().mean()), 'pure_spin_fraction': float(spin.float().mean()),
            'turn_forward_left': int((turn & (c[:, 0] > 0) & (c[:, 2] > 0)).sum()),
            'turn_forward_right': int((turn & (c[:, 0] > 0) & (c[:, 2] < 0)).sum()),
            'turn_reverse_left': int((turn & (c[:, 0] < 0) & (c[:, 2] > 0)).sum()),
            'turn_reverse_right': int((turn & (c[:, 0] < 0) & (c[:, 2] < 0)).sum()),
            'turn_speed_cap': term.turn_speed_max, 'turn_yaw_cap': term.turn_yaw_max,
            'pure_yaw_cap': term.spin_max, 'world_directed_translation_implemented': False}
