"""Explicit gate-only continuation: bounded learning exposure, not quality-number graduation.

New one-shot entry. Hardware/physics/reward/PPO remain byte-exact; no old entry
is resumed. Actual model/numerical/task failures still cause a saved rollback.
"""
import argparse,math,os,subprocess,time,traceback
from pathlib import Path
import supervise_rate7_transition as transition
from scut_half_rate_policy import validate_limit, next_limit
from scut_curriculum_gate_v4 import VERSION,assess,assess_flat,evidence,fullscale as assess_fullscale,target_evidence
prior=transition.prior;previous=prior.previous
ctl=transition.ctl;base=transition.base;repair=transition.repair;rate=transition.rate;helpers=transition.helpers
C=transition.C;P=transition.P;R=transition.R;read=transition.read
J=R/'SCUT_HALF_RATE_STATE.json';HAND=R/'SCUT_HALF_RATE_HANDOVER.json'
transition.next_limit=next_limit
rate.validate_limit=validate_limit
CONTROLLER_VERSION='scut_v4_half_rate_exposure_budget_dynamic'
prior.assess=previous.assess=assess;prior.assess_flat=assess_flat
prior.VERSION=previous.GATE_VERSION=VERSION
previous.J=prior.J=transition.J=J
PAIRED_TARGET=[]

def status(stage=None,**kw):
    kw.pop('scope',None)
    repair.status(stage,acceptance_version=VERSION,qualification_state=str(J),**kw)
    base.status(autonomy_version=CONTROLLER_VERSION,
        scope='SCUT-inspired staged learning. Finite performance values are diagnostics, not curriculum vetoes. Existing MOD4 task failure/reset, model/data correctness and hardware envelope retained. Target achievement requires measured signed yaw.')
prior.status=previous.status=ctl.status=status

def phase(stage,**kw):
    x=read(J) if J.exists() else {};x.update(phase=stage,updated_epoch=time.time(),
        acceptance_version=VERSION,controller_version=CONTROLLER_VERSION,**kw)
    base.atomic_json(J,x);status(stage,scut_curriculum_progress=x)

def freeze_run(run):
    repair.freeze_run(run)
    p=run/'rolling_source_freeze.json';x=read(p)
    x.update(acceptance_version=VERSION,controller_version=CONTROLLER_VERSION,
        finite_performance_numeric_vetoes_removed=True,policy_reward_same_as_rolling_v1=True,
        prior_verdicts_retained=True,curriculum_qualification_is_not_target_achievement=True)
    base.atomic_json(p,x)
rate.freeze_run=ctl.spin.freeze_run=freeze_run

def gate(r,kind):return (assess_flat(r) if kind=='flat' else assess(r))['pass_']
prior.gate=previous.gate=ctl.gate=gate

def decision(ck):
    label=ctl.fresh_label('scut_curriculum_v4_assessment')
    flat=prior.probe(ck,label+'_flat','flat',seed=20260927)
    yaw=prior.probe(ck,label+'_rate')
    f=assess_flat(flat);a=assess(yaw);ok=f['pass_'] and a['pass_']
    out=dict(learning_admission_pass=ok,continue_current_rate=ok,
        current_rate_skill_pass=None,curriculum_qualification_is_not_target_achievement=True,
        checkpoint=base.checkpoint(ck),cap=rate.current_limit(),acceptance_version=VERSION,
        flat_evidence=f,spin_evidence=a,original_flat_admission=rate.assess(flat),
        original_spin_skill_pass=yaw['spin_skill_pass'],legacy_spin_skill_pass=yaw.get('spin_skill_pass_legacy_reference'),
        reported_pure_yaw=[dict(command=g['wz'],yaw_rates=[yaw['per_environment']['yaw_rate'][i]
          for i,gid in enumerate(yaw['group_ids']) if gid==g['group_id']]) for g in yaw['groups'] if g['profile']=='spin'],
        report_paths=dict(flat=str(ctl.REPORTS/(label+'_flat.json')),spin=str(ctl.REPORTS/(label+'_rate.json'))))
    base.atomic_json(ctl.REPORTS/(label+'_decision.json'),out);status(latest_rate_decision=out)
    return ok

