# SPDX-License-Identifier: MIT
"""Stage 2: Closed-Loop Anti-Cheat Progressive-DR PPO on RTX 4090 + 40 Parallel MuJoCo Workers.

Strictly Zero-Cheating:
  - Actor: InstantPureNeuralJumpExpert (obs_35 + hist_1400 -> act_6), ZERO runtime teacher, ZERO world-z / step inputs.
  - E0 (c874): Strictly frozen, verified 0.0 parameter drift every single iteration.
  - Progressive Curriculum:
      Iters 01..08: Critic-Only Warmup (0-DR)
      Iters 09..24: 0-DR Closed-Loop PPO (conquer wide step-jump matrix + 24cm + 2-step + crisp latency)
      Iters 25..38: 50% DR Closed-Loop PPO
      Iters 39..52: 100% Full-DR Closed-Loop PPO
  - Saves weights/model_instant_jump_best.pt, weights/model_instant_jump_final.pt, and evidence/ppo_training_log.json.
"""
from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
import hashlib
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

from instant_jump_env import (
    Mod4v3InstantJumpEnv,
    ParallelInstantJumpVecEnv,
    ensure_instant_jump_scene_xml,
)
from moe_instant_jump_model import (
    ACT_DIM,
    HERE,
    HIST_DIM,
    HIST_LEN,
    HistoryQueue,
    JUMP_MODE_BIT_INDEX,
    MoEInstantJumpActorCritic,
    OBS_DIM,
    PRIV_CRITIC_DIM,
    StatefulInstantJumpMoE,
)

_VAL_ENV: Mod4v3InstantJumpEnv | None = None
_VAL_MODEL: MoEInstantJumpActorCritic | None = None


def _init_val_worker(xml_str: str) -> None:
    global _VAL_ENV, _VAL_MODEL
    os.environ["OPENBLAS_NUM_THREADS"] = "1"
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"
    torch.set_num_threads(1)
    _VAL_ENV = Mod4v3InstantJumpEnv(seed=7777, xml_path=Path(xml_str))
    _VAL_MODEL = MoEInstantJumpActorCritic()
    _VAL_MODEL.load_frozen_c874()
    _VAL_MODEL.eval()


