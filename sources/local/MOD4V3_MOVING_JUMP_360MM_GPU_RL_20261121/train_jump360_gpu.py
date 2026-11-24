"""Zero-update preflight and a single bounded PPO run for moving jump."""
from __future__ import annotations

from argparse import ArgumentParser
from collections import deque
import json
import math
import os
from pathlib import Path
import select
import signal
import time
import traceback

import mujoco_warp as mjw
import numpy as np
import torch
from torch.distributions import Normal
from torch.nn import functional as F
import warp as wp

from jump360_scene import HERE, PARENT, json_save, sha
from moe_jump_model import MoEJumpActorCritic

UUID = "GPU-c27eecbd-6838-7290-1cd2-37e34522213d"
EXPECTED_PARENT = "9bad1458faafa999192d4126863ae47d451ded903db6a2200a6fa8ade5674d9e"
ROLLOUT = 24
ENVS = 2048
BUDGET = 1500
EXPLORATION_START = .18
EXPLORATION_END = .06
PPO_LR = 1.6e-4
PPO_CLIP = .20
PPO_EPOCHS = 4
DR_STAGES = (0., .10, .25, .50, .75, 1.)
DEFAULT_TIMING = Path("evidence/JUMP360_R2_LEAD.json")


def digest_sources():
    return {name: sha(HERE/name) for name in ("train_jump360_gpu.py", "jump360_scene.py", "jump360_gpu.py")}


def binding():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != UUID or torch.cuda.device_count() != 1:
        raise RuntimeError("The only visible CUDA device must be the authorized GPU 1 UUID")
    properties = torch.cuda.get_device_properties(0)
    if str(properties.uuid).lower().removeprefix("gpu-") != UUID[4:]:
        raise RuntimeError("CUDA device UUID mismatch")
    return dict(uuid=UUID, physical_index=1, cuda_index=0, name=properties.name, memory_bytes=properties.total_memory)


def load(checkpoint):
    model = MoEJumpActorCritic.load_from_checkpoint(checkpoint, "cuda:0")
    return model.to("cuda:0")


def save(model, path, metadata, optimizer=None, env=None):
    checkpoint = {
        "model_type": "MOD4v3_MovingJump360",
        "obs_dim": 35, "hist_len": 12, "hist_dim": 420, "action_dim": 6, "jump_mode_bit_index": 30,
        "state_dict": model.state_dict(), "metadata": metadata,
    }
    if optimizer is not None:
        checkpoint.update(optimizer=optimizer.state_dict(), cpu_rng=torch.get_rng_state(),
                          cuda_rng=torch.cuda.get_rng_state(), reset_rng=env.rng.get_state())
    temp = path.with_suffix(".partial")
    with temp.open("wb") as stream:
        torch.save(checkpoint, stream)
        stream.flush()
        os.fsync(stream.fileno())
    temp.replace(path)
    return dict(checkpoint=path.name, sha256=sha(path), file_bytes=path.stat().st_size, **metadata)


def parameters(model):
    return [p for p in model.parameters() if p.requires_grad]


def fit(model, data, out):
    input_arrays = np.load(data)
    obs, hist, target = [torch.tensor(input_arrays[key], device="cuda:0", dtype=torch.float32)
                         for key in ("obs", "hist", "act")]
    jump = obs[:,30]>.5
    obs, hist, target = obs[jump], hist[jump], target[jump]
    sample_weight = torch.ones_like(obs[:,0])
    sample_weight += .8*((target[:,0]-obs[:,22]).abs()+(target[:,1]-obs[:,23]).abs()).clamp(0., 1.5)
    trainable = tuple(model.actor_body.e_jump.encoder.parameters()) + tuple(model.actor_body.e_jump.delta_head.parameters())
    optim = torch.optim.Adam(trainable, lr=9.e-5)
    train_indices = torch.arange(len(obs), device="cuda:0")
    out_info = dict(parent_sha256=EXPECTED_PARENT, demo_sha256=sha(data), frames=len(obs), ppo_updates=0)
    if len(obs) < 100:
        raise ValueError("Insufficient warm-start data")
    for epoch in range(34):
        if epoch == 23:
            optim.param_groups[0]["lr"] = 3.e-5
        shuffled = train_indices[torch.randperm(len(obs), device="cuda:0")]
        mse = 0.
        for rows in shuffled.split(512):
            action = model.actor_body.e_jump(obs[rows], hist[rows]).clamp(-6., 6.)
            loss = ((action-target[rows]).square().mean(dim=1)*sample_weight[rows]).mean()
            optim.zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(trainable, 1.)
            optim.step()
            mse += float(loss.detach())*len(rows)/len(obs)
        if epoch % 5 == 0:
            print("offline_epoch", epoch+1, "weighted_mse", mse)
        if epoch in (5, 13, 23, 33):
            name = f"model_bc_{epoch+1:03d}.pt"
            meta = dict(epoch=epoch+1, demo_weighted_mse=mse, **out_info)
            json_save(out/(name+".json"), save(model, out/name, meta))


