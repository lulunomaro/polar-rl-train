"""What does ONE SharedTerrainRaycast.cast() cost per control step? (perf, audit P3)

The arena task refreshes the per-env local ground height with one downward Warp ray per
control step (mod4_task.update_ground_height -> ground_height -> SharedTerrainRaycast).
Iteration time on the 4090 is ~5.1 s for 1024 envs x 24 control steps = 0.21 s per control
step, which is suspiciously close to a FIXED per-call cost: a 16-env probe measured 0.39 s
per control step, i.e. 16 environments were no cheaper than 1024.  This probe times the bare
raycast call (no physics, no policy) so the fixed cost can be attributed or cleared.

    python isaac/mod4/probe_raycast_cost.py --headless --num_envs 1024 --calls 20
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser()
parser.add_argument("--num_envs", type=int, default=1024)
parser.add_argument("--rays", type=int, default=1)
parser.add_argument("--calls", type=int, default=20)
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
launcher = AppLauncher(args)
app = launcher.app

import torch  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import mod4_task  # noqa: E402

sys.path.insert(0, str(mod4_task.RMUC2026_ISAAC))
from shared_raycast import SharedTerrainRaycast  # noqa: E402


def main() -> None:
    dev = "cuda:0"
    origins = torch.zeros(args.num_envs, 3, device=dev)
    q = SharedTerrainRaycast(origins)
    starts = torch.zeros(args.num_envs, args.rays, 3, device=dev)
    starts[:, :, 2] = 1.0
    dirs = torch.zeros_like(starts)
    dirs[:, :, 2] = -1.0
    for _ in range(3):                      # warm up the warp kernel / BVH
        q.cast(starts, dirs, max_distance=3.0)
    torch.cuda.synchronize()
    t0 = time.time()
    for _ in range(args.calls):
        out = q.cast(starts, dirs, max_distance=3.0)
    torch.cuda.synchronize()
    dt = (time.time() - t0) / args.calls
    hit = out["hit"].float().mean()
    print("[raycast] envs=%d rays=%d  %.4f s/call  (hit %.2f)"
          % (args.num_envs, args.rays, dt, float(hit)), flush=True)
    # a second, larger sweep makes the env-count scaling explicit
    for n in (1, 16, 256, 1024):
        if n > args.num_envs:
            continue
        o = torch.zeros(n, 3, device=dev)
        qn = SharedTerrainRaycast(o)
        s = torch.zeros(n, args.rays, 3, device=dev)
        s[:, :, 2] = 1.0
        d = torch.zeros_like(s)
        d[:, :, 2] = -1.0
        qn.cast(s, d, max_distance=3.0)
        torch.cuda.synchronize()
        t = time.time()
        for _ in range(args.calls):
            qn.cast(s, d, max_distance=3.0)
        torch.cuda.synchronize()
        print("[raycast] n=%-5d %.4f s/call" % (n, (time.time() - t) / args.calls), flush=True)
    app.close()


if __name__ == "__main__":
    main()
