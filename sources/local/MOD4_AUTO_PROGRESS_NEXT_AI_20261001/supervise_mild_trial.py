"""Save-boundary handover and whitelist DR trial on the SAME effective-time ledger.

Install in the candidate's isaac/mod4. Import safe. No copied 10-hour budget.
One run only: a restart must first reconcile any surviving process/active segment.
"""
from pathlib import Path
import fcntl
import json
import os
import re
import signal
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[2]
CODE = ROOT / 'isaac/mod4'
OLD = Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930')
HANDOFF = Path('/home/egde/rl_candidates/MOD4_AUTO_PROGRESS_NEXT_AI_20261001')
REPORTS = ROOT / 'reports'
CANONICAL = OLD / 'TRAINING_BUDGET_10H.json'
import supervise_native_floor as base
base.ROOT, base.CODE, base.REPORTS, base.BUDGET_PATH = ROOT, CODE, REPORTS, CANONICAL
from admission_gate import assess
STATE = base.STATE
PROFILE = 'white_v1'
LOCKS = []
LIVE = None


def read(path):
    return json.loads(Path(path).read_text())


def identity(pid):
    p = Path('/proc') / str(pid)
    try:
        stat = (p/'stat').read_text().rsplit(')', 1)[1].split()
        return {'pid': pid, 'state': stat[0], 'start_ticks': int(stat[19]),
                'cwd': str((p/'cwd').resolve()),
                'argv': [v.decode() for v in (p/'cmdline').read_bytes().split(b'\0') if v]}
    except (OSError, ValueError):
        return None


def active_processes(suffixes):
    result = []
    for p in Path('/proc').glob('[0-9]*/cmdline'):
        ident = identity(int(p.parent.name))
        if ident and ident['state'] != 'Z' and any(a.endswith(suffixes) for a in ident['argv']):
            result.append(ident)
    return result


def environment():
    cfg = read(CODE/'env.json')
    required = {'RM_DR_OFF':'1', 'RM_CONTACT_INTEGRATED':'1', 'RM_CONTACT_EAGER5MS':'1',
                'RM_FLAT_NATIVE_PLANE':'1', 'RM_KEEP_STD':'1', 'RM_GYRO_CURRICULUM':'0',
                'RM_SOLVER_POS':'16', 'RM_SOLVER_VEL':'4', 'RM_MOD4_TERRAIN':'flat'}
    assert all(str(cfg.get(k)) == v for k,v in required.items())
    assert float(cfg['RM_CMD_VX_MIN']) == -1.5 and float(cfg['RM_CMD_VX_MAX']) == 1.5
    assert float(cfg['RM_NOMINAL_HEIGHT']) == .25 and float(cfg['RM_REL_STANDING']) == .1
    env = {k:v for k,v in os.environ.items() if not k.startswith('RM_')}
    env.update({k:str(v) for k,v in cfg.items()})
    env.update(RM_MILD_DR_PROFILE=PROFILE, ISAACSIM_ACCEPT_EULA='Y',
               OMNI_KIT_ACCEPT_EULA='YES', PYTHONUNBUFFERED='1')
    return env


base.runtime_env = environment


def acquire(path):
    stream = path.open('a')
    fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
    LOCKS.append(stream)


def update_stage(stage, **kw):
    base.status(stage=stage, supervisor_pid=os.getpid(), canonical_budget=str(CANONICAL),
                profile=PROFILE, dr_enabled=(PROFILE == 'white_v1'), **kw)


def verify_candidate():
    frozen = read(ROOT/'CANDIDATE_SOURCE_FREEZE_v2.json')
    # Manifest structure is intentionally explicit: do not silently accept another recipe.
    entries = frozen.get('sha256', frozen.get('files'))
    assert entries, 'unrecognized frozen source manifest'
    for name, expected in entries.items():
        value = expected.get('sha256') if isinstance(expected, dict) else expected
        path = Path(name)
        if not path.is_absolute():
            path = ROOT/path if (ROOT/path).exists() else CODE/path
        assert base.sha(path) == value, 'candidate source drift: '+str(path)
    small = read(HANDOFF/'small_preflight_status.json')
    assert small.get('small_preflights_pass') and small.get('paired_initial_reset_exactly_equal')
    assert small['parameter_readback_pass']
    for key in ('alternate_seed_nominal_admission','mild_paired_admission',
                'paired_nominal_admission','original_seed_nominal_admission'):
        assert small[key]['eligible_for_mild_dr_trial'], key
    base.atomic_json(REPORTS/'small_preflight_receipt.json', small)
    environment()


