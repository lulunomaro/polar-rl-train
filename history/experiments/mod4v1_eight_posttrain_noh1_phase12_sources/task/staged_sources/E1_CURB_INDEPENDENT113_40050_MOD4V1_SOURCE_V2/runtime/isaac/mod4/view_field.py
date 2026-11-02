"""Open the MOD4 robot on the full RMUC2026 feature set in the Isaac Lab visualizer.

Training runs headless on the target (the Lab 3.0 visualizer crashes when the training loop
resets thousands of environments), so this is the window you actually look at: the same
robot USD, the same field builder (stairs, ramps, launch ramp / 飞坡, gap, barricade and the
250 mm x 800 mm x 300 mm tunnel), no learning and no episode resets.

    <isaaclab python> isaac/mod4/view_field.py --viz kit --num_envs 2

Keys/mouse: orbit with the mouse in the viewport; Ctrl+C in the terminal to quit.
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser()
parser.add_argument("--num_envs", type=int, default=1,
                    help="1 keeps a single field close to the camera; environments are "
                         "spaced 13 m apart so more of them push the camera far away")
parser.add_argument("--vx", type=float, default=0.6, help="slow forward command for the show")
parser.add_argument("--steps", type=int, default=0, help="0 = run until Ctrl+C")
parser.add_argument("--seconds", type=float, default=0.0, help="wall-clock limit, 0 = none")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
launcher = AppLauncher(args)
app = launcher.app

import torch  # noqa: E402
from isaaclab.envs import ManagerBasedRLEnv  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(1, str(HERE.parent))
import mod4_task  # noqa: E402


def main() -> None:
    os.environ.setdefault("RM_MOD4_TERRAIN", "field")
    cfg = mod4_task.Mod4EnvCfg()
    cfg.scene.num_envs = args.num_envs
    env = ManagerBasedRLEnv(cfg=cfg)
    # Frame the first environment the way a person wants to look at it: the robot on the
    # centre lane with the stairs/ramps ahead and the tunnel lane to its left.
    try:
        env.sim.set_camera_view([2.4, -2.9, 1.25], [0.85, 0.25, 0.32])
    except Exception as exc:  # pragma: no cover - viewer-only nicety
        print("[viewer] camera view not set:", exc)
    print("[viewer] terrain:", mod4_task.TERRAIN,
          "| tunnel hole (h,w,d):", mod4_task.FIELD_INFO.get("tunnel_hole_m"),
          "| features:", sorted(k for k in mod4_task.FIELD_INFO if k.endswith("_spawn"))[:4])
    env.reset()
    # A gentle forward command so the robots actually walk instead of standing still.
    act = torch.zeros((env.num_envs, 6), device=env.device)
    act[:, 4] = args.vx / 10.0
    act[:, 5] = args.vx / 10.0
    robot = env.scene["robot"]
    print("[viewer] robot root xyz at t=0:",
          [[round(float(c), 3) for c in row] for row in robot.data.root_pos_w[:2]], flush=True)
    t0 = time.time()
    step = 0
    while True:
        env.step(act)
        step += 1
        if args.steps and step >= args.steps:
            break
        if args.seconds and time.time() - t0 > args.seconds:
            break
    print("[viewer] done after %d steps" % step)
    env.close()


if __name__ == "__main__":
    main()
    app.close()
