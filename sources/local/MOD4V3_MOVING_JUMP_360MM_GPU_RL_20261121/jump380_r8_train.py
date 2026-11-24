"""R8 preflight and bounded host72 GPU 1 PPO continuation."""

from argparse import ArgumentParser
import json
import math
from pathlib import Path
import time
import traceback

import torch
import warp as wp

from jump360_scene import HERE, json_save, sha
from jump380_r4_contact import audit_contact
from jump380_r6_gpu import PHASES
from jump380_r6_scene import APPROACH_YAW_LIMIT_DEG, APPROACH_Y_LIMIT, HALF_WIDTH, KINDS, prepare_scene
from jump380_r7_policy import load_policy, sample_action
from jump380_r7_train import SOURCES as PPO_SOURCES, STD_START, train
from jump380_r8_gpu import TAKEOFF_SPEED, Jump380Gpu
from jump380_r8_timing import JITTER_HIGH_M, JITTER_LOW_M, PARENT, PARENT_SHA, PRESS_GAP_M, RUN
from moe_jump_model import mirror_action_6, mirror_history_420, mirror_obs_35
from train_jump360_gpu import ENVS, binding

SEED = 38007
SOURCES = ("jump380_r8_train.py", "jump380_r8_gpu.py", "jump380_r8_timing.py", *PPO_SOURCES)
TIMING = RUN/"calibration/TRAIN_TIMING.json"


def platform_exposure(stats):
    kind = stats["categories"].index("platform_380")
    field = stats["fields"].index("wheel_crossing_in_main_flight")
    crossings = sum(row[field] for stage in stats["by_stage_dr_terrain_speed"]
                    for dr in stage for row in dr[kind])
    support = stats["phase_samples"][stats["phase_columns"].index("platform_380_both_support")]
    return crossings, support


