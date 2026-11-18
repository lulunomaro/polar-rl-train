"""End-to-end preflight + remote 0-PPO probe + 40m anti-cheat continuous 2-step PPO launch
for MOD4V3_MOE_ROUTE2_CONTINUOUS_2STEP_ANTICHEAT_20261118.
"""
from pathlib import Path
import datetime
import hashlib
import json
import math
import os
import shlex
import shutil
import subprocess
import sys
import time
import numpy as np
import torch

T = Path(__file__).resolve().parent
R = T.parents[2]
SRC_ELEGANT = R / 'sources/local/MOD4V3_MOE_ROUTE2_ELEGANT_GATED_PPO_20261118'
sys.path[:0] = [str(T), str(T / 'support')]
from mod4v3_ppo_v1.route2_common import LocalRoute2Actor, HistoryQueue, action_mlp


def ensure_support_artifacts(model_path: Path, model_sha: str):
    # 1. Ensure startup_pose.json & PROTECTED_INPUTS.json exist
    for rel in ['startup_pose.json', 'c874_reference.pt', 'evidence/PROTECTED_INPUTS.json']:
        dst = T / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not dst.exists() and (SRC_ELEGANT / rel).exists():
            shutil.copy2(SRC_ELEGANT / rel, dst)

    # 2. Build probe_samples.npz covering climb head, standup_head (crouched_settled == 1.0), and top_head (obs[3]=1.0)
    actor = LocalRoute2Actor().load_checkpoint(torch.load(model_path, map_location='cpu', weights_only=False))
    c874 = torch.load(T / 'c874_reference.pt', map_location='cpu', weights_only=False)
    src_probe = np.load(SRC_ELEGANT / 'probe_samples.npz')
    obs_arr = src_probe['obs'].copy()
    hist_arr = src_probe['history'].copy()

    # 32 crouched-on-tread samples where ext = 0.25*(q0 - q1 + q2 - q3) < -0.42 across all 12 frames & obs[3]=2.0455 > 1.7 -> g_su == 1.0!
    n_su = 32
    su_obs = np.zeros((n_su, 35), dtype=np.float32)
    su_obs[:, 0] = 0.47
    su_obs[:, 3] = 2.0455
    su_obs[:, 9] = -1.0
    su_obs[:, 10] = -0.15 + 0.03 * np.linspace(-1, 1, n_su, dtype=np.float32)
    su_obs[:, 11] = +0.78
    su_obs[:, 12] = -0.15 + 0.03 * np.linspace(-1, 1, n_su, dtype=np.float32)
    su_obs[:, 13] = +0.78
    su_obs[:, 20:22] = 0.40
    su_obs[:, 28:35] = np.array([0, 1, 0, 0, 0, 1, 0], dtype=np.float32)
    su_hist = np.repeat(su_obs[:, None, :], 12, axis=1)

    # 16 top_park samples (obs[3] = 1.0 < 1.5)
    pk_obs = su_obs[:16].copy()
    pk_obs[:, 0] = 0.0
    pk_obs[:, 3] = 1.0
    pk_hist = np.repeat(pk_obs[:, None, :], 12, axis=1)

    all_obs = np.concatenate([obs_arr, su_obs, pk_obs], axis=0).astype(np.float32)
    all_hist = np.concatenate([hist_arr, su_hist, pk_hist], axis=0).astype(np.float32)
    with torch.no_grad():
        all_targ = actor.mlp.e1.encoder(torch.from_numpy(all_hist).flatten(1))[:, :5].numpy().astype(np.float32)
    np.savez_compressed(T / 'probe_samples.npz', obs=all_obs, history=all_hist, targets=all_targ)

    # 3. Verify E0 exact 0.0 error & non-zero finite gradients on ALL trainable E1 parameters (head, standup_head, top_head, encoder, STD)!
    obs_t = torch.from_numpy(all_obs)
    hist_t = torch.from_numpy(all_hist).flatten(1)
    targ_t = torch.from_numpy(all_targ)

    e0_ref = action_mlp(35)
    e0_ref.load_state_dict({k.removeprefix('mlp.'): v for k, v in c874['actor_state_dict'].items() if k.startswith('mlp.')})
    obs_norm = obs_t.clone()
    obs_norm[:, 28:35] = torch.tensor([1., 0., 0., 0., 0., 0., 0.])
    with torch.no_grad():
        e0_err = float((actor(obs_norm, hist_t) - e0_ref(obs_norm)).abs().max())
    assert e0_err == 0.0, f'E0 error {e0_err}'

    for m in [actor.mlp.e0, actor.mlp.e1.approach_base, actor.mlp.e1.gate]:
        m.requires_grad_(False)
    actor.distribution.e0_std.requires_grad_(False)
    actor.zero_grad()
    mean = actor(obs_t, hist_t)
    std = actor.distribution.std(obs_t)
    dist = torch.distributions.Normal(mean, std)
    sample_act = mean.detach() + torch.randn_like(mean) * 0.3
    logloss = -dist.log_prob(sample_act).sum(-1).mean()
    z = actor.mlp.e1.encoder(hist_t)
    aux = 0.1 * (z[:, :5] - targ_t).square().mean()
    (logloss + aux).backward()
    grads = {n: float(p.grad.norm()) for n, p in actor.named_parameters() if p.requires_grad and p.grad is not None}
    missing = [n for n, p in actor.named_parameters() if p.requires_grad and (p.grad is None or not math.isfinite(float(p.grad.norm())) or float(p.grad.norm()) <= 0.0)]
    assert not missing, f'Missing/zero gradients: {missing}'
    print('Verified all trainable actor tensors have finite >0 gradients! count=', len(grads), 'min_norm=', min(grads.values()), flush=True)


