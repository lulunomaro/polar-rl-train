"""ROOT-only finite full E2 PPO continuation. No authority writer or SSH.

Original213/232 physical+restore entry,one selected source byte/decode,learned
STD and all17Adam retained. Original owner alone issues GO and charges time.
"""
from pathlib import Path
import argparse,hashlib,json,os,runpy,shutil,subprocess,sys,time,traceback
from e2_solo_contract import (SHA,BYTES,ITER,ADAM,LR,MODEL,MANIFEST_SHA,WORKER_KIND,validate_job)

OUT=None


def validate_finite_tree(torch,value,path='root'):
 """All floating/complex tensors and scalar numbers in a complete tree."""
 import math,numbers
 if torch.is_tensor(value):
  if value.is_floating_point() or value.is_complex():
   assert bool(torch.isfinite(value).all()),'Nonfinite tensor: '+path
 elif isinstance(value,dict):
  for key,item in value.items():validate_finite_tree(torch,item,path+'.'+str(key))
 elif isinstance(value,(list,tuple)):
  for i,item in enumerate(value):validate_finite_tree(torch,item,path+'.'+str(i))
 elif isinstance(value,numbers.Complex) and not isinstance(value,numbers.Integral):
  assert math.isfinite(value.real) and math.isfinite(value.imag),'Nonfinite scalar: '+path


