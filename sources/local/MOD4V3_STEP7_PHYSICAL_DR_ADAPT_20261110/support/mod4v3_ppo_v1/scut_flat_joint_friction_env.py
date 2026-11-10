"""Stage 1 incremental DR: 75m partial-DR base + joint friction."""

from __future__ import annotations

import math
import os
import torch
import warp as wp

from .scut_flat_robust_env import ScutFlatRobustEnv
from .scut_mild_dr import MildDRv3
from .scut_flat_env import tensor


def _transform_array(value):
    return wp.from_torch(value.contiguous(), dtype=wp.transformf)


def _joint_default(robot, name, num_envs, device):
    value = getattr(robot.data, name, None)
    if value is None:
        return None
    value = tensor(value).to(device).clone()
    if value.ndim == 1:
        value = value.unsqueeze(0).expand(num_envs, -1).clone()
    return value


class PartialJointFrictionDR(MildDRv3):
    """Preserve the 75m partial-DR bundle and add joint friction only."""

    def __init__(self, env):
        super().__init__(env)
        self.body_names = list(self.robot.body_names)
        self.base_id = next(
            (self.body_names.index(name) for name in ('chassis', 'base_link', 'base')
             if name in self.body_names),
            None,
        )
        if self.base_id is None:
            raise ValueError('No MOD4 base body found for joint-friction DR')
        self.all_shapes = list(self.wheel_shapes) + list(self.nonwheel_shapes)
        self.material_mu = torch.full((env.num_envs,), 0.9, device=env.device)
        self.torque_noise_scale = torch.zeros((env.num_envs, 6), device=env.device)
        self.joint_friction_scale = float(os.environ.get('JOINT_FRICTION_SCALE', '0.5'))
        if not (0.0 <= self.joint_friction_scale <= 1.0):
            raise ValueError('JOINT_FRICTION_SCALE must be in [0, 1]')

        n = int(env.num_envs)
        self.static_friction_default = _joint_default(
            self.robot, 'default_joint_friction_coeff', n, self.device
        )
        self.dynamic_friction_default = _joint_default(
            self.robot, 'default_joint_dynamic_friction_coeff', n, self.device
        )
        self.viscous_friction_default = _joint_default(
            self.robot, 'default_joint_viscous_friction_coeff', n, self.device
        )
        if self.static_friction_default is None:
            raise RuntimeError('joint-friction DR requires default friction coefficients')
        names = list(self.robot.joint_names)

        def ids_for(predicate):
            return [i for i, name in enumerate(names) if predicate(name)]

        self.leg_active_joint_ids = ids_for(
            lambda name: name.endswith('_front1_joint') or name.endswith('_rear1_joint')
        )
        self.wheel_joint_ids = ids_for(lambda name: name.endswith('_wheel_joint'))
        self.passive_joint_ids = ids_for(
            lambda name: any(tag in name for tag in (
                '_rear2_joint', '_front2_joint', '_front3_joint',
                '_front4_joint', '_spring1_joint',
            ))
        )
        self.joint_ids = torch.arange(len(names), dtype=torch.int32, device=self.device)

    def _scaled(self, low, high):
        return (low * self.joint_friction_scale, high * self.joint_friction_scale)

    def _add_joint_friction(self, ids, joint_ids, static_range, dynamic_range, viscous_range):
        if not joint_ids:
            return
        n = len(ids)
        j = torch.tensor(joint_ids, dtype=torch.long, device=self.device)
        count = len(joint_ids)
        static = self.static_friction_default[ids].clone()
        dynamic = (
            self.dynamic_friction_default[ids].clone()
            if self.dynamic_friction_default is not None else static.clone()
        )
        viscous = (
            self.viscous_friction_default[ids].clone()
            if self.viscous_friction_default is not None else torch.zeros_like(static)
        )
        static[:, j] += torch.empty((n, count), device=self.device).uniform_(
            *self._scaled(*static_range), generator=self.generator
        )
        dynamic[:, j] += torch.empty((n, count), device=self.device).uniform_(
            *self._scaled(*dynamic_range), generator=self.generator
        )
        viscous[:, j] += torch.empty((n, count), device=self.device).uniform_(
            *self._scaled(*viscous_range), generator=self.generator
        )
        static.clamp_(min=0.0)
        dynamic.clamp_(min=0.0)
        viscous.clamp_(min=0.0)
        dynamic = torch.minimum(dynamic, static)
        self.robot.write_joint_friction_coefficient_to_sim(
            joint_friction_coeff=static,
            joint_dynamic_friction_coeff=dynamic,
            joint_viscous_friction_coeff=viscous,
            joint_ids=self.joint_ids,
            env_ids=ids,
        )

    def __call__(self, env, env_ids):
        ids = (torch.arange(env.num_envs, device=env.device)
               if env_ids is None else torch.as_tensor(env_ids, device=env.device, dtype=torch.long))
        if len(ids) == 0:
            return
        # Preserve the 75m partial-DR bundle exactly.
        super().__call__(env, ids)

        # Old partial full-DR extras: small COM, all-shape friction, torque noise.
        coms = tensor(self.robot.root_view.get_coms()).to(env.device).clone()
        delta = torch.empty((len(ids), 3), device=env.device).uniform_(
            -0.01, 0.01, generator=self.generator
        )
        coms[ids, self.base_id, :3] += delta
        self.robot.set_coms_index(
            coms=_transform_array(coms[ids][:, [self.base_id], :].contiguous()),
            body_ids=[self.base_id], env_ids=ids, full_data=False,
        )
        mu = torch.empty(len(ids), device=env.device).uniform_(
            0.75, 1.0, generator=self.generator
        )
        self.material_mu[ids] = mu
        cpu_ids = ids.to(device='cpu', dtype=torch.int32)
        materials = tensor(self.robot.root_view.get_material_properties()).clone().cpu()
        values = torch.stack((mu.cpu(), mu.cpu(), torch.zeros_like(mu.cpu())), dim=-1)
        materials[cpu_ids.long()[:, None], self.all_shapes] = values[:, None, :]
        self.robot.root_view.set_material_properties(
            wp.from_torch(materials, dtype=wp.float32),
            wp.from_torch(cpu_ids, dtype=wp.int32),
        )
        self.torque_noise_scale[ids] = torch.empty(
            (len(ids), 6), device=env.device
        ).uniform_(0.0, 0.025, generator=self.generator)

        # New DR in this stage: joint friction, scaled to 50% by default.
        self._add_joint_friction(
            ids, self.leg_active_joint_ids, (0.25, 1.0), (0.25, 1.0), (0.05, 0.2)
        )
        self._add_joint_friction(
            ids, self.wheel_joint_ids, (0.05, 0.25), (0.05, 0.25), (0.0, 0.01)
        )
        self._add_joint_friction(
            ids, self.passive_joint_ids, (0.05, 0.1), (0.05, 0.1), (0.01, 0.025)
        )

    def summary(self):
        row = super().summary()
        row.update(
            profile='flat_joint_friction_stage1',
            stage='joint_friction_only',
            joint_friction_scale=self.joint_friction_scale,
            joint_friction_ranges={
                'active_leg_static': [0.25 * self.joint_friction_scale, 1.0 * self.joint_friction_scale],
                'active_leg_dynamic': [0.25 * self.joint_friction_scale, 1.0 * self.joint_friction_scale],
                'active_leg_viscous': [0.05 * self.joint_friction_scale, 0.2 * self.joint_friction_scale],
                'wheel_static': [0.05 * self.joint_friction_scale, 0.25 * self.joint_friction_scale],
                'passive_static': [0.05 * self.joint_friction_scale, 0.1 * self.joint_friction_scale],
            },
            missing_dr=[
                'observation_noise', 'observation_delay', 'action_delay',
                'spring_damping', 'external_force_torque',
            ],
        )
        return row


class ScutFlatJointFrictionEnv(ScutFlatRobustEnv):
    """75m partial DR plus scaled joint friction."""

    def __init__(self, cfg, meta, bank):
        super().__init__(cfg, meta, bank)
        self.full_dr = PartialJointFrictionDR(self)
        self.mild_dr = self.full_dr
        self._mild_dr = self.full_dr
        self.full_dr_torque_noise_enabled = True

    def _reset_idx(self, ids):
        ids = torch.as_tensor(ids, device=self.device, dtype=torch.long).flatten()
        super()._reset_idx(ids)
        if ids.numel() == 0:
            return
        n = int(ids.numel())
        root = tensor(self.robot.data.root_state_w)[ids].clone()
        root[:, 7] += torch.empty(n, device=self.device).uniform_(-0.30, 0.30)
        root[:, 8] += torch.empty(n, device=self.device).uniform_(-0.15, 0.15)
        root[:, 12] += torch.empty(n, device=self.device).uniform_(-0.25, 0.25)
        self.robot.write_root_state_to_sim(root, env_ids=ids)
