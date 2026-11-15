"""SCUT V30 flat mild_dr_white profile for the MOD4v3 DirectRLEnv."""
import torch
import warp as wp

PROFILE = {'mass': (0.9, 1.1), 'motor': (0.9, 1.1), 'friction': (0.7, 1.0)}


def tensor(value):
    if isinstance(value, torch.Tensor):
        return value
    if hasattr(value, 'torch'):
        return value.torch
    return wp.to_torch(value)


class MildDRv3:
    def __init__(self, env):
        self.env = env
        self.robot = robot = env.robot
        self.device = env.device
        if not hasattr(robot.root_view, 'get_material_properties'):
            raise RuntimeError('mild_dr_white requires PhysX material read/write support')
        self.mass = tensor(robot.root_view.get_masses()).clone().to(env.device)
        self.inertia = tensor(robot.root_view.get_inertias()).clone().to(env.device)
        self.materials = tensor(robot.root_view.get_material_properties()).clone().cpu()
        self.generator = torch.Generator(device=env.device).manual_seed(int(env.cfg.seed) + 1717)
        self.cpu_generator = torch.Generator(device='cpu').manual_seed(int(env.cfg.seed) + 1818)
        counts = [robot._physics_sim_view.create_rigid_body_view(p).max_shapes
                  for p in robot.root_view.link_paths[0]]
        if sum(counts) != robot.root_view.max_shapes:
            raise RuntimeError('wheel collider indexing differs from the PhysX articulation view')
        self.wheel_shapes = []
        for name in ('left_wheel_link', 'right_wheel_link'):
            bid = list(robot.body_names).index(name)
            self.wheel_shapes.extend(range(sum(counts[:bid]), sum(counts[:bid + 1])))
        if len(self.wheel_shapes) < 2:
            raise RuntimeError('two wheel colliders are required')
        self.nonwheel_shapes = [i for i in range(sum(counts)) if i not in self.wheel_shapes]
        self.friction_buckets = torch.cat((torch.tensor([0.9]),
                                           torch.linspace(*PROFILE['friction'], 32)))
        self.factor = torch.ones(env.num_envs, device=env.device)
        self.nominal = torch.ones(env.num_envs, dtype=torch.bool, device=env.device)
        self.mu = torch.full((env.num_envs,), 0.9)
        self.reset_count = torch.zeros(env.num_envs, dtype=torch.long, device=env.device)
        self.leg_gain_scale = torch.ones((env.num_envs, 4), device=env.device)
        self.wheel_gain_scale = torch.ones((env.num_envs, 2), device=env.device)
        env._leg_gain_scale = self.leg_gain_scale
        env._wheel_gain_scale = self.wheel_gain_scale
        env._mild_dr = self

    def __call__(self, env, env_ids):
        ids = (torch.arange(env.num_envs, device=env.device)
               if env_ids is None else torch.as_tensor(env_ids, device=env.device, dtype=torch.long))
        if len(ids) == 0:
            return
        nominal = torch.rand(len(ids), device=env.device, generator=self.generator) < 0.2
        factor = torch.empty(len(ids), device=env.device).uniform_(*PROFILE['mass'], generator=self.generator)
        factor[nominal] = 1.0
        self.nominal[ids] = nominal
        self.reset_count[ids] += 1
        self._apply_mass_inertia(ids, factor)
        leg = self.leg_gain_scale
        wheel = self.wheel_gain_scale
        leg[ids] = torch.empty_like(leg[ids]).uniform_(*PROFILE['motor'], generator=self.generator)
        wheel[ids] = torch.empty_like(wheel[ids]).uniform_(*PROFILE['motor'], generator=self.generator)
        leg[ids[nominal]] = 1.0
        wheel[ids[nominal]] = 1.0
        cpu_ids = ids.to(device='cpu', dtype=torch.int32)
        bucket = torch.randint(1, 33, (len(ids),), device='cpu', generator=self.cpu_generator)
        bucket[nominal.cpu()] = 0
        mu = self.friction_buckets[bucket]
        self.mu[cpu_ids.long()] = mu
        materials = tensor(self.robot.root_view.get_material_properties()).clone().cpu()
        values = torch.stack((mu, mu, torch.zeros_like(mu)), dim=-1)
        materials[cpu_ids.long()[:, None], self.wheel_shapes] = values[:, None, :]
        self.robot.root_view.set_material_properties(
            wp.from_torch(materials, dtype=wp.float32),
            wp.from_torch(cpu_ids, dtype=wp.int32),
        )

    def _apply_mass_inertia(self, ids, factor):
        self.factor[ids] = factor
        self.robot.set_masses_index(masses=self.mass[ids] * factor[:, None], env_ids=ids)
        self.robot.set_inertias_index(inertias=self.inertia[ids] * factor[:, None, None], env_ids=ids)

    def summary(self):
        return {
            'profile': 'white_v3',
            'mass_inertia_factor_range': [float(self.factor.min()), float(self.factor.max())],
            'leg_gain_range': [float(self.leg_gain_scale.min()), float(self.leg_gain_scale.max())],
            'wheel_gain_range': [float(self.wheel_gain_scale.min()), float(self.wheel_gain_scale.max())],
            'wheel_friction_range': [float(self.mu.min()), float(self.mu.max())],
            'nominal_fraction_target': 0.2,
            'other_randomization': 'spring/PD/COM/armature/joint-friction/push/noise/delay unchanged',
        }
