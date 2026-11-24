"""Run the R3 zero-update probe and one 1200-second, single-GPU PPO experiment."""
from argparse import ArgumentParser
from collections import deque
import json
import math
import os
from pathlib import Path
import time
import traceback

import numpy as np
import torch
from torch.distributions import Normal
from torch.nn import functional as F
import warp as wp

from calibrate_jump360_r3 import PARENT_R2, R2_SHA
from jump360_r3_gpu import DR_LEVELS, Jump360R3Gpu, training_timing
from jump360_r3_policy import MODEL_TYPE, load_policy
from jump360_scene import HERE, json_save, sha
from train_jump360_gpu import ENVS, ROLLOUT, Rollout, binding, monitor_deadline

BUDGET = 1200.
STD_START, STD_END = .16, .055
LR, CLIP, EPOCHS = 1.2e-4, .20, 4
SEED = 36003
SOURCES = (
    "train_jump360_r3.py", "jump360_r3_policy.py", "jump360_r3_gpu.py", "train_jump360_gpu.py",
    "jump360_gpu.py", "jump360_scene.py", "calibrate_jump360_r3.py",
)


def preflight(env, model, out, metadata):
    initial = {key: value.detach().clone() for key, value in model.state_dict().items()}
    history_error = previous_error = 0.
    before = time.monotonic()
    with torch.no_grad():
        for step in range(600):
            if step in (200, 400):
                env.set_stage(step//200)
            means = model.act_deterministic(env.obs, env.hist.flatten(1))
            noise_scale = torch.where(env.mode_target(), .10, .035)
            draws = means + noise_scale[:, None]*torch.randn_like(means)
            obs, hist, reward, done = env.step(draws)
            if not all(bool(x.isfinite().all()) for x in (obs, hist, reward, env.p, env.v, means)):
                raise FloatingPointError(f"Nonfinite value returned by R3 step {step+1}")
            history_error = max(history_error, float((hist[:, -35:]-obs).abs().max()))
            previous_error = max(previous_error, float((obs[:, 22:28]-torch.where(
                done[:, None], 0., draws.clamp(-6., 6.))).abs().max()))
            if (step+1)%100 == 0:
                point = dict(steps=step+1, full_dr=int(env.dr.sum()), phase_counts=env.phase_counts.tolist(),
                             timing={"elapsed_s": time.monotonic()-before}, stats=env.audit())
                json_save(out/"LATEST.json", point)
                print("probe", step+1, point["full_dr"], point["phase_counts"], flush=True)

    phase, jump, drive = model.actor_body.components(env.obs[:512], env.hist[:512].flatten(1))
    test = jump.square().mean()+drive.square().mean()+phase.square().mean()
    test += model.evaluate_value(env.obs[:512], env.hist[:512].flatten(1), env.extra()[:512]).square().mean()
    test.backward()
    groups = dict(mode=model.actor_body.mode_head, drive=model.actor_body.drive_head,
                  encoder=model.actor_body.e_jump.encoder, jump=model.actor_body.e_jump.delta_head, critic=model.critic)
    grad = {name: float(torch.stack([parameter.grad.square().sum() for parameter in group.parameters()]).sum().sqrt())
            for name, group in groups.items()}
    actor_delta = max(float((value-initial[key]).abs().max()) for key, value in model.state_dict().items())
    stats = env.audit()
    phase = stats["phase_samples"]
    passed = (all(math.isfinite(value) and value>0. for value in grad.values())
              and actor_delta==0. and history_error==0. and previous_error==0.
              and all(value>0 for value in (phase[0], phase[1], phase[2], phase[4]))
              and stats["full_dr_envs"]>0 and stats["max_contacts_global"]<stats["contact_capacity"]
              and stats["max_constraints_per_world"]<stats["constraint_capacity"] and phase[-1]==0)
    json_save(out/"PROBE.json", dict(passed=passed, steps=600, ppo_updates=0, adam_steps=0,
                                    policy_parameter_max_change=actor_delta, history_error=history_error,
                                    executed_previous_action_error=previous_error, grad_norms=grad,
                                    elapsed_s=time.monotonic()-before, stats=stats, **metadata))
    if not passed:
        raise RuntimeError("R3 zero-update preflight failed")


class Curriculum:
    def __init__(self, env):
        self.env = env
        self.stage = 0
        self.window = deque(maxlen=21)
        self.moves = []
        self.last = None

    def update(self, rollout, elapsed):
        stage = self.stage
        if stage==2:
            return
        group = int(stage>0)
        counts = self.env.by_stage[stage, group, :2].cpu().numpy()
        self.window.append(counts)
        recent = counts-self.window[0]
        flat_n, flat_yes = recent[0].sum(0)[[0, 3]]
        wall_n, wall_yes = recent[1, 1:7].sum(0)[[0, 3]]
        wall_speed_coverage = int((recent[1, 1:7, 3]>0).sum())
        flat_rate = flat_yes/max(1., flat_n)
        wall_rate = wall_yes/max(1., wall_n)
        self.last = dict(stage=stage, applied_full_dr=bool(group), flat_trials=int(flat_n),
                         flat_qualified=int(flat_yes), flat_rate=float(flat_rate),
                         platform_trials_08_18=int(wall_n), platform_qualified_08_18=int(wall_yes),
                         platform_rate_08_18=float(wall_rate), speeds_with_wall_pass=wall_speed_coverage)
        ready = (elapsed>=25. and flat_n>=350 and wall_n>=350 and flat_rate>=(.40 if stage==0 else .30)
                 and wall_rate>=(.025 if stage==0 else .015) and wall_speed_coverage>=3)
        if ready:
            self.stage += 1
            self.env.set_stage(self.stage)
            self.moves.append(dict(rollout=rollout, elapsed_s=elapsed,
                                   full_dr_reset_probability=DR_LEVELS[self.stage], **self.last))
            self.window.clear()
            print("curriculum", self.moves[-1], flush=True)


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
                "source_sha256", "initial_sha256", "timing_sha256", "envs"))):
        raise ValueError("R3 requires the matching completed zero-update preflight")
    model.ejump_log_std.requires_grad_(False)
    frozen = {name: value.detach().clone() for name, value in model.state_dict().items()
              if name=="e0_std" or name.startswith(("actor_body.e0.", "actor_body.e_jump.loco_base."))}
    head_start = model.actor_body.e_jump.delta_head[-1].weight.detach().clone()
    drive_start = model.actor_body.drive_head[-1].weight.detach().clone()
    trainable = [parameter for parameter in model.parameters() if parameter.requires_grad]
    optimizer = torch.optim.Adam(trainable, lr=LR)
    rollout = Rollout(env.n)
    for key in ("mode", "scale"):
        rollout.data[key] = torch.zeros_like(rollout.data["reward"])
    schedule = Curriculum(env)
    settings = dict(std_start=STD_START, std_end=STD_END, lr=LR, clip=CLIP, epochs=EPOCHS, actor_samples="all phases",
                    phase_loss_weight=.04, curriculum_window_update_stride=5, curriculum_flat_rates=[.40, .30],
                    curriculum_platform_rates=[.025, .015], min_speed_bins_with_platform_pass=3)
    updates = adam = env_steps = 0
    partial = False
    metrics = {}
    start_wall, start = time.time(), time.monotonic()
    deadline = start+BUDGET
    stop = out/"REQUEST_STOP"
    watchdog, pipe = monitor_deadline(BUDGET+45., out)
    json_save(out/"PPO_START.json", dict(start_epoch=start_wall, compute_deadline_epoch=start_wall+BUDGET,
                                       hard_deadline_epoch=start_wall+BUDGET+45., budget_s=BUDGET,
                                       envs=env.n, rollout=ROLLOUT, ppo_settings=settings, **metadata["gpu"]))
    next_checkpoint = 240
    std = STD_START

    def status():
        current = model.state_dict()
        return dict(elapsed_s=time.monotonic()-start, start_epoch=start_wall, ppo_updates=updates, adam_steps=adam,
                    environment_steps=env_steps, physics_substeps=env_steps*8, ppo_settings=settings,
                    exploration_std=std, active_dr_stage=schedule.stage, full_dr_reset_probability=env.dr_probability,
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
                    mean = model.act_deterministic(obs, hist)
                    dist = Normal(mean, scale[:, None])
                    draw = dist.sample()
                    rollout.store(tick, obs=obs, history=hist, priv=priv, act=draw, log=dist.log_prob(draw).sum(1),
                                  value=model.evaluate_value(obs, hist, priv), mode=phase, scale=scale)
                    _, _, reward, done = env.step(draw)
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
                    phase, jump, drive = model.actor_body.components(obs, hist)
                    mean = torch.lerp(drive, jump, phase.sigmoid()[:, None]).clamp(-6., 6.)
                    dist = Normal(mean, data["scale"][rows, None])
                    change = (dist.log_prob(data["act"][rows]).sum(1)-data["log"][rows]).clamp(-12., 12.)
                    ratio = change.exp()
                    adv = advantage[rows]
                    policy_loss = -torch.minimum(ratio*adv, ratio.clamp(1.-CLIP, 1.+CLIP)*adv).mean()
                    value = model.evaluate_value(obs, hist, priv)
                    phase_loss = F.binary_cross_entropy_with_logits(phase, data["mode"][rows])
                    loss = policy_loss + F.smooth_l1_loss(value, returns[rows]) + .04*phase_loss
                    if not bool(loss.isfinite()):
                        raise FloatingPointError("Nonfinite R3 training objective")
                    optimizer.zero_grad(set_to_none=True)
                    loss.backward()
                    torch.nn.utils.clip_grad_norm_(trainable, 1., error_if_nonfinite=True)
                    optimizer.step()
                    adam += 1
                    minibatches += 1
                    kl = float((ratio-1.-change).detach().mean())
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
                    raise RuntimeError("Frozen R2 locomotion base changed")
                json_save(out/"LATEST.json", current)
                print("ppo", updates, "adam", adam, "seconds", round(current["elapsed_s"], 2),
                      "stage", schedule.stage, "full_dr", current["stats"]["full_dr_envs"],
                      "gate", schedule.last, flush=True)
                if updates == 1:
                    json_save(out/"FIRST_UPDATE.json", current)
                if current["elapsed_s"]>=next_checkpoint:
                    name = f"model_{next_checkpoint//60:03d}m.pt"
                    json_save(out/(name+".json"), save(model, optimizer, env, out, name, current))
                    next_checkpoint += 240
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
    parser.add_argument("--timing", type=Path, required=True)
    parser.add_argument("--initial", type=Path, required=True)
    parser.add_argument("--preflight", type=Path)
    args = parser.parse_args()
    args.out.mkdir(exist_ok=True, parents=True)
    initialized = False
    torch.set_num_threads(1)
    torch.manual_seed(SEED)
    wp.config.kernel_cache_dir = str(HERE/"cache/warp")
    try:
        gpu = binding()
        initialized = True
        initial, timing = (HERE/arg for arg in (args.initial, args.timing))
        report = json.loads(timing.read_text(encoding="utf-8"))
        seed_model = torch.load(initial, map_location="cpu", weights_only=False)
        if sha(PARENT_R2)!=R2_SHA or report["checkpoint_sha256"]!=R2_SHA or seed_model["metadata"]["parent_sha256"]!=R2_SHA:
            raise ValueError("R3 inputs must derive from the archived R2 checkpoint")
        metadata = dict(gpu=gpu, envs=ENVS, actor_inputs=[35, 420], action_dim=6, key_obs=30, policy_hz=50,
                        physics_hz=400, parent_sha256=R2_SHA, timing_sha256=sha(timing), initial_sha256=sha(initial),
                        source_sha256={name: sha(HERE/name) for name in SOURCES})
        json_save(args.out/"STARTUP.json", metadata)
        model = load_policy(initial, "cuda:0")
        del seed_model
        effective_timing = training_timing(report)
        json_save(args.out/"TRAINING_TIMING.json", {key: effective_timing[key] for key in (
            "speeds", "heights", "platform", "hurdle")})
        env = Jump360R3Gpu(ENVS, SEED, effective_timing)
        if args.mode=="probe":
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

