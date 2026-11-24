"""COMMANDER-AUTHORED 4,096-World `mujoco_warp` PPO Entry Script for Perception-Guided `E_jump` (`380 mm` + Bridge Hurdle)."""
from __future__ import annotations

import argparse
import json
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
    parser.add_argument("--envs", type=int, default=4096)
    parser.add_argument("--lr", type=float, default=6.5e-5)
    parser.add_argument("--init-ckpt", type=Path, default=ROOT / "weights/E_jump_unified_candidate.pt")
    args = parser.parse_args()

    torch.set_num_threads(1)
    torch.manual_seed(20261124)
    wp.config.kernel_cache_dir = str(ROOT / "cache/warp")

    from jump_warp_gpu import JumpWarpGpu
    from jump_warp_model import JumpWarpPerceptionActor
    from manual_fsm_model import SymmetricE0
    from unified_policies import AsymmetricValue

    e0 = (
        SymmetricE0()
        .load_e0(
            torch.load(ROOT / "weights/e0.pt", map_location="cuda:0", weights_only=False),
            torch.load(ROOT / "weights/e0_base.pt", map_location="cuda:0", weights_only=False),
        )
        .to("cuda:0")
        .eval()
    )
    if (ROOT / "E0_CALIBRATION.json").is_file():
        e0.load_calibration(json.loads((ROOT / "E0_CALIBRATION.json").read_text(encoding="utf-8")))

    r10_path = ROOT / "weights/jump_r10_donor.pt"
    actor = JumpWarpPerceptionActor(r10_path, args.init_ckpt)
    actor.verify_zero_e0_drift()

    env = None
    closed = False
    err_txt = None
    try:
        env = JumpWarpGpu(args.envs, 20261124, e0, ROOT / "cache/jump_warp_v3")
        critic = AsymmetricValue(459 + env.extra().shape[1])
        run_ppo(
            env,
            actor,
            critic,
            args.job,
            seconds=args.seconds,
            kind="jump",
            probe_dir=args.probe,
            donor_meta={
                "donor": "jump380_r10_model_009m",
                "base_init": str(args.init_ckpt.name) if args.init_ckpt else None,
                "engine": "mujoco_warp_4096_perception_jump",
                "actor_inputs": 459,
            },
            lr_actor=args.lr,
            lr_critic=3.0e-4,
            rollout_len=28,
        )
        closed = True
    except BaseException:
        err_txt = traceback.format_exc()
        args.job.mkdir(parents=True, exist_ok=True)
        (args.job / "ERROR.txt").write_text(err_txt, encoding="utf-8")
        raise
    finally:
        torch.cuda.synchronize()
        del env
        torch.cuda.empty_cache()
        args.job.mkdir(parents=True, exist_ok=True)
        put(
            args.job / "SAFE_CLOSED.json",
            dict(scene_closed=closed, cuda_synchronized=True, epoch=time.time(), worker_finished=True, error=err_txt),
        )


if __name__ == "__main__":
    main()
