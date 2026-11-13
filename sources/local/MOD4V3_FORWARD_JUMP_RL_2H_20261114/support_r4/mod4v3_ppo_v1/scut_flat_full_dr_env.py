"""SCUT V14-style full domain randomization for the MOD4v3 flat task.

This is the bridge between the validated Flat-v2/Flat-Robust policy and the
SCUT V14 event bundle.  It deliberately keeps the 35-D observation and 6-D
action contracts unchanged.  The implementation adds the events that the
earlier flat_robust_full profile reported as unsupported:

  * base/leg/wheel mass and base COM randomization
  * base/guide/wheel material randomization
  * joint friction randomization
  * actuator gain and gas-spring target randomization
  * observation noise and observation delay
  * action delay
  * periodic velocity push and external force/torque
"""

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


class FullDRv3(MildDRv3):
    """SCUT V14 event bundle adapted to the MOD4v3 explicit-PD plant."""

    def __init__(self, env):
        super().__init__(env)
        self.body_names = list(self.robot.body_names)
        self.base_id = next(
            (self.body_names.index(name) for name in ('chassis', 'base_link', 'base')
             if name in self.body_names),
            None,
        )
        if self.base_id is None:
            raise ValueError('No MOD4 base body found for full DR')
        self.wheel_body_ids = [
            i for i, name in enumerate(self.body_names) if 'wheel_link' in name
        ]
        self.leg_body_ids = [
            i for i in range(len(self.body_names))
            if i != self.base_id and i not in self.wheel_body_ids
        ]
        self.gas_ids = list(env.gas_ids)
        self.gas_target_nominal = env.gas_targets.clone()

        # Shape ranges are needed for per-body material randomization.
        counts = [
            self.robot._physics_sim_view.create_rigid_body_view(p).max_shapes
            for p in self.robot.root_view.link_paths[0]
        ]
        if sum(counts) != self.robot.root_view.max_shapes:
            raise RuntimeError('body shape indexing differs from the PhysX view')
        self.shape_counts = counts
        starts = []
        cursor = 0
        for count in counts:
            starts.append(cursor)
            cursor += count
        self.shape_starts = starts
        self.base_shapes = []
        self.guide_shapes = []
        for i, name in enumerate(self.body_names):
            ids = list(range(starts[i], starts[i] + counts[i]))
            if name in ('chassis', 'base_link', 'base'):
                self.base_shapes.extend(ids)
            if 'guide' in name:
                self.guide_shapes.extend(ids)

        # Joint defaults are captured before any reset mutation.
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
            raise RuntimeError('SCUT full DR requires joint friction coefficients')
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
        self.mass_scale = torch.ones((n, len(self.body_names)), device=self.device)
        self.torque_noise_scale = torch.zeros((n, 6), device=self.device)
        self.material_mu = torch.full((n,), 0.9, device=self.device)

    def _sample_mass_scale(self, ids):
        n = len(ids)
        b = len(self.body_names)
        factor = torch.ones((n, b), device=self.device)
        if self.base_id is not None:
            factor[:, self.base_id] = torch.empty(n, device=self.device).uniform_(
                0.9, 1.3, generator=self.generator
            )
        if self.leg_body_ids:
            factor[:, self.leg_body_ids] = torch.empty(
                (n, len(self.leg_body_ids)), device=self.device
            ).uniform_(0.9, 1.1, generator=self.generator)
        if self.wheel_body_ids:
            factor[:, self.wheel_body_ids] = torch.empty(
                (n, len(self.wheel_body_ids)), device=self.device
            ).uniform_(0.9, 1.1, generator=self.generator)
        return factor

    def _randomize_materials(self, ids):
        n = len(ids)
        cpu_ids = ids.to(device='cpu', dtype=torch.int64)
        materials = tensor(self.robot.root_view.get_material_properties()).clone().cpu()

        def set_group(shape_ids, static_range, dynamic_range, restitution_range):
            if not shape_ids:
                return
            static = torch.empty(n).uniform_(*static_range, generator=self.cpu_generator)
            dynamic = torch.empty(n).uniform_(*dynamic_range, generator=self.cpu_generator)
            restitution = torch.empty(n).uniform_(
                *restitution_range, generator=self.cpu_generator
            )
            values = torch.stack((static, dynamic, restitution), dim=-1)
            materials[cpu_ids[:, None], shape_ids] = values[:, None, :]

        set_group(self.base_shapes, (0.01, 0.1), (0.01, 0.1), (0.02, 0.2))
        set_group(self.guide_shapes, (0.1, 0.7), (0.1, 0.7), (0.01, 0.1))
        set_group(self.wheel_shapes, (0.5, 1.2), (0.4, 1.0), (0.02, 0.2))
        self.robot.root_view.set_material_properties(
            wp.from_torch(materials, dtype=wp.float32),
            wp.from_torch(cpu_ids.to(torch.int32), dtype=wp.int32),
        )

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
            *static_range, generator=self.generator
        )
        dynamic[:, j] += torch.empty((n, count), device=self.device).uniform_(
            *dynamic_range, generator=self.generator
        )
        viscous[:, j] += torch.empty((n, count), device=self.device).uniform_(
            *viscous_range, generator=self.generator
        )
        static.clamp_(min=0.0)
        dynamic.clamp_(min=0.0)
        viscous.clamp_(min=0.0)
        # PhysX requires static friction effort >= dynamic friction effort.
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
        self.reset_count[ids] += 1
        if os.environ.get('FULL_DR_MASS', '1') == '1':
            factor = self._sample_mass_scale(ids)
            self.mass_scale[ids] = factor
            self.factor[ids] = factor.mean(dim=1)
            self.robot.set_masses_index(
                masses=self.mass[ids] * factor, env_ids=ids
            )
            if self.inertia is not None:
                shape = (len(ids), len(self.body_names)) + (1,) * max(0, self.inertia.dim() - 2)
                self.robot.set_inertias_index(
                    inertias=self.inertia[ids] * factor.reshape(shape), env_ids=ids
                )

            # SCUT base COM: x ±4 cm, y/z ±2 cm.
            coms = tensor(self.robot.root_view.get_coms()).to(env.device).clone()
            delta = torch.empty((len(ids), 3), device=env.device).uniform_(
                -1.0, 1.0, generator=self.generator
            )
            delta[:, 0] *= 0.04
            delta[:, 1] *= 0.02
            delta[:, 2] *= 0.02
            coms[ids, self.base_id, :3] += delta
            self.robot.set_coms_index(
                coms=_transform_array(coms[ids][:, [self.base_id], :].contiguous()),
                body_ids=[self.base_id], env_ids=ids, full_data=False,
            )

        # Actuator gain range from SCUT V14 (0.75–1.25).
        self.leg_gain_scale[ids] = torch.empty(
            (len(ids), 4), device=env.device
        ).uniform_(0.75, 1.25, generator=self.generator)
        self.wheel_gain_scale[ids] = torch.empty(
            (len(ids), 2), device=env.device
        ).uniform_(0.75, 1.25, generator=self.generator)

        if os.environ.get('FULL_DR_MATERIAL', '1') == '1':
            self._randomize_materials(ids)
        if os.environ.get('FULL_DR_JOINT_FRICTION', '1') == '1':
            self._add_joint_friction(
                ids, self.leg_active_joint_ids, (0.25, 1.0), (0.25, 1.0), (0.05, 0.2)
            )
            self._add_joint_friction(
                ids, self.wheel_joint_ids, (0.05, 0.25), (0.05, 0.25), (0.0, 0.01)
            )
            self._add_joint_friction(
                ids, self.passive_joint_ids, (0.05, 0.1), (0.05, 0.1), (0.01, 0.025)
            )

        # Gas-spring force range: ±50 N at k=2000 N/m => ±0.025 m target offset.
        if len(self.gas_ids) and os.environ.get('FULL_DR_GAS', '1') == '1':
            env.gas_targets[ids] = self.gas_target_nominal[ids] + torch.empty(
                (len(ids), len(self.gas_ids)), device=env.device
            ).uniform_(-0.025, 0.025, generator=self.generator)

        self.torque_noise_scale[ids] = torch.empty(
            (len(ids), 6), device=env.device
        ).uniform_(0.0, 0.025, generator=self.generator)
        self.material_mu[ids] = torch.empty(
            len(ids), device=env.device
        ).uniform_(0.5, 1.2, generator=self.generator)

    def summary(self):
        return {
            'profile': 'scut_full_dr_v14',
            'mass_scale': {
                'base': [0.9, 1.3],
                'leg': [0.9, 1.1],
                'wheel': [0.9, 1.1],
            },
            'base_com_delta_m': {'x': [-0.04, 0.04], 'y': [-0.02, 0.02], 'z': [-0.02, 0.02]},
            'material': {
                'base_static_dynamic': [[0.01, 0.1], [0.01, 0.1]],
                'guide_static_dynamic': [[0.1, 0.7], [0.1, 0.7]],
                'wheel_static_dynamic': [[0.5, 1.2], [0.4, 1.0]],
                'restitution': {'base': [0.02, 0.2], 'guide': [0.01, 0.1], 'wheel': [0.02, 0.2]},
            },
            'joint_friction': {
                'active_leg': {'static': [0.25, 1.0], 'dynamic': [0.25, 1.0], 'viscous': [0.05, 0.2]},
                'wheel': {'static': [0.05, 0.25], 'dynamic': [0.05, 0.25], 'viscous': [0.0, 0.01]},
                'passive': {'static': [0.05, 0.1], 'dynamic': [0.05, 0.1], 'viscous': [0.01, 0.025]},
            },
            'actuator_gain_scale': [0.75, 1.25],
            'spring_target_offset_m': [-0.025, 0.025],
            'spring_force_range_n': [-50.0, 50.0],
            'torque_noise_range_nm': [0.0, 0.025],
            'observation_noise': {
                'root_ang_vel': 0.25, 'projected_gravity': 0.05,
                'joint_pos': 0.025, 'leg_joint_vel': 0.5,
                'wheel_joint_vel': 1.0, 'height': 0.01,
            },
            'action_delay_steps': [1, 3],
            'observation_delay_steps': [1, 4],
            'push_velocity_range_m_s': [-0.25, 0.25],
            'external_force_range_n': [-10.0, 10.0],
            'external_torque_range_nm': [-1.0, 1.0],
            'ramp_steps': int(getattr(self.env, '_dr_ramp_steps', 0)),
            'ramp_seconds': float(getattr(self.env, '_dr_ramp_steps', 0) * getattr(self.env, '_control_dt', 0.02)),
            'unsupported_scut_events': [],
        }


