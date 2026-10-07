"""Approved S1A matched A1/A2 authority; complete discard preflights then bounded learning."""
from pathlib import Path
import sys,os,time,json,subprocess,traceback,argparse
D=Path(__file__).resolve().parent;R=D/'reports'
N=Path('/home/egde/rl_candidates/MOD4_PHYSICS_DT1000_WORKER_REVIEW_20261007')
SDK=Path('/home/egde/rl_candidates/MOD4_S1A_HISTORY_LABEL_LIFECYCLE_20261007')
sys.path.insert(0,str(N));import continue_clock1000_worker_manifest_review_once as q
TARGET=275;CAP=21600;LIVE=None

def write(name,value):q.base.atomic_json(R/name,value)

def verify():
    q.verify();a=q.w.read(q.ER/'PLAN_APPROVAL.json');assert a['approved'] and a['version']=='1.5' and 'S1A' in a['allowed_stages']
    for n,h in q.w.read(R/'SOURCE_FREEZE.json')['sha256'].items():assert q.base.sha(D/n)==h,n
    assert q.w.read(D/'isaac/mod4/env.json')==q.w.read(N/'isaac/mod4/env.json')
    assert q.w.read(SDK/'reports/HISTORY_SDK_PASSED.json')['canonical_bytes_exact']
    assert q.w.read(R/'ARCHITECTURE_LABEL_REVIEW.json')['passed']

def stage_used():
    return sum(x['ended_epoch']-x['started_epoch'] for x in q.w.read(q.ctl.CANONICAL)['completed_segments'] if 'moe_S1A' in x['kind'])

def remaining():
    b=q.base.budget_state();a=b['active_segment']
    return b['remaining_training_seconds']-(max(0,time.time()-a['accounted_through_epoch']) if a else 0)

def guardian(pid,ticks):
    while True:
        owner=q.helpers.identity(pid);b=q.base.budget_state();a=b['active_segment']
        lost=not owner or owner['state']=='Z' or owner['start_ticks']!=ticks
        if a:
            child=q.helpers.identity(a['pid'])
            if child and str(D/'train_history_ppo.py') in child['argv'] and (lost or remaining()<=0):
                try:run=q.w.rate.trainer_run(D/'learning_logs',child['pid'])
                except AssertionError:
                    try:run=q.w.rate.trainer_run(D/'discard_logs',child['pid'])
                    except AssertionError:run=None
                if run and not (run/'STOP_AFTER_SAVE').exists():(run/'STOP_AFTER_SAVE').write_text('Owner/budget protection: own complete save boundary\n')
        if not a and (lost or (R/'S1A_MATCHED_HISTORY_REVIEW_READY.json').exists() or (R/'S1A_HISTORY_ATTENTION.json').exists()):return
        time.sleep(15)

def fullsave(path):
    import torch
    info=q.base.checkpoint(path);ck=torch.load(path,map_location='cpu',weights_only=False)
    meta=ck['history_architecture']
    assert ck['actor_state_dict']['mlp.0.weight'].shape==(256,38)
    assert ck['actor_state_dict']['encoder.net.0.weight'].shape==(128,175)
    assert ck['critic_state_dict']['mlp.0.weight'].shape==(256,38)
    assert meta['variant'] in ('A1','A2') and not meta['teacher_is_actor_input'] and meta['reset_teacher_mask_required']
    for key in ('rng_state','feedback_history_state','independent_generator_state','common_step_counter'):assert key in ck
    assert bool(ck['rng_state']['torch_cuda']) and meta['actual_updates']>0
    if meta['variant']=='A1':assert ck['aux_optimizer_state_dict']['state'] and meta['aux_updates']>0
    else:assert ck['aux_optimizer_state_dict'] is None and meta['aux_updates']==0
    return info,meta

