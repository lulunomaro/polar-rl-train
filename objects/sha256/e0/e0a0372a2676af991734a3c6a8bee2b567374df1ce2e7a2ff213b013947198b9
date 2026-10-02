"""Drive the loaded policy through the REAL rsl_rl training loop for a few iterations.

If this reports ~1900-step episodes while scripts/diag_policy_env_mismatch.py reports ~100
with the same env object and checkpoint, the difference is in how the action is produced
(alg.act vs a direct actor call), not in the plant.

Usage:
    PYTHONPATH=train/rmvehicle/src:third_party/rc_mjlab/mjlab/src \
    third_party/rc_mjlab/.venv/bin/python scripts/diag_train_loop.py \
        --checkpoint <model_499.pt> --num-envs 128 --iters 3
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "train" / "rmvehicle" / "src"))

import rmvehicle  # noqa: E402,F401
from mjlab.envs import ManagerBasedRlEnv  # noqa: E402
from mjlab.rl import MjlabOnPolicyRunner, RslRlVecEnvWrapper  # noqa: E402
from mjlab.tasks.registry import load_env_cfg, load_rl_cfg, load_runner_cls  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", default="RM2025-Later-CC-Flat-v0")
    ap.add_argument("--checkpoint", required=True)
    ap.add_argument("--num-envs", type=int, default=128)
    ap.add_argument("--iters", type=int, default=3)
    ap.add_argument("--device", default="cuda:0")
    args = ap.parse_args()

    cfg = load_env_cfg(args.task, play=False)
    cfg.scene.num_envs = args.num_envs
    cfg.seed = 0
    agent_cfg = load_rl_cfg(args.task)
    agent_cfg.seed = 0
    env = ManagerBasedRlEnv(cfg=cfg, device=args.device)
    env = RslRlVecEnvWrapper(env, clip_actions=agent_cfg.clip_actions)
    runner_cls = load_runner_cls(args.task) or MjlabOnPolicyRunner
    runner = runner_cls(env, asdict(agent_cfg), device=args.device)
    runner.load(args.checkpoint, load_cfg={"actor": True}, strict=True, map_location=args.device)
    runner.learn(num_learning_iterations=args.iters, init_at_random_ep_len=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
