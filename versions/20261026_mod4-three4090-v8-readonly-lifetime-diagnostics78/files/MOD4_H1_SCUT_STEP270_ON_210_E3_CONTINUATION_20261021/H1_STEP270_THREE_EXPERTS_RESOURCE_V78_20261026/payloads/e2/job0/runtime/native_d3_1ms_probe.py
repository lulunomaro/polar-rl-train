"""Frozen native MOD4 timestep/collection profile; never creates an optimizer update."""
from pathlib import Path
import argparse,json,os,time,hashlib
p=argparse.ArgumentParser();p.add_argument('--dt',type=float,required=True);p.add_argument('--checkpoint',required=True)
p.add_argument('--output',required=True);p.add_argument('--num_envs',type=int,default=20000)
p.add_argument('--warmup',type=int,default=24);p.add_argument('--steps',type=int,default=48);p.add_argument('--profile_steps',type=int,default=8)
D=Path(__file__).resolve().parent;CODE=D/'isaac/mod4'
for k,v in json.loads((CODE/'env.json').read_text()).items():os.environ[k]=str(v)
os.environ.update(ISAACSIM_ACCEPT_EULA='Y',OMNI_KIT_ACCEPT_EULA='YES')
from isaaclab.app import AppLauncher
AppLauncher.add_app_launcher_args(p);args=p.parse_args()
assert args.dt==.001 and os.environ["RM_SOLVER_POS"]=="16" and os.environ["RM_SOLVER_VEL"]=="4"
app=AppLauncher(args).app
import sys;sys.path.insert(0,str(CODE))
import torch
from feedback_delay_runtime import DelaySensorMod4Env as Mod4Env
import mod4_task as task
from nominal_parameter_audit import parameter_audit
from isaaclab_rl.rsl_rl import RslRlOnPolicyRunnerCfg,RslRlPpoActorCriticCfg,RslRlPpoAlgorithmCfg,RslRlVecEnvWrapper,handle_deprecated_rsl_rl_cfg
from rsl_rl.runners import OnPolicyRunner
from importlib import metadata
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

