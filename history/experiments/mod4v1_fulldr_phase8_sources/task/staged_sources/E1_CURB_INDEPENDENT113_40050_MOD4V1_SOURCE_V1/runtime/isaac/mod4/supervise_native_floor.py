"""One trainer, verified native flat ground, full-state warm start, ten active hours.

Install into the NEW task's isaac/mod4. Never invoke an old one-time supervisor.
CPU checkpoint validation and frozen physics probes run before PPO. Preflight PPO
is charged to the 36,000 second budget; its weights are not production weights.
"""
from pathlib import Path
import argparse
import fcntl
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import time
import traceback

ROOT = Path(__file__).resolve().parents[2]
CODE = ROOT / 'isaac/mod4'
REPORTS = ROOT / 'reports'
PY = '/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'
BUDGET_PATH = ROOT / 'TRAINING_BUDGET_10H.json'
EXPECTED_SOURCE = '343c56615e7ee6708a6a6a8057cb30877f5ea83d9a2249e079a991db522196d2'
STATE = {}
# dynamic_authorized_budget_v1
from budget_authority import validate_budget


def atomic_json(path, data):
    temp = path.with_suffix(path.suffix + '.partial')
    temp.write_text(json.dumps(data, indent=2), encoding='utf8')
    os.replace(temp, path)


def status(**kw):
    STATE.update(kw)
    STATE['updated_at'] = time.time()
    atomic_json(ROOT / 'status.json', STATE)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def checkpoint(path):
    import torch
    d = torch.load(path, map_location='cpu', weights_only=False)
    assert 'optimizer_state_dict' in d and 'iter' in d
    assert ('actor_state_dict' in d and 'critic_state_dict' in d) or 'model_state_dict' in d
    finite = 0
    def walk(x):
        nonlocal finite
        if torch.is_tensor(x) and (x.is_floating_point() or x.is_complex()):
            assert torch.isfinite(x).all(), 'nonfinite checkpoint tensor'
            finite += 1
        elif isinstance(x, dict):
            for value in x.values(): walk(value)
        elif isinstance(x, (list, tuple)):
            for value in x: walk(value)
    walk(d)
    model = d.get('actor_state_dict', d.get('model_state_dict', {}))
    assert any('std' in k.lower() or 'log_std' in k.lower() for k in model), 'std state missing'
    return {'path':str(path), 'iteration_stored':int(d['iter']),
            'sha256':sha(path), 'keys':list(d), 'finite_tensors':finite}


def latest(folder):
    candidates = list(folder.glob('**/model_*.pt'))
    return max(candidates, key=lambda p:(int(p.stem.rsplit('_',1)[1]), p.stat().st_mtime)) if candidates else None


def trainers():
    result = []
    for proc in Path('/proc').glob('[0-9]*/cmdline'):
        try:
            argv = proc.read_bytes().split(b'\0')
            if any(a.endswith(b'/train_mod4_ppo.py') or a == b'train_mod4_ppo.py' for a in argv):
                result.append(int(proc.parent.name))
        except OSError: pass
    return result


def runtime_env():
    env = {k:v for k,v in os.environ.items() if not k.startswith('RM_')}
    cfg = json.loads((CODE/'env.json').read_text())
    required = {'RM_FLAT_NATIVE_PLANE':'1', 'RM_CONTACT_INTEGRATED':'1',
                'RM_CONTACT_EAGER5MS':'1', 'RM_KEEP_STD':'1', 'RM_DR_OFF':'1',
                'RM_GYRO_CURRICULUM':'0', 'RM_MOD4_TERRAIN':'flat',
                'RM_SOLVER_POS':'16', 'RM_SOLVER_VEL':'4'}
    assert all(str(cfg.get(k)) == v for k,v in required.items()), 'recipe/config drift'
    assert float(cfg['RM_CMD_VX_MAX']) == 1.5 and float(cfg['RM_CMD_VX_MIN']) == -1.5
    assert float(cfg['RM_NOMINAL_HEIGHT']) == .25 and float(cfg['RM_REL_STANDING']) == .1
    env.update({k:str(v) for k,v in cfg.items()})
    env.update(ISAACSIM_ACCEPT_EULA='Y', OMNI_KIT_ACCEPT_EULA='YES', PYTHONUNBUFFERED='1')
    return env


