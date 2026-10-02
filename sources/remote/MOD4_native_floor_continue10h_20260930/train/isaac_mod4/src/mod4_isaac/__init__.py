"""MOD4 Isaac Lab task package: the delivered USD plant, the 35-D policy contract."""
from __future__ import annotations

import gymnasium as gym

from . import env_cfg, rl_cfg  # noqa: F401

gym.register(
    id="Mod4-Isaac-Flat-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.env_cfg:Mod4FlatEnvCfg",
        "rsl_rl_cfg_entry_point": f"{__name__}.rl_cfg:Mod4FlatPPORunnerCfg",
    },
)
