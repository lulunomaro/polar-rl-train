"""One W35 PPO fork on one remote4090, original full restore, sole72-issued GO.

No account writer, transport, hardware selection, reward editing or oldcase replay.
The parent owns actual GO→load/train/save/SDKclose/childwait/terminal accounting.
"""
from pathlib import Path
import argparse, hashlib, json, os, runpy, shutil, subprocess, sys, time, traceback

ORIGINAL_SHA='b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd'
SOURCE_SHA='ad504fec819b22f10fd1caf7befc59c1988c7609fe15373ab8851ef95942df3f'
MANIFEST_SHA='0543b0c47c53e15da0d7d017693d2b69f7f6354ef088c3a1b8ed2b9cc56e2beb'
KIND='MOD4_W35_FULL_RM70_208'
AUTHORITY='/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json'
GENERATION='MOD4_SINGLE_WRITER72_20261026'
OUT=None
def H(path):
 with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def put(path,value):
 path=Path(path);temporary=path.with_suffix(path.suffix+'.partial')
 with temporary.open('w',encoding='utf8') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.flush();os.fsync(f.fileno())
 temporary.replace(path)
def read(path):return json.loads(Path(path).read_bytes())

def guard_task_go(task,go):
 assert task['role']=='W35_RM70_FULL208' and task['source_SHA']==SOURCE_SHA and task['original_source_SHA']==ORIGINAL_SHA
 assert task['original_run_manifest_SHA']==MANIFEST_SHA and task['num_envs']==20000
 assert task['source_qualification_kind']==go['source_qualification_kind']==KIND
 assert task['canonical_authority_path']==AUTHORITY and task['authority_generation']==GENERATION
 assert go['source_SHA']==SOURCE_SHA and go['max_parent_seconds']==3900 and go['exit_headroom_seconds']==300
 assert go['original_owner_pid']>0 and go['source_CPU_SHA']==task['source_CPU_SHA']
 assert go['save_deadline']==go['learning_started_epoch']+3600 and go['nominal_end_epoch']==go['learning_started_epoch']+3900
 assert go['GPU_UUID']==task['GPU_UUID'] and go['authority_generation']==GENERATION
 assert task['actual_resource_admission']['compute_UUID_only_rows']==0
 assert task['actual_resource_admission']['GPU_UUID']==task['GPU_UUID']
 assert task['actual_resource_admission']['GPU_name']=='NVIDIA GeForce RTX 4090'
 assert task['actual_USD_gas400_composition_passed'] is True
 assert task['run_id']==go['run_id']
 assert time.time()<go['save_deadline']

