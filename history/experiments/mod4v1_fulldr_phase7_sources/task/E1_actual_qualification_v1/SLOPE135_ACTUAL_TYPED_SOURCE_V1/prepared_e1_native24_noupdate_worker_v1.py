"""PREPARED SOURCE ONLY: future originalE1 N20k restore->ONEreset->24mean controls.
No supervisor/SSH/dispatch/Ready/GO here. Requires a separately parent-created
ACTUAL Task; source-only descriptor is deliberately not an executable Task.
Exact E1factory/geometry/direction/retention/reward and original fullhelperchain.
"""
from pathlib import Path
import argparse,copy,importlib,json,os,runpy,sys,time,traceback

def main():
 p=argparse.ArgumentParser();p.add_argument('--job-root',type=Path,required=True);p.add_argument('--task',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();root=a.job_root.resolve();task=json.loads(a.task.read_bytes());meta=json.loads((root/'E1_CANONICAL_SOURCE_METADATA.json').read_bytes());out=a.out;out.mkdir(parents=True,exist_ok=False)
 def put(name,value):
  with (out/name).open('x',encoding='utf-8') as f:json.dump(value,f,indent=2,allow_nan=False)
 if task.get('kind')!='E1_MOD4V1_N20K_NATIVE24_ACTUAL_PARENT_TASK_V1' or task.get('separate_actual_SDK_permission') is not True:raise RuntimeError('Source-only descriptor is not an admitted SDK task')
 assert task['canonical']==meta['canonical'] and task['source_SHA']==meta['original_source_SHA'] and task['source_read_purpose']
 assert task['num_envs']==20000 and task['controls']==24 and task['no_optimizer_update'] is True
 source=Path(task['selected_original_source_path']);asset=Path(task['asset_dir']);mod=root/'runtime/isaac/mod4'
 # Original manifest RMscope first, then explicit newasset before FIRST taskimport.
 for key in list(os.environ):
  if key.startswith('RM_') or key in ('RANK','LOCAL_RANK','WORLD_SIZE','MASTER_ADDR','MASTER_PORT'):del os.environ[key]
 os.environ.update({k:str(v) for k,v in meta['original_env'].items() if k not in ('RM_RESCUE_DEADLINE','RM_RESCUE_STOP_FILE')})
 os.environ.update(RM_KEEP_STD='1',RM_PHYSICS_DT_S='.0025',RM_SOLVER_POS='32',RM_SOLVER_VEL='4',RM_MOD4_TERRAIN='flat',RM_MOD4_MAP='',RM_JUMP_SCRIPT_PROB='0')
 sys.path[:0]=[str(mod),str(root/'runtime'),str(root/'lib')]
 from mod4v1_fresh_dr_guard import bind_before_task_import,verify_task_module,configure_new_task,FreshDRNominalGuard
 from e1_pinned_source_v1 import PinnedSourceE1,selected_source,runner_source_load_scope
 identity=bind_before_task_import(asset);ns=env=cache=None;forbidden={'alg_update':0,'optimizer_step':0,'runner_learn':0}
 try:
  import torch
  cache=PinnedSourceE1(torch,source,task['source_SHA'],task.get('source_bytes'),role=meta['role'])
  ck=cache.state;savedLR=ck['optimizer_state_dict']['param_groups'][0]['lr'];savedIteration=ck['iter']
  entry=mod/meta['entry'];sys.argv=[str(entry),'--headless','--device','cuda:0','--num_envs','20000','--seed',str(task.get('seed',20260928)),'--steps_per_env','24','--learning_rate',str(savedLR),'--init_checkpoint',str(source),'--log_root',str(out/'logs'),'--run_name',meta['canonical']+'_FUTURE_NATIVE24_NOUPDATE','--additional_iterations','1']
  ns=runpy.run_path(str(entry),run_name='E1_original_factory_no_trainer_main')
  import mod4_task
  verify_task_module(mod4_task,identity);assert mod4_task.POLICY_HZ==50 and mod4_task.DECIMATION==8
  oldcfg=ns['Mod4EnvCfg'];factory=ns['build_env']
  def cfg():
   c=oldcfg();c.terminations.mimic.params={**c.terminations.mimic.params,'threshold':.01};configure_new_task(c,identity)
   assert c.sim.dt==.0025 and c.decimation==8 and c.sim.physics.solver_type==1
   assert c.scene.robot.spawn.articulation_props.solver_position_iteration_count==32 and c.scene.robot.spawn.articulation_props.solver_velocity_iteration_count==4
   return c
  factory.__globals__['Mod4EnvCfg']=cfg
  with selected_source(cache):
   env=factory();guard=FreshDRNominalGuard(env,identity,torch_module=torch,tensor_converter=importlib.import_module('mild_dr').tensor);env._mod4v1_nominal_guard=guard
   assert env.num_envs==20000 and env.physics_dt==.0025 and env.step_dt==.02
   command=env.command_manager.get_term('twist');assert command._dt==.02
   rcfg=ns['runner_config']();vec=ns['RslRlVecEnvWrapper'](env,clip_actions=rcfg.clip_actions);rcfg=ns['handle_deprecated_rsl_rl_cfg'](rcfg,ns['metadata'].version('rsl-rl-lib'));runner=ns['OnPolicyRunner'](vec,rcfg.to_dict(),log_dir=str(out/'logs'),device=rcfg.device)
   with runner_source_load_scope():runner.load(str(source))
   helper=importlib.import_module(meta['restore_helper'])
   with guard.around_original_fullstate_restore():helper.resume_e1_new_episode(runner,env,str(source),str(out))
   # Do not call runner.learn/alg.update or optimizer.step even once.
   def forbid(name):
    def fail(*aa,**kk):forbidden[name]+=1;raise RuntimeError('NOUPDATE forbids '+name)
    return fail
   runner.alg.update=forbid('alg_update');runner.alg.optimizer.step=forbid('optimizer_step');runner.learn=forbid('runner_learn')
   from spring_pressure_checkpoint import exact
   assert runner.current_learning_iteration==savedIteration and runner.alg.learning_rate==savedLR
   assert exact(runner.alg.actor.state_dict(),ck['actor_state_dict']) and exact(runner.alg.critic.state_dict(),ck['critic_state_dict']) and exact(runner.alg.optimizer.state_dict(),ck['optimizer_state_dict'])
   core=lambda:dict(actor=copy.deepcopy(runner.alg.actor.state_dict()),critic=copy.deepcopy(runner.alg.critic.state_dict()),optimizer=copy.deepcopy(runner.alg.optimizer.state_dict()),iteration=runner.current_learning_iteration,LR=runner.alg.learning_rate)
   before=core();audit_before=env._mild_dr.audit();assert audit_before['actual_parameters_pass']
   actual=dict(iteration=savedIteration,LR=savedLR,STD6=runner.alg.actor.state_dict()['distribution.std_param'].detach().cpu().tolist(),Adam_steps=sorted({int(s['step']) for s in runner.alg.optimizer.state_dict()['state'].values()}))
   put('E1_FULLRESTORE_BEFORE_NATIVE24.json',dict(passed=True,canonical=meta['canonical'],actual_source_counters=actual,cache=cache.receipt(),nominal_guard=guard.receipt(),actual_mild_DR_audit=audit_before,componentmemory_not_independentbackend=True,birthinertia_not_qualified=True,original_E1_scope=meta['scope'],one_original_fresh_reset=guard.reset_calls))
   runner.alg.actor.eval();runner.alg.critic.eval();obs=runner.env.get_observations();guard.check_observations(obs);start=int(env._sim_step_counter);feedback=int(env._feedback_100hz_tick);contact=int(env._integrated_contact.tick);rows=[]
   with torch.inference_mode():
    for i in range(24):
     tick=int(env._sim_step_counter);fb=int(env._feedback_100hz_tick);ct=int(env._integrated_contact.tick);action=runner.alg.actor(obs,stochastic_output=False)
     assert action.shape==(20000,6) and torch.isfinite(action).all();obs,reward,done,info=runner.env.step(action)
     assert int(env._sim_step_counter)-tick==8 and int(env._integrated_contact.tick)-ct==8 and int(env._feedback_100hz_tick)-fb==2
     assert obs['policy'].shape==(20000,35) and obs['critic'].shape==(20000,38) and torch.isfinite(obs['policy']).all() and torch.isfinite(obs['critic']).all() and torch.isfinite(reward).all()
     rows.append(dict(control=i+1,physics_tick=int(env._sim_step_counter),feedback_tick=int(env._feedback_100hz_tick),selected_episode_resets=int(done.bool().sum()),command_dt_s=float(command._dt),original_E1_phase_and_direction_logic_unmodified=True))
   assert int(env._sim_step_counter)-start==int(env._integrated_contact.tick)-contact==192 and int(env._feedback_100hz_tick)-feedback==48
   assert exact(before,core()) and all(v==0 for v in forbidden.values());audit_after=env._mild_dr.audit();assert audit_after['actual_parameters_pass'];guard.assert_new_nominals_unchanged()
   counts=cache.receipt();assert counts['selected_source_physical_byte_reads']==counts['selected_source_SHA_calculations']==counts['selected_source_decodes']==1
   put('E1_NATIVE24_192PHYSICS_48FEEDBACK_NOUPDATE_COMPLETE.json',dict(passed=True,canonical=meta['canonical'],source_SHA=task['source_SHA'],actual_source_counters=actual,num_envs=20000,controls=24,physics_callbacks=192,feedback_samples=48,per_control=rows,core_before_after_exact=True,forbidden_calls=forbidden,original_scope=meta['scope'],one_original_fresh_reset=guard.reset_calls,nominal_guard=guard.receipt(),actual_mild_DR_audit_before=audit_before,actual_mild_DR_audit_after=audit_after,source_cache=counts,D6='originalgasdamping only',componentmemory_not_independentbackend=True,birthinertia_not_qualified=True,skill_or_full_adaptation_graduation=False,productionGO_or_PPO=False,canonical_access=False))
 except BaseException:
  put('E1_NATIVE24_ORIGINAL_ERROR.json',dict(error=traceback.format_exc(),source_cache=cache.receipt() if cache is not None else None,forbidden_calls=forbidden,canonical_access=False));raise
 finally:
  if cache is not None:put('E1_SOURCE_FINAL_READ_COUNTS.json',cache.receipt())
  try:
   if env is not None:env.close();put('ENV_CLOSE_RETURNED.json',dict(closed=True))
  finally:
   if ns is not None:put('APP_CLOSING.json',dict(calling_original_App_close=True));ns['app'].close()
if __name__=='__main__':main()
