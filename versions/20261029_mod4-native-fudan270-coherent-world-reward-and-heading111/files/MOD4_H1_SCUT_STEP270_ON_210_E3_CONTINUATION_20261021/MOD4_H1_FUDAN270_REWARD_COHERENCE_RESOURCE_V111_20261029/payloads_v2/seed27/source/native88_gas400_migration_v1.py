"""Changed-plant native R5→nominal400 bridge integration, source-only candidate.

Receives decoded qualified source; performs no model/asset I/O or control.
Original native learner losses/sampler/control/physical success stay external.
"""
from dataclasses import asdict
from copy import deepcopy
import torch
from same_architecture_native_continuation_candidate_v1 import restore_same_architecture,exact_plain

REFERENCE_SHA='9223a53e7bf85a0dc3505cc46c0eb33d04fc35a9bf85e7ffe0e4fbd03e1e46c3'
SOURCES={
 'h1':dict(SHA='ae5ff91877bcfdda72b864a181fdbbbd0c78401cb34591ca507adda44a6632e9',updates=3317,world_updates=33170,policy_updates=3253,seed=27),
 'recovery':dict(SHA='870e63b6ef41f870109fc1c3b6d9d67fe2f472ca8436145755db5d74a7b8e404',updates=1409,world_updates=14090,policy_updates=1345,seed=29)}
KIND='MOD4_H1_NATIVE88_GAS400_CHANGED_PLANT_NATIVE_SOURCE_CPU_V1'
NATIVE_CONTRACT=dict(state_joints=30,actions=6,obs_dim=86,goal_dim=146,packed_state_dim=127,dynamic_aux_dim=54,static_context_dim=31,
 fresh4096_policy_only_bootstrap=False,original_physics_and_success_unchanged=False,
 original_RSL_core_frozen_bootstrap_only=True,not_production_expert_source=True,
 replay_not_saved_matching_upstream_resume_not_exact_PhysX_replay=True,
 changed_plant700_to_nominal400=True,native_all_models_norms_threeopts_global_counters_restored=True,
 original_clock_solver_geometry_physical_V8_reward_command_success_unchanged=True,native_objective_changed=True,
 nominal_gas_stiffness_N_m=2000.,nominal_gas_damping_Ns_m=3.,gas_upper_q_m=.020639440248416612,
 gas_lower_q_original_preserved=True,gas_target_q_original_preserved=True,gas_force_curve_hardware_calibrated=False,
 fresh_physics_replay_history=True,fresh_control_warmup=64,new_window_world_only_iterations=64,minimum_new_WM_steps_before_first_newPi=640)
def require(v,msg):
 if not v:raise ValueError(msg)
def validate_role_source(key,SHA,progress):
 require(key in SOURCES,'only own qualified R5 h1/recovery source')
 source=SOURCES[key];require(SHA==source['SHA'],'wrong-role/source SHA')
 require(all(progress[k]==source[k] and type(progress[k]) is int for k in ('updates','world_updates','policy_updates')),'R5 formal source counter binding')
 return deepcopy(source)
def assert_declared_admission(key,task,go):
 source=validate_role_source(key,task['source_SHA'],task['source_progress'])
 require(task['native_seed']==source['seed'] and go['source_SHA']==source['SHA'] and go['source_progress']==task['source_progress'],'own source/seed Task-GO scope')
 require(go['source_qualification_kind']==KIND,'new changed-plant source CPU kind; old87 branch forbidden')
 require(task['source_Adamstep']==832460 and task['native_reference_SHA']==REFERENCE_SHA,'frozen RSL witness/reference binding')
 require(task['changed_plant700_to_nominal400'] is True and go['changed_plant700_to_nominal400'] is True,'changed plant scope required')
 for field in ('gas400_parameter_source_contract_SHA','actual_gas400_asset_composition_report_SHA'):
  require(type(task[field]) is str and len(task[field])==64 and go[field]==task[field],'fresh pinned parameter/asset source admission required')
 require(go['max_parent_seconds']==3900 and go['exit_headroom_seconds']==300,'original finite lifecycle')
 require(task.get('independent_own_step_objective_admission_passed') is True and go.get('independent_own_step_objective_admission_passed') is True,'400N change alone cannot authorize the known misaligned objective')
 require(type(task.get('own_step_objective_qualification_SHA')) is str and len(task['own_step_objective_qualification_SHA'])==64 and go.get('own_step_objective_qualification_SHA')==task['own_step_objective_qualification_SHA'],'separate effective task-objective repair/admission pin required')
 return source
