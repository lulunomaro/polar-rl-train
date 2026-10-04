"""One guarded complete-save migration; never restart a prior one-shot entry."""
import argparse,fcntl,os,signal,subprocess,sys,time,traceback
from pathlib import Path
P=Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002')
C=Path('/home/egde/rl_candidates/MOD4_SPIN_ROLLING_REPAIR_20261004')
STAGE=Path(__file__).resolve().parent;R=C/'reports'
sys.path.insert(0,str(C))
import supervise_contact_gate_continue as old
ctl=old.ctl;repair=old.repair;base=old.base;helpers=old.helpers;rate=old.rate;read=old.read
J=R/'SCUT_STYLE_MIGRATION_RETRY1.json'
EXPECTED_PARENT=(4145334,25108417)
EXPECTED_GUARD=(4145375,25108483)
EXPECTED_TRAINER=(4158388,25453090)

def same(pid,ticks):
    a=helpers.identity(pid)
    return a if a and a['state']!='Z' and a['start_ticks']==ticks else None

def journal(stage,**kw):
    x=read(J) if J.exists() else {}
    x.update(stage=stage,updated_epoch=time.time(),**kw);base.atomic_json(J,x)

def watchdog():
    # Restore only the verified paused original parent before its retirement.
    # Never starts another trainer or settles a ledger.
    started=time.time()
    while time.time()-started<900:
        x=read(J) if J.exists() else {}
        if x.get('stage') in ('completed','rolled_back_before_retirement'):return
        if time.time()-x.get('started_epoch',started)>600:
            if x.get('old_parent_retired'):
                base.status(stage='attention_required',error='SCUT-style migration guard timeout after retirement; inspect journal and exact saved source, never duplicate settlement')
            elif same(*EXPECTED_PARENT):
                os.kill(EXPECTED_PARENT[0],signal.SIGCONT)
                journal('rolled_back_before_retirement',watchdog_restored_prior_parent=True)
            return
        time.sleep(2)

