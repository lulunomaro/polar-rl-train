"""MOD4v3 Flat-Robust bridge: SCUT-style ground reset on top of Flat-v2."""
from __future__ import annotations
import math
import torch
from isaaclab.utils.math import quat_from_euler_xyz
from .scut_flat_v2_env import ScutFlatV2Env
from .scut_flat_env import tensor


class ScutFlatRobustEnv(ScutFlatV2Env):
    """Flat-v2 continuation with randomized ground recovery.

    This is a bridge, not a claim of full SCUT event parity.  The existing
    MildDRv3 core DR remains active.  A fraction of resets additionally gets
    random root height/orientation and a short zero-torque release, matching
    the purpose of SCUT's predefined_reset_ground without changing the
    action/observation contract.
    """

    ground_reset_fraction = 0.20
    zero_torque_control_steps = 10  # 10 * 0.02 s = 0.2 s

    def __init__(self, cfg, meta, bank):
        self.zero_torque_remaining = torch.zeros(
            int(cfg.scene.num_envs), dtype=torch.long, device=cfg.sim.device
        )
        super().__init__(cfg, meta, bank)

    def _pre_physics_step(self, actions):
        super()._pre_physics_step(actions)
        self.zero_torque_remaining = torch.clamp(
            self.zero_torque_remaining - 1, min=0
        )

    def _reset_idx(self, ids):
        ids = torch.as_tensor(ids, device=self.device, dtype=torch.long).flatten()
        super()._reset_idx(ids)
        if ids.numel() == 0:
            return
        selected = torch.rand(
            ids.numel(), device=self.device, generator=self.reset_generator
        ) < float(self.ground_reset_fraction)
        reset_ids = ids[selected]
        if reset_ids.numel() == 0:
            return
        n = int(reset_ids.numel())
        root = tensor(self.robot.data.default_root_state)[reset_ids].clone()
        root[:, :3] += self.scene.env_origins[reset_ids]
        root[:, 2] = self.scene.env_origins[reset_ids, 2] + torch.empty(
            n, device=self.device
        ).uniform_(0.20, 0.34)
        roll = torch.empty(n, device=self.device).uniform_(-0.15, 0.15)
        pitch = torch.empty(n, device=self.device).uniform_(-0.15, 0.15)
        yaw = torch.empty(n, device=self.device).uniform_(-math.pi, math.pi)
        root[:, 3:7] = quat_from_euler_xyz(roll, pitch, yaw)
        root[:, 7:] = 0.0
        self.robot.write_root_state_to_sim(root, env_ids=reset_ids)
        self.actions[reset_ids] = 0.0
        self.torque[reset_ids] = 0.0
        self.zero_torque_remaining[reset_ids] = int(self.zero_torque_control_steps)
        self.reward.command.copy_(self.command)
        self.reward.height_cmd.copy_(self.height)
        self.reward._invalidate_step_caches()
