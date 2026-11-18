# SPDX-License-Identifier: MIT
"""Stage 2: Closed-Loop Anti-Cheat PPO for COD Forward Leap & Direct Jump-Onto-Step (16/20/24 cm).

Strict CPU & MoE Isolation:
  - Parallel workers capped strictly at num_envs = 6 (OPENBLAS_NUM_THREADS=1, OMP_NUM_THREADS=1, torch threads=2).
  - E0 (c874) strictly frozen (0.0 parameter drift verified every iteration).
  - Critic-Only Warmup (Iters 1..8) -> 0-DR PPO (9..16) -> 50% DR PPO (17..26) -> 100% Full-DR PPO (27..36).
  - Saves weights/model_rl_forward_leap_best.pt, weights/model_rl_forward_leap_final.pt, and evidence/ppo_training_log.json.
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

from forward_leap_env import Mod4v3ForwardLeapEnv, ParallelLeapVecEnv
from moe_forward_leap_model import (
    ACT_DIM,
    HERE,
    HIST_DIM,
    JUMP_MODE_BIT_INDEX,
    MoEForwardLeapActorCritic,
    OBS_DIM,
    PRIV_CRITIC_DIM,
    StatefulMoEForwardLeapActor,
)


def validation_scenarios() -> list[tuple[str, float, float, float | None, tuple[float, ...], float, list[tuple[float, float, float]]]]:
    """9 core pure-neural validation scenarios covering COD forward dives, multi-leaps & 16/20/24cm steps."""
    d_s16 = Mod4v3ForwardLeapEnv.step_front_for_stand_jump(0.16)
    d_s20 = Mod4v3ForwardLeapEnv.step_front_for_stand_jump(0.20)
    d_s24 = Mod4v3ForwardLeapEnv.step_front_for_stand_jump(0.24)
    xf_m20 = Mod4v3ForwardLeapEnv.step_front_for_moving_jump(0.75, 1.45)
    xf_m24 = Mod4v3ForwardLeapEnv.step_front_for_moving_jump(0.85, 1.45)
    return [
        ("stand_dive_0p0", 0.0, 0.0, None, (1.0,), 4.2, []),
        ("move_leap_0p6", 0.6, 0.6, None, (1.4,), 4.4, []),
        ("move_leap_0p9", 0.9, 0.9, None, (1.4,), 4.4, []),
        ("multi2x_0p8", 0.8, 0.8, None, (1.2, 3.3), 5.8, []),
        ("stand_step_16cm", 0.0, 0.0, 2.5, (1.0,), 4.2, [(d_s16, 3.6, 0.16)]),
        ("stand_step_20cm", 0.0, 0.0, 2.5, (1.0,), 4.2, [(d_s20, 3.6, 0.20)]),
        ("stand_step_24cm", 0.0, 0.0, 2.5, (1.0,), 4.2, [(d_s24, 3.6, 0.24)]),
        ("move_step_20cm_park", 0.75, 0.0, 2.9, (1.45,), 4.4, [(xf_m20, 3.6, 0.20)]),
        ("move_step_24cm_cruise", 0.85, 0.85, None, (1.45,), 4.4, [(xf_m24, 3.8, 0.24)]),
    ]


def evaluate_validation_suite(model: MoEForwardLeapActorCritic, dr_scale: float, base_seed: int = 9100) -> dict[str, Any]:
    """Deterministic pure-neural evaluation (ZERO teacher calls, ZERO privileged actor inputs)."""
    model.eval()
    actor = StatefulMoEForwardLeapActor(model)
    cases = validation_scenarios()

    seeds = (0, 1) if dr_scale > 0.0 else (0,)
    per_case: dict[str, Any] = {}
    pass_cnt = 0
    clean_cnt = 0
    dxs: list[float] = []
    rims: list[float] = []
    air_ps: list[float] = []
    ep_ps: list[float] = []
    tot_eps = 0

    for c_i, (name, vp, vpo, sw, jt, ms, stps) in enumerate(cases):
        c_pass = 0
        c_clean = 0
        c_dx = []
        c_rim = []
        c_air_p = []
        c_ep_p = []
        for s_off in seeds:
            env = Mod4v3ForwardLeapEnv(seed=base_seed + c_i * 37 + s_off)
            st = env.reset(
                dr_scale=dr_scale,
                v_cmd=vp,
                v_cmd_post=vpo,
                post_cmd_switch_s=sw,
                jump_times=jt,
                max_episode_s=ms,
                steps=stps,
            )
            actor.reset_history()
            actor.queue.reset(torch.from_numpy(st["obs"]).unsqueeze(0))
            first = True
            while True:
                obs_t = torch.from_numpy(st["obs"]).unsqueeze(0)
                if first:
                    with torch.inference_mode():
                        act = model.act_deterministic(obs_t, actor.queue.buffer.flatten(-2))[0].numpy()
                    first = False
                else:
                    act = actor(obs_t)[0].numpy()
                st, _r, done, info = env.step(act)
                if done:
                    tot_eps += 1
                    survived = info["fell_reason"] == "" and not info["slid_off_step"]
                    step_ok = info["steps_mounted_count"] >= info["steps_total"]
                    fwd_ok = info["ep_mean_leap_dx_m"] >= 0.55 and info["ep_min_active_vx"] >= -0.04
                    ok = survived and step_ok and fwd_ok
                    air_ps.append(info["ep_max_air_pitch_deg"])
                    ep_ps.append(info["ep_max_episode_pitch_deg"])
                    c_air_p.append(info["ep_max_air_pitch_deg"])
                    c_ep_p.append(info["ep_max_episode_pitch_deg"])
                    clean = (
                        ok
                        and info["ep_guide_force_N"] < 1.0
                        and info["ep_chassis_force_N"] < 1.0
                        and info["ep_riser_hit_N"] < 2.0
                    )
                    if ok:
                        pass_cnt += 1
                        c_pass += 1
                        dxs.append(info["ep_mean_leap_dx_m"])
                        rims.append(info["ep_peak_world_rim_cm"])
                        c_dx.append(info["ep_mean_leap_dx_m"])
                        c_rim.append(info["ep_peak_world_rim_cm"])
                    if clean:
                        clean_cnt += 1
                        c_clean += 1
                    break
        per_case[name] = {
            "pass": f"{c_pass}/{len(seeds)}",
            "clean": f"{c_clean}/{len(seeds)}",
            "mean_leap_dx_m": round(float(np.mean(c_dx)), 3) if c_dx else 0.0,
            "mean_rim_cm": round(float(np.mean(c_rim)), 2) if c_rim else 0.0,
            "max_air_pitch_deg": round(float(np.max(c_air_p)), 2) if c_air_p else 0.0,
            "max_episode_pitch_deg": round(float(np.max(c_ep_p)), 2) if c_ep_p else 0.0,
        }

    pass_rate = pass_cnt / max(1, tot_eps)
    clean_rate = clean_cnt / max(1, tot_eps)
    mean_dx = float(np.mean(dxs)) if dxs else 0.0
    mean_rim = float(np.mean(rims)) if rims else 0.0
    max_air_p = float(np.max(air_ps)) if air_ps else 99.0
    max_ep_p = float(np.max(ep_ps)) if ep_ps else 99.0
    pitch_pen = 0.0
    if dr_scale <= 0.01:
        pitch_pen = 8.0 * max(0.0, max_air_p - 9.8) + 8.0 * max(0.0, max_ep_p - 12.8) + 0.5 * (max_air_p + max_ep_p)
    else:
        pitch_pen = 0.4 * float(np.mean(air_ps))
    score = 115.0 * pass_rate + 45.0 * clean_rate + 20.0 * mean_dx + 0.7 * mean_rim - pitch_pen
    return {
        "dr_scale": dr_scale,
        "pass_rate": round(pass_rate, 4),
        "clean_rate": round(clean_rate, 4),
        "mean_leap_dx_m": round(mean_dx, 3),
        "mean_rim_cm": round(mean_rim, 2),
        "max_air_pitch_deg": round(max_air_p, 2),
        "max_episode_pitch_deg": round(max_ep_p, 2),
        "composite_score": round(score, 3),
        "cases": per_case,
    }


def curriculum_dr_scale(iteration: int) -> float:
    if iteration <= 8:
        return 0.00  # Critic-Only Warmup
    if iteration <= 16:
        return 0.00  # 0-DR PPO
    if iteration <= 26:
        return 0.50  # 50% Progressive DR PPO
    return 1.00  # 100% Full-DR PPO


def main() -> None:
    t0 = time.perf_counter()
    torch.manual_seed(20261118)
    np.random.seed(20261118)
    torch.set_num_threads(2)

    bc_ckpt = HERE / "weights/model_bc_dagger.pt"
    anchor_path = HERE / "trajectories/clean_forward_leap_anchor.pt"
    if not bc_ckpt.exists() or not anchor_path.exists():
        raise FileNotFoundError("Run stage1_forward_leap_dagger.py first!")

    model = MoEForwardLeapActorCritic.load_from_checkpoint(bc_ckpt, device="cpu")
    with torch.no_grad():
        model.ejump_log_std.copy_(
            torch.tensor([0.020, 0.020, 0.020, 0.020, 0.030, 0.030], dtype=torch.float32).log()
        )
    model.verify_zero_e0_drift()

    anchor_data = torch.load(anchor_path, map_location="cpu", weights_only=False)
    anc_obs_all: torch.Tensor = anchor_data["obs"].clone()
    anc_hist_all: torch.Tensor = anchor_data["hist"].clone()
    anc_act_all: torch.Tensor = anchor_data["act"].clone()

    actor_params = [
        p
        for _n, p in list(model.actor_body.e_jump.named_parameters()) + [("ejump_log_std", model.ejump_log_std)]
        if p.requires_grad
    ]
    critic_params = [p for p in model.critic.parameters() if p.requires_grad]

    actor_opt = torch.optim.Adam(actor_params, lr=5.0e-6, eps=1e-5)
    critic_opt = torch.optim.Adam(critic_params, lr=7.0e-4, eps=1e-5)

    num_envs = 5  # Strictly <= 5 workers per parent CPU isolation rule
    steps_per_iter = 512  # 5 * 512 = 2,560 steps/iter (36 iters = 92,160 closed-loop steps)
    total_iters = 36
    critic_warmup_iters = 8
    gamma = 0.99
    gae_lambda = 0.95
    clip_eps = 0.12
    ppo_epochs = 4
    minibatch_size = 512
    target_kl = 0.010

    val0_0dr = evaluate_validation_suite(model, dr_scale=0.0)
    val0_fdr = evaluate_validation_suite(model, dr_scale=1.0)
    best_score = 0.55 * val0_0dr["composite_score"] + 0.45 * val0_fdr["composite_score"]
    print(
        f"[Init BC+DAgger] 0-DR={val0_0dr['pass_rate']*100:.1f}% pass / air_p={val0_0dr['max_air_pitch_deg']:.2f}d / ep_p={val0_0dr['max_episode_pitch_deg']:.2f}d / dx={val0_0dr['mean_leap_dx_m']:.2f}m | "
        f"Full-DR={val0_fdr['pass_rate']*100:.1f}% pass / dx={val0_fdr['mean_leap_dx_m']:.2f}m | score={best_score:.2f}",
        flush=True,
    )

    best_ckpt_path = HERE / "weights/model_rl_forward_leap_best.pt"
    final_ckpt_path = HERE / "weights/model_rl_forward_leap_final.pt"
    best_sha = model.save_checkpoint(
        best_ckpt_path,
        metadata={"stage": "ppo_init_from_bc_dagger", "val_0dr": val0_0dr, "val_fulldr": val0_fdr},
    )
    best_iter = 0

    vec_env = ParallelLeapVecEnv(num_envs=num_envs, base_seed=2026)
    torch.set_num_threads(2)
    cur_dr = curriculum_dr_scale(1)
    obs_np, hist_np, priv_np = vec_env.reset_random(dr_scale=cur_dr)

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
        "init_validation": {"val_0dr": val0_0dr, "val_fulldr": val0_fdr, "combined_score": round(best_score, 3)},
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
            ep_surv, ep_clean, ep_dxs, ep_rims, step_rews = [], [], [], [], []

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
                step_rews.append(float(rews.mean()))

                for env_i, inf in enumerate(infos):
                    if inf.get("terminal_reset", False):
                        fell = inf["fell_reason"] != ""
                        ep_surv.append(0.0 if fell else 1.0)
                        if not fell:
                            ep_dxs.append(float(inf["ep_mean_leap_dx_m"]))
                            ep_rims.append(float(inf["ep_peak_world_rim_cm"]))
                            clean = (
                                inf["ep_guide_force_N"] < 1.0
                                and inf["ep_chassis_force_N"] < 1.0
                                and inf["ep_riser_hit_N"] < 2.0
                                and inf["ep_min_active_vx"] >= -0.06
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

            if it == 1:
                flat_priv0 = torch.from_numpy(buf_priv.reshape(-1, PRIV_CRITIC_DIM))
                model.critic.priv_mean.copy_(flat_priv0.mean(dim=0))
                model.critic.priv_scale.copy_(flat_priv0.std(dim=0) + 0.05)
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
                prog = (it - critic_warmup_iters) / max(1, total_iters - critic_warmup_iters)
                cur_actor_lr = 6.0e-6 * (0.45 + 0.55 * 0.5 * (1.0 + np.cos(np.pi * prog)))
                for pg in actor_opt.param_groups:
                    pg["lr"] = float(cur_actor_lr)
                for pg in critic_opt.param_groups:
                    pg["lr"] = 4.5e-4

                jump_mask_all = f_obs[:, JUMP_MODE_BIT_INDEX] > 0.5
                if int(jump_mask_all.sum()) > 32:
                    ja = f_adv[jump_mask_all]
                    f_adv_norm = (f_adv - ja.mean()) / (ja.std() + 1e-6)
                else:
                    f_adv_norm = (f_adv - f_adv.mean()) / (f_adv.std() + 1e-6)

                anchor_coef = float(0.38 - 0.10 * prog)
                pg_losses, vf_losses, kl_list, sym_list, anc_list = [], [], [], [], []
                kl_stop = False

                for _ep in range(ppo_epochs):
                    if kl_stop:
                        break
                    perm = torch.randperm(N)
                    for start in range(0, N, minibatch_size):
                        mb = perm[start : start + minibatch_size]
                        mb_obs, mb_hist, mb_priv = f_obs[mb], f_hist[mb], f_priv[mb]

                        v_pred = model.evaluate_value(mb_obs, mb_hist, mb_priv)
                        v_clipped = f_val_old[mb] + (v_pred - f_val_old[mb]).clamp(-0.5, 0.5)
                        vf_loss = 0.5 * torch.max((v_pred - f_ret[mb]) ** 2, (v_clipped - f_ret[mb]) ** 2).mean()
                        critic_opt.zero_grad()
                        vf_loss.backward()
                        nn.utils.clip_grad_norm_(critic_params, 1.0)
                        critic_opt.step()
                        vf_losses.append(float(vf_loss.item()))

                        j_sub = mb_obs[:, JUMP_MODE_BIT_INDEX] > 0.5
                        if int(j_sub.sum()) < 16:
                            continue

                        j_obs, j_hist, j_priv = mb_obs[j_sub], mb_hist[j_sub], mb_priv[j_sub]
                        j_act = f_act[mb][j_sub]
                        j_old_logp = f_logp[mb][j_sub]
                        j_adv_mb = f_adv_norm[mb][j_sub]

                        new_logp, entropy, _vu, _mean = model.evaluate_actions(j_obs, j_hist, j_priv, j_act)
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

            e0_drift = model.verify_zero_e0_drift()
            it_rec = {
                "iter": it,
                "mode": "critic_warmup" if it <= critic_warmup_iters else "ppo_actor_critic",
                "dr_scale": cur_dr,
                "mean_step_reward": round(float(np.mean(step_rews)), 4),
                "rollout_survival_rate": round(float(np.mean(ep_surv)), 4) if ep_surv else 1.0,
                "rollout_clean_rate": round(float(np.mean(ep_clean)), 4) if ep_clean else 1.0,
                "rollout_mean_dx_m": round(float(np.mean(ep_dxs)), 3) if ep_dxs else 0.0,
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
                    f"clean={it_rec['rollout_clean_rate']*100:5.1f}% dx={it_rec['rollout_mean_dx_m']:.2f}m "
                    f"rim={it_rec['rollout_mean_rim_cm']:5.1f}cm vf={mean_vf:.4f} kl={mean_kl:.4f} ({it_rec['wall_s']}s)",
                    flush=True,
                )

            if it >= critic_warmup_iters + 4 and (it % 4 == 0 or it in (16, 26, total_iters)):
                v0 = evaluate_validation_suite(model, dr_scale=0.0)
                vf = evaluate_validation_suite(model, dr_scale=1.0)
                comb = 0.55 * v0["composite_score"] + 0.45 * vf["composite_score"]
                pitch_gate = (
                    v0["pass_rate"] >= 0.99
                    and v0["max_air_pitch_deg"] <= 9.9
                    and v0["max_episode_pitch_deg"] <= 12.8
                )
                is_best = (comb >= best_score) and pitch_gate
                if is_best:
                    best_score = comb
                    best_iter = it
                    best_sha = model.save_checkpoint(
                        best_ckpt_path,
                        metadata={
                            "stage": "stage2_ppo_forward_leap_best",
                            "best_iter": it,
                            "val_0dr": v0,
                            "val_fulldr": vf,
                            "combined_score": round(comb, 3),
                        },
                    )
                training_log["validations"].append(
                    {
                        "iter": it,
                        "val_0dr": v0,
                        "val_fulldr": vf,
                        "combined_score": round(comb, 3),
                        "is_new_best": is_best,
                    }
                )
                print(
                    f"  >>> [VAL Iter {it:02d}] 0-DR: {v0['pass_rate']*100:.0f}% pass/{v0['clean_rate']*100:.0f}% clean/air_p={v0['max_air_pitch_deg']:.2f}d/ep_p={v0['max_episode_pitch_deg']:.2f}d/dx={v0['mean_leap_dx_m']:.2f}m | "
                    f"Full-DR: {vf['pass_rate']*100:.0f}% pass/dx={vf['mean_leap_dx_m']:.2f}m | "
                    f"score={comb:.2f} {'*BEST*' if is_best else ''}",
                    flush=True,
                )
    finally:
        vec_env.close()

    final_sha = model.save_checkpoint(
        final_ckpt_path,
        metadata={"stage": "stage2_ppo_forward_leap_final", "total_iters": total_iters},
    )
    training_log["summary"] = {
        "total_iterations": total_iters,
        "critic_warmup_iterations": critic_warmup_iters,
        "total_env_steps": total_iters * steps_per_iter * num_envs,
        "best_iteration": best_iter,
        "best_combined_score": round(best_score, 3),
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
    print(f"\nCompleted Stage-2 Forward-Leap PPO in {training_log['summary']['wall_seconds']}s | Best iter={best_iter} (SHA={best_sha[:12]})", flush=True)


if __name__ == "__main__":
    main()
