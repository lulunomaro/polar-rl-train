"""Sequential saved-boundary continuation; no second trainer or repeated preflight.

Strict target confirmation is sufficient for automatic closeout, not required
for later human/agent practical closeout. Non-perfect results get bounded
optimization rather than an indefinite percentage graduation loop.
"""
import argparse,json,os,time,subprocess,traceback
from pathlib import Path
import supervise_retention_train as c
U=Path('/home/egde/rl_candidates/MOD4_ROUGH_RETENTION_PRECISION_REVIEW_20261006')
ROOT=c.H;REPORTS=c.R;ENTRY=Path(__file__).resolve()
c.ENTRY=ENTRY;c.w.STATE=REPORTS/'RETENTION_AUTO_PROGRESS_STATE.json'
def old_exited():
    for name in ('PRECISION_LAUNCHED.json','RETENTION_GUARDIAN_STARTED.json'):
        path=U/'reports'/name
        if not path.exists():return False
        saved=c.w.read(path);actual=c.helpers.identity(saved['pid'])
        if actual and actual['state']!='Z' and actual['start_ticks']==saved['start_ticks']:return False
    return True
def diagnostic(checkpoint,paired_path,mixed_path):
    pairs=c.w.read(Path(paired_path));mixed=c.w.read(Path(mixed_path))
    assert pairs['checkpoint']['sha256']==c.base.sha(checkpoint)==mixed['checkpoint_sha256'] and pairs['pass_'] and mixed['pass_']
    anchor=c.w.read(c.F/'reports/PHYSICAL_DR_STAGE1_REVIEW_READY.json')
    anchor_pairs=c.w.read(Path(anchor['paired_path']))
    current=[];reference=[];pure=[]
    for collection,output in ((pairs,current),(anchor_pairs,reference)):
        for row in collection['rows']:
            if row['kind']=='flat':
                raw=c.w.read(Path(row['report_path']))
                group=next(g for g in raw['groups'] if g['profile']=='constant' and abs(g['command_vx']-1.5)<1e-6)
                output.append(dict(seed=row['seed'],profile=row['profile'],mean_velocity_error=group['vel_error'],actual_signed_velocity=group['speed']))
    assert len(current)==len(reference)==6
    flat_changes=[dict(current=a,reference=b,error_change=a['mean_velocity_error']-b['mean_velocity_error']) for a,b in zip(current,reference)]
    for row in pairs['rows']:
        if row['kind']=='spin':
            raw=c.w.read(Path(row['report_path']))
            for group in raw['groups']:
                if group['profile']=='spin' and abs(abs(group['wz'])-4*__import__('math').pi)<1e-4:
                    vals=[v for v,g in zip(raw['per_environment']['yaw_rate'],raw['group_ids']) if g==group['group_id']]
                    pure.extend(abs(v-group['wz'])<=.2 for v in vals)
    # This explicitly diagnoses the earlier systematic +1.5 loss. It is not a
    # simulation/data admission veto, nor a new completion percentage rule.
    systematic_straight_loss=all(x['error_change']>.05 for x in flat_changes)
    correct_rough=True
    for row in mixed['rough_progress_segments']:
        for segment in row['valid_segments_before_each_reset']:
            correct_rough &= segment['along_m_s']*row['requested_body_vx']>0
    strict=bool(pairs['world_progress_05_confirmed'])
    sufficient=strict and pure and all(pure) and correct_rough and not systematic_straight_loss
    return dict(strict_world_confirmed=strict,strict_confirmation_sufficient_not_required_for_practical_progress=True,
        pure_signed_yaw_fact_pass=bool(pure) and all(pure),pure_samples=len(pure),rough_valid_segment_signs_correct=bool(correct_rough),
        flat_changes=flat_changes,systematic_straight_regression_detected=systematic_straight_loss,
        auto_closeout_sufficient=bool(sufficient),world_summary=pairs['world_summary'],finite_quality_no_data_veto=True,
        nonperfect_results_allow_later_agent_practical_closeout=True)
