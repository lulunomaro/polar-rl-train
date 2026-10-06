"""Continuous mixed PPO cadence; wait one existing closeout, then take authority.

Keep the MOD4 runtime byte-exact. No repeated preflight, hot edits, signals,
active-ledger clearing or new budget. Same canonical locks and <=2h blocks.
"""
import argparse, os, subprocess, time, traceback
from pathlib import Path
import supervise_retention_train as c
import continue_retention_precision_review_once as precision
from retention_autonomous_progress import diagnostic
from cadence_contract import next_step, reuse_exact

ENTRY=Path(__file__).resolve()
PREVIOUS=Path('/home/egde/rl_candidates/MOD4_CONTINUOUS_MIX_BASELINE_20261006')
X=Path('/home/egde/rl_candidates/MOD4_ROUGH_RETENTION_SOURCE_REVIEW_20261006')
c.ENTRY=ENTRY;c.w.STATE=c.R/'SCUT_CADENCE_STATE.json';c.mixed_probe=precision.mixed_probe


def live(saved):
    if not saved:return None
    actual=c.helpers.identity(saved['pid'])
    return actual if actual and actual['state']!='Z' and actual['start_ticks']==saved['start_ticks'] else None


def protocol(ck,kind,profile,seed):
    name={'flat':'validate_speed.py','spin':'contact_calibration_probe.py','world':'world_spin_probe.py'}[kind]
    return dict(checkpoint_path=str(ck),checkpoint_sha256=c.base.sha(ck),kind=kind,profile=profile,seed=seed,
                steps=1500,num_envs=80 if kind=='flat' else 88,probe_sha256=c.base.sha(c.CODE/name),
                runtime_freeze_sha256=c.base.sha(c.w.F))


def checked_report(ck,kind,profile,seed,cache):
    expected=protocol(ck,kind,profile,seed);key=(kind,profile,seed)
    if key in cache:
        item=cache[key];path=Path(reuse_exact(item,expected,c.base.sha(item['report_path'])))
        raw=c.w.read(path)
        assert raw['checkpoint']==str(ck) and raw['seed']==seed and raw['steps']==1500 and raw['seconds']==15
        verdict=c.w.assess_flat(raw) if kind=='flat' else c.w.evidence(raw,'spin',15)
        assert verdict['pass_'];c.parameter_readback(raw,profile,kind)
        return raw,path,True
    raw,path=c.w.probe(ck,kind,profile,seed);c.parameter_readback(raw,profile,kind)
    cache[key]=dict(expected,report_path=str(path),report_sha256=c.base.sha(path),data_admission_pass=True,
                    initial_final_parameters_checked=True)
    return raw,path,False


def full_paired(ck,cache):
    rows=[];reused=[];profiles=('nominal','white_v2','white_v3')
    for seed in (20261002,20261003):
        for kind in ('flat','spin','world'):
            paths=[]
            for profile in profiles:
                raw,path,reuse=checked_report(ck,kind,profile,seed,cache);paths.append(str(path))
                if reuse:reused.append(cache[(kind,profile,seed)])
            rows.append(dict(seed=seed,kind=kind,paths=paths))
    result=c.paired_review(rows,lambda p:c.w.read(Path(p)),c.w.assess_flat,c.w.evidence,c.w.target,c.base.checkpoint(ck),profiles)
    result.update(pairs=rows,world_summary=c.compact_worlds(result['world_tracking']),learning_admission_only=True,
                  exact_reports_reused=reused,additional_probe_count=18-len(reused))
    out=c.ctl.REPORTS/(c.ctl.fresh_label('continuous_mix_stage_paired')+'.json');c.base.atomic_json(out,result)
    return result,str(out)


def wait_prior():
    launched=c.w.read(PREVIOUS/'reports/CONTINUOUS_MIX_LAUNCHED.json')
    guard=c.w.read(PREVIOUS/'reports/RETENTION_GUARDIAN_STARTED.json')
    c.base.atomic_json(c.R/'CADENCE_WAIT_STARTED.json',dict(epoch=time.time(),owner=c.helpers.identity(os.getpid()),
        previous_parent=launched['parent'],previous_guardian=guard,waits_existing_complete_closeout=True,
        budget_operations=0,no_current_trainer_change=True,next_blocks_seconds=7200,quick_probe_count=2,
        full_suite_at_stage_closeout_or_material_concern=True))
    c.w.phase('waiting_existing_baseline_closeout',previous_root=str(PREVIOUS),training_takeover_started=False)
    while True:
        state=c.w.read(PREVIOUS/'reports/CONTINUOUS_MIX_STATE.json')
        if state.get('phase') in ('repair_hold','attention_required_active_child_preserved'):
            c.w.phase('prior_attention_required',prior_state=state,no_automatic_old_entry_restart=True);return None
        review=PREVIOUS/'reports/CONTINUOUS_MIX_REVIEW_READY.json'
        if review.exists() and not live(launched['parent']) and not live(guard):return c.w.read(review)
        if not live(launched['parent']) and not review.exists():
            c.w.phase('prior_unexpected_exit',prior_state=state,active_child_preserved=True);return None
        time.sleep(15)