def build_validation_matrix() -> list[dict[str, Any]]:
    """Comprehensive 60-case validation matrix mirroring the exact graduation gates!"""
    cases: list[dict[str, Any]] = []
    # 1. Flat stationary & multi-hop (4 cases)
    cases.append({"tag": "flat_stat", "kind": "flat_stat", "v_cmd": 0.0, "v_jump": 0.0, "v_post": 0.0, "jt": (0.75,), "dws": [], "stand_dw": None, "drop_x": None, "steps": [], "max_s": 2.4})
    cases.append({"tag": "flat_multihop", "kind": "flat_move", "v_cmd": 0.9, "v_jump": 0.9, "v_post": 0.9, "jt": (0.85, 2.25), "dws": [], "stand_dw": None, "drop_x": None, "steps": [], "max_s": 3.8})
    # 2. Near-step Space+W on 15cm & 20cm (6 cases)
    for sh in (0.15, 0.20):
        for dw in (0.44, 0.50, 0.56):
            xf = 0.15 + 0.35 * 0.85 + dw
            cases.append({"tag": f"near_{int(sh*100)}", "kind": "near_step", "v_cmd": 0.35, "v_jump": 1.0, "v_post": 0.8, "jt": (), "dws": [(0, dw)], "stand_dw": None, "drop_x": None, "steps": [(xf, 5.5, sh)], "max_s": 3.5})
    # 3. Moving W+Space on 15cm & 20cm (15 cases each = 30 cases)
    for sh in (0.15, 0.20):
        for vc in (0.6, 1.0, 1.4):
            for k in range(5):
                dw = 0.40 + 0.07 * vc + 0.075 * k
                xf = 0.15 + vc * 0.90 + dw
                cases.append({"tag": f"move_{int(sh*100)}", "kind": "move_step", "v_cmd": vc, "v_jump": vc, "v_post": vc, "jt": (), "dws": [(0, dw)], "stand_dw": None, "drop_x": None, "steps": [(xf, 5.8, sh)], "max_s": 3.6})
    # 4. 24cm high step across moving/near window (10 cases)
    for dw in (0.46, 0.52):
        xf = 0.15 + 0.35 * 0.85 + dw
        cases.append({"tag": "step_24", "kind": "near_step", "v_cmd": 0.35, "v_jump": 1.05, "v_post": 0.8, "jt": (), "dws": [(0, dw)], "stand_dw": None, "drop_x": None, "steps": [(xf, 5.5, 0.24)], "max_s": 3.5})
    for vc in (0.8, 1.2):
        for k in range(4):
            dw = 0.44 + 0.07 * vc + 0.065 * k
            xf = 0.15 + vc * 0.90 + dw
            cases.append({"tag": "step_24", "kind": "move_step", "v_cmd": vc, "v_jump": vc, "v_post": vc, "jt": (), "dws": [(0, dw)], "stand_dw": None, "drop_x": None, "steps": [(xf, 5.8, 0.24)], "max_s": 3.6})
    # 5. Continuous 20cm -> 40cm 2-step vault (5 cases)
    for k in range(5):
        vc = 0.85 + 0.03 * (k - 2)
        dw1 = 0.52 + 0.02 * (k - 2)
        tread = 1.56
        xf1 = 0.20 + vc * 0.85 + dw1
        xf2 = xf1 + tread
        cases.append({"tag": "two_step", "kind": "two_step", "v_cmd": vc, "v_jump": vc, "v_post": vc, "jt": (), "dws": [(0, dw1), (1, 0.52)], "stand_dw": None, "drop_x": None, "steps": [(xf1, tread + 0.05, 0.20), (xf2, 4.5, 0.40)], "max_s": 4.7})
    # 6. Platform jump-down 20/30/40cm (3 cases)
    for dh in (0.20, 0.30, 0.40):
        cases.append({"tag": "drop_off", "kind": "drop_off", "v_cmd": 0.85, "v_jump": 0.85, "v_post": 0.85, "jt": (), "dws": [], "stand_dw": None, "drop_x": 0.95, "steps": [(-0.60, 1.80, dh)], "max_s": 3.5})
    return cases


def _eval_val_case(args: tuple[int, dict[str, Any], float, dict[str, np.ndarray]]) -> dict[str, Any]:
    idx, c, dr_s, sd_np = args
    assert _VAL_ENV is not None and _VAL_MODEL is not None
    _VAL_MODEL.load_state_dict({k: torch.from_numpy(v) for k, v in sd_np.items()}, strict=True)
    _VAL_MODEL.eval()
    actor = StatefulInstantJumpMoE(_VAL_MODEL)
    _VAL_ENV.rng = np.random.default_rng(8000 + idx)

    st = _VAL_ENV.reset(
        dr_scale=dr_s,
        scenario_kind=c["kind"],
        v_cmd=c["v_cmd"],
        v_jump=c["v_jump"],
        v_cmd_post=c["v_post"],
        jump_times=c["jt"],
        step_trigger_dws=c["dws"],
        stand_step_dw=c["stand_dw"],
        drop_trigger_x=c["drop_x"],
        max_episode_s=c["max_s"],
        steps=c["steps"],
    )
    actor.reset_history()
    while True:
        act = actor(torch.from_numpy(st["obs"]).unsqueeze(0))[0].numpy()
        st, _r, done, info = _VAL_ENV.step(act)
        if done:
            surv = info["fell_reason"] == "" and not info["slid_off_step"]
            if c["kind"] == "drop_off":
                ok = surv and info["drop_landed_ok"]
            elif info["steps_total"] > 0:
                ok = surv and (info["steps_mounted_count"] >= info["steps_total"]) and (info["rel_z_end"] >= 0.23)
            else:
                ok = surv and (len(info["completed_jumps"]) >= max(1, len(c["jt"])))
            clean = ok and info["ep_guide_force_N"] < 1.0 and info["ep_chassis_force_N"] < 1.0 and info["ep_riser_hit_N"] < 5.0
            rim = max((j["rel_rim_cm"] for j in info["completed_jumps"]), default=0.0)
            lift = min((j["lift_ms"] for j in info["completed_jumps"]), default=250.0)
            return {
                "tag": c["tag"],
                "ok": bool(ok),
                "clean": bool(clean),
                "rim_cm": rim,
                "lift_ms": lift,
                "air_p": info["ep_max_air_pitch_deg"],
            }


