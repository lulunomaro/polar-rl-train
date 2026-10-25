"""Independent E1 same-scope stable entry gated by actual planned route and old skills."""
from pathlib import Path
import os,sys,json,time,subprocess,traceback,shutil,argparse
D=Path(__file__).resolve().parent;R=D/'reports';CODE=D/'isaac/mod4'
sys.path.insert(0,str(D));sys.path.insert(0,str(CODE))
import supervise_dt2500_solver32_training_test as s
sys.path.insert(0,str(CODE))
from clock_training_health import learning_health_pass
from reviewed_source_guard import verify_original_records
from feedback_delay_checkpoint import validate_delay_state
from action_delay_physics_queue import PhysicsActionQueue
from spring_pressure_checkpoint import validate_saved_pressure
from gas_damping_checkpoint import validate_saved_damping
from chassis_pd_checkpoint import validate_saved_chassis_pd
OLD=Path('/home/egde/rl_candidates/MOD4_D7_FULL_CONTRACT_20261009')
ORIGINAL_RUNTIME=s.runtime
read=s.q.w.read;write=s.write;identity=s.identity

def runtime():
    e=ORIGINAL_RUNTIME();e['RM_FEEDBACK_DELAY_PROFILE']='control_0_10ms_v1'
    e['RM_PHYSICS_ACTION_DELAY_PROFILE']='physical_target_0_2500_5000us_v1'
    e['RM_ACTION_DELAY_INITIAL_ADMISSION']='D3_to_D5'
    e['RM_SPRING_PRESSURE_PROFILE']='gas_stiffness_independent_episode_090_110_v1'
    e['RM_SPRING_INITIAL_ADMISSION']='D4_to_D5'
    e['RM_GAS_DAMPING_PROFILE']='gas_damping_independent_episode_090_110_v1'
    e['RM_GAS_DAMPING_INITIAL_ADMISSION']='D5_to_D6'
    e['RM_CHASSIS_COM_PROFILE']='chassis_link_local_independent_xyz_5mm_v1'
    e['RM_EXPLICIT_PD_PROFILE']='explicit_motor_PD_independent_095_105_v1'
    e['RM_CHASSIS_PD_INITIAL_ADMISSION']='D6_to_D7'
    e['RM_E1_INITIAL_ADMISSION']='E0_to_E1'
    return e

def trainers():
    names={'train_chassis_pd_resume_ppo.py','train_chassis_pd_fresh_preflight_ppo.py','train_mod4_ppo.py','train_sensor_ppo.py','train_sensor_resume_ppo.py','train_history_ppo.py','train_action_resume_ppo.py','train_action_fresh_preflight_ppo.py','train_spring_resume_ppo.py','train_spring_fresh_preflight_ppo.py','train_gas_resume_ppo.py','train_gas_fresh_preflight_ppo.py','train_e1_route_health_resume_ppo.py','train_e1_resource_fresh_preflight_ppo.py','train_e1_reset_evidence_resume_ppo.py'}
    found=[]
    for p in Path('/proc').glob('[0-9]*/cmdline'):
        try:
            argv=p.read_bytes().split(b'\0')
            if any(Path(a.decode(errors='replace')).name in names for a in argv):found.append(identity(int(p.parent.name)))
        except (OSError,ValueError):pass
    return found

def verify():
    verify_original_records(s.q,D)
    a=read(s.q.ER/'PLAN_APPROVAL.json');assert a['approved'] and 'S3' in a['allowed_stages'] and a['approved_plan_sha256']=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
    f=read(R/'SOURCE_FREEZE.json')['sha256'];previous=Path('/home/egde/rl_candidates/MOD4_S3_E1_ROUTE_HEALTH_REVIEW_20261009');old=read(previous/'reports/SOURCE_FREEZE.json')['sha256']
    assert len(old)==310 and len(f)==311
    for n,h in f.items():assert s.q.base.sha(D/n)==h,n
    for n,h in old.items():assert f[n]==h and s.q.base.sha(previous/n)==h,n
    assert read(CODE/'env.json')==read(previous/'isaac/mod4/env.json')
    assert read(R/'REUSED_E1_COMPLETE_PPO_PREFLIGHT_PASSED.json')['weights_discarded']
    assert read(R/'E1_ROUTE_HEALTH_CPU_PASSED.json')['passed']
    assert read(R/'E1_FIRST_TASK_COMPLETE_ACTUAL_REVIEW.json')['snapshot57_exact']



