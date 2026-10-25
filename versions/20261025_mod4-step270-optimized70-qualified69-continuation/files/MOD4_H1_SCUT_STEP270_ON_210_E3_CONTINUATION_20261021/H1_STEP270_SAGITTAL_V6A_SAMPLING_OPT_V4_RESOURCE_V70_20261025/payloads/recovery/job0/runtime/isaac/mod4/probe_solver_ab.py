"""P3 A/B: PhysX solver iterations vs closed-chain quality and throughput.

Runs the delivered arena with the fixed plant under RANDOM torque-level actions (the audit asks
for the comparison under load, not while standing still) and reports the worst closure/mimic
error plus the achieved env-steps/s, so 32/8 vs 16/4 can be decided on numbers.

    $env:RM_SOLVER_POS='32'; $env:RM_SOLVER_VEL='8'
    .venv-isaaclab\\Scripts\\python.exe isaac/mod4/probe_solver_ab.py --headless --num_envs 64 --steps 300
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser()
parser.add_argument("--num_envs", type=int, default=64)
parser.add_argument("--steps", type=int, default=300)
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
    dev = env.device
    act = torch.zeros((env.num_envs, 6), device=dev)
    worst_c = worst_m = 0.0
    t0 = time.perf_counter()
    for step in range(args.steps):
        if step % 20 == 0:
            act = torch.rand_like(act) * 2.0 - 1.0
        env.step(act)
        if step % 10 == 0:
            ce = mod4_task.closure_errors(env)
            me = mod4_task.mimic_errors(env)
            worst_c = max(worst_c, float(torch.stack(list(ce.values())).max()))
            worst_m = max(worst_m, float(torch.stack(list(me.values())).max()))
    dt = time.perf_counter() - t0
    print("[solver] pos=%s vel=%s envs=%d steps=%d  closure_max=%.5f m  mimic_max=%.5f rad  "
          "%.0f env-steps/s"
          % (mod4_task.os.environ.get("RM_SOLVER_POS", "32"),
             mod4_task.os.environ.get("RM_SOLVER_VEL", "8"), env.num_envs, args.steps,
             worst_c, worst_m, env.num_envs * args.steps / max(1e-6, dt)), flush=True)
    env.close()


if __name__ == "__main__":
    main()
    app.close()
