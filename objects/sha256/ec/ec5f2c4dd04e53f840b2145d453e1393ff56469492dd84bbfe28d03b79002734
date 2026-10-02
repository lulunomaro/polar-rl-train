"""Verified sensor robustness trial, complete-save handover, same 50h ledger.

Frozen small pairs may run alongside the sole trainer. Fullscale/PPO preflight
only follows a graceful save. Never invoke this one-shot entry again blindly.
"""
from pathlib import Path
import json, os, signal, subprocess, sys, time, traceback
import supervise_spin_rate as rate
from admission_gate import assess
ROOT=Path(__file__).resolve().parents[2];CODE=ROOT/'isaac/mod4';REPORTS=ROOT/'reports'
OLD=Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002')
base,spin,helpers=rate.base,rate.spin,rate.helpers
rate.OLD=OLD;spin.OLD=OLD
CANONICAL=rate.CANONICAL
PROBES=rate.PROBES+('/sensor_readback_probe.py',)
rate.PROBES=PROBES;spin.PROBES=PROBES
HELD=None;CHILD=None
ORIGINAL_STATUS=rate.status
ORIGINAL_TRAINING=spin.training


def training(ck,phase,**kw):
    """Pin saves to this exact trainer PID, including a lower-iteration rollback."""
    original_latest=base.latest;pid=[None]
    def pinned_latest(folder):
        folder=Path(folder)
        if folder in (ROOT/'logs',ROOT/'preflight_logs'):
            current=base.STATE.get('training_pid')
            if current:pid[0]=current
            if pid[0]:
                matches=[p for p in folder.glob('*/latest_complete.json') if int(helpers.read(p)['pid'])==pid[0]]
                assert len(matches)<=1
                return Path(helpers.read(matches[0])['checkpoint']) if matches else None
        return original_latest(folder)
    base.latest=pinned_latest
    try:return ORIGINAL_TRAINING(ck,phase,**kw)
    finally:base.latest=original_latest
spin.training=training


def status(stage=None,**kw):
    kw.pop('canonical_budget',None)
    kw['sensor_profile']=helpers.read(CODE/'env.json').get('RM_SIM2REAL_SENSOR_PROFILE','off')
    ORIGINAL_STATUS(stage,**kw)
rate.status=spin.status=status


def profile(value):
    cfg=helpers.read(CODE/'env.json');cfg['RM_SIM2REAL_SENSOR_PROFILE']=value
    base.atomic_json(CODE/'env.json',cfg)
    freeze=helpers.read(REPORTS/'SPIN_SOURCE_FREEZE.json')
    freeze['sha256']['isaac/mod4/env.json']=base.sha(CODE/'env.json')
    base.atomic_json(REPORTS/'SPIN_SOURCE_FREEZE.json',freeze)


def probe(ck,name,kind='spin',steps=1500,profile='white_v1',seed=20261002,sensor=None,small=False,limit=None):
    global CHILD
    out=REPORTS/(name+'.json');assert not out.exists()
    if sensor is None:sensor=helpers.read(CODE/'env.json')['RM_SIM2REAL_SENSOR_PROFILE']=='sensor_v1'
    assert not helpers.active_processes(PROBES)
    if not small:
        assert not base.trainers() and not base.budget_state().get('active_segment')
    args=['isaac/mod4/'+('spin_rate_probe.py' if kind=='spin' else 'validate_speed.py'),'--headless',
        '--checkpoint',str(ck),'--seed',str(seed),'--dr-profile',profile,
        '--sensor-profile','sensor_v1' if sensor else 'off','--num_envs','88' if kind=='spin' else '80',
        '--steps',str(steps),'--output',str(out)]
    args += ['--max-rate',repr(limit or rate.current_limit())] if kind=='spin' else ['--speed_limit','1.5','--ramp_suite']
    p=base.spawn(args,out.with_suffix('.log'));CHILD=p
    status('isolated_sensor_pair' if small else 'frozen_'+kind+'_evaluation',evaluation_pid=p.pid,
           evaluation_path=str(out),active_log=str(out.with_suffix('.log')))
    until=time.time()+1800
    while p.poll() is None:
        if small:
            others=[v for v in helpers.active_processes(PROBES) if v['pid']!=p.pid]
            if others:
                p.send_signal(signal.SIGINT)
                try:p.wait(timeout=90)
                except subprocess.TimeoutExpired:p.kill();p.wait()
                raise RuntimeError('Own small probe yielded to existing production evaluator; inspect error, retry unique path')
        assert time.time()<until,'Probe timed out'
        time.sleep(2)
    CHILD=None
    assert p.returncode==0 and out.exists(),out
    r=helpers.read(out)
    if sensor and profile=='white_v1':
        assert r['sensor_audit']['profile']=='sensor_v1' and r['sensor_audit']['nominal_bias_zero'] and r['sensor_audit']['nominal_lag_zero']
    status(evaluation_pid=None,**({'latest_spin_evaluation':spin.compact_spin(r)} if kind=='spin' else {'latest_evaluation':r,'experimental_admission':assess(r)}))
    return r
