"""Explicit MOD4 mild DR; the legacy full DR bundle stays disabled.

Only mass/inertia density, wheel friction, and six motor output gains vary.
This module is installed in a NEW isolated task, never in the running task.
"""
import os
import torch
import warp as wp
from autonomy_policy import DR_PROFILES
from isaaclab.managers import ManagerTermBase, EventTermCfg


def tensor(value):
    if isinstance(value, torch.Tensor):
        return value
    if hasattr(value, 'torch'):
        return value.torch
    return wp.to_torch(value)


class MildDR214(ManagerTermBase):
    def __init__(self, cfg, env):
        from material214 import log
        from usd214 import material_census
        log('BEFORE_MILD_DR_CONSTRUCTION',num_envs=env.num_envs,terrain=material_census(env.sim.stage))
        super().__init__(cfg, env)
        self.profile = os.environ.get('RM_MILD_DR_PROFILE', '')
        self.recipe = DR_PROFILES[self.profile]
        self.robot = robot = env.scene['robot']
        if not hasattr(robot.root_view, 'get_material_properties'):
            raise RuntimeError('Mild DR requires actual PhysX material read/write support')
        self.mass = tensor(robot.root_view.get_masses()).clone().to(env.device)
        self.inertia = tensor(robot.root_view.get_inertias()).clone().to(env.device)
        self.materials = tensor(robot.root_view.get_material_properties()).clone().cpu()
        from material214 import cached_summary
        log('AFTER_ORIGINAL_MATERIAL_CACHE_READ',num_envs=env.num_envs,**cached_summary(torch,self.materials))
        # Local COM translation, independent of robot pose or a principal-axis quaternion representation.
        self.com = tensor(robot.data.body_com_pos_b).clone()
        seed=int(env.cfg.seed)
        self.generator=torch.Generator(device=env.device).manual_seed(seed+1717)
        self.cpu_generator=torch.Generator(device='cpu').manual_seed(seed+1818)
        self.gains = {name: {key: tensor(getattr(a, key)).clone()
            for key in ('stiffness', 'damping')}
            for name, a in robot.actuators.items()}
        self.other_joint_values = {}
        for name in ('get_dof_armatures', 'get_dof_friction_coefficients'):
            if hasattr(robot.root_view, name):
                self.other_joint_values[name] = tensor(getattr(robot.root_view, name)()).clone()
        counts = [robot._physics_sim_view.create_rigid_body_view(p).max_shapes
                  for p in robot.root_view.link_paths[0]]
        if sum(counts) != robot.root_view.max_shapes:
            raise RuntimeError('Wheel collider indexing differs from the PhysX articulation view')
        self.wheel_shapes = []
        for name in ('left_wheel', 'right_wheel'):
            bid = list(robot.body_names).index(name)
            self.wheel_shapes.extend(range(sum(counts[:bid]), sum(counts[:bid+1])))
        if len(self.wheel_shapes) < 2:
            raise RuntimeError('Two wheel colliders are required')
        self.nonwheel_shapes = [i for i in range(sum(counts)) if i not in self.wheel_shapes]
        # Exactly 33 repeatable triples; no continuous per-shape material creation.
        self.friction_buckets = torch.cat((torch.tensor([.9]), torch.linspace(*self.recipe['friction'], 32)))
        self.factor = torch.ones(env.num_envs, device=env.device)
        self.nominal = torch.ones(env.num_envs, dtype=torch.bool, device=env.device)
        self.mu = torch.full((env.num_envs,), .9)
        self.reset_count = torch.zeros(env.num_envs, dtype=torch.long, device=env.device)
        self.output = {}
        for name, width in [('legs', 4), ('wheels', 2)]:
            actuator = robot.actuators[name]
            actuator.episode_scale = torch.ones((env.num_envs, width), device=env.device)
            actuator.step_scale = torch.ones_like(actuator.episode_scale)
            self.output[name] = actuator.episode_scale
        env._mild_dr = self

    def __call__(self, env, env_ids):
        ids = torch.arange(env.num_envs, device=env.device) if env_ids is None else env_ids.to(env.device)
        if not len(ids):
            return
        nominal = torch.rand(len(ids), device=env.device, generator=self.generator) < .2
        factor = torch.empty(len(ids), device=env.device).uniform_(*self.recipe['mass'], generator=self.generator)
        factor[nominal] = 1.
        self.factor[ids], self.nominal[ids] = factor, nominal
        self.reset_count[ids] += 1
        self.robot.set_masses_index(masses=self.mass[ids] * factor[:, None], env_ids=ids)
        self.robot.set_inertias_index(inertias=self.inertia[ids] * factor[:, None, None], env_ids=ids)
        for name in ('legs', 'wheels'):
            gains = self.robot.actuators[name].episode_scale
            gains[ids] = torch.empty_like(gains[ids]).uniform_(*self.recipe['motor'], generator=self.generator)
            gains[ids[nominal]] = 1.
        cpu_ids = ids.to(device='cpu', dtype=torch.int32)
        bucket = torch.randint(1, 33, (len(ids),), device='cpu', generator=self.cpu_generator)
        bucket[nominal.cpu()] = 0
        mu = self.friction_buckets[bucket]
        self.mu[cpu_ids.long()] = mu
        materials = tensor(self.robot.root_view.get_material_properties()).clone().cpu()
        values = torch.stack((mu, mu, torch.zeros_like(mu)), dim=-1)
        materials[cpu_ids.long()[:, None], self.wheel_shapes] = values[:, None, :]
        from material214 import set_material_once
        set_material_once(torch,wp,self.robot.root_view,materials,cpu_ids)

    def audit(self):
        robot = self.robot
        actual_mass = tensor(robot.root_view.get_masses()).to(self.mass.device)
        actual_inertia = tensor(robot.root_view.get_inertias()).to(self.inertia.device)
        actual_materials = tensor(robot.root_view.get_material_properties()).cpu()
        checks = {
            'mass_relative_error': float(((actual_mass-self.mass*self.factor[:,None]).abs() / self.mass.clamp_min(1e-8)).max()),
            'inertia_absolute_error': float((actual_inertia-self.inertia*self.factor[:,None,None]).abs().max()),
            'wheel_friction_error': float((actual_materials[:,self.wheel_shapes,:2]-self.mu[:,None,None]).abs().max()),
            'wheel_restitution_abs_max': float(actual_materials[:,self.wheel_shapes,2].abs().max()),
            'nonwheel_material_error': float((actual_materials[:,self.nonwheel_shapes]-self.materials[:,self.nonwheel_shapes]).abs().max()),
            'local_com_position_error': float((tensor(robot.data.body_com_pos_b)-self.com).abs().max()),
        }
        for name, gains in self.gains.items():
            for key, value in gains.items():
                checks[name+'_'+key+'_error'] = float((tensor(getattr(robot.actuators[name],key))-value).abs().max())
        for name, value in self.other_joint_values.items():
            checks[name+'_error'] = float((tensor(getattr(robot.root_view,name)())-value).abs().max())
        assert checks['mass_relative_error'] < 1e-5 and checks['inertia_absolute_error'] < 1e-6, checks
        assert all(v < 1e-6 for k,v in checks.items() if k not in ('mass_relative_error',)), checks
        strengths = {name: {'min': float(a.episode_scale.min()), 'max': float(a.episode_scale.max()),
                            'per_step_noise_abs_error': float((a.step_scale-1.).abs().max())}
                     for name,a in robot.actuators.items() if name in ('legs','wheels')}
        assert all(self.recipe['motor'][0]-1e-5 <= s['min'] <= s['max'] <= self.recipe['motor'][1]+1e-5 and s['per_step_noise_abs_error']==0 for s in strengths.values())
        return {'profile': self.profile, 'registered_ranges': self.recipe, 'actual_parameters_pass': True, 'errors': checks,
                'mass_inertia_factor_range': [float(self.factor.min()),float(self.factor.max())],
                'motor_strength': strengths, 'friction_range': [float(self.mu.min()),float(self.mu.max())],
                'nominal_environment_count': int(self.nominal.sum()), 'num_envs': len(self.factor),
                'wheel_shapes': self.wheel_shapes, 'material_buckets': 33,
                'reset_count_range': [int(self.reset_count.min()),int(self.reset_count.max())],
                'legacy_full_dr_disabled': True,
                'other_randomization': 'spring/PD/COM/armature/joint-friction/push/noise/delay unchanged',
                'motor_rating': 'output gain followed by original torque-speed clipping'}


def configure(cfg):
    profile = os.environ.get('RM_MILD_DR_PROFILE', '')
    if profile in ('', 'nominal'):
        return
    if profile not in DR_PROFILES:
        raise ValueError('Unregistered whitelist DR profile: '+profile)
    if os.environ.get('RM_DR_OFF') != '1':
        raise RuntimeError('Whitelist cannot run alongside the legacy full DR bundle')
    for name in ('mass_inertia','wheel_friction','chassis_com','actuator_gains',
                 'leg_joint_params','wheel_joint_params','gas_gains','push_wrench',
                 'push_velocity','leg_effort_scale','wheel_effort_scale'):
        if getattr(cfg.events, name, None) is not None:
            raise RuntimeError('Unexpected full DR event: '+name)
    cfg.events.mild_dr_white = EventTermCfg(func=MildDR214, mode='reset')

