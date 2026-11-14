"""Stage 2b: spring-damping stage with speed-preserving fine-tune reward."""

from .scut_flat_spring_damping_env import ScutFlatSpringDampingEnv, SpringDampingDR
from .scut_flat_rewards import configuration_v2_speed_preserve, make_reward_class


class SpeedPreserveDR(SpringDampingDR):
    def summary(self):
        row = super().summary()
        row.update(
            profile='flat_speed_preserve_stage2b',
            stage='joint_friction_50pct + spring_damping_25pct + speed_preserve',
            reward_profile='flat_v2_speed_preserve',
            speed_preserve_error_cap_m_s=0.5,
            speed_preserve_weight=-0.5,
        )
        return row


class ScutFlatSpeedPreserveEnv(ScutFlatSpringDampingEnv):
    """Keep stage-2 DR and fine-tune with a mild vx preservation term."""

    def __init__(self, cfg, meta, bank):
        super().__init__(cfg, meta, bank)
        self.full_dr = SpeedPreserveDR(self)
        self.mild_dr = self.full_dr
        self._mild_dr = self.full_dr

    def _make_reward(self, meta):
        return make_reward_class(meta, cfg_factory=configuration_v2_speed_preserve)(
            self.view, self.num_envs, self.device
        )