def read(p):return json.loads(Path(p).read_bytes())
def H(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def put(name,value):
 p=OUT/name;tmp=p.with_suffix(p.suffix+'.partial')
 with tmp.open('w',encoding='utf8') as f:json.dump(value,f,indent=2,allow_nan=False);f.flush();os.fsync(f.fileno())
 tmp.replace(p)


def main():
 global OUT
 p=argparse.ArgumentParser();p.add_argument('--mode',choices=('train',),required=True)
 p.add_argument('--num-envs',type=int,required=True);p.add_argument('--run-id',required=True);p.add_argument('--out',type=Path,required=True)
 a=p.parse_args();J=a.out.resolve().parent;task=read(J/'TASK.json');go=read(J/'GO_PRODUCTION.json')
 validate_job(J,task,go)
 assert a.mode=='train' and a.num_envs==20000 and a.run_id==task['run_id']==go['run_id'] and a.out.resolve()==J/'production'
 assert go['max_parent_seconds']==3900 and go['save_deadline']==go['learning_started_epoch']+3600 and go['nominal_end_epoch']==go['learning_started_epoch']+3900
 assert go['physics_dt']==.0025 and go['TGS']==[32,4] and go['policy_hz']==50 and go['feedback_hz']==100 and time.time()<go['save_deadline']
 assert os.environ['CUDA_VISIBLE_DEVICES']==task['GPU_UUID']
 OUT=a.out.resolve();OUT.mkdir(exist_ok=False)
 assert H(__file__)==task['worker_SHA'] and H(J/'original_run_manifest.json')==MANIFEST_SHA
 result=subprocess.run(['nvidia-smi','-i',task['GPU_UUID'],'--query-gpu=uuid,name,memory.free,utilization.gpu','--format=csv,noheader,nounits'],capture_output=True,text=True,timeout=15)
 assert result.returncode==0
 line=[x.strip() for x in result.stdout.strip().split(',')]
 import psutil
 ram=psutil.virtual_memory().available;disk=shutil.disk_usage(J).free
 assert line[0]==task['GPU_UUID'] and line[1]=='NVIDIA GeForce RTX 4090' and int(line[2])>15669 and int(line[3])<=30 and ram>32*1024**3 and disk>25*1024**3
 put('E2_STARTUP_ORIGINAL_LIGHT_ACTUAL.json',dict(epoch=time.time(),GPU_line=result.stdout.strip(),RAM_available=ram,disk_free=disk,nonempty_compute_UUID_allowed=True,original_parent_private_EX_required=True))
 original=read(J/'original_run_manifest.json')['env']
 assert original['RM_KEEP_STD']=='1' and original['RM_SPIN_STAGE']=='world_directional_v1' and original['RM_SPIN_WORLD_PROGRESS_M_S']=='0.5'
 assert original['RM_GYRO_CURRICULUM']=='0' and original['RM_HEADING_CMD']=='0' and original['RM_MILD_DR_PROFILE']=='white_v3'
 for key in list(os.environ):
  if key.startswith('RM_') or key in ('RANK','WORLD_SIZE','LOCAL_RANK','MASTER_ADDR','MASTER_PORT'):del os.environ[key]
 os.environ.update({k:str(v) for k,v in original.items() if k not in ('RM_RESCUE_STOP_FILE','RM_RESCUE_DEADLINE')})
 runtime=J/'runtime';mod=runtime/'isaac/mod4'
 os.environ.update(RM_MOD4_USD=str(runtime/'assets/robot.usd'),RM_RESCUE_STOP_FILE=str(OUT/'STOP_AFTER_SAVE.json'),
  RM_RESCUE_DEADLINE=str(go['save_deadline']),RM_SPAWN_GRACE_STEPS='5',OWN_E2_H1_KIND='E2_WORLD_MOVING_SIGNED4',
  RM_JUMP_SCRIPT_PROB='0',RM_MOD4_MAP='',RM_MOD4_TERRAIN='flat',MOD4_RESUME_QUEUE_CONTROL_US='20000',MOD4_EXPERT213_JOB_ROOT=str(J))
 storage=J/'kit_isolation';storage.mkdir(exist_ok=False)
 for name in ('data','DerivedDataCache'):(storage/name).mkdir()
 (storage/'data/user.config.json').write_text('{}');os.environ['MOD4_EXPERT213_KIT_STORAGE_ROOT']=str(storage)
 sys.path[:0]=[str(J),str(J/'lib'),str(mod),str(runtime)]
 import torch
 from source_cache213 import PinnedSource213,selected_source,cached_load
 source=Path(MODEL);cache=PinnedSource213(torch,source,SHA,BYTES);full=cache.state
 assert full['iter']==ITER and 'E2_moving4_command_state' in full
 command_state=full['E2_moving4_command_state']
 assert command_state['version']==1 and command_state['kind']=='E2_WORLD_MOVING_SIGNED4' and command_state['moving_yaw_cap']==4.
 put('E2_SELECTED_SOURCE_CACHE_BEFORE_SDK.json',cache.receipt())
 typed=dict(kind=WORKER_KIND,source_SHA=SHA,source_bytes=BYTES,source_iteration=ITER,source_Adam_step=ADAM,source_LR=LR,
  actor_obs=35,critic_obs=38,action_dim=6,num_envs=20000,nominal_gas_N_each=400,policy_hz=50,feedback_hz=100,
  physics_dt=.0025,TGS=[32,4],domain_kind='E2_WORLD_MOVING_SIGNED4',sampler_stage='world_directional_v1',
  source_command_state_and_named_global_RNG_restored_before_one_new_physical_episode=True,
  original_world_goal_point5_and_body_pure_transition_stand_mix_retained=True,source_STD_17Adam_and_LR_retained=True,
  PhysX_exact_resume_claimed=False,full_E2_skill=False,full_SuperMimic=False)
 entry=mod/'train_e2_213.py'
 sys.argv=[str(entry),'--headless','--device','cuda:0','--num_envs','20000','--seed','20260928','--steps_per_env','24',
  '--learning_rate',str(LR),'--save_interval','25','--init_checkpoint',str(source),'--log_root',str(OUT/'logs'),
  '--run_name','E2_ORIGINAL_B3AE_FULLSTATE_CONTINUE','--additional_iterations','100000']
 ns=None;updates=[0];last_saved=[time.time()];runner_holder=[None];main_returned=[False]
 class SavedStop(Exception):pass
 with selected_source(cache):
  try:
   ns=runpy.run_path(str(entry),run_name='owned_original_E2_213_training_config')
   import rescue_training
   from spring_pressure_checkpoint213 import exact
   def work(runner,n,log_dir):
    runner_holder[0]=runner;runner.logger.writer=None
    real=runner.env.unwrapped;vec=runner.env;term=real.command_manager.get_term('twist')
    runner.alg.learning_rate=runner.alg.optimizer.param_groups[0]['lr']
    assert real.num_envs==20000 and real.physics_dt==.0025 and real.step_dt==.02 and real.cfg.decimation==8 and real._sim_step_counter==0
    assert real._physics_action_delay.queue.control_us==20000 and real.spring_pressure_recipe()['nominal_stiffness_N_m']==2000
    assert real.cfg.terminations.closure.params['threshold']==.002 and real.cfg.terminations.mimic.params['threshold']==.01
    assert runner.current_learning_iteration==ITER and runner.alg.learning_rate==LR
    assert not term.manual_evaluation_mode and term.progress_goal==.5 and term.pure_max==4*__import__('math').pi
    assert term.pure_fraction==.3 and term.moving_fraction==.2 and term.transition_within_pure==1/3
    for key,current in [('actor_state_dict',runner.alg.actor.state_dict()),('critic_state_dict',runner.alg.critic.state_dict()),('optimizer_state_dict',runner.alg.optimizer.state_dict())]:assert exact(current,full[key]),key
    steps=[int(v['step']) for v in runner.alg.optimizer.state_dict()['state'].values()];assert len(steps)==17 and set(steps)=={ADAM}
    required={'SENSOR_RESUME_STARTUP_VERIFIED.json','DELAY_RESUME_STARTUP_VERIFIED.json','ACTION_DELAY_RESUME_STARTUP_VERIFIED.json',
     'SPRING_PRESSURE_RESUME_STARTUP_VERIFIED.json','GAS_DAMPING_RESUME_STARTUP_VERIFIED.json','CHASSIS_PD_RESUME_STARTUP_VERIFIED.json','E2_COMMAND_RESUME_STARTUP_VERIFIED.json'}
    receipts={x.name:x for x in Path(log_dir).glob('*STARTUP_VERIFIED.json')};assert required<=set(receipts)
    for name in required:
     row=read(receipts[name]);assert row.get('source_sha256',row.get('source_SHA'))==SHA
    assert read(receipts['E2_COMMAND_RESUME_STARTUP_VERIFIED.json'])['source_has_E2_command_state'] is True
    def save(label):
     completed=updates[0];path=OUT/(label+'.pt');tmp=path.with_suffix('.pt.partial')
     runner.save(str(tmp));state=cached_load(tmp,map_location='cpu',weights_only=False)
     state['iter']=ITER+completed;state['typed_E2_original_world_PPO_task']=typed;state['actual_new_PPO_updates']=completed
     for key in ('PPO50_gas400_adaptation','PPO50_gas400_clock'):
      if key in full:state[key]=full[key]
     state['source_prior_formal_iteration']=ITER;state['source_prior_formal_Adam17']=ADAM
     current=[int(v['step']) for v in state['optimizer_state_dict']['state'].values()]
     assert len(current)==17 and set(current)=={ADAM+20*completed}
     for key in ('sensor_DR_state','sensor_global_rng_state','sensor_command_DR_rng_state','sensor_physical_DR_rng_state',
      'feedback_delay_state','physical_action_delay_state','spring_pressure_state','gas_damping_state','chassis_PD_state','E2_moving4_command_state'):assert key in state,key
     assert state['E2_moving4_command_state']['kind']=='E2_WORLD_MOVING_SIGNED4'
     validate_finite_tree(torch,state,'complete_save')
     torch.save(state,tmp);tmp.replace(path)
     row=dict(epoch=time.time(),path=str(path),bytes=path.stat().st_size,SHA=H(path),source_SHA=SHA,actual_new_PPO_updates=completed,
      saved_iteration=ITER+completed,Adam_min=min(current),Adam_max=max(current),full_core_STD_optimizer_and_targetDR_saved=True,
      original_E2_command_state_and_private_RNG_saved=True,all_saved_tensor_and_scalar_numbers_finite=True)
     put('latest_complete.json',row);last_saved[0]=time.time();return row
    runner._own_e2_save_complete=save
    startup=save('model_startup_fullstate0')
    put('E2_FULLSTATE_BEFORE_NEW_CONTROL_ACTUAL.json',dict(passed=True,source_SHA=SHA,source_iteration=ITER,initial_Adam_step=ADAM,
     original_35_38_6_STD_full_optimizer_LR_D0_D7_E2_RNG_restored=True,
     original_new_physical_episode_not_exact_PhysX_resume=True,startup_complete=startup,source_cache=cache.receipt(),
     receipts={k:str(receipts[k]) for k in required}))
    obs=vec.get_observations();tick=int(real._integrated_contact.tick);fb=int(real._feedback_100hz_tick);calls=dict(real._physics_action_delay.calls)
    dts=[];oldreward=real.reward_manager.compute
    def reward(*aa,**kk):
     dt=kk.get('dt',aa[0] if aa else None);assert dt==.02;dts.append(dt);return oldreward(*aa,**kk)
    real.reward_manager.compute=reward
    try:
     with torch.inference_mode():
      for i in range(24):
       before=int(real._integrated_contact.tick);beforefb=int(real._feedback_100hz_tick)
       action=runner.alg.actor(obs,stochastic_output=False);obs,reward_value,done,extras=vec.step(action)
       assert int(real._integrated_contact.tick)-before==8 and int(real._feedback_100hz_tick)-beforefb==2
       assert obs['policy'].shape==(20000,35) and obs['critic'].shape==(20000,38)
       assert all(bool(torch.isfinite(x).all()) for x in (obs['policy'],obs['critic'],reward_value))
    finally:real.reward_manager.compute=oldreward
    assert int(real._integrated_contact.tick)-tick==192 and int(real._feedback_100hz_tick)-fb==48 and dts==[.02]*24
    assert {k:real._physics_action_delay.calls[k]-calls[k] for k in ('legs','wheels')}=={'legs':192,'wheels':192}
    for key,current in [('actor_state_dict',runner.alg.actor.state_dict()),('critic_state_dict',runner.alg.critic.state_dict()),('optimizer_state_dict',runner.alg.optimizer.state_dict())]:assert exact(current,full[key]),key
    put('NATIVE24_E2_ORIGINAL_ACTUAL.json',dict(passed=True,num_envs=20000,controls=24,physics_callbacks=192,feedback_samples=48,
     source_SHA=SHA,optimizer_updates=0,actual_RewardManager_dt_s=.02,full_skill_graduation=False))
    old_update=runner.alg.update
    def update():
     losses=old_update();validate_finite_tree(torch,losses,'PPO_losses');updates[0]+=1
     if updates[0]==1:
      first=save('model_first_complete')
      put('FIRST_ACTUAL_NEW_PPO_UPDATE.json',dict(epoch=time.time(),passed=True,actual_new_PPO_updates=1,num_envs=20000,steps_per_env=24,
       new_environment_transitions=480000,source_SHA=SHA,initial_Adam_step=ADAM,new_Adam_step=ADAM+20,first_complete=first,
       original_E2_world_body_pure_transition_stand_sampler_and_reward=True,full_skill_graduation=False))
     elif time.time()-last_saved[0]>=120:save('model_latest_complete')
     put('LATEST_PROGRESS.json',dict(epoch=time.time(),new_PPO_updates=updates[0],new_environment_transitions=updates[0]*480000,
      source_SHA=SHA,initial_Adam_step=ADAM,current_Adam_step=ADAM+20*updates[0]))
     if time.time()>=go['save_deadline'] or (OUT/'STOP_AFTER_SAVE.json').exists() or (Path(log_dir)/'STOP_AFTER_SAVE').exists() or shutil.disk_usage(J).free<8*1024**3:
      save('model_final_complete');raise SavedStop()
     return losses
    runner.alg.update=update;runner.current_learning_iteration=ITER+1
    try:runner.learn(num_learning_iterations=n,init_at_random_ep_len=True)
    except SavedStop:pass
    assert updates[0]>0
    final=save('model_final_complete')
    put('FINAL.json',dict(epoch=time.time(),passed=True,actual_new_PPO_updates=updates[0],new_environment_transitions=updates[0]*480000,
     source_SHA=SHA,final=final,source_cache=cache.receipt(),full_E2_skill=False,complete_SuperMimic=False,
     own_new_artifact_reads='Original full D0-D7/E2 save wrappers and explicit fullsave checks read own new artifacts;selected source is cached,not reopened'))
   rescue_training.learn=work;ns['main']();main_returned[0]=True
  except BaseException:
   put('ORIGINAL_E2_PPO_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),actual_new_PPO_updates=updates[0],source_cache=cache.receipt(),no_automatic_retry=True))
   runner=runner_holder[0]
   if runner is not None and hasattr(runner,'_own_e2_save_complete'):
    try:runner._own_e2_save_complete('model_failed_valid_prefix')
    except BaseException:put('FAILED_PREFIX_SAVE_ERROR.json',dict(error=traceback.format_exc()))
   raise
  finally:
   # Before App.close;Kit may exit the interpreter inside close(). No postclose
   # readcount marker is required,unlike the retained232 readerfalse.
   put('E2_SOURCE_SELECTED_FINAL_READ_COUNTS.json',cache.receipt())
   if ns is not None:
    if not main_returned[0] and runner_holder[0] is not None:
     try:runner_holder[0].env.unwrapped.close()
     except BaseException:put('ENV_CLOSE_ORIGINAL_ERROR.json',dict(error=traceback.format_exc()))
    put('APP_CLOSING.json',dict(epoch=time.time(),readcounts_already_saved=True));ns['app'].close()


if __name__=='__main__':
 try:main()
 except BaseException:
  if OUT is not None and OUT.is_dir() and not (OUT/'ORIGINAL_E2_PPO_ERROR.json').exists():
   put('ORIGINAL_E2_PPO_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),phase='startup',no_automatic_retry=True))
  raise
