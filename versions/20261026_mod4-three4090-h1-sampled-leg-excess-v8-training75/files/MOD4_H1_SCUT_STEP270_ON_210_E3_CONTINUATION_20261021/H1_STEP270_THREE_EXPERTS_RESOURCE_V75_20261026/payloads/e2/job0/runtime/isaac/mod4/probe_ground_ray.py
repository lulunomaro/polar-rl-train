"""Does the local-floor ray still see the FLOOR when the robot is inside the dog hole?

audit 2026-09-11 20:10: the ray used to start 1.0 m above the root, so inside the ~0.25 m tall
dog hole it hit the ROOF and reported it as the ground -- the robot's height above "ground"
went negative and the height reward / low_base / base_contact all ran on garbage.

This probe drives the same arena route the tunnel stage will use and prints, per control step:
the root height, `env._mod4_ground_z` (the ray result) and the true floor height of the route
(from the delivered routes.json `spawn_ground_m[2]`, i.e. -0.1558 m for the dog hole).

    RM_MOD4_MAP=rmuc2026 RM_MOD4_TERRAIN=field RM_DR_OFF=1 RM_ROUTE_KINDS=tunnel_cross \
      OMNI_KIT_ACCEPT_EULA=YES python isaac/mod4/probe_ground_ray.py \
      --headless --num_envs 8 --steps 120
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
import sys

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser()
parser.add_argument("--num_envs", type=int, default=8)
parser.add_argument("--steps", type=int, default=120)
parser.add_argument("--roof_x", type=float, default=0.90,
                    help="teleport the robot under the dog-hole ROOF after half the steps")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
launcher = AppLauncher(args)
app = launcher.app

import torch  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import mod4_task  # noqa: E402
from mod4_env import Mod4Env  # noqa: E402


def route_floor_z() -> float:
    routes = json.loads((Path(mod4_task.RMUC2026_ISAAC).parent / "data" /
                         "routes.json").read_text(encoding="utf8"))
    kinds = [r["kind"] for r in routes]
    want = [k.strip() for k in __import__("os").environ.get("RM_ROUTE_KINDS", "").split(",")
            if k.strip()]
    zs = [r["spawn_ground_m"][2] for r in routes if not want or r["kind"] in want]
    return statistics.fmean(zs) if zs else 0.0


def main() -> None:
    cfg = mod4_task.Mod4EnvCfg()
    cfg.scene.num_envs = args.num_envs
    arena = mod4_task.attach_rmuc2026_terrain(cfg)
    env = Mod4Env(cfg=cfg)
    env.reset()
    robot = env.scene["robot"]
    act = torch.zeros((env.num_envs, 6), device=env.device)
    truth = route_floor_z()
    print("[ground-ray] arena=%s route_floor_z=%.4f" % (arena, truth), flush=True)
    rows = []
    for i in range(args.steps):
        if i == args.steps // 2:
            # The dog-hole roof only spans x = 0.751..1.101 m of the arena; the spawn sits on
            # the approach.  Teleport into the roofed corridor so the ray has a ceiling above it
            # -- that is the case the old 1 m-high start got wrong.
            pose = robot.data.root_pose_w.clone()
            pose[:, 0] = env.scene.env_origins[:, 0] + args.roof_x
            pose[:, 1] = env.scene.env_origins[:, 1] - 5.95
            pose[:, 2] = truth + 0.22
            robot.write_root_pose_to_sim(pose)
            robot.write_root_velocity_to_sim(torch.zeros((env.num_envs, 6), device=env.device))
            for _ in range(3):
                env.step(act)
            g = float(getattr(env, "_mod4_ground_z", torch.zeros(1)).mean())
            print("[ground-ray] under the roof: ray_ground=%.4f (true floor %.4f) -> %s"
                  % (g, truth, "OK" if abs(g - truth) < 0.05 else "HIT THE ROOF"), flush=True)
            q_old = getattr(env, "_mod4_ground_raycast", None)
            if q_old is not None:                      # A/B against the retired implementation
                pos = robot.data.root_pos_w
                s = torch.stack([pos[:, 0], pos[:, 1], pos[:, 2] + 1.0], dim=-1).unsqueeze(1)
                d = torch.zeros_like(s)
                d[:, :, 2] = -1.0
                out = q_old.cast(s, d, max_distance=3.0)
                old_z = (pos[:, 2] + 1.0) - out["distance"].squeeze(1)
                print("[ground-ray] the OLD 1 m-high ray reports %.4f under the same roof "
                      "(true floor %.4f)" % (float(old_z.mean()), truth), flush=True)
                # full detail: where exactly does each ray land, and what does its normal say?
                wheels = robot.data.body_pos_w[:, env._mod4_wheel_body_ids, :]
                print("[ground-ray] root_z=%.4f wheel_z=%s"
                      % (float(pos[:, 2].mean()),
                         [round(float(v), 4) for v in wheels[:, :, 2].mean(dim=0)]), flush=True)
                ws = wheels.clone()
                ws[:, :, 2] = ws[:, :, 2] + 0.05
                wd = torch.zeros_like(ws)
                wd[:, :, 2] = -1.0
                ow = q_old.cast(ws, wd, max_distance=3.0)
                zz = ws[:, :, 2] - ow["distance"]
                print("[ground-ray] wheel ray hit z=%s normal_z=%s hit=%s"
                      % ([round(float(v), 4) for v in zz[0]],
                         [round(float(v), 3) for v in ow["normal_w"][0, :, 2]],
                         [bool(v) for v in ow["hit"][0]]), flush=True)
                zz_old = s[:, :, 2] - out["distance"]
                print("[ground-ray] old ray hit z=%s normal_z=%s"
                      % ([round(float(v), 4) for v in zz_old[0]],
                         [round(float(v), 3) for v in out["normal_w"][0, :, 2]]), flush=True)
        env.step(act)
        z = float(robot.data.root_pos_w[:, 2].mean())
        g = float(getattr(env, "_mod4_ground_z", torch.zeros(1)).mean())
        rows.append((i, z, g, z - g))
    print("[ground-ray] %6s %10s %12s %12s" % ("step", "root_z", "ray_ground", "height"), flush=True)
    for i, z, g, h in rows[:: max(1, args.steps // 12)]:
        print("[ground-ray] %6d %10.4f %12.4f %12.4f" % (i, z, g, h), flush=True)
    err = [abs(g - truth) for _i, _z, g, _h in rows]
    neg = sum(1 for _i, _z, _g, h in rows if h < 0.0)
    print("[ground-ray] |ray - true floor| mean=%.4f max=%.4f m ; negative-height steps=%d/%d"
          % (statistics.fmean(err), max(err), neg, len(rows)), flush=True)
    print("[ground-ray] verdict: %s"
          % ("FLOOR IS TRACKED" if statistics.fmean(err) < 0.05 and neg == 0
             else "RAY IS STILL WRONG"), flush=True)
    env.close()


if __name__ == "__main__":
    main()
    app.close()
