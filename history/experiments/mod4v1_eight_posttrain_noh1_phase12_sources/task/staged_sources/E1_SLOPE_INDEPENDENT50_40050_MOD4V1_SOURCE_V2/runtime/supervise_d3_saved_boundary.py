"""Approved D3: wait for natural recovery boundary, then preflight and bounded learn."""
from pathlib import Path
import os,sys,json,time,subprocess,traceback,shutil,argparse
D=Path(__file__).resolve().parent;R=D/'reports';CODE=D/'isaac/mod4'
sys.path.insert(0,str(D));sys.path.insert(0,str(CODE))
import supervise_dt2500_solver32_training_test as s
sys.path.insert(0,str(CODE))
from clock_training_health import learning_health_pass
from reviewed_source_guard import verify_original_records
from feedback_delay_checkpoint import validate_delay_state
OLD=Path('/home/egde/rl_candidates/MOD4_VALIDATED_1MS_EPISODE_RECOVERY_20261008')
ORIGINAL_RUNTIME=s.runtime
read=s.q.w.read;write=s.write;identity=s.identity

def runtime():
    e=ORIGINAL_RUNTIME();e['RM_FEEDBACK_DELAY_PROFILE']='control_0_10ms_v1'
    e['RM_DELAY_INITIAL_ADMISSION']='D1D2_to_D3';return e

def trainers():
    names={'train_mod4_ppo.py','train_sensor_ppo.py','train_sensor_resume_ppo.py','train_history_ppo.py','train_delay_resume_ppo.py','train_delay_fresh_preflight_ppo.py'}
    found=[]
    for p in Path('/proc').glob('[0-9]*/cmdline'):
        try:
            argv=p.read_bytes().split(b'\0')
            if any(Path(a.decode(errors='replace')).name in names for a in argv):found.append(identity(int(p.parent.name)))
        except (OSError,ValueError):pass
    return found

def verify():
    verify_original_records(s.q,D)
    a=read(s.q.ER/'PLAN_APPROVAL.json');assert a['approved'] and 'S2' in a['allowed_stages']
    f=read(R/'SOURCE_FREEZE.json')['sha256'];old=read(OLD/'reports/SOURCE_FREEZE.json')['sha256']
    for n,h in f.items():assert s.q.base.sha(D/n)==h,n
    for n,h in old.items():assert f[n]==h and s.q.base.sha(OLD/n)==h,n
    cfg=read(CODE/'env.json');assert cfg['RM_PHYSICS_DT_S']=='0.001' and cfg['RM_SOLVER_POS']=='16' and cfg['RM_SOLVER_VEL']=='4'
    assert runtime()['RM_FEEDBACK_DELAY_PROFILE']=='control_0_10ms_v1' and runtime()['RM_SENSOR_PROFILE']=='noise_bias_mild_v1'
    assert read(R/'D3_FULL_CONTROLLER_CPU_CONTRACT.json')['passed']
    assert read(R/'test_delay_checkpoint_cpu_PASSED.json')['passed']

s.verify=verify;s.q.verify=s.q.w.verify=s.q.ctl.verify=lambda:verify_original_records(s.q,D)

def phase(name,**kw):
    write('D3_STATE.json',dict(epoch=time.time(),phase=name,owner=identity(os.getpid()),**kw))
    if name.startswith('waiting_'):return
    s.q.base.status(stage=name,supervisor_pid=os.getpid(),active_code_root=str(D),plan_stage='S2 E0 D3 actor feedback0/10ms',active_expert='E0',architecture_variant='A0',physics_dt_s=.001,solver_position=16,solver_velocity=4,sensor_profile='noise_bias_mild_v1',feedback_delay_profile='control_0_10ms_v1',active_log=kw.get('active_log'),normal_episode_resets_continue_learning=True)

