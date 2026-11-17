"""Step7/mass/effort plus SCUT startup material buckets per body group."""
import re
import torch
import warp as wp
from mod4v1_scut.config import observation_component
from .scut_flat_env import tensor
from .scut_flat_effort_scale_env import ScutEffortScaleDR, ScutFlatEffortScaleEnv

MATERIAL_GROUPS = {
    "wheel": (r".*_wheel_link", (0.5, 1.2), (0.4, 1.0), (0.02, 0.2), 64),
    "base": (r"base_link", (0.01, 0.1), (0.01, 0.1), (0.02, 0.2), 64),
    "guide": (r".*_guide_link", (0.1, 0.7), (0.1, 0.7), (0.01, 0.1), 8),
}


class ScutMaterialDR(ScutEffortScaleDR):
    def __init__(self, env):
        super().__init__(env)
        self.material_generator = torch.Generator(device="cpu").manual_seed(int(env.cfg.seed) + 2121)
        counts = [self.robot._physics_sim_view.create_rigid_body_view(p).max_shapes
                  for p in self.robot.root_view.link_paths[0]]
        if sum(counts) != self.robot.root_view.max_shapes:
            raise ValueError("Material shape mapping differs from articulation")
        self.material_shapes = {}
        self.material_bodies = {}
        self.material_buckets = {}
        self.material_bucket_ids = {}
        self.startup_materials = tensor(self.robot.root_view.get_material_properties()).clone().cpu()
        for key, (pattern, static, dynamic, restitution, count) in MATERIAL_GROUPS.items():
            bids = [i for i, name in enumerate(self.robot.body_names) if re.fullmatch(pattern, name)]
            shapes = [s for bid in bids for s in range(sum(counts[:bid]), sum(counts[:bid + 1]))]
            if not shapes:
                raise ValueError("Missing contact colliders for " + key)
            self.material_bodies[key] = bids
            self.material_shapes[key] = shapes
            ranges = torch.tensor([static, dynamic, restitution], dtype=torch.float32)
            # Same uniform bucket construction and consistency operation as Isaac Lab PhysX event.
            buckets = ranges[:, 0] + torch.rand((count, 3), generator=self.material_generator) * (ranges[:, 1] - ranges[:, 0])
            buckets[:, 1] = torch.minimum(buckets[:, 0], buckets[:, 1])
            indices = torch.randint(0, count, (env.num_envs, sum(counts)), generator=self.material_generator)
            self.material_buckets[key] = buckets
            self.material_bucket_ids[key] = indices[:, shapes].clone()
            self.startup_materials[:, shapes] = buckets[indices[:, shapes]]
        self.selected_material_shapes = sorted(s for values in self.material_shapes.values() for s in values)
        self.wheel_material_shapes = []
        for name in ("left_wheel_link", "right_wheel_link"):
            bid = list(self.robot.body_names).index(name)
            self.wheel_material_shapes.append(list(range(sum(counts[:bid]), sum(counts[:bid + 1]))))
        self._write_startup_materials(torch.arange(env.num_envs, device=self.device))

    def _write_startup_materials(self, ids):
        cpu_ids = ids.to(device="cpu", dtype=torch.int32)
        materials = tensor(self.robot.root_view.get_material_properties()).clone().cpu()
        materials[cpu_ids.long()[:, None], self.selected_material_shapes] = self.startup_materials[cpu_ids.long()[:, None], self.selected_material_shapes]
        self.robot.root_view.set_material_properties(wp.from_torch(materials.contiguous(), dtype=wp.float32),
                                                    wp.from_torch(cpu_ids, dtype=wp.int32))
        wheel = torch.cat([materials[:, shapes].mean(1) for shapes in self.wheel_material_shapes], -1).to(self.device)
        self.wheel_material_values = wheel
        self.material_mu[ids] = wheel[ids][:, [0, 3]].mean(-1)

    def __call__(self, env, env_ids):
        ids = (torch.arange(env.num_envs, device=self.device) if env_ids is None
               else torch.as_tensor(env_ids, device=self.device, dtype=torch.long).flatten())
        if not ids.numel():
            return
        super().__call__(env, ids)
        # Inherited Step7 reset still owns unselected shapes. Restore startup samples on the three selected groups.
        self._write_startup_materials(ids)

    def summary(self):
        row = super().summary()
        row.update(profile="step7_mass_effort_material_v1", contact_material={
            "sampling": "startup; independent per-env/per-shape bucket selection; selected properties fixed across resets",
            "make_consistent": True,
            "groups": {key: {"bodies": [self.robot.body_names[i] for i in self.material_bodies[key]],
                "shapes": self.material_shapes[key], "static": list(spec[1]), "dynamic": list(spec[2]),
                "restitution": list(spec[3]), "buckets": spec[4],
                "actual_min": self.startup_materials[:, self.material_shapes[key]].amin((0, 1)).tolist(),
                "actual_max": self.startup_materials[:, self.material_shapes[key]].amax((0, 1)).tolist()}
                for key, spec in MATERIAL_GROUPS.items()},
            "unselected": "inherited Step7 mild material reset",
            "critic": "existing six slots: actual left/right wheel material triple; shape mean if multi-shape; no base/guide encoding; 78D retained"},
            missing_dr=["full_SCUT_COM_and_other_remaining_ranges", "interval_velocity_push"])
        return row


class ScutFlatMaterialEnv(ScutFlatEffortScaleEnv):
    body_mass_dr_class = ScutMaterialDR

    def _encode(self):
        obs = super()._encode()
        dr = getattr(self, "full_dr", None)
        if not hasattr(dr, "wheel_material_values") or not getattr(self, "_delay_ready", False):
            return obs
        extra = obs["critic"][:, 39:].clone()
        extra[:, 33:39] = observation_component(self.reward.cfg, "body_material", dr.wheel_material_values, "critic")
        obs["critic"] = torch.cat((obs["critic"][:, :39], extra), -1)
        self.reward.cache_raw_observations(dict(policy=obs["policy"]), dict(critic=obs["critic"][:, :39], extra=extra))
        return obs
