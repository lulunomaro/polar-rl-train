"""Own E1 factory fresh80 noPT/actor/optimizer,24controls only; not savedrestore."""
from pathlib import Path
import argparse,importlib,json,os,runpy,sys,time,traceback

def main():
 p=argparse.ArgumentParser();p.add_argument('--job-root',type=Path,required=True);p.add_argument('--task',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();B=a.job_root;task=json.loads(a.task.read_bytes());meta=json.loads((B/'E1_CANONICAL_SOURCE_METADATA.json').read_bytes());out=a.out;out.mkdir(exist_ok=False)
 def put(n,v):
  with (out/n).open('x',encoding='utf-8') as f:json.dump(v,f,indent=2,allow_nan=False)
 assert task['kind']=='E1_CANONICAL_ACTUAL_FRESH80_NO_PT_V1' and task['num_envs']==80 and task['controls']==24
 for k in list(os.environ):
  if k.startswith('RM_') or k in ('RANK','LOCAL_RANK','WORLD_SIZE','MASTER_ADDR','MASTER_PORT'):del os.environ[k]
 os.environ.update({k:str(v) for k,v in meta['original_env'].items() if k not in ('RM_RESCUE_DEADLINE','RM_RESCUE_STOP_FILE')})
 os.environ.update(RM_KEEP_STD='1',RM_PHYSICS_DT_S='.0025',RM_SOLVER_POS='32',RM_SOLVER_VEL='4',RM_MOD4_TERRAIN='flat',RM_MOD4_MAP='',RM_JUMP_SCRIPT_PROB='0',MOD4V1_E1_ACTUAL_JOB_ROOT=str(B),MOD4V1_E1_KIT_STORAGE_ROOT=str(B/'kit_isolation'))
 storage=B/'kit_isolation';storage.mkdir();(storage/'data').mkdir();(storage/'DerivedDataCache').mkdir();(storage/'data/user.config.json').write_text('{}')
 mod=B/'runtime/isaac/mod4';sys.path[:0]=[str(mod),str(B/'runtime')]
 from mod4v1_fresh_dr_guard import bind_before_task_import,verify_task_module,configure_new_task,FreshDRNominalGuard
 identity=bind_before_task_import(B/'new_assets');entry=mod/meta['entry'];sys.argv=[str(entry),'--headless','--device','cuda:0','--num_envs','80','--seed','20260928','--dry_run','24']
 ns=env=None;calls=dict(torch_load=0,runner_construct=0,actor_calls=0,optimizer_step=0)
 try:
  import torch
  def no_load(*aa,**kk):calls['torch_load']+=1;raise RuntimeError('Fresh80 forbids every torch.load')
  def no_opt(*aa,**kk):calls['optimizer_step']+=1;raise RuntimeError('Fresh80 forbids optimizer.step')
  torch.load=no_load;torch.optim.Optimizer.step=no_opt;torch.optim.Adam.step=no_opt
  ns=runpy.run_path(str(entry),run_name='E1_fresh80_original_factory_no_trainer_main')
  import mod4_task
  verify_task_module(mod4_task,identity);assert mod4_task.POLICY_HZ==50 and mod4_task.DECIMATION==8
  oldcfg=ns['Mod4EnvCfg'];factory=ns['build_env']
  def cfg():
   c=oldcfg();c.terminations.mimic.params={**c.terminations.mimic.params,'threshold':.01};configure_new_task(c,identity)
   assert c.sim.dt==.0025 and c.decimation==8 and c.sim.physics.solver_type==1
   assert c.scene.robot.spawn.articulation_props.solver_position_iteration_count==32 and c.scene.robot.spawn.articulation_props.solver_velocity_iteration_count==4
   return c
  factory.__globals__['Mod4EnvCfg']=cfg
  def no_runner(*aa,**kk):calls['runner_construct']+=1;raise RuntimeError('Fresh80 forbids runner and actor construction')
  ns['OnPolicyRunner'].__init__=no_runner
  env=factory();assert type(env).__name__=='RetentionLearningEnv' and env.num_envs==80 and env.physics_dt==.0025 and env.step_dt==.02
  from mild_dr import tensor
  guard=FreshDRNominalGuard(env,identity,torch_module=torch,tensor_converter=tensor);guard.assert_new_nominals_unchanged();env.reset();guard.assert_new_nominals_unchanged();before=guard.verify_live_parameters();assert before['actual_parameters_pass']
  command=env.command_manager.get_term('twist');assert command._dt==.02
  state=importlib.import_module('curb20_entry_current_state' if meta['role']=='E1_CURB' else 'slope5_current_state');terrain_identity=state.identity(state.current_state(env))
  proof=env._mod4v1_e1_collision_bank_compatibility
  put('E1_FRESH80_BEFORE.json',dict(canonical=meta['canonical'],original_E1_factory_type=type(env).__module__+'.'+type(env).__name__,terrain_identity=terrain_identity,command_type=type(command).__module__+'.'+type(command).__name__,actual_mild_DR_audit=before,exact_resetbank=proof,one_explicit_fresh_reset=1,sentinels=calls,model_opens=0))
  start=int(env._sim_step_counter);fb=int(env._feedback_100hz_tick);contact=int(env._integrated_contact.tick);zeros=torch.zeros((80,6),device=env.device);finite=True
  for i in range(24):
   obs,reward,terminated,truncated,extra=env.step(zeros);finite=finite and all(bool(torch.isfinite(v).all()) for v in (obs['policy'],obs['critic'],reward))
  assert finite and int(env._sim_step_counter)-start==int(env._integrated_contact.tick)-contact==192 and int(env._feedback_100hz_tick)-fb==48
  assert obs['policy'].shape==(80,35) and obs['critic'].shape==(80,38) and all(v==0 for v in calls.values());guard.assert_new_nominals_unchanged();after=guard.verify_live_parameters();assert after['actual_parameters_pass']
  put('E1_FRESH80_COMPLETE.json',dict(passed=True,canonical=meta['canonical'],scope='Own trueE1 terrain/direction-entry/retention factory fresh80 noPT only',num_envs=80,controls=24,physics_callbacks=192,feedback_samples=48,finite_policy_critic_reward=finite,interface=[35,38,6],clock=[50,100,.0025,32,4],USD_SHA=identity.usd_sha256,contract_SHA=identity.contract_sha256,closure_episode_m=.01,mimic_rad=.01,actual_mild_DR_audit_before=before,actual_mild_DR_audit_after=after,exact_original_resetbank=proof,original_terrain_identity=terrain_identity,one_explicit_fresh_reset=1,sentinels=calls,model_opens=0,actor_calls=0,optimizer_updates=0,canonical_budget_GO_operations=0,not_independent_backend_or_birthinertia_or_skill_graduation=True,D6='Originalgasdamping only'))
 except BaseException:
  put('E1_FRESH80_ORIGINAL_ERROR.json',dict(error=traceback.format_exc(),sentinels=calls,model_opens=0,canonical_access=False));raise
 finally:
  try:
   if env is not None:env.close();put('ENV_CLOSE_RETURNED.json',dict(closed=True))
  finally:
   if ns is not None:put('APP_CLOSING.json',dict(calling_original_App_close=True));ns['app'].close()
if __name__=='__main__':main()