def fullsave(path,count=20000,require_delay=True):
    import torch
    ck=torch.load(path,map_location='cpu',weights_only=False);info=s.q.base.checkpoint(path)
    assert info['finite_tensors']>=74 and ck['actor_state_dict']['mlp.0.weight'].shape==(256,35) and ck['critic_state_dict']['mlp.0.weight'].shape==(256,38)
    assert ck['optimizer_state_dict']['state'] and ck['sensor_DR_state']['n']==count and ck['sensor_recipe']['profile']=='noise_bias_mild_v1'
    assert ck['sensor_global_rng_state']['cuda'] and ck['sensor_command_DR_rng_state'] and ck['sensor_physical_DR_rng_state']
    if require_delay:
        d=type('DelaySchema',(),dict(n=count,enabled=True))();validate_delay_state(d,ck['feedback_delay_state'])
        assert ck['feedback_delay_recipe']['profile']=='control_0_10ms_v1'
    else:assert 'feedback_delay_state' not in ck
    return info

def source():
    row=read(R/'SELECTED_D1D2_BEHAVIOR_SOURCE.json');p=Path(row['checkpoint']['path']);assert s.q.base.sha(p)==row['checkpoint']['sha256']
    original=read(OLD/'reports/validated1ms_recovery_block1_PASSED.json')
    assert row['checkpoint']==original['checkpoint'] and original['own_PID_bound_receipt']['pid']==1038504
    run=Path(original['run']);rec=read(run/'latest_complete.json');assert rec==original['own_PID_bound_receipt']
    m=read(run/'run_manifest.json');assert m['source_map']==read(OLD/'reports/SOURCE_FREEZE.json')['sha256']
    assert read(run/'rolling_source_freeze.json')['sha256']==m['source_map']
    for n,h in m['src_sha256'].items():assert s.q.base.sha(run/'src_snapshot'/n)==h
    assert learning_health_pass(original['health']) and len(original['unique_completed_segment'])==1
    review=read(R/'FIRST_RECOVERY_MATCHED_REVIEW.json');assert review['decision']['D1D2_practical_enough_for_D3_preparation']
    assert review['learning']['block']['checkpoint']['sha256']==row['checkpoint']['sha256']
    assert all(all(v for k,v in pair.items() if k!='kind') for pair in review['pairing'])
    fullsave(p,require_delay=False);return p

def wait_existing():
    start=read(OLD/'reports/RECOVERY_STARTED.json')['owner'];guard=read(OLD/'reports/RECOVERY_GUARDIAN_STARTED.json')
    write('D3_WAIT_STARTED.json',dict(epoch=time.time(),owner=identity(os.getpid()),existing_parent=start,existing_guardian=guard,no_GPU_or_training_authority_until_boundary=True,canonical_write=False))
    while True:
        assert not (OLD/'reports/SOLVER32_ATTENTION.json').exists(),'Existing integrity failure: preserve saves and audit; no automatic takeover'
        actual=identity(start['pid']);g=identity(guard['pid'])
        alive=actual and actual['state']!='Z' and actual['start_ticks']==start['start_ticks']
        galive=g and g['state']!='Z' and g['start_ticks']==guard['start_ticks']
        phase('waiting_existing_1ms_recovery_saved_boundary',existing_parent=actual,existing_guardian=g,new_training_authority_started=False)
        if not alive and not galive:
            assert (OLD/'reports/SOLVER32_REVIEW_READY.json').exists()
            assert read(OLD/'reports/RECOVERY_STATE.json')['phase']=='S2_validated1ms_saved_review_ready'
            assert not trainers() and s.q.base.budget_state()['active_segment'] is None and not read(s.q.ctl.STATE_PATH).get('active_training')
            return
        time.sleep(15)

def freeze_run(run):
    f=read(R/'SOURCE_FREEZE.json')
    if (run/'rolling_source_freeze.json').exists():assert read(run/'rolling_source_freeze.json')['sha256']==f['sha256'];return
    for n,h in f['sha256'].items():
        assert s.q.base.sha(D/n)==h;p=run/'d3_source_snapshot'/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(D/n,p)
    s.q.base.atomic_json(run/'rolling_source_freeze.json',dict(candidate_root=str(D),sha256=f['sha256'],physics_dt_s=.001,solver=[16,4],feedback_delay_profile='control_0_10ms_v1',original222_exact=True))

