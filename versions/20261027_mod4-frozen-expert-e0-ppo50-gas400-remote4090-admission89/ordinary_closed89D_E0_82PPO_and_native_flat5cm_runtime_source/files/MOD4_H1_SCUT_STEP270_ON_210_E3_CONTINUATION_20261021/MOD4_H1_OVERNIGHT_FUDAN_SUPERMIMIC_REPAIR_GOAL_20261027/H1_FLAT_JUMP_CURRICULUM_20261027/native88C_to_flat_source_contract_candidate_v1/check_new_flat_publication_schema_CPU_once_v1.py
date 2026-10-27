"""New output schema only; no source restore fixture/model/Actor/SDK is rerun."""
from pathlib import Path
from copy import deepcopy
import hashlib,json,time,traceback
import native88C_to_flat_migration_v1 as m
HERE=Path(__file__).resolve().parent
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=HERE/'NEW_FLAT_PUBLICATION_SCHEMA_CPU_ACTUAL_V1.json';assert not p.exists()
 c=dict(native_iteration=6533,window_iteration=64,world_updates=65330,policy_updates=6342,new_world_updates=640,new_policy_updates=1,completed_fresh_controls=64,window_start_sim_steps=4096)
 w=dict(schema='mod4.native88C_to_flat05.objective_window.v1',role='h1',source=deepcopy(m.SOURCES['h1']),reference_SHA=m.REFERENCE_SHA,
  source_reference_SHA=m.SOURCE_REFERENCE_SHA,new_objective=True,plant_nominal400_unchanged=True,changed_plant700_to_nominal400=False,
  parameter_source_contract_SHA=m.SOURCE_PINS['producer']['gas400_parameter_source_contract_SHA'],actual_asset_composition_report_SHA='SYNTHETIC'+'0'*55,
  adaptation=dict(fresh_warmup_controls=64,new_window_world_only_iterations=64,minimum_new_world_steps_before_newPi=640),counters=c,
  first_new_policy_update=dict(window_iteration=64,completed_fresh_controls=64,new_world_updates=640,new_policy_updates=1),
  prewrite_preload_validation=dict(actual_original_preload_active=True,synthetic_only=True),not_same_physics=True)
 producer=dict(method=m.METHOD,native_architecture_fresh=False,initial_native_source=deepcopy(m.SOURCES['h1']),bootstrap_Adam=832460,
  bootstrap_task_source_SHA=m.SOURCE_PINS['producer']['bootstrap_task_source_SHA'],reference_artifact_SHA=m.REFERENCE_SHA,
  source_reference_artifact_SHA=m.SOURCE_REFERENCE_SHA,plant_nominal400_unchanged=True,
  gas400_parameter_source_contract_SHA=w['parameter_source_contract_SHA'],actual_gas400_asset_composition_report_SHA=w['actual_asset_composition_report_SHA'],
  private_phase_frame_source_SHA=m.FLAT_OBJECTIVE_CONTRACT['private_phase_frame_source_SHA'],real_callback_counter_source_SHA=m.FLAT_OBJECTIVE_CONTRACT['real_callback_counter_source_SHA'])
 expected=dict(native88_migration_window=w,native_iteration=c['native_iteration'],world_updates=c['world_updates'],policy_updates=c['policy_updates'],producer=producer)
 full=dict(UniSuperMimic_changed_plant_migration=w,UniSuperMimic_test_contract=deepcopy(m.NATIVE_CONTRACT),spring_pressure_recipe=dict(nominal_stiffness_N_m=2000,actual_stiffness_bounds_N_m=[1800,2200]))
 m.verify_saved_migration(full,expected);negative={}
 for name,change in [('old9223_not_new_flat_reference',lambda x:x['producer'].update(reference_artifact_SHA=m.SOURCE_REFERENCE_SHA)),
  ('old88_method_not_flat_producer',lambda x:x['producer'].update(method='MOD4_own_Fudan_native88_nominal400_changed_plant')),
  ('plant700_to400_claim_not_accepted',lambda x:x['native88_migration_window'].update(changed_plant700_to_nominal400=True))]:
  bad=deepcopy(expected);change(bad)
  try:m.verify_saved_migration(full,bad)
  except ValueError as e:negative[name]=str(e)
  else:raise AssertionError(name)
 with p.open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),passed=True,new_schema_positive=True,negative_rejections=negative,
  exact_expected_producer_interface=producer,legacy_memory_fields_are_compatibility_only=True,
  no_old_restore_fixture_rerun_no_PT_Actor_torch_SDK_GPU_remote_or_ledger=True,actual_publication_and_runtime_pending=True,
  module_SHA=H(HERE/'native88C_to_flat_migration_v1.py')),f,indent=2)
 print(json.dumps(dict(passed=True,report_SHA=H(p),schema_only=True)))
if __name__=='__main__':
 try:main()
 except BaseException:(HERE/('PUBLICATION_SCHEMA_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(traceback=traceback.format_exc()),indent=2),encoding='utf8');raise
