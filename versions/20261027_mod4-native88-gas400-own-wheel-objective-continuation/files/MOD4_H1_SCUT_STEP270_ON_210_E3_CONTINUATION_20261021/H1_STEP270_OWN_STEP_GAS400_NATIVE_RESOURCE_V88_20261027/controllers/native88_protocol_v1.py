"""Native R5 full-model transfer to nominal400 + own-step objective. Metadata only."""
from pathlib import Path
import hashlib,json,re
KIND='MOD4_H1_NATIVE88_GAS400_CHANGED_PLANT_NATIVE_SOURCE_CPU_V1'
CANONICAL='/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json'
AUTHORITY_GENERATION='MOD4_SINGLE_WRITER72_20261026'
BOOTSTRAP_SHA='0c1edb9603c1cb84fbb894d242dae1b6a7c87fe3237d658dbc486ccbbad3d394'
BOOTSTRAP_ADAM=832460
SOURCES={
 'h1':dict(SHA='ae5ff91877bcfdda72b864a181fdbbbd0c78401cb34591ca507adda44a6632e9',updates=3317,world_updates=33170,policy_updates=3253,seed=27,GPU_UUID='GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e',execution_backend='source210'),
 'recovery':dict(SHA='870e63b6ef41f870109fc1c3b6d9d67fe2f472ca8436145755db5d74a7b8e404',updates=1409,world_updates=14090,policy_updates=1345,seed=29,GPU_UUID='GPU-c27eecbd-6838-7290-1cd2-37e34522213d',execution_backend='target72')}
REFERENCE_SHA='9223a53e7bf85a0dc3505cc46c0eb33d04fc35a9bf85e7ffe0e4fbd03e1e46c3'
METHOD=dict(num_envs=4096,episode_timeout_s=5.,control_dt_s=.01,physics_dt_s=.0025,solver='TGS',solver_position_iterations=32,solver_velocity_iterations=4,decimation=4,packed_state_dim=127,aux_dim=54,static_xi_dim=31,obs_dim=86,goal_dim=146,goal_frames=10,hist=10,wm_hidden=[2048,2048,2048],policy_hidden=[2048,1024,512,256],horizon=32,buffer_steps=1000,utd=.4,wm_batch=1024,pi_batch=1024,wm_only_iters=64,amp='none',compile=False)
PIN_FIELDS=('manifest_SHA','native88_contract_SHA','qualified_R5_pair_report_SHA','previous_R5_closure_SHA','reference_artifact_SHA','gas400_parameter_source_contract_SHA','actual_gas400_asset_composition_report_SHA','own_step_objective_qualification_SHA','objective_contract_SHA')
READY_FLAGS=('role_control_dependency_metadata_closure_checked','actual_installed_source_SDK_CPU_passed','actual_ordered30_encoder_SDK_source_passed','actual_SDK_tensor_ingress_CPU_passed','whole_native_R5_fullstate_finite_CPU_passed','all_native_modules_norms_threeoptimizers_strict_restore_CPU_passed','frozen_normal86_RSL832460_wholepolicy_roundtrip_CPU_passed','source_R5_original_fee_allout_qualified','native700N_environment_DR_not_restored','fresh400N4096_factory_source_passed','actual_USD_four_attribute_composition_source_passed','independent_own_step_objective_source_CPU_passed','manifest_exact_python_protected_runtime_passed','original_physical_V8_clock_control_success_save_retained','actual_fresh_GPU_before_first_control_still_required')
def require(value,message):
 if not value:raise ValueError(message)
