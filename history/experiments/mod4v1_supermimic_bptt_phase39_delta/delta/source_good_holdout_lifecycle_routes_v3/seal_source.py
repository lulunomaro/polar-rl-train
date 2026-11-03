"""Freeze only this NEW V3 SOURCE package; subsequent verification is read-only."""
from pathlib import Path
import json
import good_holdout_contract as C
import source_pins as P

HERE=Path(__file__).resolve().parent
MEMBERS=('good_holdout_contract.py','good_holdout_parent_actual_wait_controller_v1.py','good_holdout_remote_reader.py',
 'collect_good_holdout_result.py','source_pins.py','test_v3_d5_metadata_source.py','seal_source.py','README.md',
 'SOURCE_PINS.json','SOURCE_TEST_LOG.txt','SOURCE_TEST_REPORT.json','SOURCE_RECEIPT.json')
EXPECTED_TESTS=8


def report_check(report):
    C.need(report.get('kind')=='GOOD_HOLDOUT_LIFECYCLE_ROUTES_V3_D5_TYPED_METADATA_SOURCE_TESTS'and report.get('scope')=='NEW_V3_EIGHT_D5_INPUT_METADATA_AST_ONLY_NOT_PRIOR40_11_OR_UPSTREAM12'and report.get('passed')is True and type(report.get('tests'))is int and report['tests']==EXPECTED_TESTS and report.get('final_suite_declared')==EXPECTED_TESTS and report.get('excluded_test_names')==[] and all(report.get(k)==0 for k in ('failures','errors','skipped')),'complete NEW V3 eight SOURCE tests required, not prior40/11 or upstream12')
    C.need(report.get('audit')==dict(native_imports=0,model_raw_report_budget_lock_accesses=0,process_network_signals_or_locks=0,forbidden_source_entry_calls=0),'V3 SOURCE audit not zero')
    C.need(report.get('old_test_modules_replayed')is False and report.get('actual_prepare_preflight_stage_main_controller_collector_SDK_Torch_model_reports_C_Git')is False and report.get('actual_quality')is None and report.get('stage2_GO')is False,'V3 SOURCE report scope differs')
    log=(HERE/'SOURCE_TEST_LOG.txt').read_bytes()
    C.need(report.get('SOURCE_test_log')==dict(bytes=len(log),SHA256=C.H(log)),'actual on-disk V3 test log differs')


def receipt():
    C.need(not(HERE/'SOURCE_RECEIPT.json').exists(),'NEW V3 receipt already exists')
    inventory=P.verify_sources();report=json.loads((HERE/'SOURCE_TEST_REPORT.json').read_bytes());report_check(report)
    value=dict(kind='GOOD_HOLDOUT_LIFECYCLE_ROUTES_SOURCE_RECEIPT_V3',status='SOURCE_READY_FOR_PARENT_REVIEW_NOT_NATIVE_ADMISSION',tests=report,
        SOURCE_test_history=[dict(suite='NEW_V3_eight',tests=8,failures=0,errors=0,seconds=2.657,receipt_written=False)],
        prior_V1_author40_and_V2_author11_preserved_not_rerun=True,D5_upstream12_not_rerun=True,
        independent_validation_history_parent_reported_not_opened_or_executed_here=[dict(validator='independent_V1',passed=39,failed=1),dict(validator='independent_V2',passed=40,failed=0)],
        three_actual_before_stage_failures_parent_reported_preserved=['unflattened_logical_mirror_vs_original_flat20','D3_Windows_published_plan_wire_pin_vs_actual_wire','D4_selected_E1_inner_vs_ROOT_canonical_metadata'],
        prior_routes_12_seals={key:value['seal']for key,value in inventory['prior_routes_12_seals'].items()},
        prior_materializer_seals={key:value['seal']for key,value in inventory['prior_materializer_seals'].items()},
        source_inventory=dict(good20=20,good_original_seal_members=14,D5_final_seal_members=8,old_stage_D2_members=9,D3_members=10,D4_members=10,V1_routes_members=12,V2_routes_members=12,
            external_declared=127,previous92_fields_unchanged=True,new35_full_SOURCE=31,new35_report_declarations=4,external_full_allowed_SOURCE=121,report_declarations_only=6,
            logical_mirror_with_D5_package=136,logical136_does_not_replace_flat20=True,actual_report_stat_or_read=False,all127_full_bytes_read=False,groups_are_not_disjoint_sum=True),
        final_D5_materializer_source_pins=C.STAGER_SOURCE_PINS,raw_provenance=inventory['D5_raw_provenance'],SOURCE_capture_provenance=inventory['D5_SOURCE_capture_provenance'],audit_only_last4=inventory['D5_mirror']['audit_only_last4'],
        parent_physical_once_counts_not_local_counts=True,parent_diagnostic_pass_not_local_native_pass=True,
        controller_reader_collector_whole_file_bytes_equal_V2=True,complete_contract_function_AST_equal_except_existing_typed_version_literal_and_label=True,D5_other28_full_function_AST_and_source_unchanged=True,D5_three_whitelist_function_AST_deltas_checked_without_execution=True,
        original_parent_pin=C.PARENT_PIN,original_runtime_pin=C.RUNTIME_PIN,own_controller_pin=C.CONTROLLER_SOURCE_PIN,
        wire_filename_unchanged=C.STAGE_NAME,stage_receipt_kind=C.STAGE_KIND,source_derivation_version=5,
        original_grade_errors_close_binding_whole_FINAL_hash_cache_waits_preserved=True,new_wire_fields_prefixes_approval_quality_gates=False,
        original_native_resource_ready_worker_wait_seconds=[1800,900,2400],collector_poll_seconds=20,collector_cap_seconds=6000,
        original_full_good20_and_private_finite_EX_C_readonly_preserved=True,selected_E1_runtime_trees=2,eight_role_catalog_only=True,deferred_roles=list(C.DEFERRED),H1_included=False,
        actual_SSH=False,actual_prepare_preflight_stage_main=False,actual_controller_or_collector=False,actual_SDK_Torch_GPU_native=False,actual_parent_or_worker_wait=False,
        actual_model_raw_reports_C_locks_signals_Git=False,actual_B2_import_or_execute=False,actual_native_binding='UNKNOWN',actual_quality=None,phase1_Gate1='UNKNOWN',phase1_exact_contract=False,phase1_interface=False,stage2_GO=False)
    with(HERE/'SOURCE_RECEIPT.json').open('x',encoding='utf-8')as stream:json.dump(value,stream,indent=2,allow_nan=False)
    return value


