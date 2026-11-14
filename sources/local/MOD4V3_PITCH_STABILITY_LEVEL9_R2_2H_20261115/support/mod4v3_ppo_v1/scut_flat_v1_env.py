"""Flat-v1: V30 flat + airborne/pre-contact/landing recovery."""
import math
import torch
from mod4v1_scut.math_ops import quat_from_euler_xyz
from .scut_flat_env import ScutFlatEnv, configuration, tensor
from .scut_flat_rewards import make_reward_class_v1


class ScutFlatV1Env(ScutFlatEnv):
    enforce_closure_reset = False
    """Flat-v1 with 30% airborne resets and SCUT state-machine observations."""

    air_reset_fraction = 0.30

    def _make_reward(self,meta):
        return make_reward_class_v1(meta)(self.view,self.num_envs,self.device)

    def prepare_endpoint(self):
        super().prepare_endpoint()
        reward = self.reward
        if getattr(reward.cfg, 'enable_state_machines', False):
            # The original V14 environment updates the airborne state after
            # building observations. The custom DirectRLEnv does not inherit
            # that hook, so invoke the same state manager explicitly.
            reward._on_command_updated()
            reward.state_machine_manager.on_observation_step(reward)

    def _reset_idx(self, ids):
        ids = ids.long()
        super()._reset_idx(ids)
        if ids.numel() == 0:
            return
        n = int(ids.numel())
        air_mask = torch.rand(n, device=self.device, generator=self.reset_generator) < self.air_reset_fraction
        air_ids = ids[air_mask]
        if air_ids.numel() == 0:
            return
        m = int(air_ids.numel())
        root = tensor(self.robot.data.default_root_state)[air_ids].clone()
        root[:, :3] += self.scene.env_origins[air_ids]
        root[:, 2] = self.scene.env_origins[air_ids, 2] + torch.empty(m, device=self.device).uniform_(0.12, 0.42)
        roll = torch.empty(m, device=self.device).uniform_(-0.10, 0.10)
        pitch = torch.empty(m, device=self.device).uniform_(-0.20, 0.20)
        yaw = torch.empty(m, device=self.device).uniform_(-math.pi, math.pi)
        root[:, 3:7] = quat_from_euler_xyz(roll, pitch, yaw)
        root[:, 7:].zero_()
        root[:, 7] = torch.empty(m, device=self.device).uniform_(-2.5, 2.5)
        root[:, 8] = torch.empty(m, device=self.device).uniform_(-0.5, 0.5)
        root[:, 12] = torch.empty(m, device=self.device).uniform_(-0.5, 0.5)
        self.robot.write_root_state_to_sim(root, env_ids=air_ids)
        self.mild_dr(self, air_ids)
        self.height[air_ids] = torch.empty(m, device=self.device).uniform_(0.18, 0.43)
        self.command[air_ids, 0] = torch.empty(m, device=self.device).uniform_(-2.5, 2.5)
        self.command[air_ids, 1] = 0.0
        self.command[air_ids, 2] = torch.empty(m, device=self.device).uniform_(-0.5 * math.pi, 0.5 * math.pi)
        self.standing_env[air_ids] = False
        self.heading_env[air_ids] = False
        self.heading_target[air_ids] = 0.0
        self.actions[air_ids] = 0.0
        self.torque[air_ids] = 0.0
        # Reset state-machine buffers after the air pose is actually written.
        self.reward.reset(air_ids)
        self.reward.command.copy_(self.command)
        self.reward.height_cmd.copy_(self.height)
        self.reward._invalidate_step_caches()
