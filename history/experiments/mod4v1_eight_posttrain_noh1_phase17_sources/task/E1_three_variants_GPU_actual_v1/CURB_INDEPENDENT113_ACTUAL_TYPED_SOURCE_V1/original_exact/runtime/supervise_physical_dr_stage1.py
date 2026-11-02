"""One authorized physical DR step, same tasks and sole budget, then saved review.

Finite performance remains diagnostic. Task/model/data failures preserve all
weights and restore the validated source/profile. No old entry is invoked.
"""
import argparse,math,os,shutil,subprocess,time,traceback
from pathlib import Path
import supervise_world_spin as w
from physical_dr_contract import parameter_readback,paired_review,compact_worlds
D,R,P,ctl,base,helpers=w.D,w.R,w.P,w.ctl,w.base,w.helpers
w.STATE=R/'PHYSICAL_DR_STATE.json'
VERSION='physical_dr_stage1_scut_v4_bounded_saved_review'
PROFILE='white_v3'
ENTRY=D/'supervise_physical_dr_stage1.py'
original_status=w.status

def verify():
    b=base.budget_state();assert b['owner_root']==str(P)
    for n,h in w.read(P/'reports/SPIN_SOURCE_FREEZE.json')['sha256'].items():
        p=Path(n);p=p if p.is_absolute() else P/p;actual=base.sha(p)
        if actual!=h:
            ui=w.read(R/'DISPLAY_SOURCE_REVIEW.json')
            assert n==ui['path']=='isaac/mod4/tui_spin_rate.py' and h==ui['original_sha256'] and actual==ui['approved_sha256'] and ui['only_evaluation_panel_changed'] is True
    for n,h in w.read(w.F)['sha256'].items():assert base.sha(D/n)==h,n
    assert base.sha(R/'BASE_ENV.json')==w.read(w.F)['base_env_sha256']
    cfg=w.read(w.CODE/'env.json');original=w.read(R/'BASE_ENV.json')
    assert set(cfg)==set(original)
    assert all(cfg[k]==v for k,v in original.items() if k!='RM_MILD_DR_PROFILE'),'Only physical DR profile may change'
    assert cfg['RM_MILD_DR_PROFILE'] in ('white_v2',PROFILE)
    assert cfg['RM_WORLD_DRIFT_PROFILE']=='cycle_v1' and cfg['RM_KEEP_STD']=='1'
    assert float(cfg['RM_SPIN_MAX_RAD_S'])==4*math.pi and float(cfg['RM_SPIN_WORLD_PROGRESS_M_S'])==.5

def status(stage=None,**kw):
    kw.setdefault('profile',w.read(w.CODE/'env.json')['RM_MILD_DR_PROFILE'])
    kw.update(autonomy_version=VERSION,controller_version=VERSION,lesson='physical_dr_stage1',
              dr_engineering_stress_range_not_calibrated=True,
              scope='One independently validated physical DR step on fixed learned tasks; finite performance diagnostics, actual model/task/data checks, and original hardware limits preserved.')
    original_status(stage,**kw)

def freeze_run(run):
    out=run/'rolling_source_freeze.json'
    if out.exists():return
    f=w.read(w.F)
    for n,h in f['sha256'].items():
        assert base.sha(D/n)==h
        q=run/'physical_dr_source_snapshot'/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(D/n,q)
    base.atomic_json(out,dict(candidate_root=str(D),sha256=f['sha256'],acceptance_version=w.VERSION,
        controller_version=VERSION,lesson='physical_dr_stage1',physical_dr_profile=w.read(w.CODE/'env.json')['RM_MILD_DR_PROFILE'],
        world_goal_m_s=.5,world_drift_reward_version='phase_compensated_cycle_cross_v1',
        only_physical_dr_profile_changed=True,tasks_commands_rewards_hardware_physics_PPO_observations_reset_unchanged=True))

w.verify=ctl.verify=verify;w.status=ctl.status=status;w.rate.freeze_run=freeze_run

def set_profile(profile):
    ctl.idle();cfg=w.read(w.CODE/'env.json');cfg['RM_MILD_DR_PROFILE']=profile;base.atomic_json(w.CODE/'env.json',cfg)
    f=w.read(w.F);f['sha256']['isaac/mod4/env.json']=base.sha(w.CODE/'env.json');base.atomic_json(w.F,f)
    ctl.S['profile']=profile;ctl.persist();verify()

def probe(ck,kind,profile=PROFILE,seed=20261002,steps=1500,count=None):
    result,path=w.probe(ck,kind,profile,seed,steps,count)
    parameter_readback(result,profile,kind)
    return result,path

def regression(ck):
    paths={}
    for kind in ('flat','spin','world'):
        r,p=probe(ck,kind);paths[kind]=str(p)
    return paths

def paired(ck):
    pairs=[]
    profiles=('nominal','white_v2',PROFILE)
    for seed in (20261002,20261003):
        for kind in ('flat','spin','world'):
            rs=[probe(ck,kind,profile,seed) for profile in profiles]
            pairs.append(dict(seed=seed,kind=kind,paths=[str(p) for _,p in rs]))
    result=paired_review(pairs,lambda p:w.read(Path(p)),w.assess_flat,w.evidence,w.target,base.checkpoint(ck),profiles)
    result.update(pairs=pairs,profile=PROFILE,learning_admission_only=True,world_summary=compact_worlds(result['world_tracking']))
    out=ctl.REPORTS/(ctl.fresh_label('physical_dr_three_profile_paired')+'.json');base.atomic_json(out,result)
    return result,str(out)

