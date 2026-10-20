"""Unit check (goal §1): one route success must pay ~+20, not +0.2.

The reward manager multiplies every term by the control dt (0.01 s).  `route_success` used to
return the raw 0/1 flag, so a finished route paid 20 * 0.01 = 0.2 while simply surviving a 30 s
episode accumulated ~30.  This probe forces one success and reads the term's actual per-step
value back out of the reward manager.

    .venv-isaaclab\\Scripts\\python.exe isaac/mod4/probe_success_reward.py --headless --num_envs 4
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser()
parser.add_argument("--num_envs", type=int, default=4)
parser.add_argument("--expect", type=float, default=15.0)
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
    rm = env.reward_manager
    terms = list(rm.active_terms)
    idx = terms.index("route_success")
    print("[succ] reward terms: %s" % terms, flush=True)
    print("[succ] route_success weight = %.3f" % float(rm.get_term_cfg("route_success").weight),
          flush=True)
    success = torch.zeros(env.num_envs, dtype=torch.bool, device=env.device)
    zero = torch.zeros_like(success, dtype=torch.float)
    # baseline: nobody succeeds
    env._mod4_route_progress = {"success": success, "progress_reward": zero}
    total0 = float(rm.compute(float(env.step_dt)).sum())
    stored0 = float(rm._step_reward[0, idx])
    # one env succeeds
    success = success.clone()
    success[0] = True
    env._mod4_route_progress = {"success": success, "progress_reward": zero}
    total1 = float(rm.compute(float(env.step_dt)).sum())
    stored1 = float(rm._step_reward[0, idx])
    got = total1 - total0
    print("[succ] stored term value: %.1f -> %.1f (weight x func, before dt)" % (stored0, stored1),
          flush=True)
    print("[succ] ACTUAL total-reward delta for one success = %+.4f" % got, flush=True)
    ok = got >= args.expect
    print("[succ] %s (expected >= %.1f; the pre-fix value was 0.2)"
          % ("PASS" if ok else "FAIL", args.expect), flush=True)
    env.close()
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
    app.close()
