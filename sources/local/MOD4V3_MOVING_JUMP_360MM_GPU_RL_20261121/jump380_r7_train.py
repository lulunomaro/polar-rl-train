"""R7 zero-update preflight and one 750-second PPO run on host72 GPU 1."""
from argparse import ArgumentParser
import json
import math
import os
from pathlib import Path
import time
import traceback

import torch
from torch.nn import functional as F
import warp as wp

from jump360_scene import HERE, json_save, sha
from jump380_r4_contact import audit_contact
from jump380_r7_gpu import DR_LEVELS, FIELDS, PHASES, Jump380Gpu
from jump380_r6_train import CURRICULUM_MIN_TRIALS, CURRICULUM_RATE, Curriculum
from jump380_r7_policy import (INITIAL, MODEL_TYPE, PARENT_SHA, RECOVERY_LOGIT, RUN,
                              SYMMETRIC_VARIANCE, action_log_prob, load_policy, sample_action)
from moe_jump_model import mirror_action_6, mirror_history_420, mirror_obs_35
from jump380_r5_support import MIN_SUPPORT_TICKS, SUPPORT_WINDOW_TICKS
from jump380_r6_scene import APPROACH_YAW_LIMIT_DEG, APPROACH_Y_LIMIT, HALF_WIDTH, KINDS, prepare_scene
from train_jump360_gpu import ENVS, ROLLOUT, Rollout, binding, monitor_deadline

BUDGET = 750.
STD_START, STD_END = .085, .045
LR, CLIP, EPOCHS = 1.0e-4, .20, 4
SEED = 38007
SOURCES = (
    "jump380_r7_train.py", "jump380_r7_gpu.py", "jump380_r7_policy.py",
    "jump380_r6_train.py", "jump380_r6_scene.py", "jump380_r6_gpu.py", "jump380_r6_policy.py",
    "jump380_r5_scene.py", "jump380_r5_support.py",
    "jump380_r4_gpu.py", "jump380_r4_contact.py",
    "jump360_r3_policy.py", "train_jump360_gpu.py", "jump360_gpu.py", "jump360_scene.py",
)
TIMING = RUN/"calibration/TRAIN_TIMING.json"


def preflight(env, model, out, metadata):
    contact = audit_contact()
    json_save(out/"CONTACT_AUDIT.json", contact)
    if not contact["passed"]:
        raise RuntimeError("R7 contact audit failed")
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
                raise FloatingPointError(f"Nonfinite value returned by R7 step {step+1}")
            history_error = max(history_error, float((hist[:, -35:]-obs).abs().max()))
            previous_error = max(previous_error, float((obs[:, 22:28]-torch.where(
                done[:, None], 0., draws.clamp(-6., 6.))).abs().max()))
            if (step+1)%100 == 0:
                point = dict(steps=step+1, full_dr=int(env.dr.sum()), phase_counts=env.phase_samples.tolist(),
                             timing={"elapsed_s": time.monotonic()-before}, stats=env.audit())
                json_save(out/"LATEST.json", point)
                print("probe", step+1, point["full_dr"], point["phase_counts"], flush=True)

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
    valid_press_distances = all(count > 0 and below_rule == below_032m == 0
                                for count, below_rule, below_032m in presses)
    passed = (all(math.isfinite(value) and value>0. for value in grad.values())
              and valid_press_distances and deployed_approach_difference == 0.
              and action_equivariance_error <= 1.e-5 and phase_invariance_error <= 1.e-5
              and actor_delta==0. and history_error==0. and previous_error==0.
              and phase[0] > 0 and phase[1] > 0 and course_ok
              and all(count>0 for count in stats["terrain_reset_counts"])
              and all(count>0 for count in stats["holds_by_ticks"][12:51])
              and abs(stats["sampled_reset_min"][2]+.12)<.001
              and abs(stats["sampled_reset_max"][2]-.12)<.001 and stats["max_contacts_global"]<stats["contact_capacity"]
              and stats["max_constraints_per_world"]<stats["constraint_capacity"] and phase[6]==0)
    json_save(out/"PROBE.json", dict(passed=passed, steps=600, ppo_updates=0, adam_steps=0,
                                    policy_parameter_max_change=actor_delta, history_error=history_error,
                                    executed_previous_action_error=previous_error, grad_norms=grad,
                                    valid_press_distances=valid_press_distances,
                                    action_equivariance_max_error=action_equivariance_error,
                                    mode_invariance_max_error=phase_invariance_error,
                                    approach_max_mode_probability=1./(1.+math.exp(-approach_logit)),
                                    approach_passed=course_ok, approach_max_abs_y_m=approach_y,
                                    approach_max_abs_yaw_deg=approach_yaw,
                                    approach_deployed_vs_frozen_max_action_difference=deployed_approach_difference,
                                    dual_peak_support_missed_by_last_substep=recovered_substeps,
                                    elapsed_s=time.monotonic()-before, stats=stats, **metadata))
    if not passed:
        raise RuntimeError(f"R7 zero-update preflight failed with approach |y|={approach_y:.4f} m "
                           f"and |yaw|={approach_yaw:.3f} deg")


