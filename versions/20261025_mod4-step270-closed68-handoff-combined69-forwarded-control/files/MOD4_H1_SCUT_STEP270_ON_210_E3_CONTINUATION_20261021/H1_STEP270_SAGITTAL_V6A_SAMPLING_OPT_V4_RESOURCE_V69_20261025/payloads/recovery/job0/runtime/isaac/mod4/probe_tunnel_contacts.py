"""Goal §2: classify the dog-hole contacts -- roller vs belly vs roof -- with real forces.

The chassis contact sensor lumps every contact of that body together, and the eight guide
rollers are part of it.  This probe drives the robot into the crouch and prints, every N steps:
the chassis force, the guide-roller force (separate sensor on `guide_wheel_00..07`), the
belly-only remainder, the root height above the local floor and the CAD-skin roof-hit flag, so
the three classes the goal asks for are separated by measurement rather than by a threshold.

    .venv-isaaclab\\Scripts\\python.exe isaac/mod4/probe_tunnel_contacts.py --headless --num_envs 4
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser()
parser.add_argument("--num_envs", type=int, default=4)
parser.add_argument("--steps", type=int, default=600)
parser.add_argument("--every", type=int, default=100)
parser.add_argument("--vx", type=float, default=0.25)
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
launcher = AppLauncher(args)
app = launcher.app

import torch  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import mod4_task  # noqa: E402
import skills_isaac as skills  # noqa: E402
from mod4_env import Mod4Env  # noqa: E402


def forces(env, name):
    s = env.scene.sensors[name]
    f = s.data.net_forces_w
    if hasattr(f, "torch"):
        f = f.torch
    return f.norm(dim=-1).amax(dim=1)


def main() -> None:
    cfg = mod4_task.Mod4EnvCfg()
    cfg.scene.num_envs = args.num_envs
    mod4_task.attach_rmuc2026_terrain(cfg)
    env = Mod4Env(cfg=cfg)
    env.reset()
    robot = env.scene["robot"]
    n, dev = env.num_envs, env.device
    idx = {nm: i for i, nm in enumerate(mod4_task.ACTION_ORDER)}
    scale = mod4_task.LEG_ACTION_SCALE
    stop = mod4_task.CONTRACT["mechanical_stop"]
    hip = float(stop["hip_rad"])
    diff = float(mod4_task.CONTRACT["training_window"]["input_difference_min_rad"])
    wheel = args.vx / (0.0625 * mod4_task.WHEEL_ACTION_SCALE)
    act = torch.zeros((n, 6), device=dev)
    act[:, idx["left_hip"]] = hip / scale
    act[:, idx["right_hip"]] = hip / scale
    act[:, idx["left_crank"]] = (hip + diff) / scale
    act[:, idx["right_crank"]] = (hip + diff) / scale
    act[:, idx["left_wheel_spin"]] = wheel
    act[:, idx["right_wheel_spin"]] = wheel
    peak = {"chassis": 0.0, "guide": 0.0, "belly": 0.0}
    roof_steps = 0
    print("[contacts] step | root_h | chassis_N | guide_N | belly_N | roof_hit_envs", flush=True)
    for step in range(args.steps):
        env.step(act)
        c = forces(env, "chassis_contact")
        g = forces(env, "guide_contact")
        belly = (c - g).clamp(min=0.0)
        loc = robot.data.root_pos_w - env.scene.env_origins
        root_h = float((loc[:, 2] - skills.HOLE_FLOOR_Z).mean())
        hit = skills.tunnel_roof_hit_cad(env)
        roof_steps += int(hit.sum())
        peak["chassis"] = max(peak["chassis"], float(c.max()))
        peak["guide"] = max(peak["guide"], float(g.max()))
        peak["belly"] = max(peak["belly"], float(belly.max()))
        if step % args.every == 0 or step == args.steps - 1:
            print("[contacts] %4d | %+.3f | %8.0f | %7.0f | %7.0f | %d/%d"
                  % (step, root_h, float(c.mean()), float(g.mean()), float(belly.mean()),
                     int(hit.sum()), n), flush=True)
    print("[contacts] peak chassis %.0f N | guide %.0f N | belly %.0f N | roof-hit steps %d"
          % (peak["chassis"], peak["guide"], peak["belly"], roof_steps), flush=True)
    print("[contacts] classes: guide-vs-ground <= %.0f N (allowed); belly-vs-ground <= %.0f N "
          "(penalised/terminated); roof hits %d (terminated when the CAD skin is 2 mm inside)"
          % (peak["guide"], peak["belly"], roof_steps), flush=True)
    env.close()


if __name__ == "__main__":
    main()
    app.close()
