"""Root-owned finite full PPO W35->original RM70, original node CLI/schema.

One exact source read/decode via explicit cache. No authority writer/SSH. The
original parent owns private/shared locks,GO,time/accounting and terminal wait.
"""
from pathlib import Path
import argparse,hashlib,json,os,runpy,shutil,subprocess,sys,time,traceback

SHA='343e0fd8f4950ffea2b09808a3bf88d9dd68e14b06f84c7bdaad462dbc8a51bd'
BYTES=17619269; ADAM=649720; ITER=32404; LR=.00017085937500000009
KIND='MOD4_W35_FULL_RM70_QUALIFIED343E_CONTINUE227'
GENERATION='MOD4_SINGLE_WRITER72_20261026'
MANIFEST_SHA='0543b0c47c53e15da0d7d017693d2b69f7f6354ef088c3a1b8ed2b9cc56e2beb'
OUT=None


def read(path):return json.loads(Path(path).read_bytes())


def H(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def put(name,value):
    path=OUT/name; temporary=path.with_suffix(path.suffix+'.partial')
    with temporary.open('w',encoding='utf8') as f:
        json.dump(value,f,indent=2,allow_nan=False);f.flush();os.fsync(f.fileno())
    temporary.replace(path)


def validate(task,go,args,job):
    assert args.mode=='train' and args.num_envs==20000
    assert args.out.resolve()==job/'production' and args.run_id==task['run_id']==go['run_id']
    assert task['kind']==KIND and task['source_SHA']==SHA and task['source_bytes']==BYTES
    assert task['source_iteration']==ITER and task['source_Adam_step']==ADAM and task['source_LR']==LR
    assert task['num_envs']==20000 and task['original_canonical_generation']==GENERATION
    assert go['role_key']==task['role_key'] and go['source_model_SHA']==SHA
    assert go['source_iteration']==ITER and go['input_Adam']==ADAM
    assert go['one_original_writer'] is True and go['num_envs']==20000
    assert go['actor_obs']==35 and go['critic_obs']==38 and go['action_dim']==6
    assert go['physics_dt']==.0025 and go['TGS']==[32,4]
    assert go['policy_hz']==50 and go['feedback_hz']==100
    assert go['max_parent_seconds']==3900
    assert go['save_deadline']==go['learning_started_epoch']+3600
    assert go['nominal_end_epoch']==go['learning_started_epoch']+3900
    assert task['actual_private_EX_held_by_parent'] is True
    assert task['actual_scene0PT211_passed'] is True and task['actual_robot0PT212_passed'] is True
    assert task['selected219V3_fullstate_CPU_proof_reused'] is True
    assert task['new_RM70_geometry_course_and_xyzw_source_reviewed'] is True
    assert task['actual_shared_material20k0PT_passed'] is True
    assert task['actual_material_limit_error_count']==0
    assert task['source_read_purpose']==dict(physical_byte_opens=1,decodes=1,source_bytes=BYTES)
    assert os.environ.get('CUDA_VISIBLE_DEVICES')==task['GPU_UUID']
    assert time.time()<go['save_deadline']


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
    source=Path(task['model_path'])
    import torch
    from source_cache208_v3 import PinnedSource208,selected_source,cached_load
    cache=PinnedSource208(torch,source,SHA,BYTES)
    assert cache.state['iter']==ITER and cache.state['actual_new_PPO_updates']==68
    assert cache.state['typed_W35_RM70_task']['kind']=='MOD4_W35_FULL_RM70_MATERIAL_SHARED214'
    typed=dict(kind=KIND,source_SHA=SHA,source_bytes=BYTES,source_iteration=ITER,
        source_Adam_step=ADAM,nominal_gas_N_each=400,policy_hz=50,feedback_hz=100,
        physics_dt=.0025,TGS=[32,4],num_envs=20000,actor_obs=35,critic_obs=38,action_dim=6,
        original_W35_reward_and_fixed_SI_observations=True,
        original_full_D0_D7_restore_then_one_new_physical_episode=True,
        same_RM70_course_assignment_and_command_fullstate_restored=True,
        new_physical_episode_and_query_cache_after_restore=True,source_prior_new_PPO_updates=68,
        old_G3_assignment_not_restored_into_new_mesh=True,root_quaternion_order='xyzw',
        original_plane_retained_W35_source_stays_frozen=True,
        full_SuperMimic_conversion=False,full_RM70_skill=False)
    put('SOURCE208_V3_CACHE_BEFORE_SDK.json',cache.receipt())
    entry=mod/'train_full214.py'
    sys.argv=[str(entry),'--headless','--device','cuda:0','--num_envs','20000','--seed','20260928',
        '--steps_per_env','24','--learning_rate',str(LR),'--save_interval','25',
        '--init_checkpoint',str(source),'--log_root',str(OUT/'logs'),
        '--run_name','W35_QUALIFIED343E_RM70_CONTINUE227','--additional_iterations','100000']
    ns=None;runner_holder=[None];updates=[0];last_complete=[None];last_saved=[time.time()]
    class SavedStop(Exception):pass
    with selected_source(cache):
        try:
            ns=runpy.run_path(str(entry),run_name='owned_W35_RM70_qualified227_config')
            import rescue_training
            from spring_pressure_checkpoint208_v3 import exact
            def work(runner,n,log_dir):
                runner_holder[0]=runner;runner.logger.writer=None
                runner.alg.learning_rate=runner.alg.optimizer.param_groups[0]['lr']
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
                assert len(real._w35_gas400_asset_compatibility['authorized_four_scalar_changes'])==4
                required={'SENSOR_RESUME_STARTUP_VERIFIED.json','DELAY_RESUME_STARTUP_VERIFIED.json',
                    'ACTION_DELAY_RESUME_STARTUP_VERIFIED.json','SPRING_PRESSURE_RESUME_STARTUP_VERIFIED.json',
                    'GAS_DAMPING_RESUME_STARTUP_VERIFIED.json','CHASSIS_PD_RESUME_STARTUP_VERIFIED.json',
                    'E1_TERRAIN_RESUME_STARTUP_VERIFIED.json','E1_COMMAND_RETENTION_STARTUP_VERIFIED.json'}
                receipts={p.name:p for p in Path(log_dir).glob('*STARTUP_VERIFIED.json')}
                assert required<=set(receipts)
                for name in required:assert read(receipts[name])['source_sha256']==SHA
                terrain=read(receipts['E1_TERRAIN_RESUME_STARTUP_VERIFIED.json'])
                assert terrain['original_terrain_restored_exact'] and terrain['one_new_physical_episode']
                def save(label):
                    completed=updates[0];path=OUT/(label+'.pt');tmp=path.with_suffix('.pt.partial')
                    runner.save(str(tmp));state=cached_load(tmp,map_location='cpu',weights_only=False)
                    state['iter']=ITER+completed
                    state['typed_W35_RM70_task']=typed
                    state['actual_new_PPO_updates']=completed
                    state['PPO50_gas400_adaptation']=full['PPO50_gas400_adaptation']
                    state['PPO50_gas400_new_updates']=completed
                    state['PPO50_gas400_clock']=dict(policy_hz=50,physics_dt_s=.0025,decimation=8,feedback_hz=100,gamma=.9801,lam=.9025)
                    current=[int(v['step']) for v in state['optimizer_state_dict']['state'].values()]
                    assert len(current)==17 and set(current)=={ADAM+20*completed}
                    for key in ('sensor_DR_state','sensor_global_rng_state','sensor_command_DR_rng_state',
                        'sensor_physical_DR_rng_state','feedback_delay_state','physical_action_delay_state',
                        'spring_pressure_state','gas_damping_state','chassis_PD_state',
                        'E1_terrain_state','E1_retained_flat_command_state'):
                        assert key in state,key
                    torch.save(state,tmp);tmp.replace(path)
                    row=dict(epoch=time.time(),path=str(path),bytes=path.stat().st_size,SHA=H(path),
                        source_SHA=SHA,actual_new_PPO_updates=completed,saved_iteration=ITER+completed,
                        Adam_min=min(current),Adam_max=max(current),
                        full_core_STD_optimizer_and_targetDR_saved=True,
                        same_RM70_course_assignment_command_fullstate_restored=True)
                    put('latest_complete.json',row);last_complete[0]=row;last_saved[0]=time.time()
                    return row
                runner._new208_save_complete=save
                startup=save('model_startup_fullstate0')
                put('ACTUAL_W35_RM70_V3_FULLSTATE_BEFORE_NEW_CONTROL.json',dict(passed=True,
                    source_SHA=SHA,initial_Adam_step=ADAM,source_iteration=ITER,
                    actor_critic_STD_norm_optimizer_LR_original_fullstate_verified=True,
                    original_D0_D7_and_command_private_RNG_restore_before_one_new_episode=True,
                    same_RM70_profile_terrain_assignment_and_command_restored=True,source_cache=cache.receipt(),
                    full_startup_complete=startup,actual_startup_receipts={name:str(receipts[name]) for name in required}))
                obs=vec.get_observations();physics0=int(real._integrated_contact.tick)
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
                original_update=runner.alg.update
                def update():
                    losses=original_update();updates[0]+=1
                    if updates[0]==1:
                        first=save('model_first_complete')
                        put('FIRST_ACTUAL_NEW_PPO_UPDATE.json',dict(epoch=time.time(),passed=True,
                            actual_new_PPO_updates=1,num_envs=20000,steps_per_env=24,
                            new_environment_transitions=480000,source_SHA=SHA,
                            initial_Adam_step=ADAM,new_Adam_step=ADAM+20,first_complete=first,
                            original_W35_reward_and_fixed_SI_observations=True,
                            explicitly_new_original_RM70_course=True,full_skill_graduation=False))
                    elif time.time()-last_saved[0]>=120:
                        save('model_latest_complete')
                    put('LATEST_PROGRESS.json',dict(epoch=time.time(),new_PPO_updates=updates[0],
                        new_environment_transitions=updates[0]*480000,source_SHA=SHA,
                        initial_Adam_step=ADAM,current_Adam_step=ADAM+20*updates[0]))
                    stop=(time.time()>=go['save_deadline'] or (OUT/'STOP_AFTER_SAVE.json').exists()
                        or (Path(log_dir)/'STOP_AFTER_SAVE').exists() or shutil.disk_usage(job).free<8*1024**3)
                    if stop:
                        save('model_final_complete');raise SavedStop()
                    return losses
                runner.alg.update=update;runner.current_learning_iteration=ITER+1
                try:runner.learn(num_learning_iterations=n,init_at_random_ep_len=True)
                except SavedStop:pass
                assert updates[0]>0
                final=save('model_final_complete')
                put('FINAL.json',dict(epoch=time.time(),passed=True,actual_new_PPO_updates=updates[0],
                    new_environment_transitions=updates[0]*480000,source_SHA=SHA,final=final,
                    source_cache=cache.receipt(),whole_RM70_skill=False,complete_SuperMimic_conversion=False,
                    own_produced_artifact_reads_declared='Original sensor saver plus explicit D2-D7 saver/roundtrip wrappers and fullsave validation; these are new own artifacts, not source model rereads',
                    original_finite_owner_GO=dict(run_id=go['run_id'],role_key=go['role_key'],
                        max_parent_seconds=go['max_parent_seconds'],save_deadline=go['save_deadline'],
                        nominal_end_epoch=go['nominal_end_epoch'],one_original_writer=True)))
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
