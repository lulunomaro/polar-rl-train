from pathlib import Path
import json,os,time,hashlib,copy,torch
from importlib import metadata
from local_state_projection import materialize,same,SOURCE,H

class SavedWindowComplete(Exception):pass

def restore_and_run(env,args,O,write):
 from isaaclab_rl.rsl_rl import RslRlOnPolicyRunnerCfg,RslRlPpoActorCriticCfg,RslRlPpoAlgorithmCfg,RslRlVecEnvWrapper,handle_deprecated_rsl_rl_cfg
 from rsl_rl.runners import OnPolicyRunner
 cfg=RslRlOnPolicyRunnerCfg(seed=20260928,device=args.device,num_steps_per_env=24,max_iterations=100000,obs_groups={'actor':['policy'],'critic':['critic']},save_interval=10,experiment_name='mod4_local_temp',run_name=O.parent.name,clip_actions=6.,check_for_nan=True,
  policy=RslRlPpoActorCriticCfg(init_noise_std=.3,actor_hidden_dims=[256,128,64],critic_hidden_dims=[256,128,64],activation='elu'),
  algorithm=RslRlPpoAlgorithmCfg(value_loss_coef=float(os.environ.get('RM_VALUE_LOSS_COEF','1.0')),use_clipped_value_loss=True,clip_param=.2,entropy_coef=float(os.environ.get('RM_ENTROPY_COEF','.005')),num_learning_epochs=5,num_mini_batches=4,learning_rate=1e-4,schedule=os.environ.get('RM_SCHEDULE','fixed'),gamma=.99,lam=.95,desired_kl=.01,max_grad_norm=1.))
 vec=RslRlVecEnvWrapper(env,clip_actions=6.);cfg=handle_deprecated_rsl_rl_cfg(cfg,metadata.version('rsl-rl-lib'));runner=OnPolicyRunner(vec,cfg.to_dict(),log_dir=str(O),device=cfg.device)
 path,projection=materialize(env,O);source=torch.load(path,map_location='cpu',weights_only=False)
 runner.load(str(path),strict=True,map_location=args.device)
 for key,model in [('actor_state_dict',runner.alg.actor),('critic_state_dict',runner.alg.critic)]:assert same(model.state_dict(),source[key]),key
 assert same(runner.alg.optimizer.state_dict(),source['optimizer_state_dict']) and runner.current_learning_iteration==source['iter']
 from wave50_lifetime_full_checkpoint import resume_e1_new_episode,install_e1_save_contract
 resume=resume_e1_new_episode(runner,env,str(path),str(O))
 markers=list(O.glob('*STARTUP_VERIFIED.json'))
 expected={'SENSOR_RESUME_STARTUP_VERIFIED.json','DELAY_RESUME_STARTUP_VERIFIED.json','ACTION_DELAY_RESUME_STARTUP_VERIFIED.json','SPRING_PRESSURE_RESUME_STARTUP_VERIFIED.json','GAS_DAMPING_RESUME_STARTUP_VERIFIED.json','CHASSIS_PD_RESUME_STARTUP_VERIFIED.json','E1_TERRAIN_RESUME_STARTUP_VERIFIED.json','E1_COMMAND_RETENTION_STARTUP_VERIFIED.json','E1_WAVE50_ENTRY_STARTUP_VERIFIED.json','E1_WAVE50_DIRECTION_RESUME_STARTUP_VERIFIED.json','E1_WAVE50_ROUTE_RESUME_STARTUP_VERIFIED.json','E1_WAVE50_LIFETIME_RESUME_STARTUP_VERIFIED.json'}
 assert {p.name for p in markers}==expected
 assert all(json.loads(p.read_bytes())['pid']==os.getpid() for p in markers)
 install_e1_save_contract(runner,env)
 originalsave=runner.save
 branch=copy.deepcopy(source['LOCAL_TEMPORARY_BRANCH']);started_iteration=int(source['iter']);updates=0;started=float(os.environ.get('MOD4_LOCAL_PARENT_START_EPOCH',time.time()));deadline=time.monotonic()+max(0.,args.train_seconds-(time.time()-started))
 runner.alg.learning_rate=runner.alg.optimizer.param_groups[0]['lr']
 def ownsave(path,*a,**k):
  temp=Path(path).with_name(Path(path).name+'.saving.pt');originalsave(str(temp),*a,**k)
  ck=torch.load(temp,map_location='cpu',weights_only=False);ck['LOCAL_TEMPORARY_BRANCH']=branch;ck['LOCAL_TEMPORARY_BRANCH']['own_actual_PPO_updates']=updates
  torch.save(ck,temp)
  with temp.open('rb') as f:os.fsync(f.fileno())
  os.replace(temp,path)
  count=0
  def finite(v):
   nonlocal count
   if isinstance(v,torch.Tensor) and (v.is_floating_point() or v.is_complex()):assert torch.isfinite(v).all();count+=1
   elif isinstance(v,dict):
    for x in v.values():finite(x)
   elif isinstance(v,(tuple,list)):
    for x in v:finite(x)
  finite(ck)
  assert count==107
  changed=sum(not torch.equal(v,source['actor_state_dict'][n]) for n,v in ck['actor_state_dict'].items())
  delta=[float(v['step'].item())-float(source['optimizer_state_dict']['state'][n]['step'].item()) for n,v in ck['optimizer_state_dict']['state'].items()]
  if updates:assert changed>0 and min(delta)>0
  write('LOCAL_LATEST_COMPLETE.json',dict(epoch=time.time(),pid=os.getpid(),path=str(Path(path).resolve()),sha256=H(path),bytes=Path(path).stat().st_size,source_SHA=SOURCE['sha256'],projected_source_SHA=projection['projection']['sha256'],finite_floating_tensors=count,actual_updates=updates,actual_controls=updates*24,actor_tensors_changed=changed,optimizer_step_delta_min=min(delta),complete_DR_and_private_state_saved=True,temporary_backend_and_environment_projection_disclosed=True))
 runner.save=ownsave
 write('LOCAL_FULLSTATE_STARTUP_VERIFIED.json',dict(epoch=time.time(),passed=True,pid=os.getpid(),original_source_SHA=SOURCE['sha256'],projected_source_SHA=projection['projection']['sha256'],source_original_envs=20000,local_num_envs=env.num_envs,all_actor_critic_std_optimizer_exact_before_learning=True,all_source_global_named_private_CPUCUDA_RNG_exact_before_new_episode=True,actual_disk_roundtrip_startup_markers=[p.name for p in markers],selected_source_episode_plus_one=True,new_PhysX_episode=True,PhysX_exact_resume=False,backend_equivalence_not_claimed=True,projection_ref=str(O/'LOCAL_PROJECTED_STATE_CPU_ADMISSION.json'),resume=resume))
 from e1_terrain_training_health import E1TerrainTrainingHealth,learning_health_pass
 health=E1TerrainTrainingHealth(env,O)
 if args.mode=='fullrestore':
  policy=runner.get_inference_policy(device=env.device)
  for _ in range(args.probe_controls):
   obs=vec.get_observations()
   with torch.inference_mode():vec.step(policy(obs))
  report=health.write();assert learning_health_pass(report)
  write('FULLRESTORE_PHYSICAL_PROBE_PASSED.json',dict(epoch=time.time(),passed=True,actual_controls=args.probe_controls,callbacks=report['actual_physics_callbacks'],health=report,source_projection_and_fullCPUCUDA_restore_passed=True,no_PPO=True))
  return
 runner.logger.init_logging_writer()
 # One local cost record, never a secondcanonicalbudget. Actual charges are retained
 # for reconciliation with the original ledger after the remote mainplan is resumed.
 write('LOCAL_PPO_UNIQUE_COST_STARTED.json',dict(epoch=started,pid=os.getpid(),original_source_SHA=SOURCE['sha256'],mode='temporary_local_learning',target_seconds=args.train_seconds,canonical_authority_path='/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json',local_cost_is_not_new_budget_authority=True,canonical_reconciliation_pending=True,no_budget_extension_or_ledger_copy=True))
 original_update=runner.alg.update
 def update():
  nonlocal updates
  out=original_update();updates+=1;runner.current_learning_iteration=started_iteration+updates-1
  if updates%2==0:runner.save(str(O/('model_'+str(runner.current_learning_iteration)+'.pt')))
  report=health.write()
  write('LOCAL_PPO_PROGRESS.json',dict(epoch=time.time(),pid=os.getpid(),actual_updates=updates,actual_controls=updates*24,physical_seconds_per_environment=updates*.24,health=report,formal_final=False))
  stop=time.monotonic()>=deadline or (O.parents[2]/'STOP_AFTER_SAVE').exists() or health.reason is not None
  if stop:
   runner.save(str(O/('model_'+str(runner.current_learning_iteration)+'.pt')))
   write('LOCAL_PPO_FORMAL_FINAL_ACTUAL.json',dict(epoch=time.time(),passed=learning_health_pass(report),pid=os.getpid(),actual_updates=updates,actual_controls=updates*24,health=report,stop_reason=health.reason or 'bounded_window_or_human_save_stop',latest=json.loads((O/'LOCAL_LATEST_COMPLETE.json').read_bytes()),cost_seconds=time.time()-started,canonical_reconciliation_pending=True))
   raise SavedWindowComplete()
  return out
 runner.alg.update=update
 try:runner.learn(num_learning_iterations=100000,init_at_random_ep_len=True)
 except SavedWindowComplete:pass
 finally:
  write('LOCAL_PPO_UNIQUE_COST_ENDED.json',dict(epoch=time.time(),pid=os.getpid(),started_epoch=started,actual_seconds=time.time()-started,actual_updates=updates,all_failures_and_cost_retained=True,canonical_reconciliation_pending=True,no_original_budget_write_or_recharge=True))
  runner.logger.stop_logging_writer()
