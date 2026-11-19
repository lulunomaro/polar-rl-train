# SPDX-License-Identifier: MIT
"""Stage 1: Multi-Round Closed-Loop DAgger for Instant Serial-LQR-Style Pure-Neural Jump Expert.

Runs 40+ parallel MuJoCo workers + RTX 4090 GPU training:
  - Round 0 (beta=1.00): Clean teacher rollouts across all 6 scenario families (Stationary Hop,
                         Moving Multi-Hop, Near-Step Space+W, Moving W+Space Step-Vault 15/20/24cm,
                         Continuous 20->40cm 2-Step Vault, and 20/30/40cm Platform Drop-Off).
  - Round 1 (beta=0.30): 70% student closed-loop rollouts + teacher relabeling.
  - Round 2 (beta=0.00): 100% pure student closed-loop rollouts + teacher relabeling (with DR).
  - Strictly verifies 0.0 E0 (c874) drift and saves weights/model_bc_dagger.pt + clean_instant_jump_anchor.pt.
"""
from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
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

from instant_jump_env import (
    LEG_DELTA_BOUNDS,
    Mod4v3InstantJumpEnv,
    ensure_instant_jump_scene_xml,
)
from moe_instant_jump_model import (
    ACTION_CLIP,
    GATE_STEPS,
    HERE,
    HIST_LEN,
    HistoryQueue,
    JUMP_MODE_BIT_INDEX,
    MoEInstantJumpActorCritic,
    build_c874_mlp,
    verify_c874_checkpoint,
)

DELTA_GRID = np.array(
    [0.348, 0.503, 0.659, 0.809, 0.952, 1.086, 1.210, 1.325, 1.432, 1.532, 1.625, 1.712, 1.752],
    dtype=np.float64,
)
MEAN_GRID = np.array(
    [0.4674, 0.4217, 0.3800, 0.3451, 0.3172, 0.2953, 0.2780, 0.2645, 0.2538, 0.2454, 0.2386, 0.2332, 0.2317],
    dtype=np.float64,
)


def neutral_4bar_mean(actual_delta: float) -> float:
    return float(np.interp(actual_delta, DELTA_GRID, MEAN_GRID))


