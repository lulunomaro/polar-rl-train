"""mjlab task package for the dual wheel-leg robot rebuilt from 整车总装.STEP.

RMVehicle-Flat-v0     the earlier serial-chain model (regression baseline).
RMVehicle-CC-Flat-v0  the validated similar-linkage (kite four-bar) closed chain.
"""
from mjlab.tasks.registry import register_mjlab_task

from .env_cfgs import (field_cc_env_cfg, field_rm2025_later_env_cfg,
                     flat_cc_env_cfg, flat_env_cfg, flat_rm2025_later_env_cfg,
                     skills_cc_env_cfg, skills_rm2025_later_env_cfg)
from .rl_cfg import flat_ppo_runner_cfg

register_mjlab_task(
  task_id="RMVehicle-Flat-v0",
  env_cfg=flat_env_cfg(),
  play_env_cfg=flat_env_cfg(play=True),
  rl_cfg=flat_ppo_runner_cfg(),
)

register_mjlab_task(
  task_id="RMVehicle-CC-Flat-v0",
  env_cfg=flat_cc_env_cfg(),
  play_env_cfg=flat_cc_env_cfg(play=True),
  rl_cfg=flat_ppo_runner_cfg(),
)

register_mjlab_task(
  task_id="RMVehicle-CC-Skills-v0",
  env_cfg=skills_cc_env_cfg(),
  play_env_cfg=skills_cc_env_cfg(play=True),
  rl_cfg=flat_ppo_runner_cfg(),
)

register_mjlab_task(
  task_id="RMVehicle-CC-Field-v0",
  env_cfg=field_cc_env_cfg(),
  play_env_cfg=field_cc_env_cfg(play=True),
  rl_cfg=flat_ppo_runner_cfg(),
)

register_mjlab_task(
  task_id="RM2025-Later-CC-Flat-v0",
  env_cfg=flat_rm2025_later_env_cfg(),
  play_env_cfg=flat_rm2025_later_env_cfg(play=True),
  rl_cfg=flat_ppo_runner_cfg(),
)

register_mjlab_task(
  task_id="RM2025-Later-CC-Skills-v0",
  env_cfg=skills_rm2025_later_env_cfg(),
  play_env_cfg=skills_rm2025_later_env_cfg(play=True),
  rl_cfg=flat_ppo_runner_cfg(),
)

register_mjlab_task(
  task_id="RM2025-Later-CC-Field-v0",
  env_cfg=field_rm2025_later_env_cfg(),
  play_env_cfg=field_rm2025_later_env_cfg(play=True),
  rl_cfg=flat_ppo_runner_cfg(),
)
