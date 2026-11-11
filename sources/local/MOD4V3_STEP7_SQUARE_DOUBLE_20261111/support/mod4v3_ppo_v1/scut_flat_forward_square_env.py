"""User-authorized next grade: double both underspeed and overspeed squared error."""
from .scut_flat_physical_delay_env import ScutFlatPhysicalDelayEnv
from .scut_flat_rewards import configuration_v2, make_reward_class


def configuration_forward_square():
    cfg = configuration_v2()
    # The source term squares sigma * error, so use SI error without attenuation.
    cfg.lin_vel_xy_square_sigma = 1.0
    cfg.rewards["track_lin_vel_xy_square"] = -1.0
    return cfg


class ScutFlatForwardSquareEnv(ScutFlatPhysicalDelayEnv):
    """Keep the repaired DR/plant/controller and strengthen velocity tracking."""

    def _make_reward(self, meta):
        return make_reward_class(meta, cfg_factory=configuration_forward_square)(
            self.view, self.num_envs, self.device
        )