def freeze_or_verify():
    P.verify_sources();rows=[]
    for name in MEMBERS:
        item,_=P.checked_source(HERE/name);rows.append(dict(name=name,bytes=item['bytes'],SHA256=item['SHA256']))
    root=P.member_root(rows);path=HERE/'SOURCE_SEAL.json'
    if path.exists():
        value=json.loads(path.read_bytes());C.need(value.get('files')==rows and value.get('root_SHA256')==root,'immutable V3 SOURCE package differs')
        return value,True
    report=json.loads((HERE/'SOURCE_TEST_REPORT.json').read_bytes());report_check(report)
    source_receipt=json.loads((HERE/'SOURCE_RECEIPT.json').read_bytes())
    C.need(source_receipt.get('kind')=='GOOD_HOLDOUT_LIFECYCLE_ROUTES_SOURCE_RECEIPT_V3'and source_receipt.get('tests')==report and source_receipt.get('actual_native_binding')=='UNKNOWN'and source_receipt.get('stage2_GO')is False,'V3 receipt scope differs')
    value=dict(kind='SOURCE_ONLY_GOOD_HOLDOUT_LIFECYCLE_ROUTES_IMMUTABLE_SEAL_V3',status='SOURCE_READY_FOR_PARENT_REVIEW_NOT_NATIVE',
        root_algorithm='SHA256(sorted name TAB bytes TAB SHA256 LF records UTF8)',root_SHA256=root,files=rows,enabled=False,staged=False,dispatched=False,
        previous_routes_V1_V2_12_each_unchanged=True,D5_final8_unchanged=True,previous_D4_10_D3_10_old_good14_D2_9_unchanged=True,
        D5_external_mirror_full_SOURCE=121,unread_report_declarations=6,new35_split=[31,4],actual_reports_read=False,controller_reader_collector_bytes_equal_V2=True,
        actual_native_binding='UNKNOWN',actual_wait_proof=False,actual_quality=None,stage2_GO=False)
    with path.open('x',encoding='utf-8')as stream:json.dump(value,stream,indent=2,allow_nan=False)
    return value,False


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--receipt',action='store_true');args=parser.parse_args()
    if args.receipt:receipt()
    value,read_only=freeze_or_verify();blob=(HERE/'SOURCE_SEAL.json').read_bytes()
    print(json.dumps(dict(read_only_verify=read_only,members=len(value['files']),root_SHA256=value['root_SHA256'],seal_bytes=len(blob),seal_SHA256=C.H(blob),SOURCE_only=True)))
