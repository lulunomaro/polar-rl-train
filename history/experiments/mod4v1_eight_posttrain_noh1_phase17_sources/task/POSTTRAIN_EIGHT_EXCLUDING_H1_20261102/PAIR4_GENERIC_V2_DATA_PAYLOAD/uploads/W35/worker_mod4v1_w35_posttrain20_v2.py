"""Root-owned finite full PPO W35->original RM70, original node CLI/schema.

One exact source read/decode via explicit cache. No authority writer/SSH. The
original parent owns private/shared locks,GO,time/accounting and terminal wait.
"""
from pathlib import Path
import argparse,copy,hashlib,json,os,runpy,shutil,subprocess,sys,time,traceback

SHA='8d6a9ab5fae3fd2689c59bcfc1f1e776eb162b8eef671417df0fc88150285c54'
BYTES=17620037; ADAM=654500; ITER=32643; LR=1.0000000000000004e-05
KIND='MOD4V1_W35_RESUME32643_FULLD0D7_RM70_POSTTRAIN20_V4'
GENERATION='MOD4_SINGLE_WRITER72_20261026'
MANIFEST_SHA='0543b0c47c53e15da0d7d017693d2b69f7f6354ef088c3a1b8ed2b9cc56e2beb'
PRIOR_WINDOW=82; PRIOR_CUMULATIVE=162
OUT=None


class FiniteUpdateCounter:
    """stdlib-only observer. Performs no optimizer operation; checks real returns."""
    def __init__(self,limit):
        assert type(limit)is int and 1<=limit<=20
        self.limit=limit;self.completed=0;self.steps=0;self.logged=0;self.active=False
    def before_update(self):
        assert self.completed<self.limit and not self.active
        self.active=True
    def step_returned(self):
        assert self.active
        self.steps+=1
    def after_update(self):
        assert self.active and self.steps==20*(self.completed+1)
        self.completed+=1;self.active=False


def read(path):return json.loads(Path(path).read_bytes())


