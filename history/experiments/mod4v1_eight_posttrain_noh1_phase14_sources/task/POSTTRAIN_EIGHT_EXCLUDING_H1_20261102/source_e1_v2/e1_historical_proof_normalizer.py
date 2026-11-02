"""Localpurestdlib JSON-metadata normalizer/data-drivenroleplan producer.
Neveropens/stats/hashesmodel/PT/trajectory/SDK/GPU/canonical; noGO/Task/Ready.
Actualhistoricalflagsarederivedfromspecificcollectedfields,notfilenames/mock.
"""
from pathlib import Path
import copy,hashlib,json
HERE=Path(__file__).resolve().parent
V1=HERE.parent/'source_e1'
CLONE_MAP=V1/'PARENT_RUNTIME_CLONE_MAP_V1.json'
USD='2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3'
CONTRACT='bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755'
ROLES=('CURB_PROTECTED878','CURB_INDEPENDENT113','SLOPE135','SLOPE_INDEPENDENT50')
COMPLETE='gpu1/out/E1_NATIVE24_192PHYSICS_48FEEDBACK_NOUPDATE_COMPLETE.json'
HELPER_TRUE_FIELDS={
'SENSOR_RESUME_STARTUP_VERIFIED.json':('actor_critic_std_exact','optimizer_loaded_original_path','sensor_streams_restored','global_CPU_CUDA_streams_restored','all_episode_counters_incremented_once'),
'DELAY_RESUME_STARTUP_VERIFIED.json':('predecessor_had_delay_state','delay_state_and_RNG_exactly_restored_before_reset','full_sensor_optimizer_global_named_streams_verified','delay_episode_incremented_once'),
'ACTION_DELAY_RESUME_STARTUP_VERIFIED.json':('predecessor_had_action_queue','action_queue_targets_timestamps_both_RNG_restored_exact','action_episode_incremented_once','complete_D3_sensor_feedback_optimizer_global_named_streams_verified'),
'SPRING_PRESSURE_RESUME_STARTUP_VERIFIED.json':('predecessor_had_spring_pressure_state','spring_factor_episode_two_CUDA_RNG_restored_exact','actual_CUDA_spring_state_disk_roundtrip_exact','spring_episode_incremented_once','complete_D1_D4_optimizer_global_named_streams_verified'),
'GAS_DAMPING_RESUME_STARTUP_VERIFIED.json':('predecessor_had_gas_damping_state','gas_factor_episode_two_CUDA_RNG_restored_exact','actual_CUDA_gas_state_disk_roundtrip_exact','gas_episode_incremented_once','complete_D1_D5_optimizer_global_named_streams_verified'),
'CHASSIS_PD_RESUME_STARTUP_VERIFIED.json':('predecessor_had_chassis_PD_state','COM_PD_factors_episodes_six_CUDA_RNG_restored_exact','actual_CUDA_chassis_PD_disk_roundtrip_exact','COM_PD_episode_incremented_once','complete_D1_D6_optimizer_global_named_streams_verified'),
'E1_TERRAIN_RESUME_STARTUP_VERIFIED.json':('terrain_state_restored_exact','old_terrain_bookkeeping_restored_before_new_episode','actual_CUDA_terrain_bookkeeping_disk_roundtrip_exact','complete_D1_D7_optimizer_global_named_streams_verified','E1_episode_incremented_once','saved_source_episode_plus_one_verified'),
'E1_COMMAND_RETENTION_STARTUP_VERIFIED.json':('predecessor_command_state_restored_exact','actual_CUDA_command_state_and_private_rng_disk_roundtrip_exact','old_full_D1_D7_optimizer_global_named_streams_verified','E1_episode_incremented_once','one_new_physical_episode')}


def read_json_metadata(ref):
    p=Path(ref['path']);assert p.suffix.lower()=='.json','OnlycollectedJSONmetadataaccepted,neverPT/rawtrajectory'
    raw=p.read_bytes();actual=dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest())
    if 'SHA'in ref:assert actual['SHA']==ref['SHA'],str(p)
    if 'bytes'in ref:assert actual['bytes']==ref['bytes'],str(p)
    return json.loads(raw),actual


def select_handoff(role,raw):
    if role=='SLOPE135':
        assert raw['kind']=='SLOPE135_CANONICAL_ACTUAL_CPU_TYPED_FRESH_NATIVE24_PASS_CURB141_NETWORK_PENDING'
        h=raw['SLOPE135']
        return h,dict(selector=['SLOPE135'],typed_source='typed_source',one_reset='ONE_original_reset',core_exact='core_before_after_exact',exit='original_closewaitrelease',helper_refs='fullhelper_receipts',actual_status=h['status']=='ACTUAL_PROTOCOL_PASS_NOT_LONG_SKILL')
    assert raw['kind']=='EXPLICIT_FROZEN_VARIANT_ACTUAL_CPU_FRESH_NATIVE24_PROTOCOL_PASS_NOT_SKILL' and raw['variant']==role
    return raw,dict(selector=[],typed_source='new_typed_source',one_reset='ONEoriginalreset',core_exact='STD17Adam_LR_iteration_beforeafter_exact',exit='closewait_originalEX_finiteSH_release',helper_refs='complete9_original_and_extra_helper_receipts',actual_status=True)