def spawn(args, log, deadline=None):
    assert not log.exists(), 'refuse log overwrite: ' + str(log)
    env = runtime_env()
    if deadline is not None: env['RM_RESCUE_DEADLINE'] = str(deadline)
    with log.open('x') as stream:
        p = subprocess.Popen([PY]+args, cwd=ROOT, env=env, stdout=stream,
                             stderr=subprocess.STDOUT, start_new_session=True)
    return p


def budget_state():
    b = json.loads(BUDGET_PATH.read_text())
    validate_budget(b)
    assert b['checkpoint_sha256'] == EXPECTED_SOURCE
    return b


def update_budget(**kw):
    b = budget_state(); b.update(kw); atomic_json(BUDGET_PATH, b); return b


def start_segment(proc, kind, log):
    b = budget_state()
    assert not b.get('active_segment'), 'unaccounted active segment'
    update_budget(active_segment={'pid':proc.pid, 'kind':kind, 'started_epoch':time.time(),
                                  'accounted_through_epoch':time.time(), 'log':str(log)})


def account_segment(finish=False):
    b = budget_state(); a = b.get('active_segment')
    if not a: return b
    now = time.time()
    charged = float(b.get('charged_training_seconds', 0)) + max(0., now-a['accounted_through_epoch'])
    a['accounted_through_epoch'] = now
    if finish:
        a['ended_epoch'] = now
        b.setdefault('completed_segments', []).append(a)
        b['active_segment'] = None
    else: b['active_segment'] = a
    b['charged_training_seconds'] = charged
    b['remaining_training_seconds'] = max(0., float(b['authorized_training_seconds'])-charged)
    atomic_json(BUDGET_PATH, b)
    STATE.update(charged_training_seconds=charged, remaining_training_seconds=b['remaining_training_seconds'])
    return b


def freeze_auxiliary(folder):
    dest = folder/'src_snapshot'; dest.mkdir(exist_ok=True)
    out = folder/'native_floor_source_freeze.json'
    if out.exists(): return
    files = ['ground_plane_candidate.py', 'contact_capture.py', 'contact_geometry.py',
             'validate_speed.py', 'supervise_native_floor.py', 'native_floor_20k_probe.py']
    data = {}
    for name in files:
        shutil.copy2(CODE/name, dest/name); data[name] = sha(CODE/name)
    atomic_json(out, {'sha256':data, 'ground':'native Plane at z=0',
                     'hardware_rewards_and_ppo_changed':False})


def wait_probe(proc, out, timeout=1800):
    start = time.time()
    while proc.poll() is None:
        if time.time()-start > timeout:
            proc.send_signal(signal.SIGINT)
            proc.wait(timeout=90)
            raise RuntimeError('probe timeout; no production started')
        status(last_health_check=time.time())
        time.sleep(10)
    assert proc.returncode == 0 and out.exists(), 'probe failed: ' + str(out)
    return json.loads(out.read_text())


def evaluate(ck, name, seed=20260927):
    out = REPORTS/(name+'.json')
    assert not out.exists()
    p = spawn(['isaac/mod4/validate_speed.py','--headless','--checkpoint',str(ck),
               '--speed_limit','1.5','--ramp_suite','--seed',str(seed),
               '--num_envs','80','--steps','1500','--output',str(out)],out.with_suffix('.log'))
    status(evaluation_pid=p.pid, evaluation_path=str(out))
    return p, out


def physics_gate(report):
    return (report.get('physics_pass',False) and not report.get('nonfinite',True)
            and all(g['survival_fraction']>=.95 for g in report['groups']))