def verify_loaded_frozen_RSL_fresh_plant(runner,env,full):
 from same_architecture_native_continuation_candidate_v1 import exact_plain
 def exact(a,b):
  if torch.is_tensor(a):return torch.is_tensor(b) and a.dtype==b.dtype and a.shape==b.shape and torch.equal(a.cpu(),b.cpu())
  if isinstance(a,dict):return isinstance(b,dict) and set(a)==set(b) and all(exact(a[k],b[k]) for k in a)
  if isinstance(a,(list,tuple)):return type(a) is type(b) and len(a)==len(b) and all(exact(x,y) for x,y in zip(a,b))
  return type(a) is type(b) and a==b
 require(env.num_envs==4096 and env.physics_dt==.0025 and env.step_dt==.01 and env.cfg.decimation==4 and env.cfg.episode_length_s==5.,'fresh original4096/5s numerical clock')
 require(env._sim_step_counter==0 and not bool(env.h1_phase.age_control.any()) and not bool(env.h1_phase.goal.success.any()),'no old physical phase or credits')
 require(len(full['actor_state_dict'])==9 and len(full['critic_state_dict'])==8 and full['actor_state_dict']['distribution.std_param'].shape==(6,),'complete frozen RSL core')
 require(len(full['optimizer_state_dict']['state'])==17 and {int(x['step']) for x in full['optimizer_state_dict']['state'].values()}=={832460},'frozen RSL17Adam832460 witness distinct from native threeopts')
 for name,current in [('actor_state_dict',runner.alg.actor.state_dict()),('critic_state_dict',runner.alg.critic.state_dict()),('optimizer_state_dict',runner.alg.optimizer.state_dict())]:require(exact(current,full[name]),'loaded frozen RSL differs from qualified R5 '+name)
 for component in (env._sensor_mild,env._physics_action_delay,env._spring_pressure,env._gas_damping,env._chassis_com,env._explicit_pd):
  s=component.state_dict();require(s.get('n',s.get('num_envs'))==4096,'fresh new DR population')
 return dict(frozen_RSL_actor9_critic8_STD6_17Adam832460_exact=True,fresh400N_environment=True,native_models_and_optimizers_will_restore_from_own_R5=True,old700N_environment_DR_not_restored=True,not_same_physics_resume=True)

