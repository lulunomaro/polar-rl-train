"""Why do the terrain routes die in ~1.5 control steps? (measured 2026-09-11 21:45)

The terrain stage (ramp_up/ramp_down/step_up/step_down/rough_cross) terminated 25% of episodes
with `closure` and 26% with `base_contact` almost immediately.  Both point at the SPAWN pose, not
at learning, so this probe spawns the robot on each route, holds zero action and prints a short
timeline: root height above the local floor (from the root ray), the closed-chain error the
termination guard watches, the chassis contact force, and the tilt.

    RM_MOD4_MAP=rmuc2026 RM_MOD4_TERRAIN=field RM_DR_OFF=1 \
      RM_ROUTE_KINDS=ramp_up,ramp_down,step_up,step_down,rough_cross \
      OMNI_KIT_ACCEPT_EULA=YES python isaac/mod4/probe_terrain_spawn.py --headless --num_envs 12
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser()
parser.add_argument("--num_envs", type=int, default=12)
parser.add_argument("--steps", type=int, default=25)
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
    ids = getattr(env, "_mod4_route_ids", None)
    kinds = getattr(env, "_mod4_route_kinds", None)
    names = [kinds[int(i)] for i in ids] if (kinds is not None and ids is not None) else ["?"] * env.num_envs
    chassis = env.scene.sensors["chassis_contact"]
    act = torch.zeros((env.num_envs, 6), device=env.device)
    print("[terrain-spawn] routes in play: %s" % sorted(set(names)), flush=True)
    print("[terrain-spawn] env   kind                root_h  ground   closure_mm  chassis_N  tilt",
          flush=True)
    for i in range(args.steps):
        env.step(act)
        if i not in (0, 1, 2, 4, 9, 24):
            continue
        z = robot.data.root_pos_w[:, 2]
        g = getattr(env, "_mod4_ground_z", torch.zeros_like(z))
        clo = getattr(env, "_mod4_closure_now", None)
        f = chassis.data.net_forces_w
        if hasattr(f, "torch"):
            f = f.torch
        fn = f.norm(dim=-1).max(dim=1).values
        grav = robot.data.projected_gravity_b
        tilt = torch.rad2deg(torch.acos((-grav[:, 2]).clamp(-1.0, 1.0)))
        for e in range(env.num_envs):
            print("[terrain-spawn] %3d %-18s %6.3f %7.3f %10.2f %10.1f %6.1f"
                  % (e, names[e], float(z[e] - g[e]), float(g[e]),
                     float(clo[e]) * 1000.0 if clo is not None else float("nan"),
                     float(fn[e]), float(tilt[e])), flush=True)
        print("[terrain-spawn] --- step %d ---" % (i + 1), flush=True)
    env.close()


if __name__ == "__main__":
    main()
    app.close()