def controller():
    assert not (REPORTS/'AUTO_PROGRESS_STARTED.json').exists(),'Never rerun dispatcher'
    owner=c.helpers.identity(os.getpid());c.base.atomic_json(REPORTS/'AUTO_PROGRESS_STARTED.json',dict(owner=owner,scope='Wait current save/18 regressions; bounded continuation; no active trainer modification'))
    # Local files only. Current parent retains launch and ledger authority until
    # its planned full-save/regression exit; no locks/GPU/budget mutation here.
    while True:
        phase_path=U/'reports/RETENTION_PRECISION_STATE.json'
        state=c.w.read(phase_path) if phase_path.exists() else {}
        if state.get('phase') in ('repair_hold','attention_required_active_child_preserved'):
            c.base.atomic_json(REPORTS/'AUTO_PROGRESS_HOLD.json',dict(prior_state=state,reason='Actual prior failure; no automatic rerun'));return
        if (U/'reports/RETENTION_REVIEW_READY.json').exists() and old_exited():break
        time.sleep(15)
    c.helpers.acquire(c.P/'autonomy_controller.lock');c.helpers.acquire(c.ctl.CANONICAL.parent/'native_floor_supervisor.lock')
    c.ctl.S=c.w.read(c.ctl.STATE_PATH);c.base.STATE.update(c.w.read(c.P/'status.json'));c.ctl.idle();c.verify()
    for n,h in c.w.read(U/'reports/SOURCE_FREEZE.json')['sha256'].items():assert c.base.sha(U/n)==h
    prior=c.w.read(U/'reports/RETENTION_REVIEW_READY.json');source=Path(prior['checkpoint']['path'])
    info=c.base.checkpoint(source);assert info['finite_tensors']==68 and info['sha256']==prior['checkpoint']['sha256']
    assert c.w.read(U/'reports/RETENTION_COMPLETE_PREFLIGHT_PASSED.json')['pass_']
    c.ctl.S.update(profile='white_v3',chosen_checkpoint=str(source),active_training=None);c.ctl.persist()
    with (ROOT/'guardian_auto_progress.log').open('x') as log:
        guardian=subprocess.Popen([c.base.PY,str(ENTRY),'--guardian',str(os.getpid()),str(owner['start_ticks'])],cwd=c.P,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    c.base.atomic_json(REPORTS/'AUTO_PROGRESS_GUARDIAN_STARTED.json',c.helpers.identity(guardian.pid))
    last=source;review=prior;charged_start=c.base.budget_state()['charged_training_seconds'];cycles=0
    try:
        while True:
            decision=diagnostic(last,review['old_skill_paired_path'],review['mixed_assessment'])
            c.base.atomic_json(REPORTS/('RETENTION_AUTO_DECISION_'+str(cycles)+'.json'),dict(checkpoint=c.base.checkpoint(last),**decision))
            if decision['auto_closeout_sufficient']:
                closeout=dict(checkpoint=c.base.checkpoint(last),paired_path=review['old_skill_paired_path'],mixed_path=review['mixed_assessment'],actual_decision=decision,actual_budget=c.base.budget_state(),next_lesson='independent observation noise and episode encoder bias validation',next_executor_deployed=False,all_curricula_finished=False)
                c.base.atomic_json(REPORTS/'RETENTION_PRACTICAL_CLOSEOUT.json',closeout)
                c.w.phase('retention_repaired_next_sensor_DR_preparation',**closeout)
                c.status('retention_repaired_next_sensor_DR_preparation',training_pid=None,evaluation_pid=None,retention_practical_closeout=True)
                break
            exposure=c.base.budget_state()['charged_training_seconds']-charged_start
            if exposure>=7200 or c.ctl.remaining()<=120:
                c.w.phase('retention_auto_progress_saved_review',checkpoint=c.base.checkpoint(last),decision=decision,reason='Finite2h continuation envelope reached; next agent may accept minor residuals or independently prepare next stage');break
            c.w.phase('bounded_retention_auto_learning',source=c.base.checkpoint(last),reused_full_mixed_preflight=str(U/'reports/RETENTION_COMPLETE_PREFLIGHT_PASSED.json'))
            last=c.ctl.training(last,'retention_auto_continue',duration=min(2700,7200-exposure,c.ctl.remaining()))
            assessment=c.mixed_probe(last,32,1500,'auto_learning_assessment')
            pairs,path=c.old_paired(last);cycles+=1
            review=dict(checkpoint=c.base.checkpoint(last),mixed_assessment=assessment,old_skill_paired_path=path,old_skill_paired_pass=pairs['pass_'],world_summary=pairs['world_summary'],actual_budget=c.base.budget_state())
            c.base.atomic_json(REPORTS/('RETENTION_AUTO_REVIEW_'+str(cycles)+'.json'),review)
        c.base.atomic_json(REPORTS/'RETENTION_REVIEW_READY.json',dict(**review,autonomous_continuation_complete=True))
    except BaseException:
        c.w.hold(Path(c.w.read(c.F/'reports/PHYSICAL_DR_STAGE1_REVIEW_READY.json')['checkpoint']['path']),traceback.format_exc());raise
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--guardian',nargs=2);a=p.parse_args()
    if a.guardian:c.guardian(int(a.guardian[0]),a.guardian[1])
    else:controller()
