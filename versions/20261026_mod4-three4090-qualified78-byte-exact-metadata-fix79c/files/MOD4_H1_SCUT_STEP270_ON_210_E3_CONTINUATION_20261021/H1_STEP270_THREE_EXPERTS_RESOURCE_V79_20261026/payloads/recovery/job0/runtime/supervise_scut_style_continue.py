"""Explicit SCUT-inspired acceptance continuation, separate from old entries.

Only the qualification rule changes. Existing rolling reward, task/physics,
hardware, PPO and white_v2 remain unchanged. All old slip verdicts are shadows.
"""
import argparse,os,subprocess,time,traceback
from pathlib import Path
import supervise_contact_gate_continue as previous
from scut_style_gate import assess,VERSION
repair=previous.repair;ctl=previous.ctl;base=previous.base
rate=previous.rate;helpers=previous.helpers;C=previous.C;ROOT=previous.ROOT;R=previous.R
read=previous.read
J=R/'SCUT_STYLE_STATE.json'
previous.assess=assess;previous.GATE_VERSION=VERSION;previous.J=J

def status(stage=None,**kw):
    kw.pop('scope',None)
    repair.status(stage,acceptance_version=VERSION,scut_style_state=str(J),
                  original_mesh015_shadow_retained=True,loaded015_shadow_retained=True,**kw)
    base.status(autonomy_version='scut_style_v1_bounded',
                scope='SCUT-inspired slip-diagnostic curriculum with retained physical/tracking/support/old-skill gates. Rolling reward/white_v2/physics/hardware/PPO unchanged; not an exact SCUT task port.')
previous.status=status;ctl.status=status

def phase(stage,**kw):
    x=read(J) if J.exists() else {}
    x.update(phase=stage,updated_epoch=time.time(),acceptance_version=VERSION,**kw)
    base.atomic_json(J,x)
    status(stage,scut_style_progress=x)
previous.phase=phase

def hold(m,reason):
    repair.hold(Path(m['checkpoint']),m['cap'],reason)
    phase('repair_hold',reason=reason,last_paired_mature=m)

def accepted(ck,last,**extra):
    current=base.checkpoint(ck)
    m=dict(checkpoint=str(ck),cap=rate.current_limit(),profile='white_v2')
    ctl.S['mature']=m;ctl.S['chosen_checkpoint']=str(ck);ctl.persist()
    base.atomic_json(R/f'SCUT_STYLE_RATE{rate.current_limit():g}_MATURE_ACCEPTED.json',
                     dict(checkpoint=current,acceptance_version=VERSION,
                          cap=rate.current_limit(),profile='white_v2',
                          real_robot_certified=False,old_slip_verdicts_retained=True,**extra))
    return m

def step(ck,last):
    target=rate.next_limit(rate.current_limit())
    if target is None:
        phase('target_rate_accepted',checkpoint=base.checkpoint(ck))
        previous.finish(ck,'Measured target4pi under SCUT-inspired version; every prior slip verdict remains separately reported')
        return False
    if target in ctl.S['rate_rejected'] or not repair.preflight_rate(ck,target):
        hold(last,'Next rate rejected; no repeated mature-cap PPO')
        return False
    return True

