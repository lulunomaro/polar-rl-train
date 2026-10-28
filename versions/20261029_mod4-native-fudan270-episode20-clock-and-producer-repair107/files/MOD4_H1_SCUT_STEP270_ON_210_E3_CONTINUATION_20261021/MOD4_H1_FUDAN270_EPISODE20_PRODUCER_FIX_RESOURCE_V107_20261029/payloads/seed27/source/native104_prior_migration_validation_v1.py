"""Exactly qualified88C h1 -> independent flat05 objective, no model/file I/O.

The400N plant is retained; this is not another700->400 migration. Old reference
and source producer are validated literally; new outputs have a different task.
"""
from copy import deepcopy
from dataclasses import asdict
import math
from native104_prior_pins_literal_v1 import (SOURCE_PINS,NATIVE_CONTRACT,FLAT_OBJECTIVE_SHA,FLAT_OBJECTIVE_CONTRACT,OUTPUT_GAS400_PARAMETER_CONTRACT_SHA,SOURCE_MODE)

SOURCE_SHA='35e1657815fc972ed954d258fe62326074ebeb862e5bcfce7150b3ef58dc2b9f'
REFERENCE_SHA=FLAT_OBJECTIVE_SHA
SOURCE_REFERENCE_SHA='6ca65eebbefd1fddc1a5a0332914ce0db87b8c46e70c7b5f51f6047a58cf394c'
METHOD='MOD4_fudan103_actual270_from_qualified101'
KIND='MOD4_NATIVE101_FUDAN270_TARGET103_TYPED_SOURCE_CPU_V1'
SOURCES={'h1': {'SHA': '35e1657815fc972ed954d258fe62326074ebeb862e5bcfce7150b3ef58dc2b9f',
        'updates': 14784,
        'world_updates': 147840,
        'policy_updates': 14272,
        'seed': 27}}
def require(v,message):
 if not v:raise ValueError(message)
def exact_plain(a,b):
 if type(a)is not type(b):return False
 if isinstance(a,dict):return set(a)==set(b) and all(exact_plain(a[k],b[k]) for k in a)
 if isinstance(a,(list,tuple)):return len(a)==len(b) and all(exact_plain(x,y) for x,y in zip(a,b))
 return a==b
def validate_role_source(key,SHA,progress):
 require(key=='h1' and SHA==SOURCE_SHA,'only exactly qualified88C h1 admitted')
 require(all(type(progress[k])is int and progress[k]==SOURCES[key][k] for k in ('updates','world_updates','policy_updates')),'88C formal progress differs')
 return deepcopy(SOURCES[key])
def assert_declared_admission(key,task,go):
 source=validate_role_source(key,task['source_SHA'],task['source_progress'])
 require(task['input_start_mode']==go['input_start_mode']==SOURCE_MODE,'typed101 continuation')
 for field in ('fudan_step_task','task_focused_real_replay','goal_conditioning','imagination_terminal_exposure'):
  require(exact_plain(task[field],NATIVE_CONTRACT[field]) and exact_plain(go[field],task[field]),'signed Fudan task '+field)
 require(task['native_learning_seed']==go['native_learning_seed']==27 and task['native_seed']==go['native_seed'] and task['native_seed'] in (27,28),'physical and saved learning seed split')
 require(go['source_SHA']==SOURCE_SHA and exact_plain(go['source_progress'],task['source_progress']),'signed qualified101 source')
 require(go['source_qualification_kind']==task['source_qualification_kind']==KIND and task['source_Adamstep']==832460,'new source kind and frozen RSL witness')
 require(task['native_reference_SHA']==go['native_reference_SHA']==REFERENCE_SHA,'new terminal task goal')
 require(task['changed_plant700_to_nominal400'] is False and go['changed_plant700_to_nominal400'] is False,'same400 plant')
 for field in ('gas400_parameter_source_contract_SHA','actual_gas400_asset_composition_report_SHA','own_step_objective_qualification_SHA'):
  require(type(task[field]) is str and len(task[field])==64 and go[field]==task[field],'source/asset pin '+field)
 require(task['gas400_parameter_source_contract_SHA']==OUTPUT_GAS400_PARAMETER_CONTRACT_SHA,'actual400 source recipe')
 require(go['max_parent_seconds']==3900 and go['exit_headroom_seconds']==300,'original finite lifecycle')
 return source