rate.probe=probe


def gate(r,kind):
    return r['spin_skill_pass'] if kind=='spin' else assess(r)['eligible_for_mild_dr_trial']


def paired(ck,label,small=False,limit=None,seeds=(20261002,20261003)):
    pairs=[];passed=True
    for seed in seeds:
        for kind in ('flat','spin'):
            for variant in ('off','sensor'):
                while helpers.active_processes(PROBES):time.sleep(5)
                name=f'{label}_{kind}_{variant}_{seed}'
                path=REPORTS/(name+'.json')
                if path.exists():continue
                probe(ck,name,kind=kind,sensor=variant=='sensor',seed=seed,small=small,limit=limit)
            a=helpers.read(REPORTS/f'{label}_{kind}_off_{seed}.json')
            b=helpers.read(REPORTS/f'{label}_{kind}_sensor_{seed}.json')
            exact=all(a[k]==b[k] for k in ('reset_joint_pos_before_physics','reset_root_before_physics'))
            good=exact and gate(a,kind) and gate(b,kind)
            pairs.append(dict(seed=seed,kind=kind,same_checkpoint=a['checkpoint']==b['checkpoint'],
                same_initial_root_q=exact,baseline_gate=gate(a,kind),sensor_gate=gate(b,kind),pass_=bool(good)))
            passed &= good
    result=dict(pass_=bool(passed),pairs=pairs,checkpoint=base.checkpoint(ck),rate_limit=limit or rate.current_limit(),
        no_extra_ppo_for_probe=True,production_ppo_may_continue=small,real_robot_certified=False,old_window_gate_preserved=True)
    result['pass']=result.pop('pass_');base.atomic_json(REPORTS/(label+'_decision.json'),result)
    return passed


def restore_parent():
    if HELD:
        now=helpers.identity(HELD['pid'])
        if now and now['start_ticks']==HELD['start_ticks'] and now['state']=='T':os.kill(now['pid'],signal.SIGCONT)


def watchdog(owner_pid,owner_ticks,parent_pid,parent_ticks):
    while True:
        owner=helpers.identity(owner_pid)
        if not owner or owner['state']=='Z' or owner['start_ticks']!=owner_ticks:break
        time.sleep(5)
    if (REPORTS/'handover_completed.json').exists():return
    for item in helpers.active_processes(PROBES):
        if '--output' in item['argv'] and Path(item['argv'][item['argv'].index('--output')+1]).is_relative_to(REPORTS):
            os.kill(item['pid'],signal.SIGINT)
    now=helpers.identity(parent_pid)
    if now and now['start_ticks']==parent_ticks and now['state']=='T':os.kill(parent_pid,signal.SIGCONT)