def controller():
    assert not J.exists(),'One-shot already began: inspect receipts, never rerun'
    ctl.S=read(ctl.STATE_PATH);ctl.idle();repair.verify()
    helpers.acquire(ROOT/'autonomy_controller.lock')
    helpers.acquire(ctl.CANONICAL.parent/'native_floor_supervisor.lock')
    hand=read(R/'SCUT_STYLE_HANDOVER.json');prep=read(R/'SCUT_STYLE_PREPARED.json')
    assert hand['stage']=='completed' and hand['acceptance_version']==VERSION
    assert prep['CPU_contracts']['pass_'] and prep['existing_policy_review']['pass_']
    ck=Path(hand['complete_checkpoint']['path'])
    assert base.checkpoint(ck)==hand['complete_checkpoint']
    assert rate.current_limit()==6. and ctl.S['chosen_checkpoint']==str(ck)
    last=ctl.S['mature']
    assert last==hand['last_paired_mature'] and last['cap']==5.
    owner=helpers.identity(os.getpid())
    phase('scut_style_latest6_assessment',source=base.checkpoint(ck),last_paired_mature=last,
          consecutive=0,failed_blocks=0,historical_rejections=ctl.S['rate_rejected'],
          prior_policy_review=prep['existing_policy_review'])
    with (C/'guardian_scut_style.log').open('x') as log:
        g=subprocess.Popen([base.PY,str(C/'supervise_scut_style_continue.py'),'--guardian',
                            str(os.getpid()),str(owner['start_ticks'])],cwd=ROOT,
                           stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    base.atomic_json(R/'SCUT_STYLE_GUARDIAN_STARTED.json',helpers.identity(g.pid))
    physical,skilled=previous.decision(ck)
    if not physical:hold(last,'Physical/original-flat regression during explicit acceptance migration');return
    # Two existing, different complete policies were explicitly reclassified.
    # Fresh latest-policy and paired regression still required before first8.
    if skilled and previous.pairs(ck,ctl.fresh_label('scut_style_latest6_multiseed')):
        last=accepted(ck,last,two_different_formal_policies=True,
                      qualification_from_existing_reports_under_new_version=True,
                      existing_policy_review=prep['existing_policy_review'],
                      fresh_latest_policy_flat_spin_and_two_seed_nominal_DR_pair=True)
        phase('scut_style_rate_mature',cap=6.,last_paired_mature=last,consecutive=2,failed_blocks=0)
        if not step(ck,last):return
        consecutive=0;failures=0;last_sha=None;duration=2700
    else:
        consecutive=0;failures=1;last_sha=base.checkpoint(ck)['sha256'];duration=2700
    while ctl.remaining()>120:
        phase('scut_style_rate_trial_or_continued',cap=rate.current_limit(),source=base.checkpoint(ck),
              last_paired_mature=last,consecutive=consecutive,failed_blocks=failures)
        ck=ctl.training(ck,'scut_style_rate_trial_or_continued',duration=min(duration,ctl.remaining()))
        phase('scut_style_rate_assessment',cap=rate.current_limit(),checkpoint=base.checkpoint(ck))
        physical,skilled=previous.decision(ck);current=base.checkpoint(ck)
        if not physical:hold(last,'Physical/original-flat regression under SCUT-inspired curriculum');return
        different=current['sha256']!=last_sha;last_sha=current['sha256']
        consecutive=(consecutive+int(different)) if skilled else 0
        failures=0 if skilled else failures+1
        phase('scut_style_rate_assessed',cap=rate.current_limit(),checkpoint=current,
              consecutive=consecutive,failed_blocks=failures,last_paired_mature=last)
        if failures>=3:
            ctl.S['rate_rejected']=list(dict.fromkeys(ctl.S['rate_rejected']+[rate.current_limit()]));ctl.persist()
            hold(last,'Three physical/tracking/old-skill qualification failures; retain all policies and budget');return
        if consecutive>=2 and ctl.remaining()>3600:
            if previous.pairs(ck,ctl.fresh_label('scut_style_mature_multiseed')):
                last=accepted(ck,last,two_different_formal_policies=True,
                              two_seed_nominal_DR_pair=True,qualification_from_existing_reports_under_new_version=False)
                if not step(ck,last):return
                consecutive=0;failures=0;last_sha=None;duration=2700;continue
            consecutive=0;failures+=1
            if failures>=3:hold(last,'Repeated current-cap paired regression failure');return
        duration=7200
    phase('budget_final_assessment',checkpoint=base.checkpoint(ck))
    previous.finish(ck,'Effective canonical budget reached; report SCUT-inspired qualification and every old slip verdict separately')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--guardian',nargs=2,type=int);a=p.parse_args()
    if a.guardian:repair.guardian(*a.guardian);raise SystemExit
    __import__('torch').set_num_threads(1);base.STATE.update(read(ROOT/'status.json'))
    try:controller()
    except BaseException:
        status('attention_required',error=traceback.format_exc(),
               instructions='Preserve actual child and ledger; no old-entry rerun or second trainer');raise
