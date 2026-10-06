"""Same mixed task, continuous host progress until a real safe handover.

Saved <=2h blocks, two quick checks, full matched review every bounded6h
window or material concern. A healthy review never creates an idle wait for
the desktop. Stage adequacy is recorded separately from strict targets.
"""
import argparse,os,subprocess,traceback
from pathlib import Path
import supervise_scut_continuous_mix as q
from cadence_contract import next_step,quick_summary
c=q.c;q.ENTRY=c.ENTRY=Path(__file__).resolve()


def controller():
    assert not (c.R/'CADENCE_WAIT_STARTED.json').exists(),'One explicit entry only; never resume'
    c.verify();prior=q.wait_prior()
    if prior is None:return
    last,source_review=q.accept_boundary(prior);anchor=last
    owner=c.helpers.identity(os.getpid())
    with (c.H/'cadence_guardian.log').open('x') as log:
        p=subprocess.Popen([c.base.PY,str(q.ENTRY),'--guardian',str(os.getpid()),str(owner['start_ticks'])],
            cwd=c.P,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    c.base.atomic_json(c.R/'CADENCE_GUARDIAN_STARTED.json',c.helpers.identity(p.pid))
    c.base.atomic_json(c.R/'CADENCE_TRAINING_AUTHORITY_STARTED.json',dict(parent=owner,source=c.base.checkpoint(last),
        runtime_and_full_PPO_unchanged=True,save_interval=25,block_s=7200,full_review_window_s=21600,
        quick_checks='mixed32 and white_v3 flat80; full15s samples',no_repeated_PPO_preflight=True,
        healthy_review_automatically_continues=True,next_lesson_executor_not_installed=True))
    anchor_pairs=c.w.read(Path(c.w.read(c.F/'reports/PHYSICAL_DR_STAGE1_REVIEW_READY.json')['paired_path']))
    anchor_flat=c.w.read(Path(next(r['report_path'] for r in anchor_pairs['rows'] if r['kind']=='flat' and r['seed']==20261002 and r['profile']=='white_v3')))
    window_start=c.base.budget_state()['charged_training_seconds'];block=0;stage=0
    try:
        while True:
            exposure=c.base.budget_state()['charged_training_seconds']-window_start
            plan=next_step(exposure,c.ctl.remaining())
            if plan['action']!='learn':
                assert block==0, 'Every later review uses the actual new policy reports'
                result=dict(checkpoint=c.base.checkpoint(last),paired_path=source_review,reason=plan['reason'],
                    existing_complete_evidence_reused=True,all_curricula_finished=False)
                c.base.atomic_json(c.R/'CADENCE_REVIEW_READY.json',result)
                c.w.phase('cadence_budget_saved_review',**result);break
            c.w.phase('bounded_scut_persistent_mixed_learning',source=c.base.checkpoint(last),duration_s=plan['seconds'],block=block+1)
            last=c.ctl.training(last,'scut_persistent_mixed_learning',duration=plan['seconds']);block+=1
            cache={};mixed=c.mixed_probe(last,32,1500,'scut_cadence_quick_mixed')
            flat,path,_=q.checked_report(last,'flat','white_v3',20261002,cache)
            quick=quick_summary(c.w.read(Path(mixed)),flat,anchor_flat)
            exposure=c.base.budget_state()['charged_training_seconds']-window_start
            plan=next_step(exposure,c.ctl.remaining(),quick['request_full_review'])
            result=dict(checkpoint=c.base.checkpoint(last),mixed_path=mixed,flat_path=str(path),quick=quick,
                        block=block,effective_window_exposure_s=exposure,next_step=plan,actual_budget=c.base.budget_state())
            c.base.atomic_json(c.R/f'CADENCE_QUICK_REVIEW_{block}.json',result)
            if plan['action']=='learn':continue
            pairs,paired_path=q.full_paired(last,cache);decision=q.diagnostic(last,paired_path,mixed)
            material=decision['systematic_straight_regression_detected'] or not decision['rough_valid_segment_signs_correct'] or not decision['pure_signed_yaw_fact_pass']
            result.update(paired_path=paired_path,decision=decision,strict_world_progress_05_confirmed=pairs['world_progress_05_confirmed'],
                          material_regression_confirmed=bool(material),all_curricula_finished=False,next_sensor_executor_deployed=False)
            stage+=1;c.base.atomic_json(c.R/f'CADENCE_STAGE_REVIEW_{stage}.json',result)
            if material or c.ctl.remaining()<=120:
                if material:
                    c.ctl.S['chosen_checkpoint']=str(anchor);c.ctl.persist()
                    result['validated_rollback_source']=c.base.checkpoint(anchor)
                c.base.atomic_json(c.R/'CADENCE_REVIEW_READY.json',result)
                c.w.phase('cadence_retention_review_required' if material else 'cadence_budget_saved_review',**result)
                break
            # Closeout evidence is a progress index, never a budget-finished
            # marker. The original guardian continues during subsequent blocks.
            if decision['auto_closeout_sufficient']:
                c.base.atomic_json(c.R/'CADENCE_PRACTICAL_CLOSEOUT.json',dict(**result,
                    next_lesson='Independent observation noise and episode leg-encoder bias',
                    stable_mixed_training_continues_until_next_executor_safe_handover=True))
            anchor=last;source_review=paired_path
            window_start=c.base.budget_state()['charged_training_seconds']
            c.w.phase('cadence_review_passed_auto_continuing',**result)
            c.status('cadence_review_passed_auto_continuing',training_pid=None,evaluation_pid=None)
        c.base.atomic_json(c.R/'RETENTION_REVIEW_READY.json',c.w.read(c.R/'CADENCE_REVIEW_READY.json'))
    except BaseException:
        c.w.hold(anchor,traceback.format_exc());raise


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--guardian',nargs=2);a=p.parse_args()
    if a.guardian:c.guardian(int(a.guardian[0]),a.guardian[1])
    else:controller()
