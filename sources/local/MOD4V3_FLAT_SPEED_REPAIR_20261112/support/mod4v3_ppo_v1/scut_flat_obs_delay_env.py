"""Stage 5 incremental DR: Stage 4 + one-step observation delay."""

from __future__ import annotations

import os

import torch

from .scut_flat_obs_noise_env import ObservationNoiseDRStage4, ScutFlatObsNoiseEnv


class ObservationDelayDRStage5(ObservationNoiseDRStage4):
    """Keep Stage 4 noise and delay policy observations by one control step."""

    def __init__(self, env):
        super().__init__(env)
        self.obs_delay_steps = int(os.environ.get("OBS_DELAY_STEPS", "1"))
        if self.obs_delay_steps != 1:
            raise ValueError("Stage 5 currently supports exactly one observation-delay step")
        self.control_dt = float(env.cfg.sim.dt * env.cfg.decimation)

    def summary(self):
        row = super().summary()
        row.update(
            profile="flat_obs_delay_stage5",
            stage="joint_friction_50pct + spring_damping_25pct + external_force_torque_25pct + observation_noise_25pct + observation_delay_1step",
            observation_delay_control_steps=self.obs_delay_steps,
            observation_delay_s=self.obs_delay_steps * self.control_dt,
            other_randomization="stage4 noise plus one-step policy-observation delay",
            missing_dr=["action_delay", "full_SCUT_mass_COM_material_ranges"],
        )
        return row


class ScutFlatObsDelayEnv(ScutFlatObsNoiseEnv):
    """Stage 5: Stage 4 plus a one-control-step policy observation delay."""

    def __init__(self, cfg, meta, bank):
        n = int(cfg.scene.num_envs)
        self._obs_delay_history = torch.zeros((2, n, 35), device=cfg.sim.device)
        self._obs_delay_pending_reset = torch.ones(n, dtype=torch.bool, device=cfg.sim.device)
        super().__init__(cfg, meta, bank)
        self.full_dr = ObservationDelayDRStage5(self)
        self.mild_dr = self.full_dr
        self._mild_dr = self.full_dr

    def _get_observations(self):
        obs = super()._get_observations()
        policy = obs["policy"]
        if policy.shape[-1] != 35:
            return obs
        reset_ids = self._obs_delay_pending_reset
        if bool(reset_ids.any()):
            # Start every new episode with the current observation, then delay
            # subsequent policy observations by exactly one control step.
            self._obs_delay_history[:, reset_ids] = policy[reset_ids].unsqueeze(0)
            self._obs_delay_pending_reset[reset_ids] = False
        self._obs_delay_history[1].copy_(self._obs_delay_history[0])
        self._obs_delay_history[0].copy_(policy)
        obs["policy"] = self._obs_delay_history[1].clone()
        return obs

    def _reset_idx(self, ids):
        super()._reset_idx(ids)
        ids = torch.as_tensor(ids, device=self.device, dtype=torch.long).flatten()
        if ids.numel() > 0:
            self._obs_delay_pending_reset[ids] = True