class Gas400Window:
 def __init__(self,learner,bridge,trace,key,source):
  self.learner=learner;self.bridge=bridge;self.trace=trace;self.key=key;self.source=deepcopy(source)
  self.start_sim_steps=learner.sim_steps;self.new_wm=0;self.new_pi=0;self.first_pi=None;self.preload_evidence=None
  require(trace.total==0,'new trace/control namespace required')
 def counters(self):
  s=self.source;b=self.bridge
  require(b.wm_updates-s['world_updates']==self.new_wm and b.pi_updates-s['policy_updates']==self.new_pi,'new update records/global counters disagree')
  require(self.learner.sim_steps-self.start_sim_steps==self.trace.total*self.learner.env.num_envs,'complete control/transition count disagreement')
  return dict(native_iteration=self.learner.iteration,window_iteration=self.learner.iteration-s['updates'],world_updates=b.wm_updates,policy_updates=b.pi_updates,
   new_world_updates=self.new_wm,new_policy_updates=self.new_pi,completed_fresh_controls=self.trace.total,window_start_sim_steps=self.start_sim_steps)
 def allow_policy_update(self,iteration):
  c=self.counters();require(iteration==self.learner.iteration,'train predicate actual iteration scope')
  ready=iteration-self.source['updates']>=64 and self.trace.total>=64 and self.new_wm>=640
  if ready:require(self.preload_evidence is not None and self.preload_evidence['actual_original_preload_active'] is True,'real original prewrite preload proof missing')
  return ready
 def before_policy_update(self):require(self.allow_policy_update(self.learner.iteration),'new plant world-only adaptation incomplete; old positive counters cannot bypass')
 def completed_world_update(self):
  require(self.bridge.wm_updates==self.source['world_updates']+self.new_wm+1,'WM actual completed counter ordering');self.new_wm+=1
 def completed_policy_update(self):
  # Called only after original optimizer returns finite and original globalPi++.
  require(self.bridge.pi_updates==self.source['policy_updates']+self.new_pi+1,'Pi actual completed counter ordering');self.new_pi+=1
  if self.first_pi is None:self.first_pi=dict(native_iteration=self.learner.iteration,window_iteration=self.learner.iteration-self.source['updates'],completed_fresh_controls=self.trace.total,new_world_updates=self.new_wm,new_policy_updates=self.new_pi)
 def snapshot(self):
  return dict(schema='mod4.native88.gas400.changed_plant_window.v1',role=self.key,source=deepcopy(self.source),reference_SHA=REFERENCE_SHA,
   parameter_source_contract_SHA=self.parameter_contract_SHA,actual_asset_composition_report_SHA=self.asset_report_SHA,
   adaptation=dict(fresh_warmup_controls=64,new_window_world_only_iterations=64,minimum_new_world_steps_before_newPi=640),
   counters=self.counters(),first_new_policy_update=deepcopy(self.first_pi),prewrite_preload_validation=deepcopy(self.preload_evidence),not_same_physics=True,hardware_force_curve_calibrated=False)
 def qualifies_preupdate(self,publication,checkpoint):
  w=publication['native88_migration_window'];verify_window(w)
  if w['counters']['new_policy_updates']==0:return False
  verify_window(w,require_new_pi=True)
  return checkpoint['SHA']==publication['SHA'] and checkpoint['bytes']==publication['bytes'] and checkpoint['before_control']==self.trace.total and w['counters']['completed_fresh_controls']==self.trace.total

def install_restored_window(learner,bridge,trace,full,*,key,source_SHA,expected_source_contract,expected_args,parameter_contract_SHA,asset_report_SHA):
 source=validate_role_source(key,source_SHA,{k:SOURCES[key][k] for k in ('updates','world_updates','policy_updates')})
 require(expected_args['seed']==source['seed'] and expected_args['warmup_steps']==64 and expected_args['wm_only_iters']==64 and expected_args['wm_batches']==10,'original native config plus explicit64/640 adaptation')
 proof=restore_same_architecture(learner,bridge,full,expected_source_contract=expected_source_contract,expected_args=expected_args,
  expected_progress={k:source[k] for k in ('updates','world_updates','policy_updates')},expected_reference_SHA=REFERENCE_SHA)
 window=Gas400Window(learner,bridge,trace,key,source);window.parameter_contract_SHA=parameter_contract_SHA;window.asset_report_SHA=asset_report_SHA
 learner.native88_migration=window;bridge.native88_migration=window
 return window,dict(proof,changed_plant=True,source=source,world_only_uses_new_window_not_global_iteration=True,source_positivePi_is_not_new_progress=True)

def observe_first_original_preload_write(env,window,*,expected_joint_names,emit):
 """One readonly observation at original write, not a target/physics setter.

 Original Mod4Env.step applies mode='step' preload before super.step/write.
 A post-reset control boundary may truthfully contain target0; inspecting an
 actual prewrite once avoids demanding qref on already-reset rows forever.
 """
 from actual_DR_memory_getter_v1 import tensor
 from gas400_sdk_admission_candidate_v1 import check_actual_new_gas
 robot=env.scene['robot'];old=robot.write_data_to_sim
 def write(*args,**kwargs):
  if window.preload_evidence is None:
   proof=check_actual_new_gas(env,expected_joint_names=expected_joint_names,tensor=tensor,require_active_preload=True)
   proof.update(original_physical_counter=int(env._sim_step_counter),observed_before_original_write=True,no_target_or_action_changed=True)
   window.preload_evidence=proof;emit(proof)
  return old(*args,**kwargs)
 robot.write_data_to_sim=write
 return old

