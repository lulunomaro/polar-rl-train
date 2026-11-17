"""SCUT-style fixed per-episode action and observation delays."""

from __future__ import annotations

import os

import torch

from .scut_flat_obs_noise_env import ObservationNoiseDRStage4, ScutFlatObsNoiseEnv


class ScutStyleDelayDRStage7(ObservationNoiseDRStage4):
    """Add SCUT-style fixed per-env delays to Stage 4 DR."""

    def __init__(self, env):
        super().__init__(env)
        self.action_delay_min = int(os.environ.get("SCUT_ACTION_DELAY_MIN", "1"))
        self.action_delay_max = int(os.environ.get("SCUT_ACTION_DELAY_MAX", "3"))
        self.obs_delay_min = int(os.environ.get("SCUT_OBS_DELAY_MIN", "1"))
        self.obs_delay_max = int(os.environ.get("SCUT_OBS_DELAY_MAX", "4"))
        if not (1 <= self.action_delay_min <= self.action_delay_max):
            raise ValueError("invalid SCUT action delay range")
        if not (1 <= self.obs_delay_min <= self.obs_delay_max):
            raise ValueError("invalid SCUT observation delay range")
        self.control_dt = float(env.cfg.sim.dt * env.cfg.decimation)

    def summary(self):
        row = super().summary()
        row.update(
            profile="flat_scut_delay_stage7",
            stage="joint_friction_50pct + spring_damping_25pct + external_force_torque_25pct + observation_noise_25pct + SCUT_fixed_per_episode_delays",
            delay_resampling="reset_per_env",
            action_delay_groups={
                "leg_actions": [self.action_delay_min, self.action_delay_max],
                "wheel_actions": [self.action_delay_min, self.action_delay_max],
            },
            observation_delay_groups={
                "root_ang_vel_b": [self.obs_delay_min, self.obs_delay_max],
                "projected_gravity_b": [self.obs_delay_min, self.obs_delay_max],
                "joint_pos": [self.obs_delay_min, self.obs_delay_max],
                "joint_vel": [self.obs_delay_min, self.obs_delay_max],
            },
            action_low_pass_filter=False,
            other_randomization="SCUT-style per-env fixed delays sampled at reset; no per-step delay resampling",
            missing_dr=["full_SCUT_mass_COM_material_ranges"],
        )
        return row


class ScutFlatScutDelayEnv(ScutFlatObsNoiseEnv):
    """Stage 7: Stage 4 noise plus SCUT-style per-env fixed delays."""

    def __init__(self, cfg, meta, bank):
        n = int(cfg.scene.num_envs)
        self._action_delay_min = int(os.environ.get("SCUT_ACTION_DELAY_MIN", "1"))
        self._action_delay_max = int(os.environ.get("SCUT_ACTION_DELAY_MAX", "3"))
        self._obs_delay_min = int(os.environ.get("SCUT_OBS_DELAY_MIN", "1"))
        self._obs_delay_max = int(os.environ.get("SCUT_OBS_DELAY_MAX", "4"))
        if not (1 <= self._action_delay_min <= self._action_delay_max):
            raise ValueError("invalid SCUT action delay range")
        if not (1 <= self._obs_delay_min <= self._obs_delay_max):
            raise ValueError("invalid SCUT observation delay range")
        self._action_history = torch.zeros((self._action_delay_max + 1, n, 6), device=cfg.sim.device)
        self._obs_history = torch.zeros((self._obs_delay_max + 1, n, 35), device=cfg.sim.device)
        self._action_delay_steps = torch.stack([
            torch.randint(self._action_delay_min, self._action_delay_max + 1, (n,), device=cfg.sim.device),
            torch.randint(self._action_delay_min, self._action_delay_max + 1, (n,), device=cfg.sim.device),
        ], dim=1)
        self._obs_delay_steps = torch.stack([
            torch.randint(self._obs_delay_min, self._obs_delay_max + 1, (n,), device=cfg.sim.device)
            for _ in range(4)
        ], dim=1)
        self._action_pending_reset = torch.ones(n, dtype=torch.bool, device=cfg.sim.device)
        self._obs_pending_reset = torch.ones(n, dtype=torch.bool, device=cfg.sim.device)
        super().__init__(cfg, meta, bank)
        self.full_dr = ScutStyleDelayDRStage7(self)
        self.mild_dr = self.full_dr
        self._mild_dr = self.full_dr

    @staticmethod
    def _gather(history, delay_steps, dim):
        n = history.shape[1]
        idx = delay_steps.view(1, n, 1).expand(1, n, dim)
        return history.gather(0, idx).squeeze(0)

    def _pre_physics_step(self, actions):
        actions = actions.to(self.device).clamp(-6.0, 6.0)
        reset_ids = self._action_pending_reset
        if bool(reset_ids.any()):
            self._action_history[:, reset_ids] = actions[reset_ids].unsqueeze(0)
            self._action_pending_reset[reset_ids] = False
        self._action_history[1:].copy_(self._action_history[:-1].clone())
        self._action_history[0].copy_(actions)
        delayed = actions.clone()
        delayed[:, :4] = self._gather(self._action_history[:, :, :4], self._action_delay_steps[:, 0], 4)
        delayed[:, 4:] = self._gather(self._action_history[:, :, 4:], self._action_delay_steps[:, 1], 2)
        super()._pre_physics_step(delayed)

    def _get_observations(self):
        obs = super()._get_observations()
        policy = obs["policy"]
        if policy.shape[-1] != 35:
            return obs
        reset_ids = self._obs_pending_reset
        if bool(reset_ids.any()):
            self._obs_history[:, reset_ids] = policy[reset_ids].unsqueeze(0)
            self._obs_pending_reset[reset_ids] = False
        self._obs_history[1:].copy_(self._obs_history[:-1].clone())
        self._obs_history[0].copy_(policy)
        delayed = policy.clone()
        groups = [(slice(4, 7), 0), (slice(7, 10), 1), (slice(10, 16), 2), (slice(16, 22), 3)]
        for group, col in groups:
            dim = group.stop - group.start
            delayed[:, group] = self._gather(self._obs_history[:, :, group], self._obs_delay_steps[:, col], dim)
        obs["policy"] = delayed
        return obs

    def _reset_idx(self, ids):
        super()._reset_idx(ids)
        ids = torch.as_tensor(ids, device=self.device, dtype=torch.long).flatten()
        if ids.numel() == 0:
            return
        m = ids.numel()
        self._action_delay_steps[ids, 0] = torch.randint(
            self._action_delay_min, self._action_delay_max + 1, (m,), device=self.device)
        self._action_delay_steps[ids, 1] = torch.randint(
            self._action_delay_min, self._action_delay_max + 1, (m,), device=self.device)
        for col in range(4):
            self._obs_delay_steps[ids, col] = torch.randint(
                self._obs_delay_min, self._obs_delay_max + 1, (m,), device=self.device)
        self._action_pending_reset[ids] = True
        self._obs_pending_reset[ids] = True