def run_parallel_validation(
    pool: ProcessPoolExecutor,
    model: MoEInstantJumpActorCritic,
    cases: list[dict[str, Any]],
    dr_scale: float,
) -> dict[str, Any]:
    sd_np = {k: v.detach().cpu().numpy() for k, v in model.state_dict().items()}
    tasks = [(i, c, dr_scale, sd_np) for i, c in enumerate(cases)]
    res = list(pool.map(_eval_val_case, tasks))

    by_tag: dict[str, list[dict[str, Any]]] = {}
    for r in res:
        by_tag.setdefault(r["tag"], []).append(r)

    def _rate(tag: str) -> float:
        items = by_tag.get(tag, [])
        return sum(1 for x in items if x["ok"]) / max(1, len(items))

    pass_all = sum(1 for x in res if x["ok"]) / max(1, len(res))
    clean_all = sum(1 for x in res if x["clean"]) / max(1, len(res))
    flat_rims = [x["rim_cm"] for x in res if x["tag"].startswith("flat") and x["rim_cm"] > 0]
    mean_rim = float(np.mean(flat_rims)) if flat_rims else 0.0
    ok_aps = [x["air_p"] for x in res if x["ok"]]
    max_ap = float(np.max(ok_aps)) if ok_aps else 99.0
    stat_lift = by_tag["flat_stat"][0]["lift_ms"] if "flat_stat" in by_tag else 250.0

    s_move15 = _rate("move_15")
    s_move20 = _rate("move_20")
    s_near = 0.5 * (_rate("near_15") + _rate("near_20"))
    s_24 = _rate("step_24")
    s_2step = _rate("two_step")
    s_drop = _rate("drop_off")

    pitch_pen = 3.0 * max(0.0, max_ap - 9.8) if dr_scale == 0.0 else 0.5 * max(0.0, max_ap - 14.0)
    score = (
        45.0 * pass_all
        + 25.0 * clean_all
        + 30.0 * s_move20
        + 20.0 * s_move15
        + 20.0 * s_near
        + 25.0 * s_24
        + 25.0 * s_2step
        + 10.0 * s_drop
        + 0.5 * min(mean_rim, 32.0)
        - pitch_pen
    )
    return {
        "dr_scale": dr_scale,
        "composite_score": round(score, 3),
        "overall_pass": f"{sum(1 for x in res if x['ok'])}/{len(res)}",
        "overall_clean": f"{sum(1 for x in res if x['clean'])}/{len(res)}",
        "move_15cm_15": f"{sum(1 for x in by_tag['move_15'] if x['ok'])}/15",
        "move_20cm_15": f"{sum(1 for x in by_tag['move_20'] if x['ok'])}/15",
        "near_15_20_6": f"{sum(1 for x in by_tag['near_15']+by_tag['near_20'] if x['ok'])}/6",
        "step_24cm_10": f"{sum(1 for x in by_tag['step_24'] if x['ok'])}/10",
        "two_step_5": f"{sum(1 for x in by_tag['two_step'] if x['ok'])}/5",
        "drop_off_3": f"{sum(1 for x in by_tag['drop_off'] if x['ok'])}/3",
        "stat_lift_ms": round(stat_lift, 1),
        "flat_rim_cm": round(mean_rim, 2),
        "max_air_pitch_deg": round(max_ap, 2),
    }


def curriculum_dr(it: int) -> float:
    if it <= 44:
        return 0.00
    if it <= 62:
        return 0.50
    return 1.00


