"""Stage 2 incremental DR: stage 1 + spring damping 25%."""

from __future__ import annotations

import os
import torch

from .scut_flat_joint_friction_env import PartialJointFrictionDR, ScutFlatJointFrictionEnv
from .scut_flat_env import tensor


class SpringDampingDR(PartialJointFrictionDR):
    """Keep stage 1 DR and add a scaled gas-spring damping perturbation."""

    def __init__(self, env):
        super().__init__(env)
        self.spring_damping_fraction = float(os.environ.get('SPRING_DAMPING_FRACTION', '0.25'))
        if not (0.0 <= self.spring_damping_fraction <= 1.0):
            raise ValueError('SPRING_DAMPING_FRACTION must be in [0, 1]')
        self.spring_damping_scale = torch.ones(env.num_envs, device=env.device)

    def __call__(self, env, env_ids):
        ids = (torch.arange(env.num_envs, device=env.device)
               if env_ids is None else torch.as_tensor(env_ids, device=env.device, dtype=torch.long))
        super().__call__(env, ids)
        if len(ids) == 0:
            return
        half = 0.5 * self.spring_damping_fraction
        self.spring_damping_scale[ids] = torch.empty(
            len(ids), device=env.device
        ).uniform_(1.0 - half, 1.0 + half, generator=self.generator)

    def summary(self):
        row = super().summary()
        half = 0.5 * self.spring_damping_fraction
        row.update(
            profile='flat_spring_damping_stage2',
            stage='joint_friction_50pct + spring_damping_25pct',
            spring_damping_fraction=self.spring_damping_fraction,
            spring_damping_scale_range=[1.0 - half, 1.0 + half],
            missing_dr=[
                'observation_noise', 'observation_delay', 'action_delay',
                'external_force_torque',
            ],
        )
        return row


class ScutFlatSpringDampingEnv(ScutFlatJointFrictionEnv):
    """Stage 2: joint friction 50% plus spring damping 25%."""

    def __init__(self, cfg, meta, bank):
        super().__init__(cfg, meta, bank)
        self.full_dr = SpringDampingDR(self)
        self.mild_dr = self.full_dr
        self._mild_dr = self.full_dr

    def _apply_action(self):
        super()._apply_action()
        if not self.gas_ids:
            return
        qd = tensor(self.robot.data.joint_vel)[:, self.gas_ids]
        extra = (self.full_dr.spring_damping_scale[:, None] - 1.0) * 3.0 * qd
        extra = torch.clamp(extra, -10.0, 10.0)
        self.robot.set_joint_effort_target(extra, joint_ids=self.gas_ids)
