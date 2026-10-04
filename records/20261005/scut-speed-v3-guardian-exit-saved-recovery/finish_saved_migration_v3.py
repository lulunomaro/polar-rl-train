"""Unique recovery after verified save/retirement, before any settlement/install."""
import fcntl,os,subprocess,time,traceback
from pathlib import Path
import migrate_speed_gate_v3 as m
D=m.D;C=m.C;P=m.P;R=m.R;base=m.base;ctl=m.ctl;t=m.t;read=m.read
REC=R/'SCUT_SPEED_V3_SAVED_RECOVERY.json'

def progress(stage,**kw):
    x=read(REC) if REC.exists() else {}
    x.update(stage=stage,epoch=time.time(),**kw);base.atomic_json(REC,x)

def main():
    assert not REC.exists(),'Saved recovery already began; inspect receipt, never repeat'
    j=read(m.J);prep=read(D/'PREPARED.json')
    assert j['stage']=='attention_required' and j['old_parent_retired'] and 'PID identity changed' in j['error']
    assert 'checkpoint' in j and 'ended_epoch' in j and 'tail_charged_s' not in j
    assert not (R/'SCUT_SPEED_V3_HANDOVER.json').exists() and not (R/'SCUT_SPEED_V3_STATE.json').exists()
    for name,digest in prep['files'].items():assert base.sha(D/name)==digest
    for name in ('old_parent','old_guardian','old_trainer'):
        e=j[name];now=m.identity(e['pid'])
        assert not now or now['start_ticks']!=e['start_ticks'] or now['state']=='Z','Bound process remains live'
    assert not base.trainers() and not t.helpers.active_processes(ctl.PROBES)
    run=Path(j['run']);saved=read(run/'latest_complete.json');ck=Path(saved['checkpoint'])
    assert saved==j['latest_complete'] and saved['pid']==j['old_trainer']['pid'] and ck.parent==run
    source=base.checkpoint(ck);assert source==j['checkpoint'] and source['finite_tensors']==68
    text=Path(read(P/'status.json')['active_log']).read_text(errors='replace')
    assert 'Full checkpoint saved; authorized budget or stop-file reached' in text and 'Traceback (most recent call last)' not in text
    assert j['exit_evidence'] is None or j['exit_evidence']['exit_code_encoded']==0
    t.repair.verify();locks=[]
    progress('validated_saved_retired',checkpoint=source,original_error_retained=j['error'],no_child_or_active_simulator=True)
    try:
        for path in (P/'autonomy_controller.lock',ctl.CANONICAL.parent/'native_floor_supervisor.lock'):
            f=path.open('a+');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(f)
        budget=base.budget_state();assert budget['active_segment']['pid']==j['old_trainer']['pid']
        assert budget['charged_training_seconds']==j['ledger_before']['charged_training_seconds']
        assert budget['active_segment']==j['ledger_before']['active_segment']
        assert budget['budget_extensions']==j['ledger_before']['budget_extensions']
        from budget_authority import validate_budget
        assert validate_budget(budget)==324000
        from autonomy_policy import settle_segment
        tail=settle_segment(budget,j['old_trainer']['pid'],j['ended_epoch'])
        budget['completed_segments'][-1].update(end_reason='scut_speed_v3_full_save_gate_only_migration',observation_uncertainty_upper_s=.25,end_evidence=saved,exit_evidence=j['exit_evidence'])
        assert validate_budget(budget)==324000
        base.atomic_json(ctl.CANONICAL,budget)
        progress('settled_once',tail_charged_s=tail,charged_after=budget['charged_training_seconds'],remaining_after=budget['remaining_training_seconds'])
        ctl.S=read(ctl.STATE_PATH);assert ctl.S['active_training']['pid']==j['old_trainer']['pid']
        ctl.S['active_training']=None;ctl.S['chosen_checkpoint']=str(ck);ctl.persist()
        freeze=read(R/'SOURCE_FREEZE.json');original=dict(freeze['sha256'])
        assert original==prep['source_freeze'] and len(original)==137
        assert not (R/'SOURCE_FREEZE_BEFORE_SCUT_SPEED_V3.json').exists()
        base.atomic_json(R/'SOURCE_FREEZE_BEFORE_SCUT_SPEED_V3.json',freeze)
        for name,target in {'scut_style_gate_v3.py':C/'isaac/mod4/scut_style_gate_v3.py','supervise_scut_speed_continue_v3.py':C/'supervise_scut_speed_continue_v3.py'}.items():
            assert not target.exists();target.write_bytes((D/name).read_bytes());freeze['sha256'][target.relative_to(C).as_posix()]=base.sha(target)
        freeze.update(scut_style_acceptance_version=prep['acceptance_version'],spin_mean_xy_numeric_veto_removed=True,all_prior_sources_unchanged=True)
        base.atomic_json(R/'SOURCE_FREEZE.json',freeze)
        assert all(base.sha(C/name)==digest for name,digest in original.items());t.repair.verify()
        base.atomic_json(R/'SCUT_SPEED_V3_PREPARED.json',prep)
        hand=dict(stage='completed',acceptance_version=prep['acceptance_version'],checkpoint=source,latest_complete=saved,last_paired_mature=ctl.S['mature'],
                  prior_counts=dict(consecutive=j['prior_state']['consecutive'],failed_blocks=j['prior_state']['failed_blocks']),
                  old_parent=j['old_parent'],old_trainer=j['old_trainer'],old_guardian=j['old_guardian'],old_parent_future_launches_disabled=True,
                  budget_authorized=324000,budget=base.budget_state(),tail_charged_s=tail,observation_uncertainty_upper_s=.25,
                  reward_DR_hardware_physics_PPO_changes=False,source_count_before=137,source_count_after=len(freeze['sha256']),
                  original_migration_error=j['error'],saved_recovery=str(REC),no_migration_rerun=True)
        base.atomic_json(R/'SCUT_SPEED_V3_HANDOVER.json',hand)
        old=read(t.J);old.update(superseded_by=str(R/'SCUT_SPEED_V3_STATE.json'),superseded_epoch=time.time());base.atomic_json(t.J,old)
        base.status(stage='scut_speed_v3_saved_pending_assessment',supervisor_pid=None,training_pid=None,evaluation_pid=None,validation_pid=None,latest_checkpoint=str(ck),acceptance_version=prep['acceptance_version'],error=None)
        for f in locks:f.close()
        locks=[]
        with (C/'supervisor_scut_speed_v3.log').open('x') as log:
            worker=subprocess.Popen([base.PY,str(C/'supervise_scut_speed_continue_v3.py')],cwd=P,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        deadline=time.monotonic()+5;launch=m.identity(worker.pid)
        while not launch:
            assert time.monotonic()<deadline;time.sleep(.025);launch=m.identity(worker.pid)
        launch.update(epoch=time.time(),source=source,acceptance_version=prep['acceptance_version'])
        base.atomic_json(R/'SCUT_SPEED_V3_LAUNCHED.json',launch)
        progress('completed',launch=launch,checkpoint=source,gate_sha256=base.sha(C/'isaac/mod4/scut_style_gate_v3.py'),controller_sha256=base.sha(C/'supervise_scut_speed_continue_v3.py'))
        m.journal('completed',launch=launch,tail_charged_s=tail,completed_by_saved_recovery=str(REC),original_error_retained=True)
    except BaseException:
        progress('attention_required',error=traceback.format_exc())
        base.status(stage='attention_required',error=traceback.format_exc(),instructions='Preserve saved recovery journal and actual ledger; no repeated settlement/entry')
        raise
    finally:
        for f in locks:f.close()

if __name__=='__main__':
    __import__('torch').set_num_threads(1);base.STATE.update(read(P/'status.json'));main()
