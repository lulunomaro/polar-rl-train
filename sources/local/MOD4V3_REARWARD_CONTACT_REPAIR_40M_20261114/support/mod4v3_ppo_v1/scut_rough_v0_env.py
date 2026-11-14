"""SCUT Rough-v0: Flat-v2 command composition on the saved rough terrain."""
from .scut_flat_v2_env import ScutFlatV2Env
from .scut_flat_rewards import configuration_rough_v0, make_reward_class


class ScutRoughV0Env(ScutFlatV2Env):
    """SCUT Rough-v0 with a 2.2 m/s speed cap."""

    # Do not inherit Flat-v2's SCUT-style guard bypass for long rough runs.
    enforce_closure_reset = False
    rough_terrain = True

    def __init__(self, cfg, meta, bank):
        super().__init__(cfg, meta, bank)
        self.height_range = (0.20, 0.42)
        self.command_vx = (-2.2, 2.2)

    def _make_reward(self, meta):
        return make_reward_class(meta, cfg_factory=configuration_rough_v0)(
            self.view, self.num_envs, self.device
        )
