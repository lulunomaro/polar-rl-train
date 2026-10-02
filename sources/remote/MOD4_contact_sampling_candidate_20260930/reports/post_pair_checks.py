"""Isolated checks only. Does not stop, adopt, or launch a production trainer."""
from pathlib import Path
import json, os, subprocess, time

ROOT = Path('/home/egde/rl_candidates/MOD4_contact_sampling_candidate_20260930')
REPORTS = ROOT / 'reports'
PYTHON = '/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'
status = {'status': 'waiting_for_pair', 'production_handover': False}

def save():
    (REPORTS / 'preflight_status.json').write_text(json.dumps(status, indent=2))

def run(name, argv, timeout=1000):
    status.update(status='running', active_check=name); save()
    env = dict(os.environ)
    env.update({k: str(v) for k, v in json.loads((ROOT/'isaac/mod4/env.json').read_text()).items()})
    env.update(RM_CONTACT_EAGER5MS='1', ISAACSIM_ACCEPT_EULA='Y',
               OMNI_KIT_ACCEPT_EULA='YES', PYTHONUNBUFFERED='1')
    with (REPORTS / (name + '.log')).open('x') as f:
        p = subprocess.Popen([PYTHON] + argv, cwd=ROOT, env=env,
                             stdout=f, stderr=subprocess.STDOUT)
        status['active_pid'] = p.pid; save()
        rc = p.wait(timeout=timeout)
    if rc:
        raise RuntimeError(f'{name} exit {rc}')

try:
    save()
    while True:
        pair = json.loads((REPORTS / 'pair_status.json').read_text())
        if pair['status'] == 'failed':
            raise RuntimeError('Paired runtime failed; no further checks')
        if pair['status'] == 'complete':
            break
        time.sleep(10)
    old = json.loads((REPORTS / 'legacy10ms.json').read_text())
    new = json.loads((REPORTS / 'eager5ms.json').read_text())
    assert pair['production_source_unchanged']
    assert old['physics_pass'] and new['physics_pass']
    assert old['resets'] == new['resets'] == 0
    intervals = new['contact_diagnostic']['history_substep_update_intervals_s']
    assert intervals and all(abs(x - .005) < 1e-7 for x in intervals)
    ck = pair['checkpoint']
    out = REPORTS / 'dual_evaluator_smoke.json'
    run('dual_evaluator_smoke_v3', ['isaac/mod4/validate_speed.py', '--headless',
        '--checkpoint', ck, '--output', str(out), '--num_envs', '12',
        '--steps', '300', '--speed_limit', '1.5', '--seed', '20260927'])
    r = json.loads(out.read_text())
    assert r['physics_pass'] and not r['nonfinite']
    assert r['seconds'] == 3
    assert r['contact_capture_metadata']['enabled']
    assert 'legacy' in r['graduation_gate_contact_source']
    assert all('strict_pass_window_5ms' in g and 'height_credit_legacy' in g for g in r['groups'])
    status['evaluator_smoke_pass'] = True; save()
    smoke = ROOT / 'smoke_logs'
    run('ppo_smoke_v2', ['isaac/mod4/train_mod4_ppo.py', '--headless', '--num_envs', '128',
        '--additional_iterations', '2', '--steps_per_env', '24', '--save_interval', '1',
        '--learning_rate', '.0001', '--seed', '20260928', '--run_name', 'contact5ms_preflight',
        '--init_checkpoint', ck, '--log_root', str(smoke)])
    checkpoints = sorted(smoke.glob('**/model_*.pt'), key=lambda p: p.stat().st_mtime)
    assert checkpoints
    audit = REPORTS / 'ppo_checkpoint_audit.json'
    code = "import torch,json;from pathlib import Path;p=Path(" + repr(str(checkpoints[-1])) + ");d=torch.load(p,map_location='cpu',weights_only=False);r={'path':str(p),'keys':list(d),'iteration':d.get('iter'),'finite':all(bool(torch.isfinite(v).all()) for k in ['actor_state_dict','critic_state_dict'] for v in d.get(k,{}).values() if torch.is_tensor(v))};Path(" + repr(str(audit)) + ").write_text(json.dumps(r,indent=2))"
    subprocess.run([PYTHON, '-c', code], check=True)
    a = json.loads(audit.read_text())
    assert a['finite'] and all(k in a['keys'] for k in ['actor_state_dict', 'critic_state_dict', 'optimizer_state_dict'])
    assert a['iteration'] >= 7451
    status.update(status='complete', ppo_smoke_pass=True, checkpoint_audit=a,
                  scope='sampling and reward/statistics preflight; no production switch or graduation')
except Exception as e:
    status.update(status='failed', error=repr(e))
finally:
    status['finished'] = time.time(); status['active_pid'] = None; save()