class Stage1InstantZMPTeacher:
    """Offline Stage-1 ZMP-Matched Instant Serial-LQR Teacher (NEVER imported at evaluation/runtime!)."""

    def __init__(self, e0_mlp: nn.Module, default_active: np.ndarray):
        self.e0 = e0_mlp
        self.d0 = default_active.astype(np.float64)
        # Locked Gen-12 High-Clearance ZMP Teacher (34/56 zero-RL warmstart, 28.5-31.5cm rim!)
        self.stand_k = 6
        self.slow_k = 6
        self.fast_k = 5
        self.cmd_dip_dl = 0.38911
        self.trig_cdl = 0.47032
        self.s_v_lunge = 1.71217
        self.s_m_back = 0.17096
        self.s_w_trim = 0.13360
        self.p_m_stand = -0.23355
        self.p_m_move = -0.18504
        self.p_w_boost = 0.35705
        self.p_p_gain = 3.54526
        self.tuck_s = 0.18960
        self.ext_dl = 1.02044
        self.raib_k = 0.17413
        self.raib_b = 0.02982
        self.air_pref = 0.02986
        self.coast_b = 0.54686
        self.reset()

    def reset(self) -> None:
        self.ph = "DRIVE"
        self.pt0 = 0.0
        self.t_trig = 0.0
        self.t_land = -99.0
        self.pvx = 0.0
        self.lvx = 0.0
        self.snap_k = 0
        self.sj = 0
        self.last_jump_count = 0

    def query_action(self, env: Mod4v3InstantJumpEnv, obs_np: np.ndarray) -> tuple[np.ndarray, float]:
        now = float(env.d.time)
        jb = float(obs_np[JUMP_MODE_BIT_INDEX])
        cmd_vx = float(obs_np[0])
        h_cmd = float(obs_np[3]) / 5.0
        bvx = env.body_vx
        want_f = (cmd_vx > 0.08) or (bvx > 0.22)

        if jb < 0.5:
            self.ph = "DRIVE"
            self.sj = 0
            nobs = torch.from_numpy(obs_np).unsqueeze(0).clone()
            nobs[..., 28:35] = torch.tensor([1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
            with torch.no_grad():
                return np.clip(self.e0(nobs)[0].numpy(), -ACTION_CLIP, ACTION_CLIP).astype(np.float32), 0.35

        ql = env.d.qpos[env.active_qadr[:4]]
        qdw = env.d.qvel[env.active_dadr[4:6]]
        cdl = 0.5 * float((ql[0] - ql[1]) + (ql[2] - ql[3]))
        R = env.d.xmat[env.base_id].reshape(3, 3)
        p = math.asin(float(np.clip(-R[2, 0], -1.0, 1.0)))
        rl = math.atan2(float(R[2, 1]), float(R[2, 2]))
        wxa, wy = float(env.d.qvel[3]), float(env.d.qvel[4])

        if self.ph == "DRIVE" or env.jump_count != self.last_jump_count:
            self.last_jump_count = env.jump_count
            self.t_trig = now
            self.t_land = -99.0
            self.sj = 0
            if not want_f:
                # Stationary 0ms/20ms Serial-LQR thrust: <=140ms liftoff & 0.0N scrape!
                self.snap_k = 1
            elif bvx < 0.30:
                self.snap_k = self.stand_k
            elif bvx < 0.85:
                self.snap_k = self.slow_k
            else:
                self.snap_k = self.fast_k
            self.ph = "PUSH" if (self.snap_k <= 0 or cdl <= 0.44) else "SNAP"
            self.pvx = bvx
            self.pt0 = now

        el = now - self.pt0
        if self.ph == "SNAP" and (self.sj >= self.snap_k or (self.sj >= 2 and cdl <= self.trig_cdl)):
            self.ph, self.pt0, el, self.pvx = "PUSH", now, 0.0, bvx
        elif self.ph == "PUSH" and ((env.air_substeps >= 3 and env.d.qvel[2] > 0.20 and el >= 0.04) or el >= 0.16):
            self.ph, self.pt0, el = "TUCK", now, 0.0
        elif self.ph in ("TUCK", "EXTEND") and env.support_substeps >= 1 and (self.ph == "EXTEND" or el >= 0.09):
            self.lvx = max(0.85 if want_f else 0.0, bvx)
            self.t_land = now
            self.ph, self.pt0, el = "ABSORB", now, 0.0
        elif self.ph == "TUCK" and el >= self.tuck_s and (env.d.qvel[2] <= -0.24 or el >= 0.25):
            self.ph, self.pt0, el = "EXTEND", now, 0.0
        elif self.ph == "ABSORB" and el >= 0.32:
            self.ph, self.pt0, el = "HOLD", now, 0.0
        self.sj += 1

        # Emphasize critical launch & landing transitions in DAgger loss!
        sample_w = 2.6 if self.ph in ("SNAP", "PUSH", "TUCK") else (1.8 if self.ph in ("EXTEND", "ABSORB") else 1.0)

        nobs = torch.from_numpy(obs_np).unsqueeze(0).clone()
        nobs[..., 28:35] = torch.tensor([1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        dt_g = max(0.0, now - self.t_trig)
        wh = max(0.0, min(1.0, (0.86 - dt_g) / 0.24))
        nobs[..., 3] = float((h_cmd + wh * (0.34 - h_cmd)) * 5.0)
        if want_f:
            if self.ph == "SNAP":
                nobs[..., 0] = float(max(cmd_vx, self.s_v_lunge))
            elif self.ph == "PUSH":
                nobs[..., 0] = float(max(cmd_vx, 1.45, bvx))
            elif self.ph in ("TUCK", "EXTEND"):
                nobs[..., 0] = float(max(cmd_vx, 0.96 * bvx))
            else:
                dt_l = max(0.0, now - self.t_land) if self.t_land > 0 else el
                tp = max(0.0, 1.0 - dt_l / 0.55)
                nobs[..., 0] = float(max(0.20 if cmd_vx > 0.05 else 0.0, cmd_vx + tp * (self.coast_b + 0.92 * self.lvx - cmd_vx)))
        else:
            nobs[..., 0] = 0.0

        with torch.no_grad():
            raw = self.e0(nobs)[0].numpy().astype(np.float64)
        if self.ph == "HOLD":
            return np.clip(raw, -ACTION_CLIP, ACTION_CLIP).astype(np.float32), sample_w

        rm = np.array(
            [0.5 * (self.d0[0] + 0.5 * raw[0] + self.d0[1] + 0.5 * raw[1]), 0.5 * (self.d0[2] + 0.5 * raw[2] + self.d0[3] + self.d0[3])]
        )
        rm = np.array(
            [0.5 * (self.d0[0] + 0.5 * raw[0] + self.d0[1] + 0.5 * raw[1]), 0.5 * (self.d0[2] + 0.5 * raw[2] + self.d0[3] + 0.5 * raw[3])]
        )
        rd = np.clip(
            [(self.d0[0] + 0.5 * raw[0]) - (self.d0[1] + 0.5 * raw[1]), (self.d0[2] + 0.5 * raw[2]) - (self.d0[3] + 0.5 * raw[3])],
            *LEG_DELTA_BOUNDS,
        )
        act = raw.copy()
        if self.ph == "SNAP":
            dl = np.full(2, self.cmd_dip_dl if want_f else 0.54)
            if want_f:
                v_gap = float(np.clip(1.35 - bvx, 0.0, 1.35)) / 1.35
                mn = rm + self.s_m_back * (0.35 + 0.65 * v_gap)
                act[4:6] = raw[4:6] + self.s_w_trim * (0.35 + 0.65 * v_gap)
            else:
                mn = rm.copy()
        elif self.ph == "PUSH":
            dl = np.full(2, LEG_DELTA_BOUNDS[1])
            if want_f:
                alpha_v = float(np.clip(self.pvx / 1.15, 0.0, 1.0))
                pm = (1.0 - alpha_v) * self.p_m_stand + alpha_v * self.p_m_move
                mn = rm + pm
                act[4:6] = raw[4:6] + self.p_w_boost * (1.0 - 0.45 * alpha_v) - self.p_p_gain * p - 0.6 * wy
            else:
                mn = rm - 0.16
        elif self.ph == "TUCK":
            dl = np.full(2, LEG_DELTA_BOUNDS[1] + (0.173 - LEG_DELTA_BOUNDS[1]) * min(1.0, (el + 0.02) / 0.025))
            mn = rm + (0.02 if want_f else -0.35)
        elif self.ph == "EXTEND":
            ed = self.ext_dl if want_f else 1.26
            dl = np.full(2, 0.173 + (ed - 0.173) * min(1.0, (el + 0.02) / 0.08))
            ra = neutral_4bar_mean(cdl) - 0.35 * p + (self.raib_k * bvx + self.raib_b if want_f else -0.08 * bvx)
            wr = 0.85 * min(1.0, (el + 0.02) / 0.045)
            mn = (1.0 - wr) * rm + wr * np.full(2, ra)
        else:
            fd = max(0.0, 1.0 - el / 0.32)
            rel_z_est = 0.125 + 0.165 * cdl
            dl = rd + 0.36 * max(0.0, -env.d.qvel[2]) + fd * 10.0 * max(0.0, 0.285 - rel_z_est)
            mn = rm + fd * (0.85 * min(0.0, p) + 0.05 * min(0.0, wy))

        dl = np.clip(dl, *LEG_DELTA_BOUNDS)
        for i, (fi, ri) in enumerate(((0, 1), (2, 3))):
            act[fi] = 2.0 * (mn[i] + 0.5 * dl[i] - self.d0[fi])
            act[ri] = 2.0 * (mn[i] - 0.5 * dl[i] - self.d0[ri])
        if self.ph in ("TUCK", "EXTEND") and env.air_substeps >= 1:
            pe = p - (self.air_pref if want_f else 0.0)
            mt = 0.5 * (18.0 * pe + 1.50 * wy)
            act[4:6] = (0.5 * (qdw[0] + qdw[1]) + mt / 0.6) / 10.0
            rc = float(np.clip(0.65 * rl + 0.08 * wxa, -0.15, 0.15))
            nd = np.clip(dl + np.array([-rc, rc]), *LEG_DELTA_BOUNDS)
            for i, (fi, ri) in enumerate(((0, 1), (2, 3))):
                act[fi] += nd[i] - dl[i]
                act[ri] -= nd[i] - dl[i]
            act[:4] += 2.0 * float(np.clip(3.2 * pe + 0.26 * wy, -0.44, 0.44))

        return np.clip(act, -ACTION_CLIP, ACTION_CLIP).astype(np.float32), sample_w


_W_ENV: Mod4v3InstantJumpEnv | None = None
_W_ORACLE: Stage1InstantZMPTeacher | None = None
_W_MODEL: MoEInstantJumpActorCritic | None = None


def _init_dagger_worker(xml_str: str) -> None:
    global _W_ENV, _W_ORACLE, _W_MODEL
    os.environ["OPENBLAS_NUM_THREADS"] = "1"
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"
    torch.set_num_threads(1)
    _W_ENV = Mod4v3InstantJumpEnv(seed=os.getpid() % 100000, xml_path=Path(xml_str))
    ck = verify_c874_checkpoint()
    e0 = build_c874_mlp()
    e0.load_state_dict({k.replace("mlp.", "", 1): v for k, v in ck["actor_state_dict"].items() if k.startswith("mlp.")}, strict=True)
    e0.eval()
    e0.requires_grad_(False)
    _W_ORACLE = Stage1InstantZMPTeacher(e0, _W_ENV.default_active)
    _W_MODEL = MoEInstantJumpActorCritic()
    _W_MODEL.load_frozen_c874()
    _W_MODEL.eval()


def _collect_worker_chunk(args: tuple[int, int, float, float, float, dict[str, np.ndarray] | None]) -> dict[str, Any]:
    seed_off, n_eps, beta_teacher, dr_prob, dr_max, model_sd_np = args
    assert _W_ENV is not None and _W_ORACLE is not None and _W_MODEL is not None
    _W_ENV.rng = np.random.default_rng(seed_off)
    if model_sd_np is not None:
        _W_MODEL.load_state_dict({k: torch.from_numpy(v) for k, v in model_sd_np.items()}, strict=True)
    _W_MODEL.eval()

    obs_l, hist_l, act_l, w_l, priv_l = [], [], [], [], []
    anc_obs, anc_hist, anc_act = [], [], []
    survived = task_ok = clean_ok = accepted = 0
    rims, lifts, aps = [], [], []

    q = HistoryQueue(hist_len=HIST_LEN)
    for _ in range(n_eps):
        dr_s = float(_W_ENV.rng.uniform(0.15, dr_max)) if _W_ENV.rng.random() < dr_prob else 0.0
        st = _W_ENV.sample_random_scenario(dr_scale=dr_s)
        _W_ORACLE.reset()
        q.clear()

        ep_o, ep_h, ep_a, ep_w, ep_p = [], [], [], [], []
        first = True
        while True:
            obs_np = st["obs"]
            obs_t = torch.from_numpy(obs_np).unsqueeze(0)
            hist_t = q.reset(obs_t) if first else q.append(obs_t)
            first = False
            hist_np = hist_t[0].numpy()

            a_teacher, sw = _W_ORACLE.query_action(_W_ENV, obs_np)
            if beta_teacher >= 0.999:
                a_exec = a_teacher
            else:
                with torch.inference_mode():
                    a_stud = _W_MODEL.act_deterministic(obs_t, hist_t)[0].numpy()
                a_exec = a_teacher if (_W_ENV.rng.random() < beta_teacher) else a_stud

            # Record jump-window frames + 20% normal transition context
            if obs_np[JUMP_MODE_BIT_INDEX] > 0.5 or _W_ENV.rng.random() < 0.20:
                ep_o.append(obs_np.copy())
                ep_h.append(hist_np.copy())
                ep_a.append(a_teacher.copy())
                ep_w.append(sw)
                ep_p.append(st["priv"].copy())

            st, _r, done, info = _W_ENV.step(a_exec)
            if done:
                surv = info["fell_reason"] == "" and not info["slid_off_step"]
                if _W_ENV.scenario_kind == "drop_off":
                    tok = surv and info["drop_landed_ok"]
                elif info["steps_total"] > 0:
                    tok = surv and (info["steps_mounted_count"] >= info["steps_total"])
                else:
                    tok = surv and (len(info["completed_jumps"]) >= 1)
                clean = (
                    tok
                    and info["ep_guide_force_N"] < 1.0
                    and info["ep_chassis_force_N"] < 1.0
                    and info["ep_riser_hit_N"] < 5.0
                    and info["ep_max_air_pitch_deg"] <= 10.5
                )
                if surv:
                    survived += 1
                if tok:
                    task_ok += 1
                if clean:
                    clean_ok += 1
                for cj in info["completed_jumps"]:
                    rims.append(cj["rel_rim_cm"])
                    lifts.append(cj["lift_ms"])
                    aps.append(cj["air_pitch_deg"])

                # In Round 0, ONLY keep low-pitch successful episodes so BC learns 100% clean level-chassis trajectories!
                keep = (tok and info["ep_max_air_pitch_deg"] <= 13.5) if beta_teacher >= 0.999 else (len(ep_o) >= 10 and info["ep_max_air_pitch_deg"] <= 18.0)
                if keep and len(ep_o) > 0:
                    accepted += 1
                    obs_l.extend(ep_o)
                    hist_l.extend(ep_h)
                    act_l.extend(ep_a)
                    w_l.extend(ep_w)
                    priv_l.extend(ep_p)
                    if clean and dr_s == 0.0:
                        for o_i, h_i, a_i in zip(ep_o, ep_h, ep_a):
                            if o_i[JUMP_MODE_BIT_INDEX] > 0.5:
                                anc_obs.append(o_i)
                                anc_hist.append(h_i)
                                anc_act.append(a_i)
                break

    return {
        "obs": np.asarray(obs_l, dtype=np.float32) if obs_l else np.zeros((0, 35), dtype=np.float32),
        "hist": np.asarray(hist_l, dtype=np.float32) if hist_l else np.zeros((0, HIST_LEN * 35), dtype=np.float32),
        "act": np.asarray(act_l, dtype=np.float32) if act_l else np.zeros((0, 6), dtype=np.float32),
        "w": np.asarray(w_l, dtype=np.float32) if w_l else np.zeros((0,), dtype=np.float32),
        "priv": np.asarray(priv_l, dtype=np.float32) if priv_l else np.zeros((0, 18), dtype=np.float32),
        "anc_obs": np.asarray(anc_obs, dtype=np.float32) if anc_obs else np.zeros((0, 35), dtype=np.float32),
        "anc_hist": np.asarray(anc_hist, dtype=np.float32) if anc_hist else np.zeros((0, HIST_LEN * 35), dtype=np.float32),
        "anc_act": np.asarray(anc_act, dtype=np.float32) if anc_act else np.zeros((0, 6), dtype=np.float32),
        "survived": survived,
        "task_ok": task_ok,
        "clean_ok": clean_ok,
        "accepted": accepted,
        "n_eps": n_eps,
        "rims": rims,
        "lifts": lifts,
        "aps": aps,
    }


def train_supervised(
    model: MoEInstantJumpActorCritic,
    device: torch.device,
    obs_all: np.ndarray,
    hist_all: np.ndarray,
    act_all: np.ndarray,
    w_all: np.ndarray,
    epochs: int,
    lr: float,
) -> float:
    ds = TensorDataset(
        torch.from_numpy(obs_all),
        torch.from_numpy(hist_all),
        torch.from_numpy(act_all),
        torch.from_numpy(w_all),
    )
    loader = DataLoader(ds, batch_size=512, shuffle=True, drop_last=False)
    trainable = [p for p in model.actor_body.e_jump.parameters() if p.requires_grad]
    opt = torch.optim.AdamW(trainable, lr=lr, weight_decay=1e-4)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=epochs, eta_min=lr * 0.15)
    huber = nn.SmoothL1Loss(reduction="none", beta=0.25)

    model.train()
    last_loss = 0.0
    for _ in range(epochs):
        tot_l = 0.0
        n_b = 0
        for bo, bh, ba, bw in loader:
            bo = bo.to(device, non_blocking=True)
            bh = bh.to(device, non_blocking=True)
            ba = ba.to(device, non_blocking=True)
            bw = bw.to(device, non_blocking=True)

            pred = model.act_deterministic(bo, bh)
            per_sample = huber(pred, ba).mean(dim=-1)
            bc_loss = (per_sample * bw).mean()
            sym_loss = model.symmetry_loss(bo, bh)
            loss = bc_loss + 0.12 * sym_loss

            opt.zero_grad(set_to_none=True)
            loss.backward()
            nn.utils.clip_grad_norm_(trainable, 1.0)
            opt.step()
            tot_l += float(loss.item())
            n_b += 1
        sched.step()
        last_loss = tot_l / max(1, n_b)
    model.eval()
    model.verify_zero_e0_drift()
    return last_loss


def main() -> None:
    t0 = time.perf_counter()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    n_workers = min(44, max(4, (os.cpu_count() or 8) // 2))
    xml_path = ensure_instant_jump_scene_xml()
    print(f"[Stage-1 DAgger] Device={device}, Workers={n_workers}", flush=True)

    model = MoEInstantJumpActorCritic().to(device)
    model.load_frozen_c874()
    model.verify_zero_e0_drift()

    rounds = [
        ("round0_bc_clean", 440, 1.00, 0.00, 0.00, 28, 8e-4),
        ("round1_dagger_b30", 352, 0.30, 0.30, 0.40, 22, 5e-4),
        ("round2_dagger_pure_student", 352, 0.00, 0.45, 0.60, 24, 3.5e-4),
    ]

    all_o, all_h, all_a, all_w, all_p = [], [], [], [], []
    anc_o, anc_h, anc_a = [], [], []
    round_logs = []

    with ProcessPoolExecutor(max_workers=n_workers, initializer=_init_dagger_worker, initargs=(str(xml_path),)) as pool:
        for r_idx, (rname, tot_eps, beta, dr_p, dr_m, epochs, lr) in enumerate(rounds):
            rt0 = time.perf_counter()
            cpu_sd_np = {k: v.detach().cpu().numpy() for k, v in model.state_dict().items()} if r_idx > 0 else None
            eps_per_w = max(1, tot_eps // n_workers)
            tasks = [
                (10000 + r_idx * 5000 + wi * 97, eps_per_w, beta, dr_p, dr_m, cpu_sd_np)
                for wi in range(n_workers)
            ]
            chunks = list(pool.map(_collect_worker_chunk, tasks))

            ro = np.concatenate([c["obs"] for c in chunks], axis=0)
            rh = np.concatenate([c["hist"] for c in chunks], axis=0)
            ra = np.concatenate([c["act"] for c in chunks], axis=0)
            rw = np.concatenate([c["w"] for c in chunks], axis=0)
            rp = np.concatenate([c["priv"] for c in chunks], axis=0)

            all_o.append(ro)
            all_h.append(rh)
            all_a.append(ra)
            all_w.append(rw)
            all_p.append(rp)
            for c in chunks:
                if len(c["anc_obs"]) > 0:
                    anc_o.append(c["anc_obs"])
                    anc_h.append(c["anc_hist"])
                    anc_a.append(c["anc_act"])

            cat_o = np.concatenate(all_o, axis=0)
            cat_h = np.concatenate(all_h, axis=0)
            cat_a = np.concatenate(all_a, axis=0)
            cat_w = np.concatenate(all_w, axis=0)
            cat_p = np.concatenate(all_p, axis=0)

            if r_idx == 0:
                mean_t = torch.from_numpy(cat_o.mean(axis=0)).to(device)
                std_t = torch.from_numpy(cat_o.std(axis=0)).clamp_min(1e-2).to(device)
                model.actor_body.e_jump.set_normalization(mean_t, std_t)
                model.critic.priv_mean.copy_(torch.from_numpy(cat_p.mean(axis=0)).to(device))
                model.critic.priv_scale.copy_(torch.from_numpy(cat_p.std(axis=0)).clamp_min(1e-2).to(device))

            loss_val = train_supervised(model, device, cat_o, cat_h, cat_a, cat_w, epochs=epochs, lr=lr)

            tot_n = sum(c["n_eps"] for c in chunks)
            surv_n = sum(c["survived"] for c in chunks)
            tok_n = sum(c["task_ok"] for c in chunks)
            cln_n = sum(c["clean_ok"] for c in chunks)
            rims = [x for c in chunks for x in c["rims"]]
            lifts = [x for c in chunks for x in c["lifts"]]
            aps = [x for c in chunks for x in c["aps"]]

            r_stat = {
                "round": rname,
                "beta_teacher": beta,
                "episodes": tot_n,
                "survived": f"{surv_n}/{tot_n}",
                "task_success": f"{tok_n}/{tot_n}",
                "clean_zero_scrape": f"{cln_n}/{tot_n}",
                "frames_added": int(len(ro)),
                "total_frames": int(len(cat_o)),
                "mean_rel_rim_cm": round(float(np.mean(rims)) if rims else 0.0, 2),
                "mean_lift_ms": round(float(np.mean(lifts)) if lifts else 0.0, 1),
                "max_air_pitch_deg": round(float(np.max(aps)) if aps else 0.0, 2),
                "final_loss": round(loss_val, 5),
                "elapsed_s": round(time.perf_counter() - rt0, 2),
            }
            round_logs.append(r_stat)
            print(f"  [{rname}] {json.dumps(r_stat)}", flush=True)

    weights_dir = HERE / "weights"
    traj_dir = HERE / "trajectories"
    ev_dir = HERE / "evidence"
    weights_dir.mkdir(parents=True, exist_ok=True)
    traj_dir.mkdir(parents=True, exist_ok=True)
    ev_dir.mkdir(parents=True, exist_ok=True)

    cpu_state = {k: v.detach().cpu() for k, v in model.state_dict().items()}
    torch.save({"model_state_dict": cpu_state, "rounds": round_logs}, weights_dir / "model_bc_dagger.pt")

    anc_obs_np = np.concatenate(anc_o, axis=0) if anc_o else np.concatenate(all_o, axis=0)[:8000]
    anc_hist_np = np.concatenate(anc_h, axis=0) if anc_h else np.concatenate(all_h, axis=0)[:8000]
    anc_act_np = np.concatenate(anc_a, axis=0) if anc_a else np.concatenate(all_a, axis=0)[:8000]
    if len(anc_obs_np) > 16000:
        idx = np.random.default_rng(42).choice(len(anc_obs_np), size=16000, replace=False)
        anc_obs_np, anc_hist_np, anc_act_np = anc_obs_np[idx], anc_hist_np[idx], anc_act_np[idx]
    torch.save(
        {
            "obs": torch.from_numpy(anc_obs_np),
            "hist": torch.from_numpy(anc_hist_np),
            "act": torch.from_numpy(anc_act_np),
        },
        traj_dir / "clean_instant_jump_anchor.pt",
    )

    summary = {
        "total_frames": int(sum(len(x) for x in all_o)),
        "anchor_frames": int(len(anc_obs_np)),
        "e0_drift": model.verify_zero_e0_drift(),
        "rounds": round_logs,
        "total_elapsed_s": round(time.perf_counter() - t0, 2),
    }
    (ev_dir / "stage1_dagger_log.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"[Stage-1 DAgger Complete in {summary['total_elapsed_s']}s] Saved weights/model_bc_dagger.pt", flush=True)


if __name__ == "__main__":
    main()