s.verify=verify;s.q.verify=s.q.w.verify=s.q.ctl.verify=lambda:verify_original_records(s.q,D)

def phase(name,**kw):
    write('E1_STATE.json',dict(epoch=time.time(),phase=name,owner=identity(os.getpid()),**kw))
    if name.startswith('waiting_'):return
    s.q.base.status(stage=name,supervisor_pid=os.getpid(),active_code_root=str(D),plan_stage='S3 E1 gentle40x40 terrain, BODYvx+-0.3/yaw0; complete D0-D7 inherited; genuine new terrain contracts required',active_expert='E1',architecture_variant='A0',physics_dt_s=.0025,solver_position=32,solver_velocity=4,sensor_profile='noise_bias_mild_v1',feedback_delay_profile='control_0_10ms_v1',active_log=kw.get('active_log'),normal_episode_resets_continue_learning=True)

def fullsave(path,count=20000,require_action=True,require_spring=True,require_gas=True,require_d7=True,require_e1=True):
    import torch
    ck=torch.load(path,map_location='cpu',weights_only=False);info=s.q.base.checkpoint(path)
    assert info['finite_tensors']>=84 and ck['actor_state_dict']['mlp.0.weight'].shape==(256,35) and ck['critic_state_dict']['mlp.0.weight'].shape==(256,38)
    assert ck['optimizer_state_dict']['state'] and ck['sensor_DR_state']['n']==count and ck['sensor_recipe']['profile']=='noise_bias_mild_v1'
    assert ck['sensor_global_rng_state']['cuda'] and ck['sensor_command_DR_rng_state'] and ck['sensor_physical_DR_rng_state']
    d=type('DelaySchema',(),dict(n=count,enabled=True))();validate_delay_state(d,ck['feedback_delay_state'])
    assert ck['feedback_delay_recipe']['profile']=='control_0_10ms_v1'
    if require_action:
        q=PhysicsActionQueue(count,'cpu',0);saved=ck['physical_action_delay_state']
        # CUDA and CPU generators serialize different formats. Check all queue
        # schemas on CPU without asking a CPU generator to consume CUDA bytes;
        # exact CUDA RNG restoration is proved by the real startup contract.
        for r in saved['rng'].values():assert r.dtype==torch.uint8 and r.ndim==1 and r.numel()>0
        schema=dict(saved,rng={k:g.get_state() for k,g in q.rng.items()});q.validate_state(schema)
        assert ck['physical_action_delay_recipe']['profile']=='physical_target_0_2500_5000us_v1'
    else:assert 'physical_action_delay_state' not in ck
    if require_spring:
        validate_saved_pressure(ck['spring_pressure_state'],count)
        assert ck['spring_pressure_recipe']['profile']=='gas_stiffness_independent_episode_090_110_v1'
    else:assert 'spring_pressure_state' not in ck
    if require_gas:
        validate_saved_damping(ck['gas_damping_state'],count)
        assert ck['gas_damping_recipe']['profile']=='gas_damping_independent_episode_090_110_v1'
    else:assert 'gas_damping_state' not in ck
    if require_d7:
        validate_saved_chassis_pd(ck['chassis_PD_state'],count);assert ck['chassis_PD_recipe']['COM_profile']=='chassis_link_local_independent_xyz_5mm_v1' and ck['chassis_PD_recipe']['PD_profile']=='explicit_motor_PD_independent_095_105_v1'
    else:assert 'chassis_PD_state' not in ck
    if require_e1:
        from e1_terrain_state import validate
        validate(ck['E1_terrain_state'],count)
    else:assert 'E1_terrain_state' not in ck
    return info

