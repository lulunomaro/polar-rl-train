"""Bounded frozen W35 mean regression; original G3/command/reset, no optimizer."""
from pathlib import Path
import argparse,hashlib,json,math,os,runpy,sys,time,traceback
MODEL_SHA='ad504fec819b22f10fd1caf7befc59c1988c7609fe15373ab8851ef95942df3f'
GPU='GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e';OUT=None

def H(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def read(p):return json.loads(Path(p).read_bytes())

def put(n,v):
 with (OUT/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)

def main():
 global OUT
 p=argparse.ArgumentParser();p.add_argument('--job-root',type=Path,required=True);a=p.parse_args();job=a.job_root.resolve();task=read(job/'FROZEN_CASE_TASK.json')
 assert task['kind']=='MOD4_W35_ADAPTED92_ORIGINAL_N20K_FROZEN_PROFILES_V1' and task['source_SHA']==MODEL_SHA and task['num_envs']==20000 and task['controls']==1200 and task['warmup_controls']==100 and task['maximum_worker_seconds']==1680 and task['no_optimizer_steps']
 assert task['actual_source210_SDK_admission_passed'] and task['actual_private_GPU_EX_held_by_parent'] and task['canonical72_known_owner_readonly_passed'] and os.environ.get('CUDA_VISIBLE_DEVICES')==GPU
 OUT=job/'frozen_regression';OUT.mkdir();deadline=time.time()+1680;source=job/'source/W35_ADAPTED92_FINAL78.pt';assert H(source)==MODEL_SHA and source.stat().st_size==17619013
 K=job/'kit_isolation';assert not K.exists();K.mkdir()
 for name in ('data','DerivedDataCache'):(K/name).mkdir()
 with (K/'data/user.config.json').open('x') as f:f.write('{}')
 os.environ['MOD4_W35_OWN_KIT_STORAGE_ROOT']=str(K)
 original=read(job/'original_run_manifest.json');assert H(job/'original_run_manifest.json')=='0543b0c47c53e15da0d7d017693d2b69f7f6354ef088c3a1b8ed2b9cc56e2beb'
 for k in list(os.environ):
  if k.startswith('RM_') or k in ('RANK','WORLD_SIZE','LOCAL_RANK','MASTER_ADDR','MASTER_PORT'):del os.environ[k]
 env={k:str(v) for k,v in original['env'].items() if k not in ('RM_RESCUE_STOP_FILE','RM_RESCUE_DEADLINE')};assert env['RM_HEIGHT_MIN']==env['RM_HEIGHT_MAX']=='.25' and env['RM_KEEP_STD']=='1'
 env.update(RM_MOD4_USD=str(job/'runtime/assets/robot.usd'),RM_RESCUE_STOP_FILE=str(OUT/'STOP.json'),RM_RESCUE_DEADLINE=str(deadline));os.environ.update(env);os.environ['MOD4_RESUME_QUEUE_CONTROL_US']='20000'
 mod=job/'runtime/isaac/mod4';sys.path[:0]=[str(job/'lib'),str(mod),str(job/'runtime')];entry=mod/'train_e1_retention_named_owned_resume_ppo.py'
 sys.argv=[str(entry),'--headless','--device','cuda:0','--num_envs','20000','--seed','20260928','--steps_per_env','24','--learning_rate','.00011390625000000003','--save_interval','25','--init_checkpoint',str(source),'--log_root',str(OUT/'logs'),'--run_name','FROZEN_W35_40050_PROFILES_NO_PPO','--additional_iterations','1']
 import zonglin2_app_launcher as own_launcher;assert Path(own_launcher.__file__).resolve()==job/'lib/zonglin2_app_launcher.py'
 ns=runpy.run_path(str(entry),run_name='frozen_W35_original92_restore_config')
 import carb
 settings=carb.settings.get_settings();assert Path(settings.get('/UJITSO/datastore/localCachePath')).resolve()==K/'DerivedDataCache' and Path(settings.get('/app/userConfigPath')).resolve()==K/'data/user.config.json'
 assert settings.get('/physics/cooking/ujitsoCollisionCooking') is True and settings.get('/physics/cooking/ujitsoRemoteCacheEnabled') is False and settings.get('/persistent/physics/cooking/ujitsoCookingMaxProcessCount')==16
 put('ACTUAL_OWN_KIT_STORAGE_PATHS_BEFORE_ENV.json',dict(cache=str(K/'DerivedDataCache'),user_config=str(K/'data/user.config.json'),cooking_controls_unchanged=True,no_old_cache_change=True))
 import torch,numpy as np,rescue_training
 from spring_pressure_checkpoint import exact
 from spring_nominal_sdk_readback import tensor
 def work(runner,n,log_dir):
  runner.logger.writer=None;runner.alg.learning_rate=runner.alg.optimizer.param_groups[0]['lr'];real=runner.env.unwrapped;vec=runner.env;cmd=real.command_manager.get_term('twist');robot=real.scene['robot']
  assert real.num_envs==20000 and real.physics_dt==.0025 and real.step_dt==.02 and real.cfg.decimation==8 and real._sim_step_counter==0 and real._physics_action_delay.queue.control_us==20000
  assert runner.current_learning_iteration==32336 and runner.alg.learning_rate==.00011390625000000003 and {int(x['step']) for x in runner.alg.optimizer.state_dict()['state'].values()}=={648360}
  assert real.spring_pressure_recipe()['nominal_stiffness_N_m']==2000 and real._w35_gas400_selected_bank_compatibility['selected_pose_index']==34 and len(real._w35_gas400_asset_compatibility['authorized_four_scalar_changes'])==4
  receipts=list(Path(log_dir).glob('*STARTUP_VERIFIED.json'));required={'SENSOR_RESUME_STARTUP_VERIFIED.json','DELAY_RESUME_STARTUP_VERIFIED.json','ACTION_DELAY_RESUME_STARTUP_VERIFIED.json','SPRING_PRESSURE_RESUME_STARTUP_VERIFIED.json','GAS_DAMPING_RESUME_STARTUP_VERIFIED.json','CHASSIS_PD_RESUME_STARTUP_VERIFIED.json','E1_TERRAIN_RESUME_STARTUP_VERIFIED.json','E1_COMMAND_RETENTION_STARTUP_VERIFIED.json'};assert required<={x.name for x in receipts}
  for q in receipts:assert read(q).get('source_sha256',MODEL_SHA)==MODEL_SHA
  runner.alg.actor.eval();runner.alg.critic.eval();before={k:{name:value.detach().clone() for name,value in model.state_dict().items()} for k,model in [('actor',runner.alg.actor),('critic',runner.alg.critic)]};opt={k:{name:value.detach().clone() if torch.is_tensor(value) else value for name,value in row.items()} for k,row in runner.alg.optimizer.state_dict()['state'].items()}
  put('ACTUAL_ORIGINAL_N20K_W35_CUDA_FULLRESTORE_BEFORE_MEAN_ACTION.json',dict(passed=True,source_SHA=MODEL_SHA,Adam_step=648360,stored_RSL_iteration=32336,actual_algorithm_and_optimizer_LR=runner.alg.learning_rate,receipts=[dict(path=str(q),value=read(q)) for q in receipts],original_D1_D7_G3_retained_command_nearest250_reset_preserved=True,no_PPO_norm_or_optimizer_update=True))
  names=list(real.termination_manager.active_terms);declared=[dict(name=name,time_out=bool(real.termination_manager.get_term_cfg(name).time_out),function=repr(real.termination_manager.get_term_cfg(name).func),parameters=repr(real.termination_manager.get_term_cfg(name).params)) for name in names]
  put('ORIGINAL_W35_TASK_COMMAND_AND_TERMINATION_CRITERIA.json',dict(original_run_manifest_SHA=H(job/'original_run_manifest.json'),height_command_m=.25,original_selected_root_height_m=.252,retained_command_scope=cmd.audit_retention(),criterion_terms=declared,original_reward_reset_thresholds_unmodified=True,original_legacy_backend_graduation_not_inherited=True))
  ids=torch.arange(32,device=real.device);frames=[];metrics=[];ctx={};terminal=[None];previous_key=torch.full((20000,),-99,device=real.device,dtype=torch.long);age=torch.zeros(20000,device=real.device);turn=torch.zeros_like(age);max_age=torch.zeros(42,device=real.device);cycles=torch.zeros(42,device=real.device,dtype=torch.long);counts=torch.zeros((2,42),device=real.device,dtype=torch.long);failures={name:torch.zeros((2,42),device=real.device,dtype=torch.long) for name in names};coverage=[True];oldterm=real.termination_manager.compute
  def term(*aa,**kk):
   nonlocal previous_key,age,turn
   result=oldterm(*aa,**kk);tm=real.termination_manager;terminal[0]=dict(root13=tensor(robot.data.root_state_w)[ids].clone(),q30=tensor(robot.data.joint_pos)[ids].clone(),dq30=tensor(robot.data.joint_vel)[ids].clone(),executed6=real.action_manager.action[ids].clone(),terminated=tm.terminated[ids].clone(),truncated=tm.time_outs[ids].clone())
   control=len(metrics);phase=0 if control<100 else 1;key=ctx['profile_key'];live=~(tm.terminated|tm.time_outs);angle=tensor(robot.data.heading_w);delta=torch.atan2(torch.sin(angle-ctx['heading']),torch.cos(angle-ctx['heading']));same=(key==previous_key)
   if control==100:same=torch.zeros_like(same)
   age=torch.where(same,age+.02,torch.full_like(age,.02));turn=torch.where(same,turn+delta,delta);valid=(key>=0)&(key<42);counts[phase].add_(torch.bincount(key[valid],minlength=42));max_age.scatter_reduce_(0,key[valid],age[valid],reduce='amax',include_self=True)
   actual=torch.zeros_like(tm.terminated);timeouts=torch.zeros_like(tm.time_outs)
   for name in names:
    mask=tm.get_term(name).bool();failures[name][phase].add_(torch.bincount(key[mask&valid],minlength=42))
    if real.termination_manager.get_term_cfg(name).time_out:timeouts|=mask
    else:actual|=mask
   coverage[0]=coverage[0] and bool(torch.equal(actual,tm.terminated)) and bool(torch.equal(timeouts,tm.time_outs))
   moving=ctx['moving']&live&(phase==1);completed=torch.floor((turn*torch.sign(ctx['command'][:,2])).clamp_min(0)/(2*math.pi)).long();eligible=moving&(completed>0)
   if eligible.any():cycles.index_add_(0,key[eligible],completed[eligible]);turn[eligible]-=torch.sign(ctx['command'][eligible,2])*(2*math.pi)*completed[eligible]
   bodyv=tensor(robot.data.root_lin_vel_b);yaw=tensor(robot.data.root_ang_vel_b)[:,2];height=tensor(robot.data.root_pos_w)[:,2]-real._mod4_ground_z;command=ctx['command'];moving_count=int(ctx['moving'].sum());worldv=tensor(robot.data.root_lin_vel_w);progress=worldv[:,0]*torch.cos(ctx['direction'])+worldv[:,1]*torch.sin(ctx['direction'])
   metrics.append(dict(control=control+1,phase='warmup' if phase==0 else 'steady',physics_tick=int(real._sim_step_counter),forward_abs_tracking_error_mean=float((command[:,0]-bodyv[:,0]).abs().mean()),yaw_abs_tracking_error_mean=float((command[:,2]-yaw).abs().mean()),height_command_m=.25,height_abs_error_mean=float((height-.25).abs().mean()),root_local_ground_height_min=float(height.min()),root_local_ground_height_max=float(height.max()),moving_world_progress_abs_error_mean=float((progress[ctx['moving']]-.5).abs().mean()) if moving_count else None,terminated_count=int(tm.terminated.sum()),truncated_count=int(tm.time_outs.sum()),profile_counts=torch.bincount(key[valid],minlength=42).cpu().tolist()))
   age[~live]=0;turn[~live]=0;previous_key=torch.where(live,key,torch.full_like(key,-99));return result
  real.termination_manager.compute=term;obs=vec.get_observations();completed=0;last=0
  with torch.inference_mode():
   for i in range(1200):
    if time.time()>=deadline:break
    if (Path(log_dir)/'STOP_AFTER_SAVE').exists():raise RuntimeError('original E1 health observer requested integrity stop; original reason retained')
    mode=torch.zeros(20000,device=real.device,dtype=torch.long);mode[cmd.is_standing_env]=1;mode[cmd.linear&(cmd.linear_vx<0)]=2;mode[cmd.linear&(cmd.linear_vx>0)]=3;mode[cmd.moving&(cmd.signed_yaw<0)]=4;mode[cmd.moving&(cmd.signed_yaw>0)]=5;mode[cmd.eligible_flat&~cmd.is_standing_env&~cmd.linear&~cmd.moving]=6
    ctx.update(profile_key=(cmd.family+1)*7+mode,command=cmd.command.clone(),moving=cmd.moving.clone(),direction=cmd.direction.clone(),heading=tensor(robot.data.heading_w).clone());root=tensor(robot.data.root_state_w)[ids].clone();q=tensor(robot.data.joint_pos)[ids].clone();dq=tensor(robot.data.joint_vel)[ids].clone();tick=real._integrated_contact.tick;fb=real._feedback_100hz_tick;action=runner.alg.actor(obs,stochastic_output=False);requested=action[ids].clone();terminal[0]=None;obs,reward,done,info=vec.step(action)
    assert real._integrated_contact.tick-tick==8 and real._feedback_100hz_tick-fb==2 and terminal[0] is not None and obs['policy'].shape==(20000,35) and obs['critic'].shape==(20000,38) and torch.isfinite(reward).all() and torch.isfinite(obs['policy']).all() and torch.isfinite(obs['critic']).all()
    row=dict(before_root13=root,before_q30=q,before_dq30=dq,requested6=requested,command3=ctx['command'][ids],profile_key=ctx['profile_key'][ids],**terminal[0]);frames.append({k:v.cpu().numpy() for k,v in row.items()});completed+=1
    if completed==24:put('ACTUAL_NATIVE24_W35_40050_MEAN.json',dict(passed=True,controls=24,physics_callbacks=192,feedback_samples=48,policy_hz=50,nominal_force_N_each=400,Adam_step_unchanged=648360,no_optimizer_update=True))
    if time.time()-last>=25:put('PROFILE_PROGRESS_'+str(completed).zfill(4)+'.json',dict(epoch=time.time(),controls=completed,seconds=completed*.02,original_command_audit=cmd.audit_retention()));print(json.dumps(dict(stage='ACTUAL_W35_FROZEN20K_PROFILES',controls=completed,simulated_seconds=completed*.02)),flush=True);last=time.time()
  real.termination_manager.compute=oldterm;assert completed>0 and coverage[0] and all(exact(model.state_dict(),before[k]) for k,model in [('actor',runner.alg.actor),('critic',runner.alg.critic)]) and exact(runner.alg.optimizer.state_dict()['state'],opt)
  path=OUT/'selected32_full_motion_before_and_terminal.npz'
  with path.open('xb') as f:np.savez_compressed(f,**{k:np.stack([x[k] for x in frames]) for k in frames[0]})
  put('BOUNDED_FROZEN_W35_N20K_PROFILES_ACTUAL.json',dict(passed_execution=True,source_SHA=MODEL_SHA,source_adaptation_updates=78,controls=completed,simulated_seconds=completed*.02,requested_controls=1200,warmup_controls=min(completed,100),steady_controls=max(0,completed-100),wall_time_limited=completed<1200,num_envs=20000,all_population_metrics=metrics,warmup_and_steady_profile_control_counts=counts.cpu().tolist(),profile_maximum_continuous_seconds=max_age.cpu().tolist(),steady_actual_complete_signed_world_cycles_no_cross_reset=cycles.cpu().tolist(),original_termination_reason_counts={n:x.cpu().tolist() for n,x in failures.items()},termination_and_truncation_union_exact=coverage[0],original_command_audit_final=cmd.audit_retention(),core_actor_critic_STD_norm_optimizer_literal_unchanged=True,all17_Adam_steps=648360,no_optimizer_step_no_norm_update=True,actual_mean_policy=True,source_entry_retains_original_full_population_pre_reset_retention_trace=True,selected32_motion_trace=dict(path=str(path),bytes=path.stat().st_size,SHA=H(path),endpoint_before_autoreset=True),skill_graduation=False,skill_status='PENDING original full frozen acceptance and uncovered scenario review; report actual coverage/failures without inherited labels',complete_typed_WM_dataset=False))
 rescue_training.learn=work
 try:ns['main']()
 except BaseException:
  put('FROZEN_W35_ORIGINAL_EXCEPTION_BEFORE_APP_CLOSE.json',dict(epoch=time.time(),exception_type=type(sys.exc_info()[1]).__name__,traceback=traceback.format_exc(),original_exception_captured_before_SDKclose=True));raise
 finally:put('APP_CLOSING.json',dict(epoch=time.time()));ns['app'].close()

if __name__=='__main__':
 try:main()
 except BaseException:
  if OUT and OUT.exists():put('FROZEN_W35_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),traceback=traceback.format_exc(),no_source_promotion_or_optimizer_step=True))
  raise
