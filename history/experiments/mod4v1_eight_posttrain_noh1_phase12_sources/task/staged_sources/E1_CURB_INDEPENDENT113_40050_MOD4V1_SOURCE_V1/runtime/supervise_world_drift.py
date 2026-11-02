"""One explicit saved-boundary continuation of .5 world-spin with one reward.

Retain SCUT v4 decisions, actual world target facts, the sole canonical budget,
and independent supervision. Never invokes a historical controller entry.
"""
import hashlib,json,os,shutil,subprocess,time,traceback
from pathlib import Path
import supervise_world_spin as w
import torch
D=w.D;R=w.R;P=w.P;ctl=w.ctl;base=w.base;helpers=w.helpers
original_verify=w.verify
def verify():
    original_verify()
    cfg=w.read(w.CODE/'env.json')
    assert cfg['RM_WORLD_DRIFT_PROFILE']=='cycle_v1'
    assert float(cfg['RM_SPIN_WORLD_PROGRESS_M_S'])==.5
def freeze_run(run):
    out=run/'rolling_source_freeze.json'
    if out.exists():return
    dst=run/'world_source_snapshot'
    f=w.read(w.F)
    for n,h in f['sha256'].items():
        assert base.sha(D/n)==h
        q=dst/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(D/n,q)
    base.atomic_json(out,dict(candidate_root=str(D),sha256=f['sha256'],acceptance_version=w.VERSION,
        lesson='world_directional_spin',world_goal_m_s=.5,world_drift_reward_version='phase_compensated_cycle_cross_v1',
        world_drift_weight=-.3,world_drift_scale_m_s=.10,world_drift_max_cost=4.,
        other_rewards_DR_hardware_physics_PPO_observations_reset_unchanged=True))
w.verify=ctl.verify=verify;w.rate.freeze_run=freeze_run
ctl.PROBES=tuple(ctl.PROBES)+('/world_drift_readback_probe.py',);ctl.spin.PROBES=ctl.PROBES

def reward_readback(ck,reuse_completed_off=False):
    paths=[]
    for profile in ('off','cycle_v1'):
        ctl.idle();verify()
        out=R/('REWARD_READBACK_'+profile+'.json')
        reused=bool(reuse_completed_off and profile=='off' and out.exists())
        assert reused or not out.exists()
        argv=[str(w.CODE/'world_drift_readback_probe.py'),'--headless','--checkpoint',str(ck),
              '--output',str(out),'--num_envs','22','--steps','1500','--seed','20261002',
              '--max-rate',str(4*__import__('math').pi),'--dr-profile','white_v2',
              '--contact-readback','--drift-profile',profile]
        if reused:
            result=w.read(out)
            assert result['checkpoint']==str(ck) and result['probe_sha256']==base.sha(w.CODE/'world_drift_readback_probe.py')
        else:
            child=base.spawn(argv,out.with_suffix('.log'));ctl.LIVE=child
            w.phase('frozen_reward_readback',profile=profile,child=helpers.identity(child.pid),output=str(out))
            w.status('world_drift_reward_readback',training_pid=None,evaluation_pid=child.pid,validation_pid=None,active_log=str(out.with_suffix('.log')))
            result=base.wait_probe(child,out);ctl.LIVE=None
        # This is a 22-env reward audit (two/group), not an 88-env graduation.
        # Preserve the same fault/data checks and explicitly require all 15s.
        assert result['steps']==1500 and result['seconds']==15 and len(result['alive'])==22
        verdict=w.evidence(result,'spin',3.);assert verdict['pass_'],verdict
        assert result['reward_readback_error']<1e-4
        assert result['world_drift_reward_audit']['term_present']==(profile=='cycle_v1')
        paths.append(out)
    import numpy as np
    off,on=[w.read(p) for p in paths]
    for key in ('reset_joint_pos_before_physics','reset_root_before_physics','initial_parameter_audit','final_parameter_audit'):
        assert off[key]==on[key],key
    traces=[np.load(p.with_suffix('.npz')) for p in paths]
    exact={k:bool(np.array_equal(traces[0][k],traces[1][k])) for k in ('root_xy','heading','actions','commands','joint_pos','group_ids','first_failure')}
    assert all(exact.values()),exact
    expected=-.3*traces[1]['cost']*.01
    delta=traces[1]['reward']-traces[0]['reward']
    err=float(np.max(np.abs(delta-expected)));assert err<2e-6,err
    assert np.isfinite(traces[1]['cost']).all() and np.max(traces[1]['cost'])<=4
    inactive=traces[1]['group_ids']<3;assert np.all(traces[1]['cost'][:,inactive]==0)
    assert on['world_drift_reward_audit']['cached_updates']==1500
    receipt=dict(pass_=True,source=base.checkpoint(ck),paths=[str(p) for p in paths],behavior_exact=exact,
        actual_reward_delta_formula_error=err,nonmoving_cost_zero=True,one_update_per_control_step=True,
        old_acceptance_booleans_retained=True,budget_bytes_exact=True)
    base.atomic_json(R/'REWARD_READBACK_PASSED.json',receipt)
    w.status(evaluation_pid=None,validation_pid=None,reward_readback=receipt)