def normalize_historical_objects(role,clone_row,handoff_raw,collection,*,raw_refs):
    assert role in ROLES and clone_row['role']==role
    pin=clone_row['source_pin'];h,adapter=select_handoff(role,handoff_raw);files=collection['files'];terms=files['TERMINAL_ROWS.json'];children=files['CHILDREN.json'];closure=files['PARENT_EXIT_SCOPE.json'];a=files[COMPLETE];before=files['gpu1/out/E1_FULLRESTORE_BEFORE_NATIVE24.json'];guard=a['nominal_guard'];cache=files['gpu1/out/E1_SOURCE_FINAL_READ_COUNTS.json'];core_before=files['gpu1/out/E1_CORE_BEFORE.json']['core'];core_after=files['gpu1/out/E1_CORE_AFTER.json'];leaves={r['path']:r for r in core_before['leaves']};counter=a['actual_source_counters'];meta=h['actual_source_metadata'];typed=h[adapter['typed_source']]
    checks={}
    checks['collection_actual_kind']=collection['kind']=='OWN_E1_ACTUAL_RAW_JSON_LOG_COLLECTION_NOT_EXTRA_MODEL_READ'
    checks['role_and_exact_native_root']=collection['canonical']==role and collection['remote_root']==clone_row['remote_original_native_runtime_clone_root']==h['native_root']
    checks['historical_n20k_dispatch']=files['PARENT_STARTED.json']['mode']=='n20k' and files['SDK_DISPATCH_ONCE.json']['mode']=='n20k' and files['SDK_DISPATCH_ONCE.json']['no_production_GO'] is True
    checks['handoff_actual_status']=adapter['actual_status']
    checks['source_pin_exact']=a['canonical']==role and a['source_SHA']==cache['source_SHA']==typed['SHA']==pin['SHA'] and typed['path']==cache['source_path']==pin['path'] and typed['bytes']==cache['source_bytes']==pin['bytes']
    checks['saved_actual_counters']=counter['iteration']==pin['iteration']==meta['original_iteration'] and counter['LR']==pin['LR']==meta['original_LR'] and counter['Adam_steps']==[pin['Adam17']] and meta['original_17Adam_step']==pin['Adam17'] and counter['STD6']==meta['original_STD6']
    checks['terminal_and_worker_passed']=bool(terms) and all(x['passed']is True and x['actual_complete']['passed']is True and x['actual_complete']['source_SHA']==pin['SHA'] and x['returncode']==0 and x['error_json_exists']is False for x in terms) and a['passed']is True and before['passed']is True and files['FINAL.json']['passed']is True
    all_waited=closure['all_own_children_waited']is True and len(terms)==len(children) and {x['pid']for x in terms}=={x['pid']for x in children} and all(x['actual_waited']is True for x in terms)
    checks['actual_children_waited']=all_waited
    checks['original_lease_close_and_noerrors']=all(closure[k]is True for k in ('original_private_lock_released','original_shared_lock_released','all_partialleases_released','no_foreign_scope_touched')) and closure['errors']==[] and closure['canonical_access']is False and h[adapter['exit']]['all_own_children_waited']is True and h[adapter['exit']]['errors']==[]
    checks['num_envs20000']=a['num_envs']==guard['num_envs']==20000
    checks['assets_exact']=guard['usd_sha256']==USD and guard['contract_sha256']==CONTRACT
    checks['new_nominals_preserved']=guard['new_constructor_nominal_caches_preserved']is True and guard['fresh_D0_mass_inertia_based_on_new_asset']is True
    checks['original_ONE_reset']=a['one_original_fresh_reset']==guard['original_fresh_reset_calls']==h[adapter['one_reset']]==1
    checks['guard_interface_and_observation_checked']=guard['expected_interface']==dict(actor_obs=35,critic_obs=38,actions=6) and guard['observation_shapes_checked']is True
    checks['actual_live_tensor_shapes']=leaves['/actor/mlp.0.weight']['shape']==[256,35] and leaves['/critic/mlp.0.weight']['shape']==[256,38] and leaves['/actor/distribution.std_param']['shape']==[6]
    checks['actual_live_actor_critic_counts']=sum(x['path'].startswith('/actor/')for x in core_before['leaves'])==9 and sum(x['path'].startswith('/critic/')for x in core_before['leaves'])==8 and meta['actor_tensor_count']==9 and meta['critic_tensor_count']==8
    checks['whole_live_core_before_after_exact']=a['core_before_after_exact']is True and core_after['core_before_after_exact']is True and h[adapter['core_exact']]is True and core_before['tree_SHA']==core_after['core']['tree_SHA']
    checks['native24_clocks']=a['controls']==24 and a['physics_callbacks']==192 and a['feedback_samples']==48 and len(a['per_control'])==24 and all(r['control']==i and r['physics_tick']==i*8 and r['feedback_tick']==i*2 and r['command_dt_s']==.02 for i,r in enumerate(a['per_control'],1))
    checks['actual_fullDR_before_after']=a['actual_mild_DR_audit_before']['actual_parameters_pass']is True and a['actual_mild_DR_audit_after']['actual_parameters_pass']is True
    checks['no_optimizer_or_learn_or_PPO']=a['forbidden_calls']==dict(alg_update=0,optimizer_step=0,runner_learn=0) and a['productionGO_or_PPO']is False and a['canonical_access']is False
    checks['whole_source_once_immutable_nonsliced']=cache['selected_source_physical_byte_reads']==cache['selected_source_SHA_calculations']==cache['selected_source_decodes']==1 and cache['selected_typed_complete_pytree_unmodified']is True and cache['no_slicing_or_history_timestamp_rescaling']is True
    for filename,fields in HELPER_TRUE_FIELDS.items():
        r=files['gpu1/out/'+filename]
        checks['helper/'+filename]=r['source_sha256']==pin['SHA'] and all(r[k]is True for k in fields) and r['PhysX_exact_resume_claimed']is False
    if role!='SLOPE135':
        extra=files['gpu1/out/VARIANT_EXTRA_FULLSTATE_RESUME_STARTUP_VERIFIED.json'];owned=files['gpu1/out/VARIANT_FIRST_BEFORE_CONTROL.json']
        checks['variant_full_extra_before_lower_reset']=extra['variant']==role and extra['source_SHA']==pin['SHA'] and extra['all_complete_saved_extras_exact']is True and extra['extra_reset_physics_RNG_calls']==0 and owned['all_actual_root_nested_owners_mapped']is True and owned['original_knownstate_and_namedRNG_applied_by_original_helpers']is True and owned['unknown_root_or_nested_preserve_only_fields']==[]
    failed=[name for name,passed in checks.items()if not passed]
    return dict(kind='NORMALIZED_HISTORICAL_E1_WHOLE20K_RESTORE_REFERENCE_V1',role=role,historical_reference_not_newtrainingpass=True,actual_not_mock=checks['collection_actual_kind'] and checks['historical_n20k_dispatch'] and checks['role_and_exact_native_root'],source_SHA=a['source_SHA'],source_pin=copy.deepcopy(pin),asset_USD_SHA=guard['usd_sha256'],asset_contract_SHA=guard['contract_sha256'],num_envs=a['num_envs'],whole_state_restore_passed=not failed,all_own_children_waited=all_waited,actual_returncodes=[r['returncode']for r in terms],one_original_helper_reset=guard['original_fresh_reset_calls'],live_interface=guard['expected_interface'],observation_shapes_checked=guard['observation_shapes_checked'],actual_core=copy.deepcopy(counter),rawpath=raw_refs['collection']['path'],rawSHA=raw_refs['collection']['SHA'],rawbytes=raw_refs['collection']['bytes'],handoff_raw_ref=raw_refs['handoff'],collection_raw_ref=raw_refs['collection'],handoff_schema_exact=adapter,checks=checks,failed_checks=failed,new_SDK_or_training_or_skill_pass=False,PhysX_exact_resume_claimed=False,independent_backend_or_full_hardware_DR_qualification=False,skill_graduated=False,skill_metric_scope='S50_ACCEPTED_FULLRAMP_METRIC_GAP_NOT_RESTORE_PROTOCOL_FAILURE'if role=='SLOPE_INDEPENDENT50'else'ORIGINAL_OWN_TASK_SCOPE_ONLY_NOT_WHOLE_E1_GRADUATION',local_operation='JSON_METADATA_READ_AND_NORMALIZE_ONLY_NOT_NATIVE_REPLAY',model_PT_stat_read_hash_decode_SDK_GPU_SSH_C_GO_Git=0)


