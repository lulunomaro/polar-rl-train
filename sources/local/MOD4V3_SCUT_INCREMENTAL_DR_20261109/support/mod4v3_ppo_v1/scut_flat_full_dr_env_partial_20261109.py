"""Flat-Robust-Full: supported SCUT-style DR additions for MOD4v3."""
from __future__ import annotations
import math
import torch
import warp as wp
from .scut_flat_robust_env import ScutFlatRobustEnv
from .scut_mild_dr import MildDRv3
from .scut_flat_env import tensor


def _transform_array(value):
    return wp.from_torch(value.contiguous(), dtype=wp.transformf)


class FullDRv3(MildDRv3):
    """Extend MildDRv3 with COM, all-shape friction and torque noise.

    This deliberately reports the remaining unsupported SCUT events in the
    summary instead of pretending they were applied.
    """

    def __init__(self, env):
        super().__init__(env)
        body_names = list(self.robot.body_names)
        self.base_id = next(
            (body_names.index(name) for name in ('chassis', 'base_link', 'base') if name in body_names),
            None,
        )
        if self.base_id is None:
            raise ValueError('No MOD4 base body found for COM DR')
        self.torque_noise_scale = torch.zeros((env.num_envs, 6), device=env.device)
        self.material_mu = torch.full((env.num_envs,), 0.9, device=env.device)
        self.all_shapes = list(self.wheel_shapes) + list(self.nonwheel_shapes)

    def __call__(self, env, env_ids):
        ids = (torch.arange(env.num_envs, device=env.device)
               if env_ids is None else torch.as_tensor(env_ids, device=env.device, dtype=torch.long))
        if len(ids) == 0:
            return
        super().__call__(env, ids)

        # Base COM: small body-local translation perturbation.
        coms = tensor(self.robot.root_view.get_coms()).to(env.device).clone()
        delta = torch.empty((len(ids), 3), device=env.device).uniform_(-0.01, 0.01)
        coms[ids, self.base_id, :3] += delta
        self.robot.set_coms_index(
            coms=_transform_array(coms[ids][:, [self.base_id], :].contiguous()),
            body_ids=[self.base_id], env_ids=ids, full_data=False,
        )

        # Material friction: randomize all body shapes, not only wheels.
        mu = torch.empty(len(ids), device=env.device).uniform_(0.75, 1.0)
        self.material_mu[ids] = mu
        cpu_ids = ids.to(device='cpu', dtype=torch.int32)
        materials = tensor(self.robot.root_view.get_material_properties()).clone().cpu()
        values = torch.stack((mu.cpu(), mu.cpu(), torch.zeros_like(mu.cpu())), dim=-1)
        materials[cpu_ids.long()[:, None], self.all_shapes] = values[:, None, :]
        self.robot.root_view.set_material_properties(
            wp.from_torch(materials, dtype=wp.float32),
            wp.from_torch(cpu_ids, dtype=wp.int32),
        )

        # Per-episode motor effort noise.
        self.torque_noise_scale[ids] = torch.empty(
            (len(ids), 6), device=env.device
        ).uniform_(0.0, 0.025)

    def summary(self):
        row = super().summary()
        row.update(
            profile='flat_robust_full',
            base_com_delta_range_m=[-0.01, 0.01],
            material_friction_range=[0.75, 1.0],
            torque_noise_range_nm=[0.0, 0.025],
            unsupported_scut_events=[
                'observation_noise', 'action_delay', 'observation_delay',
                'joint_friction', 'spring_damping', 'external_force_torque',
            ],
        )
        return row


class ScutFlatFullDREnv(ScutFlatRobustEnv):
    """Flat-Robust bridge plus supported SCUT-style DR events."""

    def __init__(self, cfg, meta, bank):
        super().__init__(cfg, meta, bank)
        self.full_dr = FullDRv3(self)
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
