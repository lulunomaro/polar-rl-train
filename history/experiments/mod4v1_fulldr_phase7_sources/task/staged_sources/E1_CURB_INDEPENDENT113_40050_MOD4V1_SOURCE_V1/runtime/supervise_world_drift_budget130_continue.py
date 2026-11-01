"""One saved-boundary continuation after explicit fifth budget extension.

All completed reward/PPO preflights stay completed. Start with the pending
assessment of the original full 45-minute formal segment, never repeat it.
"""
import argparse, os, subprocess, traceback
from pathlib import Path
import supervise_world_drift as n
w=n.w;ctl=n.ctl;base=n.base;helpers=n.helpers;D=w.D;R=w.R;P=w.P
ID='USER_ADD40H_20261005_5TH'
original_status=w.status
def status(stage=None,**kw):
    kw.setdefault('autonomy_version','world_directional_spin_scut_v4_budget_dynamic_drift_v1')
    kw.setdefault('controller_version','world_drift_budget_dynamic_saved_continue')
    original_status(stage,**kw)
w.status=ctl.status=status

def controller():
    marker=R/'BUDGET_CONTINUATION_STARTED.json'
    assert not marker.exists(),'Already started: inspect actual children and receipts'
    ctl.S=w.read(ctl.STATE_PATH);base.STATE.update(w.read(P/'status.json'))
    ctl.idle();w.verify()
    helpers.acquire(P/'autonomy_controller.lock')
    helpers.acquire(ctl.CANONICAL.parent/'native_floor_supervisor.lock')
    hand=w.read(R/(ID+'_HANDOVER.json'))
    b=base.budget_state()
    matches=[e for e in b['budget_extensions'] if e['extension_id']==ID]
    assert len(matches)==1 and matches[0]['additional_training_seconds']==144000
    for person in hand['retired']:
        actual=helpers.identity(person['pid'])
        assert not actual or actual.get('state')=='Z' or actual['start_ticks']!=person['start_ticks']
    ck=Path(hand['checkpoint']['path'])
    actual=base.checkpoint(ck)
    assert all(actual[k]==hand['checkpoint'][k] for k in ('path','sha256','iteration_stored','finite_tensors'))
    assert hand['natural_original_deadline_completed'] and hand['current_segment_effective_seconds']>=2700
    last=Path(hand['rollback_source']['path'])
    base.checkpoint(last)
    base.atomic_json(marker,dict(parent=helpers.identity(os.getpid()),checkpoint=actual,
        extension_id=ID,reused_preflights=True,pending_original_45min_assessment=True))
    with (D/'guardian_world_drift_budget_dynamic.log').open('x') as log:
        g=subprocess.Popen([base.PY,str(D/'supervise_world_drift_budget130_continue.py'),
            '--guardian',str(os.getpid()),str(helpers.identity(os.getpid())['start_ticks'])],
            cwd=P,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    base.atomic_json(R/'BUDGET_GUARDIAN_STARTED.json',helpers.identity(g.pid))
    try:
        w.phase('saved_world_drift_assessment',checkpoint=actual,goal_m_s=.5,
                completed_effective_exposure_s=hand['current_segment_effective_seconds'],
                owner=helpers.identity(os.getpid()),budget_extension_id=ID)
        w.regression(ck);worlds,path=w.paired(ck);last=ck
        w.phase('world_drift_paired_learning_accepted',checkpoint=base.checkpoint(ck),paired_path=path,
                target_confirmed=all(x['pass_'] for x in worlds),learning_admission_only=True,
                last_validated_source=base.checkpoint(last))
        if all(x['pass_'] for x in worlds):
            w.finish(ck,'Actual .5 world-directed progress and retained skills verified after isolated drift reward',worlds)
            return
        duration=min(7200,ctl.remaining())
        while ctl.remaining() > 120:
            w.phase('bounded_world_drift_learning', goal_m_s=0.5, source=base.checkpoint(ck), duration_s=min(duration, ctl.remaining()))
            ck = ctl.training(ck, 'world_drift_learning', duration=min(duration, ctl.remaining()))
            w.regression(ck)
            worlds, path = w.paired(ck)
            last = ck
            w.phase('world_drift_paired_learning_accepted', checkpoint=base.checkpoint(ck), paired_path=path, target_confirmed=all((x['pass_'] for x in worlds)), learning_admission_only=True, last_validated_source=base.checkpoint(last))
            if all((x['pass_'] for x in worlds)):
                w.finish(ck, 'Actual .5 world-directed progress and retained skills verified after isolated drift reward', worlds)
                return
            duration = min(7200, ctl.remaining())

        w.finish(ck,'Remaining effective budget below safe block threshold; target not assumed')
    except BaseException:
        w.hold(last,traceback.format_exc());raise

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--guardian',nargs=2);a=p.parse_args()
    if a.guardian:w.guardian(int(a.guardian[0]),a.guardian[1])
    else:controller()