def validate_source(full,expected_source_contract,expected_args,expected_progress,expected_reference_SHA):
 require(exact_plain(expected_source_contract,SOURCE_PINS['native_contract']) and exact_plain(expected_args,SOURCE_PINS['native_args']),'qualified99 source contract/args')
 require(exact_plain(expected_progress,{k:SOURCES['h1'][k] for k in ('updates','world_updates','policy_updates')}) and expected_reference_SHA==SOURCE_REFERENCE_SHA,'qualified99 counters/reference')
 native=full['UniSuperMimic_H1_test'];pub=full['UniSuperMimic_publication']
 require(exact_plain(full['UniSuperMimic_test_contract'],SOURCE_PINS['native_contract']) and exact_plain(pub['producer'],SOURCE_PINS['producer']) and exact_plain(native['args'],expected_args),'qualified99 fullliteral source')
 require(native['iteration']==pub['native_iteration']==SOURCES['h1']['updates'] and pub['world_updates']==SOURCES['h1']['world_updates'] and pub['policy_updates']==SOURCES['h1']['policy_updates'],'qualified99 progress')
 from native101_prior_migration_validation_v1 import verify_saved_migration
 verify_saved_migration(full,pub)
 require(exact_plain(pub['native88_migration_window'],SOURCE_PINS['source_migration_window']),'qualified99 completed migration')
 for name,steps,count,betas in [('opt_wm',SOURCES['h1']['world_updates'],14,(.9,.999)),('opt_pi',SOURCES['h1']['policy_updates'],20,(.9,.95)),('opt_v',20*SOURCES['h1']['policy_updates'],6,(.9,.999))]:
  opt=native[name];require(len(opt['param_groups'])==1 and all(tuple(x['betas'])==betas for x in opt['param_groups']) and len(opt['state'])==count and {int(x['step']) for x in opt['state'].values()}=={steps},'qualified99 complete native optimizer '+name)
 require(len(full['optimizer_state_dict']['state'])==17 and {int(x['step']) for x in full['optimizer_state_dict']['state'].values()}=={832460},'unchanged separate frozenRSL')
 return native,pub

# Exact original restore_same_architecture function body is appended by the
# source-only builder, with only its validate_source global resolved above.

def restore_native88C_to_flat(learner,bridge,full,*,source_SHA):
 validate_role_source('h1',source_SHA,{k:SOURCES['h1'][k] for k in ('updates','world_updates','policy_updates')})
 proof=restore_same_architecture(learner,bridge,full,expected_source_contract=SOURCE_PINS['native_contract'],
  expected_args=SOURCE_PINS['native_args'],expected_progress={k:SOURCES['h1'][k] for k in ('updates','world_updates','policy_updates')},
  expected_reference_SHA=SOURCE_REFERENCE_SHA,expected_num_envs=4096)
 return dict(proof,source_SHA=source_SHA,source_objective_reference_SHA=SOURCE_REFERENCE_SHA,new_objective_reference_SHA=REFERENCE_SHA,
  new_objective=True,plant_nominal400_unchanged=True,new_700_to400_migration=False)

class FlatObjectiveWindow:
 def __init__(self,learner,bridge,trace):
  self.learner=learner;self.bridge=bridge;self.trace=trace;self.key='h1';self.source=deepcopy(SOURCES['h1'])
  self.start_sim_steps=learner.sim_steps;self.new_wm=0;self.new_pi=0;self.first_pi=None;self.preload_evidence=None
  require(trace.total==0,'fresh trace/control namespace')
 def counters(self):
  s=self.source;b=self.bridge
  require(b.wm_updates-s['world_updates']==self.new_wm and b.pi_updates-s['policy_updates']==self.new_pi,'new/global counters differ')
  require(self.learner.sim_steps-self.start_sim_steps==self.trace.total*self.learner.env.num_envs,'complete new control count')
  return dict(native_iteration=self.learner.iteration,window_iteration=self.learner.iteration-s['updates'],world_updates=b.wm_updates,policy_updates=b.pi_updates,
   new_world_updates=self.new_wm,new_policy_updates=self.new_pi,completed_fresh_controls=self.trace.total,window_start_sim_steps=self.start_sim_steps)
 def allow_policy_update(self,iteration):
  self.counters();require(iteration==self.learner.iteration,'actual iteration scope')
  ready=iteration-self.source['updates']>=64 and self.trace.total>=64 and self.new_wm>=640
  if ready:require(self.preload_evidence is not None and self.preload_evidence['actual_original_preload_active'] is True,'original prewrite preload readback')
  return ready
 def before_policy_update(self):require(self.allow_policy_update(self.learner.iteration),'new objective64/640 fresh window incomplete')
 def completed_world_update(self):
  require(self.bridge.wm_updates==self.source['world_updates']+self.new_wm+1,'WM completion order');self.new_wm+=1
 def completed_policy_update(self):
  require(self.bridge.pi_updates==self.source['policy_updates']+self.new_pi+1,'Pi completion order');self.new_pi+=1
  if self.first_pi is None:self.first_pi=dict(native_iteration=self.learner.iteration,window_iteration=self.learner.iteration-self.source['updates'],completed_fresh_controls=self.trace.total,new_world_updates=self.new_wm,new_policy_updates=self.new_pi)
 def snapshot(self):
  return dict(schema='mod4.native101_to_fudan270.target103.objective_window.v1',role='h1',source=deepcopy(self.source),reference_SHA=REFERENCE_SHA,
   source_reference_SHA=SOURCE_REFERENCE_SHA,new_objective=True,plant_nominal400_unchanged=True,changed_plant700_to_nominal400=False,
   parameter_source_contract_SHA=self.parameter_contract_SHA,actual_asset_composition_report_SHA=self.asset_report_SHA,
   adaptation=dict(fresh_warmup_controls=64,new_window_world_only_iterations=64,minimum_new_world_steps_before_newPi=640),
   counters=self.counters(),first_new_policy_update=deepcopy(self.first_pi),prewrite_preload_validation=deepcopy(self.preload_evidence),
   not_same_physics=True,hardware_force_curve_calibrated=False)
 def qualifies_preupdate(self,publication,checkpoint):
  w=publication['native88_migration_window'];verify_window(w)
  if w['counters']['new_policy_updates']==0:return False
  verify_window(w,require_new_pi=True)
  return checkpoint['SHA']==publication['SHA'] and checkpoint['bytes']==publication['bytes'] and checkpoint['before_control']==self.trace.total and w['counters']['completed_fresh_controls']==self.trace.total

