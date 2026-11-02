"""Audit actualsamecache JSONschema against originalexecuted source owners.
NO PT/stat/hash/decode, no Torch/SSH/GPU. Ownership != physicalapplication.
"""
from pathlib import Path
import ast,hashlib,json,time,traceback
B=Path(__file__).resolve().parent;T=B.parent
CH={'base_ang_vel','projected_gravity','leg_pos','leg_vel','wheel_vel'}
MAIN={
 'sensor_DR_state':set('version n profile bias episode bias_rng noise_rng cache draw_counts'.split()),
 'feedback_delay_state':set('version n enabled delay episode rng cache'.split()),
 'physical_action_delay_state':set('version n enabled physics_us control_us rng groups'.split()),
 'spring_pressure_state':set('version n enabled rng_device_type factor episode rng scope'.split()),
 'gas_damping_state':set('version n enabled rng_device_type factor episode rng scope physical_parameter'.split()),
 'chassis_PD_state':set('version rng_device_type COM PD'.split()),
 'sensor_global_rng_state':{'cpu','cuda'},
 'sensor_command_DR_rng_state':{'_mode_rng'},
 'sensor_physical_DR_rng_state':{'generator','cpu_generator'},
 'E1_retained_flat_command_state':set('version profile num_envs rng_device_type rng assignment_sha256 no_position_correction no_mask_actor_or_gate_input eligible_flat linear moving direction signed_yaw linear_vx family sample_histogram control_histogram _command_heading phase_elapsed BODY_command'.split())}