def main():
 global OUT
 p=argparse.ArgumentParser();p.add_argument('--job-root',type=Path,required=True);args=p.parse_args();job=args.job_root.resolve()
 task=read(job/'TASK.json');go=read(job/'GO_PRODUCTION.json');guard_task_go(task,go)
 OUT=job/'adaptation';OUT.mkdir()
 assert task['new_RM70_course_source_reviewed'] is True
 assert task['actual_RM70_zeroPT_scene_admission_passed'] is True
 assert task['new_geometry_is_original_shared_CAD_arena'] is True
 os.environ['MOD4_NEW208_JOB_ROOT']=str(job)
 storage=job/'kit_isolation';storage.mkdir()
 for name in ('data','DerivedDataCache'):(storage/name).mkdir()
 (storage/'data/user.config.json').write_text('{}')
 os.environ['MOD4_W35_OWN_KIT_STORAGE_ROOT']=str(storage)
 assert H(__file__)==task['worker_SHA']
 assert H(job/'source/W35_ADAPTED92_FINAL78.pt')==SOURCE_SHA
 assert H(job/'original_run_manifest.json')==MANIFEST_SHA
 assert os.environ.get('CUDA_VISIBLE_DEVICES')==task['GPU_UUID'],'parent must bind one actual UUID before SDK import'
 # UUID-only fresh resource read. An unexpected compute row is left untouched.
 g=subprocess.run(['nvidia-smi','--query-gpu=uuid,name,memory.free,utilization.gpu','--format=csv,noheader,nounits'],capture_output=True,text=True,timeout=15)
 c=subprocess.run(['nvidia-smi','--query-compute-apps=gpu_uuid','--format=csv,noheader'],capture_output=True,text=True,timeout=15)
 assert g.returncode==c.returncode==0
 lines=[x.strip() for x in c.stdout.splitlines() if x.strip() and not x.startswith('No running')]
 assert task['GPU_UUID'] not in lines,'actual selected GPU already has a compute task'
 selected=[x for x in g.stdout.splitlines() if x.split(',')[0].strip()==task['GPU_UUID']];assert len(selected)==1
 _,name,free,util=[x.strip() for x in selected[0].split(',')]
 assert name=='NVIDIA GeForce RTX 4090' and int(free)>15669
 put(OUT/'FRESH_SELECTED_UUID_RESOURCE_BOUNDARY.json',dict(epoch=time.time(),GPU_line=selected[0],selected_compute_UUID_rows=0,no_unknown_PID_inspected=True))
 for key in list(os.environ):
  if key.startswith('RM_') or key in ('RANK','WORLD_SIZE','LOCAL_RANK','MASTER_ADDR','MASTER_PORT'):del os.environ[key]
 original=read(job/'original_run_manifest.json');env={k:str(v) for k,v in original['env'].items() if k not in ('RM_RESCUE_DEADLINE','RM_RESCUE_STOP_FILE')}
 assert env['RM_KEEP_STD']=='1' and env['RM_PHYSICS_DT_S']=='0.0025' and env['RM_SOLVER_POS']=='32' and env['RM_SOLVER_VEL']=='4'
 env.update(RM_MOD4_USD=str(job/'runtime/assets/robot.usd'),RM_RESCUE_STOP_FILE=str(OUT/'STOP_AFTER_SAVE.json'),RM_RESCUE_DEADLINE=str(go['save_deadline']))
 os.environ.update(env);os.environ['MOD4_RESUME_QUEUE_CONTROL_US']='20000'
 os.environ['MOD4_RM70_ORIGINAL_ASSET_ROOT']=str(job/'original_field')
 os.environ['MOD4_RM70_ASSET_RECEIPT']=str(job/'RM70_BINARY_INSTALL_ACTUAL.json')
 os.environ['MOD4_RM70_NEW_LAYOUT_ROOT']=str(OUT/'new_original_CAD_layout')
 put(OUT/'W35_ORIGINAL_ENV_AND_EXACT_FORK_OVERRIDES.json',dict(original_manifest_SHA=MANIFEST_SHA,original_run_name=original['run_name'],actual_env=env,original_reward_PD_STD_LR_parameters_retained=True,explicitly_new_full_original_CAD_course=True,old_G3_remains_frozen=True))
 runtime=job/'runtime';mod=runtime/'isaac/mod4';sys.path[:0]=[str(mod),str(runtime)]
 source=job/'source/W35_ADAPTED92_FINAL78.pt';entry=mod/'train208.py'
 sys.argv=[str(entry),'--headless','--device','cuda:0','--num_envs','20000','--seed','20260928','--steps_per_env','24','--learning_rate','.00011390625000000003','--save_interval','25','--init_checkpoint',str(source),'--log_root',str(OUT/'logs'),'--run_name','W35_FULL_ORIGINAL_RM70_208','--additional_iterations','100000']
 ns=runpy.run_path(str(entry),run_name='owned_W35_PPO50_gas400_config')
 import torch,rescue_training
 from spring_pressure_checkpoint import exact
 class SavedStop(Exception):pass
 def work(runner,n,log_dir):
  runner.logger.writer=None
  real=runner.env.unwrapped;vec=runner.env;full=torch.load(source,map_location='cpu',weights_only=False)
  for key,current in [('actor_state_dict',runner.alg.actor.state_dict()),('critic_state_dict',runner.alg.critic.state_dict()),('optimizer_state_dict',runner.alg.optimizer.state_dict())]:assert exact(current,full[key]),key
  assert runner.current_learning_iteration==32336 and {int(v['step']) for v in runner.alg.optimizer.state_dict()['state'].values()}=={648360}
  assert real.num_envs==20000 and real.physics_dt==.0025 and real.step_dt==.02 and real.cfg.decimation==8 and real._sim_step_counter==0
  assert real._physics_action_delay.queue.control_us==20000
  assert real.spring_pressure_recipe()['nominal_stiffness_N_m']==2000
  receipts=list(Path(log_dir).glob('*STARTUP_VERIFIED.json'))
  required={'SENSOR_RESUME_STARTUP_VERIFIED.json','DELAY_RESUME_STARTUP_VERIFIED.json','ACTION_DELAY_RESUME_STARTUP_VERIFIED.json','SPRING_PRESSURE_RESUME_STARTUP_VERIFIED.json','GAS_DAMPING_RESUME_STARTUP_VERIFIED.json','CHASSIS_PD_RESUME_STARTUP_VERIFIED.json','E1_TERRAIN_RESUME_STARTUP_VERIFIED.json','E1_COMMAND_RETENTION_STARTUP_VERIFIED.json'}
  assert required.issubset({x.name for x in receipts})
  assert len(real._w35_gas400_asset_compatibility['authorized_four_scalar_changes'])==4
  assert real._w35_gas400_selected_bank_compatibility['selected_pose_index']==34
  assert runner.alg.learning_rate==full['optimizer_state_dict']['param_groups'][0]['lr']==.00011390625000000003
  assert real.command_manager.get_term('twist')._dt==.02
  robot=real.scene['robot'];gas_ids=real._spring_pressure.ids
  from spring_nominal_sdk_readback import tensor
  limits=tensor(robot.root_view.get_dof_limits());want=limits.new_tensor([-.0267046843609,.020639440248416612]).expand(20000,2,2)
  assert torch.equal(limits[:,gas_ids],want)
  preload=[];oldwrite=robot.write_data_to_sim
  def witness_prewrite(*aa,**kk):
   if not preload:
    actual=tensor(robot.data.joint_pos_target)[:,gas_ids];expected=actual.new_tensor(real.cfg.events.gas_spring_preload.params['targets']).expand(20000,2)
    assert torch.equal(actual,expected)
    k=real._spring_pressure.component.actual_stiffness(real._spring_pressure.nominal)
    assert torch.equal(tensor(robot.root_view.get_dof_stiffnesses())[:,gas_ids].to(k.device),k)
    preload.append(True);put(OUT/'GAS400_ORIGINAL_PRELOAD_ACTUAL_FIRST_PREWRITE.json',dict(epoch=time.time(),actual_original_preload=True,nominal_k_N_m=2000,nominal_force_N_each=400,gas_upper_m=.020639440248416612,hardware_calibrated=False))
   return oldwrite(*aa,**kk)
  robot.write_data_to_sim=witness_prewrite
  def save(name,updates):
   path=OUT/name;tmp=path.with_suffix('.pt.partial');runner.save(str(tmp));value=torch.load(tmp,map_location='cpu',weights_only=False)
   value['PPO50_gas400_adaptation']=full['PPO50_gas400_adaptation'];value['PPO50_gas400_new_updates']=updates
   value['PPO50_gas400_clock']=dict(policy_hz=50,physics_dt_s=.0025,decimation=8,feedback_hz=100,gamma=.9801,lam=.9025)
   steps={int(x['step']) for x in value['optimizer_state_dict']['state'].values()};assert steps=={648360+20*updates}
   torch.save(value,tmp);tmp.replace(path)
   row=dict(epoch=time.time(),path=str(path),bytes=path.stat().st_size,SHA=H(path),new_updates=updates,Adam_step=next(iter(steps)),not_skill_qualified=True)
   put(OUT/'latest_complete.json',row);return row
  put(OUT/'SOURCE_FULLRESTORE_ZERO_VERIFIED.json',dict(epoch=time.time(),source_SHA=SOURCE_SHA,original_source_SHA=ORIGINAL_SHA,original_actor9_critic8_STD_17Adam_LR_D1_D7_exact=True,actual_algorithm_learning_rate=float(runner.alg.learning_rate),W35_retained_command_and_G3_state_restored=True,receipts=[dict(path=str(x),SHA=H(x)) for x in receipts],own0=save('own_startup0.pt',0)))
  # New same-source clock/plant integration,24controls only; no extra precision
  # or graduation gate. Original per-env2mm reset and termination rules remain.
  reward_dt_calls=[];original_reward_compute=real.reward_manager.compute
  def observed_reward_compute(*aa,**kk):
   dt=kk.get('dt',aa[0] if aa else None);assert dt==.02
   reward_dt_calls.append(float(dt))
   return original_reward_compute(*aa,**kk)
  real.reward_manager.compute=observed_reward_compute
  obs=vec.get_observations();tick=real._integrated_contact.tick;fb=real._feedback_100hz_tick
  with torch.inference_mode():
   for _ in range(24):
    before=real._integrated_contact.tick;before_fb=real._feedback_100hz_tick
    action=runner.alg.actor(obs,stochastic_output=False);obs,reward,done,info=vec.step(action)
    assert real._integrated_contact.tick-before==8 and real._feedback_100hz_tick-before_fb==2
    assert obs['policy'].shape==(20000,35) and obs['critic'].shape==(20000,38) and torch.isfinite(reward).all()
  assert preload and real._integrated_contact.tick-tick==192 and real._feedback_100hz_tick-fb==48 and reward_dt_calls==[.02]*24
  real.reward_manager.compute=original_reward_compute
  for key,current in [('actor_state_dict',runner.alg.actor.state_dict()),('critic_state_dict',runner.alg.critic.state_dict()),('optimizer_state_dict',runner.alg.optimizer.state_dict())]:assert exact(current,full[key]),key
  put(OUT/'CLOCK_GAS400_NATIVE24_ACTUAL.json',dict(epoch=time.time(),passed=True,controls=24,physics_callbacks=192,feedback_samples=48,actual_reward_compute_calls=24,actual_RewardManager_dt_s=.02,reward_dt_applied_once_no_manual_rescale=True,no_optimizer_update=True,not_skill_qualification=True))
  completed=0;oldlog=runner.logger.log;original_step=vec.step
  def checked_step(action):
   before=real._integrated_contact.tick;before_fb=real._feedback_100hz_tick
   result=original_step(action)
   assert real._integrated_contact.tick-before==8 and real._feedback_100hz_tick-before_fb==2
   return result
  vec.step=checked_step
  def log(*aa,**kk):
   nonlocal completed
   oldlog(*aa,**kk);completed+=1
   stop=time.time()>=go['save_deadline'] or shutil.disk_usage(job).free<8*1024**3 or (OUT/'STOP_AFTER_SAVE.json').exists() or (Path(log_dir)/'STOP_AFTER_SAVE').exists()
   if completed==1 or completed%25==0 or stop:put(OUT/'PPO_POSITIVE_CURRENT.json',save('model_update'+str(completed)+'.pt',completed))
   if stop:raise SavedStop()
  runner.logger.log=log
  try:runner.learn(num_learning_iterations=n,init_at_random_ep_len=True)
  except SavedStop:pass
  finally:
   if completed:save('final_valid_update'+str(completed)+'.pt',completed)
  assert completed>0
  put(OUT/'FINAL.json',dict(epoch=time.time(),passed=True,source_SHA=SOURCE_SHA,final=read(OUT/'latest_complete.json'),original_frozen_label_unchanged=True,new_branch_skill_qualified=False))
 rescue_training.learn=work
 try:ns['main']()
 except BaseException:put(OUT/'WORKER_ORIGINAL_ERROR_BEFORE_APP_CLOSE.json',dict(epoch=time.time(),traceback=traceback.format_exc()));raise
 finally:
  put(OUT/'APP_CLOSING.json',dict(epoch=time.time()));ns['app'].close();put(OUT/'APP_CLOSED.json',dict(epoch=time.time()))

if __name__=='__main__':
 try:main()
 except BaseException:
  if OUT and OUT.exists():put(OUT/'WORKER_ORIGINAL_ERROR.json',dict(epoch=time.time(),traceback=traceback.format_exc(),no_automatic_retry=True))
  raise
