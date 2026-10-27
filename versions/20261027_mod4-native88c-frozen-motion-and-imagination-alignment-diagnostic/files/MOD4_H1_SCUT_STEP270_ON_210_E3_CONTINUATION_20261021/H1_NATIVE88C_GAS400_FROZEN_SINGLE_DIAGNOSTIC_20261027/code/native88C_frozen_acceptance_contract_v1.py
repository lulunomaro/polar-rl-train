"""Typed qualified88C h1 single frozen attempt; metadata only, no model I/O."""
SEEDS=(20260928,)
SOURCE_SHA='0c1edb9603c1cb84fbb894d242dae1b6a7c87fe3237d658dbc486ccbbad3d394'
FINAL_SHA='a9bf6dca376e9d570ef0a6e2c15604f38656c4ebfedaa829a34830ee57c73aaf'
FINAL_BYTES=256227465
FINAL_PROGRESS=dict(updates=6469,world_updates=64690,policy_updates=6341)
REFERENCE_SHA='9223a53e7bf85a0dc3505cc46c0eb33d04fc35a9bf85e7ffe0e4fbd03e1e46c3'
GEOMETRY_SHA='461f6b44e6014c72a755a0db5136fa8d45bd5b53b6318ee4b38221a4c597bc4d'
CANONICAL='/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json'
GPU_BACKENDS={'GPU-c27eecbd-6838-7290-1cd2-37e34522213d':'target72','GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e':'source210'}
PURPOSE='MOD4_native88C_qualified_h1_nominal400_frozen_single_seed20260928'
SCOPE='fixed_h1_higher_updates_single_diagnostic_not_best_case_or_skill'
def require(v,message):
 if not v:raise ValueError(message)
def select_source(cpu,collection,full_text_events):
 require(cpu['passed'] is True and cpu['original_fees']['passed'] is True and cpu['original_canonical_cost_settled'] is True,'repaired formal88C whole CPU/original fees required')
 require(collection['actual_finite_transport_returned'] is True and collection['all_active_node_collection_passed'] is True and collection['original_canonical_cost_settled'] is True,'complete case-safe88C transport and fees')
 a=collection['authority72'];require(a['canonical_path']==CANONICAL and a['canonical_active_segment'] is None and a['all_authority72_owner_children_actual_out'] is True,'sole72 closed original authority')
 require(len(a['original_locks'])==2 and all(r['actual_fcntl_free'] for r in a['original_locks']),'original authority locks')
 for key in ('h1','recovery'):
  n=collection['nodes'][key];require(n['all_selected_target_processes_actual_out'] and n['node_exit']['actual_all_own_children_waited'] and n['node_exit']['validation_fcntl_released_if_acquired'] and all(r['actual_fcntl_free'] for r in n['locks']),'original own node/worker allout')
 model=cpu['models']['h1'];final=model['final'];require(model['passed'] and model['whole_native_fullstate_finite'] and model['new_NativeContract_exact'] and model['native_modules']['passed'] and model['frozen_bootstrap']['Adam']==832460,'newC native fullstate/frozen witness qualification')
 require(final['SHA']==FINAL_SHA and final['bytes']==FINAL_BYTES and all(final[k]==v for k,v in FINAL_PROGRESS.items()),'fixed higher-update h1 source')
 require(final['formal_manifest_passed'] and final['twohost_complete_SHA'] and collection['native_H1_method_fullstate']['h1']==[final],'formal transported source exact')
 loads=[r for r in cpu['initial_model_load_records'] if r['producer_SHA']==FINAL_SHA and r['initial_load_attempted'] and r['completed']]
 require(len(loads)==1,'newC formal initial whole CPU record')
 return dict(selected_key='h1',source=model,selection_scope=SCOPE,planned_seeds=list(SEEDS),episodes_per_seed=1,max_controls=500,max_physics_callbacks=2000,
  deterministic_native_mean=True,no_retry_no_seed_or_case_selection=True,original_events_diagnostic_only=full_text_events,not_frozen_skill_graduation=True)
def validate_eval_binding(q):
 require(q['purpose']==PURPOSE and q['selected_key']=='h1' and q['selection_scope']==SCOPE,'new declared fixed h1 purpose')
 require(q['seeds']==list(SEEDS) and q['episodes_per_seed']==1 and q['max_controls']==500 and q['max_physics_callbacks']==2000,'exact one fixed-seed fresh episode5s')
 require(q['source_run_id'].startswith('AVAILABLE_TWO_H1_GAS400_OWN_STEP_NATIVE88C_'),'qualified88C source, never old700')
 require(q['source_model']['SHA']==FINAL_SHA and q['source_model']['bytes']==FINAL_BYTES and all(q['source_model'][k]==v for k,v in FINAL_PROGRESS.items()),'fixed formal h1 model')
 require(all(q['source_qualification'][k] is True for k in ('formal_FINAL_passed','initial_whole_CPU_passed','original_fee_allout_passed')),'source qualification prerequisites')
 require(q['GPU_UUID'] in GPU_BACKENDS and q['execution_backend']==GPU_BACKENDS[q['GPU_UUID']],'fresh selected original c27 or937 only')
 require(q['action_mode']=='deterministic_native_mean_no_collection_noise' and q['new_N1_fresh_episode_no_training_environment_restore'] is True and q['runtime_is_new_readonly_copy'] is True,'frozen fresh N1, no restore/learning')
 require(q['reference_SHA']==REFERENCE_SHA and q['own_geometry_SHA']==GEOMETRY_SHA,'unchanged own reference/geometry')
 output=q['native_output_contract'];require(output['changed_plant700_to_nominal400'] is True and output['native_objective_changed'] is True and output['nominal_gas_stiffness_N_m']==2000. and output['original_physics_and_success_unchanged'] is False,'typed400N/native88 output recipe')
 require(q['objective_contract']['schema']=='mod4.native88.own_wheel_step_objective.source_candidate.v2' and q['objective_contract']['selected_candidate'] is True,'exact own-wheel V2 objective')
 require(q.get('optional_WM_forward_enabled') is False,'default single attempt never enables WM forward')
 return True