def monitor_deadline(seconds, job):
    """The child watches the exact worker PID until its pipe closes."""
    read, write = os.pipe()
    pid = os.getpid()
    child = os.fork()
    if child == 0:
        os.close(write)
        try:
            read_ready, _, _ = select.select([read], [], [], seconds)
            if not read_ready:
                (job/"HARD_DEADLINE.txt").write_text(f"Worker {pid} exceeded {seconds}s\n")
                os.kill(pid, signal.SIGKILL)
        finally:
            os._exit(0)
    os.close(read)
    return child, write


def preflight(env, model, steps, out, metadata):
    before = {name: v.detach().clone() for name,v in model.state_dict().items()}
    single_env = env.n < ENVS
    obs, hist = env.obs, env.hist.flatten(1)
    reward_range = [float("inf"), -float("inf")]
    history_max = 0.
    start = time.monotonic()
    probes = []
    with torch.inference_mode():
        for i in range(steps):
            if i == steps//2:
                env.dr_probability = 1.
            means = model.act_deterministic(obs, hist)
            exploration = EXPLORATION_START * torch.randn_like(means)
            action = torch.where(obs[:, 30:31] > .5, means + exploration, means)
            obs, hist, reward, _ = env.step(action)
            values = (obs, hist, reward, means, env.p, env.v)
            if not all(bool(torch.isfinite(x).all()) for x in values):
                raise FloatingPointError(f"Nonfinite physics, action, history or reward at preflight step {i+1}")
            history_max = max(history_max, float((hist[:, -35:]-obs).abs().max()))
            reward_range[0] = min(reward_range[0], float(reward.min()))
            reward_range[1] = max(reward_range[1], float(reward.max()))
            if i == 0 or (i+1) % 50 == 0 or i+1 == steps:
                stats = dict(steps=i+1, elapsed_s=time.monotonic()-start, stats=env.statistics())
                probes.append(stats)
                json_save(out/"LATEST.json", stats)
                print("preflight", stats, flush=True)

    obs, hist, priv = obs.clone(), hist.clone(), env.extra().clone()
    select_rows = (obs[:,30]>0.).nonzero().flatten()
    if not len(select_rows):
        select_rows = torch.arange(min(env.n,128), device=env.device)
    obs = obs[select_rows[:256]].clone()
    obs[:,30] = 1.
    hist = hist[select_rows[:256]]
    priv = priv[select_rows[:256]]
    mean = model.actor_body.e_jump(obs,hist)
    loss = mean.square().mean() + model.evaluate_value(obs,hist,priv).square().mean() + model.ejump_log_std.mean()
    loss.backward()
    groups = {
        "encoder": list(model.actor_body.e_jump.encoder.parameters()),
        "jump_head": list(model.actor_body.e_jump.delta_head.parameters()),
        "critic": list(model.critic.parameters()), "jump_log_std": [model.ejump_log_std],
    }
    quality = {key: dict(finite=all(p.grad is not None and bool(p.grad.isfinite().all()) for p in params),
                         norm=float(sum(p.grad.square().sum() for p in params).sqrt()))
               for key, params in groups.items()}
    drift = max(float((v-before[name]).abs().max()) for name,v in model.state_dict().items())
    final_stats = env.statistics()
    samples_ok = single_env or (int(env.dr.sum())>0 and final_stats["triggered_samples"]>0
                                and all(sum(final_stats["results_0_dr_full_dr"][dr][kind][0] for dr in range(2)) > 0
                                        for kind in range(4)))
    fit_ok = all(item["finite"] and item["norm"] > 0 for item in quality.values())
    passed = bool(fit_ok and drift == 0. and history_max == 0. and samples_ok
                  and final_stats["nonfinite_world_resets"] == 0
                  and final_stats["max_contacts_global"] < final_stats["contact_capacity"]
                  and final_stats["max_constraints_per_world"] < final_stats["constraint_capacity"])
    result = dict(passed=passed, steps=steps, ppo_updates=0, optimizer_steps=0, changes=drift, max_history_error=history_max,
                  medley="full plant with physical platform and two physical hurdles", grad=quality,
                  reward_min_max=reward_range, seconds=time.monotonic()-start, final_stats=final_stats, **metadata)
    json_save(out/"PROBE.json", result)
    if not passed:
        raise RuntimeError("GPU preflight quality check failed")