def install_restored_window(learner,bridge,trace,full,*,key,source_SHA,expected_source_contract,expected_args,parameter_contract_SHA,asset_report_SHA):
 require(key=='h1' and exact_plain(expected_source_contract,SOURCE_PINS['native_contract']) and exact_plain(expected_args,SOURCE_PINS['native_args']),'typed88C caller source contract')
 require(parameter_contract_SHA==OUTPUT_GAS400_PARAMETER_CONTRACT_SHA and type(asset_report_SHA)is str and len(asset_report_SHA)==64,'same400 parameters plus fresh installed asset readback pin')
 proof=restore_native88C_to_flat(learner,bridge,full,source_SHA=source_SHA)
 window=FlatObjectiveWindow(learner,bridge,trace);window.parameter_contract_SHA=parameter_contract_SHA;window.asset_report_SHA=asset_report_SHA
 learner.native88_migration=window;bridge.native88_migration=window  # Legacy field name only; schema declares new objective.
 return window,dict(proof,changed_plant=False,world_only_uses_new_window_not_global_iteration=True,source_positivePi_is_not_new_progress=True)

def verify_window(w,require_new_pi=False):
 require(w['schema']=='mod4.native101_to_fudan270.target103.objective_window.v1' and w['new_objective'] is True and w['plant_nominal400_unchanged'] is True and w['changed_plant700_to_nominal400'] is False,'new flat objective schema, no false plant migration')
 require(w['not_same_physics'] is True,'fresh physical episode, not PhysX replay')
 s=validate_role_source(w['role'],w['source']['SHA'],w['source']);c=w['counters'];require(exact_plain(w['source'],s),'exact88C source row')
 require(w['reference_SHA']==REFERENCE_SHA and w['source_reference_SHA']==SOURCE_REFERENCE_SHA,'distinct old/new objective reference')
 require(w['adaptation']==dict(fresh_warmup_controls=64,new_window_world_only_iterations=64,minimum_new_world_steps_before_newPi=640),'original64/640 fresh window')
 require(w['parameter_source_contract_SHA']==OUTPUT_GAS400_PARAMETER_CONTRACT_SHA and type(w['actual_asset_composition_report_SHA'])is str and len(w['actual_asset_composition_report_SHA'])==64,'parameter/asset binding')
 require(all(type(c[k])is int for k in ('native_iteration','window_iteration','world_updates','policy_updates','new_world_updates','new_policy_updates','completed_fresh_controls','window_start_sim_steps')) and c['completed_fresh_controls']>=0,'integer counters')
 require(c['native_iteration']-s['updates']==c['window_iteration']>=0 and c['world_updates']-s['world_updates']==c['new_world_updates']>=0 and c['policy_updates']-s['policy_updates']==c['new_policy_updates']>=0,'source/global/window deltas')
 if c['new_policy_updates']>0:
  first=w['first_new_policy_update'];require(first is not None and first['window_iteration']>=64 and first['completed_fresh_controls']>=64 and first['new_world_updates']>=640 and first['new_policy_updates']==1,'first newPi after64/640')
  require(w['prewrite_preload_validation'] is not None and w['prewrite_preload_validation']['actual_original_preload_active'] is True,'actual original prewrite preload')
 if require_new_pi:require(c['new_policy_updates']>0 and c['new_world_updates']>=640 and c['completed_fresh_controls']>=64,'sourcePi is not new flat progress')
 return True