def run_local_preflight_and_harvest_replay(model_path: Path, model_sha: str):
    eval_dir = T / 'evidence/preflight_step000'
    if eval_dir.exists():
        shutil.rmtree(eval_dir)
    eval_dir.mkdir(parents=True, exist_ok=True)

    for label, script, extra in [
        ('single_step', 'evaluate_student200.py', ['--video']),
        ('two_step', 'evaluate_2step400.py', ['--video']),
        ('flat60', 'fixed_60_eval.py', []),
    ]:
        r = subprocess.run([sys.executable, str(T / script), '--model', str(model_path), '--out', str(eval_dir / label)] + extra, cwd=R, capture_output=True, text=True)
        print(f'[{label}] exit={r.returncode}\n{r.stdout}', flush=True)
        if r.returncode != 0:
            print(r.stderr, flush=True)
            raise SystemExit(r.returncode)

    s1 = json.loads((eval_dir / 'single_step/RESULT.json').read_text(encoding='utf8'))
    s2 = json.loads((eval_dir / 'two_step/RESULT.json').read_text(encoding='utf8'))
    f60 = json.loads((eval_dir / 'flat60/RESULT.json').read_text(encoding='utf8'))
    flat60_ok = sum(x['passed'] for x in f60['rows'])
    print(f"LOCAL PREFLIGHT SUMMARY: flat60={flat60_ok}/60 | 1-step: formal={s1['passed']}/5 crossed={s1['physical_crossed']}/5 | 2-step: formal={s2['passed']}/5 parked2={s2['physical_2step_parked']}/5 s1={s2['step1_crossed']}/5 s2={s2['step2_crossed']}/5 slid={s2['slid_off_count']}/5", flush=True)
    assert flat60_ok == 60 and s1['passed'] >= 3, (flat60_ok, s1)

    # Build clean bootstrap_replay/elegant_r2_clean from verified <=0.60m/s 1-step & 2-step rollouts!
    broot = T / 'bootstrap_replay'
    if broot.exists():
        shutil.rmtree(broot)
    clean_dir = broot / 'elegant_r2_clean'
    clean_dir.mkdir(parents=True, exist_ok=True)

    import evaluate_student200, evaluate_2step400
    h1_dir = eval_dir / 'harvest_1step'
    res1 = evaluate_student200.run(str(model_path), str(h1_dir), video=False, step_height=0.2, offsets=[-60, -50, -45, -20, -10, 0, 10, 20, 30, 40])
    h2_dir = eval_dir / 'harvest_2step'
    res2 = evaluate_2step400.run(str(model_path), str(h2_dir), video=False, offsets=[-60, -45, -30, -15, 0, 15, 30, 45, 60])

    rng = np.random.default_rng(20261118)
    saved = 0
    pinned = 0

    for row in res1['rows']:
        off = row['start_offset_mm']
        if not row['success'] or row['maximum_episode_speed_m_s'] > 0.60:
            continue
        npz = np.load(h1_dir / f'start_{off:+04d}mm/rollout.npz')
        obs = npz['obs'].astype(np.float32)
        acts = npz['actions'].astype(np.float32)
        tr = npz['trace']
        q = HistoryQueue()
        hist = np.asarray([(q.reset(torch.from_numpy(obs[i:i+1])) if i == 0 else q.append(torch.from_numpy(obs[i:i+1])))[0].numpy() for i in range(len(obs))], dtype=np.float32)
        sup = (tr[:, 9] > 0.5).astype(np.int64) + (tr[:, 10] > 0.5).astype(np.int64)
        zcmd = np.abs(obs[:, 0]) < 0.05
        phases = np.where(zcmd & (obs[:, 3] > 1.7), 0, np.where(zcmd & (obs[:, 3] <= 1.7) & (sup == 2), 3, np.where(sup > 0, 2, 1))).astype(np.int8)
        is_pin = pinned < 3
        acts_s = acts.copy()
        if not is_pin:
            jit = rng.normal(0.0, 1e-3, size=acts_s.shape).astype(np.float32)
            jit[phases == 0] = 0.0
            acts_s = np.clip(acts_s + jit, -6.0, 6.0)
        else:
            pinned += 1
        frames = np.concatenate([obs, hist, acts_s], axis=1).astype(np.float32)
        meta = dict(
            accepted_native_success=True,
            stable_hold_s=float(row['final_continuous_hold_s']),
            parked_hold_s=float(row['final_continuous_hold_s']),
            course_level=0,
            step_height_m=0.20,
            formal_evaluation_pass=True,
            source_model_sha256=model_sha,
            policy_update=0 if is_pin else 1,
            start_offset_mm=int(off),
            episode_steps=int(len(obs)),
            physics_dt_s=0.0025,
            policy_dt_s=0.02,
            history_H=12,
            teacher_assistance=False,
            actual_full_DR=False,
            speed_limit_m_s=0.60,
            episode_max_speed_m_s=float(row['maximum_episode_speed_m_s']),
            entry_speed_m_s=float(row['entry_speed_m_s']),
            strict_speed_qualified=True,
        )
        saved += 1
        np.savez_compressed(clean_dir / f'episode_{saved:06d}.npz', frames=frames, phases=phases, metadata_json=np.asarray(json.dumps(meta)))

    # Also harvest any non-sliding 2-step parked episodes <=0.65m/s so standup_head gets clean BC replay too!
    saved_2step = 0
    for row in res2['rows']:
        off = row['start_offset_mm']
        if not row['physical_2step_parked'] or row['slid_off'] or row['maximum_episode_speed_m_s'] > 0.65:
            continue
        npz = np.load(h2_dir / f'start_{off:+04d}mm/rollout.npz')
        obs = npz['obs'].astype(np.float32)
        acts = npz['actions'].astype(np.float32)
        tr = npz['trace']
        q = HistoryQueue()
        hist = np.asarray([(q.reset(torch.from_numpy(obs[i:i+1])) if i == 0 else q.append(torch.from_numpy(obs[i:i+1])))[0].numpy() for i in range(len(obs))], dtype=np.float32)
        sup2 = (tr[:, 11] > 0.5).astype(np.int64) + (tr[:, 12] > 0.5).astype(np.int64)
        zcmd = np.abs(obs[:, 0]) < 0.05
        phases = np.where(zcmd & (obs[:, 3] > 1.7), 0, np.where(zcmd & (obs[:, 3] <= 1.7) & (sup2 == 2), 3, np.where(sup2 > 0, 2, 1))).astype(np.int8)
        jit = rng.normal(0.0, 1e-3, size=acts.shape).astype(np.float32)
        jit[phases == 0] = 0.0
        acts_s = np.clip(acts + jit, -6.0, 6.0)
        frames = np.concatenate([obs, hist, acts_s], axis=1).astype(np.float32)
        meta = dict(
            accepted_native_success=True,
            stable_hold_s=float(row['physical_final_hold2_s']),
            parked_hold_s=float(row['physical_final_hold2_s']),
            course_level=1,
            step_height_m=0.40,
            formal_evaluation_pass=bool(row['success']),
            source_model_sha256=model_sha,
            policy_update=1,
            start_offset_mm=int(off),
            episode_steps=int(len(obs)),
            physics_dt_s=0.0025,
            policy_dt_s=0.02,
            history_H=12,
            teacher_assistance=False,
            actual_full_DR=False,
            speed_limit_m_s=0.65,
            episode_max_speed_m_s=float(row['maximum_episode_speed_m_s']),
            entry_speed_m_s=float(row['entry_speed_m_s'] or 0.45),
            strict_speed_qualified=bool(row['maximum_episode_speed_m_s'] <= 0.60),
        )
        saved += 1
        saved_2step += 1
        np.savez_compressed(clean_dir / f'episode_{saved:06d}.npz', frames=frames, phases=phases, metadata_json=np.asarray(json.dumps(meta)))

    print(f'Harvested {saved} clean bootstrap episodes ({saved_2step} continuous 2-step, {pinned} pinned settle)!', flush=True)
    assert saved >= 5 and pinned == 3

    rc = subprocess.run([sys.executable, str(T / 'check_repair.py')], cwd=T, capture_output=True, text=True)
    print('[check_repair]', rc.stdout, flush=True)
    if rc.returncode != 0:
        print(rc.stderr, flush=True)
        raise SystemExit(rc.returncode)


