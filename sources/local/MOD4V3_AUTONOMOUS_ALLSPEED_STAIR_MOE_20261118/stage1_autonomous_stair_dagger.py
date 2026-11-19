# SPDX-License-Identifier: MIT
"""Stage 1: Multi-Round Closed-Loop DAgger for Autonomous All-Speed Stair Climb & Proprioceptive Router.

Trains `AutonomousStairMoE` (`obs_35` + internal `H=40` `1400-D` proprioceptive history -> `act_6` & `g_stair`)
with ZERO runtime privileged inputs:
  - Round 0 (beta=1.00): 200 closed-loop episodes across 10/15/20cm all-speed [0.42..1.68 m/s], heights [0.25..0.37m],
                         W-release, continuous 20+20cm 2-step, AND negative flat/ramp-10-17deg/rough/step-down!
  - Round 1 (beta=0.30): 160 closed-loop student-dominated rollouts + state-driven Oracle relabeling.
  - Round 2 (beta=0.00): 160 100%-pure-student closed-loop rollouts + state-driven Oracle relabeling.
  - Saves `weights/model_stage1_dagger.pt`, `trajectories/clean_stair_anchor.pt`, and `evidence/stage1_dagger_log.json`.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import json
import math
import os
from pathlib import Path
import time
from typing import Any

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import mujoco as mj
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset

from autonomous_stair_env import Mod4v3AutonomousStairEnv, get_shared_arena_assets
from autonomous_stair_moe_model import (
    ACTION_CLIP,
    HERE,
    AutonomousStairActorCritic,
    AutonomousStairMoE,
    canonicalize_normal_obs,
    mirror_action_6,
    mirror_hist_1400,
    mirror_obs_35,
)


class OfflineStateDrivenClimbOracle:
    """Privileged offline Stage-1 DAgger Oracle (NEVER imported at evaluation or runtime!).

    100% causal (triggers strictly AFTER physical riser contact) and state-driven so relabeling
    remains exact even on off-trajectory student states during beta < 1.0 DAgger rollouts.
    """

    def __init__(self, e0_mlp: nn.Module):
        self.e0 = e0_mlp
        self.reset()

    def reset(self) -> None:
        self.active_idx = -1
        self.phase = "CRUISE"
        self.phase_t0 = 0.0
        self.mount_t0 = -1.0
        self.ready_to_surge = False
        self.fast_shallow = False
        self.completed_steps: set[int] = set()

    def query(self, env: Mod4v3AutonomousStairEnv, obs35: np.ndarray) -> tuple[np.ndarray, float, float, float]:
        """Returns `(act_targ_6, g_targ, v_virt_targ, h_virt_targ)`."""
        vc = float(obs35[0])
        wz_c = float(obs35[2])
        h_cmd = float(obs35[3]) / 5.0

        n_obs = obs35.copy()
        n_obs[28:35] = [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        with torch.no_grad():
            a_e0 = self.e0(torch.from_numpy(n_obs).unsqueeze(0))[0].clamp(-ACTION_CLIP, ACTION_CLIP).numpy()

        # Negative (non-stair) scenarios ALWAYS have strict target_gate == 0.0 and exact E0 action!
        if not env.is_positive_stair or not env.active_steps:
            self.phase = "CRUISE"
            return a_e0.astype(np.float32), 0.0, vc, h_cmd

        m, d = env.m, env.d
        t_s = env.k * 0.02
        vx = env.body_vx
        z_base = float(d.qpos[2])
        wpos = d.geom_xpos[env.tire_gids]
        wx_min = float(np.min(wpos[:, 0]))
        wx_mean = float(np.mean(wpos[:, 0]))
        wz_min = float(np.min(wpos[:, 2]))

        # Detect physical contact with any unmounted step
        hit_idx = -1
        tire_riser_hit = False
        for ci in range(d.ncon):
            c = d.contact[ci]
            g1, g2 = int(c.geom1), int(c.geom2)
            for s_i in range(len(env.active_steps)):
                if s_i in self.completed_steps:
                    continue
                sg = env.step_gids[s_i]
                if sg in (g1, g2):
                    f = np.zeros(6)
                    mj.mj_contactForce(m, d, ci, f)
                    if f[0] > 2.0:
                        other = g2 if g1 == sg else g1
                        xf_s, _xb_s, h_s = env.active_steps[s_i]
                        if float(c.pos[0]) < xf_s + 0.045 and wx_min < xf_s - 0.015:
                            hit_idx = max(hit_idx, s_i)
                            if other in env.tire_gids and float(c.pos[2]) < h_s - 0.005:
                                tire_riser_hit = True

        if self.phase == "CRUISE":
            if hit_idx >= 0 and (vc > 0.12 or vx > 0.18):
                self.active_idx = hit_idx
                prev_h = env.active_steps[hit_idx - 1][2] if hit_idx > 0 else 0.0
                rel_h = env.active_steps[hit_idx][2] - prev_h
                self.fast_shallow = bool(rel_h <= 0.115 and vx >= 0.82 and (z_base - prev_h) >= 0.245)
                self.phase = "TUCK_OVER" if self.fast_shallow else "RAISE"
                self.phase_t0 = t_s
                self.mount_t0 = -1.0
                self.ready_to_surge = False
            else:
                return a_e0.astype(np.float32), 0.0, vc, h_cmd

        xf_s, _xb_s, h_s = env.active_steps[self.active_idx]
        prev_h = env.active_steps[self.active_idx - 1][2] if self.active_idx > 0 else 0.0
        rel_h = h_s - prev_h
        h_raise = 0.412
        req_z = prev_h + (0.350 if rel_h <= 0.115 else 0.372)
        v_surge = 1.52 if rel_h <= 0.115 else 1.68

        # State-driven check: are both wheels mounted on step `active_idx`?
        mounted_now = wx_min > xf_s + 0.050 and wz_min > h_s + 0.045
        if mounted_now and self.phase != "STANDUP":
            self.phase = "STANDUP"
            self.phase_t0 = t_s
            self.mount_t0 = t_s

        if self.phase == "RAISE":
            el = t_s - self.phase_t0
            if z_base >= req_z - 0.010 and wx_mean <= xf_s - 0.265:
                self.ready_to_surge = True
            if not self.ready_to_surge:
                v_virt = -0.36 if wx_mean > xf_s - 0.275 else 0.08
            else:
                v_virt = max(v_surge, vc)
            h_virt = h_raise
            if self.ready_to_surge and z_base >= req_z - 0.018 and (tire_riser_hit or wx_mean >= xf_s - 0.090) and vx > 0.58:
                self.phase = "TUCK_OVER"
                self.phase_t0 = t_s
            elif el > 2.30:
                self.phase = "CRUISE"
                return a_e0.astype(np.float32), 0.0, vc, h_cmd

        if self.phase == "TUCK_OVER":
            el = t_s - self.phase_t0
            v_virt = max(v_surge, vc)
            h_virt = 0.205
            if wx_min > xf_s + 0.050 and wz_min > h_s + 0.045:
                self.phase = "STANDUP"
                self.phase_t0 = t_s
                self.mount_t0 = t_s
            elif el > 0.48:
                if wx_min > xf_s + 0.025 and wz_min > h_s + 0.044:
                    self.phase = "STANDUP"
                    self.phase_t0 = t_s
                    self.mount_t0 = t_s
                else:
                    self.phase = "RAISE"
                    self.phase_t0 = t_s
                    self.ready_to_surge = False

        if self.phase == "STANDUP":
            el = t_s - self.phase_t0
            # Fast 0.16s smooth height restoration back to user's h_cmd!
            ramp = min(1.0, el / 0.16)
            h_virt = 0.215 + (h_cmd - 0.215) * ramp
            lip_guard = 0.55 * max(0.0, 1.0 - (wx_min - xf_s) / 0.15)
            taper_v = max(vc, 0.82 * (1.0 - min(1.0, el / 0.16)))
            v_virt = max(vc, lip_guard, taper_v if vc > 0.12 else lip_guard)
            if el >= 0.30 and (z_base - h_s) >= max(0.240, h_cmd - 0.028):
                self.completed_steps.add(self.active_idx)
                self.phase = "CRUISE"
                return a_e0.astype(np.float32), 0.0, vc, h_cmd
            if el >= 0.44:
                self.completed_steps.add(self.active_idx)
                self.phase = "CRUISE"
                return a_e0.astype(np.float32), 0.0, vc, h_cmd

        obs_v = n_obs.copy()
        obs_v[0] = float(v_virt)
        obs_v[2] = float(wz_c)
        obs_v[3] = float(h_virt * 5.0)
        with torch.no_grad():
            act = self.e0(torch.from_numpy(obs_v).unsqueeze(0))[0].clamp(-ACTION_CLIP, ACTION_CLIP).numpy()

        if self.phase == "STANDUP":
            el = t_s - self.phase_t0
            g_targ = float(np.clip(1.0 - (el - 0.14) / 0.16, 0.0, 1.0))
            act = g_targ * act + (1.0 - g_targ) * a_e0
            v_virt_out = g_targ * v_virt + (1.0 - g_targ) * vc
            h_virt_out = g_targ * h_virt + (1.0 - g_targ) * h_cmd
        else:
            g_targ = 1.0
            v_virt_out = float(v_virt)
            h_virt_out = float(h_virt)

        return act.astype(np.float32), g_targ, float(v_virt_out), float(h_virt_out)


def evaluate_pure_neural_suite(moe: AutonomousStairMoE, dr_scale: float = 0.0, seed_base: int = 8100) -> dict[str, Any]:
    """Fast deterministic pure-neural validation (ZERO oracle, ZERO privileged inputs!)."""
    moe.eval()
    env = Mod4v3AutonomousStairEnv(seed=seed_base)

    # 1. 20cm across 4 speeds x 3 offsets = 12 episodes
    s20_ok = 0
    s20_total = 0
    standup_dts: list[float] = []
    for v_i, vc in enumerate([0.50, 0.90, 1.30, 1.60]):
        for o_i, off_mm in enumerate([-50, 0, 50]):
            s20_total += 1
            env.rng = np.random.default_rng(seed_base + 31 * v_i + o_i)
            st = env.reset_scenario(
                kind="stair_1step",
                dr_scale=dr_scale,
                step_heights=(0.20,),
                step_x1=1.50,
                cmd_vx=vc,
                height_cmd=0.28,
                start_x=off_mm / 1000.0,
                max_steps=380,
            )
            moe.reset_history()
            moe.history.reset(torch.from_numpy(st["obs"]).unsqueeze(0))
            while True:
                with torch.inference_mode():
                    act_t, gp_t = moe.forward_with_gate(torch.from_numpy(st["obs"]))
                st, _r, done, info = env.step(act_t.numpy(), float(gp_t.item()))
                if info["steps_graduated"] >= 1 and (env.k * 0.02 - env.step_mount_time[0]) >= 0.85:
                    done = True
                if done:
                    if info["fell_reason"] == "" and info["steps_graduated"] >= 1 and info["final_x"] > 1.62:
                        s20_ok += 1
                        if info["last_standup_dt"] is not None:
                            standup_dts.append(info["last_standup_dt"])
                    break

    # 2. 10cm & 15cm + W-release + Continuous 2-Step (20+20cm) = 8 episodes
    other_cases = [
        ("10cm_0.5", "stair_1step", (0.10,), 0.50, False, 340),
        ("10cm_1.5", "stair_1step", (0.10,), 1.50, False, 320),
        ("15cm_0.5", "stair_1step", (0.15,), 0.50, False, 360),
        ("15cm_1.5", "stair_1step", (0.15,), 1.50, False, 340),
        ("20cm_Wrel", "stair_1step", (0.20,), 0.90, True, 380),
        ("2step_0.7", "stair_2step", (0.20, 0.40), 0.70, False, 480),
        ("2step_1.1", "stair_2step", (0.20, 0.40), 1.10, False, 440),
    ]
    other_ok = 0
    s2step_ok = 0
    wrel_ok = 0
    for idx, (cname, knd, shs, vc, wrel, msteps) in enumerate(other_cases):
        env.rng = np.random.default_rng(seed_base + 500 + idx)
        st = env.reset_scenario(
            kind=knd,
            dr_scale=dr_scale,
            step_heights=shs,
            step_x1=1.50,
            tread_len=1.50,
            cmd_vx=vc,
            height_cmd=0.28,
            w_release=wrel,
            max_steps=msteps,
        )
        moe.reset_history()
        moe.history.reset(torch.from_numpy(st["obs"]).unsqueeze(0))
        while True:
            with torch.inference_mode():
                act_t, gp_t = moe.forward_with_gate(torch.from_numpy(st["obs"]))
            st, _r, done, info = env.step(act_t.numpy(), float(gp_t.item()))
            if done:
                ok = info["fell_reason"] == "" and info["steps_graduated"] >= len(shs)
                if wrel:
                    ok = ok and abs(info["final_vx"]) < 0.06 and info["final_rel_z"] >= 0.258
                    wrel_ok += int(ok)
                if knd == "stair_2step":
                    s2step_ok += int(ok)
                other_ok += int(ok)
                break

    # 3. Negative Zero-False-Positive Scenarios (flat sprint/brake, reverse, 17° ramp up/down, rough, 20cm step-down)
    neg_cases = [
        ("flat_sprint_brake", "flat", 1.70, "sprint_brake"),
        ("flat_reverse_turn", "flat", 1.10, "reverse"),
        ("flat_height_sweep", "flat", 0.90, "height_sweep"),
        ("ramp17_up", "ramp_up", 1.00, "steady"),
        ("ramp17_down", "ramp_down", 0.90, "steady"),
        ("rough_hfield", "rough", 1.10, "steady"),
        ("step_down_20cm", "step_down", 0.90, "steady"),
    ]
    neg_surv = 0
    neg_gates: list[float] = []
    for idx, (_nname, knd, vc, prof) in enumerate(neg_cases):
        env.rng = np.random.default_rng(seed_base + 900 + idx)
        st = env.reset_scenario(
            kind=knd,
            dr_scale=dr_scale,
            cmd_vx=vc,
            height_cmd=0.28,
            ramp_deg=17.0,
            step_down_h=0.20,
            maneuver_profile=prof,
            max_steps=260,
        )
        moe.reset_history()
        moe.history.reset(torch.from_numpy(st["obs"]).unsqueeze(0))
        while True:
            with torch.inference_mode():
                act_t, gp_t = moe.forward_with_gate(torch.from_numpy(st["obs"]))
            st, _r, done, info = env.step(act_t.numpy(), float(gp_t.item()))
            if done:
                if info["fell_reason"] == "":
                    neg_surv += 1
                neg_gates.append(info["mean_g_stair"])
                break

    s20_rate = s20_ok / max(1, s20_total)
    other_rate = other_ok / len(other_cases)
    neg_surv_rate = neg_surv / len(neg_cases)
    mean_neg_g = float(np.mean(neg_gates))
    mean_sdt = float(np.mean(standup_dts)) if standup_dts else 0.99

    score = (
        100.0 * s20_rate
        + 55.0 * other_rate
        + 60.0 * neg_surv_rate
        - 300.0 * max(0.0, mean_neg_g - 0.012)
        - 20.0 * max(0.0, mean_sdt - 0.48)
    )
    return {
        "dr_scale": dr_scale,
        "s20_pass": f"{s20_ok}/{s20_total}",
        "s20_rate": round(s20_rate, 4),
        "other_pass": f"{other_ok}/{len(other_cases)}",
        "2step_pass": f"{s2step_ok}/2",
        "wrel_pass": f"{wrel_ok}/1",
        "mean_standup_dt_s": round(mean_sdt, 3),
        "neg_survival": f"{neg_surv}/{len(neg_cases)}",
        "neg_mean_g_stair": round(mean_neg_g, 5),
        "composite_score": round(score, 3),
    }


def collect_dagger_episodes_parallel(
    ac: AutonomousStairActorCritic,
    num_episodes: int,
    beta_oracle: float,
    dr_max: float,
    neg_prob: float,
    seed_offset: int,
    num_workers: int = 6,
) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    """Collect closed-loop DAgger trajectories in parallel using <= 6 workers."""
    assert num_workers <= 8
    ac.eval()
    get_shared_arena_assets()
    e0_ref = ac.moe.e0
    moe_ref = ac.moe

    ep_per_worker = [num_episodes // num_workers + (1 if i < num_episodes % num_workers else 0) for i in range(num_workers)]

    def _worker_fn(w_idx: int) -> dict[str, Any]:
        env = Mod4v3AutonomousStairEnv(seed=seed_offset + 1009 * w_idx)
        oracle = OfflineStateDrivenClimbOracle(e0_ref)
        obs_l, hist_l, act_l, gt_l, vv_l, hv_l, wt_l = [], [], [], [], [], [], []
        pos_eps = 0
        pos_grad = 0
        neg_eps = 0
        neg_surv = 0

        for ep_local in range(ep_per_worker[w_idx]):
            dr_s = float(env.rng.uniform(0.0, dr_max)) if dr_max > 0.0 and env.rng.random() < 0.65 else 0.0
            st = env.sample_random_training_scenario(dr_scale=dr_s, neg_prob=neg_prob)
            oracle.reset()

            ep_obs, ep_hist, ep_act, ep_gt, ep_vv, ep_hv, ep_wt = [], [], [], [], [], [], []
            survived = True
            while True:
                obs_np = st["obs"]
                hist_np = st["hist"]
                act_targ, g_targ, vv_targ, hv_targ = oracle.query(env, obs_np)

                if beta_oracle >= 0.999:
                    act_exec = act_targ
                    g_stu = g_targ
                else:
                    with torch.inference_mode():
                        out = moe_ref.compute_all_heads(
                            torch.from_numpy(obs_np).unsqueeze(0),
                            torch.from_numpy(hist_np).unsqueeze(0),
                        )
                        act_stu = out["act"][0].numpy()
                        g_stu = float(out["g_prob"][0].item())
                    act_exec = (beta_oracle * act_targ + (1.0 - beta_oracle) * act_stu).astype(np.float32)

                # Weight climb transitions & false-positive student spikes higher so DAgger fixes mistakes fast!
                w_frame = 1.0
                if env.is_positive_stair:
                    if g_targ > 0.02:
                        w_frame = 2.6
                    elif g_stu > 0.08:
                        w_frame = 3.0
                else:
                    w_frame = 3.5 if g_stu > 0.04 else 1.2

                ep_obs.append(obs_np.copy())
                ep_hist.append(hist_np.copy())
                ep_act.append(act_targ.copy())
                ep_gt.append(g_targ)
                ep_vv.append(vv_targ)
                ep_hv.append(hv_targ)
                ep_wt.append(w_frame)

                st, _r, done, info = env.step(act_exec, g_stu)
                # Early exit on clean 1-step climb after 1.1s of post-mount cruising so data focuses on climb + handback!
                if (
                    env.scenario_kind == "stair_1step"
                    and not env.w_release_after_mount
                    and info["steps_graduated"] >= 1
                    and (env.k * 0.02 - env.step_mount_time[0]) >= 1.05
                ):
                    done = True
                if done:
                    survived = info["fell_reason"] == ""
                    if env.is_positive_stair:
                        pos_eps += 1
                        if survived and info["steps_graduated"] >= info["steps_total"]:
                            pos_grad += 1
                    else:
                        neg_eps += 1
                        if survived:
                            neg_surv += 1
                    break

            # For Round 0 (beta=1.0), keep only clean successful episodes for pristine anchor buffer;
            # for DAgger rounds (beta<1.0), keep ALL non-catastrophic frames up to failure so student learns recovery!
            keep = survived if beta_oracle >= 0.999 else (len(ep_obs) >= 15)
            if keep:
                obs_l.extend(ep_obs)
                hist_l.extend(ep_hist)
                act_l.extend(ep_act)
                gt_l.extend(ep_gt)
                vv_l.extend(ep_vv)
                hv_l.extend(ep_hv)
                wt_l.extend(ep_wt)

        return {
            "obs": np.asarray(obs_l, dtype=np.float32),
            "hist": np.asarray(hist_l, dtype=np.float32),
            "act": np.asarray(act_l, dtype=np.float32),
            "gt": np.asarray(gt_l, dtype=np.float32),
            "vv": np.asarray(vv_l, dtype=np.float32),
            "hv": np.asarray(hv_l, dtype=np.float32),
            "wt": np.asarray(wt_l, dtype=np.float32),
            "pos_eps": pos_eps,
            "pos_grad": pos_grad,
            "neg_eps": neg_eps,
            "neg_surv": neg_surv,
        }

    with ThreadPoolExecutor(max_workers=num_workers) as ex:
        parts = list(ex.map(_worker_fn, range(num_workers)))

    data = {
        k: np.concatenate([p[k] for p in parts if len(p[k]) > 0], axis=0)
        for k in ("obs", "hist", "act", "gt", "vv", "hv", "wt")
    }
    tot_pos = sum(p["pos_eps"] for p in parts)
    tot_grad = sum(p["pos_grad"] for p in parts)
    tot_neg = sum(p["neg_eps"] for p in parts)
    tot_nsurv = sum(p["neg_surv"] for p in parts)
    stats = {
        "frames": int(len(data["obs"])),
        "positive_graduated": f"{tot_grad}/{tot_pos}",
        "negative_survived": f"{tot_nsurv}/{tot_neg}",
        "active_gate_fraction": round(float((data["gt"] > 0.05).mean()), 4),
    }
    return data, stats


def train_dagger_epoch_loop(
    ac: AutonomousStairActorCritic,
    dataset_dict: dict[str, torch.Tensor],
    epochs: int,
    lr: float,
    batch_size: int = 256,
) -> dict[str, float]:
    torch.set_num_threads(2)
    ac.train()
    trainable_params = [
        p
        for n, p in ac.moe.named_parameters()
        if p.requires_grad and not n.startswith("e0.") and not n.startswith("e1_stair.loco_base.")
    ]
    opt = torch.optim.AdamW(trainable_params, lr=lr, weight_decay=1e-4)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=epochs, eta_min=lr * 0.15)

    ds = TensorDataset(
        dataset_dict["obs"],
        dataset_dict["hist"],
        dataset_dict["act"],
        dataset_dict["gt"],
        dataset_dict["vv"],
        dataset_dict["hv"],
        dataset_dict["wt"],
    )
    loader = DataLoader(ds, batch_size=batch_size, shuffle=True, drop_last=False)

    last_metrics = {}
    for _ep in range(epochs):
        tot_loss = 0.0
        tot_act = 0.0
        tot_gate = 0.0
        n_b = 0
        for b_obs, b_hist, b_act, b_gt, b_vv, b_hv, b_wt in loader:
            out = ac.moe.compute_all_heads(b_obs, b_hist)
            g_logit = out["g_logit"]
            g_prob = out["g_prob"]
            g_eff = out["g_eff"]

            # 1. Router loss: weighted BCE + hard false-positive suppression on non-stair frames!
            bce_raw = F.binary_cross_entropy_with_logits(g_logit, b_gt, reduction="none")
            pos_boost = torch.where(b_gt > 0.1, 2.2, 1.0)
            neg_mask = (b_gt < 0.01).float()
            fp_pen = neg_mask * (3.5 * g_prob + 10.0 * (g_eff ** 2))
            loss_gate = (b_wt * (pos_boost * bce_raw + fp_pen)).mean()

            # 2. Expert virtual-(v,h) + expert action supervision on active stair frames
            stair_mask = (b_gt > 0.03).float()
            stair_denom = stair_mask.sum().clamp_min(1.0)
            loss_vh = (
                stair_mask
                * (
                    F.smooth_l1_loss(out["v_virt"], b_vv, reduction="none", beta=0.10)
                    + 5.0 * F.smooth_l1_loss(out["h_virt"], b_hv, reduction="none", beta=0.02)
                )
            ).sum() / stair_denom
            loss_stair_act = (
                stair_mask * F.smooth_l1_loss(out["a_stair"], b_act, reduction="none", beta=0.15).mean(dim=-1)
            ).sum() / stair_denom

            # 3. End-to-end closed-loop blended MoE action loss across all frames
            act_err = F.smooth_l1_loss(out["act"], b_act, reduction="none", beta=0.12).mean(dim=-1)
            loss_blend = (b_wt * act_err).mean()

            # 4. Bilateral left-right symmetry regularization (prevents yaw drift during climb!)
            m_obs = mirror_obs_35(b_obs)
            m_hist = mirror_hist_1400(b_hist)
            m_out = ac.moe.compute_all_heads(m_obs, m_hist)
            loss_sym = 0.15 * (
                F.mse_loss(m_out["g_logit"], g_logit.detach())
                + F.mse_loss(m_out["act"], mirror_action_6(out["act"].detach()))
            )

            loss = 2.0 * loss_blend + 1.5 * loss_stair_act + 1.2 * loss_vh + 1.4 * loss_gate + loss_sym
            opt.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(trainable_params, 1.5)
            opt.step()

            tot_loss += float(loss.item())
            tot_act += float(loss_blend.item())
            tot_gate += float(loss_gate.item())
            n_b += 1
        sched.step()
        last_metrics = {
            "total_loss": round(tot_loss / max(1, n_b), 5),
            "blend_act_loss": round(tot_act / max(1, n_b), 5),
            "router_loss": round(tot_gate / max(1, n_b), 5),
        }

    ac.verify_zero_e0_drift()
    return last_metrics


def main() -> None:
    t0 = time.perf_counter()
    torch.manual_seed(20261118)
    np.random.seed(20261118)
    torch.set_num_threads(2)

    ac = AutonomousStairActorCritic()
    ac.load_frozen_c874()
    ac.verify_zero_e0_drift()

    agg_data: dict[str, list[np.ndarray]] = {k: [] for k in ("obs", "hist", "act", "gt", "vv", "hv", "wt")}
    anchor_data: dict[str, torch.Tensor] | None = None
    round_logs: list[dict[str, Any]] = []

    rounds = [
        # (round_idx, beta_oracle, num_episodes, dr_max, neg_prob, epochs, lr)
        (0, 1.00, 210, 0.35, 0.30, 20, 9.0e-4),
        (1, 0.30, 168, 0.65, 0.30, 18, 6.0e-4),
        (2, 0.00, 168, 0.85, 0.32, 20, 4.5e-4),
    ]

    best_score = -1e9
    best_ckpt = HERE / "weights/model_stage1_dagger.pt"

    for r_idx, beta, n_eps, dr_m, neg_p, n_ep, lr in rounds:
        rt0 = time.perf_counter()
        raw_d, col_stats = collect_dagger_episodes_parallel(
            ac=ac,
            num_episodes=n_eps,
            beta_oracle=beta,
            dr_max=dr_m,
            neg_prob=neg_p,
            seed_offset=10000 + 5000 * r_idx,
            num_workers=6,
        )
        for k in agg_data:
            agg_data[k].append(raw_d[k])

        if r_idx == 0:
            # Set encoder normalization from Round-0 clean closed-loop proprioception
            c_obs = canonicalize_normal_obs(torch.from_numpy(raw_d["obs"]))
            mean = c_obs.mean(dim=0)
            scale = c_obs.std(dim=0).clamp_min(0.02)
            ac.moe.encoder.set_normalization(mean, scale)

            # Save subsampled clean anchor buffer for Stage-2 PPO anti-forgetting regularization
            n_anc = min(16384, len(raw_d["obs"]))
            idx_anc = np.random.choice(len(raw_d["obs"]), size=n_anc, replace=False)
            anchor_data = {
                "obs": torch.from_numpy(raw_d["obs"][idx_anc]).clone(),
                "hist": torch.from_numpy(raw_d["hist"][idx_anc]).clone(),
                "act": torch.from_numpy(raw_d["act"][idx_anc]).clone(),
                "gt": torch.from_numpy(raw_d["gt"][idx_anc]).clone(),
                "vv": torch.from_numpy(raw_d["vv"][idx_anc]).clone(),
                "hv": torch.from_numpy(raw_d["hv"][idx_anc]).clone(),
            }
            anc_path = HERE / "trajectories/clean_stair_anchor.pt"
            anc_path.parent.mkdir(parents=True, exist_ok=True)
            torch.save(anchor_data, anc_path)

        merged_t = {k: torch.from_numpy(np.concatenate(agg_data[k], axis=0)) for k in agg_data}
        train_stats = train_dagger_epoch_loop(ac, merged_t, epochs=n_ep, lr=lr, batch_size=256)
        val_0dr = evaluate_pure_neural_suite(ac.moe, dr_scale=0.0)
        val_fdr = evaluate_pure_neural_suite(ac.moe, dr_scale=1.0)
        comb_score = 0.60 * val_0dr["composite_score"] + 0.40 * val_fdr["composite_score"]

        r_log = {
            "round": r_idx,
            "beta_oracle": beta,
            "collection": col_stats,
            "total_aggregated_frames": int(len(merged_t["obs"])),
            "train": train_stats,
            "val_0dr": val_0dr,
            "val_fulldr": val_fdr,
            "combined_score": round(comb_score, 3),
            "wall_s": round(time.perf_counter() - rt0, 2),
        }
        round_logs.append(r_log)
        print(
            f"[Stage1 DAgger R{r_idx} beta={beta:.2f}] frames={len(merged_t['obs'])} | "
            f"0-DR: 20cm={val_0dr['s20_pass']} other={val_0dr['other_pass']} 2step={val_0dr['2step_pass']} "
            f"sdt={val_0dr['mean_standup_dt_s']:.2f}s neg_surv={val_0dr['neg_survival']} neg_g={val_0dr['neg_mean_g_stair']:.4f} | "
            f"Full-DR: 20cm={val_fdr['s20_pass']} neg_surv={val_fdr['neg_survival']} | wall={r_log['wall_s']:.1f}s",
            flush=True,
        )

        if comb_score >= best_score:
            best_score = comb_score
            sha = ac.save_checkpoint(best_ckpt, metadata={"stage": f"stage1_dagger_r{r_idx}", "log": r_log})
            print(f"  -> Saved best Stage-1 checkpoint {best_ckpt.name} (SHA256={sha[:12]} score={best_score:.2f})", flush=True)

    ev_dir = HERE / "evidence"
    ev_dir.mkdir(parents=True, exist_ok=True)
    (ev_dir / "stage1_dagger_log.json").write_text(
        json.dumps({"rounds": round_logs, "total_wall_s": round(time.perf_counter() - t0, 2)}, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"[Stage 1 Complete] Total wall time: {time.perf_counter() - t0:.1f}s", flush=True)


if __name__ == "__main__":
    main()
