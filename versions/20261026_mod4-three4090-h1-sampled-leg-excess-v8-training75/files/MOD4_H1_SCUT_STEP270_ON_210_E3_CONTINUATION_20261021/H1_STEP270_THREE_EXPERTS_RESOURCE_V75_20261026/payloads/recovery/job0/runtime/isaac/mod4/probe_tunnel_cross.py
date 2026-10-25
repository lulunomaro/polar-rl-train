"""Can a SCRIPTED robot drive at speed, squat late and coast through the dog hole?

This is the decisive A/B for the 2026-09-12 idler-friction finding.  probe_tunnel_inertia
teleports the robot with an initial velocity, but on this Isaac build that velocity never
reaches the solver (every entry speed 0.15..0.90 produced the same 9 mm of travel), so the
coast has to be measured the honest way: DRIVE the robot with a scripted wheel command, then
switch the leg channels to the crouch pose at a chosen x and keep commanding the wheels.

  RM_MOD4_USD=<absolute path to the USD variant> ... \\
  python isaac/mod4/probe_tunnel_cross.py --num_envs 4 --steps 600 \\
      --speeds 0.6,1.0,1.4 --fold-at 0.36,0.51 --crouch trainwindow

Per (speed, fold) case it prints the speed at the mouth and at the exit, the travel, the
worst CAD-skin clearance under the roof, the peak roof force, the mean wheel/guide contact
force while driving, and whether the robot cleared the roofed span.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser()
parser.add_argument("--num_envs", type=int, default=4)
parser.add_argument("--steps", type=int, default=600)
parser.add_argument("--x0", type=float, default=0.30)
parser.add_argument("--y", type=float, default=-5.95)
parser.add_argument("--speeds", default="0.6,1.0,1.4")
parser.add_argument("--fold-at", default="0.36,0.51")
parser.add_argument("--crouch", default="trainwindow", choices=("trainwindow", "hardstop"))
parser.add_argument("--wheel-after-fold", type=float, default=1.0,
                    help="1 = keep commanding the wheels after the fold, 0 = coast")
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

CAD_TOP_ABOVE_ROOT_M = skills.CAD_TOP_ABOVE_ROOT_M
ROOF_X = skills.HOLE_ROOF_X
LANE_Y = skills.HOLE_LANE_Y
X_MOUTH = float(ROOF_X[0])
X_EXIT = float(ROOF_X[1])
X_CLEAR = X_EXIT + 0.35


def main() -> None:
    cfg = mod4_task.Mod4EnvCfg()
    cfg.scene.num_envs = args.num_envs
    mod4_task.attach_rmuc2026_terrain(cfg)
    env = Mod4Env(cfg=cfg)
    robot = env.scene["robot"]
    n, dev = env.num_envs, env.device
    idx = {nm: i for i, nm in enumerate(mod4_task.ACTION_ORDER)}
    scale = mod4_task.LEG_ACTION_SCALE
    stop = mod4_task.CONTRACT["mechanical_stop"]
    hip_hard = float(stop["hip_rad"])
    diff_tr = float(mod4_task.CONTRACT["training_window"]["input_difference_min_rad"])
    diff_hard = float(stop["input_difference_rad"])
    hip, diff = ((hip_hard, diff_tr) if args.crouch == "trainwindow" else (hip_hard, diff_hard))
    floor_z = -0.155806
    # the runway the delivered route gives: spawn 0.30 -> mouth 0.760
    print("[cross] usd=%s crouch=%s hip=%.4f diff=%.4f runway=%.3f m"
          % (mod4_task.USD_PATH.split("/")[-1], args.crouch, hip, diff, X_MOUTH - args.x0),
          flush=True)
    print("[cross] %6s %7s %8s %8s %8s %8s %8s %7s %8s %8s %7s"
          % ("vx_cmd", "fold_x", "x_end", "vx_mouth", "vx_exit", "min_clr", "roofF", "wheelF",
             "guideF", "clear145", "term"), flush=True)

    for vx in [float(s) for s in args.speeds.split(",") if s.strip()]:
        for fold_x in [float(s) for s in args.fold_at.split(",") if s.strip()]:
            env.reset()
            ids = torch.arange(n, device=dev)
            pos = env.scene.env_origins[ids].clone()
            pos[:, 0] += args.x0
            pos[:, 1] += args.y
            pos[:, 2] = floor_z + float(mod4_task.CONTRACT["spawn_height_m"])
            quat = torch.zeros((n, 4), device=dev)
            quat[:, 3] = 1.0
            robot.write_root_pose_to_sim(torch.cat([pos, quat], dim=-1), env_ids=ids)
            robot.write_root_velocity_to_sim(torch.zeros((n, 6), device=dev), env_ids=ids)

            wheel_cmd = vx / (0.0625 * mod4_task.WHEEL_ACTION_SCALE)
            act = torch.zeros((n, 6), device=dev)
            vx_mouth = torch.zeros(n, device=dev)
            vx_exit = torch.zeros(n, device=dev)
            x_end = torch.full((n,), args.x0, device=dev)
            min_clr = torch.full((n,), 9.9, device=dev)
            roof_peak = 0.0
            wheel_f = []
            guide_f = []
            term_step = -1
            for step in range(args.steps):
                loc = robot.data.root_pos_w - env.scene.env_origins
                x = loc[:, 0]
                folded = x >= fold_x
                # legs: standing (zeros) until the fold, then the crouch pose on all 4 channels
                act[:, idx["left_hip"]] = torch.where(folded, torch.full_like(x, hip / scale),
                                                      torch.zeros_like(x))
                act[:, idx["right_hip"]] = act[:, idx["left_hip"]]
                act[:, idx["left_crank"]] = torch.where(
                    folded, torch.full_like(x, (hip + diff) / scale), torch.zeros_like(x))
                act[:, idx["right_crank"]] = act[:, idx["left_crank"]]
                w = torch.full_like(x, wheel_cmd) if args.wheel_after_fold else torch.where(
                    folded, torch.zeros_like(x), torch.full_like(x, wheel_cmd))
                act[:, idx["left_wheel_spin"]] = w
                act[:, idx["right_wheel_spin"]] = w
                out = env.step(act)
                if isinstance(out, tuple) and len(out) >= 3 and hasattr(out[2], "any"):
                    if bool(out[2].any()) and term_step < 0:
                        term_step = step
                loc = robot.data.root_pos_w - env.scene.env_origins
                x, y, z = loc[:, 0], loc[:, 1], loc[:, 2]
                vxb = robot.data.root_lin_vel_b[:, 0]
                near_mouth = (x >= X_MOUTH - 0.02) & (x < X_MOUTH + 0.02)
                near_exit = (x >= X_EXIT - 0.02) & (x < X_EXIT + 0.02)
                vx_mouth = torch.where(near_mouth, vxb, vx_mouth)
                vx_exit = torch.where(near_exit, vxb, vx_exit)
                x_end = torch.maximum(x_end, x)
                inside = ((x.abs() >= ROOF_X[0]) & (x.abs() <= ROOF_X[1]) &
                          (y.abs() >= LANE_Y[0]) & (y.abs() <= LANE_Y[1]))
                clr = skills.HOLE_CEILING_Z - (z + CAD_TOP_ABOVE_ROOT_M)
                min_clr = torch.where(inside, torch.minimum(min_clr, clr), min_clr)
                f = env.scene.sensors["chassis_contact"].data.net_forces_w
                if hasattr(f, "torch"):
                    f = f.torch
                roof_peak = max(roof_peak, float(f.norm(dim=-1).max()))
                if step < 120:
                    for name, acc in (("wheel_contact", wheel_f), ("guide_contact", guide_f)):
                        g = env.scene.sensors[name].data.net_forces_w
                        if hasattr(g, "torch"):
                            g = g.torch
                        acc.append(float(g.norm(dim=-1).max(dim=1).values.mean()))
            cleared = float((x_end >= X_CLEAR).float().mean())
            print("[cross] %6.2f %7.2f %8.3f %8.3f %8.3f %8.4f %8.1f %7.1f %8.1f %7.2f %7d"
                  % (vx, fold_x, float(x_end.mean()), float(vx_mouth.mean()),
                     float(vx_exit.mean()), float(min_clr.mean()), roof_peak,
                     sum(wheel_f) / max(1, len(wheel_f)), sum(guide_f) / max(1, len(guide_f)),
                     cleared, term_step), flush=True)
    env.close()


if __name__ == "__main__":
    main()
    app.close()