def guardian(owner,ticks):
    while True:
        p=helpers.identity(owner);b=base.budget_state();a=b.get('active_segment')
        if a:
            remaining=b['authorized_training_seconds']-b['charged_training_seconds']-max(0,time.time()-a['accounted_through_epoch'])
            trainer=helpers.identity(a['pid'])
            if remaining<=0 and trainer and trainer['cwd']==str(P) and str(w.CODE/'train_mod4_ppo.py') in trainer['argv']:
                run=w.rate.trainer_run(P/'logs',trainer['pid']);stop=run/'STOP_AFTER_SAVE'
                if not stop.exists():stop.write_text('Canonical budget exhausted: complete full atomic save and stop.\n')
        if not a and ((R/'PHYSICAL_DR_STAGE1_REVIEW_READY.json').exists() or not p or str(p['start_ticks'])!=str(ticks)):return
        time.sleep(15)

def controller():
    marker=R/'PHYSICAL_DR_STARTED.json'
    assert not marker.exists() and not w.STATE.exists(),'Entry already executed; inspect actual receipt'
    ctl.S=w.read(ctl.STATE_PATH);base.STATE.update(w.read(P/'status.json'))
    ctl.idle();verify();helpers.acquire(P/'autonomy_controller.lock');helpers.acquire(ctl.CANONICAL.parent/'native_floor_supervisor.lock')
    hand=w.read(R/'PHYSICAL_DR_HANDOVER.json');close=w.read(R/'WORLD_LESSON_PRACTICAL_CLOSEOUT.json')
    assert close['practical_progression_authorized'] and close['practical_closeout_accepted']
    for person in hand['retired']:
        actual=helpers.identity(person['pid']);assert not actual or actual['state']=='Z' or actual['start_ticks']!=person['start_ticks']
    source=Path(hand['selected_validated_source']['path']);info=base.checkpoint(source)
    assert all(info[k]==hand['selected_validated_source'][k] for k in ('path','sha256','iteration_stored','finite_tensors'))
    assert info['sha256']==close['checkpoint']['sha256'] and base.budget_state()['active_segment'] is None
    base.atomic_json(marker,dict(parent=helpers.identity(os.getpid()),source=info,profile=PROFILE,controller_version=VERSION))
    with (D/'guardian_physical_dr.log').open('x') as log:
        g=subprocess.Popen([base.PY,str(ENTRY),'--guardian',str(os.getpid()),str(helpers.identity(os.getpid())['start_ticks'])],cwd=P,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    base.atomic_json(R/'PHYSICAL_DR_GUARDIAN_STARTED.json',helpers.identity(g.pid))
    last=source
    try:
        set_profile(PROFILE)
        w.phase('physical_dr_preflight',source=info,owner=helpers.identity(os.getpid()),profile=PROFILE,world_progress_05_confirmed=close['world_progress_05_confirmed'])
        probe(source,'world',steps=300,count=22)
        probe(source,'20k',steps=120,count=20000)
        baseline=regression(source)
        base.atomic_json(R/'PHYSICAL_DR_BASELINE_PASSED.json',dict(source=info,profile=PROFILE,paths=baseline))
        # Newly enlarged parameter distribution: full PPO checks are new evidence.
        # Their policies are discarded, while all their effective time is billed.
        ctl.training(source,'physical_dr_128_discard',count=128,iterations=2,duration=600)
        ctl.training(source,'physical_dr_20k_discard',count=20000,iterations=4,duration=600)
        before=base.budget_state()['charged_training_seconds']
        assert ctl.remaining()>120
        w.phase('bounded_physical_dr_learning',source=info,profile=PROFILE,duration_s=min(2700,ctl.remaining()))
        ck=ctl.training(source,'physical_dr_stage1_learning',duration=min(2700,ctl.remaining()))
        exposure=base.budget_state()['charged_training_seconds']-before
        paths=regression(ck);result,path=paired(ck);last=ck
        # Deliberately save a review boundary after one new DR exposure. Numerical
        # performance facts remain visible; no automatic infinite single-lesson loop.
        review=dict(checkpoint=base.checkpoint(ck),profile=PROFILE,effective_exposure_s=exposure,
            report_paths=paths,paired_path=path,paired_pass=result['pass_'],world_summary=result['world_summary'],
            world_progress_05_confirmed=result['world_progress_05_confirmed'],stage1_admission_only=True,
            actual_budget=base.budget_state(),all_curricula_finished=False,real_robot_certified=False)
        base.atomic_json(R/'PHYSICAL_DR_STAGE1_REVIEW_READY.json',review)
        w.phase('physical_dr_stage1_review_ready',**review,last_validated_source=base.checkpoint(last))
        status('physical_dr_stage1_review_ready',training_pid=None,evaluation_pid=None,validation_pid=None,final_evaluation=review)
    except BaseException:
        reason=traceback.format_exc()
        if not base.trainers() and not base.budget_state()['active_segment'] and not helpers.active_processes(ctl.PROBES):
            set_profile('white_v2')
        w.hold(last,reason);raise

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--guardian',nargs=2);a=p.parse_args()
    if a.guardian:guardian(int(a.guardian[0]),a.guardian[1])
    else:controller()