def handover():
    global HELD
    assert not (REPORTS/'handover_completed.json').exists()
    while True:
        old=helpers.read(OLD/'status.json');parent=helpers.identity(old['supervisor_pid'])
        assert parent and parent['cwd']==str(OLD) and any(x.endswith('/supervise_spin_rate.py') for x in parent['argv'])
        if helpers.active_processes(PROBES):time.sleep(5);continue
        assert float(helpers.read(OLD/'isaac/mod4/env.json')['RM_SPIN_MAX_RAD_S'])==4.,'Old rate advanced: candidate must be re-reviewed'
        os.kill(parent['pid'],signal.SIGSTOP);HELD=parent
        own=helpers.identity(os.getpid())
        subprocess.Popen([base.PY,str(Path(__file__).resolve()),'--watchdog',str(os.getpid()),str(own['start_ticks']),str(parent['pid']),str(parent['start_ticks'])],cwd=ROOT,start_new_session=True)
        if helpers.active_processes(PROBES):restore_parent();HELD=None;time.sleep(5);continue
        trainers=base.trainers();tail=0.
        if trainers:
            assert len(trainers)==1
            trainer=helpers.identity(trainers[0]);assert trainer['cwd']==str(OLD)
            assert trainer['pid']==base.budget_state()['active_segment']['pid']
            folder=rate.trainer_run(OLD/'logs',trainer['pid']);stop=folder/'STOP_AFTER_SAVE'
            assert not stop.exists();stop.write_text('User-authorized sensor robustness trial: preserve complete policy/optimizer/std at save boundary.\n')
            status('waiting_complete_save',old_trainer=trainer,active_log=old['active_log'])
            until=time.time()+1200
            while True:
                now=helpers.identity(trainer['pid'])
                if not now or now['state']=='Z':break
                assert now['start_ticks']==trainer['start_ticks'] and time.time()<until
                time.sleep(.5)
            receipt=helpers.read(folder/'latest_complete.json');ck=Path(receipt['checkpoint'])
            assert receipt['pid']==trainer['pid']
            assert 'Full checkpoint saved; authorized budget or stop-file reached' in Path(old['active_log']).read_text(errors='replace')
            b=base.budget_state();segment=b['active_segment'];ended=time.time()
            assert segment['pid']==trainer['pid'];tail=max(0.,ended-segment['accounted_through_epoch'])
            b['charged_training_seconds']+=tail;b['remaining_training_seconds']=b['authorized_training_seconds']-b['charged_training_seconds']
            segment.update(ended_epoch=ended,accounted_through_epoch=ended,end_evidence='Complete save and graceful exit observed',observation_uncertainty_upper_s=.5)
            b.setdefault('completed_segments',[]).append(segment);b['active_segment']=None;base.atomic_json(CANONICAL,b)
        else:
            assert not base.budget_state().get('active_segment');ck=base.latest(OLD/'logs')
        info=base.checkpoint(ck);charged=base.budget_state()['charged_training_seconds']
        # Latest 4rad source must itself pass before adding another difficulty.
        assert paired(ck,'latest4rad_before_handover',seeds=(20261002,)), 'Latest source/sensor 4rad regression; restore existing supervisor'
        assert base.budget_state()['charged_training_seconds']==charged
        os.kill(parent['pid'],signal.SIGTERM);os.kill(parent['pid'],signal.SIGCONT);HELD=None
        until=time.time()+30
        while time.time()<until:
            now=helpers.identity(parent['pid'])
            if not now or now['state']=='Z':break
            time.sleep(.2)
        assert not base.trainers() and not helpers.active_processes(PROBES)
        helpers.acquire(CANONICAL.parent/'native_floor_supervisor.lock')
        base.update_budget(owner_root=str(ROOT))
        base.atomic_json(REPORTS/'handover_completed.json',dict(source_checkpoint=info,old_parent=parent,
            tail_charged_s=tail,canonical_budget=str(CANONICAL),budget_added=False,old_checkpoints_preserved=True,
            actual_rate_rad_s=4.,physical_reward_ppo_unchanged=True))
        old.update(stage='handed_over_sensor_trial',training_pid=None,supervisor_pid=None,handover_root=str(ROOT));base.atomic_json(OLD/'status.json',old)
        return ck


def open_ui():
    gui=os.environ.copy();old_tuis=helpers.active_processes(('/tui_spin_rate.py',))
    selected=[p for p in old_tuis if p['cwd']==str(OLD) or any(str(OLD)+'/isaac/mod4/tui_spin_rate.py'==x for x in p['argv'])]
    if selected:
        data=Path('/proc',str(selected[0]['pid']),'environ').read_bytes().split(b'\0')
        for item in data:
            if b'=' in item:
                k,v=item.split(b'=',1)
                if k.decode() in ('DISPLAY','XAUTHORITY','DBUS_SESSION_BUS_ADDRESS','XDG_RUNTIME_DIR'):
                    gui[k.decode()]=v.decode()
    result=subprocess.run(['gnome-terminal','--title=MOD4 Sensor DR Trial + Spin Rate','--','/usr/bin/python3',
        str(CODE/'tui_spin_rate.py'),'--interval','5'],cwd=ROOT,env=gui,capture_output=True,text=True,timeout=30)
    assert result.returncode==0,result.stderr
    until=time.time()+20
    while time.time()<until:
        current=[p for p in helpers.active_processes(('/tui_spin_rate.py',)) if str(CODE/'tui_spin_rate.py') in p['argv']]
        if current:
            for item in selected:
                now=helpers.identity(item['pid'])
                if now and now['start_ticks']==item['start_ticks']:os.kill(item['pid'],signal.SIGTERM)
            base.atomic_json(REPORTS/'SENSOR_UI_OPENED.json',dict(actual_process=current[0],local_file_refresh_s=5))
            return
        time.sleep(.5)
    raise RuntimeError('New TUI actual process not observed; training must not depend on UI success')


