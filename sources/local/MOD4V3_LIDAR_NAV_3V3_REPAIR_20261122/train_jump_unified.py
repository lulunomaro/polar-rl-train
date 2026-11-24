"""COMMANDER-AUTHORED & LOCKED Entry Script for Priority #2: E_jump_unified (DO NOT MODIFY!)."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "jump_support"))
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"

import torch
import warp as wp
from train_generalized_ppo import put, run_ppo


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("job", type=Path)
    parser.add_argument("--seconds", type=int, default=0)
    parser.add_argument("--probe", type=Path, default=None)
    parser.add_argument("--lr", type=float, default=5.0e-5)
    args = parser.parse_args()

    torch.set_num_threads(1)
    torch.manual_seed(20261122)
    wp.config.kernel_cache_dir = str(ROOT / "cache/warp")

    from jump_unified_gpu import UnifiedJumpGpu
    from unified_policies import AsymmetricValue, UnifiedJumpActor

    r10_path = ROOT / "weights/jump_r10_donor.pt"
    actor = UnifiedJumpActor(r10_path)
    model = None
    closed = False
    err_txt = None
    try:
        timing = dict(
            speeds=[0.0, 3.0],
            heights=[0.24, 0.42],
            platform_380=[[0.5, 0.5], [1.4, 1.4]],
            platform_360=[[0.5, 0.5], [1.4, 1.4]],
            hurdle_380=[[0.5, 0.5], [1.4, 1.4]],
        )
        model = UnifiedJumpGpu(2048, 20261122, timing)
        critic = AsymmetricValue(455 + model.extra().shape[1])
        run_ppo(
            model,
            actor,
            critic,
            args.job,
            seconds=args.seconds,
            kind="jump",
            probe_dir=args.probe,
            donor_meta={"donor": "jump380_r10_model_009m"},
            lr_actor=args.lr,
            lr_critic=2.5e-4,
            rollout_len=32,
        )
        closed = True
    except BaseException:
        err_txt = traceback.format_exc()
        args.job.mkdir(parents=True, exist_ok=True)
        (args.job / "ERROR.txt").write_text(err_txt, encoding="utf-8")
        raise
    finally:
        torch.cuda.synchronize()
        del model
        torch.cuda.empty_cache()
        args.job.mkdir(parents=True, exist_ok=True)
        put(
            args.job / "SAFE_CLOSED.json",
            dict(scene_closed=closed, cuda_synchronized=True, epoch=time.time(), worker_finished=True, error=err_txt),
        )


if __name__ == "__main__":
    main()
