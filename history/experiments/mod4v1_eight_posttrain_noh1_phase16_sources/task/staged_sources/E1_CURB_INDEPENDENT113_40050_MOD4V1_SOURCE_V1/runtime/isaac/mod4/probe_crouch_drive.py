"""How fast can the crouched robot actually drive?  (2026-09-12)

The tunnel runs keep ending with the robot alive but not advancing, and the trajectory probe
showed ~0.06 m/s at the fitting crouch.  This probe holds a few leg poses (the CAD pose family
that the MuJoCo measurement mapped to root heights) while commanding a constant wheel rate, and
reports the achieved body speed, wheel rate and wheel contact force, so "is the crossing
physically possible, and at what speed" stops being a guess.

    .venv-isaaclab\\Scripts\\python.exe isaac/mod4/probe_crouch_drive.py --headless --steps 300
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser()
parser.add_argument("--num_envs", type=int, default=8)
parser.add_argument("--steps", type=int, default=300)
parser.add_argument("--vx", type=float, default=0.30)
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
launcher = AppLauncher(args)
app = launcher.app

import torch  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import mod4_task  # noqa: E402
from mod4_env import Mod4Env  # noqa: E402

POSE_CASES = (
    ("stand", 0.0, 0.0),
    ("root~0.23", 0.31, -1.00),
    ("root~0.20", 0.31, -1.04),
    ("root~0.18", 0.35, -1.06),
    ("hardstop", 0.4503, -1.0843),
)


def main() -> None:
    cfg = mod4_task.Mod4EnvCfg()
    cfg.scene.num_envs = args.num_envs
    mod4_task.attach_rmuc2026_terrain(cfg)
    env = Mod4Env(cfg=cfg)
    robot = env.scene["robot"]
    names = list(robot.joint_names)
    idx = {n: i for i, n in enumerate(mod4_task.ACTION_ORDER)}
    scale = mod4_task.LEG_ACTION_SCALE
    wheel_cmd = args.vx / (0.0625 * mod4_task.WHEEL_ACTION_SCALE)
    print("[crouch-drive] commanded wheel rate %.2f rad/s for vx %.2f m/s"
          % (wheel_cmd * mod4_task.WHEEL_ACTION_SCALE, args.vx), flush=True)
    print("[crouch-drive] %-12s %8s %8s %8s %9s %9s" %
          ("case", "root_z", "vx", "wheel", "wheelF_N", "slip"), flush=True)
    for label, hip, diff in POSE_CASES:
        act = torch.zeros((env.num_envs, 6), device=env.device)
        act[:, idx["left_hip"]] = hip / scale
        act[:, idx["left_crank"]] = (hip + diff) / scale
        act[:, idx["right_hip"]] = hip / scale
        act[:, idx["right_crank"]] = (hip + diff) / scale
        act[:, idx["left_wheel_spin"]] = wheel_cmd
        act[:, idx["right_wheel_spin"]] = wheel_cmd
        env.reset()
        for step in range(args.steps):
            env.step(act)
        loc = robot.data.root_pos_w - env.scene.env_origins
        vx = robot.data.root_lin_vel_b[:, 0]
        ids = [names.index(n) for n in mod4_task.WHEEL_ORDER]
        wv = robot.data.joint_vel[:, ids].mean(dim=1)
        f = env.scene.sensors["wheel_contact"].data.net_forces_w
        if hasattr(f, "torch"):
            f = f.torch
        fN = f.norm(dim=-1).max(dim=1).values
        slip = (wv * 0.0625 - vx).mean()
        print("[crouch-drive] %-12s %8.3f %8.3f %8.2f %9.0f %9.3f"
              % (label, float(loc[:, 2].mean()), float(vx.mean()), float(wv.mean()),
                 float(fN.mean()), float(slip)), flush=True)
    env.close()


if __name__ == "__main__":
    main()
    app.close()