def digest(value):return hashlib.sha256(json.dumps(value,indent=2).encode()).hexdigest()
def sha(value):return isinstance(value,str) and re.fullmatch('[0-9a-f]{64}',value) is not None
def validate_spec(s):
 require(s.get('key') in SOURCES,'only two authorized available H1 slots')
 old=SOURCES[s['key']]
 require(s.get('native88_changed_plant') is True and s.get('finite_method_test') is True,'typed finite88 scope')
 require(s.get('native87_policy_only') is False and s.get('new_native_architecture_fresh') is False and s.get('closed_production_continuation') is False,'not fresh87 or normalPPO')
 require(s.get('native_continuation') is True and s.get('native_continuation_restore_required') is True,'all native state restore required')
 require(s.get('source_SHA')==old['SHA'] and s.get('source_progress')=={k:old[k] for k in ('updates','world_updates','policy_updates')},'exact own formal R5 source/progress')
 require(s.get('bootstrap_source_SHA')==BOOTSTRAP_SHA and s.get('source_Adamstep')==BOOTSTRAP_ADAM,'separate immutable RSL witness')
 require(s.get('seed')==s.get('native_seed')==old['seed'] and s.get('GPU_UUID')==old['GPU_UUID'] and s.get('execution_backend')==old['execution_backend'],'actual role/seed/backend/UUID')
 require(s.get('method_config')==METHOD and s.get('policy_hz')==100,'original native dimensions/clock/config')
 require(s.get('max_parent_seconds')==3900 and s.get('exit_headroom_seconds')==300 and s.get('owner_authority_generation')==AUTHORITY_GENERATION,'original finite authority/caps')
 require(s.get('fresh_environment_resume_scope')=='native_models_only_fresh400N_environment_no_old_DR' and s.get('changed_plant700_to_nominal400') is True,'changed plant / fresh physical scope')
 require(s.get('independent_own_step_objective_admission_passed') is True,'corrected objective independently qualified')
 for key in PIN_FIELDS:require(sha(s.get(key)),key+' pin required')
 require(s['reference_artifact_SHA']==REFERENCE_SHA,'preserved own converted Fudan reference')
 require(isinstance(s.get('candidate_pins'),dict) and s['candidate_pins'] and all(sha(v) for v in s['candidate_pins'].values()),'complete exact source allowlist')
 if s['key']=='h1':require(sha(s.get('owner_control_dependency_binding_SHA')),'strict210→72 dependency binding')
 return True
def validate_schedule(cfg):
 require(set(cfg['experts'])==set(SOURCES) and cfg['deferred_experts']==['e2'],'two slots / preserve unknown16828')
 require(cfg['scheduling_authority']=='human_requested_available_experts' and cfg['authority_generation']==AUTHORITY_GENERATION,'sole72 authority')
 for key,spec in cfg['experts'].items():require(spec['key']==key and validate_spec(spec),'per-role source binding')
 require(cfg['last_closed_remaining_snapshot']==569553.363275528,'R5 actual closed balance source')
 require(sha(cfg['resource_boundary_SHA']),'fresh available-resource receipt')
 require(cfg['resource_boundary_relative']=='NATIVE88_SELECTED_RESOURCE_BOUNDARY_ACTUAL.json','exact new source resource receipt basename')
 path=Path(__file__).resolve().parent/cfg['resource_boundary_relative'];raw=path.read_bytes()
 require(hashlib.sha256(raw).hexdigest()==cfg['resource_boundary_SHA'],'resource boundary actual byteSHA')
 value=json.loads(raw);require(value['actual_finite_returned'] is True and value['canonical_None'] is True and value['original_owner_locks_free'] is True and value['no_account_write'] is True,'actual completed source/resource read')
 require(value['closed_remaining_snapshot']==569553.363275528 and value['unknown16828_identity_not_queried'] is True,'latest source and peer boundary')
 require(set(value['selected_resources'])==set(SOURCES),'only requested two GPU resources')
 for key,row in value['selected_resources'].items():
  require(row['GPU_UUID']==SOURCES[key]['GPU_UUID'] and row['selected_compute_application_count']==0 and row['free_MiB']>15669 and row['available_RAM_bytes']>32*1024**3 and row['free_payload_disk_bytes']>25*1024**3 and row['original_private_shared_locks_free'],'actual selected resource floors')
 require(value['selected_resources']['h1']['actual_durable_UUID']=='EF3105C85DD986BD' and value['selected_resources']['h1']['actual_durable_rw'] is True,'restored expanded source mount identity/rw')
 return True
