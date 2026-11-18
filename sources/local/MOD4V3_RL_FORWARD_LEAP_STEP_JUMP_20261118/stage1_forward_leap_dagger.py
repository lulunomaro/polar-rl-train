# SPDX-License-Identifier: MIT
"""Stage 1: Pure-Observation BC + Multi-Round Closed-Loop DAgger for COD Forward Leap & Step-Jump.

Trains PureNeuralForwardLeapExpert (obs_35 + obs_history_420 -> act_6) with ZERO runtime cheating:
  - Round 0 (beta=1.0): Clean closed-loop trajectories across Stand-to-Forward COD Dive, Moving High-Speed
                        Forward Leap, 2x Continuous Forward Multi-Leap, Direct Jump-Onto-Step (16/20/24 cm,
                        both standing start & moving approach, step-top park & cruise), and 2-Step Stair Vault.
  - Round 1 (beta=0.25): 75% pure student closed-loop rollouts + oracle relabeling.
  - Round 2 (beta=0.00): 100% pure student closed-loop rollouts + oracle relabeling.
  - Saves weights/model_bc_dagger.pt, trajectories/clean_forward_leap_anchor.pt, and evidence/stage1_bc_dagger_log.json.
"""
from __future__ import annotations

import json
import math
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
from torch.utils.data import DataLoader, TensorDataset

from forward_leap_env import JUMP_GATE_DURATION_S, LEG_DELTA_BOUNDS, Mod4v3ForwardLeapEnv
from moe_forward_leap_model import (
    ACTION_CLIP,
    HERE,
    JUMP_MODE_BIT_INDEX,
    MoEForwardLeapActorCritic,
    StatefulMoEForwardLeapActor,
)
from ppo_forward_leap_train import evaluate_validation_suite

DELTA_GRID = np.array([0.348, 0.503, 0.659, 0.809, 0.952, 1.086, 1.210, 1.325, 1.432, 1.532, 1.625, 1.712, 1.752])
MEAN_GRID = np.array([0.4674, 0.4217, 0.3800, 0.3451, 0.3172, 0.2953, 0.2780, 0.2645, 0.2538, 0.2454, 0.2386, 0.2332, 0.2317])