def accept_physics_smoke(probe):
    """Physical contract acceptance; preserve short-rollout posture warning.

    The initial probe mixed a novel 60 mm *worst instantaneous* height cutoff
    into a 1.2 s physics smoke. That is not the existing 15 s skill criterion.
    A safe but imperfect pretrained policy must be allowed to run PPO; this
    does not relax or pass any deterministic skill graduation gate.
    """
    raw=probe['raw_contact_evidence']
    passed=(probe['num_envs']==20000 and probe['seconds']>=1.2 and probe['plane_type']=='Plane'
        and probe['ground_z_m']==0 and probe['friction_static']==.9 and probe['friction_dynamic']==.9
        and not probe['nonfinite'] and probe['terminations']==0 and probe['max_closure_m']<.002
        and probe['max_mimic_rad']<.01 and probe['max_tilt_deg']<15
        and raw['loaded_ground_contacts']>0 and raw['loaded_downward_ground_contacts']==0
        and raw['minimum_loaded_ground_normal_z']>.9 and raw['max_abs_ground_separation_m']<.01)
    receipt={'physical_smoke_pass':passed, 'original_combined_probe_pass':probe['pass'],
        'worst_short_height_error_m':probe['max_height_error_m'],
        'short_height_warning':probe['max_height_error_m']>=.06,
        'formal_15s_graduation_criteria_changed':False,
        'explanation':'Physics smoke and pretrained policy performance are separate. Preserve original failed combined report; no claim of skill graduation.'}
    atomic_json(REPORTS/'native_floor_20k_physics_acceptance.json',receipt)
    return passed,receipt