def load_role_inputs(role,clone_map_path=CLONE_MAP):
    assert role in ROLES
    clone_map,clone_ref=read_json_metadata(dict(path=str(clone_map_path)));row=next(r for r in clone_map['rows']if r['role']==role)
    template,template_ref=read_json_metadata(row['fixed_source_descriptor']);handoff,handoff_ref=read_json_metadata(row['local_original_full20k_actual_proof']);collection,collection_ref=read_json_metadata(row['local_native_actual_collection']);pin=row['source_pin']
    assert template['canonical']==role and template['selected_typed_source_path']==template['model_path']==pin['path'] and template['source_SHA']==pin['SHA'] and template['source_bytes']==pin['bytes'] and template['source_iteration']==pin['iteration'] and template['source_Adam_step']==template['source_Adam17']==pin['Adam17'] and template['source_LR']==pin['LR'] and template['original_source_SHA']==pin['original_source_SHA']
    return row,template,handoff,collection,dict(clone_map=clone_ref,template=template_ref,handoff=handoff_ref,collection=collection_ref)


def build_role_spec(role,jobroot,runid,*,clone_map_path=CLONE_MAP):
    """Localmetadata-onlyroleplan; noactualTask/admission/Ready/GOissuance.
    Keepcompletenestedtask_fields; parentoldmake_taskmustinjectrealparentfields.
    Noe0/e2/e3globalstringreplace; native0pt_evidence_fileiskeyandneverrenamed.
    """
    row,template,handoff,collection,refs=load_role_inputs(role,clone_map_path)
    normalized=normalize_historical_objects(role,row,handoff,collection,raw_refs=refs)
    immutable=[]
    for name in row['metadata_to_retain']:
        r=dict(relative=name)
        ref=row['local_CPU_fulltyped_proof'] if name=='CPU_FOUR_LEAF_ACTUAL_COMPLETE.json' else dict(path=str(Path(row['local_complete_runtime_source_root'])/name))
        # OnlyknownJSONmetadata paths; norecursivefilesystem/modeldiscovery.
        if Path(ref['path']).is_file():
            _,actual=read_json_metadata(ref);r.update(bytes=actual['bytes'],SHA=actual['SHA'],local_metadata_path=actual['path'])
        else:r['local_SHA_status']='NOT_LOCALLY_AVAILABLE_USE_ORIGINAL_NATIVE_NONPT_METADATA_UNCHANGED'
        immutable.append(r)
    return dict(kind='E1_DATA_DRIVEN_ROLE_PLAN_SOURCE_ONLY_NOT_ACTUAL_TASK',role=role,source_family='e1',source_pin=copy.deepcopy(row['source_pin']),base_root=row['remote_original_native_runtime_clone_root'],job_root=str(jobroot),source_SHA=row['source_pin']['SHA'],source_model_metadata=copy.deepcopy(row['source_pin']),num_envs=20000,max_additional_updates=20,manifest_file='INSTALL_E1_POSTTRAIN_NONPT.json',native0pt_evidence_file='evidence/NEW_ASSET_NATIVE_ACTUAL.json',task_template=copy.deepcopy(template),historical_raw_proof=refs['collection'],historical_handoff_raw_proof=refs['handoff'],normalized_proof=copy.deepcopy(normalized),runtime_source_paths=[str(V1/'runtime_bundle'/name)for name in ('worker_e1_posttrain_full20k_original_ppo_v1.py','e1_posttrain_contract.py','e1_posttrain_state_tools.py')],required_immutable_metadata=copy.deepcopy(row['metadata_to_retain']),required_immutable_files=immutable,planned_jobroot=str(jobroot),planned_run_id=str(runid),source=copy.deepcopy(row['source_pin']),task_fields=copy.deepcopy(template),source_template_ref=refs['template'],historical_proof=normalized,proof_raw_refs=[refs['handoff'],refs['collection']],complete_original_proof_bytes_preserved=True,payload_source_inputs=[dict(local_path=refs['handoff']['path'],payload_relative='evidence/'+role+'_HISTORICAL_HANDOFF_RAW.json',bytes=refs['handoff']['bytes'],SHA=refs['handoff']['SHA']),dict(local_path=refs['collection']['path'],payload_relative='evidence/'+role+'_HISTORICAL_COLLECTED_RAW.json',bytes=refs['collection']['bytes'],SHA=refs['collection']['SHA'])],original_native_runtime_root=row['remote_original_native_runtime_clone_root'],original_native_source_nonPT_manifest=row['remote_original_native_nonPT_manifest'],entry=row['entry'],restore_helper=row['restore_helper'],original_metadata_to_retain=copy.deepcopy(row['metadata_to_retain']),train_num_envs=20000,capacity_scope='ORIGINAL_N20K_CFG_NO_N80_PRESET',common_evidence_field_names_unchanged=['native0pt_evidence_file','native0pt_evidence_SHA'],common_native0pt_evidence_value='PARENT_SUPPLIES_ONE_COMMON_NEW_ASSET_NATIVE_ACTUAL_REFERENCE_UNCHANGED_FOR_ALL_ROLES',parent_actual_task_assembler='source_e1/e1_posttrain_make_task.py:make_task',real_parent_fields_still_required=True,actualTask_Ready_GO_or_budget_created=False,source_pin_mutated=False,historical_reference_not_newtrainingpass=True)