def verify_window(w,require_new_pi=False):
 require(w['schema']=='mod4.native88.gas400.changed_plant_window.v1' and w['not_same_physics'] is True,'new typed migration window')
 s=validate_role_source(w['role'],w['source']['SHA'],w['source']);c=w['counters']
 require(exact_plain(w['source'],s),'exact source-role/counter/seed row required')
 require(w['reference_SHA']==REFERENCE_SHA and w['adaptation']==dict(fresh_warmup_controls=64,new_window_world_only_iterations=64,minimum_new_world_steps_before_newPi=640),'reference/adaptation scope')
 for key in ('parameter_source_contract_SHA','actual_asset_composition_report_SHA'):require(type(w[key]) is str and len(w[key])==64,'new parameter/asset proof pin absent')
 require(all(type(c[key]) is int for key in ('native_iteration','window_iteration','world_updates','policy_updates','new_world_updates','new_policy_updates','completed_fresh_controls','window_start_sim_steps')) and c['completed_fresh_controls']>=0,'integer cumulative/window counters required')
 require(c['native_iteration']-s['updates']==c['window_iteration']>=0 and c['world_updates']-s['world_updates']==c['new_world_updates']>=0 and c['policy_updates']-s['policy_updates']==c['new_policy_updates']>=0,'source/window/global deltas differ')
 if c['new_policy_updates']>0:
  first=w['first_new_policy_update'];require(first is not None and first['window_iteration']>=64 and first['completed_fresh_controls']>=64 and first['new_world_updates']>=640 and first['new_policy_updates']==1,'first newPi before declared adaptation')
  require(w['prewrite_preload_validation'] is not None and w['prewrite_preload_validation']['actual_original_preload_active'] is True,'actual prewrite preload proof required for newPi')
 if require_new_pi:require(c['new_policy_updates']>0 and c['new_world_updates']>=640 and c['completed_fresh_controls']>=64,'old positive sourcePi is not new formal progress')
 return True
def verify_saved_migration(full,expected):
 w=expected['native88_migration_window'];verify_window(w)
 require(exact_plain(full['UniSuperMimic_changed_plant_migration'],w),'saved migration/window binding')
 c=w['counters'];require(c['native_iteration']==expected['native_iteration'] and c['world_updates']==expected['world_updates'] and c['policy_updates']==expected['policy_updates'],'save publication/global/window disagreement')
 require(exact_plain(full['UniSuperMimic_test_contract'],NATIVE_CONTRACT),'new strict changed-plant native output contract')
 producer=expected['producer']
 require(exact_plain(producer['initial_native_source'],w['source']) and producer['gas400_parameter_source_contract_SHA']==w['parameter_source_contract_SHA'] and producer['actual_gas400_asset_composition_report_SHA']==w['actual_asset_composition_report_SHA'],'producer source/parameter/asset pins differ')
 require(producer['native_architecture_fresh'] is False and producer['method']=='MOD4_own_Fudan_native88_nominal400_changed_plant','new typed continued-architecture producer')
 recipe=full['spring_pressure_recipe'];require(recipe['nominal_stiffness_N_m']==2000 and recipe['actual_stiffness_bounds_N_m']==[1800,2200],'fullsave new2000 gas recipe required')
class RequireNewWindowFinal:
 """Keep original lifecycle/fullsave; reject zero-newPi as a formal FINAL."""
 def __init__(self,publisher):self.publisher=publisher
 def __call__(self,*args,**kwargs):
  receipt=self.publisher(*args,**kwargs)
  verify_window(receipt['native88_migration_window'],require_new_pi=True)
  return receipt