def H(b):return hashlib.sha256(b).hexdigest()
def main():
 summaries=[]
 for name in ['CURB_PROTECTED878','CURB_INDEPENDENT113','SLOPE_INDEPENDENT50']:
  package=T/'staged_sources'/('E1_'+name+'_40050_MOD4V1_SOURCE_V2');rt=package/'runtime/isaac/mod4';j=json.loads((B/(name+'_CPU_COMPLETE_ROOT_AND_NESTED_SCHEMA_OWNER_AUDIT.json')).read_bytes());cpu=json.loads((B/(name+'_CPU_FOUR_LEAF_ACTUAL_COMPLETE.json')).read_bytes());owner=json.loads((package/'SAVED_EVIDENCE_ROOTKEY_HELPER_OWNER_MAP_V1.json').read_bytes());schema=j['complete_nested_schema'];mapping={r['path']:r for r in schema};curb=name.startswith('CURB');helper='curb20_entry_full_checkpoint.py' if curb else 'slope5_full_checkpoint.py'
  FILES={
  'sensor_DR_state':['sensor_mild_math.py','sensor_resume_contract.py','sensor_a0_runtime.py'],
  'sensor_recipe':['sensor_mild_math.py','sensor_a0_runtime.py'],
  'sensor_global_rng_state':['sensor_resume_contract.py','sensor_a0_runtime.py'],
  'sensor_command_DR_rng_state':['sensor_resume_contract.py','sensor_a0_runtime.py','directional_spin_runtime.py'],
  'sensor_physical_DR_rng_state':['sensor_resume_contract.py','sensor_a0_runtime.py','mild_dr.py'],
  'feedback_delay_state':['feedback_delay_mild.py','feedback_delay_checkpoint.py'],
  'feedback_delay_recipe':['feedback_delay_runtime.py','feedback_delay_checkpoint.py'],
  'physical_action_delay_state':['action_delay_physics_queue.py','action_delay_checkpoint.py'],
  'physical_action_delay_recipe':['action_delay_physics_queue.py','action_delay_sdk_adapter.py','action_delay_training_env.py','action_delay_checkpoint.py'],
  'spring_pressure_state':['spring_pressure_component.py','spring_pressure_index_runtime.py','spring_pressure_checkpoint.py'],
  'spring_pressure_recipe':['spring_pressure_training_env.py','spring_pressure_checkpoint.py'],
  'gas_damping_state':['spring_pressure_component.py','gas_damping_factor.py','gas_damping_sdk_adapter.py','gas_damping_checkpoint.py'],
  'gas_damping_recipe':['gas_damping_training_env.py','gas_damping_checkpoint.py'],
  'chassis_PD_state':['chassis_pd_checkpoint.py','chassis_com_component.py','chassis_com_pose_roundtrip_sdk_adapter.py','explicit_pd_component.py','explicit_pd_sdk_adapter.py'],
  'chassis_PD_recipe':['chassis_pd_training_env.py','chassis_pd_checkpoint.py'],
  'E1_retained_flat_command_state':['retention_flat_runtime.py','retention_flat_runtime_named_owned.py','retention_command_state.py','directional_spin_runtime.py',helper],
  'E1_terrain_state':(['curb20_entry_current_state.py','curb20_current_state.py','e1_terrain_state.py','curb20_entry_v3_runtime.py','curb20_entry_v3_full_pose_reset.py',helper] if curb else ['slope5_current_state.py','e1_terrain_state.py','slope5_retention_runtime.py',helper]),
  'E1_CURB_entry_reset_identity':['curb20_entry_current_state.py','curb20_current_state.py','e1_terrain_state.py',helper],
  'distributed_rank_contract':['variant_extra_state_runtime_v2.py','e1_variant_fullstate_checkpoint.py'],
  'independent_expert_scope_state':['variant_extra_state_runtime_v2.py','independent_expert_axis_v1.py','e1_variant_fullstate_checkpoint.py'],
  'independent_expert_task_contract':['variant_extra_state_runtime_v2.py','e1_variant_fullstate_checkpoint.py']}
  # Resolve only namedsourcefiles; no guessedmodel paths or runtimeimports.
  source={};tokens={};defs={};missing=[]
  for rootkey,filenames in FILES.items():
   if rootkey not in cpu['actual_source_metadata']['original_topkeys']:continue
   actual=[];tok=set();ds=[]
   for filename in filenames:
    p=rt/filename
    try:raw=p.read_bytes()
    except FileNotFoundError:missing.append(dict(rootkey=rootkey,path=str(p)));continue
    tree=ast.parse(raw);actual.append(dict(relative='runtime/isaac/mod4/'+filename,SHA=H(raw)))
    for n in ast.walk(tree):
     if isinstance(n,ast.Constant) and isinstance(n.value,str):tok.add(n.value)
     elif isinstance(n,ast.keyword) and n.arg:tok.add(n.arg)
     if isinstance(n,ast.FunctionDef) and any(w in n.name for w in ('load','restore','state_dict','apply','reset','current_state','identity','audit')):ds.append(dict(file=filename,function=n.name,line=n.lineno))
   source[rootkey]=actual;tokens[rootkey]=tok;defs[rootkey]=ds
  unknown=[];dicts=[];leafowners=[]
  actionfields=set('lag_steps episode pending pending_valid issued_tick due_tick applied applied_valid applied_issue_tick first_apply_tick last_submit_tick last_apply_tick'.split())
  for r in schema:
   path=r['path'];parts=path.strip('/').split('/') if path else [];rootkey=parts[0] if parts else ''
   if not path:continue
   if r['kind']=='dict':
    actual=set(r['keys']);expected=None;kind='SOURCE_STATIC_METADATA_FIELDS'
    if path.count('/')==1 and rootkey in MAIN:expected=MAIN[rootkey];kind='EXACT_ACTIVE_ROOTSTATE_SCHEMA'
    elif path in ('/sensor_DR_state/noise_rng','/sensor_DR_state/cache','/sensor_DR_state/draw_counts','/feedback_delay_state/cache','/sensor_recipe/raw_pre_scale_uniform_bounds','/sensor_recipe/raw_units','/sensor_recipe/noise_draw_counts'):expected=CH;kind='SOURCE_CHANNEL_SCHEMA'
    elif path.startswith('/feedback_delay_state/cache/') and path.count('/')==3:expected={'last','cur','out','sample_tick','ready'};kind='SOURCE_FEEDBACK_CACHE_FIELDS'
    elif path in ('/physical_action_delay_state/rng','/physical_action_delay_state/groups'):expected={'legs','wheels'};kind='SOURCE_ACTION_GROUP_SCHEMA'
    elif path.startswith('/physical_action_delay_state/groups/') and path.count('/')==3:expected=actionfields;kind='EXACT_ACTION_QUEUE_HISTORY_FIELDS'
    elif path=='/chassis_PD_state/COM':expected=set('version profile enabled num_envs delta_m episode private_xyz_RNG'.split());kind='EXACT_COM_STATE_SCHEMA'
    elif path=='/chassis_PD_state/PD':expected=set('version profile num_envs enabled factor episode private_group_RNG'.split());kind='EXACT_EXPLICIT_PD_STATE_SCHEMA'
    elif path in ('/chassis_PD_state/PD/factor','/chassis_PD_state/PD/private_group_RNG'):expected={'leg_kp','leg_kd','wheel_kd'};kind='EXACT_PD_GROUP_SCHEMA'
    elif rootkey=='actor_state_dict':expected=set(['distribution.std_param']+[f'mlp.{i}.{p}' for i in (0,2,4,6) for p in ('weight','bias')]);kind='ORIGINAL_RSL35_ACTOR_SCHEMA'
    elif rootkey=='critic_state_dict':expected=set([f'mlp.{i}.{p}' for i in (0,2,4,6) for p in ('weight','bias')]);kind='ORIGINAL_RSL38_CRITIC_SCHEMA'
    elif path=='/optimizer_state_dict':expected={'state','param_groups'};kind='ORIGINAL_RSL_ADAM_SCHEMA'
    elif path=='/optimizer_state_dict/state':expected={str(i) for i in range(17)};kind='EXACT17PARAMETER_ADAM_SCHEMA'
    elif path.startswith('/optimizer_state_dict/state/'):expected={'step','exp_avg','exp_avg_sq'};kind='EXACT_ADAM_MOMENT_STEP_SCHEMA'
    elif path.startswith('/optimizer_state_dict/param_groups/'):kind='ORIGINAL_OPTIMIZER_GROUP_LITERAL_LOAD_AND_INVERSE_EXACT';expected=actual
    elif rootkey=='distributed_rank_contract':expected=set('world_size rank task per_rank_envs global_envs source_SHA explicit_source_stream_fork_after_strict_restore'.split());kind='HISTORICAL_RANK0_WORLD3_METADATA_ONLY_NOT_FORK'
    elif rootkey=='independent_expert_scope_state':expected=set('centers target origin kind original_private_RNG_draws_unchanged'.split())|({'reset_direction'} if name=='CURB_INDEPENDENT113' else set());kind='OWN_SAVED_AXIS_FIELDS_SOURCE_APPLY_PENDING'
    elif rootkey=='independent_expert_task_contract':kind='HISTORICAL_TASK_METADATA_ONLY_NOT_GPU_BINDING';expected=actual
    if expected is not None:extra=sorted(actual-expected);absent=sorted(expected-actual)
    else:
     tok=tokens.get(rootkey,set());extra=sorted(actual-tok);absent=[]
    if extra or absent:unknown.append(dict(path=path,type=r['type'],actual_only_fields=extra,source_expected_missing=absent,producer_references=source.get(rootkey,[]),status='UNMAPPED_OR_SCHEMA_GAP_PHYSICAL_APPLICATION_NOT_CLAIMED'))
    dicts.append(dict(path=path,audit_kind=kind,actual_fields=sorted(actual),extra_fields=extra,missing_fields=absent,producer_references=source.get(rootkey,[]),owner_functions=defs.get(rootkey,[])))
   elif r['kind']=='tensor':
    if rootkey not in owner['rootkey_owner_map']:unknown.append(dict(path=path,type=r['type'],reason='Unmappedtensorroot'))
    leafowners.append(dict(path=path,dtype=r['dtype'],shape=r['shape'],root_owner=owner['rootkey_owner_map'].get(rootkey),load_setter_refs=source.get(rootkey,[]),physical_application='NOT_EXECUTED_CPU_ONLY_PASSTHROUGH_NOT_APPLY',RNG_byte_preserve_only_CPU=bool(r['dtype']=='torch.uint8')))
  # Missing sourcefiles are precise evidence gaps, not automaticowner absence.
  report=dict(kind='ACTUAL_SAMECACHE_FULL_NESTED_SCHEMA_VS_SOURCE_OWNER_AUDIT_NO_SDK',variant=name,actual_source_SHA=cpu['original_source']['SHA'],typed_source=cpu['new_typed_source'],actual_rootkey_diff=j['actual_rootkey_diff'],actual_rootkey_count=len(cpu['actual_source_metadata']['original_topkeys']),all_actual_rootkeys_mapped=not j['actual_rootkey_diff']['actual_only'] and not j['actual_rootkey_diff']['source_derived_only'],dict_schema_audits=dicts,tensor_leaf_loadowner_audits=leafowners,unmapped_active_or_schema_fields=unknown,missing_source_reference_files=missing,all_actual_tensor_leaves_have_root_owner=len(leafowners)==cpu['actual_source_metadata']['tensor_leaf_count'],fullroot_inventory_old_saved_gap_now_resolved_from_oneCPUcache=True,source_original_seals_unmodified=True,physical_application_fullrestore_or_hardware_pass=False,future_GPU_still_requires_independent_parent_permission=True,PT_or_SSH_SDK_GPU_operations_in_thisaudit=0)
  out=B/(name+'_ACTUAL_FULL_NESTED_OWNER_AUDIT_V1.json')
  with out.open('x',encoding='utf-8') as f:json.dump(report,f,indent=2)
  summaries.append(dict(variant=name,actual_rootkeys=report['actual_rootkey_count'],tensor_leaves=len(leafowners),dict_nodes=len(dicts),unmapped=unknown,missing_refs=missing));print(json.dumps(summaries[-1],indent=2))
 with (B/'THREE_ACTUAL_ROOT_NESTED_OWNER_AUDIT_SUMMARY_V1.json').open('x',encoding='utf-8') as f:json.dump(dict(kind='ACTUAL_CPU_SCHEMA_OWNER_AUDIT_THREE_VARIANTS',rows=summaries,no_physical_apply_claim=True),f,indent=2)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (B/('NESTED_OWNER_AUDIT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf-8') as f:json.dump(dict(error=traceback.format_exc(),PT_SDK_operations=0),f,indent=2)
  raise
