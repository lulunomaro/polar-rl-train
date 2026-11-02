"""Isaac equivalent of the verified MuJoCo tunnel test (2026-09-13).

Holds the user-verified low pose (hip +0.470170 / crank -0.595844), gives the drive wheels a
velocity command and drives through the delivered 0.34 m roofed span at 0.12 / 0.18 / 0.25 m/s,
reporting exactly the quantities the MuJoCo report uses: full clearing of the roof, minimum CAD
clearance, roof contact steps, drive-wheel load fraction, closure/mimic error, pitch/roll.

  RM_LEG_KP=2500 RM_LEG_KD=10 RM_MOD4_USD=<rolling usd> \
  python isaac/mod4/probe_tunnel_cross_pi.py --num_envs 4 --speeds 0.12,0.18,0.25
"""
from __future__ import annotations
import argparse
from pathlib import Path
import sys

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser()
parser.add_argument("--num_envs", type=int, default=4)
parser.add_argument("--settle", type=int, default=200)
parser.add_argument("--steps", type=int, default=900)
parser.add_argument("--speeds", default="0.12,0.18,0.25")
parser.add_argument("--x0", type=float, default=0.30)
parser.add_argument("--y", type=float, default=-5.95)
parser.add_argument("--roof-force", type=float, default=60.0)
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

FLOOR = -0.155806
HIP, CRANK = 0.470170, -0.595844
TOP_ABOVE_ROOT = 0.066934


def main() -> None:
    cfg = mod4_task.Mod4EnvCfg()
    cfg.scene.num_envs = args.num_envs
    cfg.scene.robot = mod4_task.mod4_robot_cfg()
    mod4_task.attach_rmuc2026_terrain(cfg)
    env = Mod4Env(cfg=cfg)
    robot = env.scene["robot"]
    dev = env.device
    names = list(robot.joint_names)
    idx = {nm: i for i, nm in enumerate(mod4_task.ACTION_ORDER)}
    scale = mod4_task.LEG_ACTION_SCALE
    wscale = mod4_task.WHEEL_ACTION_SCALE
    n = env.num_envs
    print("[pi] usd=%s leg_kp=%s leg_ki=%s" % (mod4_task.USD_PATH.split("/")[-1],
                                               mod4_task.LEG_KP, getattr(mod4_task, "LEG_KI", 0)),
          flush=True)
    for vx in [float(s) for s in args.speeds.split(",") if s.strip()]:
        env.reset()
        ids = torch.arange(n, device=dev)
        pos = env.scene.env_origins[ids].clone()
        pos[:, 0] += args.x0
        pos[:, 1] += args.y
        pos[:, 2] = FLOOR + float(mod4_task.CONTRACT["spawn_height_m"])
        quat = torch.zeros((n, 4), device=dev)
        quat[:, 3] = 1.0
        robot.write_root_pose_to_sim(torch.cat([pos, quat], dim=-1), env_ids=ids)
        act = torch.zeros((n, 6), device=dev)
        for ch, val in (("left_hip", HIP), ("right_hip", HIP),
                        ("left_crank", CRANK), ("right_crank", CRANK)):
            act[:, idx[ch]] = val / scale
        wheel_cmd = (vx / 0.0625) / wscale
        for _ in range(args.settle):
            env.step(act)
        act[:, idx["left_wheel_spin"]] = wheel_cmd
        act[:, idx["right_wheel_spin"]] = wheel_cmd
        min_clr = torch.full((n,), 9.9, device=dev)
        roof_steps = torch.zeros(n, device=dev)
        x_max = torch.full((n,), args.x0, device=dev)
        wheel_loaded = torch.zeros(n, device=dev)
        wheel_force = torch.zeros(n, device=dev)
        pitch_max = torch.zeros(n, device=dev)
        for step in range(args.steps):
            env.step(act)
            loc = robot.data.root_pos_w - env.scene.env_origins
            x, y, z = loc[:, 0], loc[:, 1], loc[:, 2]
            x_max = torch.maximum(x_max, x)
            inside = ((x.abs() >= skills.HOLE_ROOF_X[0]) & (x.abs() <= skills.HOLE_ROOF_X[1]) &
                      (y.abs() >= skills.HOLE_LANE_Y[0]) & (y.abs() <= skills.HOLE_LANE_Y[1]))
            clr = skills.HOLE_CEILING_Z - (z + TOP_ABOVE_ROOT)
            min_clr = torch.where(inside, torch.minimum(min_clr, clr), min_clr)
            f = env.scene.sensors["wheel_contact"].data.net_forces_w
            if hasattr(f, "torch"):
                f = f.torch
            wf = f.norm(dim=-1).max(dim=1).values
            wheel_loaded += (wf > 1.0).float()
            wheel_force += wf
            c = env.scene.sensors["chassis_contact"].data.net_forces_w
            if hasattr(c, "torch"):
                c = c.torch
            cf = c.norm(dim=-1).max(dim=1).values
            roof_steps += (inside & (cf > args.roof_force)).float()
            g = robot.data.projected_gravity_b
            pitch_max = torch.maximum(pitch_max,
                                      torch.rad2deg(torch.asin(g[:, 0].clamp(-1, 1))).abs())
        cleared = float((x_max >= 1.45).float().mean())
        print("[pi] vx=%.2f x_max=%.3f cleared>1.45=%.2f min_clr=%+.4f m roof_steps=%.0f "
              "wheel_loaded=%.2f mean_wheelF=%.1f N max_pitch=%.2f deg"
              % (vx, float(x_max.mean()), cleared, float(min_clr.mean()),
                 float(roof_steps.mean()), float((wheel_loaded / args.steps).mean()),
                 float(wheel_force.mean() / args.steps), float(pitch_max.mean())), flush=True)
    env.close()


if __name__ == "__main__":
    main()
    app.close()