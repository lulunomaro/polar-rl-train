"""Can the robot COAST through the dog hole after it squats?  (2026-09-12, tunnel blocker)

Evidence that motivated this probe (docs/MOD4_FIXED_PLANT_INTEGRATION_20260912.md section 47):
the tunnel phase trains for 800 iterations with 34 % tunnel sampling and a 1.60 m curriculum
goal, yet `Metrics/tunnel_underpass_rate` and `Episode_Reward/tunnel_clearance` stay exactly
0.0000, the evaluation bucket ends 18/18 in `time_out` with zero roof/base contacts, and the
mean advance is ~0.35 m -- i.e. the robot squats in the pre-crouch zone and stops BEFORE the
mouth.  The design intent in skills_isaac.py ("drive in at speed, squat late, coast through on
the guide rollers") therefore needs a physics answer, not more PPO:

    is a coast-through physically possible at all, and at what entry speed?

This probe teleports the robot to a point before the mouth with a given forward velocity, puts
the legs in the crouch pose family, commands ZERO wheel rate and lets physics decide.  It
reports, per entry speed, how far the robot coasts, whether it clears the roofed span
(x >= 1.10 m) and the exit (x >= 1.45 m), the minimum CAD clearance while under the roof, the
peak roof force, and the mean wheel-contact force during the first 50 steps (traction).

    RM_MOD4_MAP=rmuc2026 RM_MOD4_TERRAIN=field RM_DR_OFF=1 RM_ROUTE_KINDS=tunnel_cross \
      OMNI_KIT_ACCEPT_EULA=YES python isaac/mod4/probe_tunnel_inertia.py --headless \
      --num_envs 4 --steps 400 --speeds 0.15,0.25,0.40,0.60

Read the result as: if nothing clears 1.10 m even at 0.60 m/s, the crossing cannot be solved by
policy/reward shaping alone -- the pre-crouch lead, the roller friction or the crouch height has
to change (see section 47 options 1-4).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser()
parser.add_argument("--num_envs", type=int, default=4)
parser.add_argument("--steps", type=int, default=400)
parser.add_argument("--x0", type=float, default=0.60, help="arena x where the coast starts")
parser.add_argument("--y", type=float, default=-5.95, help="arena y of the tunnel centre line")
parser.add_argument("--h", type=float, default=0.18, help="root height above the local floor")
parser.add_argument("--speeds", default="0.15,0.25,0.40,0.60")
parser.add_argument("--pose", default="root018", choices=("root018", "hardstop"))
parser.add_argument("--wheel-cmd", type=float, default=0.0, help="wheel action (0 = free roll)")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
launcher = AppLauncher(args)
app = launcher.app

import torch  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import mod4_task  # noqa: E402
from mod4_env import Mod4Env  # noqa: E402

# CAD-skin geometry of the delivered hole (same constants the reward uses).
CAD_TOP_ABOVE_ROOT_M = 0.066934
ROOF_X = (0.760, 1.100)
LANE_Y = (5.42, 6.355)
POSE_CASES = {"root018": (0.35, -1.06), "hardstop": (0.4503, -1.0843)}


def hole_geometry() -> dict:
    p = Path(mod4_task.RMUC2026_ISAAC).parent / "reports" / "tunnel_clearance.json"
    probes = json.loads(p.read_text(encoding="utf8"))["probes"]
    return {"floor": probes[0]["floor_z"], "ceiling": probes[0]["ceiling_z"]}


def main() -> None:
    geo = hole_geometry()
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

    print("[inertia] pose=%s hip=%.4f diff=%.4f floor=%.4f ceiling=%.4f x0=%.2f h=%.2f"
          % (args.pose, hip, diff, geo["floor"], geo["ceiling"], args.x0, args.h), flush=True)
    print("[inertia] %7s %9s %9s %9s %8s %10s %12s %10s %10s"
          % ("v0", "x_final", "x_max", "v_end", "t_stop", "cleared>1.10", "cleared>1.45",
             "min_clr_m", "roofF_N"), flush=True)

    for v0 in speeds:
        env.reset()
        pos = env.scene.env_origins[ids].clone()
        pos[:, 0] += args.x0
        pos[:, 1] += args.y
        pos[:, 2] = geo["floor"] + args.h
        quat = torch.zeros((n, 4), device=env.device)
        quat[:, 3] = 1.0
        robot.write_root_pose_to_sim(torch.cat([pos, quat], dim=-1), env_ids=ids)
        vel = torch.zeros((n, 6), device=env.device)
        vel[:, 0] = v0
        robot.write_root_velocity_to_sim(vel, env_ids=ids)

        x_max = torch.full((n,), args.x0, device=env.device)
        v_end = torch.zeros(n, device=env.device)
        t_stop = torch.zeros(n, device=env.device)
        min_clear = torch.full((n,), 999.0, device=env.device)
        roof_peak = 0.0
        wheel_f_early = []
        reset_at = -1
        ended = -1
        for step in range(args.steps):
            out = env.step(act)
            # A termination fires -> the env auto-resets and the teleport is lost; report it
            # instead of measuring the motion of a freshly spawned robot.
            if isinstance(out, tuple) and len(out) >= 3 and hasattr(out[2], "any"):
                if bool(out[2].any()):
                    ended = step
            loc = robot.data.root_pos_w - env.scene.env_origins
            if reset_at < 0 and float(loc[:, 0].mean()) < args.x0 - 0.15 and step > 5:
                reset_at = step
            x, y, z = loc[:, 0], loc[:, 1], loc[:, 2]
            vx = robot.data.root_lin_vel_b[:, 0]
            x_max = torch.maximum(x_max, x)
            inside = ((x.abs() >= ROOF_X[0]) & (x.abs() <= ROOF_X[1]) &
                      (y.abs() >= LANE_Y[0]) & (y.abs() <= LANE_Y[1]))
            clr = geo["ceiling"] - (z + CAD_TOP_ABOVE_ROOT_M)
            min_clear = torch.where(inside, torch.minimum(min_clear, clr), min_clear)
            f = chassis.data.net_forces_w
            if hasattr(f, "torch"):
                f = f.torch
            roof_peak = max(roof_peak, float(f.norm(dim=-1).max()))
            if step < 50:
                wf = wheel_sensor.data.net_forces_w
                if hasattr(wf, "torch"):
                    wf = wf.torch
                wheel_f_early.append(float(wf.norm(dim=-1).max(dim=1).values.mean()))
            moving = (vx.abs() > 0.02).float()
            t_stop = torch.where(moving > 0, torch.full_like(t_stop, float(step) * 0.01), t_stop)
            v_end = vx
        cleared_110 = float((x_max >= 1.10).float().mean())
        cleared_145 = float((x_max >= 1.45).float().mean())
        finite = min_clear[min_clear < 999.0]
        print("[inertia] %7.2f %9.3f %9.3f %9.3f %8.2f %10.2f %12.2f %10s %10.1f"
              % (v0, float(x.mean()), float(x_max.mean()), float(v_end.mean()),
                 float(t_stop.max()), cleared_110, cleared_145,
                 ("n/a" if finite.numel() == 0 else "%.4f" % float(finite.min())), roof_peak),
              flush=True)
        print("[inertia]         wheelF(first50 mean)=%.1f N  x_final_mean=%.3f"
              % (sum(wheel_f_early) / max(1, len(wheel_f_early)), float(x.mean())), flush=True)
        if ended >= 0 or reset_at >= 0:
            print("[inertia]         WARNING: termination at step %d (x-reset detected at %d) -- "
                  "this entry speed is not a clean coast measurement" % (ended, reset_at), flush=True)
    print("[inertia] rule: cleared>1.10 m means the roofed span was passed; if it is 0.00 at every "
          "entry speed the crossing is not reachable by coasting (see section 47).", flush=True)
    env.close()


if __name__ == "__main__":
    main()
    app.close()