def preflight(env, model, out, metadata):
    contact = audit_contact()
    json_save(out/"CONTACT_AUDIT.json", contact)
    if not contact["passed"]:
        raise RuntimeError("R8 contact audit failed")
    initial = {key: value.detach().clone() for key, value in model.state_dict().items()}
    history_error = previous_error = deployed_approach_difference = 0.
    action_equivariance_error = phase_invariance_error = 0.
    approach_logit = -math.inf
    before = time.monotonic()
    with torch.no_grad():
        for step in range(600):
            obs, history = env.obs, env.hist.flatten(1)
            means, logits, base = model.action_phase_and_base(obs, history)
            before_press = env.press < 0
            deployed_approach_difference = max(deployed_approach_difference,
                float(((means - base).abs() * before_press[:, None]).max()))
            approach_logit = max(approach_logit, float(logits.masked_fill(~before_press, -torch.inf).max()))
            if step % 100 == 0:
                a, m = model.action_and_phase(mirror_obs_35(obs), mirror_history_420(history))
                action_equivariance_error = max(action_equivariance_error,
                    float((means - mirror_action_6(a)).abs().max()))
                phase_invariance_error = max(phase_invariance_error, float((m - logits).abs().max()))
            noise_scale = torch.where(env.mode_target(), STD_START,
                                      torch.where(env.obs[:, 0] > .4, .58*STD_START, .26*STD_START))
            draws = torch.where(before_press[:, None], base,
                                sample_action(means, noise_scale))
            obs, hist, reward, done = env.step(draws)
            if not all(bool(x.isfinite().all()) for x in (obs, hist, reward, env.p, env.v, means)):
                raise FloatingPointError(f"Nonfinite value returned by R8 step {step+1}")
            history_error = max(history_error, float((hist[:, -35:]-obs).abs().max()))
            previous_error = max(previous_error, float((obs[:, 22:28]-torch.where(
                done[:, None], 0., draws.clamp(-6., 6.))).abs().max()))
            if (step+1)%100 == 0:
                point = dict(steps=step+1, full_dr=int(env.dr.sum()), phase_counts=env.phase_samples.tolist(),
                             timing={"elapsed_s": time.monotonic()-before}, stats=env.audit())
                json_save(out/"LATEST.json", point)
                crossing, support = platform_exposure(point["stats"])
                print("probe", step+1, "380mm flight crossings", crossing,
                      "380mm two-wheel top ticks", support, flush=True)

    grad_obs = env.obs[:512].clone()
    grad_obs[:, 30] = 1.
    grad_history = env.hist[:512].flatten(1)
    action, phase_logits = model.action_and_phase(grad_obs, grad_history)
    test = action.square().mean() + phase_logits.square().mean()
    test += model.evaluate_value(grad_obs, grad_history, env.extra()[:512]).square().mean()
    test.backward()
    groups = dict(mode=model.actor_body.mode_head, drive=model.actor_body.drive_head,
                  encoder=model.actor_body.e_jump.encoder, jump=model.actor_body.e_jump.delta_head, critic=model.critic)
    grad = {name: float(torch.stack([parameter.grad.square().sum() for parameter in group.parameters()]).sum().sqrt())
            for name, group in groups.items()}
    actor_delta = max(float((value-initial[key]).abs().max()) for key, value in model.state_dict().items())
    stats = env.audit()
    phase = stats["phase_samples"]
    approach_y, approach_yaw = stats["approach_max_by_dr"][0]
    approach_yaw = math.degrees(approach_yaw)
    course_ok = approach_y < APPROACH_Y_LIMIT and approach_yaw < APPROACH_YAW_LIMIT_DEG
    recovered_substeps = {kind: phase[PHASES.index(kind + "_dual_peak_missed_by_last_substep")]
                          for kind in KINDS[1:3]}
    presses = [cell for terrain in stats["press_clearance_by_terrain_speed"][1:] for cell in terrain]
    valid_press_distances = all(count > 0 and below_floor == 0
                                for count, below_floor, _ in presses)
    crossing, support = platform_exposure(stats)
    platform_exposed = crossing > 0 or support > 0
    valid_jitter_range = (abs(stats["sampled_reset_min"][2]-JITTER_LOW_M) < .001
                          and abs(stats["sampled_reset_max"][2]-JITTER_HIGH_M) < .001)
    passed = (all(math.isfinite(value) and value > 0. for value in grad.values())
              and valid_press_distances and deployed_approach_difference == 0.
              and action_equivariance_error <= 1.e-5 and phase_invariance_error <= 1.e-5
              and actor_delta == history_error == previous_error == 0.
              and phase[0] > 0 and phase[1] > 0 and course_ok and platform_exposed
              and all(count > 0 for count in stats["terrain_reset_counts"])
              and all(count > 0 for count in stats["holds_by_ticks"][12:51])
              and valid_jitter_range and stats["max_contacts_global"] < stats["contact_capacity"]
              and stats["max_constraints_per_world"] < stats["constraint_capacity"])
    json_save(out/"PROBE.json", dict(passed=passed, steps=600, ppo_updates=0, adam_steps=0,
                                    policy_parameter_max_change=actor_delta, history_error=history_error,
                                    executed_previous_action_error=previous_error, grad_norms=grad,
                                    valid_press_distances=valid_press_distances,
                                    wheel_crossing_in_main_flight_380=crossing,
                                    platform_380_both_support=support,
                                    physical_exposure_gate_passed=platform_exposed,
                                    action_equivariance_max_error=action_equivariance_error,
                                    mode_invariance_max_error=phase_invariance_error,
                                    approach_max_mode_probability=1./(1.+math.exp(-approach_logit)),
                                    approach_passed=course_ok, approach_max_abs_y_m=approach_y,
                                    approach_max_abs_yaw_deg=approach_yaw,
                                    approach_deployed_vs_frozen_max_action_difference=deployed_approach_difference,
                                    dual_peak_support_missed_by_last_substep=recovered_substeps,
                                    elapsed_s=time.monotonic()-before, stats=stats, **metadata))
    if not passed:
        raise RuntimeError(f"R8 preflight failed. 380 mm crossings={crossing}, "
                           f"two-wheel support ticks={support}. See PROBE.json.")


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
        timing = json.loads(TIMING.read_text(encoding="utf-8"))
        if sha(PARENT) != PARENT_SHA or timing["checkpoint_sha256"] != PARENT_SHA or not timing["training"]:
            raise ValueError("R8 requires the pinned parent and its measured training geometry")
        if args.mode == "train":
            probe = json.loads((args.preflight/"PROBE.json").read_text(encoding="utf-8"))
            if not probe["passed"] or not probe["physical_exposure_gate_passed"]:
                raise ValueError("R8 PPO requires measured 380 mm exposure in the preflight")
        gpu = binding()
        initialized = True
        metadata = dict(
            experiment="jump380_r8", gpu=gpu, envs=ENVS, actor_inputs=[35, 420], action_dim=6,
            key_obs=30, policy_hz=50, physics_hz=400, parent_sha256=PARENT_SHA, initial_sha256=PARENT_SHA,
            obstacle_width_m=2.*HALF_WIDTH, timing_sha256=sha(TIMING), scene_sha256=sha(prepare_scene(False)),
            source_sha256={name: sha(HERE/name) for name in SOURCES}, seed=SEED,
            launch_objective=dict(press_floor_m=PRESS_GAP_M, jitter_m=[JITTER_LOW_M, JITTER_HIGH_M],
                                  takeoff_target_m_s=TAKEOFF_SPEED, impulse_weight=.38,
                                  impulse_cap_m_s=2.2, air_progress_weight=5.0),
        )
        json_save(args.out/"STARTUP.json", metadata)
        model = load_policy(PARENT, "cuda:0")
        env = Jump380Gpu(ENVS, SEED, timing)
        if args.mode == "probe":
            preflight(env, model, args.out, metadata)
        else:
            train(env, model, args.out, args.preflight, metadata)
    except BaseException:
        (args.out/"ERROR.txt").write_text(traceback.format_exc(), encoding="utf-8")
        raise
    finally:
        if initialized:
            torch.cuda.synchronize()
        json_save(args.out/"SAFE_CLOSED.json", dict(epoch=time.time(), cuda_synchronized=initialized, mode=args.mode))


if __name__ == "__main__":
    main()