def handover():
    receipt_path = REPORTS/'handover_completed.json'
    if receipt_path.exists():
        assert not base.trainers(), 'existing trainer: do not restart handover'
        assert not base.budget_state().get('active_segment'), 'reconcile stopped session first'
        return Path(read(receipt_path)['nominal_checkpoint']['path'])
    old_status = read(OLD/'status.json')
    parent = identity(int(old_status['supervisor_pid']))
    trainer = identity(int(old_status['training_pid']))
    assert parent and trainer and trainer['cwd'] == str(OLD) and parent['cwd'] == str(OLD)
    assert any(a.endswith('/train_mod4_ppo.py') for a in trainer['argv'])
    assert any('supervise_native_floor' in a or 'restart_native_floor_20261001.py' in a for a in parent['argv'])
    assert [v['pid'] for v in active_processes(('/train_mod4_ppo.py',))] == [trainer['pid']]
    assert not active_processes(('/validate_speed.py','/mild_parameter_probe.py','/mild_fullscale_probe.py'))
    base.atomic_json(REPORTS/'ledger_before_handover.json', base.budget_state())
    base.atomic_json(REPORTS/'status_before_handover.json', old_status)
    base.atomic_json(REPORTS/'processes_before_handover.json', {'parent':parent,'trainer':trainer})
    update_stage('waiting_complete_save', training_pid=trainer['pid'], active_log=old_status['active_log'])
    # Suspend only this verified supervisor's launch/accounting loop, never its trainer.
    os.kill(parent['pid'], signal.SIGSTOP)
    stopped = False
    try:
        assert identity(parent['pid'])['start_ticks'] == parent['start_ticks']
        # Check again after suspending to close the automatic-evaluation launch race.
        assert not active_processes(('/validate_speed.py','/mild_parameter_probe.py'))
        ck = base.latest(OLD/'logs')
        stop = ck.parent/'STOP_AFTER_SAVE'
        assert not stop.exists(), 'existing stop request needs review'
        stop.write_text('Authorized whitelist DR handover; save complete actor/critic/optimizer/std first.\n')
        began = time.time()
        while True:
            current = identity(trainer['pid'])
            if current is None or current['state'] == 'Z':
                break
            assert current['start_ticks'] == trainer['start_ticks'], 'PID reused'
            assert time.time()-began < 1200, 'save boundary timeout'
            base.status(last_health_check=time.time())
            time.sleep(.5)
        ended = time.time()
        ck = base.latest(OLD/'logs')
        info = base.checkpoint(ck)
        saved = read(ck.parent/'latest_complete.json')
        assert Path(saved['checkpoint']) == ck and int(saved['pid']) == trainer['pid']
        logtext = Path(old_status['active_log']).read_text(errors='replace')
        assert 'Full checkpoint saved; authorized budget or stop-file reached' in logtext, 'missing graceful-save evidence'
        b = base.budget_state(); a = b['active_segment']
        assert a and a['pid'] == trainer['pid']
        tail = max(0., ended-float(a['accounted_through_epoch']))
        b['charged_training_seconds'] = float(b['charged_training_seconds'])+tail
        b['remaining_training_seconds'] = max(0., 36000-b['charged_training_seconds'])
        a.update(accounted_through_epoch=ended, ended_epoch=ended,
                 end_evidence='verified process exited after latest_complete atomic save',
                 observation_uncertainty_upper_s=.5)
        b.setdefault('completed_segments', []).append(a); b['active_segment'] = None
        base.atomic_json(CANONICAL, b)
        stopped = True
        # Trainer has exited completely; the suspended supervisor cannot launch a final probe.
        os.kill(parent['pid'], signal.SIGTERM)
        os.kill(parent['pid'], signal.SIGCONT)
        for _ in range(100):
            ident = identity(parent['pid'])
            if ident is None or ident['state'] == 'Z': break
            time.sleep(.1)
        assert not base.trainers()
        acquire(OLD/'native_floor_supervisor.lock')
        old_status.update(stage='handed_over_to_mild_dr_preflight', training_pid=None,
                          supervisor_pid=None, handover_root=str(ROOT), latest_checkpoint=str(ck),
                          remaining_training_seconds=b['remaining_training_seconds'], updated_at=time.time())
        base.atomic_json(OLD/'status.json', old_status)
        result = {'nominal_checkpoint':info,'old_parent':parent,'old_trainer':trainer,
                  'tail_charged_s':tail,'charged_training_seconds':b['charged_training_seconds'],
                  'canonical_budget':str(CANONICAL),'old_checkpoint_preserved':True,
                  'future_old_launches_disabled':True,'ended_epoch':ended}
        base.atomic_json(receipt_path,result)
        return ck
    finally:
        if not stopped:
            ident = identity(parent['pid'])
            if ident and ident['start_ticks'] == parent['start_ticks']:
                os.kill(parent['pid'], signal.SIGCONT)