def train(variant,source,count,target,discard=False):
    global LIVE
    verify();assert not q.base.trainers() and q.base.budget_state()['active_segment'] is None
    assert not q.w.read(q.ctl.STATE_PATH).get('active_training')
    left=min(remaining(),CAP-stage_used());assert left>120,'Actual stage/budget safe-start boundary'
    duration=min(600 if discard else 2700,left)
    label=('discard' if discard else 'learning')+'_'+variant+'_'+str(time.time_ns())
    logs=D/('discard_logs' if discard else 'learning_logs');logs.mkdir(exist_ok=True)
    log=D/(label+'.log');begin=time.time();deadline=begin+duration
    env=q.w.runtime();env.update(RM_RESCUE_DEADLINE=str(deadline),PYTHONUNBUFFERED='1')
    args=[q.base.PY,str(D/'train_history_ppo.py'),'--headless','--architecture_variant',variant,'--target_updates',str(target),
      '--num_envs',str(count),'--steps_per_env','24','--save_interval',str(target if discard else 25),
      '--learning_rate','.0001','--seed','20260928','--run_name',label,'--log_root',str(logs),'--init_checkpoint',str(source)]
    with log.open('x') as stream:
        child=subprocess.Popen(args,cwd=q.P,env=env,stdin=subprocess.DEVNULL,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True)
    LIVE=child;q.base.start_segment(child,'moe_S1A_'+label,log)
    q.ctl.S=q.w.read(q.ctl.STATE_PATH)
    q.ctl.S['active_training']=dict(pid=child.pid,source=q.base.checkpoint(source),phase='S1A_'+label,profile='white_v3',
       cap=4*__import__('math').pi,log_root=str(logs),deadline=deadline)
    q.ctl.persist()
    current=dict(epoch=time.time(),phase='architecture_PPO_preflight' if discard else 'bounded_matched_history_learning',
       variant=variant,owner=q.helpers.identity(os.getpid()),child=q.helpers.identity(child.pid),active_log=str(log),
       source=q.base.checkpoint(source),num_envs=count,target_actual_updates=target,deadline_epoch=deadline,
       physics_dt_s=.001,policy_period_s=.01,original_optimizer_migration_explicit=True)
    write('S1A_HISTORY_STATE.json',current)
    q.base.status(stage=current['phase'],active_code_root=str(D),plan_stage='S1A',architecture_variant=variant,
       training_pid=child.pid,evaluation_pid=None,active_log=str(log),trainer_deadline_epoch=deadline,physics_dt_s=.001)
    run=None
    while child.poll() is None:
        q.base.account_segment()
        try:run=q.w.rate.trainer_run(logs,child.pid)
        except AssertionError:pass
        if run:
            receipt=q.w.read(run/'latest_complete.json')
            current['own_run']=str(run);current['own_latest_complete']=receipt
            write('S1A_HISTORY_STATE.json',dict(current,epoch=time.time()))
        time.sleep(1 if discard else 5)
    q.base.account_segment(finish=True);LIVE=None
    q.ctl.S['active_training']=None;q.ctl.persist()
    q.base.status(training_pid=None,training_exit_code=child.returncode)
    text=log.read_text(errors='replace')
    assert child.returncode==0 and 'Traceback (most recent last)' not in text and 'Traceback (most recent call last)' not in text,('Architecture worker failed; preserve all saves',str(log))
    run=q.w.rate.trainer_run(logs,child.pid);receipt=q.w.read(run/'latest_complete.json')
    info,meta=fullsave(Path(receipt['checkpoint']));manifest=q.w.read(run/'run_manifest.json')
    assert manifest['architecture']['variant']==variant and manifest['architecture']['seed']==20260928
    assert manifest['source_map']==q.w.read(R/'SOURCE_FREEZE.json')['sha256']
    assert manifest['env']['RM_PHYSICS_DT_S']=='.001' or float(manifest['env']['RM_PHYSICS_DT_S'])==.001
    for name,h in manifest['src_sha256'].items():assert q.base.sha(run/'src_snapshot'/name)==h
    health=q.w.read(run/'CLOCK_TRAINING_HEALTH.json')
    delta=meta['actual_updates']-manifest['architecture']['actual_updates_before']
    assert delta*24==health['control_steps'] and health['actual_physics_callbacks']==health['expected_physics_callbacks']
    row=dict(epoch=time.time(),variant=variant,source=q.base.checkpoint(source),checkpoint=info,architecture=meta,
      actual_updates_this_segment=delta,actual_control_steps=health['control_steps'],actual_environment_policy_steps=count*health['control_steps'],
      physical_health=health,PID_bound_receipt=receipt,run=str(run),discarded_preflight=discard,
      unique_completed_segment=[x for x in q.w.read(q.ctl.CANONICAL)['completed_segments'] if x['pid']==child.pid])
    assert len(row['unique_completed_segment'])==1
    write(label+'_COMPLETE.json',row)
    assert health['actual_task_reset_events']==0 and health['failed_environments']==0 and health['max_closure_error_m']<=.002 and health['max_mimic_error_rad']<=.01,('Actual architecture physical/task failure',row)
    if discard:assert delta==target and meta['actual_updates']==target,'Incomplete discard preflight'
    return Path(info['path']),row

