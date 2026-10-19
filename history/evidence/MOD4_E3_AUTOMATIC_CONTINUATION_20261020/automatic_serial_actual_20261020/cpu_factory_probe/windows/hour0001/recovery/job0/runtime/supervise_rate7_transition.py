"""One explicit6->7 transition; inherited SCUT v2 gates and one canonical budget."""
import argparse,os,subprocess,time,traceback
from pathlib import Path
import supervise_scut_style_continue_v2 as prior
from transition7_policy import VERSION,GATE_VERSION,validate_limit,next_limit,progress,validate_context
ctl=prior.ctl;base=prior.base;repair=prior.repair;rate=prior.rate;helpers=prior.helpers
C=prior.C;P=prior.ROOT;R=prior.R;read=prior.read
J=R/'RATE7_TRANSITION_STATE.json'
rate.validate_limit=validate_limit;rate.next_limit=next_limit
original_status=prior.status

def status(stage=None,**kw):
    original_status(stage,**kw)
    base.status(autonomy_version=VERSION,rate_transition_state=str(J),
                scope='Explicit measured6 to intermediate7; inherited flat/spin slip-diagnostic gates; reward/white_v2/hardware/physics/PPO unchanged.')
prior.status=prior.previous.status=ctl.status=status

def phase(stage,**kw):
    x=read(J) if J.exists() else {}
    x.update(phase=stage,updated_epoch=time.time(),acceptance_version=GATE_VERSION,controller_version=VERSION,**kw)
    base.atomic_json(J,x);status(stage,rate_transition_progress=x)
prior.phase=phase

def hold(m,reason):
    repair.hold(Path(m['checkpoint']),m['cap'],reason)
    phase('repair_hold',reason=reason,last_paired_mature=m,cap=m['cap'])

def reject_rate(target,last,reason):
    ctl.S['rate_rejected']=list(dict.fromkeys(ctl.S['rate_rejected']+[target]));ctl.persist()
    hold(last,reason)

def preflight(ck,target,last):
    phase('rate7_transition_preflight',target_cap=target,source=base.checkpoint(ck),last_paired_mature=last)
    if target in ctl.S['rate_rejected']:
        hold(last,'Next rate already rejected; preserve budget without repeated PPO');return False
    previous_cap=rate.current_limit()
    repair.set_limit(target,'Explicit finer rate step; exact paired mature source and unchanged recipe')
    try:
        short=ctl.probe(ck,ctl.fresh_label('rate7_transition_short'),steps=300)
        assert short['physical_smoke_pass'] and ctl.safety_veto(short)
        ctl.fullscale(ck,ctl.fresh_label('rate7_transition_physics'))
        ctl.training(ck,'rate7_transition128_discard',count=128,iterations=2,duration=600)
    except BaseException:
        if base.trainers() or base.budget_state().get('active_segment'):raise
        rejected=R/(f'RATE7_TRANSITION_CAP{target:g}_PREFLIGHT_REJECTED.json')
        assert not rejected.exists(),'Keep prior rejection intact; no duplicate attempt'
        base.atomic_json(rejected,dict(error=traceback.format_exc(),source=base.checkpoint(ck),cap=target,
             previous_cap=previous_cap,acceptance_version=GATE_VERSION,old_reports_unchanged=True))
        repair.set_limit(previous_cap,'Retain previously measured cap after independent preflight rejection')
        reject_rate(target,last,'Explicit intermediate-rate physical/PPO preflight rejected; retain all evidence and complete mature source');return False
    base.atomic_json(R/(f'RATE7_TRANSITION_CAP{target:g}_PREFLIGHT_PASSED.json'),
        dict(source=base.checkpoint(ck),cap=target,profile='white_v2',acceptance_version=GATE_VERSION,
             original_rejection_history_retained=True,preflight_weights_discarded=True,same_canonical_budget=True))
    return True

