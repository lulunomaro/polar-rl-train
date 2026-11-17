"""Cumulative Step7/mass DR plus independent explicit motor output scale."""
import torch
from mod4v1_scut.config import observation_component
from .scut_flat_env import tensor
from .scut_flat_body_mass_env import ScutBodyMassDR, ScutFlatBodyMassEnv


class ScutEffortScaleDR(ScutBodyMassDR):
    min_step_count_between_reset = 720

    def __init__(self, env):
        super().__init__(env)
        self.effort_scale = torch.ones((env.num_envs, 6), device=self.device)
        self.effort_last_sample_step = torch.zeros(env.num_envs, dtype=torch.long, device=self.device)
        self.effort_sample_count = torch.zeros_like(self.effort_last_sample_step)
        self.effort_generator = torch.Generator(device=self.device).manual_seed(int(env.cfg.seed) + 2021)
        env._motor_effort_scale = self.effort_scale

    def sample_effort(self, ids, global_step):
        # Match reset EventManager: first call always, later only after 720 global policy steps.
        ids = torch.as_tensor(ids, device=self.device, dtype=torch.long).flatten()
        eligible = (self.effort_sample_count[ids] == 0) | (
            int(global_step) - self.effort_last_sample_step[ids] >= self.min_step_count_between_reset)
        selected = ids[eligible]
        if selected.numel():
            self.effort_scale[selected, :4] = torch.empty((len(selected), 4), device=self.device).uniform_(
                0.8, 1.1, generator=self.effort_generator)
            self.effort_scale[selected, 4:] = torch.empty((len(selected), 2), device=self.device).uniform_(
                0.9, 1.1, generator=self.effort_generator)
            self.effort_last_sample_step[selected] = int(global_step)
            self.effort_sample_count[selected] += 1
        return selected

    def __call__(self, env, env_ids):
        ids = (torch.arange(env.num_envs, device=self.device) if env_ids is None
               else torch.as_tensor(env_ids, device=self.device, dtype=torch.long).flatten())
        super().__call__(env, ids)
        step = int(env._sim_step_counter) // int(env.cfg.decimation)
        self.sample_effort(ids, step)

    def summary(self):
        row = super().summary()
        row.update(profile="step7_mass_effort_scale_v1",
                   stage="repaired Step7 plus startup body mass and explicit motor output scale",
                   effort_output_scale={
                       "leg_range": [0.8, 1.1], "wheel_range": [0.9, 1.1],
                       "sampling": "independent per env/active motor, first reset and eligible reset after 720 global policy steps",
                       "min_step_count_between_reset": 720,
                       "sample_count_range": [int(self.effort_sample_count.min()), int(self.effort_sample_count.max())],
                       "actual_leg_range": [float(self.effort_scale[:, :4].min()), float(self.effort_scale[:, :4].max())],
                       "actual_wheel_range": [float(self.effort_scale[:, 4:].min()), float(self.effort_scale[:, 4:].max())],
                       "application": "full raw PD torque multiplied before original DC envelope; inherited additive noise then final envelope",
                       "new_bias": 0.0, "new_noise_std": 0.0,
                       "critic": "existing stiffness/damping slots report effective PD gains; actual applied torque slot retained; 78D unchanged"})
        return row


class ScutFlatEffortScaleEnv(ScutFlatBodyMassEnv):
    body_mass_dr_class = ScutEffortScaleDR

    def _encode(self):
        obs = super()._encode()
        dr = getattr(self, "full_dr", None)
        if not hasattr(dr, "effort_scale") or not getattr(self, "_delay_ready", False):
            return obs
        extra = obs["critic"][:, 39:].clone()
        effective_stiffness = torch.cat((60.0 * dr.leg_gain_scale,
                                        torch.zeros_like(dr.wheel_gain_scale)), -1) * dr.effort_scale
        effective_damping = torch.cat((torch.full_like(dr.leg_gain_scale, 2.0),
                                      0.6 * dr.wheel_gain_scale), -1) * dr.effort_scale
        extra[:, :6] = observation_component(self.reward.cfg, "joint_stiffness", effective_stiffness, "critic")
        extra[:, 6:12] = observation_component(self.reward.cfg, "joint_damping", effective_damping, "critic")
        obs["critic"] = torch.cat((obs["critic"][:, :39], extra), -1)
        self.reward.cache_raw_observations(dict(policy=obs["policy"]),
                                          dict(critic=obs["critic"][:, :39], extra=extra))
        return obs
