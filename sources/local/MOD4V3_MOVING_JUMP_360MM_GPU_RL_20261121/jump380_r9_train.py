"""R9 zero-update preflight and one 600-second Host72 GPU 1 PPO run."""

from argparse import ArgumentParser
import json
from pathlib import Path
import time
import traceback

import torch
import warp as wp

from jump360_scene import HERE, json_save, sha
from jump380_r6_scene import HALF_WIDTH, prepare_scene
from jump380_r7_policy import load_policy
import jump380_r7_train as ppo
from jump380_r8_train import preflight
from jump380_r9_gpu import (CHARGE_BRAKE_WEIGHT, CHARGE_SPEED_FRACTION, HEIGHT_CAP,
                            HEIGHT_FORWARD_CAP, HEIGHT_FORWARD_SPEED, LOW_SPEED_PROBABILITY,
                            SPEED_SPLIT, TAKEOFF_SPEED, Jump380Gpu)
from jump380_r9_timing import (EXPERIMENT, JITTER_HIGH_M, JITTER_LOW_M, PARENT, PARENT_SHA,
                               PRESS_GAP_M, RUN, TRAIN_TIMING)
from train_jump360_gpu import ENVS, binding

SEED = 38007
BUDGET = 600.
SOURCES = ("jump380_r9_train.py", "jump380_r9_gpu.py", "jump380_r9_timing.py",
           "jump380_r8_train.py", "jump380_r8_gpu.py", "jump380_r8_timing.py", *ppo.SOURCES)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--mode", choices=("probe", "train"), required=True)
    parser.add_argument("--preflight", type=Path)
    args = parser.parse_args()
    if args.mode == "train" and args.preflight is None:
        parser.error("--preflight is required for training")
    args.out.mkdir(parents=True, exist_ok=True)
    initialized = False
    torch.set_num_threads(1)
    torch.manual_seed(SEED)
    wp.config.kernel_cache_dir = str(RUN/"cache/warp")
    try:
        timing = json.loads(TRAIN_TIMING.read_text(encoding="utf-8"))
        if (sha(PARENT) != PARENT_SHA or timing["checkpoint_sha256"] != PARENT_SHA
                or timing["experiment"] != EXPERIMENT or not timing["training"]):
            raise ValueError("R9 requires the pinned R8 parent and its measured geometry")
        if args.mode == "train":
            probe = json.loads((args.preflight/"PROBE.json").read_text(encoding="utf-8"))
            if not probe["passed"] or not probe["physical_exposure_gate_passed"]:
                raise ValueError("R9 PPO requires measured 380 mm exposure in the preflight")
        gpu = binding()
        initialized = True
        metadata = dict(
            experiment=EXPERIMENT, gpu=gpu, envs=ENVS, actor_inputs=[35, 420], action_dim=6,
            key_obs=30, policy_hz=50, physics_hz=400, parent_sha256=PARENT_SHA, initial_sha256=PARENT_SHA,
            obstacle_width_m=2.*HALF_WIDTH, timing_sha256=sha(TRAIN_TIMING), scene_sha256=sha(prepare_scene(False)),
            source_sha256={name: sha(HERE/name) for name in SOURCES}, seed=SEED,
            launch_objective=dict(press_floor_m=PRESS_GAP_M, jitter_m=[JITTER_LOW_M, JITTER_HIGH_M],
                                  takeoff_target_m_s=TAKEOFF_SPEED, impulse_weight=.38,
                                  impulse_cap_m_s=2.2, air_progress_weight=5.0,
                                  clearance_cap_ratio=HEIGHT_CAP, obstacle_vx_scale_m_s=HEIGHT_FORWARD_SPEED,
                                  obstacle_forward_factor_cap=HEIGHT_FORWARD_CAP,
                                  charge_speed_fraction=CHARGE_SPEED_FRACTION, charge_brake_weight=CHARGE_BRAKE_WEIGHT,
                                  speed_split_m_s=SPEED_SPLIT, low_speed_probability=LOW_SPEED_PROBABILITY),
        )
        json_save(args.out/"STARTUP.json", metadata)
        model = load_policy(PARENT, "cuda:0")
        env = Jump380Gpu(ENVS, SEED, timing)
        if args.mode == "probe":
            preflight(env, model, args.out, metadata)
        else:
            ppo.BUDGET = BUDGET
            ppo.train(env, model, args.out, args.preflight, metadata)
    except BaseException:
        (args.out/"ERROR.txt").write_text(traceback.format_exc(), encoding="utf-8")
        raise
    finally:
        if initialized:
            torch.cuda.synchronize()
        json_save(args.out/"SAFE_CLOSED.json", dict(epoch=time.time(), cuda_synchronized=initialized, mode=args.mode))


if __name__ == "__main__":
    main()