def training(ck, count, name, logroot, profile, duration=None):
    global LIVE, PROFILE
    PROFILE = profile
    assert not base.trainers() and not base.budget_state().get('active_segment')
    b = base.budget_state(); remaining = 36000-float(b['charged_training_seconds'])
    assert remaining > 120
    began = time.time(); deadline = began+min(remaining, duration or remaining)
    base.update_budget(deadline_epoch=began+remaining, owner_root=str(ROOT),
                       budget_scope='Same 36000 seconds: all PPO processes including preflight; isolated frozen evaluation pause excluded')
    number = 0
    while (ROOT/f'train_mild_{name}_{number}.log').exists(): number += 1
    log = ROOT/f'train_mild_{name}_{number}.log'
    p = base.spawn(['isaac/mod4/train_mod4_ppo.py','--headless','--num_envs',str(count),
        '--additional_iterations', '2' if name == 'ppo_preflight' else '100000',
        '--steps_per_env','24','--save_interval', '2' if name == 'ppo_preflight' else '25',
        '--learning_rate','.0001','--seed','20260928','--run_name','scut_mild_'+name,
        '--log_root',str(logroot),'--init_checkpoint',str(ck)], log, deadline)
    LIVE = p
    base.start_segment(p,name,log)
    update_stage('ppo_preflight' if name == 'ppo_preflight' else 'training', training_pid=p.pid,
        num_envs=count,steps_per_env=24,active_log=str(log),resume_checkpoint=base.checkpoint(ck),
        deadline_epoch=began+remaining,trainer_deadline_epoch=deadline,production_started_epoch=began,
        training_phase=name,scope='SCUT flat 1.5 m/s with explicit mild DR whitelist; no calibrated spring DR or Rough yet')
    ep = None; eval_out = None; next_eval = began+1800
    while p.poll() is None:
        base.account_segment()
        latest = base.latest(logroot)
        if latest:
            base.status(latest_checkpoint=str(latest), iteration=base.checkpoint(latest)['iteration_stored'], log_dir=str(latest.parent))
        if name in ('continued_mild','nominal_regression_fallback','nominal_fallback') and latest:
            if ep is None and time.time()>=next_eval and time.time()<deadline-900:
                assert not active_processes(('/validate_speed.py','/mild_parameter_probe.py'))
                eval_out=REPORTS/f'hourly_{profile}_model{base.checkpoint(latest)["iteration_stored"]}.json'
                ep=base.spawn(['isaac/mod4/validate_speed.py','--headless','--checkpoint',str(latest),
                    '--speed_limit','1.5','--ramp_suite','--seed','20260927','--num_envs','80',
                    '--steps','1500','--dr-profile',profile,'--output',str(eval_out)],eval_out.with_suffix('.log'))
                base.status(evaluation_pid=ep.pid,evaluation_path=str(eval_out))
                next_eval=time.time()+3600
            if ep is not None and ep.poll() is not None:
                if ep.returncode==0 and eval_out.exists():
                    r=read(eval_out)
                    base.status(latest_evaluation=r,experimental_admission=assess(r),
                                legacy_gate_pass=r.get('strict_pass_window'),evaluation_error=None)
                else:base.status(evaluation_error=str(eval_out))
                ep=None;base.status(evaluation_pid=None)
        base.status(last_health_check=time.time())
        time.sleep(1 if name=='ppo_preflight' else 5)
    base.account_segment(finish=True); LIVE = None
    base.status(training_pid=None,training_exit_code=p.returncode)
    if ep is not None:
        r=base.wait_probe(ep,eval_out,timeout=1800)
        base.status(evaluation_pid=None,latest_evaluation=r,experimental_admission=assess(r))
    text = log.read_text(errors='replace')
    assert p.returncode == 0 and 'Traceback (most recent call last)' not in text, 'training fault; preserve checkpoint and ledger'
    latest = base.latest(logroot); assert latest
    info = base.checkpoint(latest)
    manifest = read(latest.parent/'run_manifest.json')
    assert manifest['start_iteration'] == base.checkpoint(ck)['iteration_stored']
    assert manifest['env']['RM_KEEP_STD'] == '1' and manifest['env']['RM_MILD_DR_PROFILE'] == profile
    if name == 'ppo_preflight':
        times = [float(v) for v in re.findall(r'Iteration time:\s*([0-9.]+)s',text)]
        assert len(times) == 2 and info['iteration_stored'] >= manifest['start_iteration']+1
        base.atomic_json(REPORTS/'ppo_preflight_128.json', {'pass':True,'checkpoint':info,
            'weights_discarded':True,'production_checkpoint':str(ck),'iteration_time_s':times,
            'charged_to_same_canonical_budget':True})
    return latest


