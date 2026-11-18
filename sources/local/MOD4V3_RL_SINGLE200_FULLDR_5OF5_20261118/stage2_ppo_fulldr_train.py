"""Stage 2: Single-Process Multi-Thread (`ThreadPoolExecutor`, 220 MB RAM) Closed-Loop Anti-Cheat
Progressive-DR (`0-DR -> 25% -> 50% -> 75% -> 100% Full-DR`) PPO for MOD4v3 Single-Step (200mm).

Uses 4 pre-allocated `SingleStepRLEnv` instances in one Python process (`mj.mj_step` releases the GIL in C),
eliminating Windows `multiprocessing.spawn` duplicate PyTorch DLL commit errors while running at ~2,000+ steps/sec.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import math
import os
from pathlib import Path
import queue
import shutil
import subprocess
import sys
import time

os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')

import numpy as np
import torch
from torch import nn

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SINGLE_EXP = REPO / 'sources/local/MOD4V3_MOE_ROUTE2_SINGLE200_STABLE_5OF5_20261118'
sys.path[:0] = [str(HERE), str(HERE / 'support')]

from mod4v3_ppo_v1.route2_common import HistoryQueue, LocalRoute2Actor
from rl_stair_env import SingleStepRLEnv

torch.set_num_threads(2)


class EnvPool:
    def __init__(self, n_envs: int = 4):
        self.q: queue.Queue[SingleStepRLEnv] = queue.Queue()
        for _ in range(n_envs):
            self.q.put(SingleStepRLEnv())
        self.exec = ThreadPoolExecutor(max_workers=n_envs)

    def run_tasks(self, actor: LocalRoute2Actor, std_vec: np.ndarray, tasks: list[dict]) -> list[dict]:
        actor.eval()

        def _work(task: dict) -> dict:
            env = self.q.get()
            try:
                rng = np.random.default_rng(task['seed'])
                deterministic = bool(task['deterministic'])
                obs, c_obs = env.reset(offset_mm=task['offset_mm'], dr_scale=task['dr_scale'], seed=task['seed'])
                qh = HistoryQueue()
                obs_buf, hist_buf, cobs_buf, act_buf, logp_buf, rew_buf, done_buf, active_buf = [], [], [], [], [], [], [], []
                with torch.inference_mode():
                    while True:
                        to = torch.from_numpy(obs).reshape(1, 35)
                        th = qh.reset(to) if env.k == 0 else qh.append(to)
                        mu = actor(to, th)[0].numpy()
                        g_p = float(actor.mlp.e1.gate_prob(th)[0, 0])
                        is_active = bool((obs[3] < 1.5) or (g_p > 0.04))

                        if deterministic:
                            a = np.clip(mu, -6.0, 6.0).astype(np.float32)
                            logp = 0.0
                        else:
                            eff_std = std_vec if is_active else (std_vec * 0.12)
                            eps = rng.normal(0.0, 1.0, size=6).astype(np.float32)
                            a = np.clip(mu + eff_std * eps, -6.0, 6.0).astype(np.float32)
                            logp = float(-0.5 * np.sum(((a - mu) / (std_vec + 1e-8)) ** 2 + 2.0 * np.log(std_vec + 1e-8) + math.log(2.0 * math.pi)))

                        next_obs, next_cobs, rew, done, info = env.step(a)
                        obs_buf.append(obs)
                        hist_buf.append(th[0].numpy().copy())
                        cobs_buf.append(c_obs)
                        act_buf.append(a)
                        logp_buf.append(logp)
                        rew_buf.append(rew)
                        done_buf.append(float(done))
                        active_buf.append(float(is_active))
                        obs, c_obs = next_obs, next_cobs
                        if done:
                            return {
                                'obs': np.asarray(obs_buf, dtype=np.float32),
                                'hist': np.asarray(hist_buf, dtype=np.float32),
                                'cobs': np.asarray(cobs_buf, dtype=np.float32),
                                'act': np.asarray(act_buf, dtype=np.float32),
                                'logp': np.asarray(logp_buf, dtype=np.float32),
                                'rew': np.asarray(rew_buf, dtype=np.float32),
                                'done': np.asarray(done_buf, dtype=np.float32),
                                'active': np.asarray(active_buf, dtype=np.float32),
                                'last_cobs': next_cobs.astype(np.float32),
                                'info': info,
                                'offset_mm': task['offset_mm'],
                                'dr_scale': task['dr_scale'],
                            }
            finally:
                self.q.put(env)

        return list(self.exec.map(_work, tasks))

    def close(self):
        self.exec.shutdown(wait=True)


class ValueNet(nn.Module):
    def __init__(self, in_dim: int = 78):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, 256),
            nn.LayerNorm(256),
            nn.ELU(),
            nn.Linear(256, 128),
            nn.LayerNorm(128),
            nn.ELU(),
            nn.Linear(128, 64),
            nn.ELU(),
            nn.Linear(64, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x).squeeze(-1)


def compute_gae(rew: np.ndarray, val: np.ndarray, last_v: float, gamma: float = 0.995, lam: float = 0.95) -> tuple[np.ndarray, np.ndarray]:
    T = len(rew)
    adv = np.zeros(T, dtype=np.float32)
    gae = 0.0
    for t in reversed(range(T)):
        nv = last_v if t == T - 1 else val[t + 1]
        nonterm = 0.0 if t == T - 1 else 1.0
        delta = rew[t] + gamma * nv * nonterm - val[t]
        gae = delta + gamma * lam * nonterm * gae
        adv[t] = gae
    return adv, adv + val


def evaluate_suite(pool: EnvPool, actor: LocalRoute2Actor, std_vec: np.ndarray) -> dict:
    tasks = []
    for off in [-60, -30, 0, 30, 60]:
        tasks.append({'offset_mm': float(off), 'dr_scale': 0.0, 'seed': 100 + off, 'deterministic': True})
    dense15 = [-70, -60, -50, -40, -30, -20, -10, 0, 10, 20, 30, 40, 50, 60, 70]
    for off in dense15:
        tasks.append({'offset_mm': float(off), 'dr_scale': 0.0, 'seed': 300 + off, 'deterministic': True})
    for off in [-60, -30, 0, 30, 60]:
        for s_i in range(5):
            tasks.append({'offset_mm': float(off), 'dr_scale': 1.0, 'seed': 8000 + s_i * 131 + (off + 100), 'deterministic': True})

    outs = pool.run_tasks(actor, std_vec, tasks)
    r_5 = outs[:5]
    r_15 = outs[5:20]
    r_dr = outs[20:]

    pass_5 = sum(int(x['info']['success']) for x in r_5)
    cross_5 = sum(int(x['info']['physical_crossed']) for x in r_5)
    slide_5 = sum(int(x['info']['slid_back']) for x in r_5)
    spd_5 = float(np.mean([x['info']['max_speed_m_s'] for x in r_5]))

    pass_15 = sum(int(x['info']['success']) for x in r_15)
    cross_15 = sum(int(x['info']['physical_crossed']) for x in r_15)

    pass_dr = sum(int(x['info']['success']) for x in r_dr)
    cross_dr = sum(int(x['info']['physical_crossed']) for x in r_dr)
    slide_dr = sum(int(x['info']['slid_back']) for x in r_dr)

    score = pass_5 * 1000.0 + cross_5 * 80.0 + pass_dr * 25.0 + cross_dr * 6.0 + pass_15 * 8.0 - spd_5 * 10.0 - slide_dr * 5.0
    return {
        'formal_0dr_passed': pass_5,
        'formal_0dr_crossed': cross_5,
        'formal_0dr_slid_back': slide_5,
        'formal_0dr_mean_max_speed': round(spd_5, 4),
        'formal_0dr_rows': [
            {
                'offset_mm': x['offset_mm'],
                'success': x['info']['success'],
                'crossed': x['info']['physical_crossed'],
                'max_speed_m_s': round(x['info']['max_speed_m_s'], 4),
                'final_vx': round(x['info']['final_vx'], 4),
                'reason': x['info']['reason'],
            }
            for x in r_5
        ],
        'dense15_0dr_passed': pass_15,
        'dense15_0dr_crossed': cross_15,
        'fulldr_25_passed': pass_dr,
        'fulldr_25_crossed': cross_dr,
        'fulldr_25_slid_back': slide_dr,
        'score': round(score, 3),
    }


def main():
    t_start = time.time()
    p25_pt = SINGLE_EXP / 'weights/model_025m.pt'
    base_pt = p25_pt if p25_pt.exists() else (HERE / 'weights/model_base_step000.pt')
    print(f'Initializing Stage-2 Progressive-DR PPO from {base_pt}', flush=True)

    ck = torch.load(base_pt, map_location='cpu', weights_only=False)
    actor = LocalRoute2Actor().load_checkpoint(ck)
    e1 = actor.mlp.e1

    actor.mlp.e0.requires_grad_(False)
    actor.distribution.e0_std.requires_grad_(False)
    e1.approach_base.requires_grad_(False)
    e1.gate.requires_grad_(False)

    with torch.no_grad():
        actor.distribution.e1_log_std.copy_(torch.tensor([0.012, 0.012, 0.012, 0.012, 0.020, 0.020]).log())
    actor.distribution.e1_log_std.requires_grad_(True)

    e0_ref = {k: v.clone() for k, v in actor.mlp.e0.state_dict().items()}

    critic = ValueNet(78)
    trainable_actor_params = (
        list(e1.encoder.parameters())
        + list(e1.head.parameters())
        + list(e1.top_head.parameters())
        + [actor.distribution.e1_log_std]
    )
    opt_actor = torch.optim.Adam(trainable_actor_params, lr=1.2e-5)
    opt_critic = torch.optim.Adam(critic.parameters(), lr=3e-4, weight_decay=1e-5)

    # Seed clean replay buffer with ALL 5 OFFSETS <=0.547m/s pure-student trajectories + model_025m/030m/010m successes!
    rep_obs, rep_hist, rep_act = [], [], []
    for ep_npz in sorted((HERE / 'bootstrap_replay/elegant_r2_clean').glob('*.npz')):
        z = np.load(ep_npz)
        fr = z['frames'].astype(np.float32)
        for i in range(len(fr)):
            o_i = fr[i, :35]
            h_i = fr[i, 35:455]
            a_i = fr[i, 455:461]
            with torch.no_grad():
                gp = float(e1.gate_prob(torch.from_numpy(h_i).unsqueeze(0))[0, 0])
            if o_i[3] < 1.5 or gp > 0.15:
                rep_obs.append(o_i); rep_hist.append(h_i); rep_act.append(a_i)

    for ck_n, offs in [('model_025m', [-60, 0, 30]), ('model_030m', [-30, 30]), ('model_010m', [-30])]:
        for off in offs:
            p_r = SINGLE_EXP / f'evidence/checkpoint_evals/{ck_n}/single_step/start_{off:+04d}mm/rollout.npz'
            if p_r.exists():
                zr = np.load(p_r)
                o_arr = zr['obs'].astype(np.float32)
                a_arr = zr['actions'].astype(np.float32)
                qh = HistoryQueue()
                for i in range(len(o_arr)):
                    th = qh.reset(torch.from_numpy(o_arr[i:i + 1])) if i == 0 else qh.append(torch.from_numpy(o_arr[i:i + 1]))
                    with torch.no_grad():
                        gp = float(e1.gate_prob(th)[0, 0])
                    if o_arr[i, 3] < 1.5 or gp > 0.15:
                        rep_obs.append(o_arr[i].copy())
                        rep_hist.append(th[0].numpy().copy())
                        rep_act.append(a_arr[i].copy())

    print(f'Loaded {len(rep_obs)} clean 5-offset active climb+park replay frames!', flush=True)
    max_replay = 20000

    dr_stages = [0.00, 0.25, 0.50, 0.75, 1.00]
    stage_idx = 0
    total_iters = 36
    warmup_iters = 6
    episodes_per_iter = 16

    train_log = []
    best_state = {k: v.detach().cpu().clone() for k, v in actor.state_dict().items()}

    pool = EnvPool(n_envs=4)
    try:
        init_std = actor.distribution.e1_log_std.detach().exp().cpu().numpy()
        ev0 = evaluate_suite(pool, actor, init_std)
        best_eval = ev0
        print(
            f"[Iter 00 PRE-PPO] 0-DR 5off={ev0['formal_0dr_passed']}/5 (cross={ev0['formal_0dr_crossed']}/5, spd={ev0['formal_0dr_mean_max_speed']}) | "
            f"dense15={ev0['dense15_0dr_passed']}/15 | Full-DR={ev0['fulldr_25_passed']}/25 (cross={ev0['fulldr_25_crossed']}/25) | score={ev0['score']}",
            flush=True,
        )

        for it in range(1, total_iters + 1):
            is_warmup = it <= warmup_iters
            cur_dr = dr_stages[stage_idx]
            std_np = actor.distribution.e1_log_std.detach().exp().cpu().numpy()

            rng = np.random.default_rng(20261118 + it * 997)
            # Focus extra sampling weight on -30 and +60 while covering all 5 official offsets + continuous jitter!
            base_offs = [-60, -30, -30, 0, 30, 60, 60, -60, -30, 0, 30, 60]
            rand_offs = rng.uniform(-68.0, 68.0, size=episodes_per_iter - len(base_offs)).tolist()
            all_offs = base_offs + rand_offs

            tasks = []
            for ei, off in enumerate(all_offs):
                ep_dr = 0.0 if (ei % 3 == 0) else cur_dr
                tasks.append({
                    'offset_mm': float(off),
                    'dr_scale': float(ep_dr),
                    'seed': int(50000 + it * 101 + ei),
                    'deterministic': False,
                })

            rollouts = pool.run_tasks(actor, std_np, tasks)

            batch_succ = 0
            batch_slide = 0
            online_added = 0
            all_obs, all_hist, all_cobs, all_act, all_logp, all_adv, all_ret, all_active = [], [], [], [], [], [], [], []

            critic.eval()
            for r in rollouts:
                if r['info']['success']:
                    batch_succ += 1
                    if r['info']['max_speed_m_s'] <= 0.58 and abs(r['info']['final_vx']) <= 0.035:
                        mask = r['active'] > 0.5
                        if np.any(mask):
                            rep_obs.extend(r['obs'][mask])
                            rep_hist.extend(r['hist'][mask])
                            rep_act.extend(r['act'][mask])
                            online_added += 1
                if r['info']['slid_back']:
                    batch_slide += 1

                with torch.no_grad():
                    vals = critic(torch.from_numpy(r['cobs'])).numpy()
                    last_v = 0.0 if (r['done'][-1] > 0.5 and r['info']['reason'] != 'timeout') else float(critic(torch.from_numpy(r['last_cobs']).unsqueeze(0))[0])
                adv, ret = compute_gae(r['rew'], vals, last_v)
                all_obs.append(r['obs'])
                all_hist.append(r['hist'])
                all_cobs.append(r['cobs'])
                all_act.append(r['act'])
                all_logp.append(r['logp'])
                all_adv.append(adv)
                all_ret.append(ret)
                all_active.append(r['active'])

            if len(rep_obs) > max_replay:
                rep_obs = rep_obs[-max_replay:]
                rep_hist = rep_hist[-max_replay:]
                rep_act = rep_act[-max_replay:]

            B_obs = torch.from_numpy(np.concatenate(all_obs, axis=0))
            B_hist = torch.from_numpy(np.concatenate(all_hist, axis=0))
            B_cobs = torch.from_numpy(np.concatenate(all_cobs, axis=0))
            B_act = torch.from_numpy(np.concatenate(all_act, axis=0))
            B_logp = torch.from_numpy(np.concatenate(all_logp, axis=0))
            B_adv = torch.from_numpy(np.concatenate(all_adv, axis=0))
            B_ret = torch.from_numpy(np.concatenate(all_ret, axis=0))
            B_actv = torch.from_numpy(np.concatenate(all_active, axis=0))

            critic.train()
            vf_losses = []
            for _ in range(6 if is_warmup else 4):
                perm = torch.randperm(len(B_cobs))
                for i in range(0, len(B_cobs), 256):
                    idx = perm[i:i + 256]
                    v_pred = critic(B_cobs[idx])
                    loss_v = nn.functional.smooth_l1_loss(v_pred, B_ret[idx])
                    opt_critic.zero_grad()
                    loss_v.backward()
                    nn.utils.clip_grad_norm_(critic.parameters(), 1.0)
                    opt_critic.step()
                    vf_losses.append(float(loss_v.item()))

            pi_loss_val = 0.0
            kl_val = 0.0
            rep_loss_val = 0.0
            if not is_warmup:
                actor.train()
                act_idx = torch.nonzero(B_actv > 0.5, as_tuple=False).squeeze(-1)
                if len(act_idx) >= 64:
                    A_obs = B_obs[act_idx]
                    A_hist = B_hist[act_idx]
                    A_act = B_act[act_idx]
                    A_logp = B_logp[act_idx]
                    A_adv = B_adv[act_idx]
                    A_adv = (A_adv - A_adv.mean()) / (A_adv.std() + 1e-6)

                    R_obs = torch.tensor(np.asarray(rep_obs), dtype=torch.float32)
                    R_hist = torch.tensor(np.asarray(rep_hist), dtype=torch.float32)
                    R_act = torch.tensor(np.asarray(rep_act), dtype=torch.float32)

                    early_stop_kl = False
                    for _ in range(5):
                        if early_stop_kl:
                            break
                        perm = torch.randperm(len(A_obs))
                        for i in range(0, len(A_obs), 192):
                            b = perm[i:i + 192]
                            if len(b) < 32:
                                continue
                            mu = actor(A_obs[b], A_hist[b])
                            std = actor.distribution.e1_log_std.exp().clamp(0.005, 0.045)
                            logp_new = -0.5 * (((A_act[b] - mu) / std).square() + 2.0 * std.log() + math.log(2.0 * math.pi)).sum(dim=-1)
                            ratio = (logp_new - A_logp[b]).clamp(-10.0, 10.0).exp()
                            approx_kl = float((A_logp[b] - logp_new).mean().item())
                            kl_val = approx_kl
                            if approx_kl > 0.020:
                                early_stop_kl = True
                                break

                            surr1 = ratio * A_adv[b]
                            surr2 = ratio.clamp(1.0 - 0.16, 1.0 + 0.16) * A_adv[b]
                            loss_pi = -torch.min(surr1, surr2).mean()
                            loss_sym = (mu[:, :2] - mu[:, 2:4]).square().mean() + 0.35 * (mu[:, 4] - mu[:, 5]).square().mean()

                            rb = torch.randint(0, len(R_obs), (min(160, len(R_obs)),))
                            mu_rep = actor(R_obs[rb], R_hist[rb])
                            loss_rep = ((mu_rep - R_act[rb]) / torch.tensor([0.20, 0.20, 0.20, 0.20, 0.22, 0.22])).square().mean()

                            loss_tot = loss_pi + 0.20 * loss_sym + 0.38 * loss_rep
                            opt_actor.zero_grad()
                            loss_tot.backward()
                            nn.utils.clip_grad_norm_(trainable_actor_params, 0.5)
                            opt_actor.step()
                            with torch.no_grad():
                                actor.distribution.e1_log_std.clamp_(math.log(0.006), math.log(0.035))

                            pi_loss_val = float(loss_pi.item())
                            rep_loss_val = float(loss_rep.item())

                if (batch_succ / episodes_per_iter >= 0.625 or it >= warmup_iters + (stage_idx + 1) * 6) and stage_idx < len(dr_stages) - 1:
                    stage_idx += 1
                    print(f'   >>> PROMOTED Progressive-DR Curriculum to Stage {stage_idx} (dr_scale={dr_stages[stage_idx]:.2f})! <<<', flush=True)

            mean_ep_rew = float(np.mean([np.sum(r['rew']) for r in rollouts]))
            row = {
                'iter': it,
                'warmup': is_warmup,
                'dr_scale': cur_dr,
                'batch_succ': f'{batch_succ}/{episodes_per_iter}',
                'batch_slide': batch_slide,
                'online_replay_added': online_added,
                'replay_size': len(rep_obs),
                'mean_ep_reward': round(mean_ep_rew, 2),
                'vf_loss': round(float(np.mean(vf_losses)), 4),
                'pi_loss': round(pi_loss_val, 5),
                'approx_kl': round(kl_val, 5),
                'rep_loss': round(rep_loss_val, 5),
            }

            if it % 4 == 0 or it == total_iters:
                ev = evaluate_suite(pool, actor, actor.distribution.e1_log_std.detach().exp().cpu().numpy())
                row['eval'] = ev
                print(
                    f"[Iter {it:02d} | dr={cur_dr:.2f} | warm={is_warmup}] rew={mean_ep_rew:6.1f} kl={kl_val:.4f} | "
                    f"0-DR 5off={ev['formal_0dr_passed']}/5 (cross={ev['formal_0dr_crossed']}/5, spd={ev0['formal_0dr_mean_max_speed'] if False else ev['formal_0dr_mean_max_speed']}) | "
                    f"dense15={ev['dense15_0dr_passed']}/15 | Full-DR={ev['fulldr_25_passed']}/25 (cross={ev['fulldr_25_crossed']}/25) | score={ev['score']}",
                    flush=True,
                )
                if ev['score'] >= best_eval['score']:
                    best_eval = ev
                    best_state = {k: v.detach().cpu().clone() for k, v in actor.state_dict().items()}
            else:
                print(
                    f"[Iter {it:02d} | dr={cur_dr:.2f} | warm={is_warmup}] batch_succ={batch_succ}/{episodes_per_iter} "
                    f"rew={mean_ep_rew:6.1f} vf={row['vf_loss']:.3f} kl={kl_val:.4f} rep={rep_loss_val:.4f}",
                    flush=True,
                )
            train_log.append(row)
    finally:
        pool.close()

    e0_max_diff = max(float((actor.mlp.e0.state_dict()[k] - e0_ref[k]).abs().max()) for k in e0_ref)
    assert e0_max_diff == 0.0, f'E0 drifted: {e0_max_diff}'

    final_ck = dict(ck)
    final_ck['iter'] = int(ck.get('iter', 0)) + total_iters
    final_ck['actor_state_dict'] = {k: v.detach().cpu().clone() for k, v in actor.state_dict().items()}
    final_pt = HERE / 'weights/model_rl_stair_final.pt'
    torch.save(final_ck, final_pt)

    best_ck = dict(ck)
    best_ck['iter'] = int(ck.get('iter', 0)) + total_iters
    best_ck['actor_state_dict'] = best_state
    best_pt = HERE / 'weights/model_rl_stair_best.pt'
    torch.save(best_ck, best_pt)

    best_sha = hashlib.sha256(best_pt.read_bytes()).hexdigest()
    final_sha = hashlib.sha256(final_pt.read_bytes()).hexdigest()
    print(f'Saved BEST RL Stair Checkpoint: {best_pt} (SHA256={best_sha})', flush=True)
    print(f'Best dual-domain eval: {json.dumps(best_eval, indent=2)}', flush=True)

    off_dir = HERE / 'evidence/best_official_eval200'
    if off_dir.exists():
        shutil.rmtree(off_dir)
    subprocess.run(
        [sys.executable, str(HERE / 'evaluate_student200.py'), '--model', str(best_pt), '--out', str(off_dir), '--video'],
        cwd=REPO,
        check=True,
    )
    official_res = json.loads((off_dir / 'RESULT.json').read_text(encoding='utf8'))
    print(f"UNMODIFIED evaluate_student200.py on model_rl_stair_best.pt: passed={official_res['passed']}/5 crossed={official_res['physical_crossed']}/5", flush=True)

    (HERE / 'evidence/ppo_fulldr_training_log.json').write_text(
        json.dumps(
            {
                'wall_seconds': round(time.time() - t_start, 2),
                'best_sha256': best_sha,
                'final_sha256': final_sha,
                'e0_max_abs_drift': e0_max_diff,
                'official_0dr_passed': official_res['passed'],
                'official_0dr_crossed': official_res['physical_crossed'],
                'best_dual_domain_eval': best_eval,
                'iterations': train_log,
            },
            indent=2,
        ) + '\n',
        encoding='utf8',
    )


if __name__ == '__main__':
    main()
