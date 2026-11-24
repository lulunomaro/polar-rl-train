"""COMMANDER-AUTHORED & LOCKED Generalized Masked PPO Engine (DO NOT MODIFY!).

Shared by:
- Priority #1: E_stair_nav4d (459D input, IsaacLab 2048 envs)
- Priority #2: E_jump_unified (455D input, Warp 2048 envs)

Guarantees:
1. Strict GPU-0 UUID lock (GPU-16828f91-2b45-b646-8dc0-9481138e2842).
2. Mandatory 600-step 0-update PROBE.json + SAFE_CLOSED.json verification before PPO.
3. Bilaterally correlated Gaussian exploration (sample_symmetric_action / symmetric_action_log_prob).
4. 12-iteration Critic-only warmup before first Actor update.
5. Masked Teacher Anchor ONLY on valid nominal states (never pulling tall-stance jump,
   W-release flight, or approach/high-speed stair states back to old limitations!).
6. Graceful REQUEST_STOP & wall-clock guard support with frozen E0 0.0-drift check.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
import os
from pathlib import Path
import time
import torch

from unified_policies import sample_symmetric_action, symmetric_action_log_prob

UUID = "GPU-16828f91-2b45-b646-8dc0-9481138e2842"


def put(path: Path, obj: dict):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".partial")
    tmp.write_text(json.dumps(obj, indent=2), encoding="utf-8")
    tmp.replace(path)


def verify_device():
    assert os.environ.get("CUDA_VISIBLE_DEVICES") == UUID, f"Expected CUDA_VISIBLE_DEVICES={UUID}"
    assert torch.cuda.device_count() == 1, f"Expected 1 visible GPU, got {torch.cuda.device_count()}"
    actual = str(torch.cuda.get_device_properties(0).uuid).lower().removeprefix("gpu-")
    assert actual == UUID[4:].lower(), f"GPU UUID mismatch: {actual} != {UUID[4:]}"


def run_ppo(
    env,
    actor: torch.nn.Module,
    critic: torch.nn.Module,
    output: Path,
    seconds: int = 0,
    kind: str = "stair",
    probe_dir: Path | None = None,
    donor_meta: dict | None = None,
    lr_actor: float = 5.0e-5,
    lr_critic: float = 2.5e-4,
    rollout_len: int = 28,
):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    verify_device()
    torch.set_num_threads(1)

    device = env.device
    actor = actor.to(device)
    critic = critic.to(device)

    baseline_sd = {k: v.detach().clone() for k, v in actor.state_dict().items()}
    frozen_params = [(n, p, p.detach().clone()) for n, p in actor.named_parameters() if not p.requires_grad]
    if hasattr(env, "e0"):
        frozen_e0_init = {k: v.detach().clone() for k, v in env.e0.state_dict().items()}
    else:
        frozen_e0_init = {}

    def compute_frozen_drift() -> float:
        d1 = max([float((p - v).abs().max()) for _, p, v in frozen_params] + [0.0])
        d2 = (
            max([float((v - frozen_e0_init[k]).abs().max()) for k, v in env.e0.state_dict().items()] + [0.0])
            if frozen_e0_init
            else 0.0
        )
        return max(d1, d2)

    critic_steps = 0
    actor_updates = 0
    optimizer_steps = 0

    def get_inputs() -> torch.Tensor:
        return env.actor_input() if hasattr(env, "actor_input") else torch.cat((env.obs, env.hist.flatten(1)), dim=1)

    def get_priv(x: torch.Tensor) -> torch.Tensor:
        return torch.cat((x, env.extra()), dim=1)

    def get_active() -> torch.Tensor:
        return env.active_mask()

    def get_anchor_mask() -> torch.Tensor:
        return env.anchor_mask() if hasattr(env, "anchor_mask") else torch.zeros_like(env.active_mask())

    # --- MODE 1: 600-STEP ZERO-UPDATE PRECHECK PROBE ---
    if seconds == 0:
        t0 = time.time()
        history_error = 0.0
        finite = True
        actor.eval()
        critic.eval()
        for i in range(600):
            if i == 200:
                env.set_stage(1)
            elif i == 400:
                env.set_stage(2)
            with torch.no_grad():
                x = get_inputs()
                mean_act = actor(x)
                obs, hist_flat, reward, done = env.step(mean_act)
            finite &= bool(torch.isfinite(x).all() & torch.isfinite(mean_act).all() & torch.isfinite(reward).all())
            history_error = max(history_error, float((hist_flat[:, -35:] - obs).abs().max()))
            if (i + 1) % 100 == 0:
                snap = dict(steps=i + 1, elapsed_s=time.time() - t0, stats=env.statistics())
                put(output / "LATEST.json", snap)
                print("PROBE", i + 1, json.dumps(snap["stats"]), flush=True)

        # Gradient sanity check WITHOUT stepping optimizer
        actor.train()
        critic.train()
        x_sub = get_inputs()[:128].detach().clone()
        p_sub = get_priv(get_inputs())[:128].detach().clone()
        test_loss = actor(x_sub).square().mean() + critic(p_sub).square().mean()
        test_loss.backward()
        grad_finite = all(
            bool(torch.isfinite(p.grad).all()) for p in list(actor.parameters()) + list(critic.parameters()) if p.grad is not None
        )
        actor.zero_grad(set_to_none=True)
        critic.zero_grad(set_to_none=True)

        actor_drift = max(float((v - baseline_sd[k]).abs().max()) for k, v in actor.state_dict().items())
        f_drift = compute_frozen_drift()
        report = dict(
            passed=bool(finite and grad_finite and actor_drift == 0.0 and f_drift == 0.0 and history_error < 1e-6),
            kind=kind,
            steps=600,
            envs=2048,
            optimizer_steps=0,
            ppo_updates=0,
            actor_unchanged=(actor_drift == 0.0),
            e0_unchanged=(f_drift == 0.0),
            gradient_finite=grad_finite,
            max_history_error=history_error,
            statistics=env.statistics(),
            elapsed_s=time.time() - t0,
        )
        put(output / "PROBE.json", report)
        if not report["passed"]:
            raise RuntimeError(f"Zero-update probe failed: {report}")
        return

    # --- MODE 2: GUARDED PPO TRAINING ---
    assert 0 < seconds <= 1800, f"Invalid training budget: {seconds}"
    assert probe_dir is not None, "Training requires a completed zero-update --probe directory"
    probe_json = json.loads((Path(probe_dir) / "PROBE.json").read_text(encoding="utf-8"))
    closed_json = json.loads((Path(probe_dir) / "SAFE_CLOSED.json").read_text(encoding="utf-8"))
    assert probe_json["passed"] and probe_json["steps"] == 600 and probe_json["optimizer_steps"] == 0
    assert closed_json["scene_closed"]

    teacher = copy.deepcopy(actor).eval().requires_grad_(False)

    init_std = [0.042, 0.042, 0.042, 0.042, 0.075, 0.075] if kind == "stair" else [0.055, 0.055, 0.055, 0.055, 0.085, 0.085]
    logstd = torch.nn.Parameter(torch.tensor(init_std, dtype=torch.float32, device=device).log())
    trainable_actor = [p for p in actor.parameters() if p.requires_grad]
    opt_actor = torch.optim.Adam([{"params": trainable_actor, "lr": lr_actor}, {"params": [logstd], "lr": lr_actor * 0.5}])
    opt_critic = torch.optim.Adam(critic.parameters(), lr=lr_critic)

    def save_ckpt(name: str, steps_done: int, elapsed_s: float) -> dict:
        f_drift = compute_frozen_drift()
        if hasattr(actor, "verify_zero_e0_drift"):
            actor.verify_zero_e0_drift()
        assert f_drift == 0.0, f"Frozen E0 drifted by {f_drift}!"
        meta = dict(
            steps=steps_done,
            ppo_updates=actor_updates,
            critic_updates=critic_steps,
            optimizer_steps=optimizer_steps,
            elapsed_s=elapsed_s,
            envs=2048,
            kind=kind,
            actor_inputs=459 if kind == "stair" else 455,
            std=logstd.detach().exp().cpu().tolist(),
            physical_hz=400,
            leg_pd_hz=100,
            wheel_hz=400,
            policy_hz=50,
            gpu_uuid=UUID,
            frozen_e0_drift=f_drift,
            statistics=env.statistics(),
        )
        payload = dict(
            format=f"mod4v3_commander_{kind}_v2",
            actor=actor.state_dict(),
            critic=critic.state_dict(),
            logstd=logstd.detach().cpu(),
            metadata=meta,
            donor_meta=donor_meta,
        )
        path = output / name
        tmp = path.with_suffix(".partial")
        torch.save(payload, tmp)
        tmp.replace(path)
        sha = hashlib.sha256(path.read_bytes()).hexdigest()
        put(output / f"{name}.json", dict(meta, sha256=sha))
        return meta

    save_ckpt("model_step000.pt", 0, 0.0)
    start = time.time()
    hard = start + seconds
    put(
        output / "TRAIN_START.json",
        dict(epoch=start, hard_stop_epoch=hard, budget_s=seconds, soft_stop_epoch=hard - 40.0, gpu_uuid=UUID, kind=kind),
    )

    next_save = 240.0  # Save checkpoint every 4 minutes for fine-grained CPU MuJoCo screening!
    iteration = 0
    steps = 0
    warmup_iters = 12

    while time.time() < hard - 40.0 and not (output / "REQUEST_STOP").exists():
        elapsed = time.time() - start
        frac = elapsed / max(float(seconds), 1.0)
        # Progressive 4-stage DR schedule: 0% -> 25% -> 50% -> 100%
        stage = 0 if frac < 0.22 else (1 if frac < 0.48 else (2 if frac < 0.75 else 3))
        env.set_stage(stage)

        buf = {k: [] for k in ("x", "priv", "act", "logp", "val", "rew", "done", "active", "anc")}
        actor.eval()
        critic.eval()
        std_now = logstd.detach().exp()

        for _ in range(rollout_len):
            if time.time() >= hard - 35.0 or (output / "REQUEST_STOP").exists():
                break
            with torch.no_grad():
                x = get_inputs().clone()
                priv = get_priv(x).clone()
                active = get_active().clone()
                anc = get_anchor_mask().clone()
                mean = actor(x)
                sampled = sample_symmetric_action(mean, std_now)
                # Only inject exploration noise on active expert frames; keep cruise frames deterministic!
                exec_act = torch.where(active[:, None], sampled, mean)
                logp = symmetric_action_log_prob(exec_act, mean, std_now)
                val = critic(priv)
                _, _, rew, done = env.step(exec_act)
                for k, v in zip(buf, (x, priv, exec_act, logp, val, rew.clone(), done.clone(), active, anc)):
                    buf[k].append(v)
            steps += 1

        if len(buf["x"]) < rollout_len:
            break

        with torch.no_grad():
            next_val = critic(get_priv(get_inputs()))
        gae = torch.zeros_like(next_val)
        adv_list = []
        ret_list = []
        for t in reversed(range(rollout_len)):
            not_done = (~buf["done"][t]).float()
            delta = buf["rew"][t] + 0.99 * not_done * next_val - buf["val"][t]
            gae = delta + 0.99 * 0.95 * not_done * gae
            adv_list.insert(0, gae.clone())
            ret_list.insert(0, gae + buf["val"][t])
            next_val = buf["val"][t]

        flat = {k: torch.cat(v, dim=0) for k, v in buf.items()}
        ret = torch.cat(ret_list, dim=0)
        adv = torch.cat(adv_list, dim=0)
        mask = flat["active"]
        sel_adv = adv[mask]
        if sel_adv.numel() > 16:
            adv = (adv - sel_adv.mean()) / sel_adv.std().clamp_min(1.0e-5)

        actor.train()
        critic.train()
        vloss_sum = 0.0
        aloss_sum = 0.0
        anchor_decay = max(0.0, 1.0 - frac / 0.65)  # Decays to 0 after 65% of run

        for _ in range(3):
            perm = torch.randperm(ret.shape[0], device=device)
            for mb_ids in perm.chunk(4):
                if time.time() >= hard - 30.0:
                    break
                v_pred = critic(flat["priv"][mb_ids])
                # Huber-like clipped value loss prevents rare -25 spike from destabilizing critic
                lv = torch.nn.functional.smooth_l1_loss(v_pred, ret[mb_ids], beta=5.0)
                opt_critic.zero_grad(set_to_none=True)
                lv.backward()
                torch.nn.utils.clip_grad_norm_(critic.parameters(), 1.0, error_if_nonfinite=True)
                opt_critic.step()
                critic_steps += 1
                optimizer_steps += 1
                vloss_sum += float(lv.detach())

                if iteration < warmup_iters:
                    continue

                chosen = mb_ids[mask[mb_ids]]
                if chosen.numel() < 32:
                    continue

                std_cur = logstd.exp()
                mean_cur = actor(flat["x"][chosen])
                new_logp = symmetric_action_log_prob(flat["act"][chosen], mean_cur, std_cur)
                ratio = (new_logp - flat["logp"][chosen]).clamp(-10.0, 10.0).exp()
                adv_c = adv[chosen]
                surr1 = -adv_c * ratio
                surr2 = -adv_c * ratio.clamp(0.88, 1.12)
                pg_loss = torch.maximum(surr1, surr2).mean()

                anc_sub = flat["anc"][chosen]
                if anchor_decay > 0.0 and bool(anc_sub.any()):
                    with torch.no_grad():
                        prior = teacher(flat["x"][chosen][anc_sub])
                    anc_loss = 0.010 * anchor_decay * (mean_cur[anc_sub] - prior).square().mean()
                else:
                    anc_loss = pg_loss.new_zeros(())

                ent_bonus = std_cur.log().mean()
                loss_a = pg_loss + anc_loss - 1.5e-4 * ent_bonus

                opt_actor.zero_grad(set_to_none=True)
                loss_a.backward()
                torch.nn.utils.clip_grad_norm_([*trainable_actor, logstd], 0.75, error_if_nonfinite=True)
                opt_actor.step()

                with torch.no_grad():
                    if kind == "stair":
                        logstd[:4].clamp_(math.log(0.015), math.log(0.075))
                        logstd[4:].clamp_(math.log(0.025), math.log(0.120))
                    else:
                        logstd[:4].clamp_(math.log(0.018), math.log(0.090))
                        logstd[4:].clamp_(math.log(0.025), math.log(0.140))

                optimizer_steps += 1
                aloss_sum += float(loss_a.detach())

        iteration += 1
        if iteration > warmup_iters:
            actor_updates += 1

        elapsed = time.time() - start
        report = dict(
            iteration=iteration,
            steps=steps,
            elapsed_s=elapsed,
            ppo_updates=actor_updates,
            critic_updates=critic_steps,
            optimizer_steps=optimizer_steps,
            active_fraction=float(mask.float().mean()),
            dr_stage=stage,
            value_loss=vloss_sum / 12.0,
            actor_loss=aloss_sum / 12.0,
            std=logstd.detach().exp().cpu().tolist(),
            frozen_e0_drift=compute_frozen_drift(),
            stats=env.statistics(),
        )
        put(output / "LATEST.json", report)
        print("PPO", json.dumps(report), flush=True)

        if iteration == warmup_iters + 1:
            save_ckpt("model_first_actor.pt", steps, elapsed)
        if elapsed >= next_save:
            save_ckpt(f"model_{int(next_save // 60):03d}m.pt", steps, elapsed)
            next_save += 240.0

    final_meta = save_ckpt("model_final.pt", steps, time.time() - start)
    changed = any(not torch.equal(v, baseline_sd[k]) for k, v in actor.state_dict().items() if any(k.endswith(n) for n, p in actor.named_parameters() if p.requires_grad))
    put(
        output / "TRAIN_COMPLETE.json",
        dict(
            final_meta,
            iterations=iteration,
            hard_stop_epoch=hard,
            finish_epoch=time.time(),
            bounded=(time.time() <= hard),
            actual_actor_changed=changed,
        ),
    )