def native88_valid_ready(row,spec):
 try:
  validate_spec(spec);e=row.get('closed_source_CPU') or {};v=e.get('value') or {}
  require(row.get('key')==spec['key'] and row.get('phase')=='ready' and row.get('manifest_SHA')==spec['manifest_SHA'] and not row.get('original_error'),'ready identity/phase')
  require(e.get('actual_CPU_waited_EXIT0') is True and e.get('SHA')==digest(v) and v.get('passed') is True and v.get('kind')==KIND,'actual waited new installed CPU envelope')
  require(v.get('source_SHA')==spec['source_SHA'] and v.get('source_progress')==spec['source_progress'] and v.get('bootstrap_SHA')==BOOTSTRAP_SHA and v.get('bootstrap_Adam')==BOOTSTRAP_ADAM,'native source distinct from bootstrap')
  require(v.get('seed')==spec['seed'] and v.get('GPU_UUID')==spec['GPU_UUID'] and v.get('execution_backend')==spec['execution_backend'] and v.get('method_config')==METHOD,'role/seed/source config')
  require(v.get('native_continuation_restore_required') is True and v.get('native_environment_state_from_source') is False and v.get('actual_GPU_runtime_readback_passed') is False and v.get('actual_environment_count') is None and v.get('configured_environment_count')==4096,'CPU not actual new GPU scene')
  require(v.get('candidate_pins')==spec['candidate_pins'] and all(v.get(k)==spec[k] for k in PIN_FIELDS),'all current source evidence pins')
  role=v.get('role_control_dependency_CPU') or {}
  require(role.get('checked') is True,'control dependency source proof')
  if spec['key']=='h1':
   require(role.get('actual_installed_dependencies_verified') is True and role.get('scope')=='source210_h1_exact_installed_dependency_SHA_and_import' and role.get('binding_SHA')==spec['owner_control_dependency_binding_SHA'],'H1 actual dependency closure')
  else:require(role.get('scope')=='target72_original_loopback_not_required' and role.get('actual_installed_dependencies_verified') is False,'72 loopback scope')
  return all(v.get(k) is True for k in READY_FLAGS)
 except (ValueError,KeyError,TypeError):return False
def validate_task_go(task,go,manifest_SHA):
 old=SOURCES.get(task.get('key'));require(old is not None,'own source role')
 require(go['source_SHA']==task['source_SHA']==old['SHA'] and go['source_progress']==task['source_progress']=={k:old[k] for k in ('updates','world_updates','policy_updates')},'native Task/GO source')
 require(go['bootstrap_SHA']==task['bootstrap_source_SHA']==BOOTSTRAP_SHA and go['bootstrap_Adam']==task['source_Adamstep']==BOOTSTRAP_ADAM,'RSL bootstrap separate')
 require(go['source_qualification_kind']==KIND and go['manifest_SHA']==manifest_SHA and go['seed']==task['native_seed']==old['seed'],'actual native CPU grant binding')
 require(go['native88_changed_plant'] is True and go['changed_plant700_to_nominal400'] is True and go['native_continuation_restore_required'] is True and go['new_native_architecture_fresh'] is False,'changed plant full native scope')
 require(go['max_parent_seconds']==3900 and go['exit_headroom_seconds']==300 and go['nominal_end_epoch']-go['save_deadline']==300,'unchanged deadlines')
 for key in ('native88_contract_SHA','gas400_parameter_source_contract_SHA','actual_gas400_asset_composition_report_SHA','own_step_objective_qualification_SHA','objective_contract_SHA'):require(task[key]==go[key] and sha(task[key]),'Task/GO '+key)
 require(task['independent_own_step_objective_admission_passed'] is True and go['independent_own_step_objective_admission_passed'] is True,'effective own-step objective source gate')
 return True

def native88_go_fields(spec):
 validate_spec(spec)
 return dict(native88_changed_plant=True,changed_plant700_to_nominal400=True,native_continuation_restore_required=True,new_native_architecture_fresh=False,
  source_progress=spec['source_progress'],bootstrap_SHA=spec['bootstrap_source_SHA'],bootstrap_Adam=spec['source_Adamstep'],seed=spec['seed'],num_envs=4096,
  actual_H1_step270_scope_admitted=True,source_native_iteration=spec['source_progress']['updates'],window_start_world_updates=spec['source_progress']['world_updates'],window_start_policy_updates=spec['source_progress']['policy_updates'],
  independent_own_step_objective_admission_passed=True,**{key:spec[key] for key in ('manifest_SHA','native88_contract_SHA','gas400_parameter_source_contract_SHA','actual_gas400_asset_composition_report_SHA','own_step_objective_qualification_SHA','objective_contract_SHA')})