def controller():
    assert not J.exists(),'One-shot already began; inspect exact receipt/children, never rerun'
    ctl.S=read(ctl.STATE_PATH);ctl.idle();repair.verify()
    helpers.acquire(P/'autonomy_controller.lock');helpers.acquire(ctl.CANONICAL.parent/'native_floor_supervisor.lock')
    prepared=read(R/'RATE7_TRANSITION_PREPARED.json');context=prepared['context']
    assert prepared['CPU_contracts']['pass_'];validate_context(context)
    prior_state=read(prior.J)
    assert prior_state['phase']=='repair_hold' and ctl.S['mature']==context['mature'] and ctl.S['chosen_checkpoint']==context['checkpoint']['path']
    ck=Path(context['checkpoint']['path']);assert base.checkpoint(ck)==context['checkpoint']
    assert rate.current_limit()==6. and not ctl.S.get('active_training') and not base.budget_state()['active_segment']
    assert base.budget_state()['authorized_training_seconds']==context['budget']['authorized']
    last=ctl.S['mature'];owner=helpers.identity(os.getpid())
    phase('rate7_transition_validated',source=base.checkpoint(ck),last_paired_mature=last,owner=owner,
          historical_rejections=ctl.S['rate_rejected'],budget_added=False,consecutive=0,failed_blocks=0)
    prior_state.update(superseded_by=str(J),superseded_epoch=time.time());base.atomic_json(prior.J,prior_state)
    with (C/'guardian_rate7_transition.log').open('x') as log:
        g=subprocess.Popen([base.PY,str(C/'supervise_rate7_transition.py'),'--guardian',str(os.getpid()),str(owner['start_ticks'])],
             cwd=P,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    base.atomic_json(R/'RATE7_TRANSITION_GUARDIAN_STARTED.json',helpers.identity(g.pid))
    if not preflight(ck,7.,last):return
    consecutive=failures=pair_failures=0;last_sha=None;duration=2700
    while ctl.remaining()>120:
        phase('rate7_transition_trial_or_continued',cap=rate.current_limit(),source=base.checkpoint(ck),
              last_paired_mature=last,consecutive=consecutive,failed_blocks=failures)
        ck=ctl.training(ck,'rate7_transition_trial_or_continued',duration=min(duration,ctl.remaining()))
        phase('rate7_transition_assessment',cap=rate.current_limit(),checkpoint=base.checkpoint(ck))
        physical,skilled=prior.decision(ck);current=base.checkpoint(ck)
        if not physical:hold(last,'Physical or non-slip flat regression during intermediate-rate learning');return
        consecutive,failures=progress(skilled,current['sha256']!=last_sha,consecutive,failures);last_sha=current['sha256']
        phase('rate7_transition_assessed',cap=rate.current_limit(),checkpoint=current,consecutive=consecutive,failed_blocks=failures,last_paired_mature=last)
        if failures>=3:reject_rate(rate.current_limit(),last,'Three current-rate skill failures; return exact mature policy');return
        if consecutive>=2 and ctl.remaining()>3600:
            if prior.pairs(ck,ctl.fresh_label('rate7_transition_mature_multiseed')):
                last=dict(checkpoint=str(ck),cap=rate.current_limit(),profile='white_v2')
                ctl.S['mature']=last;ctl.S['chosen_checkpoint']=str(ck);ctl.persist()
                base.atomic_json(R/(f'RATE7_TRANSITION_CAP{rate.current_limit():g}_MATURE_ACCEPTED.json'),
                     dict(checkpoint=current,cap=rate.current_limit(),profile='white_v2',acceptance_version=GATE_VERSION,
                          two_different_formal_policies=True,two_seed_nominal_DR_pair=True,old_slip_booleans_retained=True,real_robot_certified=False))
                target=next_limit(rate.current_limit())
                if target is None:
                    phase('target_rate_accepted',checkpoint=current);prior.finish(ck,'Actual4pi qualification completed under inherited SCUT v2 rules');return
                if not preflight(ck,target,last):return
                consecutive=failures=pair_failures=0;last_sha=None;duration=2700;continue
            consecutive=0;pair_failures+=1
            phase('rate7_transition_paired_regression_failed',cap=rate.current_limit(),paired_failed_blocks=pair_failures,
                  last_paired_mature=last)
            if pair_failures>=3:reject_rate(rate.current_limit(),last,'Three current-rate paired regression failures');return
        duration=7200
    phase('budget_final_assessment',checkpoint=base.checkpoint(ck))
    prior.finish(ck,'Effective canonical budget reached; preserve all original slip diagnostic verdicts')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--guardian',nargs=2,type=int);a=p.parse_args()
    if a.guardian:repair.guardian(*a.guardian);raise SystemExit
    __import__('torch').set_num_threads(1);base.STATE.update(read(P/'status.json'))
    try:controller()
    except BaseException:
        status('attention_required',error=traceback.format_exc(),instructions='Preserve exact child, phase and ledger; do not rerun transition entry or duplicate trainer/20k');raise
