"""Flat-v2: flat base + small-gyro, high-speed and heading curriculum."""
import torch

from .scut_flat_env import ScutFlatEnv
from .scut_flat_rewards import configuration_v2, make_reward_class


class ScutFlatV2Env(ScutFlatEnv):
    """Flat-v0 plus SCUT-style gyro / high-speed command composition.

    SCUT's Flat-v2 command ranges keep lateral velocity at zero, so this stage
    deliberately does not invent a lateral command.  It focuses on forward/back,
    height, heading, small gyro and high-speed straight tracking.
    """

    enforce_closure_reset = False
    command_vy = (0.0, 0.0)

    def __init__(self, cfg, meta, bank):
        super().__init__(cfg, meta, bank)
        # This experiment only targets the validated 0..2.2 m/s envelope.
        # Keep the Flat-v2 composition intact; just stop sampling commands
        # above the speed range we actually need.
        self.command_vx = (-2.2, 2.2)

    def _make_reward(self, meta):
        return make_reward_class(meta, cfg_factory=configuration_v2)(
            self.view, self.num_envs, self.device
        )

    def _sample_command(self, ids):
        ids = torch.as_tensor(ids, device=self.device, dtype=torch.long).flatten()
        n = int(ids.numel())
        if n == 0:
            return

        vx = torch.empty(n, device=self.device).uniform_(*self.command_vx)
        vy = torch.zeros(n, device=self.device)
        wz = torch.empty(n, device=self.device).uniform_(*self.command_wz)
        height = torch.empty(n, device=self.device).uniform_(*self.height_range)
        standing = torch.rand(n, device=self.device) < self.standing_fraction
        heading = (torch.rand(n, device=self.device) < self.heading_fraction) & (~standing)
        target = torch.empty(n, device=self.device).uniform_(*self.heading_range)
        sign = torch.where(torch.rand(n, device=self.device) < 0.5, -1.0, 1.0)
        mode = torch.rand(n, device=self.device)

        # 15% gyro 6.28..10.21 rad/s.
        gyro_low = mode < 0.15
        m = int(gyro_low.sum())
        if m:
            vx[gyro_low] = torch.empty(m, device=self.device).uniform_(-0.10, 0.10)
            wz[gyro_low] = torch.empty(m, device=self.device).uniform_(6.283185307179586, 10.210176124166829) * sign[gyro_low]
            heading[gyro_low] = False
            standing[gyro_low] = False

        # 15% gyro 10.21..14.14 rad/s.
        gyro_high = (mode >= 0.15) & (mode < 0.30)
        m = int(gyro_high.sum())
        if m:
            vx[gyro_high] = torch.empty(m, device=self.device).uniform_(-0.10, 0.10)
            wz[gyro_high] = torch.empty(m, device=self.device).uniform_(10.210176124166829, 14.137166941154069) * sign[gyro_high]
            heading[gyro_high] = False
            standing[gyro_high] = False

        # 30% high-speed straight tracking, matching SCUT's special mode.
        high = (mode >= 0.30) & (mode < 0.60)
        m = int(high.sum())
        if m:
            vx[high] = torch.empty(m, device=self.device).uniform_(2.0, 2.2) * sign[high]
            wz[high] = torch.empty(m, device=self.device).uniform_(-6.283185307179586, 6.283185307179586)
            heading[high] = False

        vx[standing] = 0.0
        vy[standing] = 0.0
        wz[standing] = 0.0
        heading[standing] = False
        target[~heading] = 0.0

        self.command[ids, 0] = vx
        self.command[ids, 1] = vy
        self.command[ids, 2] = wz
        self.heading_env[ids] = heading
        self.standing_env[ids] = standing
        self.heading_target[ids] = target
        self.height[ids] = height
        self.command_timer[ids] = torch.empty(n, device=self.device).uniform_(*self.command_resample)
