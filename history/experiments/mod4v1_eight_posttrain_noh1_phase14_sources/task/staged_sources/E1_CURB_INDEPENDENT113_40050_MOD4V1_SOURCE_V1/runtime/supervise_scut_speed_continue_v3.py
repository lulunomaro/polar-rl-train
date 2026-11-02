"""One explicit SCUT-inspired mean-speed diagnostic continuation."""
from supervise_rate7_transition import *
import supervise_rate7_transition as transition
from scut_style_gate_v3 import assess,assess_flat,VERSION as GATE_VERSION
CONTROLLER_VERSION='scut_speed_v3_rate7_budget_dynamic'
J=R/'SCUT_SPEED_V3_STATE.json'
HAND=R/'SCUT_SPEED_V3_HANDOVER.json'
PREP=R/'SCUT_SPEED_V3_PREPARED.json'
START=R/'SCUT_SPEED_V3_CONTINUATION_STARTED.json'
transition.J=prior.J=prior.previous.J=J
transition.GATE_VERSION=prior.VERSION=prior.previous.GATE_VERSION=GATE_VERSION
transition.VERSION=CONTROLLER_VERSION
prior.assess=prior.previous.assess=assess
prior.assess_flat=assess_flat

def status(stage=None,**kw):
    transition.original_status(stage,**kw)
    base.status(autonomy_version=CONTROLLER_VERSION,acceptance_version=GATE_VERSION,
                rate_transition_state=str(J),scope='SCUT-inspired spin mean-XY-speed and slip diagnostics; retained tracking/physical/contact/flat regression; rolling reward, white_v2, hardware, dynamics and PPO unchanged.')
prior.status=prior.previous.status=ctl.status=status

def phase(stage,**kw):
    x=read(J) if J.exists() else {}
    x.update(phase=stage,updated_epoch=time.time(),acceptance_version=GATE_VERSION,controller_version=CONTROLLER_VERSION,**kw)
    base.atomic_json(J,x);status(stage,scut_speed_v3_progress=x)
transition.status=status;transition.phase=prior.phase=prior.previous.phase=phase