def fullscale(ck):
    assert not base.trainers() and not helpers.active_processes(PROBES)
    out=REPORTS/'sensor20k.json'
    p=base.spawn(['isaac/mod4/spin_rate_fullscale_probe.py','--headless','--checkpoint',str(ck),
        '--num_envs','20000','--steps','120','--max-rate','4.','--output',str(out)],out.with_suffix('.log'))
    r=base.wait_probe(p,out);ok,acceptance=base.accept_physics_smoke(r)
    base.atomic_json(REPORTS/'sensor20k_acceptance.json',acceptance)
    assert ok and r['mild_initial_parameters']['actual_parameters_pass'] and r['mild_final_parameters']['actual_parameters_pass']
    assert r['sensor_audit']['profile']=='sensor_v1' and r['sensor_audit']['nominal_lag_zero']


def preflight20k(ck):
    """Four full PPO updates, charged once and discarded; no second large trainer."""
    import re
    assert not base.trainers() and not helpers.active_processes(PROBES) and not base.budget_state().get('active_segment')
    log=ROOT/'train_sensor20k_preflight.log';assert not log.exists()
    p=base.spawn(['isaac/mod4/train_mod4_ppo.py','--headless','--num_envs','20000','--additional_iterations','4',
        '--steps_per_env','24','--save_interval','4','--learning_rate','.0001','--seed','20260928',
        '--run_name','sensor20k_preflight','--log_root',str(ROOT/'preflight20k_logs'),'--init_checkpoint',str(ck)],log)
    base.start_segment(p,'sensor20k_four_ppo',log);status('ppo_preflight20k',training_pid=p.pid,active_log=str(log))
    while p.poll() is None:base.account_segment();time.sleep(5)
    base.account_segment(finish=True);status(training_pid=None)
    assert p.returncode==0, 'Fullscale PPO failed; preserve logs/ledger'
    folder=rate.trainer_run(ROOT/'preflight20k_logs',p.pid);info=base.checkpoint(Path(helpers.read(folder/'latest_complete.json')['checkpoint']))
    times=[float(v) for v in re.findall(r'Iteration time:\s*([0-9.]+)s',log.read_text(errors='replace'))]
    assert len(times)==4 and all(x>0 for x in times)
    throughput=480000/(sum(times)/len(times))
    base.atomic_json(REPORTS/'SENSOR20K_PPO_RECEIPT.json',dict(pass_=True,iteration_time_s=times,
        env_policy_steps_per_second=throughput,discarded_weights=info,production_source=base.checkpoint(ck),
        charged_same_ledger=True,weights_discarded=True,not_controlled_baseline_ab=True))
    assert throughput>=23000, 'Sensor path throughput below 23k; retain original white_v1 and diagnose cost'


def fallback(source,reason):
    assert not base.trainers() and not base.budget_state().get('active_segment')
    profile('off');status('sensor_trial_rejected_restoring_white_v1',fallback_reason=reason)
    base.atomic_json(REPORTS/'SENSOR_FALLBACK.json',dict(source=base.checkpoint(source),reason=reason,all_trial_weights_preserved=True,budget_added=False))
    # Resume measured rate curriculum from exact preserved 4rad source and same ledger.
    base.atomic_json(REPORTS/'RATE_PRODUCTION_STARTED.json',dict(source=base.checkpoint(source),sensor_trial_rejected=True))
    chosen=training(source,'sensor_safe_fallback',duration=2700)
    continue_curriculum(chosen)
rate.fallback=fallback