def frozen(ck, name, seed, profile):
    global PROFILE, LIVE
    PROFILE = profile
    assert not base.trainers()
    out = REPORTS/(name+'.json')
    if out.exists(): return read(out)
    p = base.spawn(['isaac/mod4/validate_speed.py','--headless','--checkpoint',str(ck),
        '--speed_limit','1.5','--ramp_suite','--seed',str(seed),'--num_envs','80',
        '--steps','1500','--dr-profile',profile,'--output',str(out)],out.with_suffix('.log'))
    LIVE = p
    update_stage('trial_evaluation',training_pid=None,evaluation_pid=p.pid,evaluation_path=str(out),
                 active_log=str(out.with_suffix('.log')))
    r = base.wait_probe(p,out,timeout=1800); LIVE = None
    base.status(evaluation_pid=None, latest_evaluation=r, legacy_gate_pass=r.get('strict_pass_window'))
    return r


def fullscale(ck):
    global PROFILE, LIVE
    PROFILE = 'white_v1'
    out = REPORTS/'mild_fullscale_20k.json'
    p = base.spawn(['isaac/mod4/mild_fullscale_probe.py','--headless','--checkpoint',str(ck),
        '--num_envs','20000','--steps','120','--output',str(out)],out.with_suffix('.log'))
    LIVE = p
    update_stage('validating_20k_mild_dr',training_pid=None,validation_pid=p.pid,active_log=str(out.with_suffix('.log')))
    r = base.wait_probe(p,out); LIVE = None
    passed, acceptance = base.accept_physics_smoke(r)
    assert passed and r['mild_initial_parameters']['actual_parameters_pass'] and r['mild_final_parameters']['actual_parameters_pass']
    assert r['mild_final_parameters']['num_envs'] == 20000
    base.atomic_json(REPORTS/'mild_fullscale_acceptance.json',acceptance)
    base.status(validation_pid=None,physics_preflight=r)


