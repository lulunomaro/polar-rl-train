"""Independent low80 first-episode confirmation. Not the original 74+6 E3 score.
Each of three case processes has its own constructor seed and one selected-source
CPU read/hash/decode. No reference case, learning, model selection or lock acquire.
"""
from pathlib import Path
import json,os,runpy,sys,time,traceback
from fudan_frozen_eval_safe import KIND,INTERFACE,WholeFDNCheckpointCache,task_args,put,wait_start,close_original_resources
from launch_storage_contract import parent_five_storage
from n80_gpu_capacity import capacity_ctor

def main():
 task,out,group=task_args();role=task['role'];B=Path(task['runtime_root']);mod=B/'runtime/isaac/mod4';namespace=env=cache=policy=oldterm=None;execution_error=None;started_wall=time.time();completed=0;max_returned=max_applied=0.
 try:
  original=json.loads((B/'original_run_manifest.json').read_bytes())['env']
  for key in list(os.environ):
   if key.startswith('RM_')or key in('RANK','WORLD_SIZE','LOCAL_RANK','MASTER_ADDR','MASTER_PORT'):del os.environ[key]
  os.environ.update({k:str(v)for k,v in original.items()if k not in('RM_RESCUE_STOP_FILE','RM_RESCUE_DEADLINE','RM_SLOPE_INITIAL_ADMISSION')})
  os.environ.update(RM_MOD4_USD=str(B/'runtime/assets/robot.usd'),RM_KEEP_STD='1',RM_PHYSICS_DT_S='0.0025',RM_SOLVER_POS='32',RM_SOLVER_VEL='4',MOD4_RESUME_QUEUE_CONTROL_US='20000')
  storage=parent_five_storage(B,out);storage.mkdir();(storage/'data').mkdir();(storage/'DerivedDataCache').mkdir();(storage/'data/user.config.json').write_text('{}')
  os.environ['WP_CACHE_DIR']=str(out/'warp_cache');os.environ['PYTHONDONTWRITEBYTECODE']='1'
  os.environ.update(MOD4V1_E3_ASSET_DIR=str(B/'runtime/assets'),MOD4V1_E3_JOB_ROOT=str(B),MOD4V1_E3_KIT_STORAGE_ROOT=str(storage),OWN_E2_H1_KIND='E3_PUBLIC_RECOVERY',RM_SPAWN_GRACE_STEPS='5',RM_JUMP_SCRIPT_PROB='0',RM_MOD4_MAP='',RM_MOD4_TERRAIN='flat')
  entry=mod/'train_mod4v1_e3.py';sys.path[:0]=[str(Path(__file__).resolve().parent),str(B/'lib'),str(mod),str(B/'runtime'),str(B),str(out)]
  assert os.environ.get('CUDA_VISIBLE_DEVICES')==task['GPU_UUID']
  from mod4v1_fresh_dr_guard import FreshDRNominalGuard
  sys.argv=[str(entry),'--headless','--device','cuda:0','--num_envs','80','--seed',str(task['seed']),'--dry_run','400']
  import torch
  cache=WholeFDNCheckpointCache(torch,task)
  def no_other_checkpoint(*args,**kwargs):raise RuntimeError('Only this independently cached selected55afa source permitted; no reference/other PT')
  torch.load=no_other_checkpoint
  namespace=runpy.run_path(str(entry),run_name='fudan_low80_confirmation_build_no_training_main')
  import low80_confirmation_phase_v1 as scope
  scope.install_before_build();factory=namespace['build_env'];factory.__globals__['Mod4Env']=capacity_ctor(factory.__globals__['Mod4Env']);env=factory();identity=namespace['E3_IDENTITY']
  from mild_dr import tensor
  from actual_DR_memory_getter272 import RuntimeOrderBinding,ActualDRMemoryGetter
  import pose_cache_runtime_adapter_v4 as pose_module
  from app_close_semantics_v6 import BoundedPoseCacheEventsV5
  scope.bind_after_build(env,B);pose_receipt=[None]
  def pose_emit(event):pose_receipt[0]=event
  pose_events=BoundedPoseCacheEventsV5(pose_emit);pose_handle=pose_module.install_pose_cache_runtime_adapter_v4(env.scene['robot'],receipt_callback=pose_events)
  robot=env.scene['robot'];guard=FreshDRNominalGuard(env,identity,torch_module=torch,tensor_converter=tensor)
  with guard.around_original_fullstate_restore():reset=env.reset()
  obs=reset[0]if isinstance(reset,tuple)else reset;guard.check_observations(obs);guard.assert_new_nominals_unchanged()
  recipe=env.recovery.recipe;assert torch.equal(recipe,13+torch.arange(80,device=env.device)%5)
  assert env.num_envs==80 and env.step_dt==.02 and env.physics_dt==.0025 and env.cfg.decimation==8
  assert env.cfg.terminations.closure.params['threshold']==.01 and env.cfg.terminations.mimic.params['threshold']==.01
  assert identity.usd_sha256==task['asset_SHA']and identity.contract_sha256==task['contract_SHA']
  def names(key):
   ids=robot.actuators[key].joint_indices
   if isinstance(ids,slice):ids=list(range(len(robot.joint_names)))[ids]
   elif hasattr(ids,'tolist'):ids=ids.tolist()
   return tuple(robot.joint_names[i]for i in ids)
  binding=RuntimeOrderBinding(tuple(robot.body_names),tuple(robot.joint_names),names('legs'),names('wheels'),names('gas_springs'),int(env._mild_dr.materials.shape[1]));getter=ActualDRMemoryGetter(env,binding);getter.capture_initial()
  def small(v):
   v=v.detach();return dict(shape=list(v.shape),dtype=str(v.dtype),finite=bool(torch.isfinite(v).all()),min=float(v.min()),max=float(v.max()),first8=v.reshape(-1)[:8].cpu().tolist())
  memory={k:small(v)for k,v in getter.cache.items()};audit=env._mild_dr.audit();assert audit['actual_parameters_pass']
  policy=cache.policy(env.device);policy.initialize(obs['policy']);pose_id=recipe-13;assert all(int((pose_id==p).sum())==16 for p in range(5))
  ready=dict(kind=KIND,resource_only_GPU_capacity=env._n80_allocation_only_capacity,source_cache=cache.receipt(),policy_receipt=policy.receipt(),D0_D7_fresh_audit=audit,actual_component_memory_not_independentbackend=memory,num_envs=80,observations={k:list(v.shape)for k,v in obs.items()},new_nominal_guard_passed=True,one_explicit_fresh_reset=True,scope=task['evaluation_scope'],controls=400,seed=task['seed'],interface=dict(raw_policy=35,fresh_noisy_history_frames=5,encoder_input=175,latent=3,actor_input=38,critic_observation_logged_only=38,actions=6),policy_interface=INTERFACE,physics_dt=.0025,policy_dt=.02,feedback_Hz=100,low80_request_denominator=80,normal_envs_excluded_from_low_denominator=0,new_lowrise_8second_task_enabled=True,original_74_score_recomputed=False,pose_counts=[16]*5,pose_cache_events=pose_receipt[0],constructor_seed=task['seed'],reference_native_cohort_executed=False)
  put(out/'FRESH80_FULLDR_BEFORE_CONTROL.json',ready)
  live=torch.ones(80,dtype=torch.bool,device=env.device);credit=torch.zeros_like(live);physical=torch.zeros_like(live);timeouts=torch.zeros_like(live);end_live=torch.zeros_like(live)
  first_credit_step=torch.full((80,),-1,dtype=torch.long,device=env.device);first_end_step=first_credit_step.clone();maximum_good=torch.zeros(80,dtype=torch.long,device=env.device)
  last_flags=torch.zeros((80,7),dtype=torch.bool,device=env.device);last_metrics=torch.zeros((80,8),dtype=torch.float32,device=env.device);end_flags=last_flags.clone();end_metrics=last_metrics.clone()
  reasons={k:0 for k in env.termination_manager.active_terms};term_events=0;closure_max=mimic_max=0.;oldterm=env.termination_manager.compute
  def terminal(*args,**kwargs):
   nonlocal term_events,closure_max,mimic_max
   value=oldterm(*args,**kwargs);tm=env.termination_manager;ter,tru=tm.terminated.clone(),tm.time_outs.clone();p=env.recovery;alive=live.clone();step=completed+1
   flags=p.low80_last_flags;metrics=p.low80_last_metrics;assert flags.shape==(80,7)and metrics.shape==(80,8)
   assert torch.equal(flags[:,6],p.stable>0)
   newly=p.credited&alive&~credit;first_credit_step[newly]=step;credit.logical_or_(p.credited&alive);maximum_good.copy_(torch.maximum(maximum_good,torch.where(alive,p.stable//2,0)))
   last_flags[alive]=flags[alive];last_metrics[alive]=metrics[alive]
   ending=(ter|tru)&alive;first_end_step[ending]=step;physical.logical_or_(ter&alive);timeouts.logical_or_(tru&alive)
   if step==400:end_live.copy_(alive&~ter);end_flags.copy_(flags);end_metrics.copy_(metrics)
   live.logical_and_(~(ter|tru));term_events+=int((ter|tru).sum())
   for name in reasons:reasons[name]+=int(tm.get_term(name).sum())
   closure,mimic=getattr(env,'_mod4_closure_now',None),getattr(env,'_mod4_mimic_now',None)
   if closure is not None:closure_max=max(closure_max,float(closure.max()))
   if mimic is not None:mimic_max=max(mimic_max,float(mimic.max()))
   return value
  env.termination_manager.compute=terminal;torch.cuda.empty_cache();wait_start(task,out,group,ready);tick=int(env._integrated_contact.tick);feedback_tick=int(env._feedback_100hz_tick);delay=dict(env._physics_action_delay.calls);eval_started=time.time()
  with torch.inference_mode():
   for _ in range(400):
    if time.time()>=task['absolute_worker_deadline_epoch']:raise TimeoutError('Original bounded worker deadline')
    if(group/'GROUP_ABORT.json').exists():raise RuntimeError('Own low80 group aborted')
    action=policy.act();assert action.shape==(80,6)and torch.isfinite(action).all();max_returned=max(max_returned,float(action.abs().max()));applied=action.clamp(-6.,6.);max_applied=max(max_applied,float(applied.abs().max()))
    obs,reward,ter,tru,extra=env.step(applied);completed+=1;assert obs['policy'].shape==(80,35)and obs['critic'].shape==(80,38)and all(bool(torch.isfinite(v).all())for v in(obs['policy'],obs['critic'],reward));policy.observe(obs['policy'],ter|tru)
  physics=int(env._integrated_contact.tick)-tick;feedback=int(env._feedback_100hz_tick)-feedback_tick;actual_delay={k:env._physics_action_delay.calls[k]-delay[k]for k in('legs','wheels')}
  assert completed==400 and physics==3200 and feedback==800 and actual_delay==dict(legs=3200,wheels=3200)
  cache.check_policy(policy);pr=policy.receipt();assert pr['actions_issued']==pr['returned_observations_accepted']==400 and not pr['awaiting_env_step_result'];guard.assert_new_nominals_unchanged();after=env._mild_dr.audit();assert after['actual_parameters_pass']
  stable_end=credit&end_live&end_flags[:,6];rows=[]
  for pid in range(5):
   mask=pose_id==pid;rows.append(dict(pose=pid,first_episode_denominator=int(mask.sum()),first_episode_stable_credits=int((mask&credit).sum()),credited_and_stable_at_end=int((mask&stable_end).sum()),first_episode_physical_terminated=int((mask&physical).sum()),first_episode_truncated=int((mask&timeouts).sum())))
  skill=dict(full_expert_graduated=False,independent_low80_scope=True,original_74_score_recomputed=False,low80_request_denominator=80,normal_envs_excluded=0,new_lowrise_8second_task_evaluated=True,no_reset_stitched_credit=True,pose_rows=rows,first_episode_stable_credits=int(credit.sum()),credited_and_stable_at_end=int(stable_end.sum()),first_episode_physical_terminated=int(physical.sum()),first_episode_truncated=int(timeouts.sum()),first_credit_control_per_env=first_credit_step.cpu().tolist(),first_end_control_per_env=first_end_step.cpu().tolist(),maximum_first_episode_good_controls=maximum_good.cpu().tolist(),first_episode_last_flags=last_flags.cpu().tolist(),first_episode_last_metrics=last_metrics.cpu().tolist(),control400_flags=end_flags.cpu().tolist(),control400_metrics=end_metrics.cpu().tolist(),control400_first_episode_physically_live=end_live.cpu().tolist(),flag_columns=['height_ok','upright_ok','speed_ok','angular_ok','wheels_ok','chassis_ok','joint_good'],metric_columns=['height_m','gravity_z','root_speed_m_s','angular_speed_rad_s','wheel0_force_N','wheel1_force_N','chassis_force_N','upright'],stable_policy_controls=25,stable_seconds=.5,request_policy_controls=400,source_training_credit_not_used=True,reference_native_cohort_executed=False,paired_native_difference=None)
  final=dict(kind=KIND,group_id=task['group_id'],role=role,expert_role='E3',GPU_UUID=task['GPU_UUID'],worker_pid=os.getpid(),parent_pid=os.getppid(),task_sha256=task['_task_sha256'],passed_execution=True,num_envs=80,controls=completed,seconds=8.,seed=task['seed'],physics_callbacks=physics,feedback_samples=feedback,delay_calls=actual_delay,source_cache=cache.receipt(),policy_receipt=pr,policy_interface=INTERFACE,actor_encoder_weights_before_after_exact=True,cached_full_checkpoint_before_after_exact=True,live_critic_optimizer_created=False,live_log_std_created=False,live_SequencePPO_created=False,optimizer_updates=0,policy_clip_actions=6.,original_control_clip_actions=6.,max_policy_return_action_abs=max_returned,max_applied_action_abs=max_applied,source_saved_training_DR_history_applied=False,source_N4096_DR_history_sliced=False,D0_D7_fresh_audit_before=audit,D0_D7_fresh_audit_after=after,termination_events_by_reason=reasons,episode_end_events=term_events,max_current_closure_m=closure_max,max_current_mimic_rad=mimic_max,skill=skill,first_eval_epoch=eval_started,last_eval_epoch=time.time(),wall_seconds=time.time()-started_wall,canonical_access=False,new_PPO_or_BPTT=False,asset_SHA=task['asset_SHA'],contract_SHA=task['contract_SHA'],parent_actual_wait_and_close_evidence_still_required=True,independent_31body_MuJoCo_acceptance_proven=False,pose_cache_events=pose_receipt[0])
  put(out/'FINAL.json',final);env.termination_manager.compute=oldterm
 except BaseException:
  execution_error=traceback.format_exc();put(out/'WORKER_ERROR.json',dict(role=role,epoch=time.time(),controls_completed=completed,error=execution_error,source_cache=cache.receipt()if cache is not None else None,no_retry_samepurpose=True));raise
 finally:
  if env is not None and oldterm is not None:env.termination_manager.compute=oldterm
  close_original_resources(task,out,env,namespace,cache,execution_error,controls_completed=completed)
if __name__=='__main__':main()