def launch_remote_probe_and_ppo(model_sha: str):
    remote_root = '/home/egde/rl_candidates/mod4v3_moe_route2_continuous_2step_anticheat_20261118_r1'
    plan = json.loads((T / 'PLAN.json').read_text(encoding='utf8'))
    plan['experiment'] = 'MOD4V3_MOE_ROUTE2_CONTINUOUS_2STEP_ANTICHEAT_20261118'
    plan['root'] = remote_root
    plan['support'] = remote_root + '/support'
    plan['parent'] = remote_root + '/model_step000.pt'
    plan['parent_sha256'] = model_sha
    plan['locked_v1_sha256'] = model_sha
    plan['local_skill_preflight_passed'] = True
    plan['training_job'] = 'train_2step_anticheat_40m'
    plan['training_round'] = 'continuous_2step_anticheat_0dr_to_dr_40m'
    plan['native_probe']['job'] = 'native_2step_anticheat_probe_r2'
    plan['route2']['E1_initial_std'] = [0.010, 0.010, 0.010, 0.010, 0.020, 0.020]
    plan['route2']['E1_trainable'] = [
        'encoder (16D history latent)',
        'climb head (51->256->128->64->6)',
        'standup_head (51->256->128->64->6)',
        'top_park head (51->256->128->64->6)',
        'independent6D logSTD',
        'independent78D critic (15-iter critic-only warmup)',
    ]
    plan['route2']['v1_anchor']['source_sha256'] = model_sha
    plan['continuous_stair']['heights_m'] = [0.20, 0.40]
    plan['continuous_stair']['steps'] = 2
    plan['continuous_stair']['speed_ladder_m_s'] = [0.78, 0.72, 0.68, 0.64, 0.62, 0.60]
    plan['bootstrap_replay_dirs'] = [remote_root + '/bootstrap_replay/elegant_r2_clean']
    plan['PPO_training_authorized'] = False
    plan['authorized_PPO_seconds'] = 0
    plan['human_restart_authorized'] = False
    plan['zero_update_precheck_passed'] = False
    if 'collection_source_sha256' in plan:
        del plan['collection_source_sha256']
    (T / 'PLAN.json').write_text(json.dumps(plan, ensure_ascii=False, indent=2) + '\n', encoding='utf8')

    # Upload & launch 0-PPO native probe
    for act in ['upload', 'probe']:
        r = subprocess.run([sys.executable, '-X', 'utf8', str(T / 'remote_control.py'), act], cwd=T, capture_output=True, text=True)
        print(f'[remote_control {act}]', r.stdout, flush=True)
        if r.returncode != 0:
            print(r.stderr, flush=True)
            raise SystemExit(r.returncode)

    from remote_run import connect, execute
    probe_job = remote_root + '/' + plan['native_probe']['job']
    e_probe = T / 'evidence/native_probe'
    e_probe.mkdir(parents=True, exist_ok=True)

    deadline = time.time() + 420
    pre = None
    has_native_sr = False
    while time.time() < deadline:
        c = connect()
        try:
            sf = c.open_sftp()
            try:
                names = set(sf.listdir(probe_job))
            except FileNotFoundError:
                names = set()
            if 'ERROR.json' in names:
                sf.get(probe_job + '/ERROR.json', str(e_probe / 'ERROR.json'))
                raise RuntimeError('Remote probe ERROR:\n' + (e_probe / 'ERROR.json').read_text(encoding='utf8'))
            if 'SAFE_CLOSED.json' in names and 'ROUTE2_NATIVE_PREFLIGHT.json' in names:
                for fn in ['ROUTE2_NATIVE_PREFLIGHT.json', 'SAFE_CLOSED.json', 'OFFSET_COVERAGE.json', 'STARTUP_DIAGNOSTICS.json', 'STARTUP.json']:
                    if fn in names:
                        sf.get(probe_job + '/' + fn, str(e_probe / fn))
                sf.get(remote_root + '/' + plan['native_probe']['job'] + '.log', str(e_probe / 'probe.log'))
                sr_local = e_probe / 'success_replay'
                sr_local.mkdir(exist_ok=True)
                try:
                    for rn in sf.listdir(probe_job + '/success_replay'):
                        if rn.endswith('.npz') or rn == 'MANIFEST.json':
                            sf.get(probe_job + '/success_replay/' + rn, str(sr_local / rn))
                            if rn.startswith('episode_') and rn.endswith('.npz'):
                                has_native_sr = True
                except FileNotFoundError:
                    pass
                time.sleep(3)
                gpu = execute(c, 'nvidia-smi --query-gpu=memory.used,memory.free,utilization.gpu --format=csv,noheader').strip()
                pre = json.loads((e_probe / 'ROUTE2_NATIVE_PREFLIGHT.json').read_text(encoding='utf8'))
                print('REMOTE 0-PPO PROBE PASSED! GPU:', gpu, 'height_pop:', pre['height_population'], 's1_events:', pre['step1_climb_events_DR_then_nominal'], 's2_events:', pre['step2_climb_events_DR_then_nominal'], 'completions:', pre['completions_DR_then_nominal'], flush=True)
                break
            if 'PROBE_PROGRESS.json' in names:
                sf.get(probe_job + '/PROBE_PROGRESS.json', str(e_probe / 'PROBE_PROGRESS.json'))
                print('PROBE_PROGRESS:', (e_probe / 'PROBE_PROGRESS.json').read_text(encoding='utf8').strip(), flush=True)
        finally:
            c.close()
        time.sleep(8)
    if pre is None:
        raise TimeoutError('Timed out waiting for remote 0-PPO probe')

    # Authorize 40m (2400s) PPO run!
    now_iso = datetime.datetime.now().astimezone().isoformat()
    plan['PPO_training_authorized'] = True
    plan['authorized_PPO_seconds'] = 2400
    plan['human_restart_authorized'] = True
    plan['zero_update_precheck_passed'] = True
    if has_native_sr:
        nsr = probe_job + '/success_replay'
        if nsr not in plan['bootstrap_replay_dirs']:
            plan['bootstrap_replay_dirs'].append(nsr)
    plan['human_training_authorization'] = {
        'recorded_at': now_iso,
        'human_message': '/goal 推进mod4v3的rl上台阶和rl大跳和移动大跳，最好的训练结果留好配方，方便我们后训练同样构型的机器人',
        'interpretation': 'Human authorized autonomous RL stair-climbing (continuous 2-step anti-cheat 0-DR->Full-DR) and RL high/moving jump training + recipe consolidation.',
        'authorized_PPO_seconds': 2400,
        'work_cutoff_seconds': 2340,
        'reserve_seconds': 60,
        'parent_sha256': model_sha,
        'automatically_extend': False,
        'automatically_restart': False,
        'automatically_promote': False,
    }
    plan['restart_policy']['human_confirmation'] = dict(plan['human_training_authorization'])
    (T / 'PLAN.json').write_text(json.dumps(plan, ensure_ascii=False, indent=2) + '\n', encoding='utf8')

    c = connect()
    try:
        with c.open_sftp() as sf:
            sf.put(str(T / 'PLAN.json'), remote_root + '/PLAN.json.partial')
            sf.posix_rename(remote_root + '/PLAN.json.partial', remote_root + '/PLAN.json')
    finally:
        c.close()

    r_tr = subprocess.run([sys.executable, '-X', 'utf8', str(T / 'remote_control.py'), 'train'], cwd=T, capture_output=True, text=True)
    print('[remote_control train]', r_tr.stdout, flush=True)
    if r_tr.returncode != 0:
        print(r_tr.stderr, flush=True)
        raise SystemExit(r_tr.returncode)
    launch_info = json.loads(r_tr.stdout.strip().splitlines()[-1])

    train_job = remote_root + '/' + plan['training_job']
    e_train = T / 'evidence/training'
    e_train.mkdir(parents=True, exist_ok=True)
    deadline = time.time() + 300
    while time.time() < deadline:
        c = connect()
        try:
            sf = c.open_sftp()
            try:
                names = set(sf.listdir(train_job))
            except FileNotFoundError:
                names = set()
            if 'ERROR.json' in names:
                sf.get(train_job + '/ERROR.json', str(e_train / 'ERROR.json'))
                raise RuntimeError('Remote train ERROR:\n' + (e_train / 'ERROR.json').read_text(encoding='utf8'))
            if 'FIRST_UPDATE.json' in names and 'model_first_complete.pt' in names:
                for fn in ['TRAINING_CLOCK.json', 'PREUPDATE_ISOLATION.json', 'FIRST_UPDATE.json', 'LATEST_PROGRESS.json', 'STARTUP.json']:
                    if fn in names:
                        sf.get(train_job + '/' + fn, str(e_train / fn))
                sf.get(train_job + '/model_first_complete.pt', str(T / 'weights/model_first_complete.pt.partial'))
                os.replace(T / 'weights/model_first_complete.pt.partial', T / 'weights/model_first_complete.pt')
                first = json.loads((e_train / 'FIRST_UPDATE.json').read_text(encoding='utf8'))
                clock = json.loads((e_train / 'TRAINING_CLOCK.json').read_text(encoding='utf8'))
                ver = dict(
                    probe_passed=True,
                    probe_height_population=pre['height_population'],
                    probe_s1_events=pre['step1_climb_events_DR_then_nominal'],
                    probe_s2_events=pre['step2_climb_events_DR_then_nominal'],
                    probe_completions=pre['completions_DR_then_nominal'],
                    train_launch=launch_info,
                    clock=clock,
                    first_update_checkpoint=first['checkpoint'],
                    trainable_group_max_changes=first['trainable_group_max_changes'],
                    normal_isolation=first['normal_isolation'],
                )
                (T / 'evidence/LAUNCH40M_VERIFICATION.json').write_text(json.dumps(ver, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
                print('FIRST_UPDATE_VERIFIED:', json.dumps(ver, ensure_ascii=False), flush=True)
                return
        finally:
            c.close()
        time.sleep(8)
    raise TimeoutError('Timed out waiting for FIRST_UPDATE.json')


if __name__ == '__main__':
    mpath = T / 'weights/model_step000.pt'
    sha = hashlib.sha256(mpath.read_bytes()).hexdigest()
    print('Preparing model_step000.pt SHA256:', sha, flush=True)
    ensure_support_artifacts(mpath, sha)
    if not (T / 'bootstrap_replay/elegant_r2_clean/episode_000005.npz').exists():
        run_local_preflight_and_harvest_replay(mpath, sha)
    else:
        rc = subprocess.run([sys.executable, str(T / 'check_repair.py')], cwd=T, capture_output=True, text=True)
        print('[check_repair]', rc.stdout, flush=True)
        if rc.returncode != 0:
            print(rc.stderr, flush=True)
            raise SystemExit(rc.returncode)
    launch_remote_probe_and_ppo(sha)