def pairs(ck,label):
    global PAIRED_TARGET
    PAIRED_TARGET=[];rows=[];passed=True
    for seed in (20261002,20261003):
        for kind in ('flat','spin'):
            rs=[prior.probe(ck,f'{label}_{kind}_{profile}_{seed}',kind,profile,seed) for profile in ('nominal','white_v2')]
            exact=all(rs[0][k]==rs[1][k] for k in ('reset_joint_pos_before_physics','reset_root_before_physics'))
            verdicts=[assess_flat(r) if kind=='flat' else assess(r) for r in rs]
            gs=[a['pass_'] for a in verdicts];passed &= exact and all(gs)
            if kind=='spin' and abs(rate.current_limit()-4*math.pi)<1e-8:
                PAIRED_TARGET.extend(target_evidence(r,rate.current_limit()) for r in rs)
            rows.append(dict(seed=seed,kind=kind,initial_root_q_exact=exact,admission=verdicts,
                original_flat_booleans=[rate.assess(r)['eligible_for_mild_dr_trial'] for r in rs] if kind=='flat' else None,
                original_spin_booleans=[r.get('spin_skill_pass') for r in rs],legacy_spin_booleans=[r.get('spin_skill_pass_legacy_reference') for r in rs]))
    base.atomic_json(ctl.REPORTS/(label+'_paired_decision.json'),dict(pass_=bool(passed),pairs=rows,
        checkpoint=base.checkpoint(ck),cap=rate.current_limit(),acceptance_version=VERSION,
        target_tracking_evidence=PAIRED_TARGET,curriculum_qualification_is_not_target_achievement=True))
    return bool(passed)

def fullscale(ck,label):
    ctl.idle();repair.verify();out=ctl.REPORTS/(label+'_20k.json');assert not out.exists()
    p=base.spawn([str(ctl.CODE/'spin_rate_fullscale_probe.py'),'--headless','--checkpoint',str(ck),
        '--num_envs','20000','--steps','120','--max-rate',str(rate.current_limit()),'--output',str(out)],out.with_suffix('.log'))
    ctl.LIVE=p;status('fullscale_integrity_preflight',validation_pid=p.pid,training_pid=None,active_log=str(out.with_suffix('.log')))
    r=base.wait_probe(p,out);ctl.LIVE=None;a=assess_fullscale(r)
    old_pass,old=base.accept_physics_smoke(r)
    base.atomic_json(ctl.REPORTS/(label+'_20k_acceptance.json'),dict(**a,old_physical_smoke=old,old_physical_smoke_pass=old_pass))
    status(validation_pid=None,physics_preflight_acceptance=a)
    assert a['pass_'],a
    return r

def hold(last,reason):
    repair.hold(Path(last['checkpoint']),last['cap'],reason)
    phase('repair_hold',reason=reason,last_validated_source=last,
          performance_numbers_did_not_cause_hold=True)

def preflight(ck,target,last):
    # A new-version explicit attempt retains old rejection receipts without treating
    # a legacy quality-number rejection as proof that an untrained cap is unlearnable.
    receipt=R/f'SCUT_HALF_RATE_CAP{target:g}_PREFLIGHT.json'
    assert not receipt.exists(),'Inspect existing same-version attempt; do not repeat'
    previous_cap=rate.current_limit();repair.set_limit(target,'Separate rate-only SCUT-inspired learning step')
    phase('rate_integrity_preflight',target_cap=target,source=base.checkpoint(ck))
    try:
        short=prior.probe(ck,ctl.fresh_label('scut_v4_short'),steps=300)
        a=evidence(short,'spin',3);assert a['pass_'],a
        fullscale(ck,ctl.fresh_label('scut_v4_fullscale'))
        ctl.training(ck,'scut_v4_128_discard',count=128,iterations=2,duration=600)
    except BaseException:
        if base.trainers() or base.budget_state().get('active_segment'):raise
        base.atomic_json(receipt,dict(pass_=False,source=base.checkpoint(ck),target=target,
            error=traceback.format_exc(),acceptance_version=VERSION))
        repair.set_limit(previous_cap,'Actual integrity/preflight failure; preserve all candidate evidence')
        hold(last,'Actual task/model/data/PPO preflight failure');return False
    base.atomic_json(receipt,dict(pass_=True,source=base.checkpoint(ck),target=target,
        acceptance_version=VERSION,preflight_weights_discarded=True,same_canonical=True,
        historical_rejections=ctl.S['rate_rejected']))
    return True

