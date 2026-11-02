"""Explicit bounded rolling adaptation, then measured rate progression.

Execution lives in one candidate; status/logs and the sole budget remain attached
to the existing production root. No old one-shot supervisor is invoked.
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import traceback
from pathlib import Path

D = Path(__file__).resolve().parent
ROOT = Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002')
CODE = D / 'isaac/mod4'
R = D / 'reports'
sys.path.insert(0, str(ROOT / 'isaac/mod4'))
import supervise_autonomy as ctl
base, rate, spin, helpers = ctl.base, ctl.rate, ctl.spin, ctl.helpers
ctl.CODE = rate.CODE = spin.CODE = CODE
ctl.PROBES = tuple(ctl.PROBES) + ('/rolling_readback_probe.py',)
spin.PROBES = ctl.PROBES
read = ctl.read
F = R / 'SOURCE_FREEZE.json'
J = R / 'REPAIR_STATE.json'
ORIGINAL = '/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/logs/2026-10-03_22-54-58_auto_0035_autonomous_continued_cap5_white_v2/model_17039.pt'
ORIGINAL_SHA = '253ed8effd5fe8580859bce1b7731006ae62a5e7bf1c63a9f8825de2c74bc73e'
VERSION = 'rolling_repair_v1_bounded'


def verify():
    b = base.budget_state()
    assert b['owner_root'] == str(ROOT) and b['authorized_training_seconds'] == __import__('budget_authority').validate_budget(b)
    for name, digest in read(ROOT/'reports/SPIN_SOURCE_FREEZE.json')['sha256'].items():
        p = Path(name); p = p if p.is_absolute() else ROOT/p
        assert base.sha(p) == digest, 'Original production source drift: '+name
    for name, digest in read(F)['sha256'].items():
        assert base.sha(D/name) == digest, 'Rolling candidate source drift: '+name
    cfg = read(CODE/'env.json')
    assert cfg['RM_MILD_DR_PROFILE'] == 'white_v2' and cfg['RM_SPIN_ROLLING_PROFILE'] in ('v1','off')
    assert cfg['RM_KEEP_STD'] == '1' and cfg['RM_CONTACT_INTEGRATED'] == '1'
    assert cfg['RM_CONTACT_EAGER5MS'] == '1' and cfg['RM_FLAT_NATIVE_PLANE'] == '1'
    assert cfg['RM_DR_OFF'] == '1' and cfg['RM_SOLVER_POS'] == '16' and cfg['RM_SOLVER_VEL'] == '4'
    assert cfg['RM_GYRO_CURRICULUM'] == '0' and cfg['RM_HEADING_CMD'] == '0'
    assert float(cfg['RM_SPIN_FRACTION']) == .3 and float(cfg['RM_REL_STANDING']) == .1
    assert float(cfg['RM_NOMINAL_HEIGHT']) == .25 and float(cfg['RM_CMD_VX_MAX']) == 1.5 and float(cfg['RM_CMD_VX_MIN']) == -1.5
    rate.current_limit()


def runtime():
    cfg = read(CODE/'env.json')
    env = {k:v for k,v in os.environ.items() if not k.startswith('RM_')}
    env.update({k:str(v) for k,v in cfg.items()})
    env.update(ISAACSIM_ACCEPT_EULA='Y', OMNI_KIT_ACCEPT_EULA='YES', PYTHONUNBUFFERED='1')
    return env


def status(stage=None, **kw):
    b = base.budget_state()
    kw.pop('scope', None)
    kw.pop('budget_seconds', None); kw.pop('authorized_training_seconds', None)
    base.status(**({'stage':stage} if stage else {}), supervisor_pid=os.getpid(),
        canonical_budget=str(ctl.CANONICAL), budget_seconds=b['authorized_training_seconds'],
        authorized_training_seconds=b['authorized_training_seconds'], profile='white_v2',
        yaw_limit_rad_s=rate.current_limit(), autonomy_version=VERSION,
        rolling_repair_state=str(J), active_code_root=str(D),
        rolling_profile=read(CODE/'env.json')['RM_SPIN_ROLLING_PROFILE'],
        scope='One explicit contact reward adaptation at cap5, then separate measured rate steps; original gates/hardware/DR unchanged', **kw)


def freeze_run(run):
    target = run/'rolling_source_freeze.json'
    if target.exists(): return
    dest = run/'rolling_source_snapshot'
    for name, digest in read(F)['sha256'].items():
        p = D/name
        assert base.sha(p) == digest
        q = dest/name; q.parent.mkdir(parents=True, exist_ok=True)
        assert q.resolve().is_relative_to(dest.resolve()) and q.resolve() != p.resolve()
        shutil.copy2(p,q)
    base.atomic_json(target, dict(sha256=read(F)['sha256'], candidate_root=str(D),
        canonical_budget=str(ctl.CANONICAL), only_added_contact_reward=True,
        physics_hardware_PPO_DR_unchanged=True))


def config_update(**changes):
    ctl.idle(); cfg = read(CODE/'env.json'); cfg.update(changes)
    base.atomic_json(CODE/'env.json',cfg)
    f = read(F); f['sha256']['isaac/mod4/env.json'] = base.sha(CODE/'env.json')
    base.atomic_json(F,f)


def set_limit(value, reason):
    rate.validate_limit(value)
    old = rate.current_limit()
    config_update(RM_SPIN_MAX_RAD_S=repr(value))
    base.atomic_json(R/(ctl.fresh_label('rate_change')+'.json'),
        dict(old=old, new=value, reason=reason, reward_DR_hardware_unchanged=True, history_rejections=ctl.S['rate_rejected']))


ctl.verify = verify
ctl.runtime = runtime
base.runtime_env = runtime
spin.runtime = runtime
ctl.status = spin.status = status
rate.freeze_run = spin.freeze_run = freeze_run
rate.set_limit = set_limit


def phase(name, **kw):
    x = read(J) if J.exists() else {}
    x.update(phase=name, updated_epoch=time.time(), **kw)
    base.atomic_json(J,x)
    ctl.S['rolling_repair'] = x; ctl.persist()


def hold(ck, cap, reason, disable=False):
    ctl.idle()
    set_limit(cap, reason)
    if disable: config_update(RM_SPIN_ROLLING_PROFILE='off')
    ctl.S['chosen_checkpoint'] = str(ck); ctl.S['active_training'] = None; ctl.persist()
    phase('repair_hold', reason=reason, checkpoint=base.checkpoint(ck), rate_cap=cap)
    status('targeted_repair_hold', training_pid=None, evaluation_pid=None, validation_pid=None,
        latest_checkpoint=str(ck), targeted_repair=read(J))


def frozen_input_pair(ck):
    b = ctl.CANONICAL.read_bytes(); reports = []
    for profile in ('off','v1'):
        ctl.idle(); verify()
        out = R/('reward_input_'+profile+'.json'); assert not out.exists()
        args=[str(CODE/'rolling_readback_probe.py'),'--headless','--checkpoint',str(ck),
              '--output',str(out),'--steps','300','--num_envs','22','--seed','20261002',
              '--max-rate','5','--dr-profile','white_v2','--rolling-profile',profile]
        p=base.spawn(args,out.with_suffix('.log'));ctl.LIVE=p
        status('rolling_reward_input_readback', evaluation_pid=p.pid, training_pid=None, active_log=str(out.with_suffix('.log')))
        r=base.wait_probe(p,out);ctl.LIVE=None
        assert r['physical_smoke_pass'] and ctl.safety_veto(r) and all(r['alive']) and not r['nonfinite']
        assert r['initial_parameter_audit']['actual_parameters_pass'] and r['final_parameter_audit']['actual_parameters_pass']
        reports.append(r)
    a,bp=reports
    assert all(a[k]==bp[k] for k in ('reset_joint_pos_before_physics','reset_root_before_physics','per_environment','group_ids','alive'))
    import torch
    for off,on in zip(a['rolling_input_readback']['samples'],bp['rolling_input_readback']['samples']):
        assert off['step']==on['step']
        cost=torch.tensor(on['cost'])
        expected=-.3*.01*cost
        observed=torch.tensor(on['total_reward'])-torch.tensor(off['total_reward'])
        assert torch.allclose(observed,expected,atol=2e-6,rtol=1e-4),'Actual reward delta does not match registered term'
        assert torch.isfinite(cost).all() and (cost>=0).all() and (cost<=4.25+1e-6).all()
        assert any(on['enabled'])
        assert all(cost[i]==0 for i,g in enumerate(bp['group_ids']) if g<7)
    assert ctl.CANONICAL.read_bytes()==b
    receipt=dict(pass_=True, source=base.checkpoint(ck), frozen_input_root_q_behavior_exact=True,
        actual_reward_delta_verified=True, profile_fixed='white_v2', cap_fixed=5, ledger_bytes_exact=True,
        old_skill_booleans_retained=True, no_PPO=True)
    base.atomic_json(R/'REWARD_INPUT_PAIR_PASSED.json',receipt)
    status(evaluation_pid=None)


def preflight_rate(ck,target):
    previous=rate.current_limit()
    set_limit(target,'Explicit isolated rate step after current-cap reward/skill verification')
    try:
        short=ctl.probe(ck,ctl.fresh_label('rolling_rate_short'),steps=300)
        assert short['physical_smoke_pass'] and ctl.safety_veto(short)
        ctl.fullscale(ck,ctl.fresh_label('rolling_rate_physics'))
        ctl.training(ck,'rolling_rate128_discard',count=128,iterations=2,duration=600)
        return True
    except BaseException:
        if base.trainers() or base.budget_state().get('active_segment'): raise
        error=traceback.format_exc()
        base.atomic_json(R/('RATE'+str(target)+'_PREFLIGHT_REJECTED.json'),dict(error=error,source=base.checkpoint(ck)))
        set_limit(previous,'Retain previous measured cap; preflight rejection')
        return False


def controller():
    assert not J.exists(),'One-shot already began; inspect exact phase/children/budget before an explicit recovery'
    ctl.S=read(ctl.STATE_PATH);ctl.idle();verify()
    assert ctl.S['mature']==dict(checkpoint=ORIGINAL,cap=5.0,profile='white_v2')
    assert base.checkpoint(Path(ORIGINAL))['sha256']==ORIGINAL_SHA and 6 in ctl.S['rate_rejected']
    assert read(ROOT/'status.json')['stage']=='targeted_repair_hold'
    helpers.acquire(ROOT/'autonomy_controller.lock');helpers.acquire(ctl.CANONICAL.parent/'native_floor_supervisor.lock')
    ctl.S['profile']='white_v2';ctl.persist()
    owner=helpers.identity(os.getpid())
    phase('frozen_inputs', owner=owner, original_source=base.checkpoint(Path(ORIGINAL)), historical_rejections=ctl.S['rate_rejected'],
          user_authorized_target='repair6_then_continue_rate_steps', budget_added=False)
    with (D/'guardian.log').open('x') as log:
        g=subprocess.Popen([base.PY,str(D/'supervise_rolling_repair.py'),'--guardian',str(os.getpid()),str(owner['start_ticks'])],
            cwd=ROOT,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    base.atomic_json(R/'GUARDIAN_STARTED.json',helpers.identity(g.pid))
    ck=Path(ORIGINAL)
    try:
        frozen_input_pair(ck)
        phase('physical_and_PPO_preflight5')
        ctl.fullscale(ck,ctl.fresh_label('rolling_fixed5_physics'))
        ctl.training(ck,'rolling128_discard',count=128,iterations=2,duration=600)
        ctl.training(ck,'rolling20k_discard',count=20000,iterations=4,duration=900)
        phase('reward_adaptation5_trial45', original_source=base.checkpoint(ck))
        trial=ctl.training(ck,'rolling_adaptation5_trial45',duration=2700)
        phase('reward_adaptation5_paired_assessment', checkpoint=base.checkpoint(trial))
        if not ctl.pairs(trial,ctl.fresh_label('rolling_adaptation5_multiseed'),('nominal','white_v2')):
            hold(ck,5,'Contact reward trial failed original5/flat regression; all new policies retained',disable=True);return
        ck=trial
        ctl.S['mature']=dict(checkpoint=str(ck),cap=5.,profile='white_v2');ctl.S['chosen_checkpoint']=str(ck);ctl.persist()
        base.atomic_json(R/'ROLLING_REWARD_ACCEPTED.json',dict(source=base.checkpoint(Path(ORIGINAL)),
            accepted=base.checkpoint(ck), cap=5, profile='white_v2', original_gates_unchanged=True,
            no_rate6_skill_claim=True))
    except BaseException:
        if base.trainers() or base.budget_state().get('active_segment'):raise
        base.atomic_json(R/'ROLLING_REWARD_PRETRIAL_REJECTED.json',dict(error=traceback.format_exc(),source=base.checkpoint(Path(ORIGINAL))))
        hold(Path(ORIGINAL),5,'Isolated reward/physical/PPO preflight rejected; preserve mature source and all evidence',disable=True)
        return
    # Historical6 rejection remains; this is ONE explicit retry with a newly tested reward.
    phase('explicit6_repair_preflight', source=base.checkpoint(ck), rejection_history_retained=True)
    if not preflight_rate(ck,6.):
        hold(ck,5,'Explicit repaired6 preflight rejected; no blind old-entry resume');return
    last_mature=dict(checkpoint=str(ck),cap=5.,profile='white_v2')
    consecutive=0;failures=0;last_sha=None
    duration=2700
    while ctl.remaining()>120:
        phase('rate_trial_or_continued',cap=rate.current_limit(), source=base.checkpoint(ck), last_paired_mature=last_mature)
        ck=ctl.training(ck,'rolling_rate_trial_or_continued',duration=min(duration,ctl.remaining()))
        phase('rate_assessment', cap=rate.current_limit(),checkpoint=base.checkpoint(ck))
        physical,skilled=ctl.current_decision(ck)
        current=base.checkpoint(ck)
        if not physical:
            hold(Path(last_mature['checkpoint']),last_mature['cap'],'Physical/flat regression during new-rate learning');return
        different=current['sha256']!=last_sha;last_sha=current['sha256']
        consecutive=(consecutive+int(different)) if skilled else 0
        failures=0 if skilled else failures+1
        phase('rate_assessed',cap=rate.current_limit(),consecutive=consecutive,failed_blocks=failures,checkpoint=current)
        if failures>=3:
            ctl.S['rate_rejected']=list(dict.fromkeys(ctl.S['rate_rejected']+[rate.current_limit()]));ctl.persist()
            hold(Path(last_mature['checkpoint']),last_mature['cap'],'Three original skill failures in targeted rate trial; preserve all policies');return
        if consecutive>=2 and ctl.remaining()>3600:
            if ctl.pairs(ck,ctl.fresh_label('rolling_rate_mature_multiseed'),('nominal','white_v2')):
                last_mature=dict(checkpoint=str(ck),cap=rate.current_limit(),profile='white_v2')
                ctl.S['mature']=last_mature;ctl.persist()
                base.atomic_json(R/(f'RATE{rate.current_limit():g}_MATURE_ACCEPTED.json'),dict(
                    checkpoint=current,cap=rate.current_limit(),profile='white_v2',two_different_policy_assessments=True,
                    two_seed_nominal_DR_paired=True,historical_rejections_retained=True,real_robot_certified=False))
                target=rate.next_limit(rate.current_limit())
                if target is None:
                    phase('target_rate_accepted',checkpoint=current)
                    ctl.finish(ck,'Measured target4pi accepted; budget not automatically extended')
                    return
                if target in ctl.S['rate_rejected'] or not preflight_rate(ck,target):
                    hold(ck,last_mature['cap'],'Next rate rejected; no repeated mature-cap PPO');return
                consecutive=0;failures=0;last_sha=None;duration=2700
                continue
            consecutive=0;failures+=1
        duration=7200
    phase('budget_final_assessment',checkpoint=base.checkpoint(ck))
    ctl.finish(ck,'Effective canonical budget reached; report original capability/failure metrics')


def guardian(owner,ticks):
    while True:
        now=helpers.identity(owner)
        if not now or now['state']=='Z' or now['start_ticks']!=ticks:return
        b=base.budget_state();a=b.get('active_segment')
        if a:
            rem=b['authorized_training_seconds']-b['charged_training_seconds']-max(0,time.time()-a['accounted_through_epoch'])
            if rem<=0:
                ident=helpers.identity(a['pid'])
                if ident and ident['cwd']==str(ROOT) and str(CODE/'train_mod4_ppo.py') in ident['argv']:
                    status_now=read(ROOT/'status.json')
                    for folder in (ROOT/'logs',ROOT/'autonomy_preflight_logs'):
                        try:run=rate.trainer_run(folder,a['pid'])
                        except AssertionError:continue
                        p=run/'STOP_AFTER_SAVE'
                        if not p.exists():p.write_text('Canonical budget exhausted; complete save then exit.\n')
        time.sleep(15)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--guardian',nargs=2,type=int);a=p.parse_args()
    if a.guardian:guardian(*a.guardian);sys.exit()
    __import__('torch').set_num_threads(1)
    base.STATE.update(read(ROOT/'status.json'))
    try:controller()
    except BaseException:
        status('attention_required',error=traceback.format_exc(),instructions='Preserve exact children/state/budget; do not repeat one-shot repair entry or start a second trainer.')
        raise
