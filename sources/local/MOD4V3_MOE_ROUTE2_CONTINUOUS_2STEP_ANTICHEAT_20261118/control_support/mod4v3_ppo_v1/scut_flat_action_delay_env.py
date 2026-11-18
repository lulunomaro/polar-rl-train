"""Stage 6 incremental DR: Stage 5 + one-step action delay."""

from __future__ import annotations

import os

import torch

from .scut_flat_obs_delay_env import ObservationDelayDRStage5, ScutFlatObsDelayEnv


class ActionDelayDRStage6(ObservationDelayDRStage5):
    """Keep Stage 5 observation delay and delay actions by one control step."""

    def __init__(self, env):
        super().__init__(env)
        self.action_delay_steps = int(os.environ.get("ACTION_DELAY_STEPS", "1"))
        self.action_delay_probability = float(os.environ.get("ACTION_DELAY_PROB", "1.0"))
        if self.action_delay_steps != 1:
            raise ValueError("Stage 6 currently supports exactly one action-delay step")
        if not (0.0 <= self.action_delay_probability <= 1.0):
            raise ValueError("ACTION_DELAY_PROB must be in [0, 1]")
        self.control_dt = float(env.cfg.sim.dt * env.cfg.decimation)

    def summary(self):
        row = super().summary()
        pct = int(round(self.action_delay_probability * 100))
        profile = "flat_action_delay_stage6b" if self.action_delay_probability < 1.0 else "flat_action_delay_stage6"
        row.update(
            profile=profile,
            stage=f"joint_friction_50pct + spring_damping_25pct + external_force_torque_25pct + observation_noise_25pct + observation_delay_1step + action_delay_1step_probability_{pct}pct",
            action_delay_control_steps=self.action_delay_steps,
            action_delay_s=self.action_delay_steps * self.control_dt,
            action_delay_probability=self.action_delay_probability,
            other_randomization="stage5 observation delay plus probabilistic one-step action delay",
            missing_dr=["full_SCUT_mass_COM_material_ranges"],
        )
        return row


class ScutFlatActionDelayEnv(ScutFlatObsDelayEnv):
    """Stage 6: Stage 5 plus a one-control-step action delay."""

    def __init__(self, cfg, meta, bank):
        n = int(cfg.scene.num_envs)
        self._action_delay_history = torch.zeros((2, n, 6), device=cfg.sim.device)
        self._action_delay_pending_reset = torch.ones(n, dtype=torch.bool, device=cfg.sim.device)
        super().__init__(cfg, meta, bank)
        self.full_dr = ActionDelayDRStage6(self)
        self.mild_dr = self.full_dr
        self._mild_dr = self.full_dr

    def _pre_physics_step(self, actions):
        actions = actions.to(self.device).clamp(-6.0, 6.0)
        reset_ids = self._action_delay_pending_reset
        if bool(reset_ids.any()):
            # The first action after reset is immediate; subsequent actions are
            # delayed by exactly one control step.
            self._action_delay_history[:, reset_ids] = actions[reset_ids].unsqueeze(0)
            self._action_delay_pending_reset[reset_ids] = False
        self._action_delay_history[1].copy_(self._action_delay_history[0])
        self._action_delay_history[0].copy_(actions)
        delayed = self._action_delay_history[1].clone()
        prob = float(self.full_dr.action_delay_probability)
        use_delay = torch.rand(self.num_envs, device=self.device) < prob
        applied = torch.where(use_delay[:, None], delayed, actions)
        super()._pre_physics_step(applied)

    def _reset_idx(self, ids):
        super()._reset_idx(ids)
        ids = torch.as_tensor(ids, device=self.device, dtype=torch.long).flatten()
        if ids.numel() > 0:
            self._action_delay_pending_reset[ids] = True
