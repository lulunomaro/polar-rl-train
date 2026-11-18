# SPDX-License-Identifier: MIT
"""Stage 1: Pure-Observation Behavioral Cloning + Multi-Round Closed-Loop DAgger Warmstart.

Trains the pure neural jump expert E_jump(obs_35, obs_history_420) -> act_6 inside MoEJumpActorCritic:
  - Round 0: Diverse closed-loop expert rollouts across vx_cmd in [-0.6, +1.2] m/s, single jumps,
             2x/3x continuous multi-jumps, 14-20 cm hurdles, and 0-DR + perturbed DR physics.
  - Round 1: Closed-loop DAgger (beta = 0.30, 70% pure student actions) + oracle relabeling.
  - Round 2: Closed-loop DAgger (beta = 0.00, 100% pure student actions) + oracle relabeling.
  - Saves weights/model_bc_dagger.pt, trajectories/clean_jump_anchor.pt, and evidence/stage1_bc_dagger_log.json.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
import time
from typing import Any

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

from moe_jump_model import (
    ACTION_CLIP,
    HERE,
    JUMP_MODE_BIT_INDEX,
    MoEJumpActorCritic,
    StatefulMoEJumpActor,
)
from rl_jump_env import JUMP_GATE_DURATION_S, LEG_DELTA_BOUNDS, Mod4v3RLJumpEnv

DELTA_GRID = np.array([0.348, 0.503, 0.659, 0.809, 0.952, 1.086, 1.210, 1.325, 1.432, 1.532, 1.625, 1.712, 1.752])
MEAN_GRID = np.array([0.4674, 0.4217, 0.3800, 0.3451, 0.3172, 0.2953, 0.2780, 0.2645, 0.2538, 0.2454, 0.2386, 0.2332, 0.2317])


class Stage1JumpOracle:
    """Offline/DAgger trajectory teacher (used ONLY during Stage-1 dataset collection, NEVER at runtime)."""

    def __init__(self, e0_mlp: nn.Module, default_active: np.ndarray):
        self.e0 = e0_mlp
        self.default = default_active.astype(np.float64)
        self.reset()

    def reset(self) -> None:
        self.phase = "DRIVE"
        self.phase_t0 = 0.0
        self.c_delta = np.full(2, 1.02, dtype=np.float64)
        self.push_vx = 0.0
        self.last_window_idx = -1

    def query_action(self, env: Mod4v3RLJumpEnv, obs_np: np.ndarray) -> tuple[np.ndarray, int]:
        """Compute clean [-6, 6] target action for current state visited during DAgger rollout."""
        now = float(env.d.time)
        jump_on = bool(obs_np[JUMP_MODE_BIT_INDEX] > 0.5)

        n_obs = torch.from_numpy(obs_np).unsqueeze(0).clone()
        n_obs[..., 28:35] = torch.tensor([1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        if jump_on:
            dt_g = max(0.0, now - env.window_t0)
            w_h = max(0.0, min(1.0, (JUMP_GATE_DURATION_S - dt_g) / 0.24))
            ref_h = env.height_cmd + w_h * (0.365 - env.height_cmd)
            n_obs[..., 3] = float(ref_h * 5.0)

        with torch.no_grad():
            raw = self.e0(n_obs)[0].numpy().astype(np.float64)

        if not jump_on:
            self.phase = "DRIVE"
            return np.clip(raw, -ACTION_CLIP, ACTION_CLIP).astype(np.float32), 0

        if env.cur_window_idx != self.last_window_idx:
            self.last_window_idx = env.cur_window_idx
            self.phase = "CROUCH"
            self.phase_t0 = now
            self.c_delta = np.full(2, 1.02, dtype=np.float64)

        R = env.d.xmat[env.base_id].reshape(3, 3)
        pitch = math.asin(float(np.clip(-R[2, 0], -1.0, 1.0)))
        roll = math.atan2(float(R[2, 1]), float(R[2, 2]))
        wx, wy = float(env.d.qvel[3]), float(env.d.qvel[4])
        q_legs = env.d.qpos[env.active_qadr[:4]]
        qd_w = env.d.qvel[env.active_dadr[4:6]]
        default = self.default

        raw_mean = np.array(
            [
                0.5 * (default[0] + 0.5 * raw[0] + default[1] + 0.5 * raw[1]),
                0.5 * (default[2] + 0.5 * raw[2] + default[3] + 0.5 * raw[3]),
            ],
            dtype=np.float64,
        )
        raw_delta = np.clip(
            [
                (default[0] + 0.5 * raw[0]) - (default[1] + 0.5 * raw[1]),
                (default[2] + 0.5 * raw[2]) - (default[3] + 0.5 * raw[3]),
            ],
            *LEG_DELTA_BOUNDS,
        )

        el = now - self.phase_t0
        if self.phase == "CROUCH":
            if (el >= 0.40 and env.support_substeps >= 4) or el >= 0.54:
                self.phase, self.phase_t0, el = "PUSH", now, 0.0
                self.push_vx = float(env.body_vx)
        elif self.phase == "PUSH":
            if env.air_substeps >= 4 and env.d.qvel[2] > 0.20 and el >= 0.04:
                self.phase, self.phase_t0, el = "FLIGHT_TUCK", now, 0.0
            elif el >= 0.30:
                self.phase, self.phase_t0, el = "CRUISE_HOLD", now, 0.0
        elif self.phase == "FLIGHT_TUCK":
            if el >= 0.14 and (env.d.qvel[2] <= -0.35 or el >= 0.28):
                self.phase, self.phase_t0, el = "LANDING_EXTEND", now, 0.0
        elif self.phase == "LANDING_EXTEND":
            if env.support_substeps >= 1 and el >= 0.02:
                self.phase, self.phase_t0, el = "SKYHOOK_ABSORB", now, 0.0
            elif el > 0.60:
                self.phase, self.phase_t0, el = "CRUISE_HOLD", now, 0.0
        elif self.phase == "SKYHOOK_ABSORB":
            if el >= 0.34:
                self.phase, self.phase_t0, el = "CRUISE_HOLD", now, 0.0

        phase_code = {
            "DRIVE": 0,
            "CROUCH": 1,
            "PUSH": 2,
            "FLIGHT_TUCK": 3,
            "LANDING_EXTEND": 4,
            "SKYHOOK_ABSORB": 5,
            "CRUISE_HOLD": 6,
        }[self.phase]

        if self.phase == "CRUISE_HOLD":
            return np.clip(raw, -ACTION_CLIP, ACTION_CLIP).astype(np.float32), phase_code

        act = raw.copy()
        if self.phase == "CROUCH":
            ct_base = 0.42 if abs(env.v_cmd_target) > 0.15 else 0.38
            ct = ct_base + 0.03 * abs(env.body_vx)
            self.c_delta = self.c_delta + np.clip(ct - self.c_delta, -1.7 * 0.02, 1.7 * 0.02)
            delta = self.c_delta.copy()
        elif self.phase == "PUSH":
            delta = np.full(2, LEG_DELTA_BOUNDS[1])
        elif self.phase == "FLIGHT_TUCK":
            delta = np.full(2, LEG_DELTA_BOUNDS[1] + (0.173 - LEG_DELTA_BOUNDS[1]) * min(1.0, el / 0.025))
        elif self.phase == "LANDING_EXTEND":
            delta = np.full(2, 0.173 + (1.54 - 0.173) * min(1.0, el / 0.07))
        else:  # SKYHOOK_ABSORB
            fade = max(0.0, 1.0 - el / 0.34)
            delta = (
                raw_delta
                + 0.42 * max(0.0, -float(env.d.qvel[2]))
                + fade * 12.0 * max(0.0, 0.290 - float(env.d.qpos[2]))
            )

        delta = np.clip(delta, *LEG_DELTA_BOUNDS)
        mean = raw_mean.copy()
        cur_ad = 0.5 * float((q_legs[0] - q_legs[1]) + (q_legs[2] - q_legs[3]))

        if self.phase == "CROUCH" and abs(env.cmd_vx) > 0.15:
            mean += 0.030 * env.cmd_vx
        elif self.phase == "PUSH":
            if self.push_vx > 0.15:
                mean += -0.285 + 0.120 * self.push_vx
            else:
                mean += -0.315 + 0.055 * self.push_vx
        elif self.phase == "FLIGHT_TUCK":
            mean += -0.145
        elif self.phase == "LANDING_EXTEND":
            r_air = (
                float(np.interp(cur_ad, DELTA_GRID, MEAN_GRID))
                - 0.55 * pitch
                - 0.20 * env.body_vx
                + 0.16 * max(0.0, env.cmd_vx)
                - 0.06 * (env.body_vx - env.cmd_vx)
            )
            wr = float(np.clip(0.75 - 0.06 * max(0.0, env.body_vx), 0.52, 0.82)) * min(1.0, el / 0.06)
            mean = (1.0 - wr) * raw_mean + wr * np.full(2, r_air)

        for i, (fi, ri) in enumerate(((0, 1), (2, 3))):
            act[fi] = float(2.0 * (mean[i] + 0.5 * delta[i] - default[fi]))
            act[ri] = float(2.0 * (mean[i] - 0.5 * delta[i] - default[ri]))

        if self.phase in ("FLIGHT_TUCK", "LANDING_EXTEND") and env.air_substeps >= 1:
            pr = 0.075 if self.phase == "FLIGHT_TUCK" else 0.0
            pe = pitch - pr
            mt = 0.5 * (10.0 * pe + 1.1 * wy)
            act[4:6] = (qd_w + mt / 0.6) / 10.0
            rc = float(np.clip(0.65 * roll + 0.08 * wx, -0.15, 0.15))
            nd = np.clip(delta + np.array([-rc, rc]), *LEG_DELTA_BOUNDS)
            for i, (fi, ri) in enumerate(((0, 1), (2, 3))):
                act[fi] += float(nd[i] - delta[i])
                act[ri] -= float(nd[i] - delta[i])
            act[:4] += 2.0 * float(np.clip(2.6 * pe + 0.21 * wy, -0.42, 0.42))

        return np.clip(act, -ACTION_CLIP, ACTION_CLIP).astype(np.float32), phase_code


def collect_dagger_round(
    env: Mod4v3RLJumpEnv,
    oracle: Stage1JumpOracle,
    model: MoEJumpActorCritic,
    num_episodes: int,
    beta_teacher: float,
    dr_prob: float,
    dr_max: float,
) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    """Collect closed-loop trajectories where E_jump drives with probability (1 - beta_teacher)."""
    model.eval()
    obs_list, hist_list, act_list, weight_list = [], [], [], []
    anchor_obs, anchor_hist, anchor_act = [], [], []

    accepted_eps = 0
    survived_eps = 0
    peak_rims = []
    scrape_free_eps = 0

    speeds_grid = [-0.6, -0.5, -0.3, 0.0, 0.0, 0.25, 0.4, 0.6, 0.8, 0.8, 1.0, 1.2]

    for ep_i in range(num_episodes):
        dr_s = float(env.rng.uniform(0.15, dr_max)) if env.rng.random() < dr_prob else 0.0
        v_cmd = float(speeds_grid[ep_i % len(speeds_grid)] + env.rng.uniform(-0.06, 0.06))
        v_cmd = float(np.clip(v_cmd, -0.60, 1.25))
        if abs(v_cmd) < 0.08:
            v_cmd = 0.0
        wz_cmd = float(env.rng.uniform(-0.30, 0.30)) if (ep_i % 5 == 4 and abs(v_cmd) <= 0.8) else 0.0
        h_nom = 0.28 if (ep_i % 4 != 3) else float(env.rng.uniform(0.27, 0.365))

        mode_pick = ep_i % 5
        hurdles: list[tuple[float, float]] = []
        if mode_pick == 3 and v_cmd >= 0.60:
            # Multi-jump 2x or 3x
            t1 = float(env.rng.uniform(1.35, 1.55))
            gap = float(env.rng.uniform(1.80, 2.05))
            j_times = (t1, t1 + gap, t1 + 2 * gap)
            max_s = t1 + 2 * gap + 2.0
        elif mode_pick == 4 and 1.00 <= v_cmd <= 1.25:
            # Physical 14-20cm solid box hurdle
            t1 = float(env.rng.uniform(1.50, 1.75))
            apex_x = env.hurdle_apex_x(v_cmd, t1) + float(env.rng.uniform(-0.025, 0.025))
            hurdles = [(apex_x, float(env.rng.uniform(0.14, 0.20)))]
            j_times = (t1,)
            max_s = 4.6
        else:
            t1 = float(env.rng.uniform(1.35, 1.90))
            j_times = (t1,)
            max_s = 4.6

        init_pose = (
            float(env.rng.uniform(-0.04, 0.04)),
            float(env.rng.uniform(-0.05, 0.05)),
            float(env.rng.uniform(-0.035, 0.035)),
        )
        st = env.reset(
            dr_scale=dr_s,
            v_cmd=v_cmd,
            wz_cmd=wz_cmd,
            h_nom=h_nom,
            jump_times=j_times,
            max_episode_s=max_s,
            hurdles=hurdles,
            init_pose=init_pose,
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
                # Upweight critical dynamic phases (PUSH=2, FLIGHT_TUCK=3, LANDING_EXTEND=4, SKYHOOK=5)
                w_frame = 3.0 if ph_code in (2, 3, 4) else (2.0 if ph_code in (1, 5) else 1.0)
                ep_w.append(w_frame)

            # Decide which action actually steps the closed-loop physics
            if obs_np[JUMP_MODE_BIT_INDEX] <= 0.5:
                with torch.no_grad():
                    exec_act = (
                        model.act_deterministic(
                            torch.from_numpy(obs_np).unsqueeze(0),
                            torch.from_numpy(hist_np).unsqueeze(0),
                        )[0]
                        .numpy()
                    )
            elif env.rng.random() < beta_teacher:
                exec_act = target_act
            else:
                with torch.no_grad():
                    exec_act = (
                        model.act_deterministic(
                            torch.from_numpy(obs_np).unsqueeze(0),
                            torch.from_numpy(hist_np).unsqueeze(0),
                        )[0]
                        .numpy()
                    )

            st, _rew, done, info = env.step(exec_act)
            if done:
                survived = info["fell_reason"] == ""
                if survived:
                    survived_eps += 1
                    peak_rims.append(info["ep_peak_rim_cm"])
                clean_scrape = info["ep_guide_force_N"] < 1.0 and info["ep_chassis_force_N"] < 1.0 and info["ep_hurdle_hit_N"] < 1.0
                if survived and clean_scrape:
                    scrape_free_eps += 1

                # In Round 0 (beta=1.0), keep ONLY high-clearance zero-scrape demonstrations.
                # In DAgger Rounds (beta<1.0), keep survived episodes (and recovery corrections before any fall) so student fixes drift!
                keep = (
                    (survived and clean_scrape and info["ep_peak_rim_cm"] >= 28.0)
                    if beta_teacher > 0.99
                    else (len(ep_obs) >= 20 and (survived or beta_teacher < 0.5))
                )
                if keep and len(ep_obs) > 0:
                    accepted_eps += 1
                    obs_list.extend(ep_obs)
                    hist_list.extend(ep_hist)
                    act_list.extend(ep_act)
                    weight_list.extend(ep_w)
                    if survived and clean_scrape and info["ep_peak_rim_cm"] >= 32.5 and dr_s == 0.0:
                        anchor_obs.extend(ep_obs)
                        anchor_hist.extend(ep_hist)
                        anchor_act.extend(ep_act)
                break

    batch = {
        "obs": np.asarray(obs_list, dtype=np.float32),
        "hist": np.asarray(hist_list, dtype=np.float32),
        "act": np.asarray(act_list, dtype=np.float32),
        "weight": np.asarray(weight_list, dtype=np.float32),
        "anchor_obs": np.asarray(anchor_obs, dtype=np.float32) if anchor_obs else np.zeros((0, 35), dtype=np.float32),
        "anchor_hist": np.asarray(anchor_hist, dtype=np.float32) if anchor_hist else np.zeros((0, 420), dtype=np.float32),
        "anchor_act": np.asarray(anchor_act, dtype=np.float32) if anchor_act else np.zeros((0, 6), dtype=np.float32),
    }
    stats = {
        "episodes_run": num_episodes,
        "survived_episodes": survived_eps,
        "scrape_free_episodes": scrape_free_eps,
        "accepted_episodes": accepted_eps,
        "collected_jump_frames": int(len(obs_list)),
        "mean_peak_rim_cm": round(float(np.mean(peak_rims)), 2) if peak_rims else 0.0,
    }
    return batch, stats


def train_ejump_supervised(
    model: MoEJumpActorCritic,
    obs_all: np.ndarray,
    hist_all: np.ndarray,
    act_all: np.ndarray,
    weight_all: np.ndarray,
    epochs: int = 35,
    lr: float = 1.2e-3,
    batch_size: int = 512,
) -> dict[str, float]:
    """Train ONLY PureNeuralJumpExpert (encoder + delta_head) with weighted MSE + Symmetry loss."""
    model.train()
    trainable_params = [
        p for n, p in model.actor_body.e_jump.named_parameters() if p.requires_grad
    ]
    optimizer = torch.optim.AdamW(trainable_params, lr=lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs, eta_min=1.5e-4)

    ds = TensorDataset(
        torch.from_numpy(obs_all),
        torch.from_numpy(hist_all),
        torch.from_numpy(act_all),
        torch.from_numpy(weight_all),
    )
    loader = DataLoader(ds, batch_size=batch_size, shuffle=True, drop_last=False)

    first_loss = last_loss = last_sym = 0.0
    for ep in range(epochs):
        tot_mse, tot_sym, n_b = 0.0, 0.0, 0
        for b_obs, b_hist, b_act, b_w in loader:
            pred = model.actor_body.e_jump(b_obs, b_hist)
            sq_err = ((pred - b_act) ** 2).mean(dim=-1)
            mse_loss = (sq_err * b_w).mean() / b_w.mean()
            sym_loss = model.symmetry_loss(b_obs, b_hist)
            loss = mse_loss + 0.25 * sym_loss

            optimizer.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(trainable_params, 2.0)
            optimizer.step()

            tot_mse += float(mse_loss.item())
            tot_sym += float(sym_loss.item())
            n_b += 1
        scheduler.step()
        avg_mse = tot_mse / max(1, n_b)
        avg_sym = tot_sym / max(1, n_b)
        if ep == 0:
            first_loss = avg_mse
        last_loss, last_sym = avg_mse, avg_sym

    model.eval()
    model.verify_zero_e0_drift()
    return {
        "first_epoch_mse": round(first_loss, 5),
        "final_epoch_mse": round(last_loss, 5),
        "final_sym_loss": round(last_sym, 6),
    }


def eval_pure_neural_suite(model: MoEJumpActorCritic, dr_scale: float = 0.0) -> dict[str, Any]:
    """Evaluate 100% pure StatefulMoEJumpActor (ZERO oracle calls, ZERO privileged state!)."""
    actor = StatefulMoEJumpActor(model)
    env = Mod4v3RLJumpEnv(seed=777)

    cases = [
        ("stand_0p0", 0.0, (1.6,), 4.6, []),
        ("move_0p4", 0.4, (1.6,), 4.6, []),
        ("move_0p8", 0.8, (1.6,), 4.6, []),
        ("move_1p2", 1.2, (1.6,), 4.6, []),
        ("rev_m0p5", -0.5, (1.6,), 4.6, []),
        ("multi3x_0p8", 0.8, (1.4, 3.3, 5.2), 7.2, []),
        ("hurdle18cm_1p20", 1.20, (1.6,), 4.6, [(Mod4v3RLJumpEnv.hurdle_apex_x(1.20, 1.6), 0.18)]),
    ]
    results = {}
    for name, v_cmd, j_times, max_s, hurdles in cases:
        st = env.reset(dr_scale=dr_scale, v_cmd=v_cmd, h_nom=0.28, jump_times=j_times, max_episode_s=max_s, hurdles=hurdles)
        actor.reset_history()
        actor.queue.reset(torch.from_numpy(st["obs"]).unsqueeze(0))
        first_step = True
        while True:
            obs_t = torch.from_numpy(st["obs"]).unsqueeze(0)
            if first_step:
                with torch.inference_mode():
                    act = model.act_deterministic(obs_t, actor.queue.buffer.flatten(-2))[0].numpy()
                first_step = False
            else:
                act = actor(obs_t)[0].numpy()
            st, _r, done, info = env.step(act)
            if done:
                results[name] = {
                    "survived": info["fell_reason"] == "",
                    "peak_rim_cm": info["ep_peak_rim_cm"],
                    "completed_jumps": f"{info['ep_completed_jumps']}/{info['ep_expected_jumps']}",
                    "guide_N": info["ep_guide_force_N"],
                    "chassis_N": info["ep_chassis_force_N"],
                    "hurdles_cleared": f"{info['hurdles_cleared']}/{info['hurdles_total']}",
                }
                break
    return results


def main() -> None:
    t0 = time.perf_counter()
    torch.manual_seed(20261118)
    np.random.seed(20261118)
    torch.set_num_threads(4)

    model = MoEJumpActorCritic()
    model.load_frozen_c874()
    model.verify_zero_e0_drift()

    env = Mod4v3RLJumpEnv(seed=101)
    oracle = Stage1JumpOracle(model.actor_body.e0, env.default_active)

    log_data: dict[str, Any] = {"stages": []}

    # --- Round 0: Pure Oracle Rollouts (150 episodes) ---
    print("=== Stage 1 Round 0: Collecting Clean Multi-Speed / Multi-Jump / Hurdle / DR Demos ===", flush=True)
    b0, s0 = collect_dagger_round(env, oracle, model, num_episodes=150, beta_teacher=1.0, dr_prob=0.40, dr_max=0.75)
    print(f"  Round 0 stats: {s0}", flush=True)

    # Fit and freeze observation normalizer on Round-0 state distribution
    obs_mean = torch.from_numpy(b0["obs"].mean(axis=0))
    obs_std = torch.from_numpy(b0["obs"].std(axis=0) + 0.05)
    model.actor_body.e_jump.set_normalization(obs_mean, obs_std)

    agg_obs, agg_hist, agg_act, agg_w = [b0["obs"]], [b0["hist"]], [b0["act"]], [b0["weight"]]
    anc_obs, anc_hist, anc_act = [b0["anchor_obs"]], [b0["anchor_hist"]], [b0["anchor_act"]]

    tr0 = train_ejump_supervised(model, b0["obs"], b0["hist"], b0["act"], b0["weight"], epochs=35, lr=1.4e-3)
    ev0 = eval_pure_neural_suite(model, dr_scale=0.0)
    print(f"  Round 0 train: {tr0}\n  Round 0 Pure-Neural Eval: {json.dumps(ev0)}", flush=True)
    log_data["stages"].append({"round": 0, "beta_teacher": 1.0, "collection": s0, "train": tr0, "pure_eval_0dr": ev0})

    # --- Round 1: Closed-Loop DAgger (beta = 0.25, 90 episodes) ---
    print("\n=== Stage 1 Round 1: Closed-Loop DAgger (75% Student-Driven) ===", flush=True)
    b1, s1 = collect_dagger_round(env, oracle, model, num_episodes=90, beta_teacher=0.25, dr_prob=0.50, dr_max=0.85)
    print(f"  Round 1 stats: {s1}", flush=True)
    agg_obs.append(b1["obs"])
    agg_hist.append(b1["hist"])
    agg_act.append(b1["act"])
    agg_w.append(b1["weight"])
    if len(b1["anchor_obs"]) > 0:
        anc_obs.append(b1["anchor_obs"])
        anc_hist.append(b1["anchor_hist"])
        anc_act.append(b1["anchor_act"])

    tr1 = train_ejump_supervised(
        model,
        np.concatenate(agg_obs),
        np.concatenate(agg_hist),
        np.concatenate(agg_act),
        np.concatenate(agg_w),
        epochs=28,
        lr=9.0e-4,
    )
    ev1 = eval_pure_neural_suite(model, dr_scale=0.0)
    print(f"  Round 1 train: {tr1}\n  Round 1 Pure-Neural Eval: {json.dumps(ev1)}", flush=True)
    log_data["stages"].append({"round": 1, "beta_teacher": 0.25, "collection": s1, "train": tr1, "pure_eval_0dr": ev1})

    # --- Round 2: Closed-Loop DAgger (beta = 0.00, 100% Pure Student Rollouts, 90 episodes) ---
    print("\n=== Stage 1 Round 2: Closed-Loop DAgger (100% Pure Student-Driven) ===", flush=True)
    b2, s2 = collect_dagger_round(env, oracle, model, num_episodes=90, beta_teacher=0.0, dr_prob=0.60, dr_max=1.0)
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
        epochs=32,
        lr=6.5e-4,
    )
    ev2_0dr = eval_pure_neural_suite(model, dr_scale=0.0)
    ev2_fdr = eval_pure_neural_suite(model, dr_scale=1.0)
    print(f"  Round 2 train: {tr2}\n  Round 2 Pure-Neural Eval (0-DR): {json.dumps(ev2_0dr)}", flush=True)
    print(f"  Round 2 Pure-Neural Eval (Full-DR): {json.dumps(ev2_fdr)}", flush=True)
    log_data["stages"].append(
        {"round": 2, "beta_teacher": 0.0, "collection": s2, "train": tr2, "pure_eval_0dr": ev2_0dr, "pure_eval_fulldr": ev2_fdr}
    )

    # Save clean jump anchor buffer for Stage-2 PPO anti-collapse regularization
    traj_dir = HERE / "trajectories"
    traj_dir.mkdir(parents=True, exist_ok=True)
    a_obs_cat = np.concatenate(anc_obs, axis=0)
    a_hist_cat = np.concatenate(anc_hist, axis=0)
    a_act_cat = np.concatenate(anc_act, axis=0)
    if len(a_obs_cat) > 16384:
        idx = np.random.choice(len(a_obs_cat), size=16384, replace=False)
        a_obs_cat, a_hist_cat, a_act_cat = a_obs_cat[idx], a_hist_cat[idx], a_act_cat[idx]
    anchor_path = traj_dir / "clean_jump_anchor.pt"
    torch.save(
        {
            "obs": torch.from_numpy(a_obs_cat),
            "hist": torch.from_numpy(a_hist_cat),
            "act": torch.from_numpy(a_act_cat),
        },
        anchor_path,
    )

    weights_dir = HERE / "weights"
    ckpt_path = weights_dir / "model_bc_dagger.pt"
    sha = model.save_checkpoint(
        ckpt_path,
        metadata={
            "stage": "stage1_bc_dagger",
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
    (ev_dir / "stage1_bc_dagger_log.json").write_text(json.dumps(log_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nSaved Stage-1 BC+DAgger checkpoint -> {ckpt_path} (SHA={sha[:12]}, wall={log_data['wall_seconds']}s)", flush=True)


if __name__ == "__main__":
    main()
