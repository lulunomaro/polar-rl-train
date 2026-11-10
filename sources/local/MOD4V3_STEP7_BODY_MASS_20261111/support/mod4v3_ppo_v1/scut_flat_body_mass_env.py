"""Step7 continuation with SCUT startup independent rigid-body mass scales."""
import re
import torch
from .scut_flat_physical_delay_env import PhysicalDelayDR
from .scut_flat_forward_square_env import ScutFlatForwardSquareEnv


class ScutBodyMassDR(PhysicalDelayDR):
    """Replace only the inherited common mass factor; retain other Step7 DR."""

    def __init__(self, env):
        super().__init__(env)
        names = list(self.robot.body_names)
        self.mass_body_names = names
        self.mass_groups = {
            "base": [i for i, name in enumerate(names) if name == "base_link"],
            "leg": [i for i, name in enumerate(names) if re.fullmatch(
                r".*_(?:front[1-4]|rear[1-2]|spring[1-2])_link|gimbal_(?:yaw|pitch)_link", name)],
            "wheel": [i for i, name in enumerate(names) if re.fullmatch(r".*_wheel_link", name)],
        }
        if len(self.mass_groups["base"]) != 1 or len(self.mass_groups["wheel"]) != 2:
            raise ValueError("Expected one MOD4 base and two main wheels")
        if len(self.mass_groups["leg"]) != 16:
            raise ValueError("Expected the sixteen selected MOD4 leg links")
        self.mass_ranges = {"base": (0.9, 1.3), "leg": (0.9, 1.1), "wheel": (0.9, 1.1)}
        self.body_mass_scale = torch.ones_like(self.mass)
        generator = torch.Generator(device=self.device).manual_seed(int(env.cfg.seed) + 1921)
        for group, body_ids in self.mass_groups.items():
            samples = torch.empty((env.num_envs, len(body_ids)), device=self.device).uniform_(
                *self.mass_ranges[group], generator=generator)
            self.body_mass_scale[:, body_ids] = samples
        self.total_mass_scale = (self.mass * self.body_mass_scale).sum(-1) / self.mass.sum(-1)
        ids = torch.arange(env.num_envs, device=self.device, dtype=torch.long)
        self._write_body_mass_inertia(ids)

    def _apply_mass_inertia(self, ids, unused_common_factor):
        # Suppress the old shared factor; write after the inherited COM setter.
        self.factor[ids] = self.total_mass_scale[ids]

    def _write_body_mass_inertia(self, ids):
        # Reassert the immutable startup sample after COM frame updates.
        scale = self.body_mass_scale[ids]
        self.factor[ids] = self.total_mass_scale[ids]
        self.robot.set_masses_index(masses=self.mass[ids] * scale, env_ids=ids)
        self.robot.set_inertias_index(inertias=self.inertia[ids] * scale[..., None], env_ids=ids)

    def __call__(self, env, env_ids):
        ids = (torch.arange(env.num_envs, device=self.device) if env_ids is None
               else torch.as_tensor(env_ids, device=self.device, dtype=torch.long))
        if not len(ids):
            return
        super().__call__(env, ids)
        self._write_body_mass_inertia(ids)

    def summary(self):
        row = super().summary()
        row.update(
            profile="step7_scut_startup_body_mass_v1",
            stage="repaired Step7 DR and squared tracking reward plus SCUT independent body mass",
            mass_inertia_factor_range=None,
            body_mass_randomization={
                "sampling": "independent per environment and selected rigid body at startup; fixed across resets",
                "groups": {key: {"range": list(self.mass_ranges[key]),
                    "bodies": [self.mass_body_names[i] for i in body_ids]}
                    for key, body_ids in self.mass_groups.items()},
                "unselected_bodies": [name for i, name in enumerate(self.mass_body_names)
                    if all(i not in ids for ids in self.mass_groups.values())],
                "unselected_scale": 1.0,
                "inertia": "nominal inertia tensor scaled by that body's mass ratio",
                "nominal_mass_mixture": False,
                "critic_mass_slot": "actual total robot mass divided by nominal total mass; existing 78D layout",
                "total_mass_ratio_range": [float(self.total_mass_scale.min()), float(self.total_mass_scale.max())],
            },
            base_com_delta_m={axis: [-0.01, 0.01] for axis in ("x", "y", "z")},
            missing_dr=["full_SCUT_COM_and_material_ranges"],
        )
        return row


class ScutFlatBodyMassEnv(ScutFlatForwardSquareEnv):
    def __init__(self, cfg, meta, bank):
        super().__init__(cfg, meta, bank)
        self.full_dr = ScutBodyMassDR(self)
        self.mild_dr = self.full_dr
        self._mild_dr = self.full_dr