def source():
    review=read(R/'E1_PLANNED_BEHAVIOR_SCOPE_ACCEPTED.json')
    assert review['actual_five_cases_review_complete'] and review['task_model_data_scope_accepted'] and review['no_systemic_direction_or_major_retention_failure_observed']
    actual=read(R/'E1_FIRST_TASK_COMPLETE_ACTUAL_REVIEW.json');row=actual['row'];p=Path(row['checkpoint']['path'])
    assert review['source_sha256']==row['checkpoint']['sha256']=='655a36b78926bc17d4230996fe152b62d0f997f3037105d5247582697440481f'
    assert fullsave(p)==row['checkpoint'] and learning_health_pass(row['health']) and len(row['unique_completed_segment'])==1
    return p


def wait_existing():
    previous=Path('/home/egde/rl_candidates/MOD4_S3_E1_ROUTE_HEALTH_REVIEW_20261009');pr=previous/'reports';ps=read(pr/'E1_STATE.json')
    assert ps['phase']=='E1_shallow_saved_review_ready' and ps.get('child') is None
    row=read(pr/'e1_gentle_route_recovery_PASSED.json')
    locators=[ps['owner'],read(pr/'E1_GUARDIAN_STARTED.json'),dict(pid=row['own_PID_bound_receipt']['pid'],start_ticks=69438489)]
    assert all(not (x:=identity(p['pid'])) or x['state']=='Z' or x['start_ticks']!=p['start_ticks'] for p in locators)
    assert not trainers() and s.q.base.budget_state()['active_segment'] is None and not read(s.q.ctl.STATE_PATH).get('active_training')
    assert len([v for v in read(s.q.ctl.CANONICAL)['completed_segments'] if v['pid']==row['own_PID_bound_receipt']['pid']])==1



def freeze_run(run):
    f=read(R/'SOURCE_FREEZE.json')
    if (run/'rolling_source_freeze.json').exists():assert read(run/'rolling_source_freeze.json')['sha256']==f['sha256'];return
    for n,h in f['sha256'].items():
        assert s.q.base.sha(D/n)==h;p=run/'e1_source_snapshot'/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(D/n,p)
    s.q.base.atomic_json(run/'rolling_source_freeze.json',dict(candidate_root=str(D),sha256=f['sha256'],physics_dt_s=.0025,solver=[32,4],feedback_delay_profile='control_0_10ms_v1',all277_predecessor_exact=True))

def native20k(init):
    proof=read(R/'REUSED_E1_NATIVE20K_PASSED.json');compact=read(R/'REUSED_E1_NATIVE_COMPACT.json')
    assert proof['no_PPO'] and compact['checkpoint_sha256']==s.q.base.sha(init) and compact['physical_callback_count']==480 and compact['health']['actual_physics_callbacks']==576
    assert compact['E1_actual_ground_error_m']==0 and compact['E1_height_reward_formula_error']==0
    assert compact['E1_terrain_identity']['seed']==20260928 and compact['E1_terrain_identity']['partition_exact']
    write('E1_NATIVE20K_PASSED.json',dict(proof,reused_actual_native=True,no_GPU_replay=True,reuse_reason='Only independently requested reset-q audit metadata and failed-log destination change; actual ground/plant/configure/native source exact. Real new20k restore must still pass.'))


