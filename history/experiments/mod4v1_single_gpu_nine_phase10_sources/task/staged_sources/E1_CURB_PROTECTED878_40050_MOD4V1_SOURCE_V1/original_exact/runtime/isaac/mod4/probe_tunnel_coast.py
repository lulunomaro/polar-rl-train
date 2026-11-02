"""Corrected dog-hole COAST probe (2026-09-12 19:10).

WHY THIS EXISTS
    probe_tunnel_inertia.py teleports the root to the crouch height but never writes the leg
    joints, so the robot starts with STANDING legs ~0.15 m inside the floor: the solver pushes it
    out and the measurement is dominated by that transient.  Evidence that this is a defect and
    not physics: wheelF(first50) = 0.0 N and *identical* numbers (0.15 m/s -> x_final 0.609,
    t_stop 2.15 s) for the delivered plant, the idler-friction variant and every other variant -
    while MuJoCo, which sets the pose and lets it settle first, predicts 0.031 m over the
    delivered friction average (0.525) and 0.515 m with the idler pair at 0.02.

WHAT IT DOES INSTEAD
    1. spawn on the tunnel route (0.46 m before the mouth, on the trench floor) and step
       `--settle` steps holding the crouch targets with zero wheel command, so the machine
       really settles onto whichever parts touch;
    2. report the settled root height above the local floor and the wheel-contact force -
       i.e. whether the tyres or the eight guide rollers carry it;
    3. only then apply the entry speed and measure 400 steps: coast distance, whether the roofed
       span (x >= 1.10) and the exit (x >= 1.45) are reached, the minimum CAD clearance under the
       roof, the peak roof force, and the wheel-contact force during the coast.

    RM_GUIDE_FRICTION=0.02 python isaac/mod4/probe_tunnel_coast.py --headless --num_envs 4 \
        --steps 400 --settle 150 --speeds 0.15,0.25,0.40,0.60

    RM_MOD4_USD=incoming/.../robot_idler002.usd ... (plant variant, if the trainer supports it)
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser()
parser.add_argument("--num_envs", type=int, default=4)
parser.add_argument("--steps", type=int, default=400)
parser.add_argument("--settle", type=int, default=150)
parser.add_argument("--speeds", default="0.15,0.25,0.40,0.60")
parser.add_argument("--pose", default="root018", choices=("root018", "hardstop"))
parser.add_argument("--wheel-cmd", type=float, default=0.0)
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
launcher = AppLauncher(args)
app = launcher.app

import torch  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import mod4_task  # noqa: E402
from mod4_env import Mod4Env  # noqa: E402

CAD_TOP_ABOVE_ROOT_M = 0.066934
ROOF_X = (0.760, 1.100)
LANE_Y = (5.42, 6.355)
POSE_CASES = {"root018": (0.35, -1.06), "hardstop": (0.4503, -1.0843)}


def main() -> None:
    hip, diff = POSE_CASES[args.pose]
    speeds = [float(s) for s in args.speeds.split(",") if s.strip()]
    cfg = mod4_task.Mod4EnvCfg()
    cfg.scene.num_envs = args.num_envs
    mod4_task.attach_rmuc2026_terrain(cfg)
    env = Mod4Env(cfg=cfg)
    env.reset()
    robot = env.scene["robot"]
    n = env.num_envs
    ids = torch.arange(n, device=env.device)
    idx = {name: i for i, name in enumerate(mod4_task.ACTION_ORDER)}
    scale = mod4_task.LEG_ACTION_SCALE
    chassis = env.scene.sensors["chassis_contact"]
    wheel_sensor = env.scene.sensors["wheel_contact"]

    act = torch.zeros((n, 6), device=env.device)
    act[:, idx["left_hip"]] = hip / scale
    act[:, idx["left_crank"]] = (hip + diff) / scale
    act[:, idx["right_hip"]] = hip / scale
    act[:, idx["right_crank"]] = (hip + diff) / scale
    act[:, idx["left_wheel_spin"]] = args.wheel_cmd
    act[:, idx["right_wheel_spin"]] = args.wheel_cmd

    print("[coast] pose=%s hip=%.4f diff=%.4f settle=%d steps=%d"
          % (args.pose, hip, diff, args.settle, args.steps), flush=True)
    print("[coast] %7s %9s %9s %9s %8s %10s %12s %10s %11s %11s"
          % ("v0", "x0", "x_final", "x_max", "t_stop", "cleared>1.10", "cleared>1.45",
             "min_clr_m", "roofF_N", "wheelF_N"), flush=True)

    for v0 in speeds:
        env.reset()
        for _ in range(args.settle):                      # settle in the crouch, no entry speed
            env.step(act)
        loc = robot.data.root_pos_w - env.scene.env_origins
        ground = getattr(env, "_mod4_ground_z", None)
        gz = float(ground.mean()) if ground is not None else float(loc[:, 2].mean()) - 0.18
        z_settle = float(loc[:, 2].mean())
        x0 = float(loc[:, 0].mean())
        wf = wheel_sensor.data.net_forces_w
        if hasattr(wf, "torch"):
            wf = wf.torch
        wheel_f_settle = float(wf.norm(dim=-1).max(dim=1).values.mean())
        cf = chassis.data.net_forces_w
        if hasattr(cf, "torch"):
            cf = cf.torch
        chassis_f_settle = float(cf.norm(dim=-1).max(dim=1).values.mean())
        print("[coast] settled: x0=%.3f root_z=%.4f ground_z=%.4f height=%.4f "
              "wheelF=%.1fN chassisF=%.1fN"
              % (x0, z_settle, gz, z_settle - gz, wheel_f_settle, chassis_f_settle), flush=True)

        vel = torch.zeros((n, 6), device=env.device)
        vel[:, 0] = v0
        robot.write_root_velocity_to_sim(vel, env_ids=ids)

        x_max = torch.full((n,), x0, device=env.device)
        v_end = torch.zeros(n, device=env.device)
        t_stop = torch.zeros(n, device=env.device)
        min_clear = torch.full((n,), 999.0, device=env.device)
        roof_peak = 0.0
        wheel_f_coast = []
        reset_at = -1
        for step in range(args.steps):
            out = env.step(act)
            if isinstance(out, tuple) and len(out) >= 3 and hasattr(out[2], "any"):
                if bool(out[2].any()) and reset_at < 0:
                    reset_at = step
            loc = robot.data.root_pos_w - env.scene.env_origins
            x, y, z = loc[:, 0], loc[:, 1], loc[:, 2]
            vx = robot.data.root_lin_vel_b[:, 0]
            x_max = torch.maximum(x_max, x)
            inside = ((x.abs() >= ROOF_X[0]) & (x.abs() <= ROOF_X[1]) &
                      (y.abs() >= LANE_Y[0]) & (y.abs() <= LANE_Y[1]))
            clr = (gz + 0.2472) - (z + CAD_TOP_ABOVE_ROOT_M)
            min_clear = torch.where(inside, torch.minimum(min_clear, clr), min_clear)
            f = chassis.data.net_forces_w
            if hasattr(f, "torch"):
                f = f.torch
            roof_peak = max(roof_peak, float(f.norm(dim=-1).max()))
            wf = wheel_sensor.data.net_forces_w
            if hasattr(wf, "torch"):
                wf = wf.torch
            wheel_f_coast.append(float(wf.norm(dim=-1).max(dim=1).values.mean()))
            moving = (vx.abs() > 0.02).float()
            t_stop = torch.where(moving > 0, torch.full_like(t_stop, float(step) * 0.01), t_stop)
            v_end = vx
        cleared_110 = float((x_max >= 1.10).float().mean())
        cleared_145 = float((x_max >= 1.45).float().mean())
        finite = min_clear[min_clear < 999.0]
        print("[coast] %7.2f %9.3f %9.3f %9.3f %8.2f %10.2f %12.2f %10s %11.1f %11.1f"
              % (v0, x0, float(loc[:, 0].mean()), float(x_max.mean()), float(t_stop.max()),
                 cleared_110, cleared_145,
                 ("n/a" if finite.numel() == 0 else "%.4f" % float(finite.min())),
                 roof_peak, sum(wheel_f_coast) / max(1, len(wheel_f_coast))), flush=True)
        if reset_at >= 0:
            print("[coast]   WARNING: termination at step %d -- this entry speed is not a clean "
                  "coast measurement" % reset_at, flush=True)
    print("[coast] rule: cleared>1.10 at 0.60 m/s with wheelF>0 means the machine can cross under "
          "power; cleared 0.00 everywhere means the crouch region cannot be traversed at all.",
          flush=True)
    env.close()


if __name__ == "__main__":
    main()