def controller():
    assert not START.exists() and not J.exists(),'Explicit versioned continuation already began; inspect receipts, never rerun'
    ctl.S=read(ctl.STATE_PATH);ctl.idle();repair.verify()
    helpers.acquire(P/'autonomy_controller.lock');helpers.acquire(ctl.CANONICAL.parent/'native_floor_supervisor.lock')
    hand=read(HAND);prep=read(PREP)
    assert hand['stage']=='completed' and hand['acceptance_version']==GATE_VERSION and prep['CPU_contracts']['pass_']
    assert len(prep['CPU_contracts']['existing_policy_review'])==2
    assert all(p['new_v3_pass'] for p in prep['CPU_contracts']['existing_policy_review'])
    ck=Path(hand['checkpoint']['path']);assert base.checkpoint(ck)==hand['checkpoint']
    assert ctl.S['chosen_checkpoint']==str(ck) and ctl.S['mature']==hand['last_paired_mature'] and rate.current_limit()==7.
    assert base.budget_state()['authorized_training_seconds']==hand['budget_authorized']==324000
    last=hand['last_paired_mature'];owner=helpers.identity(os.getpid())
    base.atomic_json(START,dict(owner=owner,source=base.checkpoint(ck),acceptance_version=GATE_VERSION,same_canonical=True))
    phase('scut_speed_v3_latest7_assessment',source=base.checkpoint(ck),owner=owner,last_paired_mature=last,
          historical_rejections=ctl.S['rate_rejected'],prior_counts=hand['prior_counts'],
          existing_policy_review=prep['CPU_contracts']['existing_policy_review'],reclassification_not_new_replay=True)
    with (C/'guardian_scut_speed_v3.log').open('x') as log:
        g=subprocess.Popen([base.PY,str(C/'supervise_scut_speed_continue_v3.py'),'--guardian',str(os.getpid()),str(owner['start_ticks'])],
            cwd=P,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    base.atomic_json(R/'SCUT_SPEED_V3_GUARDIAN_STARTED.json',helpers.identity(g.pid))
    physical,skilled=prior.decision(ck)
    if not physical:
        hold(last,'Physical or retained tracking/flat regression during explicit speed-gate migration');return
    current=base.checkpoint(ck)
    if skilled and ctl.remaining()>3600 and prior.pairs(ck,ctl.fresh_label('scut_speed_v3_latest7_multiseed')):
        last=dict(checkpoint=str(ck),cap=7.,profile='white_v2')
        ctl.S['mature']=last;ctl.S['chosen_checkpoint']=str(ck);ctl.persist()
        base.atomic_json(R/'SCUT_SPEED_V3_CAP7_MATURE_ACCEPTED.json',dict(checkpoint=current,cap=7.,profile='white_v2',
            acceptance_version=GATE_VERSION,two_different_formal_policies=True,
            qualification_from_existing_reports_under_new_version=True,
            existing_policy_review=prep['CPU_contracts']['existing_policy_review'],
            fresh_latest_policy_flat_spin_and_two_seed_nominal_DR_pair=True,
            all_prior_verdicts_retained=True,real_robot_certified=False))
        phase('scut_speed_v3_rate7_mature',checkpoint=current,last_paired_mature=last,consecutive=2,failed_blocks=0)
        if not preflight(ck,next_limit(7.),last):return
        consecutive=failures=pair_failures=0;last_sha=None;duration=2700
    else:
        consecutive=0;failures=int(not skilled);pair_failures=int(skilled);last_sha=current['sha256'];duration=2700
    while ctl.remaining() > 120:
        phase('rate7_transition_trial_or_continued', cap=rate.current_limit(), source=base.checkpoint(ck), last_paired_mature=last, consecutive=consecutive, failed_blocks=failures)
        ck = ctl.training(ck, 'rate7_transition_trial_or_continued', duration=min(duration, ctl.remaining()))
        phase('rate7_transition_assessment', cap=rate.current_limit(), checkpoint=base.checkpoint(ck))
        physical, skilled = prior.decision(ck)
        current = base.checkpoint(ck)
        if not physical:
            hold(last, 'Physical or non-slip flat regression during intermediate-rate learning')
            return
        consecutive, failures = progress(skilled, current['sha256'] != last_sha, consecutive, failures)
        last_sha = current['sha256']
        phase('rate7_transition_assessed', cap=rate.current_limit(), checkpoint=current, consecutive=consecutive, failed_blocks=failures, last_paired_mature=last)
        if failures >= 3:
            reject_rate(rate.current_limit(), last, 'Three current-rate skill failures; return exact mature policy')
            return
        if consecutive >= 2 and ctl.remaining() > 3600:
            if prior.pairs(ck, ctl.fresh_label('rate7_transition_mature_multiseed')):
                last = dict(checkpoint=str(ck), cap=rate.current_limit(), profile='white_v2')
                ctl.S['mature'] = last
                ctl.S['chosen_checkpoint'] = str(ck)
                ctl.persist()
                base.atomic_json(R / f'RATE7_TRANSITION_CAP{rate.current_limit():g}_MATURE_ACCEPTED.json', dict(checkpoint=current, cap=rate.current_limit(), profile='white_v2', acceptance_version=GATE_VERSION, two_different_formal_policies=True, two_seed_nominal_DR_pair=True, old_slip_booleans_retained=True, real_robot_certified=False))
                target = next_limit(rate.current_limit())
                if target is None:
                    phase('target_rate_accepted', checkpoint=current)
                    prior.finish(ck, 'Actual4pi qualification completed under inherited SCUT v2 rules')
                    return
                if not preflight(ck, target, last):
                    return
                consecutive = failures = pair_failures = 0
                last_sha = None
                duration = 2700
                continue
            consecutive = 0
            pair_failures += 1
            phase('rate7_transition_paired_regression_failed', cap=rate.current_limit(), paired_failed_blocks=pair_failures, last_paired_mature=last)
            if pair_failures >= 3:
                reject_rate(rate.current_limit(), last, 'Three current-rate paired regression failures')
                return
        duration = 7200
    phase('budget_final_assessment', checkpoint=base.checkpoint(ck))
    prior.finish(ck, 'Effective canonical budget reached; preserve all original slip diagnostic verdicts')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--guardian',nargs=2,type=int);a=p.parse_args()
    if a.guardian:repair.guardian(*a.guardian);raise SystemExit
    __import__('torch').set_num_threads(1);base.STATE.update(read(P/'status.json'))
    try:controller()
    except BaseException:
        status('attention_required',error=traceback.format_exc(),instructions='Preserve current children, versioned phase and exact ledger; never rerun migration/entry or double-open training');raise
