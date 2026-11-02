"""NEW original normal-H1 true270 fresh80, no model and no trainer.main.
Same actual453 factory/phase/clock, new2c/bae. No PT/actor/optimizer admitted.
"""
from pathlib import Path
import argparse,json,os,runpy,sys,time,traceback

def main():
 p=argparse.ArgumentParser();p.add_argument('--task',type=Path,required=True);a=p.parse_args();task=json.loads(a.task.read_bytes());out=a.task.parent;B=Path(task['runtime_job']);J=B/'job0'
 def put(n,v):
  with (out/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
 assert task['kind']=='MOD4V1_H1_NORMAL_FRESH80_NO_PT_V1' and task['num_envs']==80 and task['controls']==24
 assert os.environ['CUDA_VISIBLE_DEVICES']==task['GPU_UUID']
 original=json.loads((J/'original_run_manifest.json').read_bytes())['env']
 for k in list(os.environ):
  if k.startswith('RM_') or k in ('RANK','WORLD_SIZE','LOCAL_RANK','MASTER_ADDR','MASTER_PORT'):del os.environ[k]
 os.environ.update({k:str(v) for k,v in original.items() if k not in ('RM_RESCUE_DEADLINE','RM_RESCUE_STOP_FILE','RM_SLOPE_INITIAL_ADMISSION')})
 os.environ.update(RM_MOD4_USD=str(B/'new_assets/robot.usd'),RM_MOD4_TERRAIN='flat',RM_MOD4_MAP='',RM_JUMP_SCRIPT_PROB='0',RM_KEEP_STD='1',RM_PHYSICS_DT_S='0.0025',RM_SOLVER_POS='32',RM_SOLVER_VEL='4',OWN_E2_H1_KIND='H1_NORMAL_MOD4V1_FRESH80_NO_PT')
 sys.path[:0]=[str(B/'lib'),str(J/'runtime/isaac/mod4'),str(B)]
 from mod4v1_fresh_dr_guard import bind_before_task_import,verify_task_module,configure_new_task,FreshDRNominalGuard
 identity=bind_before_task_import(B/'new_assets');entry=J/'runtime/isaac/mod4/train_H1_ground_prelaunch_fullstate_v2.py'
 sys.argv=[str(entry),'--headless','--device','cuda:0','--num_envs','80','--seed','20260928','--dry_run','24']
 ns=env=None;sentinels=dict(torch_load=0,runner_construct=0,actor_calls=0,optimizer_step=0)
 try:
  import torch
  def no_load(*args,**kw):sentinels['torch_load']+=1;raise RuntimeError('H1 fresh80 forbids torch.load')
  torch.load=no_load
  def no_optimizer(*args,**kw):sentinels['optimizer_step']+=1;raise RuntimeError('H1 fresh80 forbids optimizer.step')
  torch.optim.Optimizer.step=no_optimizer;torch.optim.Adam.step=no_optimizer
  ns=runpy.run_path(str(entry),run_name='H1_normal_original453_fresh80_ownfactory_no_main')
  import mod4_task;verify_task_module(mod4_task,identity)
  import h1_scut_fudan_jump_reward_v1 as scut
  import h1_step270_sdk_runtime_candidate as terrain
  oldconfigure=scut.configure;scut.configure=lambda cfg:terrain.configure_rewards(cfg,oldconfigure)
  oldcfg=ns['Mod4EnvCfg'];factory=ns['build_env']
  def cfg():
   c=oldcfg();c.scene.num_envs=80;c.seed=20260928;c.sim.device='cuda:0';c.terminations.mimic.params={**c.terminations.mimic.params,'threshold':.01};configure_new_task(c,identity)
   assert c.sim.dt==.0025 and c.decimation==8 and c.sim.physics.solver_type==1
   assert c.scene.robot.spawn.articulation_props.solver_position_iteration_count==32 and c.scene.robot.spawn.articulation_props.solver_velocity_iteration_count==4
   return c
  factory.__globals__.update(Mod4Env=terrain.H1Step270Env,Mod4EnvCfg=cfg)
  def no_runner(*args,**kw):sentinels['runner_construct']+=1;raise RuntimeError('Fresh80 forbids runner/actor creation')
  ns['OnPolicyRunner'].__init__=no_runner
  env=factory();assert type(env).__module__=='h1_step270_sdk_runtime_candidate' and type(env).__name__=='H1Step270Env'
  from mild_dr import tensor
  from actual_DR_memory_getter272 import RuntimeOrderBinding,ActualDRMemoryGetter
  robot=env.scene['robot'];guard=FreshDRNominalGuard(env,identity,torch_module=torch,tensor_converter=tensor)
  guard.assert_new_nominals_unchanged();env.reset();guard.assert_new_nominals_unchanged();audit=guard.verify_live_parameters();assert audit['actual_parameters_pass']
  assert not env.h1_phase.age_control.any() and not env.h1_phase.public_request().any()
  def names(key):
   ids=robot.actuators[key].joint_indices
   if isinstance(ids,slice):ids=list(range(len(robot.joint_names)))[ids]
   elif hasattr(ids,'tolist'):ids=ids.tolist()
   return tuple(robot.joint_names[i] for i in ids)
  binding=RuntimeOrderBinding(tuple(robot.body_names),tuple(robot.joint_names),names('legs'),names('wheels'),names('gas_springs'),int(env._mild_dr.materials.shape[1]));getter=ActualDRMemoryGetter(env,binding);getter.capture_initial()
  def small(v):
   v=v.detach();return dict(shape=list(v.shape),dtype=str(v.dtype),finite=bool(torch.isfinite(v).all()),min=float(v.min()),max=float(v.max()),first8=v.reshape(-1)[:8].cpu().tolist())
  obs=env.observation_manager.compute();guard.check_observations(obs)
  assert env.num_envs==80 and env.physics_dt==.0025 and env.step_dt==.02 and env.cfg.decimation==8
  assert env.cfg.terminations.closure.params['threshold']==.01 and env.cfg.terminations.mimic.params['threshold']==.01
  assert env.spring_pressure_recipe()['nominal_stiffness_N_m']==2000 and env._physics_action_delay.queue.control_us==20000
  tick=int(env._integrated_contact.tick);fb=int(env._feedback_100hz_tick);cb=int(env.h1_callback_count);calls=dict(env._physics_action_delay.calls)
  put('H1_FRESH80_BEFORE_CONTROL.json',dict(scope='actual H1Step270 fresh80 noPT, not20krestore orskill',asset_SHA=identity.usd_sha256,contract_SHA=identity.contract_sha256,actual_mild_DR_audit=audit,exact_H1_bank_compatibility=env._mod4v1_h1_bank_compatibility,component_memory_NOT_independent_PhysX={k:small(v) for k,v in getter.cache.items()},episode_counts={k:small(v) for k,v in getter.counts.items()},phase=env.h1_phase.state_dict()['geometry'],interface=[35,38,6],policy_hz=50,feedback_hz=100,closure_m=.01,mimic_rad=.01,one_explicit_fresh_reset=1,sentinels=sentinels,model_opens=0))
  zeros=torch.zeros((80,6),device=env.device);finite=True;resets={n:0 for n in env.termination_manager.active_terms}
  for i in range(24):
   age=env.h1_phase.age_control.clone();obs,reward,terminated,truncated,extras=env.step(zeros);done=terminated|truncated
   assert torch.equal(env.h1_phase.age_control,torch.where(done,torch.zeros_like(age),age+2))
   finite=finite and all(bool(torch.isfinite(v).all()) for v in (obs['policy'],obs['critic'],reward))
   for n in resets:resets[n]+=int(env.termination_manager.get_term(n).sum())
  physics=int(env._integrated_contact.tick)-tick;feedback=int(env._feedback_100hz_tick)-fb;callbacks=int(env.h1_callback_count)-cb
  assert finite and physics==192 and feedback==48 and callbacks==192
  assert {k:env._physics_action_delay.calls[k]-calls[k] for k in ('legs','wheels')}=={'legs':192,'wheels':192}
  guard.assert_new_nominals_unchanged();after=guard.verify_live_parameters();assert after['actual_parameters_pass'] and all(v==0 for v in sentinels.values())
  put('H1_FRESH80_COMPLETE.json',dict(passed=True,scope='Original normalH1 ownfactory true270/phase100 age+2 fresh80 noPT only',asset_SHA=identity.usd_sha256,contract_SHA=identity.contract_sha256,num_envs=80,controls=24,physics_callbacks=physics,H1_callbacks=callbacks,feedback_samples=feedback,finite_policy_critic_reward=finite,actual_mild_DR_audit_after=after,exact_H1_bank_compatibility=env._mod4v1_h1_bank_compatibility,termination_events=resets,sentinels=sentinels,model_opens=0,source_decodes=0,actor_calls=0,optimizer_updates=0,canonical_access=False,one_explicit_fresh_reset=1,D6_scope='originalgasdamping only',getter_scope='original component memory not independentbackend',birth_inertia_independent_qualification=False,full20k_restore_or_skill_pass=False))
 except BaseException:
  put('H1_FRESH80_ORIGINAL_ERROR.json',dict(error=traceback.format_exc(),sentinels=sentinels,model_opens=0,canonical_access=False));raise
 finally:
  try:
   if env is not None:env.close();put('ENV_CLOSE_RETURNED.json',dict(closed=True))
  finally:
   if ns is not None:put('APP_CLOSING.json',dict(calling_original_App_close=True));ns['app'].close()
if __name__=='__main__':main()