def save(model, optim, env, out, name, metadata):
    target = out/name
    temp = target.with_suffix(".partial")
    payload = dict(model_type=MODEL_TYPE, obs_dim=35, hist_dim=420, action_dim=6, hist_len=12,
                   jump_mode_bit_index=30, state_dict=model.state_dict(), optimizer=optim.state_dict(),
                   metadata=metadata, cpu_rng=torch.get_rng_state(), cuda_rng=torch.cuda.get_rng_state(),
                   reset_rng=env.rng.get_state())
    with temp.open("wb") as stream:
        torch.save(payload, stream)
        stream.flush()
        os.fsync(stream.fileno())
    temp.replace(target)
    return dict(checkpoint=name, sha256=sha(target), file_bytes=target.stat().st_size, **metadata)


def train(env, model, out, probe_folder, metadata):
    probe = json.loads((probe_folder/"PROBE.json").read_text(encoding="utf-8"))
    closed = json.loads((probe_folder/"SAFE_CLOSED.json").read_text(encoding="utf-8"))
    if not (probe["passed"] and probe["steps"]==600 and probe["ppo_updates"]==probe["adam_steps"]==0
            and closed["cuda_synchronized"] and all(probe[key]==metadata[key] for key in (
                "source_sha256", "initial_sha256", "timing_sha256", "scene_sha256", "envs"))):
        raise ValueError("R7 requires the matching completed zero-update preflight")
    model.ejump_log_std.requires_grad_(False)
    frozen = {name: value.detach().clone() for name, value in model.state_dict().items()
              if name=="e0_std" or name.startswith(("actor_body.e0.", "actor_body.e_jump.loco_base."))}
    head_start = model.actor_body.e_jump.delta_head[-1].weight.detach().clone()
    drive_start = model.actor_body.drive_head[-1].weight.detach().clone()
    trainable = [parameter for parameter in model.parameters() if parameter.requires_grad]
    optimizer = torch.optim.Adam(trainable, lr=LR)
    rollout = Rollout(env.n)
    for key in ("mode", "scale", "mode_weight", "active"):
        rollout.data[key] = torch.zeros_like(rollout.data["reward"])
    schedule = Curriculum(env)
    settings = dict(std_start=STD_START, std_end=STD_END, lr=LR, clip=CLIP, epochs=EPOCHS,
                    actor_samples="after operator press", approach="mirrored calibrated frozen c874",
                    symmetric_exploration_variance=SYMMETRIC_VARIANCE, phase_recovery_logit=RECOVERY_LOGIT,
                    phase_loss_weight=.10, pre_press_phase_target=0, pre_press_phase_weight=1.25,
                    held_touchdown_weight=3., curriculum_window_update_stride=5,
                    curriculum_window_max_updates=100, curriculum_380mm_strict_rate=CURRICULUM_RATE,
                    curriculum_380mm_min_trials=CURRICULUM_MIN_TRIALS, support_window_ticks=SUPPORT_WINDOW_TICKS,
                    min_support_ticks=MIN_SUPPORT_TICKS)
    updates = adam = env_steps = 0
    partial = False
    metrics = {}
    approach_difference = torch.zeros((), device=env.device)
    start_wall, start = time.time(), time.monotonic()
    deadline = start+BUDGET
    stop = out/"REQUEST_STOP"
    watchdog, pipe = monitor_deadline(BUDGET+45., out)
    json_save(out/"PPO_START.json", dict(start_epoch=start_wall, compute_deadline_epoch=start_wall+BUDGET,
                                       hard_deadline_epoch=start_wall+BUDGET+45., budget_s=BUDGET,
                                       envs=env.n, rollout=ROLLOUT, ppo_settings=settings, **metadata["gpu"]))
    checkpoint_targets = iter((60, 180, 360, 540, 720))
    next_checkpoint = next(checkpoint_targets)
    std = STD_START

    def status():
        current = model.state_dict()
        return dict(elapsed_s=time.monotonic()-start, start_epoch=start_wall, ppo_updates=updates, adam_steps=adam,
                    environment_steps=env_steps, physics_substeps=env_steps*8, ppo_settings=settings,
                    exploration_std=std, active_dr_stage=schedule.stage, full_dr_reset_probability=env.dr_probability,
                    approach_deployed_vs_frozen_max_action_difference=float(approach_difference),
                    curriculum_last=schedule.last, dr_promotions=schedule.moves, stats=env.audit(),
                    e0_max_parameter_change=max(float((current[key]-value).abs().max()) for key, value in frozen.items()),
                    jump_head_max_change=float((model.actor_body.e_jump.delta_head[-1].weight-head_start).detach().abs().max()),
                    drive_head_max_change=float((model.actor_body.drive_head[-1].weight-drive_start).detach().abs().max()),
                    **metrics, **metadata)

    try:
        while time.monotonic()<deadline and not stop.exists():
            began = time.monotonic()
            std = STD_START + (STD_END-STD_START)*min(1., (began-start)/BUDGET)
            model.ejump_log_std.fill_(math.log(std))
            with torch.no_grad():
                for tick in range(ROLLOUT):
                    obs, hist, priv = env.obs, env.hist.flatten(1), env.extra()
                    phase = env.mode_target()
                    scale = torch.where(phase, std, torch.where(obs[:, 0]>.4, .58*std, .26*std))
                    held_recovery = (env.first_touch_tick >= 0) & (obs[:, 30] > .5)
                    active = env.press >= 0
                    mode_weight = torch.where(active, 1. + 2.*held_recovery, 1.25)
                    mean, _, base = model.action_phase_and_base(obs, hist)
                    difference = ((mean - base).abs() * (~active)[:, None]).amax()
                    approach_difference.copy_(torch.maximum(approach_difference, difference))
                    draw = sample_action(mean, scale)
                    rollout.store(tick, obs=obs, history=hist, priv=priv, act=draw,
                                  log=action_log_prob(draw, mean, scale),
                                  value=model.evaluate_value(obs, hist, priv), mode=phase, scale=scale,
                                  mode_weight=mode_weight, active=active)
                    action = torch.where(active[:, None], draw, base)
                    _, _, reward, done = env.step(action)
                    rollout.store(tick, reward=reward, done=done)
                    env_steps += env.n
                    if time.monotonic()>=deadline or stop.exists():
                        partial = True
                        break
                if partial:
                    break
                advantage, returns = rollout.returns(model.evaluate_value(env.obs, env.hist.flatten(1), env.extra()))
            data = {name: values.flatten(0, 1) for name, values in rollout.data.items()}
            advantage, returns = advantage.flatten(), returns.flatten()
            advantage = ((advantage-advantage.mean())/advantage.std(unbiased=False).clamp_min(1.e-5)).clamp(-8., 8.)
            minibatches, total_loss, total_kl = 0, 0., 0.
            for _ in range(EPOCHS):
                epoch_kl = 0.
                for rows in torch.randperm(len(advantage), device=env.device).chunk(4):
                    if time.monotonic()>=deadline or stop.exists():
                        partial = True
                        break
                    obs, hist, priv = (data[name][rows] for name in ("obs", "history", "priv"))
                    mean, phase = model.action_and_phase(obs, hist)
                    log_prob = action_log_prob(data["act"][rows], mean, data["scale"][rows])
                    change = (log_prob-data["log"][rows]).clamp(-12., 12.)
                    ratio = change.exp()
                    adv = advantage[rows]
                    active = data["active"][rows]
                    active_count = active.sum().clamp_min(1.)
                    policy_loss = -(torch.minimum(ratio*adv, ratio.clamp(1.-CLIP, 1.+CLIP)*adv)
                                    * active).sum()/active_count
                    value = model.evaluate_value(obs, hist, priv)
                    phase_loss = F.binary_cross_entropy_with_logits(phase, data["mode"][rows],
                                                                    weight=data["mode_weight"][rows])
                    loss = policy_loss + F.smooth_l1_loss(value, returns[rows]) + .10*phase_loss
                    if not bool(loss.isfinite()):
                        raise FloatingPointError("Nonfinite R7 training objective")
                    optimizer.zero_grad(set_to_none=True)
                    loss.backward()
                    torch.nn.utils.clip_grad_norm_(trainable, 1., error_if_nonfinite=True)
                    optimizer.step()
                    adam += 1
                    minibatches += 1
                    kl = float(((ratio-1.-change).detach() * active).sum()/active_count)
                    epoch_kl += kl
                    total_kl += kl
                    total_loss += float(loss.detach())
                if partial or epoch_kl/4 > .045:
                    break
            if partial:
                break
            updates += 1
            if updates%5 == 0:
                schedule.update(updates, time.monotonic()-start)
            if updates==1 or updates%5 == 0 or time.monotonic()-start>=next_checkpoint:
                metrics = dict(loss=total_loss/minibatches, approximate_kl=total_kl/minibatches,
                               rollout_seconds=time.monotonic()-began,
                               current_batch_mean_reward=float(data["reward"].mean()))
                current = status()
                if current["e0_max_parameter_change"] != 0.:
                    raise RuntimeError("Frozen locomotion base changed")
                json_save(out/"LATEST.json", current)
                print("ppo", updates, "adam", adam, "seconds", round(current["elapsed_s"], 2),
                      "stage", schedule.stage, "full_dr", current["stats"]["full_dr_envs"],
                      "gate", schedule.last, flush=True)
                if updates == 1:
                    json_save(out/"FIRST_UPDATE.json", current)
                if current["elapsed_s"]>=next_checkpoint:
                    name = f"model_{next_checkpoint//60:03d}m.pt"
                    json_save(out/(name+".json"), save(model, optimizer, env, out, name, current))
                    next_checkpoint = next(checkpoint_targets, math.inf)
        torch.cuda.synchronize()
        final = status()
        final.update(compute_end_epoch=time.time(), end_reason="requested" if stop.exists() else "budget",
                     partial_rollout_or_update=partial)
        json_save(out/"FINAL.json", save(model, optimizer, env, out, "model_final.pt", final))
    finally:
        os.close(pipe)
        os.waitpid(watchdog, 0)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--mode", choices=("probe", "train"), required=True)
    parser.add_argument("--preflight", type=Path)
    args = parser.parse_args()
    if args.mode == "train" and args.preflight is None:
        parser.error("--preflight is required for training")
    args.out.mkdir(exist_ok=True, parents=True)
    initialized = False
    torch.set_num_threads(1)
    torch.manual_seed(SEED)
    wp.config.kernel_cache_dir = str(RUN/"cache/warp")
    try:
        gpu = binding()
        initialized = True
        report = json.loads(TIMING.read_text(encoding="utf-8"))
        initial_sha = sha(INITIAL)
        if report["checkpoint_sha256"] != initial_sha or not report["training"]:
            raise ValueError("Expected measured timing for the assembled R7 actor")
        metadata = dict(experiment="jump380_r7", gpu=gpu, envs=ENVS, actor_inputs=[35, 420],
                        action_dim=6, key_obs=30, policy_hz=50, physics_hz=400,
                        parent_sha256=PARENT_SHA, initial_sha256=initial_sha,
                        obstacle_width_m=2.*HALF_WIDTH, timing_sha256=sha(TIMING),
                        scene_sha256=sha(prepare_scene(False)),
                        source_sha256={name: sha(HERE/name) for name in SOURCES})
        json_save(args.out/"STARTUP.json", metadata)
        model = load_policy(INITIAL, "cuda:0")
        env = Jump380Gpu(ENVS, SEED, report)
        if args.mode == "probe":
            preflight(env, model, args.out, metadata)
        else:
            train(env, model, args.out, HERE/args.preflight, metadata)
    except BaseException:
        (args.out/"ERROR.txt").write_text(traceback.format_exc(), encoding="utf-8")
        raise
    finally:
        if initialized:
            torch.cuda.synchronize()
        json_save(args.out/"SAFE_CLOSED.json", dict(epoch=time.time(), cuda_synchronized=initialized, mode=args.mode))


if __name__ == "__main__":
    main()
