"""Dump the resolved env config as YAML so it can be diffed against a training run's
params/env.yaml (which is what the training process actually used)."""
from __future__ import annotations

import argparse
import sys
from dataclasses import asdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "train" / "rmvehicle" / "src"))

import rmvehicle  # noqa: E402,F401
from mjlab.tasks.registry import load_env_cfg  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", default="RM2025-Later-CC-Flat-v0")
    ap.add_argument("--out", required=True)
    ap.add_argument("--num-envs", type=int, default=None)
    args = ap.parse_args()
    cfg = load_env_cfg(args.task, play=False)
    if args.num_envs is not None:
        cfg.scene.num_envs = args.num_envs
    with open(args.out, "w", encoding="utf8") as fh:
        # The training script writes params/env.yaml with the default (unsafe) dumper so
        # enum-valued fields survive; safe_dump cannot represent them.
        yaml.dump(asdict(cfg), fh, sort_keys=True, default_flow_style=False)
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
