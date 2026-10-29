"""One bounded E0 mean-policy diagnostic; original command/reset/plant unchanged."""
from pathlib import Path
import argparse,hashlib,json,os,runpy,sys,time,traceback
MODEL_SHA='a92c9e8d7cb3dbda9828b6c37bb38dd63183818e91b1aa3f7746c2c46379c74a'
ORIGINAL_MANIFEST_SHA='1dbde5972c65baf8842bc82024fe7ddfd6393d73a51137cc9880ed6310ff1af1'
GPU='GPU-90a66ae2-f536-7033-79c0-487536ae36d3';OUT=None

def H(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def put(n,v):
 with (OUT/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def guard(task):
 assert task['kind']=='MOD4_E0_ADAPTED82_NEW86_FROZEN_PROFILE_DOMAIN_V1' and task['source_SHA']==MODEL_SHA
 assert task['num_envs']==20000 and task['controls']==1000 and task['warmup_controls']==100 and task['maximum_worker_seconds']==1680
 assert task['no_optimizer_steps'] and task['actual_target86_SDK_admission_passed'] and task['actual_private_GPU_EX_held_by_parent']
 assert task['canonical72_known_owner_readonly_passed'] and task['domain_kind']=='E0_DIRECTIONAL_SPIN_V1'
 assert task['original_Adam']==641200 and task['original_LR']==.00038443359375000017

def main():
 global OUT
 p=argparse.ArgumentParser();p.add_argument('--job-root',required=True,type=Path);a=p.parse_args();job=a.job_root.resolve();task=read(job/'FROZEN_CASE_TASK.json');guard(task)
 assert os.environ.get('CUDA_VISIBLE_DEVICES')==GPU
 assert H(__file__)==task['worker_SHA']
 assert H(job/'e0_long_command_domain_telemetry_v1.py')==task['telemetry_component_SHA']
 assert H(job/'GROUND_PROVIDER_SOURCE_CONTRACT.json')==task['ground_provider_contract_SHA']
 assert H(job/'E0_TARGET_SOURCE_SDK_METADATA_ACTUAL.json')==task['actual_CPU_report_SHA']
 assert H(job/'E0_NEW86_CPU_ORIGINAL_WAIT_PROOF.json')==task['actual_CPU_waited_proof_SHA']
 cw=read(job/'E0_NEW86_CPU_ORIGINAL_WAIT_PROOF.json');assert cw['passed'] and cw['actual_waited'] and cw['returncode']==0
 OUT=job/'frozen_regression';OUT.mkdir();deadline=time.time()+1680;source=job/'source/E0_ADAPTED89D_FINAL82.pt'
 assert source.stat().st_size==14031973 and H(source)==MODEL_SHA
 original=read(job/'original_run_manifest.json');assert H(job/'original_run_manifest.json')==ORIGINAL_MANIFEST_SHA
 for k in list(os.environ):
  if k.startswith('RM_') or k in ('RANK','WORLD_SIZE','LOCAL_RANK','MASTER_ADDR','MASTER_PORT'):del os.environ[k]
 env={k:str(v) for k,v in original['env'].items() if k not in ('RM_RESCUE_STOP_FILE','RM_RESCUE_DEADLINE')}
 assert env['RM_KEEP_STD']=='1' and env['RM_PHYSICS_DT_S']=='0.0025' and env['RM_SOLVER_POS']=='32' and env['RM_SOLVER_VEL']=='4'
 env.update(RM_MOD4_USD=str(job/'runtime/assets/robot.usd'),RM_RESCUE_STOP_FILE=str(OUT/'STOP.json'),RM_RESCUE_DEADLINE=str(deadline))
 os.environ.update(env);os.environ['MOD4_RESUME_QUEUE_CONTROL_US']='20000'
 put('ORIGINAL_E0_ENV_AND_DECLARED_FORK_OVERRIDES.json',dict(original_manifest_SHA=ORIGINAL_MANIFEST_SHA,actual_env=env,original_E0_flat_command_and_DR_retained=True,no_W35_terrain_or_profile_assumption=True))
 mod=job/'runtime/isaac/mod4';sys.path[:0]=[str(job),str(job/'lib'),str(mod),str(job/'runtime')];entry=mod/'train_chassis_pd_resume_ppo.py'
 sys.argv=[str(entry),'--headless','--device','cuda:0','--num_envs','20000','--seed','20260928','--steps_per_env','24','--learning_rate','.00038443359375000017','--save_interval','25','--init_checkpoint',str(source),'--log_root',str(OUT/'logs'),'--run_name','FROZEN_E0_82_PROFILE_DOMAIN_NO_PPO','--additional_iterations','1']
 ns=runpy.run_path(str(entry),run_name='frozen_E0_original82_restore_config')
 import torch,rescue_training
 from spring_pressure_checkpoint import exact
 from spring_nominal_sdk_readback import tensor
 from e0_long_command_domain_telemetry_v1 import E0Panel
 def clone(v):
  if torch.is_tensor(v):return v.detach().clone()
  if isinstance(v,dict):return {k:clone(x) for k,x in v.items()}
  if isinstance(v,list):return [clone(x) for x in v]
  if isinstance(v,tuple):return tuple(clone(x) for x in v)
  return v
 def work(runner,n,log_dir):
  runner.logger.writer=None;runner.alg.learning_rate=runner.alg.optimizer.param_groups[0]['lr'];real=runner.env.unwrapped;vec=runner.env;robot=real.scene['robot'];cmd=real.command_manager.get_term('twist')
  assert real.num_envs==20000 and real.physics_dt==.0025 and real.step_dt==.02 and real.cfg.decimation==8 and real._sim_step_counter==0
  assert real._physics_action_delay.queue.control_us==20000 and real.spring_pressure_recipe()['nominal_stiffness_N_m']==2000
  assert runner.current_learning_iteration==31984 and runner.alg.learning_rate==.00038443359375000017
  assert len(runner.alg.optimizer.state_dict()['state'])==17 and {int(x['step']) for x in runner.alg.optimizer.state_dict()['state'].values()}=={641200}
  receipts=list(Path(log_dir).glob('*STARTUP_VERIFIED.json'));required={'SENSOR_RESUME_STARTUP_VERIFIED.json','DELAY_RESUME_STARTUP_VERIFIED.json','ACTION_DELAY_RESUME_STARTUP_VERIFIED.json','SPRING_PRESSURE_RESUME_STARTUP_VERIFIED.json','GAS_DAMPING_RESUME_STARTUP_VERIFIED.json','CHASSIS_PD_RESUME_STARTUP_VERIFIED.json'}
  assert required<={x.name for x in receipts}
  from gas400_reset_bank_exact_compatibility_v1 import check_runtime_source
  bank=check_runtime_source(mod);assert bank['passed'] and bank['pose_ranges']['original_height_filter_selected_poses']==74
  gas_ids=real._spring_pressure.ids;limits=tensor(robot.root_view.get_dof_limits());want=limits.new_tensor([-.0267046843609,.020639440248416612]).expand(20000,2,2);assert torch.equal(limits[:,gas_ids],want)
  assert not cmd.manual_evaluation_mode and cmd._dt==.02 and cmd.progress_goal==.5 and cmd.pure_max==4*__import__('math').pi
  assert real.cfg.episode_length_s==20 and tuple(cmd.cfg.resampling_time_range)==(12.,16.)
  assert H(mod/'directional_spin_runtime.py')=='8fed717b0d2ba77491c252b183f9462f49457402d96927cc441c88ecd36b1cd8'
  runner.alg.actor.eval();runner.alg.critic.eval();before={k:clone(v.state_dict()) for k,v in [('actor',runner.alg.actor),('critic',runner.alg.critic),('optimizer',runner.alg.optimizer)]}
  # Initial current core tensors must match the already-qualified formal CPU witness.
  witness=read(job/'E0_EXISTING_FORMAL_WHOLE_CPU_WITNESS.json');wanted={r['path']:r for r in witness['review']['new_final_tensor_fingerprints']};seen=[]
  def check(v,path):
   if torch.is_tensor(v):
    row=wanted[path];raw=v.detach().cpu().contiguous().reshape(-1).view(torch.uint8).numpy().tobytes()
    assert row['shape']==list(v.shape) and row['dtype']==str(v.dtype) and row['SHA']==hashlib.sha256(raw).hexdigest(),path;seen.append(path)
   elif isinstance(v,dict):
    for k,x in v.items():check(x,path+'/'+str(k))
   elif isinstance(v,(list,tuple)):
    for k,x in enumerate(v):check(x,path+'/'+str(k))
  for k,name in [('actor','actor_state_dict'),('critic','critic_state_dict'),('optimizer','optimizer_state_dict')]:check(before[k],'/'+name)
  put('ACTUAL_E0_82_CUDA_FULLRESTORE_BEFORE_MEAN_ACTION.json',dict(passed=True,source_SHA=MODEL_SHA,Adam_step=641200,stored_RSL_iteration=31984,actual_constructor_algorithm_optimizer_LR=runner.alg.learning_rate,current_core_tensor_fingerprints_matched=len(seen),D1_D7_original_CUDA_restore_receipts=[dict(path=str(q),value=read(q)) for q in receipts],original_E0_command_bank74_reset_retained=True,no_optimizer_norm_update=True))
  declarations=[dict(name=k,time_out=bool(real.termination_manager.get_term_cfg(k).time_out),function=repr(real.termination_manager.get_term_cfg(k).func),parameters=repr(real.termination_manager.get_term_cfg(k).params)) for k in real.termination_manager.active_terms]
  put('ORIGINAL_E0_COMMAND_AND_TERMINATION_CRITERIA.json',dict(command_kind='E0_DIRECTIONAL_SPIN_V1',resampling_time_range=list(cmd.cfg.resampling_time_range),standing_fraction=.1,pure_fraction=.3,moving_fraction=.2,transition_fraction_within_pure=1/3,moving_yaw_signed_abs_rad_s=[1,2],pure_yaw_abs_rad_s=[1,4*__import__('math').pi],world_progress_goal_m_s=.5,height_command_m=.25,criterion_terms=declarations,original_criteria_unmodified=True,graduated_skill_claim=False))
  panel=E0Panel(real,torch,OUT,task);oldterm=real.termination_manager.compute;oldreward=real.reward_manager.compute;oldwrite=robot.write_data_to_sim;reward_calls=[];preload=[];completed=0;coverage=True;last=0
  def term(*aa,**kk):
   nonlocal coverage
   value=oldterm(*aa,**kk);tm=real.termination_manager;non_timeout=torch.zeros_like(tm.terminated);timeouts=torch.zeros_like(tm.time_outs)
   for k in tm.active_terms:
    if tm.get_term_cfg(k).time_out:timeouts|=tm.get_term(k).bool()
    else:non_timeout|=tm.get_term(k).bool()
   coverage=coverage and bool(torch.equal(non_timeout,tm.terminated)) and bool(torch.equal(timeouts,tm.time_outs));panel.terminal();return value
  def reward(*aa,**kk):
   dt=kk.get('dt',aa[0] if aa else None);assert dt==.02;reward_calls.append(float(dt));return oldreward(*aa,**kk)
  def prewrite(*aa,**kk):
   if not preload:
    target=tensor(robot.data.joint_pos_target)[:,gas_ids];expected=target.new_tensor(real.cfg.events.gas_spring_preload.params['targets']).expand(20000,2);assert torch.equal(target,expected)
    k=real._spring_pressure.component.actual_stiffness(real._spring_pressure.nominal);assert torch.equal(tensor(robot.root_view.get_dof_stiffnesses())[:,gas_ids].to(k.device),k);preload.append(True)
   return oldwrite(*aa,**kk)
  real.termination_manager.compute=term;real.reward_manager.compute=reward;robot.write_data_to_sim=prewrite;obs=vec.get_observations();tick=real._integrated_contact.tick;fb=real._feedback_100hz_tick
  try:
   with torch.inference_mode():
    for i in range(1000):
     if time.time()>=deadline:break
     if (Path(log_dir)/'STOP_AFTER_SAVE').exists():raise RuntimeError('Original E0 health observer requested stop; original reason retained')
     panel.begin(i,obs);action=runner.alg.actor(obs,stochastic_output=False);panel.requested(action);obs,rewards,done,info=vec.step(action);panel.after(i)
     assert obs['policy'].shape==(20000,35) and obs['critic'].shape==(20000,38) and torch.isfinite(obs['policy']).all() and torch.isfinite(obs['critic']).all() and torch.isfinite(rewards).all();completed+=1
     if completed==24:
      assert preload and int(real._integrated_contact.tick)-tick==192 and int(real._feedback_100hz_tick)-fb==48 and reward_calls==[.02]*24 and panel.apply_calls=={'legs':192,'wheels':192} and panel.trace_controls==list(range(1,25))
      put('ACTUAL_NATIVE24_E0_40050_CLOCK_QUEUE.json',dict(passed=True,source_SHA=MODEL_SHA,controls=24,physics_callbacks=192,feedback_samples=48,legs_queue_apply=192,wheels_queue_apply=192,trace_controls=panel.trace_controls,RewardManager_calls=24,RewardManager_dt_s=.02,original_preload_actual=True,original_Adam641200_unchanged=True,policy_hz=50,nominal_force_N_each=400,no_optimizer_update=True))
     if time.time()-last>=25:put('E0_PROFILE_PROGRESS_'+str(completed).zfill(4)+'.json',dict(epoch=time.time(),controls=completed,seconds=completed*.02,not_skill_acceptance=True));print(json.dumps(dict(stage='ACTUAL_FROZEN_E0_PROFILE_DOMAIN',controls=completed)),flush=True);last=time.time()
   assert completed>0 and coverage and len(reward_calls)==completed
   assert all(exact(v.state_dict(),before[k]) for k,v in [('actor',runner.alg.actor),('critic',runner.alg.critic),('optimizer',runner.alg.optimizer)])
   assert runner.alg.learning_rate==.00038443359375000017 and runner.current_learning_iteration==31984
   panel.finish()
   put('BOUNDED_FROZEN_E0_N20K_PROFILES_ACTUAL.json',dict(passed_execution=True,source_SHA=MODEL_SHA,num_envs=20000,requested_controls=1000,controls=completed,simulated_seconds=completed*.02,warmup_controls=min(100,completed),steady_controls=max(0,completed-100),wall_time_limited=completed<1000,core_actor_critic_STD_norm_optimizer_literal_unchanged=True,all17_Adam_steps=641200,actual_LR_unchanged=.00038443359375000017,termination_and_truncation_union_exact=coverage,complete_typed_WM_dataset=False,skill_graduation=False,coverage_pending_original_acceptance=True,profile_report='E0_PROFILE_DOMAIN_DIAGNOSTIC_ACTUAL.json'))
  finally:real.termination_manager.compute=oldterm;real.reward_manager.compute=oldreward;robot.write_data_to_sim=oldwrite;panel.uninstall()
 rescue_training.learn=work
 try:ns['main']()
 except BaseException:put('FROZEN_E0_ORIGINAL_EXCEPTION_BEFORE_APP_CLOSE.json',dict(epoch=time.time(),traceback=traceback.format_exc(),original_exception_captured_before_SDKclose=True));raise
 finally:put('APP_CLOSING.json',dict(epoch=time.time()));ns['app'].close()

if __name__=='__main__':
 try:main()
 except BaseException:
  if OUT and OUT.exists():put('FROZEN_E0_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),traceback=traceback.format_exc(),no_optimizer_or_source_promotion=True))
  raise