def finish(ck,outcome,target_confirmed=False):
    ctl.idle();label=ctl.fresh_label('scut_v4_final')
    f=prior.probe(ck,label+'_flat','flat');w=prior.probe(ck,label+'_white');n=prior.probe(ck,label+'_nominal',profile='nominal')
    tracking=[target_evidence(r,4*math.pi) for r in (w,n)]
    target_confirmed=bool(target_confirmed and all(x['pass_'] for x in tracking))
    result=dict(checkpoint=base.checkpoint(ck),cap=rate.current_limit(),profile='white_v2',
        acceptance_version=VERSION,outcome=outcome,target_2rev_s_confirmed=target_confirmed,
        target_tracking_evidence=tracking,flat=assess_flat(f),spin_active_DR=assess(w),spin_nominal=assess(n),
        original_flat_admission=rate.assess(f),original_spin_active_DR=ctl.spin.compact_spin(w),
        original_spin_nominal=ctl.spin.compact_spin(n),actual_budget=base.budget_state(),
        curriculum_qualification_is_not_target_achievement=True,real_robot_certified=False)
    base.atomic_json(ctl.REPORTS/'AUTONOMY_FINISHED.json',result)
    status('finished',training_pid=None,evaluation_pid=None,validation_pid=None,final_evaluation=result,outcome=outcome)

