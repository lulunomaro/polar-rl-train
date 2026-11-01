"""Scripted crouch-and-cross on the FIXED plant: is the delivered dog hole actually solvable?

P2 asks for a dedicated, DR-off environment that proves a skill is learnable BEFORE the PPO
stage burns GPU hours.  This probe drives the robot by hand (no policy): hold the CAD
training-window low pose (hip = +0.4503 rad, crank = hip - 1.0843 rad) and command a constant
wheel rate towards the delivered `tunnel` route goal, then reports whether the route's own
bookkeeping fires (underpass_visited / success) and what the roof contact force was.

    .venv-isaaclab\\Scripts\\python.exe isaac/mod4/probe_tunnel_script.py --headless \\
        --num_envs 4 --steps 700 --vx 0.35
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser()
parser.add_argument("--num_envs", type=int, default=4)
parser.add_argument("--steps", type=int, default=700)
parser.add_argument("--vx", type=float, default=0.35)
parser.add_argument("--crouch-steps", type=int, default=60)
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
launcher = AppLauncher(args)
app = launcher.app

import torch  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import mod4_task  # noqa: E402
from mod4_env import Mod4Env  # noqa: E402


def main() -> None:
    cfg = mod4_task.Mod4EnvCfg()
    cfg.scene.num_envs = args.num_envs
    mod4_task.attach_rmuc2026_terrain(cfg)
    env = Mod4Env(cfg=cfg)
    env.reset()
    robot = env.scene["robot"]
    n = env.num_envs
    dev = env.device
    stop = mod4_task.CONTRACT["mechanical_stop"]
    win = mod4_task.CONTRACT.get("training_window", {}).get("input_difference_min_rad", -1.0843)
    hip = float(stop["hip_rad"])
    crank = hip + float(win)                     # deepest pose the policy is allowed to command
    scale = mod4_task.LEG_ACTION_SCALE
    leg = torch.zeros((n, 4), device=dev)
    leg[:, 0] = hip / scale
    leg[:, 1] = crank / scale
    leg[:, 2] = hip / scale
    leg[:, 3] = crank / scale
    wheel = args.vx / (0.0625 * mod4_task.WHEEL_ACTION_SCALE)
    print("[script] crouch hip=%.4f crank=%.4f (action %.3f/%.3f), wheel act %.3f"
          % (hip, crank, hip / scale, crank / scale, wheel), flush=True)

    act = torch.zeros((n, 6), device=dev)
    act[:, [0, 1, 3, 4]] = leg
    goal = torch.zeros(n, device=dev)
    start = torch.zeros(n, device=dev)
    min_z = torch.full((n,), 1e9, device=dev)
    max_roof_n = torch.zeros(n, device=dev)
    max_tilt = torch.zeros(n, device=dev)
    success = torch.zeros(n, dtype=torch.bool, device=dev)
    stage_max = torch.zeros(n, dtype=torch.long, device=dev)
    cmd_lo = torch.full((n,), 9.0, device=dev)
    cmd_hi = torch.zeros(n, device=dev)
    for step in range(args.steps):
        a = act.clone()
        if step >= args.crouch_steps:
            a[:, 2] = wheel
            a[:, 5] = wheel
        env.step(a)
        loc = robot.data.root_pos_w - env.scene.env_origins
        g = robot.data.projected_gravity_b
        tilt = torch.rad2deg(torch.acos((-g[:, 2]).clamp(-1.0, 1.0)))
        if step == 0:
            start = loc[:, 0].clone()
        goal = loc[:, 0].clone()
        min_z = torch.minimum(min_z, loc[:, 2])
        max_tilt = torch.maximum(max_tilt, tilt)
        f = env.scene.sensors["chassis_contact"].data.net_forces_w
        if hasattr(f, "torch"):
            f = f.torch
        max_roof_n = torch.maximum(max_roof_n, f.norm(dim=-1).max(dim=1).values)
        d = getattr(env, "_mod4_route_progress", None)
        if isinstance(d, dict) and "success" in d:
            success |= d["success"].bool()
        st = getattr(env, "_mod4_tunnel_state", None)
        if st is not None:
            stage_max = torch.maximum(stage_max, st)
        h = getattr(env, "_mod4_height_cmd", None)
        if h is not None:
            cmd_lo = torch.minimum(cmd_lo, h[:, 0])
            cmd_hi = torch.maximum(cmd_hi, h[:, 0])
    rc = getattr(env, "_mod4_routes", None)
    under = rc.underpass_visited.clone() if rc is not None else torch.zeros(n, dtype=torch.bool)
    for i in range(n):
        print("[script] env %2d  x %+.2f -> %+.2f (moved %+.2f)  min_root_z %.3f  "
              "chassis_peak %.0f N  underpass=%s success=%s  tilt_max %.0f deg  "
              "stage_max=%d height_cmd %.3f..%.3f"
              % (i, float(start[i]), float(goal[i]), float(goal[i] - start[i]),
                 float(min_z[i]), float(max_roof_n[i]), bool(under[i]), bool(success[i]),
                 float(max_tilt[i]), int(stage_max[i]), float(cmd_lo[i]), float(cmd_hi[i])),
              flush=True)
    print("[script] SUMMARY underpass %d/%d  success %d/%d  moved %.2f..%.2f m  "
          "chassis_peak %.0f N  min_root_z %.3f  stages %s"
          % (int(under.sum()), n, int(success.sum()), n, float((goal - start).min()),
             float((goal - start).max()), float(max_roof_n.max()), float(min_z.min()),
             [int(v) for v in stage_max]),
          flush=True)
    env.close()


if __name__ == "__main__":
    main()
    app.close()
