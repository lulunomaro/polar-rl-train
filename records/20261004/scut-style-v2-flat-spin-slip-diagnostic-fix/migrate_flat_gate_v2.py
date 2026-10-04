"""One guarded PID-bound save migration; no prior entry or settlement rerun."""
import argparse,fcntl,os,signal,subprocess,sys,time,traceback
from pathlib import Path
P=Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002')
C=Path('/home/egde/rl_candidates/MOD4_SPIN_ROLLING_REPAIR_20261004')
STAGE=Path(__file__).resolve().parent;R=C/'reports'
sys.path.insert(0,str(C))
import supervise_scut_style_continue as old
ctl=old.ctl;repair=old.repair;base=old.base;helpers=old.helpers;rate=old.rate;read=old.read
J=R/'SCUT_STYLE_V2_MIGRATION.json'
PREP=read(STAGE/'PREPARED.json')

def same(identity):
    a=helpers.identity(identity['pid'])
    return a if a and a['state']!='Z' and a['start_ticks']==identity['start_ticks'] and a['cwd']==identity['cwd'] and a['argv']==identity['argv'] else None

def journal(stage,**kw):
    x=read(J) if J.exists() else {}
    x.update(stage=stage,updated_epoch=time.time(),**kw);base.atomic_json(J,x)

def watchdog():
    while True:
        x=read(J)
        if x.get('stage') in ('completed','rolled_back_before_retirement'):return
        if time.time()-x['started_epoch']>600:
            if x.get('old_parent_retired'):
                base.status(stage='attention_required',error='Flat-gate v2 migration timed out after retirement. Preserve journal/full source/ledger; no duplicate settlement.')
            else:
                prior=x['old_parent']
                if same(prior):os.kill(prior['pid'],signal.SIGCONT)
                journal('rolled_back_before_retirement',watchdog_restored_prior_parent=True)
            return
        time.sleep(2)

def retire(identity):
    if same(identity):
        os.kill(identity['pid'],signal.SIGTERM)
        now=helpers.identity(identity['pid'])
        if now and now['start_ticks']==identity['start_ticks'] and now['state']=='T':os.kill(identity['pid'],signal.SIGCONT)
    deadline=time.monotonic()+20
    while same(identity):
        assert time.monotonic()<deadline,'Verified process did not retire'
        time.sleep(.1)