def main():
    REPORTS.mkdir(exist_ok=True)
    acquire(ROOT/'mild_trial_supervisor.lock')
    assert not (REPORTS/'mild_production_started.json').exists(), 'one-time handover already executed; reconcile before recovery'
    # Wait for the already-running small evaluator; never open a duplicate probe.
    update_stage('waiting_small_preflights',training_pid=None)
    while True:
        s = read(HANDOFF/'small_preflight_status.json')
        if s.get('small_preflights_pass'): break
        assert s.get('stage') != 'preflight_needs_review', s.get('error')
        assert base.budget_state()['remaining_training_seconds'] > 7200, 'insufficient safe-trial budget'
        time.sleep(10)
    verify_candidate()
    while active_processes(('/validate_speed.py','/mild_parameter_probe.py')): time.sleep(5)
    nominal = handover()
    # All large production is now stopped; PPO preflight consumes the same budget.
    try:
        training(nominal,128,'ppo_preflight',ROOT/'preflight_logs','white_v1')
        fullscale(nominal)
    except Exception:
        base.atomic_json(REPORTS/'preflight_failure.json',{'error':traceback.format_exc(),'fallback_checkpoint':str(nominal)})
        assert not base.trainers() and not base.budget_state().get('active_segment')
        final=training(nominal,20000,'nominal_fallback',ROOT/'fallback_logs','nominal')
        evaluation=frozen(final,'final_nominal_fallback',20261001,'nominal')
        update_stage('finished_nominal_fallback',final_checkpoint=base.checkpoint(final),final_evaluation=evaluation,
                     outcome='DR preflight failed; original nominal full-state checkpoint restored')
        return
    base.atomic_json(REPORTS/'mild_production_started.json',{'checkpoint':base.checkpoint(nominal),
        'started_epoch':time.time(),'canonical_budget':str(CANONICAL),'preflight_weights_discarded':True,
        'profile':'white_v1','trial_seconds':3600})
    trial = training(nominal,20000,'trial_60min',ROOT/'logs','white_v1',duration=3600)
    pair = {}; gates = {}
    for seed in (20261001,20260927):
        a=frozen(trial,f'trial_model{base.checkpoint(trial)["iteration_stored"]}_nominal_seed{seed}',seed,'nominal')
        d=frozen(trial,f'trial_model{base.checkpoint(trial)["iteration_stored"]}_mild_seed{seed}',seed,'white_v1')
        assert a['reset_joint_pos_before_physics']==d['reset_joint_pos_before_physics'] and a['reset_root_before_physics']==d['reset_root_before_physics']
        pair[str(seed)]={'nominal':a,'mild':d}
        gates[str(seed)]={'nominal':assess(a),'mild':assess(d)}
    allowed=all(v['eligible_for_mild_dr_trial'] for s in gates.values() for v in s.values())
    base.atomic_json(REPORTS/'trial_multiseed_decision.json',{'continue_mild':allowed,'gates':gates,
        'legacy_graduation_criteria_changed':False,'spring_300_700N_validated':False})
    profile='white_v1' if allowed else 'nominal'
    chosen=trial if allowed else nominal
    final=training(chosen,20000,'continued_mild' if allowed else 'nominal_regression_fallback',
                   ROOT/'logs' if allowed else ROOT/'fallback_logs',profile)
    f_nom=frozen(final,'final_nominal',20261001,'nominal')
    f_dr=frozen(final,'final_mild',20261001,'white_v1')
    base.status(stage='finished',training_pid=None,evaluation_pid=None,final_checkpoint=base.checkpoint(final),
        final_evaluation={'nominal':f_nom,'mild':f_dr}, latest_evaluation=f_dr,
        outcome='Effective budget exhausted; calibrated spring DR/Rough/2m remain separate tasks')


if __name__ == '__main__':
    try: main()
    except BaseException:
        update_stage('attention_required',error=traceback.format_exc(),
                     child_pid=LIVE.pid if LIVE and LIVE.poll() is None else None,
                     instructions='Inspect real processes and canonical active segment before any recovery; do not reset the budget.')
        raise
