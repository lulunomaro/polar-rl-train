"""Print where the field task actually spawns the robot.

`reset_root_state_from_flat_patches` is the only reset in mjlab that does NOT add
``env.scene.env_origins`` to the sampled position, so the field task drops the robot from
~2.5 m.  This prints the raw ingredients so the fix is not guesswork.
"""
from __future__ import annotations

import sys
from dataclasses import asdict
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "train" / "rmvehicle" / "src"))

import rmvehicle  # noqa: E402,F401
from mjlab.envs import ManagerBasedRlEnv  # noqa: E402
from mjlab.tasks.registry import load_env_cfg  # noqa: E402


def main() -> int:
    cfg = load_env_cfg("RM2025-Later-CC-Field-v0", play=True)
    cfg.scene.num_envs = 4
    cfg.episode_length_s = 1e9
    cfg.auto_reset = True
    env = ManagerBasedRlEnv(cfg=cfg, device="cuda:0")
    E = env.unwrapped if hasattr(env, "unwrapped") else env
    terrain = E.scene.terrain
    patches = terrain.flat_patches["spawn"]
    print("flat_patches['spawn'].shape:", tuple(patches.shape))
    print("terrain_levels:", terrain.terrain_levels[:4].tolist())
    print("terrain_types :", terrain.terrain_types[:4].tolist())
    for lvl in range(min(3, patches.shape[0])):
        z = patches[lvl, :, 0, 2]
        print("level %d patch0 z per column: %s" % (lvl, [round(float(v), 3) for v in z[:6]]))
    print("patch0 xy of (level0,cols 0..3):",
          [[round(float(v), 3) for v in patches[0, c, 0, :2]] for c in range(4)])
    origins = E.scene.env_origins
    print("env_origins[:4]:", [[round(float(v), 3) for v in o] for o in origins[:4]])
    robot = E.scene["robot"]
    print("default_root_state z:", float(robot.data.default_root_state[0, 2]))
    E.reset()
    print("root_z after reset:", [round(float(v), 3) for v in robot.data.root_link_pos_w[:4, 2]])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
