"""Verify P0-2: every env now carries a task bucket, its mode bits and a matching command."""
from __future__ import annotations
import sys
from pathlib import Path
from isaaclab.app import AppLauncher
import argparse
parser = argparse.ArgumentParser(); parser.add_argument("--num_envs", type=int, default=12)
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
launcher = AppLauncher(args); app = launcher.app
import torch  # noqa: E402
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import mod4_task  # noqa: E402
from mod4_env import Mod4Env  # noqa: E402


def main() -> None:
    cfg = mod4_task.Mod4EnvCfg(); cfg.scene.num_envs = args.num_envs
    env = Mod4Env(cfg=cfg)
    env.reset()
    for _ in range(3):
        env.step(torch.zeros(env.num_envs, 6, device=env.device))
    task = env._mod4_task_id
    modes = mod4_task.mode_onehot(env)
    cmd = env.command_manager.get_term("twist").command
    height = env._mod4_height_cmd
    print("[p0] env | task | mode bits (normal/stair/slope/rec/jump/height/time) | cmd vx,vy,wz | h", flush=True)
    names = {0: "normal", 1: "stair", 2: "slope", 3: "tunnel", 4: "jump", 5: "gyro"}
    for i in range(env.num_envs):
        print("   %2d | %-6s | %s | %+.2f %+.2f %+.2f | %.2f"
              % (i, names.get(int(task[i]), "?"), [int(v) for v in modes[i]],
                 float(cmd[i, 0]), float(cmd[i, 1]), float(cmd[i, 2]), float(height[i, 0])), flush=True)
    env.close()


if __name__ == "__main__":
    main(); app.close()