def native20k(init):
    assert not trainers() and s.q.base.budget_state()['active_segment'] is None
    out=R/'D3_NATIVE20K.json';log=D/'d3_native20k.log';assert not out.exists() and not log.exists();before=s.q.ctl.CANONICAL.read_bytes()
    args=[s.q.base.PY,str(D/'native_d3_1ms_probe.py'),'--dt','.001','--checkpoint',str(init),'--num_envs','20000','--warmup','24','--steps','120','--profile_steps','0','--output',str(out),'--headless']
    with log.open('x') as f:p=subprocess.Popen(args,cwd=s.q.P,env=runtime(),stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
    s.LIVE=p;phase('frozen_D3_native20k',child=identity(p.pid),active_log=str(log));p.wait(timeout=1800);s.LIVE=None
    assert p.returncode==0 and out.exists() and not Path(str(out)+'.error').exists();r=read(out)
    assert before==s.q.ctl.CANONICAL.read_bytes() and r['actual_physics_dt']==.001 and r['decimation']==10
    assert not r['nonfinite'] and r['physical_callback_count']==1200 and r['health']['actual_physics_callbacks']==1440 and learning_health_pass(r['health'])
    assert r['initial_parameters']['actual_parameters_pass'] and r['final_parameters']['actual_parameters_pass'] and r['actual_solver_readback']['all_position16_velocity4']
    assert r['feedback_delay_recipe']['profile']=='control_0_10ms_v1' and r['actual_delay_manager_audit']['formula_max_error']<=2e-6
    write('D3_NATIVE20K_PASSED.json',dict(epoch=time.time(),output_sha256=s.q.base.sha(out),health=r['health'],callbacks=1200,num_envs=20000,ordinary_events_preserved=True,actual_parameters_pass=True,delay_recipe=r['feedback_delay_recipe'],no_PPO=True))

def train(init,count,updates,duration,label,discard):
    verify();assert not trainers() and s.q.base.budget_state()['active_segment'] is None and not read(s.q.ctl.STATE_PATH).get('active_training')
    assert s.left()>120;deadline=time.time()+min(duration,s.left());logs=D/('discard_logs' if discard else 'learning_logs');logs.mkdir(exist_ok=True);name=label+'_'+str(time.time_ns());log=D/(name+'.log')
    e=runtime();e['RM_RESCUE_DEADLINE']=str(deadline);entry='train_delay_fresh_preflight_ppo.py' if count==128 else 'train_delay_resume_ppo.py'
    args=[s.q.base.PY,str(CODE/entry),'--headless','--num_envs',str(count),'--steps_per_env','24','--max_iterations',str(updates),'--save_interval','1' if discard else '25','--learning_rate','.0001','--seed','20260928','--run_name',name,'--log_root',str(logs),'--init_checkpoint',str(init)]
    with log.open('x') as f:p=subprocess.Popen(args,cwd=s.q.P,env=e,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
    s.LIVE=p;s.q.base.start_segment(p,'S2_E0_D3_'+name,log);s.q.ctl.S=read(s.q.ctl.STATE_PATH)
    s.q.ctl.S['active_training']=dict(pid=p.pid,source=s.q.base.checkpoint(init),phase=label,log_root=str(logs),deadline=deadline,physics_dt_s=.001,solver_position=16,feedback_delay_profile='control_0_10ms_v1',discarded_preflight=discard);s.q.ctl.persist()
    phase('D3_complete_PPO_preflight' if discard else 'bounded_E0_D3_feedback_delay_learning',child=identity(p.pid),source=s.q.base.checkpoint(init),deadline_epoch=deadline,active_log=str(log))
    while p.poll() is None:
        s.q.base.account_segment();roots=list(logs.glob('*_'+name))
        if len(roots)==1:
            run=roots[0]
            if (run/'latest_complete.json').exists():
                rec=read(run/'latest_complete.json');assert rec['pid']==p.pid;freeze_run(run);write('D3_CURRENT_SAVE.json',dict(epoch=time.time(),own_run=str(run),receipt=rec,discarded_preflight=discard))
            if (run/'CLOCK_TRAINING_HEALTH.json').exists():write('D3_ACTIVE_HEALTH.json',read(run/'CLOCK_TRAINING_HEALTH.json'))
        time.sleep(1 if discard else 5)
    s.q.base.account_segment(finish=True);s.LIVE=None;s.q.ctl.S['active_training']=None;s.q.ctl.persist()
    assert p.returncode==0 and 'Traceback (most recent call last)' not in log.read_text(errors='replace')
    run=s.q.w.rate.trainer_run(logs,p.pid);freeze_run(run);rec=read(run/'latest_complete.json');ck=fullsave(Path(rec['checkpoint']),count=count);m=read(run/'run_manifest.json');h=read(run/'CLOCK_TRAINING_HEALTH.json')
    assert rec['pid']==p.pid and m['source_map']==read(R/'SOURCE_FREEZE.json')['sha256'] and m['init_checkpoint_sha256']==s.q.base.sha(init)
    assert m['feedback_delay_recipe']['profile']=='control_0_10ms_v1' and m['env']['RM_PHYSICS_DT_S']=='0.001' and m['env']['RM_SOLVER_POS']=='16'
    for n,v in m['src_sha256'].items():assert s.q.base.sha(run/'src_snapshot'/n)==v,n
    if count==20000:
        startup=read(run/'DELAY_RESUME_STARTUP_VERIFIED.json');assert startup['source_sha256']==s.q.base.sha(init) and startup['delay_episode_incremented_once'] and startup['sensor_bias_reset_once'] and not startup['PhysX_exact_resume_claimed']
    seg=[x for x in read(s.q.ctl.CANONICAL)['completed_segments'] if x['pid']==p.pid];assert len(seg)==1
    row=dict(epoch=time.time(),checkpoint=ck,run=str(run),own_PID_bound_receipt=rec,health=h,actual_updates=h['control_steps']//24,actual_environment_steps=h['control_steps']*count,unique_completed_segment=seg,discarded_preflight=discard,small128_uses_fresh_sensor_and_delay_streams=count==128,ordinary_events_preserved=True,new_physical_episode=True)
    write(label+'_SAVED_EXIT.json',row);assert learning_health_pass(h),('Integrity failure, own source retained',h)
    if discard:assert h['control_steps']==24*updates
    write(label+'_PASSED.json',row);return Path(ck['path']),row

def publish(init,label):
    package=read(R/'D3_FROZEN_BEHAVIOR_PACKAGE.json');sha=s.q.base.sha(init);dest=s.q.ER.parent/'artifacts'/('d3-own-'+sha+'.pt')
    if not dest.exists():shutil.copy2(init,dest)
    assert s.q.base.sha(dest)==sha;source=dict(path=str(dest),bytes=dest.stat().st_size,sha256=sha);a=read(s.q.ER/'PLAN_APPROVAL.json');jobs=[]
    for kind in ('flat','spin','world'):
        job='clk1000-recovery-d3-'+label+'-'+kind;p=s.q.ER.parent/'eval_queue'/(job+'.json');assert not p.exists()
        row=dict(job_id=job,stage='S0E',immutable=True,plan_id=a['plan_id'],plan_sha256=a['approved_plan_sha256'],published_epoch=time.time(),kind=kind,profile='white_v3',sensor_profile='noise_bias_mild_v1',feedback_delay_profile='control_0_10ms_v1',seed=20261002,num_envs=80 if kind=='flat' else 88,steps=1500,max_wall_seconds=1800,architecture_variant='A0',role='Actual D3 closed-loop frozen skill, not fixed-clean SDK',physics_dt_s=.001,control_dt_s=.01,solver_position=16,solver_velocity=4,artifacts=dict(runtime=package,checkpoint=source),no_learning=True,canonical_write_authority=False,GPU_concurrency=1,platform_scope_not_yet_accepted=True)
        s.q.base.atomic_json(p,row);jobs.append(row)
    write('D3_'+label+'_ASYNC_PUBLISHED.json',dict(epoch=time.time(),source=source,jobs=jobs,no_GPU_or_canonical_write=True))

def guardian(owner,ticks):
    while True:
        actual=identity(owner);a=s.q.base.budget_state()['active_segment'];lost=not actual or actual['state']=='Z' or actual['start_ticks']!=ticks
        if a and (lost or s.left()<=0):
            child=identity(a['pid'])
            if child and any(str(CODE/n) in child['argv'] for n in ('train_delay_resume_ppo.py','train_delay_fresh_preflight_ppo.py')):
                for logs in (D/'discard_logs',D/'learning_logs'):
                    try:run=s.q.w.rate.trainer_run(logs,child['pid']);break
                    except (AssertionError,FileNotFoundError):run=None
                if run and not (run/'STOP_AFTER_SAVE').exists():(run/'STOP_AFTER_SAVE').write_text('Own complete save: guardian budget/owner protection\n')
        if not a and (lost or (R/'D3_REVIEW_READY.json').exists() or (R/'D3_ATTENTION.json').exists()):return
        time.sleep(15)

def main():
    import torch;torch.set_num_threads(1)
    assert not (R/'D3_DISPATCH_STARTED.json').exists();verify();init=source()
    write('D3_DISPATCH_STARTED.json',dict(epoch=time.time(),owner=identity(os.getpid()),source=fullsave(init,require_delay=False),new_training_authority_started=False,first_block_seconds=2700,subsequent_block_seconds=7200,maximum_window_seconds=17100,new_budget_seconds=0))
    wait_existing();verify()
    assert read(R/'D3_1MS_ACTUAL_SDK_REVIEW.json')['passed']
    s.q.helpers.acquire(s.q.P/'autonomy_controller.lock');s.q.helpers.acquire(s.q.ctl.CANONICAL.parent/'native_floor_supervisor.lock')
    assert not trainers() and s.q.base.budget_state()['active_segment'] is None and not read(s.q.ctl.STATE_PATH).get('active_training')
    before=s.q.ctl.CANONICAL.read_bytes()
    write('D3_INSTALL_BOUNDARY.json',dict(epoch=time.time(),owner=identity(os.getpid()),source=fullsave(init,require_delay=False),old_parent_guardian_children_exited=True,two_original_locks_held=True,active_empty=True,no_budget_mutation=True,source_is_actual_behavior_reviewed_not_maxiter=True))
    assert before==s.q.ctl.CANONICAL.read_bytes();native20k(init)
    with (D/'guardian.log').open('x') as f:g=subprocess.Popen([s.q.base.PY,str(Path(__file__)),'--guardian',str(os.getpid()),str(identity(os.getpid())['start_ticks'])],cwd=s.q.P,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
    write('D3_GUARDIAN_STARTED.json',identity(g.pid));pre=[]
    for count,updates in ((128,2),(20000,4)):
        _,row=train(init,count,updates,900,'d3_discard_'+str(count),True);pre.append(row)
    write('D3_COMPLETE_PPO_PREFLIGHT_PASSED.json',dict(epoch=time.time(),receipts=pre,weights_discarded=True,real6144_and1920000_steps=True))
    publish(init,'10-anchor')
    for block,duration in enumerate((2700,7200,7200),1):
        if s.left()<=120:break
        init,row=train(init,20000,10000,duration,'d3_formal_block'+str(block),False);publish(init,'20-b'+str(block))
    write('D3_REVIEW_READY.json',dict(epoch=time.time(),own_saved_source=str(init),all_courses_finished=False,next='Actual same-platform D3/clean skill and ordinary event review; progress D4 by approved plan, not unlimited same-scope repeats'))
    phase('E0_D3_saved_review_ready',child=None)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--guardian',nargs=2);args=p.parse_args()
    try:
        if args.guardian:guardian(int(args.guardian[0]),int(args.guardian[1]))
        else:main()
    except BaseException:
        write('D3_ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),own_child_still_alive=bool(s.LIVE and s.LIVE.poll() is None),active_segment=s.q.base.budget_state()['active_segment'],all_weights_retained=True,no_blind_resume=True));raise
