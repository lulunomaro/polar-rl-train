"""E0/E2/E3/H1normal/W35 ownactualfactory N80freshDR, EMBEDDED ORIGINAL TEACHER MEAN, explicit E3/W35 reference barrier. No saved20k projection/no learning."""
from pathlib import Path
import os,sys,json,time,runpy,traceback,math,types
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from parallel_eval_safe import put
from frozen_embedded_teacher_native_runtime_v1 import wait_start
from frozen_embedded_teacher_native_runtime_v1 import task_args,A1CheckpointAdapter,install_paired_pose_before_original_reset,record_primary_error,close_original_eval_resources,INTEGRATION,paired_protocol_receipt,unresolved_evidence
from launch_storage_contract import parent_five_storage
from n80_gpu_capacity import capacity_ctor

def main():
 task,out,group=task_args();role=task['role'];assert role in('E0','E2','E3','W35');B=Path(task['runtime_root']);J=B/'job0'if role=='H1_normal'else B;mod=J/'runtime/isaac/mod4';ns=env=None;cache=None;actor=None;start_wall=time.time();completed=0;maxraw=0.;maxapplied=0.
 try:
  original=json.loads((J/'original_run_manifest.json').read_bytes())['env']
  for k in list(os.environ):
   if k.startswith('RM_')or k in('RANK','WORLD_SIZE','LOCAL_RANK','MASTER_ADDR','MASTER_PORT'):del os.environ[k]
  os.environ.update({k:str(v)for k,v in original.items()if k not in('RM_RESCUE_STOP_FILE','RM_RESCUE_DEADLINE','RM_SLOPE_INITIAL_ADMISSION')})
  os.environ.update(RM_MOD4_USD=str(B/'new_assets/robot.usd')if role=='H1_normal'else str(B/'runtime/assets/robot.usd'),RM_KEEP_STD='1',RM_PHYSICS_DT_S='0.0025',RM_SOLVER_POS='32',RM_SOLVER_VEL='4',MOD4_RESUME_QUEUE_CONTROL_US='20000')
  storage=parent_five_storage(B,out);storage.mkdir();(storage/'data').mkdir();(storage/'DerivedDataCache').mkdir();(storage/'data/user.config.json').write_text('{}');os.environ['WP_CACHE_DIR']=str(out/'warp_cache');os.environ['PYTHONDONTWRITEBYTECODE']='1'
  if role=='W35':
   os.environ.update(MOD4V1_ASSET_DIR=str(B/'runtime/assets'),MOD4_RM70_ORIGINAL_ASSET_ROOT=str(B/'original_field'),MOD4_RM70_ASSET_RECEIPT=str(B/'RM70_BINARY_INSTALL_ACTUAL.json'),MOD4_RM70_NEW_LAYOUT_ROOT=str(out/'new_CAD_layout'),MOD4_NEW208_JOB_ROOT=str(B),MOD4_W35_OWN_KIT_STORAGE_ROOT=str(storage));entry=mod/'train_mod4v1_w35.py';identity_name='MOD4V1_IDENTITY'
  elif role=='H1_normal':
   os.environ.update(MOD4_EXPERT213_KIT_STORAGE_ROOT=str(storage),RM_MOD4_TERRAIN='flat',RM_MOD4_MAP='',RM_JUMP_SCRIPT_PROB='0',OWN_E2_H1_KIND='H1_NORMAL_MOD4V1_N80_PARALLEL');entry=mod/'train_H1_ground_prelaunch_fullstate_v2.py';identity_name=None
  else:
   low=role.lower();os.environ.update({f'MOD4V1_{role}_ASSET_DIR':str(B/'runtime/assets'),f'MOD4V1_{role}_JOB_ROOT':str(B),f'MOD4V1_{role}_KIT_STORAGE_ROOT':str(storage)});entry=mod/f'train_mod4v1_{low}.py';identity_name=role+'_IDENTITY'
   if role in('E2','E3'):os.environ.update(OWN_E2_H1_KIND='E2_WORLD_MOVING_SIGNED4'if role=='E2'else'E3_PUBLIC_RECOVERY',RM_SPAWN_GRACE_STEPS='5',RM_JUMP_SCRIPT_PROB='0',RM_MOD4_MAP='',RM_MOD4_TERRAIN='flat')
  sys.path[:0]=[str(B/'lib'),str(mod),str(B/'runtime'),str(B),str(out)]
  from mod4v1_fresh_dr_guard import FreshDRNominalGuard
  if role=='H1_normal':
   from mod4v1_fresh_dr_guard import bind_before_task_import,verify_task_module,configure_new_task
   identity=bind_before_task_import(B/'new_assets')
  sys.argv=[str(entry),'--headless','--device','cuda:0','--num_envs','80','--seed','20260928','--dry_run',str(task['controls'])]
  import torch
  cache=A1CheckpointAdapter(torch,task)
  def no_other_checkpoint(*a,**kw):raise RuntimeError('N80freshpurposepermitsonlytheonealreadycachedselectedcheckpoint; no savedDRhelpers/otherPT')
  torch.load=no_other_checkpoint
  ns=runpy.run_path(str(entry),run_name='nine_n80_own_'+role+'_build_no_main')
  if role=='H1_normal':
   import mod4_task;verify_task_module(mod4_task,identity)
   import h1_scut_fudan_jump_reward_v1 as scut,h1_step270_sdk_runtime_candidate as terrain
   oldconfigure=scut.configure;scut.configure=lambda cfg:terrain.configure_rewards(cfg,oldconfigure);oldcfg=ns['Mod4EnvCfg'];factory=ns['build_env']
   def cfg():
    c=oldcfg();c.scene.num_envs=80;c.seed=20260928;c.sim.device='cuda:0';c.terminations.mimic.params={**c.terminations.mimic.params,'threshold':.01};configure_new_task(c,identity);return c
   factory.__globals__.update(Mod4Env=capacity_ctor(terrain.H1Step270Env),Mod4EnvCfg=cfg);env=factory()
  else:
   factory=ns['build_env'];factory.__globals__['Mod4Env']=capacity_ctor(factory.__globals__['Mod4Env']);env=factory();identity=ns[identity_name]
  from mild_dr import tensor
  from actual_DR_memory_getter272 import RuntimeOrderBinding,ActualDRMemoryGetter
  robot=env.scene['robot'];book=None;e2cycles=None
  if role=='W35':
   from rm70_intervals227 import RM70Intervals227
   book=RM70Intervals227(torch,80,env.device,out,task['source_SHA']);book.install(type(env.command_manager.get_term('twist')))
  install_paired_pose_before_original_reset(env);guard=FreshDRNominalGuard(env,identity,torch_module=torch,tensor_converter=tensor);guard.assert_new_nominals_unchanged();env.reset()
  if book is not None:book.arm(env,env.command_manager.get_term('twist'))
  if role=='E3':env.e3_reset_enabled=True;env.place_declared_fall(torch.arange(80,device=env.device));env.publish();assert set(env.recovery.recipe.tolist())==set(range(13))
  guard.assert_new_nominals_unchanged();audit=env._mild_dr.audit();assert audit['actual_parameters_pass'];assert env.num_envs==80 and env.step_dt==.02 and env.physics_dt==.0025 and env.cfg.decimation==8;assert env.cfg.terminations.closure.params['threshold']==.01 and env.cfg.terminations.mimic.params['threshold']==.01
  assert identity.usd_sha256==task['asset_SHA']and identity.contract_sha256==task['contract_SHA']
  def names(key):
   ids=robot.actuators[key].joint_indices
   if isinstance(ids,slice):ids=list(range(len(robot.joint_names)))[ids]
   elif hasattr(ids,'tolist'):ids=ids.tolist()
   return tuple(robot.joint_names[i]for i in ids)
  binding=RuntimeOrderBinding(tuple(robot.body_names),tuple(robot.joint_names),names('legs'),names('wheels'),names('gas_springs'),int(env._mild_dr.materials.shape[1]));getter=ActualDRMemoryGetter(env,binding);getter.capture_initial()
  def small(v):
   v=v.detach();return dict(shape=list(v.shape),dtype=str(v.dtype),finite=bool(torch.isfinite(v).all()),min=float(v.min()),max=float(v.max()),first8=v.reshape(-1)[:8].cpu().tolist())
  memory={k:small(v)for k,v in getter.cache.items()};obs=env.observation_manager.compute();guard.check_observations(obs);actor=cache.actor(env.device);from tensordict import TensorDict
  def actor_obs(o):return o if isinstance(o,TensorDict)else TensorDict(dict(o),batch_size=[80])
  ready=dict(policy_variant=task['policy_variant'],evaluation_purpose=task['batch_purpose'],resource_only_GPU_capacity=env._n80_allocation_only_capacity,source_cache=cache.receipt(),D0_D7_fresh_audit=audit,actual_component_memory_not_independentbackend=memory,num_envs=80,observations={k:list(v.shape)for k,v in obs.items()},new_nominal_guard_passed=True,one_explicit_fresh_reset=True,scope='FreshN80originalfactoryandrecipes;wholeOwnA1N1024CPUrootretained;noenvDRorhistoryrestoreorslice',controls=task['controls'],interface=[35,38,6],physics_dt=.0025,policy_dt=.02,feedback_Hz=100)
  put(out/'FRESH80_FULLDR_BEFORE_CONTROL.json',ready)
  reasons={k:0 for k in env.termination_manager.active_terms};terminated_env=torch.zeros(80,dtype=torch.bool,device=env.device);truncated_env=terminated_env.clone();first_episode_live=~terminated_env;episode_events=torch.zeros(80,dtype=torch.long,device=env.device);integrated_body_error=torch.zeros(80,3,device=env.device);root_initial=tensor(robot.data.root_pos_w).clone();root_last=root_initial.clone();reward_sum=torch.zeros(80,device=env.device);original_old_closure_boundary=terminated_env.clone();current_closure_max=0.;current_mimic_max=0.;command_before=None;first_recipe=None;first_credit=terminated_env.clone();first_term=terminated_env.clone();h1_flags={}
  if role=='E3':first_recipe=env.recovery.recipe.clone()
  if role=='E2':
   from minimal_e2_cycles_bridge import E2FreshCycleBridge
   e2cycles=E2FreshCycleBridge(env,torch,tensor,out)
  oldterm=env.termination_manager.compute
  def terminal(*aa,**kk):
   nonlocal root_last,current_closure_max,current_mimic_max
   value=oldterm(*aa,**kk);tm=env.termination_manager
   if book is not None:book.terminal(env._e1_pre_reset_frame,tm)
   if e2cycles is not None:e2cycles.terminal()
   ter=tm.terminated.clone();tru=tm.time_outs.clone();terminated_env.logical_or_(ter);truncated_env.logical_or_(tru);episode_events.add_((ter|tru).long());root_last=tensor(robot.data.root_pos_w).clone()
   for name in reasons:reasons[name]+=int(tm.get_term(name).sum())
   if command_before is not None:
    vb=tensor(robot.data.root_lin_vel_b);yaw=tensor(robot.data.root_ang_vel_b)[:,2];integrated_body_error.add_(torch.stack((vb[:,0]-command_before[:,0],vb[:,1]-command_before[:,1],yaw-command_before[:,2]),1).abs()*.02)
   clo=getattr(env,'_mod4_closure_now',None);mim=getattr(env,'_mod4_mimic_now',None)
   if clo is not None:current_closure_max=max(current_closure_max,float(clo.max()));original_old_closure_boundary.logical_or_(clo>.002)
   if mim is not None:current_mimic_max=max(current_mimic_max,float(mim.max()))
   if role=='E3':
    first_credit.logical_or_(env.recovery.credited&first_episode_live);first_term.logical_or_(ter&first_episode_live)
   if role=='H1_normal':
    phase=getattr(env,'h1_phase',None)
    for label,obj in [('phase',phase),('goal',getattr(phase,'goal',None)),('events',getattr(phase,'events',None))]:
     if obj is None:continue
     for key,v in vars(obj).items():
      if torch.is_tensor(v)and v.shape==(80,)and v.dtype==torch.bool:
       k=label+'.'+key
       if k not in h1_flags:h1_flags[k]=v.clone()
       else:h1_flags[k].logical_or_(v)
   first_episode_live.logical_and_(~(ter|tru));return value
  env.termination_manager.compute=terminal;ready['torch_reserved_bytes_before_empty_cache']=torch.cuda.memory_reserved();torch.cuda.empty_cache();ready['torch_reserved_bytes_after_empty_cache']=torch.cuda.memory_reserved();ready['allocation_only_empty_cache_no_live_tensor_or_RNG_change']=True;wait_start(task,out,group,ready);tick=int(env._integrated_contact.tick);fb=int(env._feedback_100hz_tick);delay=dict(env._physics_action_delay.calls);eval_started=time.time()
  with torch.inference_mode():
   for i in range(task['controls']):
    if time.time()>=task['absolute_worker_deadline_epoch']:raise TimeoutError('Ownninegroupboundedworkerdeadline')
    if(group/'GROUP_ABORT.json').exists():raise RuntimeError('Owngroupaborted')
    command_before=tensor(env.command_manager.get_term('twist').command).clone()
    if book is not None:book.begin(i,tensor(robot.data.root_pos_w)[:,:2].clone(),tensor(robot.data.heading_w).clone())
    if e2cycles is not None:e2cycles.begin(i)
    action=actor(actor_obs(obs),stochastic_output=False);assert action.shape==(80,6)and torch.isfinite(action).all();maxraw=max(maxraw,float(action.abs().max()));applied=action.clamp(-6.,6.);maxapplied=max(maxapplied,float(applied.abs().max()));obs,reward,ter,tru,extra=env.step(applied);actor.observe_transition(ter,tru);completed+=1;reward_sum.add_(reward)
    assert obs['policy'].shape==(80,35)and obs['critic'].shape==(80,38)and all(bool(torch.isfinite(x).all())for x in(obs['policy'],obs['critic'],reward))
  physics=int(env._integrated_contact.tick)-tick;feedback=int(env._feedback_100hz_tick)-fb;actual_delay={k:env._physics_action_delay.calls[k]-delay[k]for k in('legs','wheels')};assert physics==8*completed and feedback==2*completed and actual_delay=={'legs':8*completed,'wheels':8*completed};cache.check_actor(actor);guard.assert_new_nominals_unchanged();after=env._mild_dr.audit();assert after['actual_parameters_pass'];skill={'original_aggregate_graduation_rule':'NONE_IN_JOINED_SOURCE_NO_NEW_PASS_RATE','full_expert_graduated':False,'new_N80_fresh_cohort_not_original_N20k_cohort':True,'body_velocity_absolute_error_time_integral_per_env':integrated_body_error.cpu().tolist(),'root_before_and_last_terminal_world_xyz_per_env':{'before':root_initial.cpu().tolist(),'last':root_last.cpu().tolist()},'no_cross_reset_endpoint_displacement_success_claim':True}
  if role=='E3':
   rows=[]
   for recipe in range(13):
    m=first_recipe==recipe;rows.append({'recipe':recipe,'initial_envs':int(m.sum()),'original_request':recipe!=12,'first_episode_original_stable_credit':int((m&first_credit).sum()),'first_episode_physical_terminated':int((m&first_term).sum())})
   skill.update(original_recovery_recipe_rows=rows,stable50_public100Hz_age_equals_seconds=.5,stable50_equals_policy_controls=25,request300_age_seconds=3.,no_reset_stitched_credit=True)
  if role=='H1_normal':skill.update(original_phase_natural_boolean_event_counts={k:int(v.sum())for k,v in h1_flags.items()},horizon_scope='20secondsoriginalcfgdefaultnotprovedoriginalacceptedcohort',original_270mm_event_source='Owntrue270physicalcallbackstate; no generic18cmheightreplacement')
  if role=='E2':skill.update(domain='OwnE2_WORLD_MOVING_SIGNED4',cycle_rule='SameUIDepisode/direction/sign fullsigned2pi plus .5±.05/cross±.05/yaw±.2 andnonterminal/nontimeout',exact_cycle_observer_status='OriginalE2Cycles213sameUIDsigned2pi observerattachedtofreshN80; notoriginal20kcohort',original_E2_sameUID_cycle_facts=e2cycles.finish())
  if book is not None:skill['original_RM70_interval_route_facts']=book.finish();book.uninstall();book=None
  result=dict(policy_variant=task['policy_variant'],evaluation_purpose=task['batch_purpose'],actor_semantics='EMBEDDED_ORIGINAL_TEACHER_MEAN',kind=task['kind'],group_id=task['group_id'],role=role,GPU_UUID=task['GPU_UUID'],passed_execution=True,num_envs=80,controls=completed,seconds=.02*completed,physics_callbacks=physics,feedback_samples=feedback,delay_calls=actual_delay,source_cache=cache.receipt(),A1_entire_pi_weights_norms_before_after_frozen=True,cached_full_checkpoint_before_after_exact=True,live_critic_optimizer_created=False,optimizer_updates=0,original_RSL_clip_actions=6.,max_raw_action_abs=maxraw,max_applied_action_abs=maxapplied,source_saved20k_DR_history_applied=False,source20k_DR_sliced=False,D0_D7_fresh_audit_before=audit,D0_D7_fresh_audit_after=after,termination_events_by_reason=reasons,unique_envs_terminated=int(terminated_env.sum()),unique_envs_truncated=int(truncated_env.sum()),episode_end_events=int(episode_events.sum()),reward_sum_per_env=reward_sum.cpu().tolist(),max_current_closure_m=current_closure_max,max_current_mimic_rad=current_mimic_max,old002_closure_prefix_hit_envs=int(original_old_closure_boundary.sum()),skill=skill,first_eval_epoch=eval_started,last_eval_epoch=time.time(),wall_seconds=time.time()-start_wall,integration=INTEGRATION,paired_reset_protocol=paired_protocol_receipt(),unresolved_evidence=unresolved_evidence(),canonical_access=False,new_PPO_or_BPTT=False,asset_SHA=task['asset_SHA'],contract_SHA=task['contract_SHA']);put(out/'FINAL.json',result);env.termination_manager.compute=oldterm
 except BaseException:
  record_primary_error(out,role=role,phase='formal_worker',error=traceback.format_exc(),cache=cache);raise
 finally:
  close_original_eval_resources(env,None if ns is None else ns['app'],out,task)

if __name__=='__main__':main()