def accept_boundary(prior):
    c.helpers.acquire(c.P/'autonomy_controller.lock');c.helpers.acquire(c.ctl.CANONICAL.parent/'native_floor_supervisor.lock')
    c.ctl.S=c.w.read(c.ctl.STATE_PATH);c.base.STATE.update(c.w.read(c.P/'status.json'))
    c.ctl.idle();c.verify();assert not c.ctl.S.get('active_training')
    for n,sha in c.w.read(PREVIOUS/'reports/SOURCE_FREEZE.json')['sha256'].items():
        assert c.base.sha(PREVIOUS/n)==c.base.sha(c.H/n)==sha
    assert c.w.read(X/'reports/RETENTION_COMPLETE_PREFLIGHT_PASSED.json')['pass_']
    candidate=Path(prior['checkpoint']['path']);info=c.base.checkpoint(candidate)
    assert info==prior['checkpoint'] and info['finite_tensors']==68
    installed=c.w.read(c.R/'CADENCE_INSTALL_BOUNDARY.json')
    latest=c.w.read(candidate.parent/'latest_complete.json')
    assert latest['checkpoint']==str(candidate) and latest['pid']==installed['old_trainer']['pid']
    assert not live(installed['old_trainer'])
    assert c.w.read(candidate.parent/'rolling_source_freeze.json')['sha256']==c.w.read(PREVIOUS/'reports/SOURCE_FREEZE.json')['sha256']
    manifest=c.w.read(candidate.parent/'run_manifest.json')
    for n,sha in manifest['src_sha256'].items():assert c.base.sha(candidate.parent/'src_snapshot'/n)==sha
    assert len([s for s in c.base.budget_state()['completed_segments'] if s['pid']==latest['pid']])==1
    paired=c.w.read(Path(prior['paired_path']));assert paired['pass_'] and paired['checkpoint']==info and paired['all_initial_root_q_exact']
    decision=diagnostic(candidate,prior['paired_path'],prior['mixed_assessment'])
    material=decision['systematic_straight_regression_detected'] or not decision['rough_valid_segment_signs_correct'] or not decision['pure_signed_yaw_fact_pass']
    if material:
        balanced=c.w.read(X/'reports/RETENTION_MODEL23621_PAIRED_ACTUAL_REVIEW.json')
        source=Path(balanced['checkpoint']['path']);source_info=c.base.checkpoint(source)
        assert source_info==balanced['checkpoint'] and source_info['finite_tensors']==68
        assert balanced['admission_pass'] and balanced['all_initial_root_q_exact'] and not balanced['systematic_straight_regression_detected']
        assert balanced['pure_signed_yaw_fact_pass'] and balanced['rough_valid_segment_signs_correct']
        source_review=balanced['paired_path']
    else:source=candidate;source_info=info;source_review=prior['paired_path']
    before=c.ctl.CANONICAL.read_bytes()
    c.ctl.S.update(profile='white_v3',chosen_checkpoint=str(source),active_training=None);c.ctl.persist()
    assert c.ctl.CANONICAL.read_bytes()==before
    receipt=dict(epoch=time.time(),source=source_info,preserved_prior_candidate=info,prior_paired_path=prior['paired_path'],
        source_paired_path=source_review,prior_decision=decision,balanced_rollback_for_material_regression=bool(material),
        no_current_runtime_change=True,existing_scope_preflight_reused=True,budget_operations=0,budget_bytes_exact=True,
        no_tail_reaccounting=True,canonical_sha256=c.base.sha(c.ctl.CANONICAL),old_authority_exited=True,same_two_locks_acquired=True)
    c.base.atomic_json(c.R/'CADENCE_HANDOVER_ACCEPTED.json',receipt)
    return source,source_review