def train(init,count,updates,duration,label,discard):
    verify();assert not trainers() and s.q.base.budget_state()['active_segment'] is None and not read(s.q.ctl.STATE_PATH).get('active_training')
    assert s.left()>120;deadline=time.time()+min(duration,s.left());logs=D/('discard_logs' if discard else 'learning_logs');logs.mkdir(exist_ok=True);name=label+'_'+str(time.time_ns());log=D/(name+'.log')
    e=runtime();e['RM_RESCUE_DEADLINE']=str(deadline);entry='train_e1_resource_fresh_preflight_ppo.py' if count==128 else 'train_e1_route_health_resume_ppo.py'
    args=[s.q.base.PY,str(CODE/entry),'--headless','--num_envs',str(count),'--steps_per_env','24','--max_iterations',str(updates),'--save_interval','1' if discard else '25','--learning_rate','.0001','--seed','20260928','--run_name',name,'--log_root',str(logs),'--init_checkpoint',str(init)]
    with log.open('x') as f:p=subprocess.Popen(args,cwd=s.q.P,env=e,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
    s.LIVE=p;s.q.base.start_segment(p,'S3_E1_'+name,log);s.q.ctl.S=read(s.q.ctl.STATE_PATH)
    s.q.ctl.S['active_training']=dict(pid=p.pid,source=s.q.base.checkpoint(init),phase=label,log_root=str(logs),deadline=deadline,physics_dt_s=.0025,solver_position=32,feedback_delay_profile='control_0_10ms_v1',discarded_preflight=discard);s.q.ctl.persist()
    phase('E1_complete_PPO_preflight' if discard else 'bounded_E1_gentle_terrain_learning',child=identity(p.pid),source=s.q.base.checkpoint(init),deadline_epoch=deadline,active_log=str(log))
    while p.poll() is None:
        s.q.base.account_segment();roots=list(logs.glob('*_'+name))
        if len(roots)==1:
            run=roots[0]
            if (run/'latest_complete.json').exists():
                rec=read(run/'latest_complete.json');assert rec['pid']==p.pid;freeze_run(run);write('E1_CURRENT_SAVE.json',dict(epoch=time.time(),own_run=str(run),receipt=rec,discarded_preflight=discard))
            if (run/'CLOCK_TRAINING_HEALTH.json').exists():write('E1_ACTIVE_HEALTH.json',read(run/'CLOCK_TRAINING_HEALTH.json'))
        time.sleep(1 if discard else 5)
    s.q.base.account_segment(finish=True);s.LIVE=None;s.q.ctl.S['active_training']=None;s.q.ctl.persist()
    assert p.returncode==0 and 'Traceback (most recent call last)' not in log.read_text(errors='replace')
    run=s.q.w.rate.trainer_run(logs,p.pid);freeze_run(run);rec=read(run/'latest_complete.json');ck=fullsave(Path(rec['checkpoint']),count=count);m=read(run/'run_manifest.json');h=read(run/'CLOCK_TRAINING_HEALTH.json')
    assert rec['pid']==p.pid and m['source_map']==read(R/'SOURCE_FREEZE.json')['sha256'] and m['init_checkpoint_sha256']==s.q.base.sha(init)
    assert m['feedback_delay_recipe']['profile']=='control_0_10ms_v1' and m['physical_action_delay_recipe']['profile']=='physical_target_0_2500_5000us_v1' and m['env']['RM_PHYSICS_DT_S']=='0.0025' and m['env']['RM_SOLVER_POS']=='32'
    for n,v in m['src_sha256'].items():assert s.q.base.sha(run/'src_snapshot'/n)==v,n
    if count==20000:
        terrain=read(run/'E1_TERRAIN_RESUME_STARTUP_VERIFIED.json');assert terrain['source_sha256']==s.q.base.sha(init) and terrain['actual_CUDA_terrain_bookkeeping_disk_roundtrip_exact'] and terrain['complete_D1_D7_optimizer_global_named_streams_verified'] and terrain['E1_episode_incremented_once'] and not terrain['PhysX_exact_resume_claimed']
        cp=read(run/'CHASSIS_PD_RESUME_STARTUP_VERIFIED.json');assert cp['source_sha256']==s.q.base.sha(init) and cp['actual_CUDA_chassis_PD_disk_roundtrip_exact'] and cp['COM_PD_episode_incremented_once'] and cp['complete_D1_D6_optimizer_global_named_streams_verified'] and not cp['PhysX_exact_resume_claimed']
        gas=read(run/'GAS_DAMPING_RESUME_STARTUP_VERIFIED.json');assert gas['source_sha256']==s.q.base.sha(init) and gas['actual_CUDA_gas_state_disk_roundtrip_exact'] and gas['gas_episode_incremented_once'] and gas['complete_D1_D5_optimizer_global_named_streams_verified'] and not gas['PhysX_exact_resume_claimed']
        spring=read(run/'SPRING_PRESSURE_RESUME_STARTUP_VERIFIED.json');assert spring['source_sha256']==s.q.base.sha(init) and spring['actual_CUDA_spring_state_disk_roundtrip_exact'] and spring['spring_episode_incremented_once'] and spring['complete_D1_D4_optimizer_global_named_streams_verified'] and not spring['PhysX_exact_resume_claimed']
        startup=read(run/'ACTION_DELAY_RESUME_STARTUP_VERIFIED.json');assert startup['source_sha256']==s.q.base.sha(init) and startup['action_episode_incremented_once'] and startup['complete_D3_sensor_feedback_optimizer_global_named_streams_verified'] and not startup['PhysX_exact_resume_claimed']
    assert m['gas_damping_recipe']['profile']=='gas_damping_independent_episode_090_110_v1'
    seg=[x for x in read(s.q.ctl.CANONICAL)['completed_segments'] if x['pid']==p.pid];assert len(seg)==1
    row=dict(epoch=time.time(),checkpoint=ck,run=str(run),own_PID_bound_receipt=rec,health=h,actual_updates=h['control_steps']//24,actual_environment_steps=h['control_steps']*count,unique_completed_segment=seg,discarded_preflight=discard,small128_uses_fresh_sensor_feedback_action_pressure_gas_streams=count==128,ordinary_events_preserved=True,new_physical_episode=True)
    write(label+'_SAVED_EXIT.json',row);assert learning_health_pass(h),('Integrity failure, own source retained',h)
    if discard:assert h['control_steps']==24*updates
    write(label+'_PASSED.json',row);return Path(ck['path']),row

def publish(init,label):
    packages=read(R/'E1_PLANNED_BEHAVIOR_PUBLISHED.json');sha=s.q.base.sha(init);dest=s.q.ER.parent/'artifacts'/('e1-stable-own-'+sha+'.pt')
    if not dest.exists():shutil.copy2(init,dest)
    assert s.q.base.sha(dest)==sha;checkpoint=dict(path=str(dest),bytes=dest.stat().st_size,sha256=sha);jobs=[]
    # Exact admitted frozen dispatchers; one actual terrain route and three old skills.
    for template in packages['jobs'][1:]:
        row=json.loads(json.dumps(template));kind=row['kind'];terrain=row['actual_behavior_scope'].startswith('gentle terrain')
        job='clk2500-closure-episode-d3-'+label+('-terrain' if terrain else '-retention')+'-'+kind
        row.update(job_id=job,published_epoch=time.time(),role='Independent E1 unchanged-gentle stable candidate; actual terrain and inherited old skill, no learning evaluation',scope_pending_actual_review=True)
        row['artifacts']['checkpoint']=checkpoint;p=s.q.ER.parent/'eval_queue'/(job+'.json');assert not p.exists()
        s.q.base.atomic_json(p,row);jobs.append(row)
    write('E1_'+label+'_ASYNC_PUBLISHED.json',dict(epoch=time.time(),source=checkpoint,jobs=jobs,no_GPU_or_canonical_write=True))


def guardian(owner,ticks):
    while True:
        actual=identity(owner);a=s.q.base.budget_state()['active_segment'];lost=not actual or actual['state']=='Z' or actual['start_ticks']!=ticks
        if a and (lost or s.left()<=0):
            child=identity(a['pid'])
            if child and any(str(CODE/n) in child['argv'] for n in ('train_action_resume_ppo.py','train_action_fresh_preflight_ppo.py','train_spring_resume_ppo.py','train_spring_fresh_preflight_ppo.py','train_e1_route_health_resume_ppo.py','train_e1_resource_fresh_preflight_ppo.py')):
                for logs in (D/'discard_logs',D/'learning_logs'):
                    try:run=s.q.w.rate.trainer_run(logs,child['pid']);break
                    except (AssertionError,FileNotFoundError):run=None
                if run and not (run/'STOP_AFTER_SAVE').exists():(run/'STOP_AFTER_SAVE').write_text('Own complete save: guardian budget/owner protection\n')
        if not a and (lost or (R/'E1_REVIEW_READY.json').exists() or (R/'E1_ATTENTION.json').exists()):return
        time.sleep(15)

def main():
    import torch;torch.set_num_threads(1)
    assert not (R/'E1_DISPATCH_STARTED.json').exists();verify()
    write('E1_BEHAVIOR_GATED_ENTRY_STARTED.json',dict(epoch=time.time(),owner=identity(os.getpid()),CPU_only_while_waiting=True,no_GPU_or_canonical_write_before_actual_scope=True))
    phase('waiting_actual_E1_route_and_old_skill_review',child=None)
    while not (R/'E1_PLANNED_BEHAVIOR_SCOPE_ACCEPTED.json').exists():
        if (R/'E1_BEHAVIOR_SCOPE_ATTENTION.json').exists():
            write('E1_REVIEW_READY.json',dict(epoch=time.time(),actual_behavior_attention_hold=True,all_courses_finished=False));return
        time.sleep(15)
    verify();wait_existing();init=source()
    s.q.helpers.acquire(s.q.P/'autonomy_controller.lock');s.q.helpers.acquire(s.q.ctl.CANONICAL.parent/'native_floor_supervisor.lock')
    wait_existing();before=s.q.ctl.CANONICAL.read_bytes()
    write('E1_INSTALL_BOUNDARY.json',dict(epoch=time.time(),owner=identity(os.getpid()),source=fullsave(init),old_parent_guardian_children_exited=True,two_original_locks_held=True,active_empty=True,new_budget_seconds=0))
    write('E1_DISPATCH_STARTED.json',dict(epoch=time.time(),owner=identity(os.getpid()),source=fullsave(init),maximum_stable_window_seconds=14400,blocks=2,unchanged_gentle_geometry=True,repeated45min_clock_trial=False,new_budget_seconds=0))
    assert before==s.q.ctl.CANONICAL.read_bytes()
    with (D/'guardian.log').open('x') as out:g=subprocess.Popen([s.q.base.PY,str(Path(__file__)),'--guardian',str(os.getpid()),str(identity(os.getpid())['start_ticks'])],cwd=s.q.P,stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
    write('E1_GUARDIAN_STARTED.json',identity(g.pid))
    write('E1_COMPLETE_PPO_PREFLIGHT_PASSED.json',dict(read(R/'REUSED_E1_COMPLETE_PPO_PREFLIGHT_PASSED.json'),reused_exact_scope_no_GPU_replay=True))
    for block in (1,2):
        if s.left()<=120:break
        init,row=train(init,20000,10000,min(7200,s.left()),'e1_gentle_stable_block'+str(block),False)
        publish(init,'116-e1-gentle-b'+str(block))
    write('E1_REVIEW_READY.json',dict(epoch=time.time(),own_saved_source=str(init),all_courses_finished=False,next='Actual stable terrain and inherited retention review before any gradual geometry increment; E0 remains frozen; RM annotations retained'))
    phase('E1_gentle_stable_saved_review_ready',child=None)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--guardian',nargs=2);args=p.parse_args()
    try:
        if args.guardian:guardian(int(args.guardian[0]),int(args.guardian[1]))
        else:main()
    except BaseException:
        write('E1_ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),own_child_still_alive=bool(s.LIVE and s.LIVE.poll() is None),active_segment=s.q.base.budget_state()['active_segment'],all_weights_retained=True,no_blind_resume=True));raise