def verify_saved_migration(full,expected):
 w=expected['native88_migration_window'];verify_window(w)
 require(exact_plain(full['UniSuperMimic_changed_plant_migration'],w),'literal new window')
 require(exact_plain(full['UniSuperMimic_test_contract'],NATIVE_CONTRACT),'literal Fudan270 output contract')
 c=w['counters'];require(c['native_iteration']==expected['native_iteration'] and c['world_updates']==expected['world_updates'] and c['policy_updates']==expected['policy_updates'],'publication counters')
 p=expected['producer'];require(p['input_start_mode']==SOURCE_MODE and p['method']==METHOD and p['native_architecture_fresh'] is False,'complete101 continuation producer')
 require(exact_plain(p['fudan_step_task'],NATIVE_CONTRACT['fudan_step_task']) and exact_plain(p['task_focused_real_replay'],NATIVE_CONTRACT['task_focused_real_replay']) and p['native_learning_seed']==27,'new reward and replay task')
 require(exact_plain(p['initial_native_source'],w['source']) and p['bootstrap_Adam']==832460 and p['bootstrap_task_source_SHA']==SOURCE_PINS['producer']['bootstrap_task_source_SHA'],'native source separate from frozen RSL')
 require(p['reference_artifact_SHA']==REFERENCE_SHA and p['source_reference_artifact_SHA']==SOURCE_REFERENCE_SHA and p['plant_nominal400_unchanged'] is True,'new reference and preserved400 plant')
 require(p['gas400_parameter_source_contract_SHA']==w['parameter_source_contract_SHA'] and p['actual_gas400_asset_composition_report_SHA']==w['actual_asset_composition_report_SHA'],'producer actual recipe binding')
 require(p['private_phase_frame_source_SHA']==FLAT_OBJECTIVE_CONTRACT['private_phase_frame_source_SHA'] and p['real_callback_counter_source_SHA']==FLAT_OBJECTIVE_CONTRACT['real_callback_counter_source_SHA'],'exact request and original event source')
 require(full['spring_pressure_recipe']['nominal_stiffness_N_m']==2000 and full['spring_pressure_recipe']['actual_stiffness_bounds_N_m']==[1800,2200],'saved400 recipe')

class RequireNewWindowFinal:
 def __init__(self,publisher):self.publisher=publisher
 def __call__(self,*args,**kwargs):
  receipt=self.publisher(*args,**kwargs);verify_window(receipt['native88_migration_window'],require_new_pi=True);return receipt


def restore_same_architecture(learner,bridge,full,*,expected_source_contract,
                              expected_args,expected_progress,expected_reference_SHA,
                              expected_num_envs=4096):
    native,pub=validate_source(full,expected_source_contract,expected_args,
                              expected_progress,expected_reference_SHA)
    if not exact_plain(asdict(learner.cfg),expected_args):
        raise ValueError('new learner config differs before state mutation')
    if learner.env.num_envs!=expected_num_envs or learner.buffer.size!=0:
        raise ValueError('fresh target physical population/replay required')
    if learner.iteration!=0 or learner.sim_steps!=0 or bridge.wm_updates!=0 or bridge.pi_updates!=0:
        raise ValueError('do not restore over an already running learner')
    if tuple(learner.obs_hist.shape)!=(expected_num_envs,10,86) or tuple(bridge.ep_step.shape)!=(expected_num_envs,):
        raise ValueError('fresh target history/episode shape differs')
    # Do not copy source physical state, DR/RNG, replay, obs_history or ep_step.
    # load_state_dict includes registered normalization buffers.
    for name in ('wm','pi','critic'):
        getattr(learner,name).load_state_dict(native[name],strict=True)
    for name in ('opt_wm','opt_pi','opt_v'):
        getattr(learner,name).load_state_dict(deepcopy(native[name]))
    learner.iteration=native['iteration']
    learner.wall_time=native['wall_time']
    learner.sim_steps=native['sim_steps']
    bridge.wm_updates=pub['world_updates'];bridge.pi_updates=pub['policy_updates']
    return dict(passed=True,restored_iteration=learner.iteration,
        restored_world_updates=bridge.wm_updates,restored_policy_updates=bridge.pi_updates,
        all_three_modules_and_optimizers_restored=True,normalizers_inside_model_state_restored=True,
        source_observation_history_restored=False,source_environment_or_DR_RNG_or_replay_restored=False,
        fresh_environment_history_preserved=True,no_exact_PhysX_or_replay_resume=True,
        future_publisher_and_source_guard_contract_integration_required=True)


def verify_loaded_frozen_RSL_fresh_plant(runner,env,full):
 import torch
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
 return dict(frozen_RSL_actor9_critic8_STD6_17Adam832460_exact=True,fresh400N_environment=True,native_models_and_optimizers_will_restore_from_qualified88C=True,old700N_environment_DR_not_restored=True,not_same_physics_resume=True)


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
