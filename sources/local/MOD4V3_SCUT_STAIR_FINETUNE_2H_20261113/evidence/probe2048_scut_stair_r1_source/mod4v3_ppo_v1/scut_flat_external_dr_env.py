"""Stage 3 incremental DR: stage 2 + external force/torque 25%."""

from __future__ import annotations

import os
import torch

from .scut_flat_spring_damping_env import ScutFlatSpringDampingEnv, SpringDampingDR


class ExternalDRStage3(SpringDampingDR):
    def __init__(self, env):
        super().__init__(env)
        self.external_fraction = float(os.environ.get('EXTERNAL_DR_FRACTION', '0.25'))
        if not (0.0 <= self.external_fraction <= 1.0):
            raise ValueError('EXTERNAL_DR_FRACTION must be in [0, 1]')

    def summary(self):
        row = super().summary()
        row.update(
            profile='flat_external_dr_stage3',
            stage='joint_friction_50pct + spring_damping_25pct + external_force_torque_25pct',
            external_fraction=self.external_fraction,
            external_force_range_n=[-10.0 * self.external_fraction, 10.0 * self.external_fraction],
            external_torque_range_nm=[-1.0 * self.external_fraction, 1.0 * self.external_fraction],
            external_interval_s=[5.0, 10.0],
            external_hold_control_steps=10,
            missing_dr=['observation_noise', 'observation_delay', 'action_delay', 'full_SCUT_mass_COM_material_ranges'],
        )
        return row


class ScutFlatExternalDREnv(ScutFlatSpringDampingEnv):
    """Stage 3: stage-2 DR plus a scaled periodic external wrench."""

    def __init__(self, cfg, meta, bank):
        super().__init__(cfg, meta, bank)
        self.full_dr = ExternalDRStage3(self)
        self.mild_dr = self.full_dr
        self._mild_dr = self.full_dr
        n = int(self.num_envs)
        self._external_force = torch.zeros((n, 3), device=self.device)
        self._external_torque = torch.zeros((n, 3), device=self.device)
        self._external_hold = torch.zeros(n, dtype=torch.long, device=self.device)
        self._external_timer = torch.empty(n, device=self.device).uniform_(5.0, 10.0)
        self._control_dt = float(cfg.sim.dt * cfg.decimation)

    def _pre_physics_step(self, actions):
        super()._pre_physics_step(actions)
        self._update_external_wrench()

    def _update_external_wrench(self):
        n = int(self.num_envs)
        self._external_timer -= self._control_dt
        self._external_hold.sub_(1).clamp_(min=0)
        event = self._external_timer <= 0.0
        if bool(event.any()):
            ids = event.nonzero().flatten()
            self._external_timer[event] = torch.empty(ids.numel(), device=self.device).uniform_(5.0, 10.0)
            f = float(self.full_dr.external_fraction)
            self._external_force[event] = torch.empty((ids.numel(), 3), device=self.device).uniform_(-10.0 * f, 10.0 * f)
            self._external_torque[event] = torch.empty((ids.numel(), 3), device=self.device).uniform_(-1.0 * f, 1.0 * f)
            self._external_hold[event] = 10
        active = self._external_hold > 0
        forces = torch.zeros((n, 1, 3), device=self.device)
        torques = torch.zeros((n, 1, 3), device=self.device)
        forces[active, 0] = self._external_force[active]
        torques[active, 0] = self._external_torque[active]
        self.robot.set_external_force_and_torque(
            forces, torques, env_ids=torch.arange(n, device=self.device),
            body_ids=[self.full_dr.base_id],
        )

    def _reset_idx(self, ids):
        ids = torch.as_tensor(ids, device=self.device, dtype=torch.long).flatten()
        super()._reset_idx(ids)
        if ids.numel() == 0:
            return
        n = int(ids.numel())
        self._external_force[ids] = 0.0
        self._external_torque[ids] = 0.0
        self._external_hold[ids] = 0
        self._external_timer[ids] = torch.empty(n, device=self.device).uniform_(5.0, 10.0)