def migrate():
    assert not J.exists(),'One-shot already began; inspect journal instead of rerunning'
    for name,digest in PREP['files'].items():assert base.sha(STAGE/name)==digest,name
    status=read(P/'status.json');ctl.S=read(ctl.STATE_PATH);repair.verify()
    expected=PREP['expected_processes'];parent=expected['parent'];guard=expected['guardian'];trainer=expected['trainer']
    assert same(parent) and same(guard) and same(trainer)
    assert str(C/'supervise_scut_style_continue.py') in parent['argv']
    assert status['training_pid']==trainer['pid'] and status['supervisor_pid']==parent['pid']
    assert base.trainers()==[trainer['pid']] and not helpers.active_processes(ctl.PROBES)
    assert base.budget_state()['active_segment']['pid']==trainer['pid'] and ctl.S['active_training']['pid']==trainer['pid']
    assert rate.current_limit()==6. and ctl.S['mature']==PREP['last_paired_mature']
    run=rate.trainer_run(P/'logs',trainer['pid']);saved=read(run/'latest_complete.json')
    assert saved['pid']==trainer['pid'] and not (run/'STOP_AFTER_SAVE').exists()
    assert PREP['CPU_contracts']['pass_'] and PREP['existing_policy_review']['pass_']
    journal('validated_before_save',started_epoch=time.time(),old_parent=parent,old_guardian=guard,
            old_trainer=trainer,run=str(run),ledger_before=base.budget_state(),last_paired_mature=ctl.S['mature'],
            acceptance_version=PREP['acceptance_version'],old_parent_retired=False)
    with (STAGE/'migration_watchdog.log').open('x') as log:
        watch=subprocess.Popen([base.PY,str(Path(__file__).resolve()),'--watchdog'],cwd=C,
            stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    journal('save_requested',watchdog=helpers.identity(watch.pid))
    retired=False;locks=[]
    try:
        os.kill(parent['pid'],signal.SIGSTOP)
        deadline=time.monotonic()+5
        while True:
            paused=same(parent);assert paused,'Prior parent disappeared before pause acknowledgment'
            if paused['state']=='T':break
            assert time.monotonic()<deadline,'Prior parent pause acknowledgment timed out'
            time.sleep(.025)
        assert same(trainer) and base.trainers()==[trainer['pid']] and not helpers.active_processes(ctl.PROBES)
        began=time.time()
        (run/'STOP_AFTER_SAVE').write_text('User corrects slip-numeric-veto omission in flat regression: complete full checkpoint/save/exit for versioned gate migration.\n')
        while same(trainer):
            assert time.time()-began<500,'Complete save timeout; watchdog preserves prior parent'
            time.sleep(.25)
        ended=time.time()
        exited=helpers.identity(trainer['pid']);exit_code=None
        if exited and exited['state']=='Z':
            rest=Path(f'/proc/{trainer["pid"]}/stat').read_text().rsplit(')',1)[1].split()
            exit_code=int(rest[49]);assert exit_code==0,'Trainer did not exit normally'
        saved=read(run/'latest_complete.json');ck=Path(saved['checkpoint'])
        assert saved['pid']==trainer['pid'] and ck.parent==run and saved['saved_at']>=began
        source=base.checkpoint(ck);assert source['finite_tensors']==68
        text=Path(status['active_log']).read_text(errors='replace')
        assert 'Full checkpoint saved; authorized budget or stop-file reached' in text and 'Traceback (most recent call last)' not in text
        journal('complete_saved_pending_retirement',complete_checkpoint=source,latest_complete=saved,
                ended_epoch=ended,observation_uncertainty_upper_s=.25,trainer_exit_code=exit_code)
        retire(parent);retired=True
        journal('old_parent_retired',old_parent_retired=True)
        retire(guard)
        # Wait for real flock release. Do not remove lock files or bypass owners.
        for path in (P/'autonomy_controller.lock',ctl.CANONICAL.parent/'native_floor_supervisor.lock'):
            f=path.open('a+');deadline=time.monotonic()+30
            while True:
                try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(f);break
                except BlockingIOError:
                    assert time.monotonic()<deadline,'Real lock remains owned; explicit recovery required'
                    time.sleep(.1)
        assert not base.trainers() and not helpers.active_processes(ctl.PROBES)
        budget=base.budget_state();assert budget['active_segment']['pid']==trainer['pid']
        from autonomy_policy import settle_segment
        tail=settle_segment(budget,trainer['pid'],ended)
        budget['completed_segments'][-1].update(end_reason='scut_style_v2_flat_gate_save_boundary',
            observation_uncertainty_upper_s=.25,end_evidence='Exact PID exited after atomic full save and graceful log',trainer_exit_code=exit_code)
        base.atomic_json(ctl.CANONICAL,budget)
        journal('settled_once',tail_charged_s=tail,charged_after=budget['charged_training_seconds'],remaining_after=budget['remaining_training_seconds'])
        ctl.S=read(ctl.STATE_PATH);assert ctl.S['active_training']['pid']==trainer['pid']
        ctl.S['active_training']=None;ctl.S['chosen_checkpoint']=str(ck);ctl.persist()
        freeze=read(R/'SOURCE_FREEZE.json');original=dict(freeze['sha256'])
        base.atomic_json(R/'SOURCE_FREEZE_BEFORE_SCUT_STYLE_V2.json',freeze)
        for name,target in {'scut_style_gate_v2.py':C/'isaac/mod4/scut_style_gate_v2.py',
                            'supervise_scut_style_continue_v2.py':C/'supervise_scut_style_continue_v2.py'}.items():
            assert not target.exists();target.write_bytes((STAGE/name).read_bytes())
            freeze['sha256'][target.relative_to(C).as_posix()]=base.sha(target)
        freeze.update(scut_style_acceptance_version=PREP['acceptance_version'],flat_and_spin_slip_diagnostic=True,
                      all_prior_sources_unchanged=True)
        base.atomic_json(R/'SOURCE_FREEZE.json',freeze)
        assert all(base.sha(C/name)==h for name,h in original.items());repair.verify()
        base.atomic_json(R/'SCUT_STYLE_V2_PREPARED.json',PREP)
        hand=dict(stage='completed',epoch=time.time(),complete_checkpoint=source,latest_complete=saved,
            last_paired_mature=ctl.S['mature'],old_parent=parent,old_guardian=guard,old_trainer=trainer,
            old_parent_future_launches_disabled=True,acceptance_version=PREP['acceptance_version'],
            tail_charged_s=tail,trainer_exit_code=exit_code,observation_uncertainty_upper_s=.25,budget=base.budget_state(),
            new_reward_physics_PPO_DR_hardware_changes=False,source_count_before=len(original),source_count_after=len(freeze['sha256']))
        base.atomic_json(R/'SCUT_STYLE_V2_HANDOVER.json',hand)
        old_state=read(old.J);old_state.update(superseded_by=str(R/'SCUT_STYLE_V2_STATE.json'),superseded_epoch=time.time())
        base.atomic_json(old.J,old_state)
        base.status(stage='scut_style_v2_saved_pending_assessment',supervisor_pid=None,training_pid=None,
                    evaluation_pid=None,validation_pid=None,latest_checkpoint=str(ck),acceptance_version=PREP['acceptance_version'])
        for f in locks:f.close()
        locks=[]
        with (C/'supervisor_scut_style_continue_v2.log').open('x') as log:
            worker=subprocess.Popen([base.PY,str(C/'supervise_scut_style_continue_v2.py')],cwd=C,
                stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        launch=helpers.identity(worker.pid);deadline=time.monotonic()+5
        while not launch:
            assert time.monotonic()<deadline,'New supervisor identity unavailable'
            time.sleep(.025);launch=helpers.identity(worker.pid)
        launch.update(epoch=time.time(),acceptance_version=PREP['acceptance_version'],source=source)
        base.atomic_json(R/'SCUT_STYLE_V2_LAUNCHED.json',launch)
        journal('completed',launch=launch)
    except BaseException:
        journal('attention_required',error=traceback.format_exc(),old_parent_retired=retired)
        if not retired and same(parent):os.kill(parent['pid'],signal.SIGCONT)
        else:base.status(stage='attention_required',error=traceback.format_exc(),instructions='Inspect v2 journal and exact saved source/ledger; no repeat migration or settlement')
        raise
    finally:
        for f in locks:f.close()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--watchdog',action='store_true');args=p.parse_args()
    __import__('torch').set_num_threads(1);base.STATE.update(read(P/'status.json'))
    watchdog() if args.watchdog else migrate()