class Stage1ForwardLeapOracle:
    """Offline/DAgger trajectory teacher (used ONLY in Stage-1 collection, NEVER imported at runtime!)."""

    def __init__(self, e0_mlp: nn.Module, default_active: np.ndarray):
        self.e0 = e0_mlp
        self.default = default_active.astype(np.float64)
        self.reset()

    def reset(self) -> None:
        self.phase = "DRIVE"
        self.phase_t0 = 0.0
        self.c_delta = np.full(2, 1.02, dtype=np.float64)
        self.push_vx = 0.0
        self.land_vx = 0.0
        self.last_w_idx = -1

    def query_action(self, env: Mod4v3ForwardLeapEnv, obs_np: np.ndarray) -> tuple[np.ndarray, int]:
        now = float(env.d.time)
        jump_on = bool(obs_np[JUMP_MODE_BIT_INDEX] > 0.5)
        if not jump_on:
            self.phase = "DRIVE"
            n_obs = torch.from_numpy(obs_np).unsqueeze(0).clone()
            n_obs[..., 28:35] = torch.tensor([1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
            with torch.no_grad():
                return np.clip(self.e0(n_obs)[0].numpy(), -ACTION_CLIP, ACTION_CLIP).astype(np.float32), 0

        if env.cur_window_idx != self.last_w_idx:
            self.last_w_idx = env.cur_window_idx
            self.phase = "CROUCH"
            self.phase_t0 = now
            self.c_delta = np.full(2, 1.02, dtype=np.float64)

        el = now - self.phase_t0
        c_s = 0.64 if env.cmd_vx < 0.25 else 0.44
        if self.phase == "CROUCH":
            if (el >= c_s and env.support_substeps >= 4) or el >= c_s + 0.12:
                self.phase, self.phase_t0, el = "PUSH", now, 0.0
                self.push_vx = float(env.body_vx)
        elif self.phase == "PUSH":
            if env.air_substeps >= 3 and env.d.qvel[2] > 0.20 and el >= 0.04:
                self.phase, self.phase_t0, el = "FLIGHT_TUCK", now, 0.0
            elif el >= 0.28:
                self.phase, self.phase_t0, el = "CRUISE_HOLD", now, 0.0
        elif self.phase == "FLIGHT_TUCK":
            if el >= 0.14 and (env.d.qvel[2] <= -0.22 or el >= 0.26):
                self.phase, self.phase_t0, el = "LANDING_EXTEND", now, 0.0
        elif self.phase == "LANDING_EXTEND":
            if env.support_substeps >= 1:
                self.land_vx = max(0.75, float(env.body_vx))
                self.phase, self.phase_t0, el = "SKYHOOK_ABSORB", now, 0.0
            elif el > 0.55:
                self.phase, self.phase_t0, el = "CRUISE_HOLD", now, 0.0
        elif self.phase == "SKYHOOK_ABSORB":
            if el >= 0.50:
                self.phase, self.phase_t0, el = "CRUISE_HOLD", now, 0.0

        ph_code = {
            "DRIVE": 0,
            "CROUCH": 1,
            "PUSH": 2,
            "FLIGHT_TUCK": 3,
            "LANDING_EXTEND": 4,
            "SKYHOOK_ABSORB": 5,
            "CRUISE_HOLD": 6,
        }[self.phase]

        R = env.d.xmat[env.base_id].reshape(3, 3)
        pitch = math.asin(float(np.clip(-R[2, 0], -1.0, 1.0)))
        roll = math.atan2(float(R[2, 1]), float(R[2, 2]))
        wx_ang, wy_ang = float(env.d.qvel[3]), float(env.d.qvel[4])

        n_obs = torch.from_numpy(obs_np).unsqueeze(0).clone()
        n_obs[..., 28:35] = torch.tensor([1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        dt_g = max(0.0, now - env.window_t0)
        w_h = max(0.0, min(1.0, (JUMP_GATE_DURATION_S - dt_g) / 0.28))
        ref_h = env.height_cmd + w_h * (0.365 - env.height_cmd)
        n_obs[..., 3] = float(ref_h * 5.0)

        v_lunge = max(float(env.cmd_vx), 1.92 - 0.22 * min(0.85, float(env.cmd_vx)))
        if self.phase == "CROUCH":
            ramp = min(1.0, dt_g / 0.24)
            n_obs[..., 0] = float(env.cmd_vx + ramp * (v_lunge - env.cmd_vx))
        elif self.phase == "PUSH":
            n_obs[..., 0] = float(max(float(env.cmd_vx) * 0.94, 0.94 * max(1.00, env.body_vx)))
        elif self.phase in ("FLIGHT_TUCK", "LANDING_EXTEND"):
            n_obs[..., 0] = max(float(env.cmd_vx), 0.96 * float(env.body_vx))
        elif self.phase in ("SKYHOOK_ABSORB", "CRUISE_HOLD"):
            dt_land = max(0.0, now - env.window_land_time) if env.window_landed else el
            taper = max(0.0, 1.0 - dt_land / 1.05)
            coast_v = float(env.cmd_vx) + taper * (0.96 * self.land_vx - float(env.cmd_vx)) + 0.75 * min(0.0, pitch)
            n_obs[..., 0] = max(0.15, max(float(env.cmd_vx) * 0.80, coast_v))

        with torch.no_grad():
            raw = self.e0(n_obs)[0].numpy().astype(np.float64)
        if self.phase == "CRUISE_HOLD":
            return np.clip(raw, -ACTION_CLIP, ACTION_CLIP).astype(np.float32), ph_code

        q_legs = env.d.qpos[env.active_qadr[:4]]
        qd_w = env.d.qvel[env.active_dadr[4:6]]
        d0 = self.default

        raw_mean = np.array(
            [
                0.5 * (d0[0] + 0.5 * raw[0] + d0[1] + 0.5 * raw[1]),
                0.5 * (d0[2] + 0.5 * raw[2] + d0[3] + 0.5 * raw[3]),
            ],
            dtype=np.float64,
        )
        raw_delta = np.clip(
            [
                (d0[0] + 0.5 * raw[0]) - (d0[1] + 0.5 * raw[1]),
                (d0[2] + 0.5 * raw[2]) - (d0[3] + 0.5 * raw[3]),
            ],
            *LEG_DELTA_BOUNDS,
        )

        act = raw.copy()
        if self.phase == "CROUCH":
            dl_delay = 0.15 if env.cmd_vx < 0.25 else 0.08
            if el >= dl_delay:
                ct = (0.495 if env.cmd_vx < 0.25 else 0.515) + 0.02 * abs(env.body_vx)
                self.c_delta = self.c_delta + np.clip(ct - self.c_delta, -1.88 * 0.02, 1.88 * 0.02)
            delta = self.c_delta.copy()
        elif self.phase == "PUSH":
            delta = np.full(2, LEG_DELTA_BOUNDS[1])
        elif self.phase == "FLIGHT_TUCK":
            delta = np.full(2, LEG_DELTA_BOUNDS[1] + (0.173 - LEG_DELTA_BOUNDS[1]) * min(1.0, el / 0.025))
        elif self.phase == "LANDING_EXTEND":
            delta = np.full(2, 0.173 + (1.34 - 0.173) * min(1.0, el / 0.09))
        else:
            wx_m = float(env.d.xpos[env.wheels, 0].mean())
            rel_z = float(env.d.qpos[2]) - env.terrain_z_at(wx_m)
            fade = max(0.0, 1.0 - el / 0.46)
            delta = raw_delta + 0.36 * max(0.0, -float(env.d.qvel[2])) + fade * 11.0 * max(0.0, 0.285 - rel_z)

        delta = np.clip(delta, *LEG_DELTA_BOUNDS)
        mean = raw_mean.copy()
        cur_ad = 0.5 * float((q_legs[0] - q_legs[1]) + (q_legs[2] - q_legs[3]))
        if self.phase == "CROUCH":
            mean += 0.020 * v_lunge
        elif self.phase == "PUSH":
            mean += -0.326 + 0.085 * max(0.95, self.push_vx)
        elif self.phase == "FLIGHT_TUCK":
            mean += +0.04
        elif self.phase == "LANDING_EXTEND":
            # Level-chassis hip-sweep Raibert law (pitch_ref = 0.0 rad!)
            r_air = float(np.interp(cur_ad, DELTA_GRID, MEAN_GRID)) - 0.55 * pitch + 0.16 * env.body_vx
            wr = 0.85 * min(1.0, el / 0.04)
            mean = (1.0 - wr) * raw_mean + wr * np.full(2, r_air)
        elif self.phase == "SKYHOOK_ABSORB":
            # Ground-pinned anti-wheelie hip damping keeps post-landing |pitch| <= 11.5 deg!
            fade_s = max(0.0, 1.0 - el / 0.30)
            mean += fade_s * (0.95 * min(0.0, pitch) + 0.05 * min(0.0, wy_ang))

        for i, (fi, ri) in enumerate(((0, 1), (2, 3))):
            act[fi] = float(2.0 * (mean[i] + 0.5 * delta[i] - d0[fi]))
            act[ri] = float(2.0 * (mean[i] - 0.5 * delta[i] - d0[ri]))

        if self.phase in ("FLIGHT_TUCK", "LANDING_EXTEND") and env.air_substeps >= 1:
            # Strict zero-pitch airborne reaction-wheel + symmetric 4-bar leg attitude control (pitch_ref = 0.0!)
            pe = pitch
            mt = 0.5 * (15.5 * pe + 1.40 * wy_ang)
            qd_w_sym = 0.5 * float(qd_w[0] + qd_w[1])
            act[4:6] = (qd_w_sym + mt / 0.6) / 10.0
            rc = float(np.clip(0.65 * roll + 0.08 * wx_ang, -0.15, 0.15))
            nd = np.clip(delta + np.array([-rc, rc]), *LEG_DELTA_BOUNDS)
            for i, (fi, ri) in enumerate(((0, 1), (2, 3))):
                act[fi] += float(nd[i] - delta[i])
                act[ri] -= float(nd[i] - delta[i])
            act[:4] += 2.0 * float(np.clip(3.5 * pe + 0.28 * wy_ang, -0.48, 0.48))

        return np.clip(act, -ACTION_CLIP, ACTION_CLIP).astype(np.float32), ph_code


def collect_dagger_round(
    env: Mod4v3ForwardLeapEnv,
    oracle: Stage1ForwardLeapOracle,
    model: MoEForwardLeapActorCritic,
    num_episodes: int,
    beta_teacher: float,
    dr_prob: float,
    dr_max: float,
) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    model.eval()
    obs_list, hist_list, act_list, w_list = [], [], [], []
    anc_obs, anc_hist, anc_act = [], [], []

    survived_eps = 0
    clean_eps = 0
    accepted_eps = 0
    dxs, rims, air_pitches, ep_pitches = [], [], [], []

    for ep_i in range(num_episodes):
        dr_s = float(env.rng.uniform(0.15, dr_max)) if env.rng.random() < dr_prob else 0.0
        st = env.sample_random_scenario(dr_scale=dr_s)
        # Every 10th episode: also include a 2-step continuous platform vault (20cm -> 40cm)!
        if ep_i % 10 == 9:
            st = env.reset(
                dr_scale=dr_s,
                v_cmd=0.0,
                v_cmd_post=0.0,
                post_cmd_switch_s=4.5,
                jump_times=(1.0, 3.25),
                max_episode_s=5.8,
                steps=[(0.745, 2.15, 0.20), (2.18, 2.50, 0.40)],
            )
        oracle.reset()

        ep_obs, ep_hist, ep_act, ep_w = [], [], [], []
        while True:
            obs_np = st["obs"]
            hist_np = st["hist"]
            target_act, ph_code = oracle.query_action(env, obs_np)

            if obs_np[JUMP_MODE_BIT_INDEX] > 0.5:
                ep_obs.append(obs_np.copy())
                ep_hist.append(hist_np.copy())
                ep_act.append(target_act.copy())
                w_frame = 3.2 if ph_code in (2, 3, 4) else (2.2 if ph_code in (1, 5) else 1.2)
                ep_w.append(w_frame)

            if obs_np[JUMP_MODE_BIT_INDEX] <= 0.5 or env.rng.random() >= beta_teacher:
                with torch.no_grad():
                    exec_act = (
                        model.act_deterministic(
                            torch.from_numpy(obs_np).unsqueeze(0),
                            torch.from_numpy(hist_np).unsqueeze(0),
                        )[0]
                        .numpy()
                    )
                if obs_np[JUMP_MODE_BIT_INDEX] > 0.5 and env.rng.random() < beta_teacher:
                    exec_act = target_act
            else:
                exec_act = target_act

            st, _rew, done, info = env.step(exec_act)
            if done:
                survived = info["fell_reason"] == "" and not info["slid_off_step"]
                step_ok = info["steps_mounted_count"] >= info["steps_total"]
                fwd_ok = info["ep_mean_leap_dx_m"] >= 0.55 and info["ep_min_active_vx"] >= -0.04
                pitch_ok = info["ep_max_air_pitch_deg"] <= 10.0 and info["ep_max_episode_pitch_deg"] <= 12.6
                clean = (
                    survived
                    and step_ok
                    and fwd_ok
                    and pitch_ok
                    and info["ep_guide_force_N"] < 1.0
                    and info["ep_chassis_force_N"] < 1.0
                    and info["ep_riser_hit_N"] < 2.0
                )
                if survived and step_ok and fwd_ok:
                    survived_eps += 1
                    dxs.append(info["ep_mean_leap_dx_m"])
                    rims.append(info["ep_peak_world_rim_cm"])
                    air_pitches.append(info["ep_max_air_pitch_deg"])
                    ep_pitches.append(info["ep_max_episode_pitch_deg"])
                if clean:
                    clean_eps += 1

                keep = clean if beta_teacher > 0.99 else (len(ep_obs) >= 20 and (survived or beta_teacher < 0.5))
                if keep and len(ep_obs) > 0:
                    accepted_eps += 1
                    obs_list.extend(ep_obs)
                    hist_list.extend(ep_hist)
                    act_list.extend(ep_act)
                    w_list.extend(ep_w)
                    if clean and dr_s == 0.0:
                        anc_obs.extend(ep_obs)
                        anc_hist.extend(ep_hist)
                        anc_act.extend(ep_act)
                break

    batch = {
        "obs": np.asarray(obs_list, dtype=np.float32),
        "hist": np.asarray(hist_list, dtype=np.float32),
        "act": np.asarray(act_list, dtype=np.float32),
        "weight": np.asarray(w_list, dtype=np.float32),
        "anc_obs": np.asarray(anc_obs, dtype=np.float32) if anc_obs else np.zeros((0, 35), dtype=np.float32),
        "anc_hist": np.asarray(anc_hist, dtype=np.float32) if anc_hist else np.zeros((0, 420), dtype=np.float32),
        "anc_act": np.asarray(anc_act, dtype=np.float32) if anc_act else np.zeros((0, 6), dtype=np.float32),
    }
    stats = {
        "episodes_run": num_episodes,
        "valid_forward_step_episodes": survived_eps,
        "clean_zero_scrape_lowpitch_episodes": clean_eps,
        "accepted_episodes": accepted_eps,
        "collected_jump_frames": int(len(obs_list)),
        "mean_leap_dx_m": round(float(np.mean(dxs)), 3) if dxs else 0.0,
        "mean_rim_cm": round(float(np.mean(rims)), 2) if rims else 0.0,
        "max_air_pitch_deg": round(float(np.max(air_pitches)), 2) if air_pitches else 0.0,
        "max_episode_pitch_deg": round(float(np.max(ep_pitches)), 2) if ep_pitches else 0.0,
    }
    return batch, stats


def train_ejump_supervised(
    model: MoEForwardLeapActorCritic,
    obs_all: np.ndarray,
    hist_all: np.ndarray,
    act_all: np.ndarray,
    w_all: np.ndarray,
    epochs: int = 35,
    lr: float = 1.2e-3,
    batch_size: int = 512,
) -> dict[str, float]:
    model.train()
    params = [p for p in model.actor_body.e_jump.parameters() if p.requires_grad]
    opt = torch.optim.AdamW(params, lr=lr, weight_decay=1e-4)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=epochs, eta_min=1.5e-4)

    ds = TensorDataset(
        torch.from_numpy(obs_all),
        torch.from_numpy(hist_all),
        torch.from_numpy(act_all),
        torch.from_numpy(w_all),
    )
    loader = DataLoader(ds, batch_size=batch_size, shuffle=True, drop_last=False)

    first_mse = last_mse = last_sym = 0.0
    for ep in range(epochs):
        tm, ts, nb = 0.0, 0.0, 0
        for bo, bh, ba, bw in loader:
            pred = model.actor_body.e_jump(bo, bh)
            mse = (((pred - ba) ** 2).mean(dim=-1) * bw).mean() / bw.mean()
            sym = model.symmetry_loss(bo, bh)
            loss = mse + 0.25 * sym
            opt.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(params, 2.0)
            opt.step()
            tm += float(mse.item())
            ts += float(sym.item())
            nb += 1
        sched.step()
        if ep == 0:
            first_mse = tm / max(1, nb)
        last_mse, last_sym = tm / max(1, nb), ts / max(1, nb)

    model.eval()
    model.verify_zero_e0_drift()
    return {
        "first_epoch_mse": round(first_mse, 5),
        "final_epoch_mse": round(last_mse, 5),
        "final_sym_loss": round(last_sym, 6),
    }


def main() -> None:
    t0 = time.perf_counter()
    torch.manual_seed(20261118)
    np.random.seed(20261118)
    torch.set_num_threads(2)

    model = MoEForwardLeapActorCritic()
    model.load_frozen_c874()
    model.verify_zero_e0_drift()

    env = Mod4v3ForwardLeapEnv(seed=101)
    oracle = Stage1ForwardLeapOracle(model.actor_body.e0, env.default_active)

    log_data: dict[str, Any] = {"stages": []}

    print("=== Stage 1 Round 0: Collecting Forward-Dive + 16/20/24cm Step-Jump Demos ===", flush=True)
    b0, s0 = collect_dagger_round(env, oracle, model, num_episodes=200, beta_teacher=1.0, dr_prob=0.35, dr_max=0.70)
    print(f"  Round 0 stats: {s0}", flush=True)

    obs_mean = torch.from_numpy(b0["obs"].mean(axis=0))
    obs_std = torch.from_numpy(b0["obs"].std(axis=0) + 0.05)
    model.actor_body.e_jump.set_normalization(obs_mean, obs_std)

    agg_obs, agg_hist, agg_act, agg_w = [b0["obs"]], [b0["hist"]], [b0["act"]], [b0["weight"]]
    anc_obs, anc_hist, anc_act = [b0["anc_obs"]], [b0["anc_hist"]], [b0["anc_act"]]

    tr0 = train_ejump_supervised(model, b0["obs"], b0["hist"], b0["act"], b0["weight"], epochs=42, lr=1.4e-3)
    ev0 = evaluate_validation_suite(model, dr_scale=0.0)
    print(f"  Round 0 train: {tr0}\n  Round 0 Pure-Neural 0-DR: pass={ev0['pass_rate']*100:.1f}%, air_p={ev0['max_air_pitch_deg']}d, ep_p={ev0['max_episode_pitch_deg']}d, dx={ev0['mean_leap_dx_m']}m", flush=True)
    log_data["stages"].append({"round": 0, "beta_teacher": 1.0, "collection": s0, "train": tr0, "pure_eval_0dr": ev0})

    print("\n=== Stage 1 Round 1: Closed-Loop DAgger (75% Student-Driven) ===", flush=True)
    b1, s1 = collect_dagger_round(env, oracle, model, num_episodes=120, beta_teacher=0.25, dr_prob=0.50, dr_max=0.85)
    print(f"  Round 1 stats: {s1}", flush=True)
    agg_obs.append(b1["obs"])
    agg_hist.append(b1["hist"])
    agg_act.append(b1["act"])
    agg_w.append(b1["weight"])
    if len(b1["anc_obs"]) > 0:
        anc_obs.append(b1["anc_obs"])
        anc_hist.append(b1["anc_hist"])
        anc_act.append(b1["anc_act"])

    tr1 = train_ejump_supervised(
        model,
        np.concatenate(agg_obs),
        np.concatenate(agg_hist),
        np.concatenate(agg_act),
        np.concatenate(agg_w),
        epochs=36,
        lr=9.0e-4,
    )
    ev1 = evaluate_validation_suite(model, dr_scale=0.0)
    print(f"  Round 1 train: {tr1}\n  Round 1 Pure-Neural 0-DR: pass={ev1['pass_rate']*100:.1f}%, air_p={ev1['max_air_pitch_deg']}d, ep_p={ev1['max_episode_pitch_deg']}d, dx={ev1['mean_leap_dx_m']}m", flush=True)
    log_data["stages"].append({"round": 1, "beta_teacher": 0.25, "collection": s1, "train": tr1, "pure_eval_0dr": ev1})

    print("\n=== Stage 1 Round 2: Closed-Loop DAgger (100% Pure Student-Driven) ===", flush=True)
    b2, s2 = collect_dagger_round(env, oracle, model, num_episodes=120, beta_teacher=0.0, dr_prob=0.60, dr_max=1.0)
    print(f"  Round 2 stats: {s2}", flush=True)
    agg_obs.append(b2["obs"])
    agg_hist.append(b2["hist"])
    agg_act.append(b2["act"])
    agg_w.append(b2["weight"])

    tr2 = train_ejump_supervised(
        model,
        np.concatenate(agg_obs),
        np.concatenate(agg_hist),
        np.concatenate(agg_act),
        np.concatenate(agg_w),
        epochs=40,
        lr=6.5e-4,
    )
    ev2_0dr = evaluate_validation_suite(model, dr_scale=0.0)
    ev2_fdr = evaluate_validation_suite(model, dr_scale=1.0)
    print(f"  Round 2 train: {tr2}\n  Round 2 Pure-Neural 0-DR: {json.dumps(ev2_0dr)}", flush=True)
    print(f"  Round 2 Pure-Neural Full-DR: {json.dumps(ev2_fdr)}", flush=True)
    log_data["stages"].append(
        {"round": 2, "beta_teacher": 0.0, "collection": s2, "train": tr2, "pure_eval_0dr": ev2_0dr, "pure_eval_fulldr": ev2_fdr}
    )

    traj_dir = HERE / "trajectories"
    traj_dir.mkdir(parents=True, exist_ok=True)
    a_obs_cat = np.concatenate(anc_obs, axis=0)
    a_hist_cat = np.concatenate(anc_hist, axis=0)
    a_act_cat = np.concatenate(anc_act, axis=0)
    if len(a_obs_cat) > 16384:
        idx = np.random.choice(len(a_obs_cat), size=16384, replace=False)
        a_obs_cat, a_hist_cat, a_act_cat = a_obs_cat[idx], a_hist_cat[idx], a_act_cat[idx]
    torch.save(
        {
            "obs": torch.from_numpy(a_obs_cat),
            "hist": torch.from_numpy(a_hist_cat),
            "act": torch.from_numpy(a_act_cat),
        },
        traj_dir / "clean_forward_leap_anchor.pt",
    )

    ckpt_path = HERE / "weights/model_bc_dagger.pt"
    sha = model.save_checkpoint(
        ckpt_path,
        metadata={
            "stage": "stage1_forward_leap_bc_dagger",
            "total_jump_frames": int(sum(len(x) for x in agg_obs)),
            "anchor_frames": int(len(a_obs_cat)),
            "wall_s": round(time.perf_counter() - t0, 2),
            "pure_eval_0dr": ev2_0dr,
            "pure_eval_fulldr": ev2_fdr,
        },
    )
    log_data["checkpoint"] = str(ckpt_path)
    log_data["checkpoint_sha256"] = sha
    log_data["total_jump_frames"] = int(sum(len(x) for x in agg_obs))
    log_data["wall_seconds"] = round(time.perf_counter() - t0, 2)

    ev_dir = HERE / "evidence"
    ev_dir.mkdir(parents=True, exist_ok=True)
    (ev_dir / "stage1_bc_dagger_log.json").write_text(
        json.dumps(log_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"\nSaved Stage-1 Forward-Leap BC+DAgger -> {ckpt_path} (SHA={sha[:12]}, wall={log_data['wall_seconds']}s)", flush=True)


if __name__ == "__main__":
    main()
