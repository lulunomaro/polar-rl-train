"""Pin saved JSON/pure AST only, then one synthetic structural restore fixture."""
from pathlib import Path
from types import SimpleNamespace
from dataclasses import dataclass,asdict,make_dataclass
from copy import deepcopy
import ast,hashlib,importlib.util,json,pprint,sys,time,traceback
HERE=Path(__file__).resolve().parent;COURSE=HERE.parent;T=COURSE.parents[1]
PAYLOAD=T/'H1_STEP270_OWN_STEP_GAS400_NATIVE_RESOURCE_V88C_20261027/payloads/h1'
REPORTS=PAYLOAD.parents[1]/'reports'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def emit(name,v):
 with (HERE/name).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def extract(path,name,scope):
 tree=ast.parse(path.read_bytes());nodes=[n for n in tree.body if getattr(n,'name',None)==name or isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in n.targets)]
 assert len(nodes)==1;exec(compile(ast.Module(body=nodes,type_ignores=[]),str(path),'exec'),scope);return scope[name]
def main():
 pins_file=HERE/'native88C_flat_pins_v1.py';assert not pins_file.exists()
 cpu_path=REPORTS/'NATIVE88C_READER_REPAIRED_TYPED_FINALS_AND_ORIGINAL_COST_CPU_ACTUAL.json'
 close_path=REPORTS/'NATIVE88C_CASE_SAFE_COMPLETE_FINALS_AND_ORIGINAL_COST_RETURNED_V2_ACTUAL.json'
 cpu=json.loads(cpu_path.read_bytes());close=json.loads(close_path.read_bytes())
 acceptance=COURSE.parent/'native88C_frozen_single_attempt_source_preparation_v1/native88C_frozen_acceptance_contract_v1.py'
 sp=importlib.util.spec_from_file_location('saved88C_qualification_only',acceptance);a=importlib.util.module_from_spec(sp);sp.loader.exec_module(a)
 selected=a.select_source(cpu,close,{})['source'];final=selected['final']
 migration=PAYLOAD/'source/native88_gas400_migration_v1.py';restore=PAYLOAD/'source/same_architecture_native_continuation_candidate_v1.py'
 learner=PAYLOAD/'source/supermimic_wheel_leg_v3/learner.py';config=PAYLOAD/'source/native_own_fudan88_gas400_training_v2.py'
 cls=extract(learner,'SuperMimicConfig',dict(dataclass=dataclass));args=asdict(extract(config,'config_for',dict(SuperMimicConfig=cls))(27))
 contract=extract(migration,'NATIVE_CONTRACT',{})
 adapter_path=COURSE/'runtime_adapter_candidate_v1/FLAT5CM_NATIVE_ADAPTER_SOURCE_CPU_V2_ACTUAL.json'
 adapter=json.loads(adapter_path.read_bytes());assert adapter['passed'] and adapter['new_reference_SHA']=='b4d801a47b92a0d63378df0cea15e8c736fe489c2fd37a63399a1a2ed3d00502'
 objective=dict(schema='mod4.native88C_to_flat05.new_objective_source.v1',target='both real wheel bottoms>=.05 then actual floor landing stable>=.5s',
  source_MDP_contract=adapter['source_contract'],new_reference_SHA=adapter['new_reference_SHA'],stationary_horizontal_command=[0.,0.,0.],
  private_phase_frame_source_SHA='196063b60aa4fd956b97bd4db427aa44aa7a9ea0a8b060e68de57b849796be70',
  real_callback_counter_source_SHA='51db83fb9e75427bd0f28f7c5d7d2a31700fdb030eb672b002223d95068cbb8a',
  old_reference_is_source_provenance_only=True,not_measured_Fudan_joint_demo=True,source_only_actual_runtime_pending=True)
 pins=dict(final=final,native_contract=contract,native_args=args,producer=final['producer'],source_migration_window=final['native88_migration_window'],
  original_native_threeopt_CPU=selected['native_modules'],original_frozen_normal86_CPU=selected['frozen_bootstrap'],
  original_saved_D0_D7=selected['original_saved_D0_D7'],actual400_precontrol=selected['actual_physical_precontrol'],
  evidence=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p)) for p in (cpu_path,close_path,acceptance,migration,restore,learner,config,adapter_path)],
  model_path_size_SHA_are_cached_producer_metadata_only=True,no_model_stat_hash_or_load=True)
 newcontract=deepcopy(contract);newcontract.update(changed_plant700_to_nominal400=False,
  original_clock_solver_geometry_physical_V8_reward_command_success_unchanged=False,
  plant_nominal400_unchanged=True,native_objective_changed=True,native_flat05_objective=True,
  target_both_wheel_clearance_m=.05,actual_landing_stability_s=.5,stationary_horizontal_command=True,
  private_frame_encoding='(envID%250)*1024+original_public_age',original_public_age_and_selected_reset_unchanged=True,
  original_physics_clock_solver_and_true270_success_unchanged=True,
  reference_artifact_SHA=adapter['new_reference_SHA'],source_reference_artifact_SHA=a.REFERENCE_SHA)
 pins_file.write_text('"""Generated exact saved88C source pins; no PT I/O."""\nSOURCE_PINS='+pprint.pformat(pins,sort_dicts=False,width=120)+
  '\nNATIVE_CONTRACT='+pprint.pformat(newcontract,sort_dicts=False,width=120)+'\nFLAT_OBJECTIVE_SHA='+repr(adapter['new_reference_SHA'])+
  '\nFLAT_OBJECTIVE_CONTRACT='+pprint.pformat(objective,sort_dicts=False,width=120)+'\n',encoding='utf8')
 target=HERE/'native88C_to_flat_migration_v1.py';text=target.read_text('utf8');assert '\ndef restore_same_architecture(' not in text
 old=restore.read_text('utf8');tree=ast.parse(old);fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='restore_same_architecture')
 body=ast.get_source_segment(old,fn);text+='\n\n'+body+'\n'
 old_migration=migration.read_text('utf8');mt=ast.parse(old_migration)
 for name in ('verify_loaded_frozen_RSL_fresh_plant','observe_first_original_preload_write'):
  node=next(n for n in mt.body if isinstance(n,ast.FunctionDef) and n.name==name);part=ast.get_source_segment(old_migration,node)
  if name=='verify_loaded_frozen_RSL_fresh_plant':
   part=part.replace('\n from same_architecture','\n import torch\n from same_architecture',1).replace('native_models_and_optimizers_will_restore_from_own_R5=True','native_models_and_optimizers_will_restore_from_qualified88C=True')
  text+='\n\n'+part+'\n'
 target.write_text(text,encoding='utf8');newfn=next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name=='restore_same_architecture')
 assert ast.dump(fn,include_attributes=False)==ast.dump(newfn,include_attributes=False)
 emit('EXACT88C_SOURCE_PINNING_AND_RESTORE_AST_ACTUAL.json',dict(epoch=time.time(),passed=True,evidence=pins['evidence'],
  model_SHA=final['SHA'],source_counters={k:final[k] for k in ('updates','world_updates','policy_updates')},new_reference_SHA=adapter['new_reference_SHA'],
  old_restore_whole_function_AST_exact=True,changed_validator_only_exact88C_not_blanket_method=True,
  frozen_RSL_helper_only_local_torch_import_and_proof_key_rename=True,preload_observer_whole_function_reused=True,
  no_PT_normal86_Actor_SDK_GPU_remote_or_ledger_read=True,actual_restore_and_native_runtime_pending=True,
  original_reader_errors=[dict(tool_chunk='ad3dd6',error='Final filename filter found no non-PT files; rg exit1, no PT operation.'),
   dict(tool_chunk='54934a',error='Guessed train_h1_own87_native_v1.py absent; actual config source located via pinned CPU reader native_own_fudan88_gas400_training_v2.py.'),
   dict(tool_chunk='aab0e7',error='Optional guessed native_finalization_own87.py absent; actual finalizer own88_gas400 source read; no runtime operation.')]))
 sys.path.insert(0,str(HERE));sp=importlib.util.spec_from_file_location('typed88Cflat',target);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 native=dict(iteration=6469,wall_time=1.,sim_steps=4096,args=deepcopy(args),saved_at=1.)
 for name,prefixes in [('wm',('in_norm','out_norm')),('pi',('obs_norm','goal_norm')),('critic',('norm',))]:native[name]={p+'.'+field:0. for p in prefixes for field in ('mean','var','count')}
 for name,steps,count,betas in [('opt_wm',64690,14,(.9,.999)),('opt_pi',6341,20,(.9,.95)),('opt_v',126820,6,(.9,.999))]:native[name]=dict(state={i:dict(step=steps) for i in range(count)},param_groups=[dict(betas=betas)])
 full=dict(UniSuperMimic_test_contract=deepcopy(contract),UniSuperMimic_H1_test=native,
  UniSuperMimic_publication=dict(native_iteration=6469,world_updates=64690,policy_updates=6341,history_shape=[4096,10,86],episode_step_shape=[4096],producer=deepcopy(final['producer'])),
  UniSuperMimic_changed_plant_migration=deepcopy(final['native88_migration_window']),
  actor_state_dict={**{'x'+str(i):0 for i in range(8)},'distribution.std_param':SimpleNamespace(shape=(6,))},critic_state_dict={str(i):0 for i in range(8)},
  optimizer_state_dict=dict(state={i:dict(step=832460) for i in range(17)}),
  spring_pressure_recipe=dict(nominal_stiffness_N_m=2000,actual_stiffness_bounds_N_m=[1800,2200]),physical_action_delay_state=dict(control_us=10000))
 Cfg=make_dataclass('SyntheticConfig',[(k,object) for k in args]);calls=[]
 class Module:
  def load_state_dict(self,value,strict=True):calls.append(('module',strict));self.value=deepcopy(value)
 class Optimizer:
  def load_state_dict(self,value):calls.append(('opt',));self.value=deepcopy(value)
 learner_fake=SimpleNamespace(cfg=Cfg(**args),env=SimpleNamespace(num_envs=4096),buffer=SimpleNamespace(size=0),iteration=0,sim_steps=0,obs_hist=SimpleNamespace(shape=(4096,10,86)),
  **{k:Module() for k in ('wm','pi','critic')},**{k:Optimizer() for k in ('opt_wm','opt_pi','opt_v')})
 bridge=SimpleNamespace(wm_updates=0,pi_updates=0,ep_step=SimpleNamespace(shape=(4096,)))
 negatives={}
 for label,change in [('R5_fresh_method_rejected',lambda x:x['UniSuperMimic_publication']['producer'].update(method='MOD4_own_Fudan_native_v3',native_architecture_fresh=True)),
  ('arbitrary_method_rejected',lambda x:x['UniSuperMimic_publication']['producer'].update(method='any_method')),
  ('old700_recipe_rejected',lambda x:x['spring_pressure_recipe'].update(nominal_stiffness_N_m=3500)),
  ('wrong_counter_rejected',lambda x:x['UniSuperMimic_publication'].update(policy_updates=6342))]:
  bad=deepcopy(full);change(bad)
  try:m.restore_native88C_to_flat(learner_fake,bridge,bad,source_SHA=m.SOURCE_SHA)
  except ValueError as e:negatives[label]=str(e)
  else:raise AssertionError(label)
  assert not calls and learner_fake.iteration==0 and bridge.wm_updates==0
 proof=m.restore_native88C_to_flat(learner_fake,bridge,full,source_SHA=m.SOURCE_SHA)
 assert len(calls)==6 and learner_fake.iteration==6469 and bridge.wm_updates==64690 and bridge.pi_updates==6341
 trace=SimpleNamespace(total=0);window=m.FlatObjectiveWindow(learner_fake,bridge,trace);window.parameter_contract_SHA=final['producer']['gas400_parameter_source_contract_SHA'];window.asset_report_SHA='SYNTHETIC'+'0'*55
 assert not window.allow_policy_update(6469)
 learner_fake.iteration+=64;trace.total=64;learner_fake.sim_steps+=64*4096
 for _ in range(640):bridge.wm_updates+=1;window.completed_world_update()
 try:window.before_policy_update()
 except ValueError:pass
 else:raise AssertionError('preload proof bypass')
 window.preload_evidence=dict(actual_original_preload_active=True,synthetic_only=True);window.before_policy_update();bridge.pi_updates+=1;window.completed_policy_update()
 assert m.verify_window(window.snapshot(),require_new_pi=True)
 emit('TYPED88C_FLAT_RESTORE_STRUCTURAL_CPU_ACTUAL_V1.json',dict(epoch=time.time(),passed=True,source_SHA=H(target),pins_SHA=H(pins_file),
  synthetic_only_no_actual_module_optimizer_or_model_constructed=True,negative_rejections=negatives,
  exactly3_module_strict_loads_and3_opt_restores=True,normalization_state_dicts_carried_not_reset=True,
  old_positive_sourcePi_cannot_bypass_new64_640_and_preload=True,
  restored_progress=[6469,64690,6341],new_objective_reference_SHA=adapter['new_reference_SHA'],original_RSL_832460_distinct=True,
  no_PT_normal86_Actor_SDK_GPU_remote_or_ledger_read=True,actual_runtime_restore_pending=True))
 print(json.dumps(dict(passed=True,module_SHA=H(target),pins_SHA=H(pins_file),structural_CPU_only=True,new_reference_SHA=adapter['new_reference_SHA'])))
if __name__=='__main__':
 try:main()
 except BaseException:emit('SOURCE_PREPARATION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(traceback=traceback.format_exc(),no_PT_or_native_execution=True));raise