def controller():
    assert not J.exists(),'One-shot already started; inspect state, never rerun'
    ctl.S=read(ctl.STATE_PATH);ctl.idle();repair.verify()
    helpers.acquire(P/'autonomy_controller.lock');helpers.acquire(ctl.CANONICAL.parent/'native_floor_supervisor.lock')
    hand=read(HAND);assert hand['stage']=='completed' and hand['acceptance_version']==VERSION
    assert base.sha(ctl.CANONICAL)==hand['frozen_ledger_sha256']
    assert not base.budget_state().get('active_segment') and not ctl.S.get('active_training')
    assert not base.trainers() and not helpers.active_processes(ctl.PROBES)
    for expected in hand['retired_processes']:
        assert helpers.identity(expected) is None
    old=read(R/'SCUT_FINE_RATE_STATE.json')
    assert old['phase']=='repair_hold' and old['last_validated_source']==hand['last_paired_mature']
    ck=Path(hand['checkpoint']['path']);assert base.checkpoint(ck)==hand['checkpoint']
    assert ctl.S['chosen_checkpoint']==str(ck) and rate.current_limit()==10.
    assert ctl.S['mature']==hand['last_paired_mature']
    assert base.budget_state()['authorized_training_seconds']==324000==hand['budget_authorized']
    pair=read(Path(hand['reused_10_pair_path']))
    assert base.sha(Path(hand['reused_10_pair_path']))==hand['reused_10_pair_sha256']
    assert pair['pass_'] and pair['checkpoint']==hand['checkpoint'] and pair['cap']==10.
    assert len(pair['pairs'])==4 and all(row['initial_root_q_exact'] and all(x['pass_'] for x in row['admission']) for row in pair['pairs'])
    rejected=read(R/'SCUT_CURRICULUM_V4_CAP12.5664_PREFLIGHT.json')
    assert rejected['pass_'] is False and rejected['source']==hand['checkpoint']
    assert read(R/'SCUT_FINE_RATE_CAP11_PREFLIGHT.json')['pass_'] is False
    last=hand['last_paired_mature'];owner=helpers.identity(os.getpid())
    phase('fine_rate_continuation',owner=owner,checkpoint=base.checkpoint(ck),cap=rate.current_limit(),
        last_validated_source=last,route=[10.,10.5,11.,12.,4*math.pi],
        policy_reward_DR_hardware_physics_PPO_unchanged=True,prior_rejections=ctl.S['rate_rejected'],
        old_target_failure_retained=True,completed10_pairs_reused_not_replayed=True,
        qualification_method='Same v4 actual task/model/data gate and bounded exposure; smaller rate-only steps.')
    with (C/'guardian_scut_half_rate.log').open('x') as log:
        g=subprocess.Popen([base.PY,str(C/'supervise_scut_half_rate_continue.py'),'--guardian',str(os.getpid()),str(owner['start_ticks'])],
            cwd=P,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    base.atomic_json(R/'SCUT_HALF_RATE_GUARDIAN_STARTED.json',helpers.identity(g.pid))
    if not preflight(ck,10.5,last):return
    exposure=0;duration=2700
    while ctl.remaining()>120:
        if duration>0:
            began=time.time();phase('bounded_rate_learning',cap=rate.current_limit(),source=base.checkpoint(ck),
                duration_s=min(duration,ctl.remaining()),effective_cap_exposure_s=exposure,last_validated_source=last)
            ck=ctl.training(ck,'scut_v4_rate_learning',duration=min(duration,ctl.remaining()))
            exposure+=time.time()-began
        phase('rate_learning_assessment',cap=rate.current_limit(),checkpoint=base.checkpoint(ck),effective_cap_exposure_s=exposure)
        if not decision(ck):hold(last,'Actual task/model/data failure in latest formal flat/spin regression');return
        if exposure>=2700 and ctl.remaining()>120:
            if not pairs(ck,ctl.fresh_label('scut_v4_paired_regression')):
                hold(last,'Actual task/model/data or paired reset/parameter regression failure');return
            last=dict(checkpoint=str(ck),cap=rate.current_limit(),profile='white_v2')
            ctl.S['mature']=last;ctl.S['chosen_checkpoint']=str(ck);ctl.persist()
            base.atomic_json(R/(ctl.fresh_label('scut_v4_curriculum_accepted')+'.json'),dict(
                checkpoint=base.checkpoint(ck),cap=rate.current_limit(),acceptance_version=VERSION,
                effective_cap_exposure_s=exposure,learning_admission_only=True,
                target_achievement_not_assumed=True,two_formal_policies_required=False))
            target=transition.next_limit(rate.current_limit())
            if target is None:
                if len(PAIRED_TARGET)==4 and all(x['pass_'] for x in PAIRED_TARGET):
                    finish(ck,'Requested signed4pi rate confirmed on two-seed nominal/white paired and final reports',True);return
                phase('target_tracking_learning',target_cap=rate.current_limit(),
                    actual_target_tracking=PAIRED_TARGET,target_not_yet_achieved=True)
                duration=min(7200,ctl.remaining());continue
            if not preflight(ck,target,last):return
            exposure=0;duration=2700;continue
        duration=min(max(1,2700-exposure),ctl.remaining())
        if duration<=120:break
    finish(ck,'Effective canonical budget reached; report measured capability and all legacy diagnostics',False)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--guardian',nargs=2,type=int);a=p.parse_args()
    if a.guardian:repair.guardian(*a.guardian);raise SystemExit
    __import__('torch').set_num_threads(1);base.STATE.update(read(P/'status.json'))
    try:controller()
    except BaseException:
        status('attention_required',error=traceback.format_exc(),instructions='Protect actual children/complete weights/ledger. Never rerun entry/migration or duplicate trainer.');raise
