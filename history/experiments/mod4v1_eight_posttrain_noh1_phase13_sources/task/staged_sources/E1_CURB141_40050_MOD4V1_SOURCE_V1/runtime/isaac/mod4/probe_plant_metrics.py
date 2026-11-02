"""Smoke test for the online plant-health metrics (audit P0-5).

Builds the delivered arena, steps it, and prints whatever `log_plant_metrics` published into
`env.extras["log"]` -- the closure-anchor separation and the transmission-mimic drift that
TensorBoard is supposed to show before they cross the termination thresholds.

    RM_MOD4_MAP=rmuc2026 RM_MOD4_TERRAIN=field RM_DR_OFF=1 OMNI_KIT_ACCEPT_EULA=YES \
      python isaac/mod4/probe_plant_metrics.py --headless --num_envs 8 --steps 40
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser()
parser.add_argument("--num_envs", type=int, default=8)
parser.add_argument("--steps", type=int, default=40)
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
    act = torch.zeros((env.num_envs, 6), device=env.device)
    for _ in range(args.steps):
        env.step(act)
    log = env.extras.get("log", {})
    want = [k for k in log if k.startswith("Metrics/plant/")]
    for k in sorted(want):
        print("[plant-metrics] %-46s %.6f" % (k, float(log[k])), flush=True)
    ok = {"Metrics/plant/closure_err_max_m", "Metrics/plant/mimic_err_max_rad"} <= set(want)
    print("[plant-metrics] verdict: %s" % ("PUBLISHING" if ok else "MISSING"), flush=True)
    env.close()


if __name__ == "__main__":
    main()
    app.close()