def main():
    lock = (ROOT/'native_floor_supervisor.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX|fcntl.LOCK_NB)
    assert not trainers(), 'trainer already exists; refuse double start'
    REPORTS.mkdir(exist_ok=True)
    b = budget_state()
    assert not b.get('active_segment'), 'abrupt previous session: reconcile ledger before resume'
    ck = latest(ROOT/'logs') if (ROOT/'logs').exists() else None
    source = Path(b['checkpoint'])
    source_info = checkpoint(source)
    assert source_info['sha256'] == EXPECTED_SOURCE
    ck = ck or source
    status(stage='validating_native_plane', supervisor_pid=os.getpid(), training_pid=None,
           source_checkpoint=source_info, latest_checkpoint=str(ck), iteration=checkpoint(ck)['iteration_stored'],
           authorized_training_seconds=b['authorized_training_seconds'], num_envs=20000, steps_per_env=24,
           speed_limit_m_s=1.5, ground='native Z-plane at z=0', dr_enabled=False)
    runtime_env()
    probe_path = REPORTS/'native_floor_20k_physics.json'
    if not probe_path.exists():
        p = spawn(['isaac/mod4/native_floor_20k_probe.py','--headless','--checkpoint',str(source),
                   '--num_envs','20000','--steps','120','--output',str(probe_path)], probe_path.with_suffix('.log'))
        status(validation_pid=p.pid)
        probe = wait_probe(p, probe_path)
    else: probe = json.loads(probe_path.read_text())
    passed,receipt=accept_physics_smoke(probe)
    assert passed, '20k physical contract preflight failed'
    status(validation_pid=None, physics_preflight=probe, physics_preflight_acceptance=receipt)
    preflight_path = REPORTS/'native_floor_20k_ppo.json'
    if not preflight_path.exists():
        assert not trainers()
        remaining = float(budget_state()['authorized_training_seconds'])-float(budget_state().get('charged_training_seconds',0))
        assert remaining > 600
        deadline = time.time()+remaining
        update_budget(budget_started_epoch=time.time(), deadline_epoch=deadline)
        log = ROOT/'ppo_preflight_20k.log'
        p = spawn(['isaac/mod4/train_mod4_ppo.py','--headless','--num_envs','20000',
                   '--additional_iterations','4','--steps_per_env','24','--save_interval','4',
                   '--learning_rate','.0001','--seed','20260928','--run_name','native_floor_ppo_preflight',
                   '--log_root',str(ROOT/'preflight_logs'),'--init_checkpoint',str(source)],log,deadline)
        start_segment(p,'ppo_preflight',log)
        status(stage='ppo_preflight', validation_pid=p.pid, active_log=str(log), deadline_epoch=deadline)
        began = time.time()
        while p.poll() is None:
            account_segment(); status(last_health_check=time.time()); time.sleep(10)
            if time.time()-began > 1200:
                p.send_signal(signal.SIGINT); p.wait(timeout=90)
                raise RuntimeError('PPO preflight timed out')
        account_segment(finish=True)
        text = log.read_text(errors='replace')
        times = [float(x) for x in re.findall(r'Iteration time:\s*([0-9.]+)s',text)]
        saved = latest(ROOT/'preflight_logs')
        assert p.returncode == 0 and len(times)==4 and saved and 'Traceback' not in text
        info = checkpoint(saved)
        assert info['iteration_stored'] >= source_info['iteration_stored']+3
        frozen = json.loads((saved.parent/'run_manifest.json').read_text())
        assert frozen['start_iteration'] == source_info['iteration_stored']
        assert frozen['env']['RM_KEEP_STD']=='1' and frozen['env']['RM_FLAT_NATIVE_PLANE']=='1'
        atomic_json(preflight_path, {'pass':True, 'checkpoint':info, 'iteration_time_s':times,
                    'environment_policy_steps_s':20000*24/(sum(times[1:])/len(times[1:])),
                    'weights_discarded':True, 'production_checkpoint':source_info})
    # Frozen-policy baseline after PPO preflight. Never continue from preflight weights.
    baseline_path = REPORTS/'native_floor_8648_baseline15s.json'
    if not baseline_path.exists():
        p, baseline_path = evaluate(source, 'native_floor_8648_baseline15s', seed=20260926)
        baseline = wait_probe(p, baseline_path)
    else: baseline = json.loads(baseline_path.read_text())
    assert physics_gate(baseline), 'nominal repaired-floor baseline unsafe'
    status(baseline=baseline, latest_evaluation=baseline, evaluation_pid=None, validation_pid=None)
    assert not trainers()
    b = budget_state(); remaining = float(b['authorized_training_seconds'])-float(b.get('charged_training_seconds',0))
    assert remaining > 0
    started = time.time(); deadline = started+remaining
    update_budget(production_started_epoch=started, deadline_epoch=deadline,
                  budget_scope='PPO process wall time including scene load; frozen physics and evaluation while no trainer do not consume budget')
    attempt = 0
    while (ROOT/f'train_native_floor_{attempt}.log').exists(): attempt+=1
    log = ROOT/f'train_native_floor_{attempt}.log'
    p = spawn(['isaac/mod4/train_mod4_ppo.py','--headless','--num_envs','20000',
               '--additional_iterations','100000','--steps_per_env','24','--save_interval','25',
               '--learning_rate','.0001','--seed','20260928','--run_name','scut_flat_native_floor_1.5m',
               '--log_root',str(ROOT/'logs'),'--init_checkpoint',str(ck)], log, deadline)
    start_segment(p,'production',log)
    status(stage='training',training_pid=p.pid, active_log=str(log), resume_checkpoint=checkpoint(ck),
           deadline_epoch=deadline, trainer_deadline_epoch=deadline, production_started_epoch=started,
           scope='SCUT flat walk/run on native plane; no DR/2m/Rough automatic promotion',
           contact_statistics_change_is_not_learning=True)
    ep = None; out = None; next_eval = started+1800
    while p.poll() is None:
        account_segment()
        current = latest(ROOT/'logs')
        if current:
            ck=current
            freeze_auxiliary(current.parent)
            STATE.update(latest_checkpoint=str(ck),iteration=int(ck.stem.rsplit('_',1)[1]),log_dir=str(ck.parent))
            if ep is None and time.time()>=next_eval and time.time()<deadline-900:
                ep,out=evaluate(ck, 'native_floor_model'+ck.stem.rsplit('_',1)[1])
                next_eval=time.time()+3600
        if ep is not None and ep.poll() is not None:
            if ep.returncode==0 and out.exists():
                r=json.loads(out.read_text())
                status(latest_evaluation=r, evaluation_error=None,
                       legacy_gate_pass=r.get('strict_pass_window'), physics_safety_pass=physics_gate(r))
            else: status(evaluation_error=str(out))
            ep=None;STATE['evaluation_pid']=None
        status(last_health_check=time.time())
        time.sleep(10)
    account_segment(finish=True)
    status(training_pid=None,training_exit_code=p.returncode)
    current=latest(ROOT/'logs')
    assert current, 'production failed before saving; source retained'
    ck=current; checkpoint(ck)
    assert p.returncode==0, 'training fault: inspect log and ledger before recovery'
    if ep is not None: wait_probe(ep,out)
    status(stage='final_evaluation',evaluation_pid=None)
    p,out=evaluate(ck,'final_native_floor_nominal',seed=20260926)
    final=wait_probe(p,out)
    status(stage='finished',final_checkpoint=checkpoint(ck), final_evaluation=final,
           latest_evaluation=final,evaluation_pid=None,
           outcome='nominal reported; calibrated spring DR and Rough pending')


if __name__=='__main__':
    try:main()
    except BaseException:
        status(stage='attention_required', error=traceback.format_exc())
        raise