def controller(reuse_completed_off=False):
    if reuse_completed_off:
        review=w.read(R/'READBACK_PROTOCOL_REVIEW.json')
        assert review['only_readback_group_count_contract_corrected'] and review['completed_off_reused']
        assert w.read(w.STATE)['phase']=='repair_hold'
    else:
        assert not w.STATE.exists(),'Explicit drift entry already ran; inspect state, never rerun'
    torch.set_num_threads(1)
    ctl.S=w.read(ctl.STATE_PATH);base.STATE.update(w.read(P/'status.json'))
    ctl.idle();verify();helpers.acquire(P/'autonomy_controller.lock');helpers.acquire(ctl.CANONICAL.parent/'native_floor_supervisor.lock')
    hand=w.read(R/'REWARD_HANDOVER.json');ck=Path(hand['checkpoint']['path']);last=ck
    actual_source=base.checkpoint(ck)
    assert all(actual_source[k]==hand['checkpoint'][k] for k in ('path','sha256','iteration_stored','finite_tensors'))
    for person in hand['retired']:
        actual=helpers.identity(person['pid']);assert not actual or actual.get('state')=='Z' or actual['start_ticks']!=person['start_ticks']
    w.phase('world_drift_preflight',source=hand['checkpoint'],owner=helpers.identity(os.getpid()),goal_m_s=.5,
        reward_version='phase_compensated_cycle_cross_v1',last_validated_source=hand['checkpoint'])
    with (D/('guardian_world_drift_readback_review.log' if reuse_completed_off else 'guardian_world_drift.log')).open('x') as log:
        g=subprocess.Popen([base.PY,str(D/'supervise_world_drift.py'),'--guardian',str(os.getpid()),str(helpers.identity(os.getpid())['start_ticks'])],
            cwd=P,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    base.atomic_json(R/'REWARD_GUARDIAN_STARTED.json',helpers.identity(g.pid))
    try:
        ledger_sha=base.sha(ctl.CANONICAL)
        reward_readback(ck,reuse_completed_off)
        assert base.sha(ctl.CANONICAL)==ledger_sha,'Frozen readback must not charge PPO time'
        w.probe(ck,'20k',steps=120,count=20000)
        baseline=w.regression(ck)
        assert base.sha(ctl.CANONICAL)==ledger_sha
        base.atomic_json(R/'REWARD_BASELINE_PASSED.json',dict(source=hand['checkpoint'],baseline=baseline,ledger_bytes_exact=True))
        ctl.training(ck,'world_drift_128_discard',count=128,iterations=2,duration=600)
        ctl.training(ck,'world_drift_20k_discard',count=20000,iterations=4,duration=600)
        duration=2700
        while ctl.remaining()>120:
            w.phase('bounded_world_drift_learning',goal_m_s=.5,source=base.checkpoint(ck),duration_s=min(duration,ctl.remaining()))
            ck=ctl.training(ck,'world_drift_learning',duration=min(duration,ctl.remaining()))
            w.regression(ck);worlds,path=w.paired(ck);last=ck
            w.phase('world_drift_paired_learning_accepted',checkpoint=base.checkpoint(ck),paired_path=path,
                    target_confirmed=all(x['pass_'] for x in worlds),learning_admission_only=True,last_validated_source=base.checkpoint(last))
            if all(x['pass_'] for x in worlds):
                w.finish(ck,'Actual .5 world-directed progress and retained skills verified after isolated drift reward',worlds);return
            duration=min(7200,ctl.remaining())
        w.finish(ck,'Remaining effective budget below safe block threshold; target not assumed')
    except BaseException:
        w.hold(last,traceback.format_exc());raise

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--guardian',nargs=2);p.add_argument('--readback-review-continuation',action='store_true');a=p.parse_args()
    if a.guardian:w.guardian(int(a.guardian[0]),a.guardian[1])
    else:controller(a.readback_review_continuation)
