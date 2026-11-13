"""Pinned SCUT command class, with a single DirectRLEnv-timed manager clock."""
import importlib.util
import sys

from .config import command_recipe
from .upstream import source_path


def build_command_cfg(profile):
    """Import the verified source only after Isaac's application has started."""
    name = 'mod4v1_scut_pinned_commands'
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, source_path('commands'))
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    module = sys.modules[name]
    cfg = module.SpecialModeUniformVelocityCommandCfg(asset_name='robot')
    recipe = command_recipe(profile)
    for key in ('resampling_time_range', 'heading_command', 'heading_control_stiffness',
                'rel_standing_envs', 'rel_heading_envs', 'special_modes',
                'special_mode_min_episode_time', 'special_mode_require_stable',
                'special_mode_stable_projected_gravity_xy_norm_max',
                'special_mode_stable_root_lin_vel_b_abs_max',
                'special_mode_stable_root_ang_vel_b_abs_max'):
        setattr(cfg, key, recipe[key])
    cfg.ranges = module.UniformVelocityCommandCfg.Ranges(**recipe['ranges'])
    cfg.debug_vis = False
    return cfg


class RewardTailCommand:
    """Delegate command values and perform the real manager update at reward tail.

    The later ManagerBasedRLEnv post-reset call is suppressed by the SDK bridge.
    This keeps resampling and state hooks in source env.py:4047-4051 order.
    """
    def __init__(self, term, compute):
        self.term, self._compute = term, compute

    def __getattr__(self, name):
        return getattr(self.term, name)

    def compute(self, dt):
        return self._compute(dt=dt)
