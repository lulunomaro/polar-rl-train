"""Run the R10 zero-update probe or the 600-second GPU 1 PPO job."""

from argparse import ArgumentParser
import json
import math
from pathlib import Path
import time
import traceback

import torch
import warp as wp

from jump360_scene import HERE, json_save, sha
from jump380_r6_scene import HALF_WIDTH, prepare_scene
import jump380_r7_train as ppo
from jump380_r8_train import preflight
from jump380_r10_gpu import (CHARGE_BRAKE_WEIGHT, CHARGE_SPEED_FRACTION, HEIGHT_CAP,
                            HEIGHT_FORWARD_CAP, HEIGHT_FORWARD_SPEED, HIGH_SPEED_PITCH_MIN_VX,
                            HIGH_SPEED_PITCH_TARGET, HIGH_SPEED_PITCH_WEIGHT, LOW_SPEED_PROBABILITY,
                            SPEED_ANCHORS, SPEED_SPLIT, TAKEOFF_SPEED, Jump380Gpu)
from jump380_r10_policy import EXPERIMENT, MAX_SPEED, MIN_SPEED, MODEL_TYPE, PARENT, PARENT_SHA, RUN, load_policy
from jump380_r10_timing import CRUISE_FILE, JITTER_HIGH_M, JITTER_LOW_M, PRESS_GAP_M, TRAIN_TIMING
from train_jump360_gpu import ENVS, binding

SEED = 38007
BUDGET = 600.
SOURCES = ("jump380_r10_train.py", "jump380_r10_gpu.py", "jump380_r10_policy.py", "jump380_r10_timing.py",
           "jump380_r9_gpu.py", "jump380_r8_train.py", "jump380_r8_gpu.py", "jump380_r8_timing.py",
           *ppo.SOURCES)


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def speed_coverage_passed(report):
    stats = report["stats"]
    low, high = stats["sampled_reset_min"][0], stats["sampled_reset_max"][0]
    return (abs(low - MIN_SPEED) < .01 and high == MAX_SPEED and stats["reset_batches_with_anchors"] > 0
            and min(stats["speed_anchor_reset_counts"]) >= stats["reset_batches_with_anchors"])


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
        timing = read(TRAIN_TIMING)
        cruise = read(CRUISE_FILE)
        if (sha(PARENT) != PARENT_SHA or timing["checkpoint_sha256"] != PARENT_SHA
                or timing["experiment"] != EXPERIMENT or not timing["training"]
                or cruise["checkpoint_sha256"] != PARENT_SHA or not cruise["high_speed_target_passed"]):
            raise ValueError("R10 requires the pinned parent and the measured R10 cruise and geometry")
        if args.mode == "train":
            probe = read(args.preflight/"PROBE.json")
            if (not probe["passed"] or not probe["physical_exposure_gate_passed"]
                    or not probe["speed_coverage_passed"]
                    or not read(args.preflight/"SAFE_CLOSED.json")["cuda_synchronized"]):
                raise ValueError("R10 PPO requires a passing and closed 600-step R10 probe")
        gpu = binding()
        initialized = True
        metadata = dict(
            experiment=EXPERIMENT, gpu=gpu, envs=ENVS, actor_inputs=[35, 420], action_dim=6,
            key_obs=30, policy_hz=50, physics_hz=400, parent_sha256=PARENT_SHA, initial_sha256=PARENT_SHA,
            obstacle_width_m=2.*HALF_WIDTH, timing_sha256=sha(TRAIN_TIMING), cruise_sha256=sha(CRUISE_FILE),
            scene_sha256=sha(prepare_scene(False)), source_sha256={name: sha(HERE/name) for name in SOURCES},
            seed=SEED, ppo_budget_s=BUDGET,
            launch_objective=dict(
                press_floor_m=PRESS_GAP_M, jitter_m=[JITTER_LOW_M, JITTER_HIGH_M],
                takeoff_target_m_s=TAKEOFF_SPEED, impulse_weight=.38, impulse_cap_m_s=2.2,
                air_progress_weight=5., clearance_cap_ratio=HEIGHT_CAP, obstacle_vx_scale_m_s=HEIGHT_FORWARD_SPEED,
                obstacle_forward_factor_cap=HEIGHT_FORWARD_CAP, charge_speed_fraction=CHARGE_SPEED_FRACTION,
                charge_brake_weight=CHARGE_BRAKE_WEIGHT, speed_range_m_s=[MIN_SPEED, MAX_SPEED],
                speed_split_m_s=SPEED_SPLIT, low_speed_probability=LOW_SPEED_PROBABILITY,
                speed_anchors_m_s=SPEED_ANCHORS, high_speed_pitch_min_vx_m_s=HIGH_SPEED_PITCH_MIN_VX,
                high_speed_pitch_target_deg=math.degrees(HIGH_SPEED_PITCH_TARGET),
                high_speed_pitch_weight=HIGH_SPEED_PITCH_WEIGHT),
        )
        json_save(args.out/"STARTUP.json", metadata)
        model = load_policy(PARENT, "cuda:0")
        env = Jump380Gpu(ENVS, SEED, timing)
        if args.mode == "probe":
            preflight(env, model, args.out, metadata)
            report = read(args.out/"PROBE.json")
            report["speed_coverage_passed"] = speed_coverage_passed(report)
            report["passed"] &= report["speed_coverage_passed"]
            json_save(args.out/"PROBE.json", report)
            if not report["passed"]:
                raise RuntimeError("R10 speed coverage failed")
        else:
            ppo.BUDGET = BUDGET
            ppo.MODEL_TYPE = MODEL_TYPE
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