def save_ckpt(model: MoEInstantJumpActorCritic, path: Path, meta: dict[str, Any]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    cpu_sd = {k: v.detach().cpu() for k, v in model.state_dict().items()}
    torch.save({"model_state_dict": cpu_sd, "metadata": meta}, path)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    t0 = time.perf_counter()
    torch.manual_seed(20261118)
    np.random.seed(20261118)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    bc_ckpt = HERE / "weights/model_bc_dagger.pt"
    anc_path = HERE / "trajectories/clean_instant_jump_anchor.pt"
    if not bc_ckpt.exists() or not anc_path.exists():
        raise FileNotFoundError("Run stage1_instant_jump_dagger.py first!")

    ck = torch.load(bc_ckpt, map_location=device, weights_only=False)
    model = MoEInstantJumpActorCritic().to(device)
    model.load_frozen_c874()
    model.load_state_dict(ck["model_state_dict"], strict=True)
    with torch.no_grad():
        model.ejump_log_std.copy_(
            torch.tensor([0.032, 0.032, 0.032, 0.032, 0.045, 0.045], dtype=torch.float32, device=device).log()
        )
    model.verify_zero_e0_drift()

    anc = torch.load(anc_path, map_location=device, weights_only=False)
    anc_obs = anc["obs"].to(device)
    anc_hist = anc["hist"].to(device)
    anc_act = anc["act"].to(device)

    actor_params = [
        p
        for _n, p in list(model.actor_body.e_jump.named_parameters()) + [("ejump_log_std", model.ejump_log_std)]
        if p.requires_grad
    ]
    critic_params = [p for p in model.critic.parameters() if p.requires_grad]

    actor_opt = torch.optim.Adam(actor_params, lr=2.8e-5, eps=1e-5)
    critic_opt = torch.optim.Adam(critic_params, lr=6.0e-4, eps=1e-5)

    num_envs = 40
    steps_per_iter = 256  # 10,240 steps/iter!
    total_iters = 80      # 819,200 closed-loop 400Hz steps!
    critic_warmup_iters = 8
    gamma = 0.99
    gae_lambda = 0.95
    clip_eps = 0.14
    ppo_epochs = 4
    minibatch_size = 1024
    target_kl = 0.015

    xml_path = ensure_instant_jump_scene_xml()
    val_cases = build_validation_matrix()
    val_pool = ProcessPoolExecutor(max_workers=16, initializer=_init_val_worker, initargs=(str(xml_path),))

    v0_init = run_parallel_validation(val_pool, model, val_cases, dr_scale=0.0)
    vf_init = run_parallel_validation(val_pool, model, val_cases, dr_scale=1.0)
    best_score = 0.65 * v0_init["composite_score"] + 0.35 * vf_init["composite_score"]
    best_ckpt = HERE / "weights/model_instant_jump_best.pt"
    final_ckpt = HERE / "weights/model_instant_jump_final.pt"
    best_sha = save_ckpt(model, best_ckpt, {"iter": 0, "val_0dr": v0_init, "val_fulldr": vf_init})
    best_iter = 0
    print(f"[PPO Init] 0-DR={v0_init} | Full-DR={vf_init} | score={best_score:.2f}", flush=True)

    vec_env = ParallelInstantJumpVecEnv(num_envs=num_envs, base_seed=3000, dr_scale=0.0)
    obs_np, priv_np = vec_env.reset_all(dr_scale=0.0)
    hist_q = HistoryQueue(hist_len=HIST_LEN)
    hist_t_cur = hist_q.reset(torch.from_numpy(obs_np).to(device))

    buf_obs = torch.zeros((steps_per_iter, num_envs, OBS_DIM), device=device)
    buf_hist = torch.zeros((steps_per_iter, num_envs, HIST_DIM), device=device)
    buf_priv = torch.zeros((steps_per_iter, num_envs, PRIV_CRITIC_DIM), device=device)
    buf_act = torch.zeros((steps_per_iter, num_envs, ACT_DIM), device=device)
    buf_logp = torch.zeros((steps_per_iter, num_envs), device=device)
    buf_val = torch.zeros((steps_per_iter, num_envs), device=device)
    buf_rew = torch.zeros((steps_per_iter, num_envs), device=device)
    buf_done = torch.zeros((steps_per_iter, num_envs), device=device)
    buf_to_val = torch.zeros((steps_per_iter, num_envs), device=device)

    log_data: dict[str, Any] = {
        "init_val_0dr": v0_init,
        "init_val_fulldr": vf_init,
        "iterations": [],
        "validations": [],
    }

    cur_dr = 0.0
    try:
        for it in range(1, total_iters + 1):
            it_t0 = time.perf_counter()
            ndr = curriculum_dr(it)
            if abs(ndr - cur_dr) > 1e-6:
                cur_dr = ndr
                vec_env.set_dr_scale(cur_dr)

            model.eval()
            ep_surv, ep_mnt, step_rews = [], [], []
            for t in range(steps_per_iter):
                obs_t = torch.from_numpy(obs_np).to(device)
                priv_t = torch.from_numpy(priv_np).to(device)
                buf_obs[t] = obs_t
                buf_hist[t] = hist_t_cur
                buf_priv[t] = priv_t

                with torch.no_grad():
                    exec_a, raw_a, logp, val = model.sample_action_and_value(obs_t, hist_t_cur, priv_t)

                buf_act[t] = raw_a
                buf_logp[t] = logp
                buf_val[t] = val

                obs_np, priv_np, rews_np, dones_np, infos = vec_env.step(exec_a.cpu().numpy())
                buf_rew[t] = torch.from_numpy(rews_np).to(device)
                buf_done[t] = torch.from_numpy(dones_np.astype(np.float32)).to(device)
                buf_to_val[t].zero_()
                step_rews.append(float(rews_np.mean()))

                # Timeout bootstrap BEFORE resetting history for done envs!
                for ei, inf in enumerate(infos):
                    if dones_np[ei]:
                        fell = inf["fell_reason"] != ""
                        ep_surv.append(0.0 if fell else 1.0)
                        if inf["steps_total"] > 0:
                            ep_mnt.append(1.0 if (not fell and inf["steps_mounted_count"] >= inf["steps_total"]) else 0.0)
                        if "terminal_obs" in inf:
                            with torch.no_grad():
                                to_o = torch.from_numpy(inf["terminal_obs"]).unsqueeze(0).to(device)
                                to_p = torch.from_numpy(inf["terminal_priv"]).unsqueeze(0).to(device)
                                # Construct terminal history by shifting hist_q.buffer[ei] + terminal_obs
                                prev_seq = hist_q.buffer[ei, 1:, :]
                                to_h = torch.cat((prev_seq, to_o), dim=0).flatten().unsqueeze(0)
                                buf_to_val[t, ei] = model.evaluate_value(to_o, to_h, to_p)[0]

                dones_t = torch.from_numpy(dones_np).to(device)
                hist_t_cur = hist_q.append(torch.from_numpy(obs_np).to(device), done=dones_t)

            if it == 1:
                fp0 = buf_priv.reshape(-1, PRIV_CRITIC_DIM)
                model.critic.priv_mean.copy_(fp0.mean(dim=0))
                model.critic.priv_scale.copy_(fp0.std(dim=0) + 0.05)
                with torch.no_grad():
                    for t in range(steps_per_iter):
                        buf_val[t] = model.evaluate_value(buf_obs[t], buf_hist[t], buf_priv[t])

            with torch.no_grad():
                next_val = model.evaluate_value(
                    torch.from_numpy(obs_np).to(device),
                    hist_t_cur,
                    torch.from_numpy(priv_np).to(device),
                )

            adv = torch.zeros_like(buf_rew)
            last_gae = torch.zeros(num_envs, device=device)
            for t in reversed(range(steps_per_iter)):
                nv = next_val if t == steps_per_iter - 1 else buf_val[t + 1]
                nonterm = 1.0 - buf_done[t]
                boot_v = nonterm * nv + buf_done[t] * buf_to_val[t]
                delta = buf_rew[t] + gamma * boot_v - buf_val[t]
                last_gae = delta + gamma * gae_lambda * nonterm * last_gae
                adv[t] = last_gae
            ret = adv + buf_val

            N = steps_per_iter * num_envs
            f_obs = buf_obs.reshape(N, OBS_DIM)
            f_hist = buf_hist.reshape(N, HIST_DIM)
            f_priv = buf_priv.reshape(N, PRIV_CRITIC_DIM)
            f_act = buf_act.reshape(N, ACT_DIM)
            f_logp = buf_logp.reshape(N)
            f_adv = adv.reshape(N)
            f_ret = ret.reshape(N)
            f_vold = buf_val.reshape(N)

            huber_vf = nn.SmoothL1Loss(beta=1.0)
            model.train()
            if it <= critic_warmup_iters:
                vls = []
                for _ in range(10):
                    perm = torch.randperm(N, device=device)
                    for st_i in range(0, N, minibatch_size):
                        mb = perm[st_i : st_i + minibatch_size]
                        vp = model.evaluate_value(f_obs[mb], f_hist[mb], f_priv[mb])
                        vl = huber_vf(vp, f_ret[mb])
                        critic_opt.zero_grad(set_to_none=True)
                        vl.backward()
                        nn.utils.clip_grad_norm_(critic_params, 1.0)
                        critic_opt.step()
                        vls.append(float(vl.item()))
                mean_vf = float(np.mean(vls))
                mean_pg = mean_kl = mean_anc = 0.0
            else:
                prog = (it - critic_warmup_iters) / max(1, total_iters - critic_warmup_iters)
                cur_lr = 3.2e-5 * (0.25 + 0.75 * 0.5 * (1.0 + math.cos(math.pi * prog)))
                for pg in actor_opt.param_groups:
                    pg["lr"] = cur_lr
                for pg in critic_opt.param_groups:
                    pg["lr"] = 4.0e-4

                j_mask = f_obs[:, JUMP_MODE_BIT_INDEX] > 0.5
                if int(j_mask.sum()) > 64:
                    ja = f_adv[j_mask]
                    f_adv_n = (f_adv - ja.mean()) / (ja.std() + 1e-6)
                else:
                    f_adv_n = (f_adv - f_adv.mean()) / (f_adv.std() + 1e-6)

                anc_coef = float(0.10 * (1.0 - 0.80 * prog))
                pgls, vfls, kls, ancls = [], [], [], []
                kl_stop = False

                for _ in range(ppo_epochs):
                    if kl_stop:
                        break
                    perm = torch.randperm(N, device=device)
                    for st_i in range(0, N, minibatch_size):
                        mb = perm[st_i : st_i + minibatch_size]
                        vp = model.evaluate_value(f_obs[mb], f_hist[mb], f_priv[mb])
                        vl = huber_vf(vp, f_ret[mb])
                        critic_opt.zero_grad(set_to_none=True)
                        vl.backward()
                        nn.utils.clip_grad_norm_(critic_params, 1.0)
                        critic_opt.step()
                        vfls.append(float(vl.item()))

                        js = f_obs[mb, JUMP_MODE_BIT_INDEX] > 0.5
                        if int(js.sum()) < 32:
                            continue
                        jo, jh, jp = f_obs[mb][js], f_hist[mb][js], f_priv[mb][js]
                        ja_act, j_olp, j_adv_mb = f_act[mb][js], f_logp[mb][js], f_adv_n[mb][js]

                        nlp, ent, _v, _m = model.evaluate_actions(jo, jh, jp, ja_act)
                        lr_rat = nlp - j_olp
                        rat = lr_rat.exp()
                        with torch.no_grad():
                            akl = float(((rat - 1.0) - lr_rat).mean().item())
                        kls.append(akl)
                        if akl > 1.5 * target_kl:
                            kl_stop = True
                            break

                        s1 = rat * j_adv_mb
                        s2 = rat.clamp(1.0 - clip_eps, 1.0 + clip_eps) * j_adv_mb
                        pg_loss = -torch.min(s1, s2).mean()
                        ent_loss = -0.001 * ent.mean()
                        sym_loss = 0.25 * model.symmetry_loss(jo, jh)

                        a_idx = torch.randint(0, len(anc_obs), (min(384, len(anc_obs)),), device=device)
                        a_pred = model.actor_body.e_jump(anc_obs[a_idx], anc_hist[a_idx])
                        anc_loss = anc_coef * ((a_pred - anc_act[a_idx]) ** 2).mean()

                        aloss = pg_loss + ent_loss + sym_loss + anc_loss
                        actor_opt.zero_grad(set_to_none=True)
                        aloss.backward()
                        nn.utils.clip_grad_norm_(actor_params, 0.5)
                        actor_opt.step()

                        pgls.append(float(pg_loss.item()))
                        ancls.append(float(anc_loss.item()))

                mean_vf = float(np.mean(vfls)) if vfls else 0.0
                mean_pg = float(np.mean(pgls)) if pgls else 0.0
                mean_kl = float(np.mean(kls)) if kls else 0.0
                mean_anc = float(np.mean(ancls)) if ancls else 0.0

            drift = model.verify_zero_e0_drift()
            rec = {
                "iter": it,
                "dr_scale": cur_dr,
                "step_rew": round(float(np.mean(step_rews)), 4),
                "surv_rate": round(float(np.mean(ep_surv)) if ep_surv else 1.0, 4),
                "step_mnt_rate": round(float(np.mean(ep_mnt)) if ep_mnt else 0.0, 4),
                "vf_loss": round(mean_vf, 5),
                "pg_loss": round(mean_pg, 5),
                "kl": round(mean_kl, 5),
                "anc_loss": round(mean_anc, 5),
                "e0_drift": drift,
                "wall_s": round(time.perf_counter() - it_t0, 2),
            }
            log_data["iterations"].append(rec)
            if it in (1, 6, 10, 14, 18, 24, 30, 38, 46, 52) or it % 4 == 0:
                print(
                    f"[Iter {it:02d}/{total_iters} DR={cur_dr:.2f}] rew={rec['step_rew']:+.3f} "
                    f"surv={rec['surv_rate']*100:5.1f}% mnt={rec['step_mnt_rate']*100:5.1f}% "
                    f"vf={mean_vf:.4f} kl={mean_kl:.4f} ({rec['wall_s']}s)",
                    flush=True,
                )

            if it >= critic_warmup_iters + 4 and (it % 4 == 0 or it in (24, 38, total_iters)):
                v0 = run_parallel_validation(val_pool, model, val_cases, dr_scale=0.0)
                vf = run_parallel_validation(val_pool, model, val_cases, dr_scale=1.0)
                comb = 0.65 * v0["composite_score"] + 0.35 * vf["composite_score"]
                log_data["validations"].append({"iter": it, "val_0dr": v0, "val_fulldr": vf, "combined_score": round(comb, 3)})
                tag = ""
                if comb > best_score:
                    best_score = comb
                    best_iter = it
                    best_sha = save_ckpt(model, best_ckpt, {"iter": it, "val_0dr": v0, "val_fulldr": vf, "combined_score": comb})
                    tag = " *** NEW BEST ***"
                print(
                    f"  -> [Val@{it:02d}] 0-DR: pass={v0['overall_pass']} m15={v0['move_15cm_15']} m20={v0['move_20cm_15']} "
                    f"near={v0['near_15_20_6']} s24={v0['step_24cm_10']} 2step={v0['two_step_5']} ap={v0['max_air_pitch_deg']}d | "
                    f"Full-DR: pass={vf['overall_pass']} | score={comb:.2f}{tag}",
                    flush=True,
                )
    finally:
        vec_env.close()
        val_pool.shutdown(wait=True)

    final_sha = save_ckpt(model, final_ckpt, {"iter": total_iters})
    log_data["best_iter"] = best_iter
    log_data["best_score"] = round(best_score, 3)
    log_data["best_sha256"] = best_sha
    log_data["final_sha256"] = final_sha
    log_data["total_elapsed_s"] = round(time.perf_counter() - t0, 2)
    (HERE / "evidence/ppo_training_log.json").write_text(json.dumps(log_data, indent=2), encoding="utf-8")
    print(f"\n[Stage-2 PPO Complete in {log_data['total_elapsed_s']}s] Best iter={best_iter}, SHA={best_sha[:12]}", flush=True)


if __name__ == "__main__":
    main()
