"""Strict full20k restoration, one explicit left initializer, bounded PPO/save.

This is a new process scope. It never writes the original Linux canonical ledger.
"""
from pathlib import Path
import copy,json,os,time
from importlib import metadata
import torch
from windows20k_fullstate_binding import materialize,same,H,validate,floating_count,DONOR_SHA
import left_head_offset_aware_migration_v3 as repair
MARKERS={'SENSOR_RESUME_STARTUP_VERIFIED.json','DELAY_RESUME_STARTUP_VERIFIED.json','ACTION_DELAY_RESUME_STARTUP_VERIFIED.json','SPRING_PRESSURE_RESUME_STARTUP_VERIFIED.json','GAS_DAMPING_RESUME_STARTUP_VERIFIED.json','CHASSIS_PD_RESUME_STARTUP_VERIFIED.json','E1_TERRAIN_RESUME_STARTUP_VERIFIED.json','E1_COMMAND_RETENTION_STARTUP_VERIFIED.json','E1_WAVE50_ENTRY_STARTUP_VERIFIED.json','E1_WAVE50_DIRECTION_RESUME_STARTUP_VERIFIED.json','E1_WAVE50_ROUTE_RESUME_STARTUP_VERIFIED.json','E1_WAVE50_LIFETIME_RESUME_STARTUP_VERIFIED.json'}
class SavedWindowComplete(Exception):pass
def CPU(v):
 if torch.is_tensor(v):return v.detach().cpu().clone()
 if isinstance(v,dict):return {k:CPU(x) for k,x in v.items()}
 if isinstance(v,list):return [CPU(x) for x in v]
 if isinstance(v,tuple):return tuple(CPU(x) for x in v)
 return copy.deepcopy(v)
def make_runner(env,args,O):
 from isaaclab_rl.rsl_rl import RslRlOnPolicyRunnerCfg,RslRlPpoActorCriticCfg,RslRlPpoAlgorithmCfg,RslRlVecEnvWrapper,handle_deprecated_rsl_rl_cfg
 from rsl_rl.runners import OnPolicyRunner
 assert env.num_envs in (10,20000) and 0<args.train_seconds<=7200
 cfg=RslRlOnPolicyRunnerCfg(seed=20260928,device=args.device,num_steps_per_env=24,max_iterations=100000,obs_groups={'actor':['policy'],'critic':['critic']},save_interval=10,experiment_name='mod4_windows4090_full20k_repair',run_name=O.parent.name,clip_actions=6.,check_for_nan=True,
  policy=RslRlPpoActorCriticCfg(init_noise_std=.3,actor_hidden_dims=[256,128,64],critic_hidden_dims=[256,128,64],activation='elu'),
  algorithm=RslRlPpoAlgorithmCfg(value_loss_coef=float(os.environ.get('RM_VALUE_LOSS_COEF','1.0')),use_clipped_value_loss=True,clip_param=.2,entropy_coef=float(os.environ.get('RM_ENTROPY_COEF','.005')),num_learning_epochs=5,num_mini_batches=4,learning_rate=1e-4,schedule=os.environ.get('RM_SCHEDULE','adaptive'),gamma=.99,lam=.95,desired_kl=.01,max_grad_norm=1.))
 vec=RslRlVecEnvWrapper(env,clip_actions=6.);cfg=handle_deprecated_rsl_rl_cfg(cfg,metadata.version('rsl-rl-lib'));runner=OnPolicyRunner(vec,cfg.to_dict(),log_dir=str(O),device=cfg.device)
 return vec,runner
