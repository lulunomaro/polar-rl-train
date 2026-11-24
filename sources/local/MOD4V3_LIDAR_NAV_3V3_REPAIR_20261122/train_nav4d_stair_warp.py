"""COMMANDER-AUTHORED 4,096-World `mujoco_warp` Ultra-Fast PPO Entry Script for Priority #1 (`E_stair_nav4d`)."""
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
    parser.add_argument("--lr", type=float, default=6.0e-5)
    parser.add_argument("--init-ckpt", type=Path, default=ROOT / "weights/E_stair_nav4d_candidate.pt")
    args = parser.parse_args()

    torch.set_num_threads(1)
    torch.manual_seed(20261122)
    wp.config.kernel_cache_dir = str(ROOT / "cache/warp")

    from manual_fsm_model import SymmetricE0
    from stair_warp_gpu import StairWarpGpu
    from stair_warp_model import StairWarpExpert
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

    donor_payload = torch.load(ROOT / "weights/stair_donor.pt", map_location="cpu", weights_only=False)
    actor = StairWarpExpert(donor_payload, enable_hs_residual=True)
    init_info = "stair_donor_cold"
    if args.init_ckpt is not None and args.init_ckpt.is_file():
        ckpt = torch.load(args.init_ckpt, map_location="cpu", weights_only=False)
        missing, unexpected = actor.load_state_dict(ckpt["actor"], strict=False)
        assert not unexpected and all(k.startswith(("hs_conv.", "hs_delta.")) for k in missing), (missing, unexpected)
        init_info = f"frozen_r3_plus_hs:{args.init_ckpt.name}"
        print(f"Loaded frozen r3 base + zero-init hs_residual from {args.init_ckpt}", flush=True)

    env = None
    closed = False
    err_txt = None
    try:
        env = StairWarpGpu(args.envs, 20261122, e0, ROOT / "cache/stair_warp")
        critic = AsymmetricValue(459 + env.extra().shape[1])
        run_ppo(
            env,
            actor,
            critic,
            args.job,
            seconds=args.seconds,
            kind="stair",
            probe_dir=args.probe,
            donor_meta={"donor": "E_stair_stage2_gate_final_fsm_r10c_model_015m", "engine": "mujoco_warp_4096", "init": init_info},
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