def migrate():
    assert not J.exists(),'One-shot migration already began; inspect journal'
    status=read(P/'status.json');ctl.S=read(ctl.STATE_PATH);repair.verify()
    parent=same(*EXPECTED_PARENT);trainer=same(*EXPECTED_TRAINER);guard=same(*EXPECTED_GUARD)
    assert parent and guard and trainer
    assert parent['cwd']==str(C) and str(C/'supervise_contact_gate_continue.py') in parent['argv']
    assert trainer['cwd']==str(P) and str(C/'isaac/mod4/train_mod4_ppo.py') in trainer['argv']
    assert status['training_pid']==trainer['pid'] and status['supervisor_pid']==parent['pid']
    assert base.trainers()==[trainer['pid']] and not helpers.active_processes(ctl.PROBES)
    assert base.budget_state()['active_segment']['pid']==trainer['pid']
    active=ctl.S['active_training'];assert active['pid']==trainer['pid']
    run=rate.trainer_run(P/'logs',trainer['pid']);saved=read(run/'latest_complete.json')
    assert saved['pid']==trainer['pid'] and not (run/'STOP_AFTER_SAVE').exists()
    prep=read(STAGE/'PREPARED.json')
    for name,h in prep['files'].items():assert base.sha(STAGE/name)==h,name
    journal('validated_before_save',started_epoch=time.time(),old_parent=parent,
            old_trainer=trainer,old_guardian=guard,run=str(run),ledger_before=base.budget_state(),
            last_paired_mature=ctl.S['mature'],acceptance_version=prep['acceptance_version'])
    with (STAGE/'migration_watchdog_retry1.log').open('x') as log:
        watch=subprocess.Popen([base.PY,str(Path(__file__).resolve()),'--watchdog'],cwd=C,
                stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    journal('save_requested',watchdog=helpers.identity(watch.pid))
    retired=False;locks=[]
    try:
        os.kill(parent['pid'],signal.SIGSTOP)
        pause_requested=time.monotonic()
        while True:
            paused=same(*EXPECTED_PARENT)
            assert paused,'Verified parent disappeared during pause handshake'
            if paused['state']=='T':break
            assert time.monotonic()-pause_requested<5,'Parent did not acknowledge SIGSTOP'
            time.sleep(.025)
        assert not helpers.active_processes(ctl.PROBES)
        assert same(*EXPECTED_TRAINER) and base.trainers()==[trainer['pid']]
        (run/'STOP_AFTER_SAVE').write_text('User-authorized SCUT-inspired slip-diagnostic qualification migration; complete full atomic save and exit.\n')
        began=time.time()
        while same(*EXPECTED_TRAINER):
            assert time.time()-began<500,'Complete-save boundary timeout; watchdog protects prior parent'
            time.sleep(.25)
        ended=time.time()
        saved=read(run/'latest_complete.json');ck=Path(saved['checkpoint'])
        assert saved['pid']==trainer['pid'] and ck.parent==run and saved['saved_at']>=began
        source=base.checkpoint(ck);assert source['finite_tensors']==68
        text=Path(status['active_log']).read_text(errors='replace')
        assert 'Full checkpoint saved; authorized budget or stop-file reached' in text
        assert 'Traceback (most recent call last)' not in text
        journal('complete_saved_pending_retirement',complete_checkpoint=source,
                latest_complete=saved,ended_epoch=ended,observation_uncertainty_upper_s=.25)
        os.kill(parent['pid'],signal.SIGTERM);os.kill(parent['pid'],signal.SIGCONT)
        for _ in range(100):
            if not same(*EXPECTED_PARENT):break
            time.sleep(.1)
        assert not same(*EXPECTED_PARENT);retired=True
        if same(*EXPECTED_GUARD):os.kill(guard['pid'],signal.SIGTERM)
        journal('old_parent_retired',old_parent_retired=True)
        for path in (P/'autonomy_controller.lock',ctl.CANONICAL.parent/'native_floor_supervisor.lock'):
            f=path.open('a+');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(f)
        assert not base.trainers() and not helpers.active_processes(ctl.PROBES)
        b=base.budget_state();assert b['active_segment']['pid']==trainer['pid']
        from autonomy_policy import settle_segment
        before=b.copy();tail=settle_segment(b,trainer['pid'],ended)
        b['completed_segments'][-1].update(end_reason='scut_style_save_boundary_migration',
            observation_uncertainty_upper_s=.25,end_evidence='Exact process exited after atomic latest_complete and graceful-save log')
        base.atomic_json(ctl.CANONICAL,b)
        journal('settled_once',tail_charged_s=tail,charged_after=b['charged_training_seconds'],
                remaining_after=b['remaining_training_seconds'])
        ctl.S=read(ctl.STATE_PATH);assert ctl.S['active_training']['pid']==trainer['pid']
        ctl.S['active_training']=None;ctl.S['chosen_checkpoint']=str(ck);ctl.persist()
        freeze=read(R/'SOURCE_FREEZE.json');original=dict(freeze['sha256'])
        base.atomic_json(R/'SOURCE_FREEZE_BEFORE_SCUT_STYLE.json',freeze)
        targets={'scut_style_gate.py':C/'isaac/mod4/scut_style_gate.py',
                 'supervise_scut_style_continue.py':C/'supervise_scut_style_continue.py'}
        for name,path in targets.items():
            assert not path.exists();path.write_bytes((STAGE/name).read_bytes())
            freeze['sha256'][path.relative_to(C).as_posix()]=base.sha(path)
        freeze.update(scut_style_acceptance_version=prep['acceptance_version'],
                      slip_numeric_veto_removed=True,all_prior_sources_unchanged=True)
        base.atomic_json(R/'SOURCE_FREEZE.json',freeze)
        assert all(base.sha(C/name)==h for name,h in original.items())
        repair.verify();ledger_after_install=ctl.CANONICAL.read_bytes()
        base.atomic_json(R/'SCUT_STYLE_PREPARED.json',prep)
        hand=dict(stage='completed',epoch=time.time(),complete_checkpoint=source,
                  latest_complete=saved,last_paired_mature=ctl.S['mature'],
                  old_parent=parent,old_trainer=trainer,old_guardian=guard,
                  old_parent_future_launches_disabled=True,tail_charged_s=tail,
                  observation_uncertainty_upper_s=.25,acceptance_version=prep['acceptance_version'],
                  budget=base.budget_state(),new_reward_physics_PPO_DR_hardware_changes=False,
                  source_count_before=len(original),source_count_after=len(freeze['sha256']))
        base.atomic_json(R/'SCUT_STYLE_HANDOVER.json',hand)
        old_state=read(old.J);old_state.update(superseded_by=str(R/'SCUT_STYLE_STATE.json'),
                                               superseded_epoch=time.time())
        base.atomic_json(old.J,old_state)
        base.status(stage='scut_style_saved_pending_assessment',supervisor_pid=None,
                    training_pid=None,evaluation_pid=None,validation_pid=None,latest_checkpoint=str(ck),
                    acceptance_version=prep['acceptance_version'])
        assert ctl.CANONICAL.read_bytes()==ledger_after_install
        # Release both locks BEFORE starting a nonblocking-lock controller.
        for f in locks:f.close()
        locks=[]
        with (C/'supervisor_scut_style_continue.log').open('x') as log:
            worker=subprocess.Popen([base.PY,str(C/'supervise_scut_style_continue.py')],cwd=C,
                stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        launch=helpers.identity(worker.pid)
        assert launch and launch['cwd']==str(C)
        launch.update(epoch=time.time(),acceptance_version=prep['acceptance_version'],source=source)
        base.atomic_json(R/'SCUT_STYLE_LAUNCHED.json',launch)
        journal('completed',launch=launch)
    except BaseException:
        journal('attention_required',error=traceback.format_exc(),old_parent_retired=retired)
        if not retired and same(*EXPECTED_PARENT):os.kill(parent['pid'],signal.SIGCONT)
        else:base.status(stage='attention_required',error=traceback.format_exc(),
                         instructions='Read SCUT migration journal, exact source and ledger; no repeated handover or settlement')
        raise
    finally:
        for f in locks:f.close()

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--watchdog',action='store_true');args=parser.parse_args()
    __import__('torch').set_num_threads(1)
    base.STATE.update(read(P/'status.json'))
    if args.watchdog:watchdog()
    else:migrate()
