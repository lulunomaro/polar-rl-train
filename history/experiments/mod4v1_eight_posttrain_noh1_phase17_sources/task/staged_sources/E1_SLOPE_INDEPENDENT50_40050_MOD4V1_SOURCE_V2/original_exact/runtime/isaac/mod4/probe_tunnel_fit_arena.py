"""Does the delivery COLLISION envelope fit the delivered dog hole? (audit: "结合碰撞外形验证")

The delivered package measures the dog hole itself: `data/../reports/tunnel_clearance.json`
gives floor -0.1558 m, ceiling +0.0914 m -> **0.2472 m of clear height** over x = 0.76..1.09 m
at y = +-5.95 m.  What was never checked is whether the robot's collision geometry fits under
that ceiling at the crouch the height command asks for.

This probe teleports the robot into the roofed corridor at several root heights ABOVE THE LOCAL
FLOOR, holds zero action, and reports for each height:

  * whether the chassis contact sensor sees the roof (a fit failure),
  * how far the root is pushed (PhysX resolving an overlap) and the tilt,
  * the local floor the new root-ray reports (regression guard for the 2026-09-11 ray fix).

    RM_MOD4_MAP=rmuc2026 RM_MOD4_TERRAIN=field RM_DR_OFF=1 RM_ROUTE_KINDS=tunnel_cross \
      OMNI_KIT_ACCEPT_EULA=YES python isaac/mod4/probe_tunnel_fit_arena.py --headless --num_envs 6
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser()
parser.add_argument("--num_envs", type=int, default=6)
parser.add_argument("--steps", type=int, default=40)
parser.add_argument("--x", type=float, default=0.92, help="arena x of the roofed corridor")
parser.add_argument("--y", type=float, default=-5.95, help="arena y of the tunnel centre line")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
launcher = AppLauncher(args)
app = launcher.app

import torch  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import mod4_task  # noqa: E402
from mod4_env import Mod4Env  # noqa: E402


def clearance() -> dict:
    p = Path(mod4_task.RMUC2026_ISAAC).parent / "reports" / "tunnel_clearance.json"
    probes = json.loads(p.read_text(encoding="utf8"))["probes"]
    return {"floor": probes[0]["floor_z"], "ceiling": probes[0]["ceiling_z"],
            "clearance": max(q["clearance_m"] for q in probes)}


def main() -> None:
    geo = clearance()
    cfg = mod4_task.Mod4EnvCfg()
    cfg.scene.num_envs = args.num_envs
    mod4_task.attach_rmuc2026_terrain(cfg)
    env = Mod4Env(cfg=cfg)
    env.reset()
    robot = env.scene["robot"]
    n = env.num_envs
    ids = torch.arange(n, device=env.device)
    chassis = env.scene.sensors["chassis_contact"]
    print("[tunnel-fit] delivered clearance %.4f m (floor %.4f, ceiling %.4f)"
          % (geo["clearance"], geo["floor"], geo["ceiling"]), flush=True)
    print("[tunnel-fit] %8s %10s %10s %10s %12s %8s"
          % ("root_cmd", "root_end", "pushed", "tilt_deg", "roof_force_N", "floor_ray"), flush=True)
    # Fine sweep around the measured boundary: 0.20 m fits, 0.24 m penetrates the roof hard.
    for h in (0.18, 0.19, 0.20, 0.21, 0.22, 0.23):
        pos = env.scene.env_origins[ids].clone()
        pos[:, 0] += args.x
        pos[:, 1] += args.y
        pos[:, 2] = geo["floor"] + h
        quat = torch.zeros((n, 4), device=env.device)
        quat[:, 3] = 1.0
        hold = torch.cat([pos, quat], dim=-1)
        robot.write_root_pose_to_sim(torch.cat([pos, quat], dim=-1), env_ids=ids)
        robot.write_root_velocity_to_sim(torch.zeros((n, 6), device=env.device), env_ids=ids)
        # A free-standing robot falls over in 0.4 s with zero action (measured tilt 30-37 deg),
        # which measures toppling, not fit.  Clamp the base to the test pose every step so the
        # question asked here is exactly "does this ENVELOPE fit under this CEILING".
        act = torch.zeros((n, 6), device=env.device)
        roof = 0.0
        for _ in range(args.steps):
            env.step(act)
            robot.write_root_pose_to_sim(hold, env_ids=ids)
            robot.write_root_velocity_to_sim(torch.zeros((n, 6), device=env.device), env_ids=ids)
            f = chassis.data.net_forces_w
            if hasattr(f, "torch"):
                f = f.torch
            roof = max(roof, float(f.norm(dim=-1).max()))
        g = robot.data.projected_gravity_b
        tilt = float(torch.rad2deg(torch.acos((-g[:, 2]).clamp(-1.0, 1.0))).mean())
        z = float(robot.data.root_pos_w[:, 2].mean()) - geo["floor"]
        ray = float(getattr(env, "_mod4_ground_z", torch.zeros(1)).mean())
        head = float(robot.data.body_pos_w[:, 0, 2].mean())     # chassis link origin
        print("[tunnel-fit] %8.3f %10.3f %10.3f %10.1f %12.1f %8.4f  chassis_z=%.3f"
              % (h, z, z - h, tilt, roof, ray, head), flush=True)
    print("[tunnel-fit] rule: roof_force_N ~0 AND tilt < 10 deg AND root_end >= 0.20 m means the "
          "crouch fits; a large push with roof force means the collision envelope is taller than "
          "the opening.", flush=True)
    env.close()


if __name__ == "__main__":
    main()
    app.close()