class ScutFlatFullDREnv(ScutFlatRobustEnv):
    """Flat-Robust plus the full SCUT V14 event bundle."""

    def __init__(self, cfg, meta, bank):
        super().__init__(cfg, meta, bank)
        self.full_dr = FullDRv3(self)
        self.mild_dr = self.full_dr
        self._mild_dr = self.full_dr
        self.full_dr_torque_noise_enabled = True

        n = int(self.num_envs)
        self.max_action_delay = 3
        self.max_observation_delay = 4
        self._action_history = torch.zeros(
            (self.max_action_delay + 1, n, 6), device=self.device
        )
        self._action_delay_steps = torch.randint(
            1, self.max_action_delay + 1, (n,), device=self.device
        )
        self._obs_history = torch.zeros(
            (self.max_observation_delay + 1, n, 35), device=self.device
        )
        self._obs_delay_steps = torch.randint(
            1, self.max_observation_delay + 1, (n,), device=self.device
        )
        self._obs_pending_reset = torch.ones(n, dtype=torch.bool, device=self.device)

        self._external_force = torch.zeros((n, 3), device=self.device)
        self._external_torque = torch.zeros((n, 3), device=self.device)
        self._external_hold = torch.zeros(n, dtype=torch.long, device=self.device)
        self._external_timer = torch.empty(n, device=self.device).uniform_(5.0, 10.0)
        self._control_dt = float(cfg.sim.dt * cfg.decimation)
        self._dr_ramp_steps = int(os.environ.get('FULL_DR_RAMP_STEPS', '30000'))
        self._dr_control_steps = 0
        self._dr_ramp = 0.0

    def _pre_physics_step(self, actions):
        n = int(self.num_envs)
        self._dr_control_steps += 1
        self._dr_ramp = min(1.0, self._dr_control_steps / max(1, self._dr_ramp_steps))
        max_action_delay = int(round(self.max_action_delay * self._dr_ramp))
        actions = actions.to(self.device).clamp(-6.0, 6.0)
        if os.environ.get('FULL_DR_ACTION_DELAY', '1') == '1' and max_action_delay > 0:
            self._action_delay_steps.clamp_(max=max_action_delay)
            self._action_history[1:] = self._action_history[:-1].clone()
            self._action_history[0] = actions
            idx = self._action_delay_steps.view(1, n, 1).expand(1, n, 6)
            delayed = self._action_history.gather(0, idx).squeeze(0)
        else:
            delayed = actions
        super()._pre_physics_step(delayed)
        self._update_external_wrench()

    def _update_external_wrench(self):
        n = int(self.num_envs)
        if os.environ.get('FULL_DR_EXTERNAL', '1') != '1':
            forces = torch.zeros((n, 1, 3), device=self.device)
            torques = torch.zeros((n, 1, 3), device=self.device)
            self.robot.set_external_force_and_torque(
                forces, torques, env_ids=torch.arange(n, device=self.device),
                body_ids=[self.full_dr.base_id],
            )
            return
        self._external_timer -= self._control_dt
        self._external_hold.clamp_(min=0)
        event = self._external_timer <= 0.0
        if bool(event.any()):
            event_ids = event.nonzero().flatten()
            self._external_timer[event] = torch.empty(
                event_ids.numel(), device=self.device
            ).uniform_(5.0, 10.0)
            self._external_force[event] = torch.empty(
                (event_ids.numel(), 3), device=self.device
            ).uniform_(-10.0, 10.0)
            self._external_torque[event] = torch.empty(
                (event_ids.numel(), 3), device=self.device
            ).uniform_(-1.0, 1.0)
            self._external_hold[event] = 10
            root = tensor(self.robot.data.root_state_w).clone()
            root[event_ids, 7] += torch.empty(
                event_ids.numel(), device=self.device
            ).uniform_(-0.25, 0.25)
            root[event_ids, 8] += torch.empty(
                event_ids.numel(), device=self.device
            ).uniform_(-0.25, 0.25)
            self.robot.write_root_state_to_sim(root[event_ids], env_ids=event_ids)

        active = self._external_hold > 0
        forces = torch.zeros((n, 1, 3), device=self.device)
        torques = torch.zeros((n, 1, 3), device=self.device)
        forces[active, 0] = self._external_force[active]
        torques[active, 0] = self._external_torque[active]
        self.robot.set_external_force_and_torque(
            forces, torques, env_ids=torch.arange(n, device=self.device),
            body_ids=[self.full_dr.base_id],
        )

    def _get_observations(self):
        obs = super()._get_observations()
        policy = obs['policy']
        n = int(self.num_envs)
        if policy.shape[-1] != 35:
            return obs
        reset_ids = self._obs_pending_reset
        if bool(reset_ids.any()):
            self._obs_history[:, reset_ids] = policy[reset_ids]
            self._obs_pending_reset[reset_ids] = False
        max_obs_delay = int(round(self.max_observation_delay * self._dr_ramp))
        if os.environ.get('FULL_DR_OBS_DELAY', '1') == '1' and max_obs_delay > 0:
            self._obs_delay_steps.clamp_(max=max_obs_delay)
            self._obs_history[1:] = self._obs_history[:-1].clone()
            self._obs_history[0] = policy
            idx = self._obs_delay_steps.view(1, n, 1).expand(1, n, 35)
            delayed = self._obs_history.gather(0, idx).squeeze(0)
        else:
            delayed = policy
        noise = torch.zeros_like(delayed)
        if os.environ.get('FULL_DR_OBS_NOISE', '1') == '1':
            noise[:, 3].uniform_(-0.01, 0.01)
            noise[:, 4:7].uniform_(-0.25, 0.25)
            noise[:, 7:10].uniform_(-0.05, 0.05)
            noise[:, 10:16].uniform_(-0.025, 0.025)
            noise[:, 16:20].uniform_(-0.5, 0.5)
            noise[:, 20:22].uniform_(-1.0, 1.0)
            noise *= self._dr_ramp
        obs['policy'] = delayed + noise
        return obs

    def _reset_idx(self, ids):
        ids = torch.as_tensor(ids, device=self.device, dtype=torch.long).flatten()
        super()._reset_idx(ids)
        if ids.numel() == 0:
            return
        n = int(ids.numel())
        self._action_history[:, ids] = 0.0
        self._action_delay_steps[ids] = torch.randint(
            1, self.max_action_delay + 1, (n,), device=self.device
        )
        self._obs_history[:, ids] = 0.0
        self._obs_delay_steps[ids] = torch.randint(
            1, self.max_observation_delay + 1, (n,), device=self.device
        )
        self._obs_pending_reset[ids] = True
        self._external_force[ids] = 0.0
        self._external_torque[ids] = 0.0
        self._external_hold[ids] = 0
        self._external_timer[ids] = torch.empty(n, device=self.device).uniform_(5.0, 10.0)

        root = tensor(self.robot.data.root_state_w)[ids].clone()
        root[:, 7] += torch.empty(n, device=self.device).uniform_(-0.30, 0.30)
        root[:, 8] += torch.empty(n, device=self.device).uniform_(-0.15, 0.15)
        root[:, 12] += torch.empty(n, device=self.device).uniform_(-0.25, 0.25)
        self.robot.write_root_state_to_sim(root, env_ids=ids)