def main():
    import torch;torch.set_num_threads(1)
    assert not (R/'S1A_HISTORY_STARTED.json').exists(),'Unique architecture authority already executed'
    verify();q.helpers.acquire(q.P/'autonomy_controller.lock');q.helpers.acquire(q.ctl.CANONICAL.parent/'native_floor_supervisor.lock')
    assert not q.base.trainers() and q.base.budget_state()['active_segment'] is None and not q.w.read(q.ctl.STATE_PATH).get('active_training')
    ready=q.w.read(N/'reports/SELECTED_CLOCK_REVIEW_READY.json')
    assert q.w.read(N/'reports/FORMAL_CLOCK_HEALTH_REVIEW.json')['adoption_retained']
    assert q.base.checkpoint(Path(ready['checkpoint']['path']))==ready['checkpoint']
    assert q.w.read(Path(ready['run'])/'CLOCK_TRAINING_HEALTH.json')['control_steps']==TARGET*24
    assert not q.helpers.identity(q.w.read(SDK/'reports/HISTORY_SDK_LAUNCHED.json')['owner']['pid'])
    assert not q.helpers.identity(q.w.read(SDK/'reports/HISTORY_SDK_LAUNCHED.json')['owner']['pid'])
    old=Path('/home/egde/rl_candidates/MOD4_S1A_MATCHED_HISTORY_TRAINING_20261007')
    att=q.w.read(old/'reports/S1A_HISTORY_ATTENTION.json')
    assert att['active_segment'] is None and 'runtime_env' in att['error'] and not att['child_still_alive']
    assert not q.helpers.identity(q.w.read(old/'reports/S1A_HISTORY_LAUNCHED.json')['owner']['pid'])
    assert not q.helpers.identity(q.w.read(old/'reports/S1A_HISTORY_GUARDIAN_STARTED.json')['pid'])
    assert not (old/'reports/S1A_HISTORY_STATE.json').exists()
    assert callable(q.w.runtime) and q.w.runtime()['RM_PHYSICS_DT_S']=='0.001'
    write('S1A_LAUNCH_API_REVIEW.json',dict(epoch=time.time(),previous_error=att,
      old_owner_guardian_exited=True,error_before_GPU_PPO_or_budget_segment=True,actual_runtime_API_used=True,
      original212_runtime_and_architecture_sources_unchanged=True))
    write('S1A_HISTORY_STARTED.json',dict(epoch=time.time(),owner=q.helpers.identity(os.getpid()),stage_used_before=stage_used(),stage_cap_seconds=CAP,
      original_A0=ready,target_matched_actual_updates=TARGET,source_original23509=q.base.checkpoint(q.SOURCE),
      seed=20260928,new_architecture_optimizers=True,old_A0_optimizer_retained=True,causal_architecture_isolation_not_claimed=True))
    with (D/'guardian.log').open('x') as stream:
        guard=subprocess.Popen([q.base.PY,str(D/'supervise_matched_history_launch_review_once.py'),'--guardian',str(os.getpid()),str(q.helpers.identity(os.getpid())['start_ticks'])],
          cwd=q.P,stdin=subprocess.DEVNULL,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True)
    write('S1A_HISTORY_GUARDIAN_STARTED.json',q.helpers.identity(guard.pid))
    results=[]
    for variant in ('A1','A2'):
        pre=[]
        for count,updates in ((128,2),(20000,4)):
            ck,row=train(variant,q.SOURCE,count,updates,discard=True);pre.append(row)
        write(variant+'_COMPLETE_PPO_PREFLIGHT_PASSED.json',dict(epoch=time.time(),receipts=pre,weights_discarded=True,new_scope=variant))
        source=q.SOURCE;blocks=[]
        for block in range(3):
            source,row=train(variant,source,20000,TARGET,discard=False);blocks.append(row)
            if row['architecture']['actual_updates']==TARGET:break
            assert row['architecture']['actual_updates']<TARGET and stage_used()<CAP
        else:raise AssertionError('Matched update target not reached within bounded architecture windows')
        write(variant+'_MATCHED_LEARNING_COMPLETE.json',dict(epoch=time.time(),final=blocks[-1],segments=blocks,target_actual_updates=TARGET,
          task_health_passed=True,skill_behavior_evaluation_pending=True))
        results.append(blocks[-1])
    write('S1A_MATCHED_HISTORY_REVIEW_READY.json',dict(epoch=time.time(),A0=ready,A1=results[0],A2=results[1],
      matched_control_steps=TARGET*24,matched_environment_policy_steps=TARGET*24*20000,stage_used_seconds=stage_used(),
      next='Evaluate actual same-clock policies/skills and compute deployment/wall cost; architecture winner not selected by reward'))
    write('S1A_HISTORY_STATE.json',dict(epoch=time.time(),phase='S1A_matched_architecture_saved_review_ready',child=None,active_segment=None,
      trained_architectures=['A1','A2'],behavior_comparison_pending=True,all_curricula_finished=False))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--guardian',nargs=2);args=p.parse_args()
    try:
        if args.guardian:guardian(int(args.guardian[0]),int(args.guardian[1]))
        else:main()
    except BaseException:
        write('S1A_HISTORY_ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),active_segment=q.base.budget_state()['active_segment'],
          child_still_alive=LIVE is not None and LIVE.poll() is None,all_checkpoints_preserved=True))
        print(traceback.format_exc(),flush=True);raise
