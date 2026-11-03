"""Freeze only this NEW V4 SOURCE package; later verification is read-only."""
from pathlib import Path
import json
import good_holdout_contract as C
import source_pins as P

HERE=Path(__file__).resolve().parent
MEMBERS=('good_holdout_contract.py','good_holdout_parent_actual_wait_controller_v1.py','good_holdout_remote_reader.py',
 'collect_good_holdout_result.py','source_pins.py','test_v4_d6_metadata_source.py','seal_source.py','README.md',
 'SOURCE_PINS.json','SOURCE_TEST_LOG.txt','SOURCE_TEST_REPORT.json','SOURCE_RECEIPT.json')
EXPECTED_TESTS=7


def report_check(report):
    C.need(report.get('kind')=='GOOD_HOLDOUT_LIFECYCLE_ROUTES_V4_D6_TYPED_METADATA_SOURCE_TESTS'and report.get('scope')=='NEW_V4_SEVEN_MEMORY_AST_PINS_SOURCE_ONLY_NOT_PRIOR40_11_8_OR_D6_UPSTREAM8'and report.get('passed')is True and type(report.get('tests'))is int and report['tests']==EXPECTED_TESTS and report.get('final_suite_declared')==EXPECTED_TESTS and report.get('excluded_test_names')==[] and all(report.get(k)==0 for k in ('failures','errors','skipped')),'complete NEW V4 seven SOURCE tests required')
    C.need(report.get('audit')==dict(native_imports=0,model_raw_report_budget_lock_accesses=0,process_network_signals_or_locks=0,forbidden_source_entry_calls=0),'V4 SOURCE audit not zero')
    C.need(report.get('old_test_modules_replayed')is False and report.get('actual_prepare_preflight_stage_main_guard_runtime_controller_reader_collector_SDK_Torch_model_reports_C_Git')is False and report.get('actual_native_binding')=='UNKNOWN'and report.get('actual_quality')is None and report.get('stage2_GO')is False,'V4 SOURCE report scope differs')
    log=(HERE/'SOURCE_TEST_LOG.txt').read_bytes();C.need(report.get('SOURCE_test_log')==dict(bytes=len(log),SHA256=C.H(log)),'actual on-disk V4 test log differs')


def receipt():
    C.need(not(HERE/'SOURCE_RECEIPT.json').exists(),'NEW V4 receipt already exists')
    inventory=P.verify_sources();report=json.loads((HERE/'SOURCE_TEST_REPORT.json').read_bytes());report_check(report)
    history=[dict(suite='NEW_V4_seven',tests=7,failures=1,errors=0,seconds=1.758,receipt_written=False,cause='NEW_test_whitelist_omitted_published_SOURCE_DERIVATION_VERSION_5_to_6',production_source_changed=False),
        dict(suite='NEW_V4_seven',tests=7,failures=1,errors=0,seconds=1.690,receipt_written=False,cause='NEW_test_function_counter_included_two_complete_ClassDef_nodes',production_source_changed=False),
        dict(suite='NEW_V4_seven',tests=7,failures=0,errors=0,seconds=2.009,receipt_written=False)]
    value=dict(kind='GOOD_HOLDOUT_LIFECYCLE_ROUTES_SOURCE_RECEIPT_V4',status='SOURCE_READY_FOR_PARENT_REVIEW_NOT_NATIVE_ADMISSION',tests=report,SOURCE_test_history=history,
        authoring_history_SOURCE_only=dict(pre_creation_author_guard_failures=2,reason='temporary_author_guard_restricted_SOURCE_to_R_instead_of_exact_two_named_SOURCE_trees',NEW_package_created_on_failed_author_attempts=False,large_shell_source_generator_blocked_before_execution=True,tool_rule='analysis.dynamic-shell-source',explicit_literal_SOURCE_write_used_after_block=True,approval_or_scope_escalation=False),
        prior_V1_author40_V2_author11_V3_author8_preserved_not_rerun=True,D6_upstream8_not_rerun=True,
        independent_validation_history_parent_reported_not_opened_or_executed_here=[dict(validator='independent_V1',passed=39,failed=1),dict(validator='independent_V2',passed=40,failed=0)],
        actual_before_stage_failures_parent_reported_preserved=['unflattened_logical_mirror_vs_original_flat20','D3_Windows_published_plan_wire_pin_vs_actual_wire','D4_selected_E1_inner_vs_ROOT_canonical_metadata','D5_full_teacher9_vs_guard_projection4_runtime147_equality'],
        old_RC127_diagnostic_preserved_as_unread_SOURCE_declaration=True,
        prior_routes12_seals={key:value['seal']for key,value in inventory['prior_routes12_seals'].items()},prior_materializer_seals={key:value['seal']for key,value in inventory['prior_materializer_seals'].items()},
        source_inventory=dict(active_NEW_component20=20,active_index=inventory['good_index'],historical_original_index=inventory['historical_original_index'],original_good14_members=14,D6_final_members=8,teacher_component_members=5,
            old_D2_members=9,D3_members=10,D4_members=10,D5_members=8,V1_routes_members=12,V2_routes_members=12,V3_routes_members=12,
            external_declared=145,previous127_fields_unchanged=True,new18_full_SOURCE=15,new18_report_declarations=3,external_full_allowed_SOURCE=136,report_declarations_only=9,
            logical_mirror_with_D6_package=154,logical154_does_not_replace_flat20=True,actual_report_stat_or_read=False,all145_full_bytes_read=False,groups_are_not_disjoint_sum=True),
        final_D6_materializer_source_pins=C.STAGER_SOURCE_PINS,teacher_component_seal=inventory['component5_seal'],active_component20=inventory['active_component20'],active_component_provenance=inventory['D6_active_component'],
        raw_provenance=inventory['D6_raw_provenance'],SOURCE_capture_provenance=inventory['D6_SOURCE_capture_provenance'],audit_only_prior_last4=inventory['D6_mirror']['audit_only_prior_last4'],
        parent_physical_once_counts_not_local_counts=True,parent_diagnostic_pass_not_local_native_pass=True,
        controller_reader_collector_whole_file_bytes_equal_V3=True,complete_contract_functions_AST_equal_except_existing_typed6_literal_and_label=True,contract_assignments_changed_only=['STAGE_KIND','STAGER_SOURCE_PINS','INDEX_PIN','RUNTIME_PIN','OVERLAY_PINS'],
        D6_remaining28_full_function_AST_and_source_unchanged=True,D6_three_whitelist_function_deltas_only_deepcopy_raw9_and_SOURCE_labels_checked_without_execution=True,
        component_runtime30_functions_and_two_complete_classes_unchanged=True,component_runtime_whole_text_changed_only_existing_guard_tuple=True,component_guard_other6_full_functions_unchanged=True,complete_new_guard_function_AST_checked_strict9_plus_original_fourkey_identity=True,
        raw9_synthetic_memory_contract_not_actual_guard_or_runtime147_execution=True,old_runtime_whole_bytes_unchanged=False,other18_overlay_rows_fieldwise_unchanged=True,
        target_source_mappings_whole_original_function_unchanged=True,flat_memory_test_normalizes_entry_path_basename_and_whole_bytes=True,target_F_provenance_paths_not_dereferenced_by_memory_test=True,actual_target_source_mappings_executed=False,
        original_parent_pin=C.PARENT_PIN,new_component_runtime_pin=C.RUNTIME_PIN,new_component_index_pin=C.INDEX_PIN,own_controller_pin=C.CONTROLLER_SOURCE_PIN,
        wire_filename_unchanged=C.STAGE_NAME,stage_receipt_kind=C.STAGE_KIND,source_derivation_version=6,
        original_grade_errors_close_binding_whole_FINAL_hash_singlecache_and_double_wait_EX_semantics_preserved=True,new_wire_fields_prefixes_approval_quality_gates=False,
        original_native_resource_ready_worker_wait_seconds=[1800,900,2400],collector_poll_seconds=20,collector_cap_seconds=6000,
        full_current20_private_finite_EX_C_readonly_preserved=True,selected_E1_runtime_trees=2,eight_role_catalog_only=True,deferred_roles=list(C.DEFERRED),H1_included=False,
        D6_packager_executed=False,foreign_rederive_or_reseal=False,
        actual_SSH=False,actual_prepare_preflight_stage_main=False,actual_guard_runtime_controller_reader_or_collector=False,actual_SDK_Torch_GPU_native=False,actual_parent_or_worker_wait=False,
        actual_model_raw_reports_C_locks_signals_Git=False,actual_B2_import_or_execute=False,actual_native_binding='UNKNOWN',actual_quality=None,phase1_Gate1='UNKNOWN',phase1_exact_contract=False,phase1_interface=False,stage2_GO=False)
    with(HERE/'SOURCE_RECEIPT.json').open('x',encoding='utf-8')as stream:json.dump(value,stream,indent=2,allow_nan=False)
    return value


