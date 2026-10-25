"""One explicit full-save budget handover; inherit unchanged rate7 progression."""
from supervise_rate7_transition import *
import supervise_rate7_transition as transition
transition.VERSION='rate7_transition_scut_v2_budget_dynamic'
HAND=R/'USER_ADD20H_20261004_4TH_HANDOVER.json'
START=R/'USER_ADD20H_20261004_4TH_CONTINUATION_STARTED.json'

def controller():
    assert not START.exists(),'One explicit budget continuation already began; never rerun'
    ctl.S=read(ctl.STATE_PATH);ctl.idle();repair.verify()
    helpers.acquire(P/'autonomy_controller.lock');helpers.acquire(ctl.CANONICAL.parent/'native_floor_supervisor.lock')
    hand=read(HAND);assert hand['stage']=='completed' and hand['extension_id']=='USER_ADD20H_20261004_4TH'
    assert base.budget_state()['authorized_training_seconds']==324000
    ck=Path(hand['checkpoint']['path']);assert base.checkpoint(ck)==hand['checkpoint']
    assert ctl.S['chosen_checkpoint']==str(ck) and ctl.S['mature']==hand['last_paired_mature'] and rate.current_limit()==hand['cap']==7.
    consecutive=hand['consecutive'];failures=hand['failed_blocks'];pair_failures=hand['paired_failed_blocks']
    last_sha=hand['previous_assessed_sha'];last=hand['last_paired_mature'];duration=hand['remaining_block_seconds']
    owner=helpers.identity(os.getpid());base.atomic_json(START,dict(owner=owner,source=base.checkpoint(ck),same_canonical=True,counts_preserved=True))
    phase('rate7_budget_continuation',source=base.checkpoint(ck),owner=owner,last_paired_mature=last,
          consecutive=consecutive,failed_blocks=failures,explicit_budget_extension=hand['extension_id'])
    with (C/'guardian_rate7_budget90.log').open('x') as log:
        g=subprocess.Popen([base.PY,str(C/'supervise_rate7_budget90_continue.py'),'--guardian',str(os.getpid()),str(owner['start_ticks'])],
            cwd=P,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    base.atomic_json(R/'USER_ADD20H_20261004_4TH_GUARDIAN_STARTED.json',helpers.identity(g.pid))
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
        status('attention_required',error=traceback.format_exc(),instructions='Preserve exact children/budget/receipt; no repeated extension or old entry');raise