def H(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def put(name,value):
    path=OUT/name; temporary=path.with_suffix(path.suffix+'.partial')
    with temporary.open('w',encoding='utf8') as f:
        json.dump(value,f,indent=2,allow_nan=False);f.flush();os.fsync(f.fileno())
    temporary.replace(path)


def merge_original_omissions(source,live):
    if isinstance(source,dict) and isinstance(live,dict):
        out=dict(source)
        for key,value in live.items():out[key]=merge_original_omissions(source[key],value) if key in source else value
        return out
    return live


def validate(task,go,args,job):
    sys.path.insert(0,str(job/'runtime/isaac/mod4'))
    from mod4v1_w35_posttrain_protocol_v2 import validate_new_job
    return validate_new_job(task,go,args,job)


def main():
    global OUT
    parser=argparse.ArgumentParser()
    parser.add_argument('--mode',choices=('train',),required=True)
    parser.add_argument('--num-envs',dest='num_envs',type=int,required=True)
    parser.add_argument('--run-id',required=True);parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();job=args.out.resolve().parent
    task=read(job/'TASK.json');go=read(job/'GO_PRODUCTION.json');validate(task,go,args,job)
    OUT=args.out.resolve();OUT.mkdir(exist_ok=False)
    assert H(__file__)==task['worker_SHA'] and H(job/'original_run_manifest.json')==MANIFEST_SHA
    # Same original startup light limits. Nonempty compute UUID rows are allowed;
    # no unrelated PID/argv inspection and no new empty-GPU condition exists.
    result=subprocess.run(['nvidia-smi','-i',task['GPU_UUID'],
        '--query-gpu=uuid,name,memory.free,utilization.gpu','--format=csv,noheader,nounits'],
        capture_output=True,text=True,timeout=15)
    assert result.returncode==0
    gpu=[x.strip() for x in result.stdout.strip().split(',')]
    import psutil
    ram=psutil.virtual_memory().available; disk=shutil.disk_usage(job).free
    assert gpu[0]==task['GPU_UUID'] and gpu[1]=='NVIDIA GeForce RTX 4090'
    assert int(gpu[2])>15669 and int(gpu[3])<=30 and ram>32*1024**3 and disk>25*1024**3
    put('ACTUAL_W35_RM70_V3_STARTUP_LIGHT.json',dict(epoch=time.time(),GPU_line=result.stdout.strip(),
        RAM_available=ram,disk_free=disk,private_EX_held_by_original_parent=True,
        nonempty_compute_UUID_not_rejected=True,no_other_PID_inspected=True))
    for key in list(os.environ):
        if key.startswith('RM_') or key in ('RANK','WORLD_SIZE','LOCAL_RANK','MASTER_ADDR','MASTER_PORT'):
            del os.environ[key]
    original=read(job/'original_run_manifest.json')
    env={k:str(v) for k,v in original['env'].items() if k not in ('RM_RESCUE_STOP_FILE','RM_RESCUE_DEADLINE')}
    assert env['RM_KEEP_STD']=='1' and env['RM_PHYSICS_DT_S']=='0.0025'
    assert env['RM_SOLVER_POS']=='32' and env['RM_SOLVER_VEL']=='4'
    env.update(RM_MOD4_USD=str(job/'runtime/assets/robot.usd'),
        RM_RESCUE_STOP_FILE=str(OUT/'STOP_AFTER_SAVE.json'),RM_RESCUE_DEADLINE=str(go['save_deadline']))
    os.environ.update(env);os.environ['MOD4_RESUME_QUEUE_CONTROL_US']='20000'
    os.environ['MOD4_RM70_ORIGINAL_ASSET_ROOT']=str(job/'original_field')
    os.environ['MOD4_RM70_ASSET_RECEIPT']=str(job/'RM70_BINARY_INSTALL_ACTUAL.json')
    os.environ['MOD4_RM70_NEW_LAYOUT_ROOT']=str(OUT/'new_original_CAD_layout')
    os.environ['MOD4_NEW208_JOB_ROOT']=str(job)
    storage=job/'kit_isolation';storage.mkdir(exist_ok=False)
    for name in ('data','DerivedDataCache'):(storage/name).mkdir()
    (storage/'data/user.config.json').write_text('{}')
    os.environ['MOD4_W35_OWN_KIT_STORAGE_ROOT']=str(storage)
    runtime=job/'runtime';mod=runtime/'isaac/mod4';sys.path[:0]=[str(mod),str(runtime)]
    from mod4v1_fresh_dr_guard import bind_before_task_import
    asset_identity=bind_before_task_import(task['asset_dir'])
    os.environ['MOD4V1_ASSET_DIR']=task['asset_dir']
    source=Path(task['model_path'])
    import torch
    from source_cache208_v3 import PinnedSource208,selected_source,cached_load
    cache=PinnedSource208(torch,source,SHA,BYTES)
    assert cache.state['iter']==ITER and cache.state['actual_new_PPO_updates']==PRIOR_WINDOW
    assert cache.state['typed_W35_RM70_task']['kind']=='MOD4V1_W35_RESUME32561_FULLD0D7_RM70_V3' and cache.state['typed_W35_RM70_task']['source_SHA']=='89aca6ce52f8e83719de14dd53cb423a182f14e4f370614887605b2131d5bf0f'
    typed=dict(kind=KIND,source_SHA=SHA,source_bytes=BYTES,source_iteration=ITER,
        source_Adam_step=ADAM,nominal_gas_N_each=400,policy_hz=50,feedback_hz=100,
        physics_dt=.0025,TGS=[32,4],num_envs=20000,actor_obs=35,critic_obs=38,action_dim=6,
        original_W35_reward_and_fixed_SI_observations=True,
        original_full_D0_D7_restore_then_one_new_physical_episode=True,
        same_RM70_course_assignment_and_command_fullstate_restored=True,
        new_physical_episode_and_query_cache_after_restore=True,source_prior_new_PPO_updates=PRIOR_CUMULATIVE,
        source_prior_window_PPO_updates=PRIOR_WINDOW,source_prior_cumulative_PPO_updates=PRIOR_CUMULATIVE,
        new_asset_USD_SHA=asset_identity.usd_sha256,new_asset_contract_SHA=asset_identity.contract_sha256,
        closure_episode_m=.01,mimic_rad=.01,D6_scope='original_gas_damping_not_all_joint_friction',
        old_G3_assignment_not_restored_into_new_mesh=True,root_quaternion_order='xyzw',
        original_plane_retained_W35_source_stays_frozen=True,
        full_SuperMimic_conversion=False,full_RM70_skill=False)
    put('SOURCE208_V3_CACHE_BEFORE_SDK.json',cache.receipt())
    entry=mod/'train_mod4v1_w35.py'
    sys.argv=[str(entry),'--headless','--device','cuda:0','--num_envs','20000','--seed',str(task['seed']),
        '--steps_per_env',str(task['steps_per_env']),'--learning_rate',str(LR),'--save_interval','25',
        '--init_checkpoint',str(source),'--log_root',str(OUT/'logs'),
        '--run_name','W35_RESUME32643_MOD4V1_POSTTRAIN20_FULLDR_RM70','--additional_iterations',str(task['max_additional_updates'])]
    ns=None;runner_holder=[None];updates=[0];last_complete=[None];last_saved=[time.time()]
    class SavedStop(Exception):pass
    with selected_source(cache):
        try:
            ns=runpy.run_path(str(entry),run_name='owned_W35_MOD4V1_config')
            import rescue_training
            from spring_pressure_checkpoint208_v3 import exact
            original_bounded_learn=rescue_training.learn
            def work(runner,n,log_dir):
                runner_holder[0]=runner;runner.logger.writer=None
                assert n==task['max_additional_updates'] and runner.alg.learning_rate==LR
                assert all(g['lr']==LR for g in runner.alg.optimizer.param_groups)
                real=runner.env.unwrapped;vec=runner.env;full=cache.state
                assert real.num_envs==20000 and real.physics_dt==.0025 and real.step_dt==.02 and real.cfg.decimation==8
                assert real._sim_step_counter==0 and real._physics_action_delay.queue.control_us==20000
                assert runner.current_learning_iteration==ITER and runner.alg.learning_rate==LR
                for key,current in [('actor_state_dict',runner.alg.actor.state_dict()),
                    ('critic_state_dict',runner.alg.critic.state_dict()),('optimizer_state_dict',runner.alg.optimizer.state_dict())]:
                    assert exact(current,full[key]),key
                steps=[int(v['step']) for v in runner.alg.optimizer.state_dict()['state'].values()]
                assert len(steps)==17 and set(steps)=={ADAM}
                assert real.spring_pressure_recipe()['nominal_stiffness_N_m']==2000
                assert real._w35_gas400_selected_bank_compatibility['selected_pose_index']==34
                assert real._mod4v1_asset_compatibility['new_contract_SHA']==asset_identity.contract_sha256
                assert set(real._mod4v1_asset_compatibility['authorized_changed_bodies'])=={'chassis','left_shin','right_shin'}
                assert real._mod4v1_fresh_dr_guard.restore_completed
                required={'SENSOR_RESUME_STARTUP_VERIFIED.json','DELAY_RESUME_STARTUP_VERIFIED.json',
                    'ACTION_DELAY_RESUME_STARTUP_VERIFIED.json','SPRING_PRESSURE_RESUME_STARTUP_VERIFIED.json',
                    'GAS_DAMPING_RESUME_STARTUP_VERIFIED.json','CHASSIS_PD_RESUME_STARTUP_VERIFIED.json',
                    'E1_TERRAIN_RESUME_STARTUP_VERIFIED.json','E1_COMMAND_RETENTION_STARTUP_VERIFIED.json'}
                receipts={p.name:p for p in Path(log_dir).glob('*STARTUP_VERIFIED.json')}
                assert required<=set(receipts)
                for name in required:assert read(receipts[name])['source_sha256']==SHA
                terrain=read(receipts['E1_TERRAIN_RESUME_STARTUP_VERIFIED.json'])
                assert terrain['original_terrain_restored_exact'] and terrain['one_new_physical_episode']
                full=cache.state
                immutable_truth=copy.deepcopy(full)
                raw_save=runner.save  # eight original full-state installers already active
                required_live={'actor_state_dict','critic_state_dict','optimizer_state_dict','iter',
                    'sensor_DR_state','sensor_global_rng_state','sensor_command_DR_rng_state',
                    'sensor_physical_DR_rng_state','feedback_delay_state','physical_action_delay_state',
                    'spring_pressure_state','gas_damping_state','chassis_PD_state',
                    'E1_terrain_state','E1_retained_flat_command_state'}
                counter=FiniteUpdateCounter(task['max_additional_updates'])
                def complete_save_path(path,*args,**kwargs):
                    assert not counter.active,'Never certify a partial original PPO update'
                    assert exact(cache.state,immutable_truth),'Immutable selected-source truth changed'
                    path=Path(path).resolve()
                    assert path.is_relative_to(OUT) and (path.suffix=='.pt' or path.name.endswith('.pt.partial'))
                    assert path!=source.resolve(),'Never overwrite mother'
                    path.parent.mkdir(parents=True,exist_ok=True)
                    tmp=path.with_name(path.name+'.fullstate.partial');assert not tmp.exists()
                    raw_save(str(tmp),*args,**kwargs)
                    live=cached_load(tmp,map_location='cpu',weights_only=False)
                    assert required_live<=set(live),('Original LIVE save omitted fields',required_live-set(live))
                    for key,obj in [('actor_state_dict',runner.alg.actor),('critic_state_dict',runner.alg.critic),('optimizer_state_dict',runner.alg.optimizer)]:
                        assert exact(live[key],obj.state_dict()),key
                    # The ORIGINAL runner publishes this value before logger.log.
                    # Record it as-is: no assignment to saved iter or live runner iteration.
                    assert live['iter']==int(runner.current_learning_iteration) and live['iter']>=ITER
                    current=[int(v['step']) for v in live['optimizer_state_dict']['state'].values()]
                    assert len(current)==17 and set(current)=={ADAM+20*counter.completed}
                    assert all(g['lr']==runner.alg.learning_rate for g in live['optimizer_state_dict']['param_groups'])
                    for key,adapter in [('sensor_DR_state',real._sensor_mild),('physical_action_delay_state',real._physics_action_delay),
                        ('spring_pressure_state',real._spring_pressure),('gas_damping_state',real._gas_damping)]:
                        assert exact(live[key],adapter.state_dict()),key
                    assert exact(live['chassis_PD_state']['COM'],real._chassis_com.state_dict())
                    assert exact(live['chassis_PD_state']['PD'],real._explicit_pd.state_dict())
                    from checkpoint_cache208_v3 import current_state as current_terrain
                    assert exact(live['E1_terrain_state'],current_terrain(real))
                    assert exact(live['E1_retained_flat_command_state'],real.command_manager.get_term('twist').state_dict_retention())
                    state=merge_original_omissions(full,live)
                    state['posttrain_live_runner_counter_at_save']=int(runner.current_learning_iteration)
                    state['posttrain_iteration_semantics']='Unmodified original RSL iteration; separately counted completed PPO updates; no arithmetic backfill'
                    state['posttrain_cumulative_new_PPO_updates']=PRIOR_CUMULATIVE+counter.completed
                    state['typed_W35_RM70_task']=merge_original_omissions(full.get('typed_W35_RM70_task',{}),typed)
                    state['actual_new_PPO_updates']=counter.completed
                    from mod4v1_w35_asset_compat import record_historical_source_metadata
                    record_historical_source_metadata(state,full)
                    state=merge_original_omissions(full,state)  # preserve even original historical root omissions
                    state['posttrain_source_cache_truth_unchanged']=True
                    state['mod4v1_clock']=dict(policy_hz=50,physics_dt_s=.0025,decimation=8,feedback_hz=100,gamma=.9801,lam=.9025)
                    torch.save(state,tmp)
                    roundtrip=cached_load(tmp,map_location='cpu',weights_only=False)
                    assert exact(roundtrip,state) and exact(cache.state,immutable_truth)
                    assert roundtrip['iter']==int(runner.current_learning_iteration)
                    tmp.replace(path)
                    row=dict(epoch=time.time(),path=str(path),bytes=path.stat().st_size,SHA=H(path),
                        source_SHA=SHA,actual_new_PPO_updates=counter.completed,
                        saved_iteration=roundtrip['iter'],actual_live_runner_iteration=int(runner.current_learning_iteration),
                        Adam_min=min(current),Adam_max=max(current),actual_saved_LR=roundtrip['optimizer_state_dict']['param_groups'][0]['lr'],
                        actual_optimizer_step_calls=counter.steps,
                        full_core_STD_optimizer_and_targetDR_saved=True,
                        source_prior_window_updates=PRIOR_WINDOW,source_prior_cumulative_updates=PRIOR_CUMULATIVE,
                        cumulative_new_PPO_updates=PRIOR_CUMULATIVE+counter.completed,
                        source_cache_truth_all_roots_unchanged=True,all_original_source_root_keys_retained=set(full)<=set(roundtrip),
                        same_RM70_course_assignment_command_fullstate_restored=True,
                        original_rescue_rename_pending=path.name.endswith('.pt.partial'))
                    put('latest_complete.json',row);last_complete[0]=row;last_saved[0]=time.time()
                    return row
                def save(label):return complete_save_path(OUT/(label+'.pt'))
                runner._new208_save_complete=save
                startup=save('model_startup_fullstate0')
                put('ACTUAL_W35_RM70_V3_FULLSTATE_BEFORE_NEW_CONTROL.json',dict(passed=True,
                    source_SHA=SHA,initial_Adam_step=ADAM,source_iteration=ITER,
                    actor_critic_STD_norm_optimizer_LR_original_fullstate_verified=True,
                    original_D0_D7_and_command_private_RNG_restore_before_one_new_episode=True,
                    same_RM70_profile_terrain_assignment_and_command_restored=True,source_cache=cache.receipt(),
                    full_startup_complete=startup,actual_startup_receipts={name:str(receipts[name]) for name in required}))
                obs=vec.get_observations();real._mod4v1_fresh_dr_guard.check_observations(obs)
                put('MOD4V1_FRESH_DR_NOMINAL_ACTUAL.json',real._mod4v1_fresh_dr_guard.receipt())
                physics0=int(real._integrated_contact.tick)
                feedback0=int(real._feedback_100hz_tick);apply0=dict(real._physics_action_delay.calls)
                reward_dt=[];old_reward=real.reward_manager.compute
                def reward(*args,**kwargs):
                    dt=kwargs.get('dt',args[0] if args else None);assert dt==.02;reward_dt.append(dt)
                    return old_reward(*args,**kwargs)
                real.reward_manager.compute=reward
                with torch.inference_mode():
                    for i in range(24):
                        before=int(real._integrated_contact.tick);fb=int(real._feedback_100hz_tick)
                        action=runner.alg.actor(obs,stochastic_output=False);obs,reward_value,done,extras=vec.step(action)
                        assert int(real._integrated_contact.tick)-before==8 and int(real._feedback_100hz_tick)-fb==2
                        assert obs['policy'].shape==(20000,35) and obs['critic'].shape==(20000,38)
                        assert all(bool(torch.isfinite(v).all()) for v in (obs['policy'],obs['critic'],reward_value))
                real.reward_manager.compute=old_reward
                assert int(real._integrated_contact.tick)-physics0==192 and int(real._feedback_100hz_tick)-feedback0==48
                assert {k:real._physics_action_delay.calls[k]-apply0[k] for k in ('legs','wheels')}=={'legs':192,'wheels':192}
                assert reward_dt==[.02]*24
                for key,current in [('actor_state_dict',runner.alg.actor.state_dict()),
                    ('critic_state_dict',runner.alg.critic.state_dict()),('optimizer_state_dict',runner.alg.optimizer.state_dict())]:
                    assert exact(current,full[key]),key
                put('NATIVE24_W35_RM70_V3_ACTUAL.json',dict(passed=True,num_envs=20000,controls=24,
                    physics_callbacks=192,feedback_samples=48,source_SHA=SHA,
                    optimizer_updates=0,actual_RewardManager_dt_s=.02,whole_RM70_skill=False))
                original_update=runner.alg.update;original_step=runner.alg.optimizer.step;original_log=runner.logger.log
                def update(*args,**kwargs):
                    counter.before_update()
                    losses=original_update(*args,**kwargs)
                    counter.after_update();updates[0]=counter.completed
                    return losses
                def optimizer_step(*args,**kwargs):
                    result=original_step(*args,**kwargs);counter.step_returned();return result
                def log(*args,**kwargs):
                    result=original_log(*args,**kwargs)
                    assert counter.completed==counter.logged+1,'One original completed PPO update per log boundary'
                    counter.logged=counter.completed
                    if counter.completed==1 or counter.completed%5==0:save('model_update'+str(counter.completed)+'_complete')
                    put('LATEST_PROGRESS.json',dict(epoch=time.time(),actual_new_PPO_updates=counter.completed,
                        actual_optimizer_step_calls=counter.steps,actual_live_runner_iteration=int(runner.current_learning_iteration),
                        actual_Adam_steps=[int(v['step'])for v in runner.alg.optimizer.state_dict()['state'].values()]))
                    stop=(counter.completed>=task['max_additional_updates'] or time.time()>=go['save_deadline']
                        or Path(task['stop_file']).exists() or (OUT/'STOP_AFTER_SAVE.json').exists()
                        or (Path(log_dir)/'STOP_AFTER_SAVE').exists() or shutil.disk_usage(job).free<8*1024**3)
                    if stop:save('model_final_complete');raise SavedStop()
                    return result
                runner.save=complete_save_path
                runner.alg.update=update;runner.alg.optimizer.step=optimizer_step;runner.logger.log=log
                try:
                    if (time.time()<go['save_deadline'] and not Path(task['stop_file']).exists()
                        and not (OUT/'STOP_AFTER_SAVE.json').exists() and not (Path(log_dir)/'STOP_AFTER_SAVE').exists()):
                        # Original rescue_training.learn installs its atomic/deadline
                        # hook and calls original runner.learn(..., init_at_random_ep_len=True).
                        original_bounded_learn(runner,n,log_dir)
                except SavedStop:pass
                finally:
                    runner.alg.update=original_update;runner.alg.optimizer.step=original_step;runner.logger.log=original_log
                    runner.save=raw_save
                assert not counter.active and counter.completed<=task['max_additional_updates']
                assert exact(cache.state,immutable_truth)
                final=save('model_final_complete')
                put('FINAL.json',dict(epoch=time.time(),passed=counter.completed>0,actual_new_PPO_updates=counter.completed,
                    new_environment_transitions=counter.completed*20000*task['steps_per_env'],source_SHA=SHA,final=final,
                    actual_optimizer_step_calls=counter.steps,actual_live_runner_iteration=int(runner.current_learning_iteration),
                    source_cache_truth_all_roots_unchanged=True,source_cache=cache.receipt(),whole_RM70_skill=False,
                    complete_SuperMimic_conversion=False,no_extra_training_window=True,
                    original_finite_owner_GO=dict(run_id=go['run_id'],role_key=go['role_key'],max_parent_seconds=go['max_parent_seconds'],
                        save_deadline=go['save_deadline'],nominal_end_epoch=go['nominal_end_epoch'],one_original_writer=True)))
            rescue_training.learn=work
            ns['main']()
        except BaseException:
            put('ORIGINAL_W35_RM70_V3_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),
                actual_new_PPO_updates=updates[0],source_cache=cache.receipt(),no_automatic_retry=True))
            runner=runner_holder[0]
            if runner is not None and hasattr(runner,'_new208_save_complete'):
                try:runner._new208_save_complete('model_failed_valid_prefix')
                except BaseException:put('FAILED_PREFIX_SAVE_ERROR.json',dict(error=traceback.format_exc()))
            raise
        finally:
            put('SOURCE208_V3_FINAL_READ_COUNTS.json',cache.receipt())
            if ns is not None:
                put('APP_CLOSING.json',dict(epoch=time.time(),source_read_counts_closed=True))
                ns['app'].close()
                put('APP_CLOSED.json',dict(epoch=time.time(),closed=True))


if __name__=='__main__':
    try:main()
    except BaseException:
        if OUT is not None and OUT.is_dir() and not (OUT/'ORIGINAL_W35_RM70_V3_ERROR.json').exists():
            put('ORIGINAL_W35_RM70_V3_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),
                phase='startup_or_source_admission_before_runtime',no_automatic_retry=True))
        raise