def controller():
    assert not (c.R/'CADENCE_WAIT_STARTED.json').exists(),'One explicit entry only; never resume'
    c.verify();prior=wait_prior()
    if prior is None:return
    last,source_review=accept_boundary(prior);anchor=last
    owner=c.helpers.identity(os.getpid())
    with (c.H/'cadence_guardian.log').open('x') as log:
        p=subprocess.Popen([c.base.PY,str(ENTRY),'--guardian',str(os.getpid()),str(owner['start_ticks'])],
            cwd=c.P,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    c.base.atomic_json(c.R/'CADENCE_GUARDIAN_STARTED.json',c.helpers.identity(p.pid))
    c.base.atomic_json(c.R/'CADENCE_TRAINING_AUTHORITY_STARTED.json',dict(epoch=time.time(),parent=owner,source=c.base.checkpoint(last),
        runtime_and_full_PPO_unchanged=True,save_interval=25,block_s=7200,finite_stage_s=21600,
        quick_checks='mixed32 and white_v3 flat80; full15s samples',no_repeated_PPO_preflight=True))
    anchor_pairs=c.w.read(Path(c.w.read(c.F/'reports/PHYSICAL_DR_STAGE1_REVIEW_READY.json')['paired_path']))
    anchor_flat=c.w.read(Path(next(r['report_path'] for r in anchor_pairs['rows'] if r['kind']=='flat' and r['seed']==20261002 and r['profile']=='white_v3')))
    charged_start=c.base.budget_state()['charged_training_seconds'];block=0
    try:
        while True:
            exposure=c.base.budget_state()['charged_training_seconds']-charged_start
            plan=next_step(exposure,c.ctl.remaining())
            if plan['action']!='learn':
                # No new block if no safe time remains; reuse the complete prior
                # review instead of creating duplicate simulations for its SHA.
                assert block==0, 'Use this SHA\'s actual quick/full closeout after any new training'
                c.base.atomic_json(c.R/'CADENCE_REVIEW_READY.json',dict(checkpoint=c.base.checkpoint(last),
                    paired_path=source_review,reason=plan['reason'],existing_complete_evidence_reused=True,all_curricula_finished=False))
                c.w.phase('cadence_budget_saved_review',checkpoint=c.base.checkpoint(last),reason=plan['reason'])
                break
            c.w.phase('bounded_scut_continuous_mixed_learning',source=c.base.checkpoint(last),duration_s=plan['seconds'],block=block+1)
            last=c.ctl.training(last,'scut_continuous_mixed_learning',duration=plan['seconds']);block+=1
            cache={};mixed=c.mixed_probe(last,32,1500,'scut_cadence_quick_mixed')
            flat,path,_=checked_report(last,'flat','white_v3',20261002,cache)
            from cadence_contract import quick_summary
            quick=quick_summary(c.w.read(Path(mixed)),flat,anchor_flat)
            exposure=c.base.budget_state()['charged_training_seconds']-charged_start
            plan=next_step(exposure,c.ctl.remaining(),quick['request_full_review'])
            result=dict(checkpoint=c.base.checkpoint(last),mixed_path=mixed,flat_path=str(path),quick=quick,
                        block=block,effective_exposure_s=exposure,next_step=plan,actual_budget=c.base.budget_state())
            c.base.atomic_json(c.R/f'CADENCE_QUICK_REVIEW_{block}.json',result)
            if plan['action']=='learn':continue
            pairs,paired_path=full_paired(last,cache);decision=diagnostic(last,paired_path,mixed)
            material=decision['systematic_straight_regression_detected'] or not decision['rough_valid_segment_signs_correct'] or not decision['pure_signed_yaw_fact_pass']
            result.update(paired_path=paired_path,decision=decision,strict_world_progress_05_confirmed=pairs['world_progress_05_confirmed'],
                          material_regression_confirmed=bool(material),all_curricula_finished=False,next_sensor_executor_deployed=False,
                          next_lesson='Actual balanced review, then independent sensor DR; no percentage graduation gate')
            if material:
                c.ctl.S['chosen_checkpoint']=str(anchor);c.ctl.persist()
                result['validated_rollback_source']=c.base.checkpoint(anchor)
            c.base.atomic_json(c.R/'CADENCE_REVIEW_READY.json',result)
            c.w.phase('cadence_retention_review_required' if material else 'scut_mixed_stage_closeout_review',**result)
            c.status('scut_mixed_stage_closeout_review',training_pid=None,evaluation_pid=None,final_evaluation=result)
            break
        c.base.atomic_json(c.R/'RETENTION_REVIEW_READY.json',c.w.read(c.R/'CADENCE_REVIEW_READY.json'))
    except BaseException:
        c.w.hold(anchor,traceback.format_exc());raise


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--guardian',nargs=2);a=p.parse_args()
    if a.guardian:c.guardian(int(a.guardian[0]),a.guardian[1])
    else:controller()