def freeze_or_verify():
    P.verify_sources();report=json.loads((HERE/'SOURCE_TEST_REPORT.json').read_bytes());report_check(report)
    source_receipt=json.loads((HERE/'SOURCE_RECEIPT.json').read_bytes())
    C.need(source_receipt.get('kind')=='GOOD_HOLDOUT_LIFECYCLE_ROUTES_SOURCE_RECEIPT_V4'and source_receipt.get('tests')==report and source_receipt.get('actual_native_binding')=='UNKNOWN'and source_receipt.get('stage2_GO')is False,'V4 receipt scope differs')
    rows=[]
    for name in MEMBERS:
        item,_=P.checked_source(HERE/name);rows.append(dict(name=name,bytes=item['bytes'],SHA256=item['SHA256']))
    root=P.member_root(rows)
    value=dict(kind='SOURCE_ONLY_GOOD_HOLDOUT_LIFECYCLE_ROUTES_IMMUTABLE_SEAL_V4',status='SOURCE_READY_FOR_PARENT_REVIEW_NOT_NATIVE',root_algorithm='SHA256(sorted name TAB bytes TAB SHA256 LF records UTF8)',root_SHA256=root,files=rows,enabled=False,staged=False,dispatched=False,
        previous_routes_V1_V2_V3_12_each_unchanged=True,D6_final8_and_teacher_component5_unchanged=True,old_D5_8_D4_10_D3_10_original_good14_D2_9_unchanged=True,
        D6_external_mirror_full_SOURCE=136,unread_report_declarations=9,new18_split=[15,3],active_component_index_pin=list(C.INDEX_PIN),actual_reports_read=False,controller_reader_collector_bytes_equal_V3=True,
        actual_native_binding='UNKNOWN',actual_wait_proof=False,actual_quality=None,stage2_GO=False)
    path=HERE/'SOURCE_SEAL.json'
    if path.exists():
        C.need(json.loads(path.read_bytes())==value,'immutable complete V4 SOURCE package or seal metadata differs');return value,True
    with path.open('x',encoding='utf-8')as stream:json.dump(value,stream,indent=2,allow_nan=False)
    return value,False


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--receipt',action='store_true');args=parser.parse_args()
    if args.receipt:receipt()
    value,read_only=freeze_or_verify();blob=(HERE/'SOURCE_SEAL.json').read_bytes()
    print(json.dumps(dict(read_only_verify=read_only,members=len(value['files']),root_SHA256=value['root_SHA256'],seal_bytes=len(blob),seal_SHA256=C.H(blob),SOURCE_only=True)))