def restore_and_run(env,args,O,write):
 assert env.num_envs==20000
 vec,runner=make_runner(env,args,O)
 path,binding=materialize(env,O,args,write);source=torch.load(path,map_location='cpu',weights_only=False)
 runner.load(str(path),strict=True,map_location=args.device)
 for key,model in [('actor_state_dict',runner.alg.actor),('critic_state_dict',runner.alg.critic)]:assert same(model.state_dict(),source[key]),key
 assert same(runner.alg.optimizer.state_dict(),source['optimizer_state_dict']) and runner.current_learning_iteration==source['iter']
 from wave50_lifetime_full_checkpoint import resume_e1_new_episode,install_e1_save_contract
 resume=resume_e1_new_episode(runner,env,str(path),str(O))
 files={p.name:p for p in O.glob('*STARTUP_VERIFIED.json')};assert set(files)==MARKERS
 marker_rows={k:json.loads(p.read_bytes()) for k,p in files.items()}
 for name,row in marker_rows.items():
  assert row['pid']==os.getpid(),name
  if 'passed' in row:assert row['passed'],name
 assert same(runner.alg.actor.state_dict(),source['actor_state_dict']) and same(runner.alg.critic.state_dict(),source['critic_state_dict']) and same(runner.alg.optimizer.state_dict(),source['optimizer_state_dict'])
 assert torch.equal(env._e1_episode.cpu(),source['E1_terrain_state']['episode']+1)
 install_e1_save_contract(runner,env)
 legs=env.action_manager.get_term('legs');off=legs._offset.detach().clone();default=env.scene['robot'].data.default_joint_pos
 default=default.torch if hasattr(default,'torch') else default
 assert off.shape==(20000,4) and torch.equal(off,default[:,legs._joint_ids])
 admitted=json.loads(Path(args.manifest).read_bytes())['admitted_leg_offsets']
 expected=torch.tensor(admitted,device=env.device,dtype=off.dtype).expand(20000,4)
 assert torch.equal(off,expected),'actual API offset differs from reviewed fixture'
 repair.offsets_validate(off.cpu(),20000)
 import mod4_task as task
 assert task.LEG_ORDER==['left_crank','left_hip','right_crank','right_hip'] and task.LEG_ACTION_SCALE==repair.SCALE and legs.diff_min==repair.LOWER and legs.diff_max==repair.UPPER
 # This is the normal first policy observation, captured once before the no-RNG
 # initializer boundary. Runner.learn/probe consumes this exact sample once;
 # the initialization proof does not create an extra observation/noise draw.
 initial_obs=vec.get_observations()
 cpu_rng=torch.get_rng_state().clone();cuda_rng=torch.cuda.get_rng_state(env.device).clone()
 if args.source_sha==DONOR_SHA:
  obs=initial_obs
  with torch.inference_mode():old_mean=runner.alg.actor(obs).clone()
  candidate=repair.migrate_tree(source,source_sha=DONOR_SHA,actual_offsets=off.cpu())
  runner.alg.actor.load_state_dict(candidate['actor_state_dict'],strict=True);runner.alg.optimizer.load_state_dict(candidate['optimizer_state_dict'])
  with torch.inference_mode():new_mean=runner.alg.actor(obs).clone()
  assert torch.equal(old_mean[:,1:],new_mean[:,1:]) and same(runner.alg.critic.state_dict(),source['critic_state_dict'])
  oldtargets=repair.guarded_targets(old_mean,off);newtargets=repair.guarded_targets(new_mean,off)
  target_delta=float((oldtargets-newtargets).abs().max());assert target_delta<=1e-6,'unadmitted initial deterministic mechanical target change'
  actor_cpu=CPU(runner.alg.actor.state_dict());optimizer_cpu=CPU(runner.alg.optimizer.state_dict())
  assert same(actor_cpu,candidate['actor_state_dict']) and same(optimizer_cpu,candidate['optimizer_state_dict'])
  metadata_actual=dict(profile=repair.PROFILE,original_complete20k_donor_SHA=DONOR_SHA,initial_source_SHA=args.source_sha,num_envs=20000,applied_once_after_complete_source_restore=True,CPU_prepared_only=False,actual_GPU_API_offset_and_default_q_leg_order=off[0].cpu().tolist(),actual_API_offset_all20000_exact=True,actual_initial_guarded_target_max_error_rad=target_delta,other5_means_std_and_hidden_critic_initially_exact=True,last_action_feedback_may_change_future_other5_outputs_without_weight_change=True,full_rollout_behavior_equivalence_not_claimed=True,initial_Adam_moment_row0_only_cleared_parameter_ids=[0,7,8],original_Adam_step_scalars_retained=True,same_repaired_resume_must_not_repeat_initializer=True,not_live_action_coupling_teacher_or_PhysX_exact_resume=True,qualification_claimed=False)
 else:
  metadata_actual=copy.deepcopy(source['WINDOWS4090_LEFT_HEAD_REPAIR_ACTUAL']);assert metadata_actual['profile']==repair.PROFILE
  assert metadata_actual['actual_GPU_API_offset_and_default_q_leg_order']==off[0].cpu().tolist()
  metadata_actual['same_repaired_resume_source_SHA']=args.source_sha
  metadata_actual['initializer_repeated_on_this_resume']=False
 assert torch.equal(cpu_rng,torch.get_rng_state()) and torch.equal(cuda_rng,torch.cuda.get_rng_state(env.device)),'initializer drew RNG'
 # Independent actual CUDA -> CPU disk -> CUDA actor/Adam roundtrip; no second
 # physical reset is performed. Full DR/RNG disk roundtrips are the12 above.
 initial_actor=CPU(runner.alg.actor.state_dict());initial_critic=CPU(runner.alg.critic.state_dict());initial_opt=CPU(runner.alg.optimizer.state_dict())
 roundtrip=O/'LEFT_HEAD_ACTUAL_CUDA_ACTOR_ADAM_ROUNDTRIP.pt';assert not roundtrip.exists();torch.save(dict(actor=initial_actor,critic=initial_critic,optimizer=initial_opt,metadata=metadata_actual),roundtrip)
 ck=torch.load(roundtrip,map_location='cpu',weights_only=False)
 runner.alg.actor.load_state_dict(ck['actor'],strict=True);runner.alg.critic.load_state_dict(ck['critic'],strict=True);runner.alg.optimizer.load_state_dict(ck['optimizer'])
 assert same(initial_actor,runner.alg.actor.state_dict()) and same(initial_critic,runner.alg.critic.state_dict()) and same(initial_opt,runner.alg.optimizer.state_dict())
 assert torch.equal(cpu_rng,torch.get_rng_state()) and torch.equal(cuda_rng,torch.cuda.get_rng_state(env.device))
 original_get_obs=vec.get_observations;first_obs_pending=True
 def first_observation_once():
  nonlocal first_obs_pending
  if first_obs_pending:first_obs_pending=False;return initial_obs
  return original_get_obs()
 vec.get_observations=first_observation_once
 write('LEFT_HEAD_ACTUAL_INIT_VERIFIED.json',dict(epoch=time.time(),pid=os.getpid(),passed=True,metadata=metadata_actual,roundtrip_SHA=H(roundtrip),no_RNG_draw_inside_initializer=True,normal_first_observation_captured_once_then_consumed_once=True,no_extra_observation_for_proof=True,no_second_physical_reset=True,initialization_on_this_attempt=args.source_sha==DONOR_SHA))
 originalsave=runner.save;updates=0;started_iteration=int(source['iter']);started=float(os.environ['MOD4_WINDOWS_PARENT_START_EPOCH']);deadline=time.monotonic()+max(0.,args.train_seconds-(time.time()-started))
 backend_binding=copy.deepcopy(source['WINDOWS4090_FULL20K_BACKEND_BINDING'])
 def ownsave(path,*a,**k):
  path=Path(path);temp=path.with_name(path.name+'.saving.pt');originalsave(str(temp),*a,**k)
  saved=torch.load(temp,map_location='cpu',weights_only=False);saved['WINDOWS4090_FULL20K_BACKEND_BINDING']=backend_binding;saved['WINDOWS4090_LEFT_HEAD_REPAIR_ACTUAL']=metadata_actual
  torch.save(saved,temp)
  with temp.open('r+b') as f:f.flush();os.fsync(f.fileno())
  os.replace(temp,path);validate(saved,H(path));assert floating_count(saved)==107
  changed=sum(not same(v,initial_actor[n]) for n,v in saved['actor_state_dict'].items());deltas=[float(v['step'].item())-float(initial_opt['state'][n]['step'].item()) for n,v in saved['optimizer_state_dict']['state'].items()]
  if updates:assert changed>0 and min(deltas)>0
  write('WINDOWS4090_LATEST_COMPLETE.json',dict(epoch=time.time(),pid=os.getpid(),path=str(path.resolve()),sha256=H(path),bytes=path.stat().st_size,source_SHA=args.source_sha,original_complete20k_donor_SHA=DONOR_SHA,finite_floating_tensors=107,perenv_tensor_fields=99,actual_updates=updates,actual_controls=updates*24,actual_envsteps=updates*24*20000,callbacks=updates*24*4,actor_tensors_changed_since_postinit=len([n for n in saved['actor_state_dict'] if not same(saved['actor_state_dict'][n],initial_actor[n])]),optimizer_step_delta_min=min(deltas),complete_DR_globalnamed_dictprivate_CPUCUDA_state_saved=True,initialization_not_miscounted_as_PPO=True,formal_final=False))
 runner.save=ownsave;runner.alg.learning_rate=runner.alg.optimizer.param_groups[0]['lr']
 write('WINDOWS4090_FULLSTATE_STARTUP_VERIFIED.json',dict(epoch=time.time(),pid=os.getpid(),passed=True,source_SHA=args.source_sha,num_envs=20000,all12_original_CPUCUDA_restore_markers=marker_rows,source_episode_plus_one=True,complete_original_donor_restored_before_explicit_initializer=True,source_binding=binding,backend_equivalence_not_claimed=True,PhysX_exact_resume=False))
 from e1_terrain_training_health import E1TerrainTrainingHealth,learning_health_pass
 health=E1TerrainTrainingHealth(env,O)
 if args.mode=='fullrestore':
  from windows4090_probe_contract import birth_inputs,end_contract
  birth=birth_inputs(env,O,write,source,None);ground_error=0.;height_error=0.
  policy=runner.get_inference_policy(device=env.device)
  obs=vec.get_observations()
  for _ in range(args.probe_controls):
   with torch.inference_mode():obs,_,_,_=vec.step(policy(obs))
   ground_error=max(ground_error,env._e1_pre_reset_frame['independent_ground_error']);height_error=max(height_error,env._e1_height_formula_error)
   assert env._rough_termination_query_tick==env._rough_reward_query_tick==int(env._sim_step_counter)
  report=health.write();assert learning_health_pass(report)
  contract=end_contract(env,O,write,source,args.probe_controls,ground_error,height_error,birth)
  runner.save(str(O/'WINDOWS4090_REPAIRED_FULLRESTORE_COMPLETE.pt'))
  write('FULLRESTORE_PHYSICAL_PROBE_PASSED.json',dict(epoch=time.time(),pid=os.getpid(),passed=True,actual_controls=args.probe_controls,actual_callbacks=report['actual_physics_callbacks'],health=report,complete_physical_command_DR_contract=contract,no_PPO=True,latest=json.loads((O/'WINDOWS4090_LATEST_COMPLETE.json').read_bytes()),initial_head_repair_not_learning_or_fullroute_certificate=True))
  return
 assert args.mode=='train';runner.logger.init_logging_writer()
 write('WINDOWS4090_PPO_UNIQUE_COST_STARTED.json',dict(epoch=started,pid=os.getpid(),target_seconds=args.train_seconds,source_SHA=args.source_sha,canonical_authority_path='/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json',canonical_reconciliation_pending=True,local_cost_evidence_not_second_budget=True))
 oldupdate=runner.alg.update
 def update():
  nonlocal updates
  value=oldupdate();updates+=1;runner.current_learning_iteration=started_iteration+updates-1
  if updates%2==0:runner.save(str(O/('model_'+str(runner.current_learning_iteration)+'.pt')))
  report=health.write();write('WINDOWS4090_PPO_PROGRESS.json',dict(epoch=time.time(),pid=os.getpid(),actual_updates=updates,actual_controls=updates*24,actual_envsteps=updates*24*20000,physical_seconds_per_environment=updates*.24,health=report,formal_final=False))
  if time.monotonic()>=deadline or Path(args.stop_after_save).exists() or health.reason is not None:
   runner.save(str(O/('model_'+str(runner.current_learning_iteration)+'.pt')))
   write('WINDOWS4090_PPO_FORMAL_FINAL_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),passed=learning_health_pass(report),actual_updates=updates,actual_controls=updates*24,health=report,stop_reason=health.reason or 'bounded_window_or_human_save_stop',latest=json.loads((O/'WINDOWS4090_LATEST_COMPLETE.json').read_bytes()),worker_cost_before_Kit_exit_seconds=time.time()-started,canonical_reconciliation_pending=True))
   raise SavedWindowComplete()
  return value
 runner.alg.update=update
 try:runner.learn(num_learning_iterations=100000,init_at_random_ep_len=True)
 except SavedWindowComplete:pass
 finally:
  write('WINDOWS4090_PPO_UNIQUE_COST_ENDED.json',dict(epoch=time.time(),pid=os.getpid(),started_epoch=started,worker_before_Kit_exit_seconds=time.time()-started,actual_updates=updates,canonical_reconciliation_pending=True,parent_EXIT_full_load_learn_save_exit_is_accounting_basis=True,no_budget_write_extension_refund_or_duplicate_charge=True));runner.logger.stop_logging_writer()