class Rollout:
    def __init__(self, n):
        shapes = {"obs":(35,), "history":(420,), "priv":(14,), "act":(6,), "log":(), "value":(),
                  "reward":(), "done":()}
        self.data = {name: torch.zeros((ROLLOUT,n,*shape), device="cuda:0") for name,shape in shapes.items()}

    def store(self, step, **values):
        for key, value in values.items():
            self.data[key][step].copy_(value)

    def returns(self, last_value):
        values, rewards, dones = (self.data[k] for k in ("value","reward","done"))
        advantage = torch.zeros_like(values)
        next_advantage = torch.zeros_like(last_value)
        for i in reversed(range(ROLLOUT)):
            not_done = 1.-dones[i]
            delta = rewards[i]+.992*not_done*last_value-values[i]
            next_advantage = delta+.992*.95*not_done*next_advantage
            advantage[i] = next_advantage
            last_value = values[i]
        return advantage, advantage+values


def ppo(env, model, out, checkpoint, preflight_folder, metadata):
    if env.n != ENVS:
        raise ValueError("PPO requires all 2048 environments")
    probe = json.loads((preflight_folder/"PROBE.json").read_text())
    safe = json.loads((preflight_folder/"SAFE_CLOSED.json").read_text())
    if not (probe["passed"] and safe["cuda_synchronized"] and probe["steps"]==600 and
            probe["envs"]==env.n and probe["source_sha256"]==metadata["source_sha256"] and
            probe["warm_sha256"]==sha(checkpoint) and probe["timing_sha256"]==metadata["timing_sha256"]):
        raise RuntimeError("Matching 600-step zero-update preflight is required")

    # Preserve the base E0 and anneal exploration while training the jump actor and critic.
    model.ejump_log_std.requires_grad_(False)
    with torch.no_grad():
        model.ejump_log_std.fill_(math.log(EXPLORATION_START))
    trainable = parameters(model)
    optim = torch.optim.Adam(trainable, lr=PPO_LR)
    frozen = {k:v.detach().clone() for k,v in model.state_dict().items()
              if k=="e0_std" or k.startswith(("actor_body.e0.","actor_body.e_jump.loco_base."))}
    actor_initial = model.actor_body.e_jump.delta_head[-1].weight.detach().clone()
    data = Rollout(env.n)
    n_updates, n_steps, env_steps = 0, 0, 0
    durations = []
    metrics = {}
    dr_stage = 0
    dr_window = deque(maxlen=21)
    dr_window.append(np.zeros((2, 2)))
    dr_changes = []
    settings = dict(std_start=EXPLORATION_START, std_end=EXPLORATION_END, lr=PPO_LR,
                    clip=PPO_CLIP, epochs=PPO_EPOCHS, imitation_anchor_weight=0.)

    def mark():
        elapsed = time.monotonic()-start
        return dict(elapsed_s=elapsed, start_epoch=start_wall, stats=env.statistics(), ppo_updates=n_updates,
                    adam_steps=n_steps, env_steps=env_steps, simulation_substeps=8*env_steps,
                    actor_head_max_change=float((model.actor_body.e_jump.delta_head[-1].weight-actor_initial).detach().abs().max()),
                    active_dr_reset_probability=env.dr_probability, dr_promotions=dr_changes,
                    exploration_std=float(model.ejump_log_std[0].exp()), ppo_settings=settings, **metadata, **metrics)

    start_wall, start = time.time(), time.monotonic()
    deadline = start+BUDGET
    watchdog, pipe = monitor_deadline(BUDGET+45., out)
    json_save(out/"PPO_START.json", dict(start_epoch=start_wall, compute_deadline_epoch=start_wall+BUDGET,
                                       hard_deadline_epoch=start_wall+BUDGET+45., budget_s=BUDGET, envs=env.n,
                                       rollout=ROLLOUT, ppo_settings=settings, **metadata["gpu"]))
    next_check = 180
    completed_partial = False
    try:
        while time.monotonic() < deadline:
            if (out/"REQUEST_STOP").exists():
                break
            began = time.monotonic()
            progress = min(1., (began-start)/BUDGET)
            exploration_std = EXPLORATION_START + (EXPLORATION_END-EXPLORATION_START)*progress
            model.ejump_log_std.fill_(math.log(exploration_std))
            std = model.ejump_log_std.exp()
            with torch.no_grad():
                for t in range(ROLLOUT):
                    obs, history, priv = env.obs, env.hist.flatten(1), env.extra()
                    mean = model.act_deterministic(obs,history)
                    dist = Normal(mean,std)
                    active = obs[:,30]>.5
                    draw = torch.where(active[:,None],dist.sample(),mean)
                    value = model.evaluate_value(obs,history,priv)
                    data.store(t,obs=obs,history=history,priv=priv,act=draw,log=dist.log_prob(draw).sum(-1),value=value)
                    _, _, reward, done = env.step(draw)
                    data.store(t,reward=reward,done=done)
                    env_steps += env.n
                    if time.monotonic() >= deadline or (out/"REQUEST_STOP").exists():
                        completed_partial = True
                        break
                if completed_partial:
                    break
                if not bool(torch.isfinite(data.data["reward"]).all()):
                    raise RuntimeError("Nonfinite PPO rollout reward")
                end = model.evaluate_value(env.obs,env.hist.flatten(1),env.extra())
                adv, returns = data.returns(end)

            names = {key:tensor.flatten(0,1) for key,tensor in data.data.items()}
            adv, returns = adv.flatten(), returns.flatten()
            jump_mask = names["obs"][:,30]>.5
            if jump_mask.any():
                active_adv = adv[jump_mask]
                adv = (adv-active_adv.mean())/active_adv.std(unbiased=False).clamp_min(1.e-5)
            adv = adv.clamp(-8.,8.)
            total_loss = total_kl = 0.
            done_minibatches = 0
            for _ in range(PPO_EPOCHS):
                shuffle = torch.randperm(len(adv), device=env.device)
                for row in shuffle.chunk(4):
                    if time.monotonic() >= deadline or (out/"REQUEST_STOP").exists():
                        completed_partial = True
                        break
                    obs, history, priv = [names[key][row] for key in ("obs","history","priv")]
                    mean = model.act_deterministic(obs,history)
                    dist = Normal(mean,std)
                    log = dist.log_prob(names["act"][row]).sum(-1)
                    change = (log-names["log"][row]).clamp(-12.,12.)
                    ratio = change.exp()
                    mask = jump_mask[row].float()
                    denom = mask.sum().clamp_min(1.)
                    adv_row = adv[row]
                    policy = -(mask*torch.minimum(ratio*adv_row,ratio.clamp(1.-PPO_CLIP,1.+PPO_CLIP)*adv_row)).sum()/denom
                    value = model.evaluate_value(obs,history,priv)
                    critic = F.smooth_l1_loss(value,returns[row],beta=1.)
                    kl = ((ratio-1.-change)*mask).sum()/denom
                    loss = critic + policy
                    if not bool(torch.isfinite(loss)):
                        raise FloatingPointError("Nonfinite PPO loss")
                    optim.zero_grad(set_to_none=True)
                    loss.backward()
                    torch.nn.utils.clip_grad_norm_(trainable, 1., error_if_nonfinite=True)
                    optim.step()
                    n_steps += 1
                    done_minibatches += 1
                    total_loss += float(loss.detach())
                    total_kl += float(kl.detach())
                if completed_partial:
                    break
            if completed_partial:
                break
            n_updates += 1
            durations.append(time.monotonic()-began)
            if n_updates % 5 == 0 and dr_stage < len(DR_STAGES)-1:
                group = int(dr_stage > 0)
                counts = env.counters[group, :2][:, [0, 3]].cpu().numpy()
                recent = counts-dr_window[0]
                dr_window.append(counts)
                rates = recent[:, 1]/np.maximum(1., recent[:, 0])
                if np.all(recent[:, 0] >= (256, 128)) and np.all(rates >= (.20, .05)):
                    dr_stage += 1
                    env.dr_probability = DR_STAGES[dr_stage]
                    dr_changes.append(dict(ppo_update=n_updates, full_dr_probability=env.dr_probability,
                                           recent_trials=recent[:, 0].astype(int).tolist(), strict_rates=rates.tolist()))
                    dr_window.clear()
                    dr_window.append(env.counters[1, :2][:, [0, 3]].cpu().numpy())
            metrics = dict(loss=total_loss/done_minibatches, approximate_kl=total_kl/done_minibatches,
                           seconds_per_rollout=durations[-1], reward_mean=float(names["reward"].mean()),
                           sampled_jump_steps=int(jump_mask.sum()))
            status = mark()
            status["e0_parameter_max_change"] = max(float((model.state_dict()[k]-v).abs().max()) for k,v in frozen.items())
            if status["e0_parameter_max_change"] != 0.:
                raise RuntimeError("Frozen E0 changed")
            json_save(out/"LATEST.json", status)
            print("ppo", n_updates, "adam", n_steps, "seconds", round(status["elapsed_s"],2),
                  "rollout_s", round(durations[-1],2), "all_car_peak", status["stats"]["measured_all_car_peak_any_m"])
            if n_updates == 1:
                json_save(out/"FIRST_UPDATE.json", status)
            if status["actor_head_max_change"] > 0. and not (out/"FIRST_ACTOR_UPDATE.json").exists():
                json_save(out/"FIRST_ACTOR_UPDATE.json", status)
            if status["elapsed_s"] >= next_check and status["elapsed_s"] < BUDGET:
                name = f"model_{next_check//60:03d}m.pt"
                json_save(out/(name+".json"),save(model,out/name,status,optim,env))
                next_check += 180
        final = mark()
        final["compute_end_epoch"] = time.time()
        final["partial_rollout_or_update"] = completed_partial
        final["e0_parameter_max_change"] = max(float((model.state_dict()[k]-v).abs().max()) for k,v in frozen.items())
        final["end_reason"] = "requested" if (out/"REQUEST_STOP").exists() else "bounded training duration"
        final["warm_start_sha"] = sha(checkpoint)
        json_save(out/"FINAL.json",save(model,out/"model_final.pt",final,optim,env))
    finally:
        os.close(pipe)
        os.waitpid(watchdog,0)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--out",type=Path,required=True)
    parser.add_argument("--mode",choices=("warm","probe","train"),required=True)
    parser.add_argument("--checkpoint",type=Path,default=PARENT)
    parser.add_argument("--demo",type=Path)
    parser.add_argument("--preflight",type=Path,default=Path("evidence/jump360_r2_probe"))
    parser.add_argument("--timing",type=Path,default=DEFAULT_TIMING)
    parser.add_argument("--steps",type=int,default=600)
    parser.add_argument("--envs",type=int,default=ENVS)
    args = parser.parse_args()
    args.checkpoint = HERE / args.checkpoint
    if args.demo is not None:
        args.demo = HERE / args.demo
    args.out.mkdir(exist_ok=True,parents=True)
    torch.set_num_threads(1)
    torch.manual_seed(29115)
    wp.config.kernel_cache_dir = str(HERE/"cache/warp")
    initialized = False
    try:
        gpu = binding()
        initialized = True
        if sha(PARENT)!=EXPECTED_PARENT:
            raise RuntimeError("Unmodified parent jump checkpoint required")
        model = load(args.checkpoint)
        metadata = dict(gpu=gpu, source_sha256=digest_sources(), warm_sha256=sha(args.checkpoint),
                        actor_input_dimensions=[35,420], actor_output_dim=6, envs=args.envs, physics_hz=400,
                        leg_pd_hz=100, wheel_control_hz=400, policy_hz=50, simulator="MuJoCo Warp",
                        torch_version=str(torch.__version__), mjwarp_version=mjw.__version__)
        json_save(args.out/"STARTUP.json",metadata)
        if args.mode=="warm":
            fit(model,args.demo,args.out)
        else:
            from jump360_gpu import JumpGpu
            timing_path = HERE / args.timing
            timing = json.loads(timing_path.read_text(encoding="utf-8"))
            metadata["timing_sha256"] = sha(timing_path)
            env = JumpGpu(args.envs,29115,timing)
            metadata["native_model"] = dict(timestep=float(env.cpu.m.opt.timestep), mujoco_iterations=int(env.cpu.m.opt.iterations),
                                            body_count=env.cpu.m.nbody, qpos_dim=env.cpu.m.nq, action_dim=env.cpu.m.nu)
            if args.mode=="probe":
                preflight(env,model,args.steps,args.out,metadata)
            else:
                ppo(env,model,args.out,args.checkpoint,HERE/args.preflight,metadata)
    except BaseException:
        (args.out/"ERROR.txt").write_text(traceback.format_exc(),encoding="utf-8")
        raise
    finally:
        if initialized:
            torch.cuda.synchronize()
        json_save(args.out/"SAFE_CLOSED.json",dict(epoch=time.time(),cuda_synchronized=initialized,mode=args.mode))


if __name__=="__main__":
    main()
