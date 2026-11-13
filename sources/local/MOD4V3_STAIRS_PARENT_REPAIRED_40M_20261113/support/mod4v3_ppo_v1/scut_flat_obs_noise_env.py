"""Stage 4 incremental DR: Stage 3 + observation noise 25%."""

from __future__ import annotations

import os

import torch

from .scut_flat_external_dr_env import ExternalDRStage3, ScutFlatExternalDREnv


class ObservationNoiseDRStage4(ExternalDRStage3):
    """Keep Stage 3 DR and add a scaled sensor-noise perturbation."""

    def __init__(self, env):
        super().__init__(env)
        self.obs_noise_fraction = float(os.environ.get("OBS_NOISE_FRACTION", "0.25"))
        if not (0.0 <= self.obs_noise_fraction <= 1.0):
            raise ValueError("OBS_NOISE_FRACTION must be in [0, 1]")

    def summary(self):
        row = super().summary()
        f = float(self.obs_noise_fraction)
        row.update(
            profile="flat_obs_noise_stage4",
            stage="joint_friction_50pct + spring_damping_25pct + external_force_torque_25pct + observation_noise_25pct",
            obs_noise_fraction=f,
            obs_noise_ranges={
                "height": [-0.01 * f, 0.01 * f],
                "base_ang_vel_observation": [-0.25 * f, 0.25 * f],
                "projected_gravity_observation": [-0.05 * f, 0.05 * f],
                "joint_pos": [-0.025 * f, 0.025 * f],
                "leg_joint_vel_observation": [-0.5 * f, 0.5 * f],
                "wheel_joint_vel_observation": [-1.0 * f, 1.0 * f],
            },
            missing_dr=[
                "observation_delay",
                "action_delay",
                "full_SCUT_mass_COM_material_ranges",
            ],
        )
        return row


class ScutFlatObsNoiseEnv(ScutFlatExternalDREnv):
    """Stage 4: Stage 3 plus observation noise; no observation/action delay."""

    def __init__(self, cfg, meta, bank):
        super().__init__(cfg, meta, bank)
        self.full_dr = ObservationNoiseDRStage4(self)
        self.mild_dr = self.full_dr
        self._mild_dr = self.full_dr

    def _get_observations(self):
        obs = super()._get_observations()
        policy = obs["policy"]
        if policy.shape[-1] != 35:
            return obs
        f = float(self.full_dr.obs_noise_fraction)
        noise = torch.zeros_like(policy)
        # Indices follow the existing 35-D policy observation contract.
        noise[:, 3].uniform_(-0.01, 0.01)
        noise[:, 4:7].uniform_(-0.25, 0.25)
        noise[:, 7:10].uniform_(-0.05, 0.05)
        noise[:, 10:16].uniform_(-0.025, 0.025)
        noise[:, 16:20].uniform_(-0.5, 0.5)
        noise[:, 20:22].uniform_(-1.0, 1.0)
        obs["policy"] = policy + noise * f
        return obs