def continue_curriculum(chosen):
    consecutive=0
    while True:
        label='sensor_rate'+str(rate.current_limit()).replace('.','p')+'_model'+str(base.checkpoint(chosen)['iteration_stored'])
        physical,skilled=rate.decision(chosen,label)
        assert physical,'Physical/flat regression: preserve checkpoint and stop for diagnosis, no blind reset'
        consecutive=consecutive+1 if skilled else 0
        remaining=base.budget_state()['remaining_training_seconds'];higher=rate.next_limit(rate.current_limit())
        if consecutive>=2 and higher is not None and remaining>3600:
            if rate.multiseed(chosen,label):
                previous=rate.current_limit();rate.set_limit(higher,'Sensor trial accepted, current yaw twice passed and nominal/DR multi-seed pairs passed')
                try:
                    short=probe(chosen,label+'_next_short',steps=300)
                    assert short['physical_smoke_pass'] and not short['nonfinite']
                    rate.fullscale(chosen,label+'_next');rate.ppo_preflight(chosen,'sensor_next_rate_preflight')
                except BaseException:
                    if base.trainers() or base.budget_state().get('active_segment'):raise
                    base.atomic_json(REPORTS/(label+'_promotion_rejected.json'),dict(error=traceback.format_exc(),checkpoint=str(chosen)))
                    rate.set_limit(previous,'Next yaw physical/PPO preflight rejected; preserve current validated rate')
                consecutive=0
        remaining=base.budget_state()['remaining_training_seconds']
        if remaining<=120:break
        chosen=training(chosen,'sensor_rate_continued',duration=min(7200,remaining))
        if base.budget_state()['remaining_training_seconds']<=120:break
    flat=probe(chosen,'final_sensor_flat',kind='flat')
    yaw=probe(chosen,'final_sensor_spin');nominal=probe(chosen,'final_sensor_nominal_spin',profile='nominal')
    status('finished',training_pid=None,final_checkpoint=base.checkpoint(chosen),final_evaluation=dict(flat=assess(flat),spin=spin.compact_spin(yaw),nominal_spin=spin.compact_spin(nominal)))


def main():
    import torch
    torch.set_num_threads(1);helpers.acquire(ROOT/'sensor_supervisor.lock');rate.verify_sources()
    assert not (REPORTS/'handover_completed.json').exists(),'Already handed over: reconcile before recovery'
    assert helpers.read(REPORTS/'sensor_readback.json')['pass']
    stable=Path(helpers.read(OLD/'reports/rate3p0_model14817_multiseed.json')['checkpoint']['path'])
    status('isolated_sensor_preflight',canonical_budget=str(CANONICAL),budget_seconds=180000,training_root_unchanged=str(OLD))
    if not paired(stable,'frozen3rad_sensor',small=True,limit=3.):
        status('sensor_preflight_rejected',outcome='Production unchanged; provisional sensor stress fails paired acceptance. Inspect failed groups before changing ranges.');return
    source=handover()
    try:
        fullscale(source);rate.ppo_preflight(source,'sensor128');preflight20k(source)
    except BaseException:
        if base.trainers() or base.budget_state().get('active_segment'):raise
        fallback(source,traceback.format_exc());return
    base.atomic_json(REPORTS/'SENSOR_PRODUCTION_STARTED.json',dict(source=base.checkpoint(source),rate_limit=4.,profile='sensor_v1',budget_added=False,preflight_weights_discarded=True))
    try:open_ui()
    except Exception:base.atomic_json(REPORTS/'SENSOR_UI_ATTENTION.json',dict(error=traceback.format_exc(),training_not_blocked=True))
    chosen=spin.training(source,'sensor_trial45',duration=2700)
    if not paired(chosen,'sensor_trial45_multiseed'):
        fallback(source,'45min trial paired flat/spin regression');return
    base.atomic_json(REPORTS/'SENSOR_TRIAL_ACCEPTED.json',dict(checkpoint=base.checkpoint(chosen),rate_limit=4.,frozen_two_seed_baseline_and_sensor_pass=True,real_robot_certified=False))
    base.atomic_json(REPORTS/'RATE_PRODUCTION_STARTED.json',dict(source=base.checkpoint(source),sensor_trial_accepted=True))
    # Keep the existing rate ladder, requiring two checks and nominal/DR pairs.
    # New sensors remain fixed; future COM/PD/payload expansion is separate.
    continue_curriculum(chosen)


if __name__=='__main__':
    if len(sys.argv)==6 and sys.argv[1]=='--watchdog':watchdog(*(int(x) for x in sys.argv[2:]))
    else:
        try:main()
        except BaseException:
            if not (REPORTS/'handover_completed.json').exists():
                rate.owned_probe_cleanup();restore_parent()
            status('attention_required',error=traceback.format_exc(),instructions='Inspect actual processes/ledger. Do not rerun one-shot, duplicate budget or trainer.')
            raise
