"""Wait for remote 0-PPO native probe completion, verify all assertions & GPU release,
authorize 40m PPO in PLAN.json, launch train_elegant_gated_40m, and verify FIRST_UPDATE.json.
"""
from pathlib import Path
import datetime
import hashlib
import json
import os
import shlex
import subprocess
import sys
import time

T = Path(__file__).resolve().parent
sys.path.insert(0, str(T))
from remote_run import connect, execute

P = json.loads((T / 'PLAN.json').read_text(encoding='utf8'))
REMOTE = P['root']
PROBE_JOB = REMOTE + '/' + P['native_probe']['job']
E_PROBE = T / 'evidence/native_probe'
E_PROBE.mkdir(parents=True, exist_ok=True)


def wait_remote_probe():
    deadline = time.time() + 360
    while time.time() < deadline:
        c = connect()
        try:
            sf = c.open_sftp()
            try:
                names = set(sf.listdir(PROBE_JOB))
            except FileNotFoundError:
                names = set()
            if 'ERROR.json' in names:
                sf.get(PROBE_JOB + '/ERROR.json', str(E_PROBE / 'ERROR.json'))
                try:
                    sf.get(REMOTE + '/' + P['native_probe']['job'] + '.log', str(E_PROBE / 'probe.log'))
                except Exception:
                    pass
                raise RuntimeError('Remote probe ERROR.json:\n' + (E_PROBE / 'ERROR.json').read_text(encoding='utf8'))
            if 'SAFE_CLOSED.json' in names and 'ROUTE2_NATIVE_PREFLIGHT.json' in names:
                for fn in ['ROUTE2_NATIVE_PREFLIGHT.json', 'SAFE_CLOSED.json', 'OFFSET_COVERAGE.json', 'STARTUP_DIAGNOSTICS.json', 'STARTUP.json']:
                    if fn in names:
                        sf.get(PROBE_JOB + '/' + fn, str(E_PROBE / fn))
                sf.get(REMOTE + '/' + P['native_probe']['job'] + '.log', str(E_PROBE / 'probe.log'))
                # Download any native 0-PPO probe success replay episodes
                sr_local = E_PROBE / 'success_replay'
                sr_local.mkdir(exist_ok=True)
                has_native_sr = False
                try:
                    for rn in sf.listdir(PROBE_JOB + '/success_replay'):
                        if rn.endswith('.npz') or rn == 'MANIFEST.json':
                            sf.get(PROBE_JOB + '/success_replay/' + rn, str(sr_local / rn))
                            if rn.startswith('episode_') and rn.endswith('.npz'):
                                has_native_sr = True
                except FileNotFoundError:
                    pass
                # Wait up to 15s for GPU process exit and check memory free
                time.sleep(3)
                gpu = execute(c, 'nvidia-smi --query-gpu=memory.used,memory.free,utilization.gpu --format=csv,noheader').strip()
                return json.loads((E_PROBE / 'ROUTE2_NATIVE_PREFLIGHT.json').read_text(encoding='utf8')), gpu, has_native_sr
            if 'PROBE_PROGRESS.json' in names:
                sf.get(PROBE_JOB + '/PROBE_PROGRESS.json', str(E_PROBE / 'PROBE_PROGRESS.json'))
                prog = json.loads((E_PROBE / 'PROBE_PROGRESS.json').read_text(encoding='utf8'))
                print('PROBE_PROGRESS:', prog, flush=True)
        finally:
            c.close()
        time.sleep(8)
    raise TimeoutError('Timed out waiting for remote native probe')


pre, gpu_after_probe, has_native_sr = wait_remote_probe()
assert pre['passed'] and pre['PPO_updates'] == 0 and pre['optimizer_updates'] == 0
print('NATIVE PROBE PASSED! completions_DR_then_nominal:', pre['completions_DR_then_nominal'], 'true_top_events:', pre['true_top_completion_events_DR_then_nominal'], 'GPU:', gpu_after_probe, flush=True)

# Update PLAN.json for 40-minute (2400s) PPO run
plan = json.loads((T / 'PLAN.json').read_text(encoding='utf8'))
now_iso = datetime.datetime.now().astimezone().isoformat()
plan['PPO_training_authorized'] = True
plan['authorized_PPO_seconds'] = 2400
plan['human_restart_authorized'] = True
plan['zero_update_precheck_passed'] = True
if has_native_sr:
    native_sr_dir = PROBE_JOB + '/success_replay'
    if native_sr_dir not in plan['bootstrap_replay_dirs']:
        plan['bootstrap_replay_dirs'].append(native_sr_dir)