@torch.inference_mode()
def main():
 started=time.time();torch.manual_seed(20260928);cfg=task.Mod4EnvCfg();cfg.seed=20260928;cfg.scene.num_envs=args.num_envs
 cfg.sim.dt=args.dt;cfg.decimation=round(.01/args.dt);cfg.sim.render_interval=cfg.decimation
 from physics_clock import validate_clock
 assert validate_clock(args.dt)['decimation']==cfg.decimation
 # Geometry, material, drives and task are inherited without collider simplification.
 assert cfg.terminations.closure.func is task.closure_broken and cfg.terminations.closure.params['threshold']==.002
 env=Mod4Env(cfg=cfg)
 from clock_training_health import ClockTrainingHealth
 native_health=ClockTrainingHealth(env,Path(args.output).parent)
 vec=RslRlVecEnvWrapper(env,clip_actions=6.)
 from pxr import Usd,UsdPhysics,PhysxSchema
 solvers=[];loops=0
 for ei in range(env.num_envs):
  for prim in Usd.PrimRange(env.sim.stage.GetPrimAtPath('/World/envs/env_'+str(ei)+'/Robot')):
   if prim.HasAPI(PhysxSchema.PhysxArticulationAPI):
    api=PhysxSchema.PhysxArticulationAPI(prim);solvers.append((api.GetSolverPositionIterationCountAttr().Get(),api.GetSolverVelocityIterationCountAttr().Get()))
   if prim.IsA(UsdPhysics.Joint):
    joint=UsdPhysics.Joint(prim)
    if joint.GetExcludeFromArticulationAttr().Get() and joint.GetJointEnabledAttr().Get():loops+=1
 assert len(solvers)==env.num_envs and all(x==(16,4) for x in solvers) and loops==6*env.num_envs
 assert cfg.sim.physics.solver_type==1 and cfg.sim.physics.min_position_iteration_count<=16<=cfg.sim.physics.max_position_iteration_count
 actual_solver=dict(all_position16_velocity4=True,articulations=len(solvers),enabled_closed_loops=loops,solver_type=cfg.sim.physics.solver_type,position_min=cfg.sim.physics.min_position_iteration_count,position_max=cfg.sim.physics.max_position_iteration_count,closure_termination_enabled_threshold_m=.002,no_shadow=True)
 rc=RslRlOnPolicyRunnerCfg(seed=20260928,device=env.device,num_steps_per_env=24,max_iterations=1,save_interval=1,
  experiment_name='timestep_frozen',run_name='readback',clip_actions=6.,check_for_nan=True,obs_groups={'actor':['policy'],'critic':['critic']},
  policy=RslRlPpoActorCriticCfg(init_noise_std=.3,actor_hidden_dims=[256,128,64],critic_hidden_dims=[256,128,64],activation='elu'),
  algorithm=RslRlPpoAlgorithmCfg(value_loss_coef=2.,use_clipped_value_loss=True,clip_param=.2,entropy_coef=.005,num_learning_epochs=5,num_mini_batches=4,learning_rate=1e-4,schedule='adaptive',gamma=.99,lam=.95,desired_kl=.01,max_grad_norm=1.))
 rc=handle_deprecated_rsl_rl_cfg(rc,metadata.version('rsl-rl-lib'));runner=OnPolicyRunner(vec,rc.to_dict(),log_dir=None,device=env.device)
 runner.load(args.checkpoint);policy=runner.get_inference_policy(device=env.device)
 env.reset();obs=vec.get_observations();robot=env.scene['robot'];initial_params=parameter_audit(env);initial_q=robot.data.joint_pos.cpu().tolist();initial_root=robot.data.root_state_w.cpu().tolist()
 failed=torch.zeros(env.num_envs,dtype=torch.bool,device=env.device);nonfinite=torch.zeros((),dtype=torch.bool,device=env.device);task_events=0
 def one(obs):
  nonlocal task_events
  if os.environ.get("RM_SENSOR_FIXED_CLEAN")=="1":
   obs=obs.clone();obs["policy"]=env.clean_policy()
  action=policy(obs);obs,reward,done,extra=vec.step(action)
  # Timeouts are expected; only actual task resets accumulate in failed.
  bad=env.termination_manager.terminated
  failed.logical_or_(bad);nonfinite.logical_or_(~torch.isfinite(robot.data.root_state_w).all() | ~torch.isfinite(robot.data.joint_pos).all() | ~torch.isfinite(action).all() | ~torch.isfinite(reward).all())
  return obs
 for _ in range(args.warmup):obs=one(obs)
 torch.cuda.synchronize();t0=time.perf_counter();tick0=env._integrated_contact.tick
 sdk=[];selected_reset_audit=None
 for i in range(args.steps):
  if args.num_envs==10:
   sdk.append(env.sensor_sdk_audit())
   if i==100:
    ids=torch.tensor([1,4,7],device=env.device);others=torch.tensor([0,2,3,5,6,8,9],device=env.device);s=env._sensor_mild;bias=s.bias.clone();episodes=s.episode.clone();tick=env.common_step_counter
    env._reset_idx(ids);assert torch.equal(bias[others],s.bias[others]) and torch.equal(episodes[others],s.episode[others]) and bool((s.episode[ids]==episodes[ids]+1).all()) and env.common_step_counter==tick
    obs=vec.get_observations();selected_reset_audit=dict(selected_ids=ids.cpu().tolist(),other_bias_episode_exact=True,global_tick_unchanged=True)
  obs=one(obs)
 torch.cuda.synchronize();wall=time.perf_counter()-t0;tick1=env._integrated_contact.tick
 # CPU submission spans and asynchronous CUDA spans are diagnostics; throughput above is uninstrumented.
 spans={};events={};originals=[]
 def wrap(owner,name,label):
  old=getattr(owner,name);originals.append((owner,name,old));spans[label]=0.;events[label]=[]
  def measured(*a,**kw):
   s=torch.cuda.Event(enable_timing=True);e=torch.cuda.Event(enable_timing=True);s.record();t=time.perf_counter()
   try:return old(*a,**kw)
   finally:spans[label]+=time.perf_counter()-t;e.record();events[label].append((s,e))
  setattr(owner,name,measured)
 for owner,name,label in [(env.sim,'step','sim_step'),(env.scene,'update','scene_update'),(env.action_manager,'apply_action','apply_action'),
  (env._integrated_contact,'capture','integrated_contact'),(env.reward_manager,'compute','reward'),(env.termination_manager,'compute','termination'),(env.observation_manager,'compute','observation')]:wrap(owner,name,label)
 for _ in range(args.profile_steps):obs=one(obs)
 torch.cuda.synchronize();cuda={k:sum(s.elapsed_time(e) for s,e in v)/1000 for k,v in events.items()}
 for owner,name,old in originals:setattr(owner,name,old)
 report=dict(phase='complete',requested_physics_dt=args.dt,actual_physics_dt=float(env.physics_dt),actual_step_dt=float(env.step_dt),decimation=cfg.decimation,
  original_import_contract_physics_dt=task.CONTRACT['physics_dt_s'],contract_override_is_explicit_frozen_benchmark_only=True,solver16_training_test_physical_admission=True,
  warmup_control_steps=args.warmup,timed_control_steps=args.steps,num_envs=env.num_envs,steady_wall_seconds=wall,
  environment_policy_steps_per_second=env.num_envs*args.steps/wall,environment_physics_steps_per_second=env.num_envs*(tick1-tick0)/wall,
  physical_callback_count=tick1-tick0,expected_callback_count=args.steps*cfg.decimation,contact_bin_period_s=.005,
  contact_capture_metadata=env._contact_capture_metadata,actual_task_failed_environments=int(failed.sum()),nonfinite=bool(nonfinite),
  max_closure_error_m=float(getattr(env,'_mod4_max_closure',float('nan'))),max_mimic_error_rad=float(getattr(env,'_mod4_max_mimic',float('nan'))),
  initial_parameters=initial_params,final_parameters=parameter_audit(env),reset_root_before_physics=initial_root,reset_joint_pos_before_physics=initial_q,
  profiled_control_steps=args.profile_steps,host_submission_seconds=spans,cuda_event_seconds=cuda,profile_spans_are_nested_not_additive=True,
  checkpoint_path=args.checkpoint,checkpoint_sha256=sha(args.checkpoint),robot_usd_sha256=sha(task.USD_PATH),import_contract_sha256=sha(Path(task.USD_PATH).with_name('import_contract.json')),
  frozen_policy_only=True,PPO_update_count=0,load_and_probe_wall_seconds=time.time()-started,production_deployment=False)
 report['actual_solver_readback']=actual_solver;report['sensor_recipe']=env._sensor_mild.receipt();report['sensor_sdk_audit']=dict(rows=sdk,selected_reset=selected_reset_audit)
 report['health']=native_health.write()
 report['feedback_delay_recipe']=env.feedback_delay_recipe()
 report['actual_delay_manager_audit']=env.sensor_sdk_audit()
 report['scope']='Actual1ms D3 native physical/manager/callback check; source weights only, fresh physical/sensor/delay streams. Complete optimizer/RNG resume is separately required by full PPO startup.'
 report['final_root_state']=robot.data.root_state_w.cpu().tolist();report['final_joint_pos']=robot.data.joint_pos.cpu().tolist()
 assert report['physical_callback_count']==report['expected_callback_count']
 Path(args.output).write_text(json.dumps(report,indent=2));print('PHYSICS_SPEED_RESULT '+json.dumps({k:report[k] for k in ['actual_physics_dt','actual_step_dt','environment_policy_steps_per_second','actual_task_failed_environments','nonfinite','max_closure_error_m','max_mimic_error_rad','host_submission_seconds','cuda_event_seconds']}),flush=True)
 env.close()
if __name__=='__main__':
 try:main()
 except BaseException:
  import traceback;Path(args.output+'.error').write_text(traceback.format_exc());print(traceback.format_exc(),flush=True);raise
 finally:app.close()
