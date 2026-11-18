# SPDX-License-Identifier: MIT
"""Stage 2: Genuine Closed-Loop PPO RL Fine-Tuning (0-DR -> Progressive DR -> Full-DR).

Trains PureNeuralJumpExpert (E_jump: obs_35 + obs_history_420 -> act_6) + Asymmetric Value Critic
inside MoEJumpActorCritic while keeping E0 (c874) strictly frozen (0.0 parameter drift):
  1. Critic-Only Warmup (Iters 1..8): Calibrates privileged critic normalizer and trains Value Critic
     for 8 iterations before enabling actor updates, preventing cold-critic GAE shock.
  2. Masked On-Policy PPO + Progressive DR (Iters 9..54):
       - Iters  9..22: dr_scale = 0.00 (0-DR nominal clearance, attitude & hurdle optimization)
       - Iters 23..38: dr_scale = 0.50 (50% progressive DR + physical hurdles)
       - Iters 39..54: dr_scale = 1.00 (100% Full-DR: mass ±12%, COM ±2.5cm, friction [0.55,1.15],
                       PD ±12%, motor effort ±10%, 0-20ms delay + 14-20cm physical hurdles)
  3. Masked Trust Region & Anti-Collapse Regularization:
       - Advantages, Clipped Surrogate, Entropy & Adaptive KL (target_kl=0.015) computed strictly on
         active E_jump steps (obs[:, 30] > 0.5) so E0 steps never dilute KL measurement.
       - Bilateral Symmetry Loss (pi(mirror(s)) == mirror(pi(s))) + Clean Trajectory Anchor MSE.
  4. Saves weights/model_rl_best.pt, weights/model_rl_final.pt, and evidence/ppo_training_log.json.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import time
from typing import Any

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np
import torch
import torch.nn as nn

from moe_jump_model import (
    ACT_DIM,
    HERE,
    HIST_DIM,
    JUMP_MODE_BIT_INDEX,
    MoEJumpActorCritic,
    OBS_DIM,
    PRIV_CRITIC_DIM,
    StatefulMoEJumpActor,
)
from rl_jump_env import Mod4v3RLJumpEnv, SubprocVecJumpEnv


def evaluate_validation_suite(model: MoEJumpActorCritic, dr_scale: float, base_seed: int = 9000) -> dict[str, Any]:
    """Deterministic pure-neural evaluation (ZERO teacher calls, ZERO privileged actor inputs)."""
    model.eval()
    actor = StatefulMoEJumpActor(model)
    cases = [
        ("stand_0p0", 0.0, (1.6,), 4.6, []),
        ("move_0p4", 0.4, (1.6,), 4.6, []),
        ("move_0p8", 0.8, (1.6,), 4.6, []),
        ("move_1p2", 1.2, (1.6,), 4.6, []),
        ("rev_m0p5", -0.5, (1.6,), 4.6, []),
        ("multi3x_0p8", 0.8, (1.4, 3.3, 5.2), 7.2, []),
        ("hurdle18cm_1p20", 1.20, (1.6,), 4.6, None),  # None -> auto-computed hurdle apex_x
    ]

    per_case: dict[str, Any] = {}
    surv_cnt = 0
    clean_cnt = 0
    rims: list[float] = []
    total_eps = 0

    seeds = (0, 1) if dr_scale > 0.0 else (0,)
    for c_idx, (name, v_cmd, j_times, max_s, hurdles_spec) in enumerate(cases):
        case_surv = 0
        case_clean = 0
        case_rims = []
        case_h_clr = 0
        case_h_tot = 0
        for s_off in seeds:
            env = Mod4v3RLJumpEnv(seed=base_seed + c_idx * 31 + s_off)
            if hurdles_spec is None:
                # Physical 18cm box hurdle placed under ballistic jump apex
                hx = float(env.hurdle_apex_x(v_cmd, j_times[0]))
                hurdles = [(hx, 0.18)]
            else:
                hurdles = hurdles_spec
            st = env.reset(
                dr_scale=dr_scale,
                v_cmd=v_cmd,
                h_nom=0.28,
                jump_times=j_times,
                max_episode_s=max_s,
                hurdles=hurdles,
            )
            actor.reset_history()
            # Prime 12-step history with initial obs, then step using ONLY obs_35 -> act_6
            actor.queue.reset(torch.from_numpy(st["obs"]).unsqueeze(0))
            first_step = True
            while True:
                obs_t = torch.from_numpy(st["obs"]).unsqueeze(0)
                if first_step:
                    with torch.inference_mode():
                        hist_t = actor.queue.buffer.flatten(-2)
                        act = model.act_deterministic(obs_t, hist_t)[0].numpy()
                    first_step = False
                else:
                    act = actor(obs_t)[0].numpy()
                st, _r, done, info = env.step(act)
                if done:
                    total_eps += 1
                    ok = info["fell_reason"] == "" and info["ep_completed_jumps"] >= info["ep_expected_jumps"]
                    no_scrape = (
                        info["ep_guide_force_N"] < 1.0
                        and info["ep_chassis_force_N"] < 1.0
                        and info["ep_hurdle_hit_N"] < 1.0
                    )
                    if ok:
                        surv_cnt += 1
                        case_surv += 1
                        rims.append(info["ep_peak_rim_cm"])
                        case_rims.append(info["ep_peak_rim_cm"])
                    if ok and no_scrape:
                        clean_cnt += 1
                        case_clean += 1
                    case_h_clr += info["hurdles_cleared"]
                    case_h_tot += info["hurdles_total"]
                    break
        per_case[name] = {
            "pass": f"{case_surv}/{len(seeds)}",
            "clean": f"{case_clean}/{len(seeds)}",
            "mean_rim_cm": round(float(np.mean(case_rims)), 2) if case_rims else 0.0,
            "hurdles": f"{case_h_clr}/{case_h_tot}" if case_h_tot > 0 else "-",
        }

    surv_rate = surv_cnt / max(1, total_eps)
    clean_rate = clean_cnt / max(1, total_eps)
    mean_rim = float(np.mean(rims)) if rims else 0.0
    score = 100.0 * surv_rate + 45.0 * clean_rate + 1.2 * mean_rim
    return {
        "dr_scale": dr_scale,
        "survival_rate": round(surv_rate, 4),
        "clean_zero_scrape_rate": round(clean_rate, 4),
        "mean_peak_rim_cm": round(mean_rim, 2),
        "composite_score": round(score, 3),
        "cases": per_case,
    }


def curriculum_dr_scale(iteration: int) -> float:
    if iteration <= 8:
        return 0.00  # Critic warmup aligned with initial 0-DR distribution
    if iteration <= 16:
        return 0.00  # Stage 2A: 0-DR nominal PPO refinement
    if iteration <= 26:
        return 0.50  # Stage 2B: 50% progressive DR + hurdles
    return 1.00  # Stage 2C: 100% Full-DR + hurdles


def main() -> None:
    t0 = time.perf_counter()
    torch.manual_seed(20261118)
    np.random.seed(20261118)
    torch.set_num_threads(4)

    bc_ckpt = HERE / "weights/model_bc_dagger.pt"
    anchor_path = HERE / "trajectories/clean_jump_anchor.pt"
    if not bc_ckpt.exists() or not anchor_path.exists():
        raise FileNotFoundError("Run stage1_bc_dagger.py first to create model_bc_dagger.pt and clean_jump_anchor.pt")

    model = MoEJumpActorCritic.load_from_checkpoint(bc_ckpt, device="cpu")
    # Calibrated low-variance exploration std ([0.020, 0.030]) paired with 6e-6 Adam trust-region step
    with torch.no_grad():
        model.ejump_log_std.copy_(
            torch.tensor([0.020, 0.020, 0.020, 0.020, 0.030, 0.030], dtype=torch.float32).log()
        )
    model.verify_zero_e0_drift()

    anchor_data = torch.load(anchor_path, map_location="cpu", weights_only=False)
    anc_obs_all: torch.Tensor = anchor_data["obs"].clone()
    anc_hist_all: torch.Tensor = anchor_data["hist"].clone()
    anc_act_all: torch.Tensor = anchor_data["act"].clone()

    # Strict parameter group isolation: E0 and loco_base are excluded and frozen
    actor_params = [
        p
        for n, p in list(model.actor_body.e_jump.named_parameters()) + [("ejump_log_std", model.ejump_log_std)]
        if p.requires_grad
    ]
    critic_params = [p for p in model.critic.parameters() if p.requires_grad]

    actor_opt = torch.optim.Adam(actor_params, lr=6.0e-6, eps=1e-5)
    critic_opt = torch.optim.Adam(critic_params, lr=7.0e-4, eps=1e-5)

    num_envs = 14
    steps_per_iter = 256  # 14 * 256 = 3,584 steps/iter (36 iters = 129,024 closed-loop steps)
    total_iters = 36
    critic_warmup_iters = 8
    gamma = 0.99
    gae_lambda = 0.95
    clip_eps = 0.12
    ppo_epochs = 4
    minibatch_size = 512
    target_kl = 0.012

    # Baseline Stage-1 validation before any PPO updates
    val0_0dr = evaluate_validation_suite(model, dr_scale=0.0)
    val0_fdr = evaluate_validation_suite(model, dr_scale=1.0)
    best_combined_score = 0.45 * val0_0dr["composite_score"] + 0.55 * val0_fdr["composite_score"]
    print(
        f"[Init BC+DAgger] 0-DR={val0_0dr['survival_rate']*100:.1f}% surv / {val0_0dr['mean_peak_rim_cm']:.2f}cm | "
        f"Full-DR={val0_fdr['survival_rate']*100:.1f}% surv / {val0_fdr['mean_peak_rim_cm']:.2f}cm | "
        f"score={best_combined_score:.2f}",
        flush=True,
    )

    best_ckpt_path = HERE / "weights/model_rl_best.pt"
    final_ckpt_path = HERE / "weights/model_rl_final.pt"
    best_sha = model.save_checkpoint(
        best_ckpt_path,
        metadata={"stage": "ppo_init_from_bc_dagger", "val_0dr": val0_0dr, "val_fulldr": val0_fdr},
    )
    best_iter = 0

    vec_env = SubprocVecJumpEnv(num_envs=num_envs, base_seed=2026)
    torch.set_num_threads(4)
    cur_dr = curriculum_dr_scale(1)
    obs_np, hist_np, priv_np = vec_env.reset_random(dr_scale=cur_dr)

    # Pre-allocate rollout storage
    buf_obs = np.zeros((steps_per_iter, num_envs, OBS_DIM), dtype=np.float32)
    buf_hist = np.zeros((steps_per_iter, num_envs, HIST_DIM), dtype=np.float32)
    buf_priv = np.zeros((steps_per_iter, num_envs, PRIV_CRITIC_DIM), dtype=np.float32)
    buf_raw_act = np.zeros((steps_per_iter, num_envs, ACT_DIM), dtype=np.float32)
    buf_logp = np.zeros((steps_per_iter, num_envs), dtype=np.float32)
    buf_val = np.zeros((steps_per_iter, num_envs), dtype=np.float32)
    buf_rew = np.zeros((steps_per_iter, num_envs), dtype=np.float32)
    buf_done = np.zeros((steps_per_iter, num_envs), dtype=np.float32)
    buf_timeout_val = np.zeros((steps_per_iter, num_envs), dtype=np.float32)

    training_log: dict[str, Any] = {
        "init_validation": {"val_0dr": val0_0dr, "val_fulldr": val0_fdr, "combined_score": round(best_combined_score, 3)},
        "iterations": [],
        "validations": [],
    }

    try:
        for it in range(1, total_iters + 1):
            it_t0 = time.perf_counter()
            new_dr = curriculum_dr_scale(it)
            if abs(new_dr - cur_dr) > 1e-6:
                cur_dr = new_dr
                vec_env.set_dr_scale(cur_dr)

            model.eval()
            ep_rims: list[float] = []
            ep_surv: list[float] = []
            ep_clean: list[float] = []
            ep_rews_step: list[float] = []

            for t in range(steps_per_iter):
                buf_obs[t] = obs_np
                buf_hist[t] = hist_np
                buf_priv[t] = priv_np

                with torch.no_grad():
                    obs_t = torch.from_numpy(obs_np)
                    hist_t = torch.from_numpy(hist_np)
                    priv_t = torch.from_numpy(priv_np)
                    exec_act_t, raw_act_t, logp_t, val_t = model.sample_action_and_value(obs_t, hist_t, priv_t)

                buf_raw_act[t] = raw_act_t.numpy()
                buf_logp[t] = logp_t.numpy()
                buf_val[t] = val_t.numpy()

                obs_np, hist_np, priv_np, rews, dones, infos = vec_env.step(exec_act_t.numpy())
                buf_rew[t] = rews
                buf_done[t] = dones.astype(np.float32)
                buf_timeout_val[t] = 0.0
                ep_rews_step.append(float(rews.mean()))

                for env_i, inf in enumerate(infos):
                    if inf.get("terminal_reset", False):
                        fell = inf["fell_reason"] != ""
                        ep_surv.append(0.0 if fell else 1.0)
                        if not fell:
                            ep_rims.append(float(inf["ep_peak_rim_cm"]))
                            clean = (
                                inf["ep_guide_force_N"] < 1.0
                                and inf["ep_chassis_force_N"] < 1.0
                                and inf["ep_hurdle_hit_N"] < 1.0
                            )
                            ep_clean.append(1.0 if clean else 0.0)
                            if "terminal_state" in inf:
                                ts = inf["terminal_state"]
                                with torch.no_grad():
                                    tv = model.evaluate_value(
                                        torch.from_numpy(ts["obs"]).unsqueeze(0),
                                        torch.from_numpy(ts["hist"]).unsqueeze(0),
                                        torch.from_numpy(ts["priv"]).unsqueeze(0),
                                    ).item()
                                buf_timeout_val[t, env_i] = float(tv)

            # Fit privileged critic input normalizer on Iteration 1
            if it == 1:
                flat_priv0 = torch.from_numpy(buf_priv.reshape(-1, PRIV_CRITIC_DIM))
                model.critic.priv_mean.copy_(flat_priv0.mean(dim=0))
                model.critic.priv_scale.copy_(flat_priv0.std(dim=0) + 0.05)
                # Re-evaluate buffer values with calibrated normalizer
                with torch.no_grad():
                    for t in range(steps_per_iter):
                        buf_val[t] = model.evaluate_value(
                            torch.from_numpy(buf_obs[t]),
                            torch.from_numpy(buf_hist[t]),
                            torch.from_numpy(buf_priv[t]),
                        ).numpy()

            with torch.no_grad():
                next_val = model.evaluate_value(
                    torch.from_numpy(obs_np),
                    torch.from_numpy(hist_np),
                    torch.from_numpy(priv_np),
                ).numpy()

            # Compute exact GAE-Lambda advantages with timeout bootstrap preservation
            adv_np = np.zeros_like(buf_rew)
            last_gae = np.zeros(num_envs, dtype=np.float32)
            for t in reversed(range(steps_per_iter)):
                next_v = next_val if t == steps_per_iter - 1 else buf_val[t + 1]
                nonterm = 1.0 - buf_done[t]
                bootstrap_v = nonterm * next_v + buf_done[t] * buf_timeout_val[t]
                delta = buf_rew[t] + gamma * bootstrap_v - buf_val[t]
                last_gae = delta + gamma * gae_lambda * nonterm * last_gae
                adv_np[t] = last_gae
            ret_np = adv_np + buf_val

            # Flatten batch
            N = steps_per_iter * num_envs
            f_obs = torch.from_numpy(buf_obs.reshape(N, OBS_DIM))
            f_hist = torch.from_numpy(buf_hist.reshape(N, HIST_DIM))
            f_priv = torch.from_numpy(buf_priv.reshape(N, PRIV_CRITIC_DIM))
            f_act = torch.from_numpy(buf_raw_act.reshape(N, ACT_DIM))
            f_logp = torch.from_numpy(buf_logp.reshape(N))
            f_adv = torch.from_numpy(adv_np.reshape(N))
            f_ret = torch.from_numpy(ret_np.reshape(N))
            f_val_old = torch.from_numpy(buf_val.reshape(N))

            model.train()
            if it <= critic_warmup_iters:
                # Stage 2 Warmup: Train Value Critic ONLY (0 actor gradient steps!)
                v_losses = []
                for _ in range(10):
                    perm = torch.randperm(N)
                    for start in range(0, N, minibatch_size):
                        mb = perm[start : start + minibatch_size]
                        v_pred = model.evaluate_value(f_obs[mb], f_hist[mb], f_priv[mb])
                        v_loss = 0.5 * ((v_pred - f_ret[mb]) ** 2).mean()
                        critic_opt.zero_grad()
                        v_loss.backward()
                        nn.utils.clip_grad_norm_(critic_params, 1.0)
                        critic_opt.step()
                        v_losses.append(float(v_loss.item()))
                mean_pg = mean_kl = mean_sym = mean_anc = 0.0
                mean_vf = float(np.mean(v_losses))
            else:
                # Cosine decay actor LR gently across PPO iterations (6e-6 -> 2.7e-6)
                prog = (it - critic_warmup_iters) / max(1, total_iters - critic_warmup_iters)
                cur_actor_lr = 6.0e-6 * (0.45 + 0.55 * 0.5 * (1.0 + np.cos(np.pi * prog)))
                cur_critic_lr = 4.5e-4
                for pg in actor_opt.param_groups:
                    pg["lr"] = float(cur_actor_lr)
                for pg in critic_opt.param_groups:
                    pg["lr"] = float(cur_critic_lr)

                # Normalize advantages strictly across active E_jump steps
                jump_all_mask = f_obs[:, JUMP_MODE_BIT_INDEX] > 0.5
                if int(jump_all_mask.sum()) > 32:
                    j_adv = f_adv[jump_all_mask]
                    f_adv_norm = (f_adv - j_adv.mean()) / (j_adv.std() + 1e-6)
                else:
                    f_adv_norm = (f_adv - f_adv.mean()) / (f_adv.std() + 1e-6)

                anchor_coef = float(0.28 - 0.08 * prog)
                pg_losses, vf_losses, kl_list, sym_list, anc_list = [], [], [], [], []
                kl_stop = False

                for _ep in range(ppo_epochs):
                    if kl_stop:
                        break
                    perm = torch.randperm(N)
                    for start in range(0, N, minibatch_size):
                        mb = perm[start : start + minibatch_size]
                        mb_obs = f_obs[mb]
                        mb_hist = f_hist[mb]
                        mb_priv = f_priv[mb]

                        # 1. Critic update (trains across ALL steps)
                        v_pred = model.evaluate_value(mb_obs, mb_hist, mb_priv)
                        v_clipped = f_val_old[mb] + (v_pred - f_val_old[mb]).clamp(-0.5, 0.5)
                        vf_loss = 0.5 * torch.max((v_pred - f_ret[mb]) ** 2, (v_clipped - f_ret[mb]) ** 2).mean()
                        critic_opt.zero_grad()
                        vf_loss.backward()
                        nn.utils.clip_grad_norm_(critic_params, 1.0)
                        critic_opt.step()
                        vf_losses.append(float(vf_loss.item()))

                        # 2. Actor update (strictly on active E_jump steps!)
                        j_sub = mb_obs[:, JUMP_MODE_BIT_INDEX] > 0.5
                        if int(j_sub.sum()) < 16:
                            continue

                        j_obs = mb_obs[j_sub]
                        j_hist = mb_hist[j_sub]
                        j_priv = mb_priv[j_sub]
                        j_act = f_act[mb][j_sub]
                        j_old_logp = f_logp[mb][j_sub]
                        j_adv_mb = f_adv_norm[mb][j_sub]

                        new_logp, entropy, _v_unused, _mean = model.evaluate_actions(j_obs, j_hist, j_priv, j_act)
                        log_ratio = new_logp - j_old_logp
                        ratio = log_ratio.exp()
                        with torch.no_grad():
                            approx_kl = float(((ratio - 1.0) - log_ratio).mean().item())
                        kl_list.append(approx_kl)

                        if approx_kl > 1.5 * target_kl:
                            kl_stop = True
                            break

                        surr1 = ratio * j_adv_mb
                        surr2 = ratio.clamp(1.0 - clip_eps, 1.0 + clip_eps) * j_adv_mb
                        pg_loss = -torch.min(surr1, surr2).mean()
                        ent_loss = -0.001 * entropy.mean()
                        sym_loss = 0.35 * model.symmetry_loss(j_obs, j_hist)

                        # Clean trajectory anchor batch to prevent crouch/tuck collapse under heavy DR
                        anc_idx = torch.randint(0, len(anc_obs_all), (min(256, len(anc_obs_all)),))
                        anc_pred = model.actor_body.e_jump(anc_obs_all[anc_idx], anc_hist_all[anc_idx])
                        anc_loss = anchor_coef * ((anc_pred - anc_act_all[anc_idx]) ** 2).mean()

                        actor_loss = pg_loss + ent_loss + sym_loss + anc_loss
                        actor_opt.zero_grad()
                        actor_loss.backward()
                        nn.utils.clip_grad_norm_(actor_params, 0.5)
                        actor_opt.step()

                        pg_losses.append(float(pg_loss.item()))
                        sym_list.append(float(sym_loss.item()))
                        anc_list.append(float(anc_loss.item()))

                mean_pg = float(np.mean(pg_losses)) if pg_losses else 0.0
                mean_vf = float(np.mean(vf_losses)) if vf_losses else 0.0
                mean_kl = float(np.mean(kl_list)) if kl_list else 0.0
                mean_sym = float(np.mean(sym_list)) if sym_list else 0.0
                mean_anc = float(np.mean(anc_list)) if anc_list else 0.0

            # Enforce zero E0 drift contract every single iteration
            e0_drift = model.verify_zero_e0_drift()

            it_rec = {
                "iter": it,
                "mode": "critic_warmup" if it <= critic_warmup_iters else "ppo_actor_critic",
                "dr_scale": cur_dr,
                "mean_step_reward": round(float(np.mean(ep_rews_step)), 4),
                "rollout_survival_rate": round(float(np.mean(ep_surv)), 4) if ep_surv else 1.0,
                "rollout_clean_rate": round(float(np.mean(ep_clean)), 4) if ep_clean else 1.0,
                "rollout_mean_rim_cm": round(float(np.mean(ep_rims)), 2) if ep_rims else 0.0,
                "vf_loss": round(mean_vf, 5),
                "pg_loss": round(mean_pg, 5),
                "approx_kl": round(mean_kl, 5),
                "sym_loss": round(mean_sym, 6),
                "anc_loss": round(mean_anc, 5),
                "e0_drift": e0_drift,
                "wall_s": round(time.perf_counter() - it_t0, 2),
            }
            training_log["iterations"].append(it_rec)
            if it in (1, 8, 12, 16, 20, 26, 32, 36) or it % 4 == 0:
                print(
                    f"[Iter {it:02d}/{total_iters} | {it_rec['mode'][:6]} | DR={cur_dr:.2f}] "
                    f"rew={it_rec['mean_step_reward']:+.3f} surv={it_rec['rollout_survival_rate']*100:5.1f}% "
                    f"clean={it_rec['rollout_clean_rate']*100:5.1f}% rim={it_rec['rollout_mean_rim_cm']:5.2f}cm "
                    f"vf={mean_vf:.4f} kl={mean_kl:.4f} ({it_rec['wall_s']}s)",
                    flush=True,
                )

            # Periodic deterministic validation on both 0-DR and Full-DR
            if it >= critic_warmup_iters + 4 and (it % 4 == 0 or it in (16, 26, total_iters)):
                v0 = evaluate_validation_suite(model, dr_scale=0.0)
                vf = evaluate_validation_suite(model, dr_scale=1.0)
                comb = 0.45 * v0["composite_score"] + 0.55 * vf["composite_score"]
                is_best = comb >= best_combined_score
                if is_best:
                    best_combined_score = comb
                    best_iter = it
                    best_sha = model.save_checkpoint(
                        best_ckpt_path,
                        metadata={
                            "stage": "stage2_ppo_best",
                            "best_iter": it,
                            "val_0dr": v0,
                            "val_fulldr": vf,
                            "combined_score": round(comb, 3),
                        },
                    )
                val_rec = {
                    "iter": it,
                    "val_0dr": v0,
                    "val_fulldr": vf,
                    "combined_score": round(comb, 3),
                    "is_new_best": is_best,
                }
                training_log["validations"].append(val_rec)
                print(
                    f"  >>> [VAL Iter {it:02d}] 0-DR: {v0['survival_rate']*100:.0f}% surv/{v0['clean_zero_scrape_rate']*100:.0f}% clean/{v0['mean_peak_rim_cm']:.2f}cm | "
                    f"Full-DR: {vf['survival_rate']*100:.0f}% surv/{vf['clean_zero_scrape_rate']*100:.0f}% clean/{vf['mean_peak_rim_cm']:.2f}cm | "
                    f"score={comb:.2f} {'*BEST*' if is_best else ''}",
                    flush=True,
                )
    finally:
        vec_env.close()

    final_sha = model.save_checkpoint(
        final_ckpt_path,
        metadata={
            "stage": "stage2_ppo_final",
            "total_iters": total_iters,
            "total_steps": total_iters * steps_per_iter * num_envs,
        },
    )
    training_log["summary"] = {
        "total_iterations": total_iters,
        "critic_warmup_iterations": critic_warmup_iters,
        "total_env_steps": total_iters * steps_per_iter * num_envs,
        "best_iteration": best_iter,
        "best_combined_score": round(best_combined_score, 3),
        "best_checkpoint": str(best_ckpt_path),
        "best_checkpoint_sha256": best_sha,
        "final_checkpoint": str(final_ckpt_path),
        "final_checkpoint_sha256": final_sha,
        "e0_drift": model.verify_zero_e0_drift(),
        "wall_seconds": round(time.perf_counter() - t0, 2),
    }

    ev_dir = HERE / "evidence"
    ev_dir.mkdir(parents=True, exist_ok=True)
    (ev_dir / "ppo_training_log.json").write_text(
        json.dumps(training_log, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(
        f"\nCompleted Stage-2 PPO in {training_log['summary']['wall_seconds']}s | "
        f"Best iter={best_iter} (SHA={best_sha[:12]}) | Final SHA={final_sha[:12]}",
        flush=True,
    )


if __name__ == "__main__":
    main()