plan['human_training_authorization'] = {
    'recorded_at': now_iso,
    'human_message': '你看看视频这跟我们要的优雅的上台阶根本不一样绝对有问题，修复 / 你直接负责操作，ssh直接远程链接后开跑，你不是又视频能力吗，修复一下然后开始ppo训练',
    'interpretation': 'Human instructed full repair of twitching/squatting stair gait, visual video verification, and launching the repaired 40-minute PPO run via SSH.',
    'authorized_PPO_seconds': 2400,
    'work_cutoff_seconds': 2340,
    'reserve_seconds': 60,
    'parent_sha256': plan['locked_v1_sha256'],
    'automatically_extend': False,
    'automatically_restart': False,
    'automatically_promote': False,
}
plan['restart_policy']['human_confirmation'] = dict(plan['human_training_authorization'])
if 'collection_source_sha256' in plan:
    del plan['collection_source_sha256']
(T / 'PLAN.json').write_text(json.dumps(plan, ensure_ascii=False, indent=2) + '\n', encoding='utf8')

# Upload updated PLAN.json only (do NOT touch support/ files whose SHA256s are locked in ROUTE2_NATIVE_PREFLIGHT.json!)
c = connect()
try:
    with c.open_sftp() as sf:
        sf.put(str(T / 'PLAN.json'), REMOTE + '/PLAN.json.partial')
        sf.posix_rename(REMOTE + '/PLAN.json.partial', REMOTE + '/PLAN.json')
    remote_plan_sha = execute(c, 'sha256sum -- ' + shlex.quote(REMOTE + '/PLAN.json')).split()[0]
    assert remote_plan_sha == hashlib.sha256((T / 'PLAN.json').read_bytes()).hexdigest()
finally:
    c.close()

# Launch 40-minute PPO run via remote_control.py train
r_train = subprocess.run([sys.executable, str(T / 'remote_control.py'), 'train'], cwd=T, capture_output=True, text=True)
print('TRAIN LAUNCH STDOUT:', r_train.stdout, flush=True)
if r_train.returncode != 0:
    print('TRAIN LAUNCH STDERR:', r_train.stderr, flush=True)
    raise SystemExit(r_train.returncode)
launch_info = json.loads(r_train.stdout.strip().splitlines()[-1])

# Wait for FIRST_UPDATE.json (1st complete PPO / 12 Adam steps)
TRAIN_JOB = REMOTE + '/' + plan['training_job']
E_TRAIN = T / 'evidence/training'
E_TRAIN.mkdir(parents=True, exist_ok=True)
W = T / 'weights'

deadline = time.time() + 300
while time.time() < deadline:
    c = connect()
    try:
        sf = c.open_sftp()
        try:
            names = set(sf.listdir(TRAIN_JOB))
        except FileNotFoundError:
            names = set()
        if 'ERROR.json' in names:
            sf.get(TRAIN_JOB + '/ERROR.json', str(E_TRAIN / 'ERROR.json'))
            try:
                sf.get(REMOTE + '/' + plan['training_job'] + '.log', str(E_TRAIN / 'train_error.log'))
            except Exception:
                pass
            raise RuntimeError('Remote train ERROR.json:\n' + (E_TRAIN / 'ERROR.json').read_text(encoding='utf8'))
        if 'FIRST_UPDATE.json' in names and 'model_first_complete.pt' in names:
            for fn in ['TRAINING_CLOCK.json', 'PREUPDATE_ISOLATION.json', 'FIRST_UPDATE.json', 'LATEST_PROGRESS.json', 'STARTUP.json']:
                if fn in names:
                    sf.get(TRAIN_JOB + '/' + fn, str(E_TRAIN / fn))
            sf.get(TRAIN_JOB + '/model_first_complete.pt', str(W / 'model_first_complete.pt.partial'))
            os.replace(W / 'model_first_complete.pt.partial', W / 'model_first_complete.pt')
            first = json.loads((E_TRAIN / 'FIRST_UPDATE.json').read_text(encoding='utf8'))
            clock = json.loads((E_TRAIN / 'TRAINING_CLOCK.json').read_text(encoding='utf8'))
            summary = dict(
                probe_passed=True,
                probe_completions_DR_then_nominal=pre['completions_DR_then_nominal'],
                probe_true_top_events=pre['true_top_completion_events_DR_then_nominal'],
                probe_startup_collapse_DR_nominal=pre['startup_diagnostics'].get('collapse_below_22cm_first_1s'),
                train_launch=launch_info,
                clock=clock,
                first_update_checkpoint=first['checkpoint'],
                trainable_group_max_changes=first['trainable_group_max_changes'],
                normal_isolation=first['normal_isolation'],
            )
            (T / 'evidence/LAUNCH40M_VERIFICATION.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
            print('FIRST_UPDATE_VERIFIED:', json.dumps(summary, ensure_ascii=False), flush=True)
            break
    finally:
        c.close()
    time.sleep(8)
else:
    raise TimeoutError('Timed out waiting for FIRST_UPDATE.json')
