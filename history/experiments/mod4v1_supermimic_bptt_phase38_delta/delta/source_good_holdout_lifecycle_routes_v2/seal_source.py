"""Freeze only this NEW V2 SOURCE package; subsequent verification is read-only."""
from pathlib import Path
import json
import good_holdout_contract as C
import source_pins as P

HERE=Path(__file__).resolve().parent
MEMBERS=('good_holdout_contract.py','good_holdout_parent_actual_wait_controller_v1.py','good_holdout_remote_reader.py',
 'collect_good_holdout_result.py','source_pins.py','test_v2_input_propagation_source.py','seal_source.py','README.md',
 'SOURCE_PINS.json','SOURCE_TEST_LOG.txt','SOURCE_TEST_REPORT.json','SOURCE_RECEIPT.json')
EXPECTED_TESTS=11


def report_check(report):
    C.need(report.get('kind')=='GOOD_HOLDOUT_LIFECYCLE_ROUTES_V2_INPUT_PROPAGATION_SOURCE_TESTS' and report.get('passed')is True and report.get('tests')==EXPECTED_TESTS and report.get('template_only')is False and report.get('excluded_test_names')==[] and all(report.get(k)==0 for k in ('failures','errors','skipped')),'complete NEW V2 eleven SOURCE tests required, not prior40/template10')
    C.need(report.get('audit')==dict(native_imports=0,model_raw_report_budget_lock_accesses=0,process_network_signals_or_locks=0),'SOURCE audit not zero')
    log=(HERE/'SOURCE_TEST_LOG.txt').read_bytes()
    C.need(report.get('SOURCE_test_log')==dict(bytes=len(log),SHA256=C.H(log)),'actual on-disk V2 test log differs')


def receipt():
    C.need(not(HERE/'SOURCE_RECEIPT.json').exists(),'NEW V2 receipt already exists')
    inventory=P.verify_sources();report=json.loads((HERE/'SOURCE_TEST_REPORT.json').read_bytes());report_check(report)
    value=dict(kind='GOOD_HOLDOUT_LIFECYCLE_ROUTES_SOURCE_RECEIPT_V2',status='SOURCE_READY_FOR_PARENT_REVIEW_NOT_NATIVE_ADMISSION',
        tests=report,template_history=dict(tests=10,failures=0,errors=0,excluded_final_inventory_tests=1,final_pins_available_then=False,receipt_written=False),
        original_V1_author40_evidence_preserved_not_rerun=True,independent_validation_history_parent_reported_not_opened_or_executed_here=[dict(validator='independent_V1',passed=39,failed=1),dict(validator='independent_V2',passed=40,failed=0)],
        prior_routes_V1_12_seal=inventory['previous_routes_V1_12_seal']['seal'],old_good14_and_stage_V2_9_and_D3_10_unchanged=True,
        source_inventory=dict(good20=20,good_original_seal_members=14,D4_final_seal_members=10,old_stage_V2_seal_members=9,previous_D3_seal_members=10,previous_routes_V1_seal_members=12,
            D4_mirror_declared=92,D4_mirror_full_allowed_SOURCE=90,report_declarations_only=2,actual_report_stat_or_read=False,all92_full_bytes_read=False,groups_are_not_disjoint_sum=True,logical92_does_not_replace_flat20=True),
        final_D4_materializer_source_pins=C.STAGER_SOURCE_PINS,raw_provenance=inventory['D4_raw_provenance'],
        source_diagnosis_executed_false_not_a_denial_of_parent_actual_diagnosis=True,
        controller_reader_collector_whole_file_bytes_equal_V1=True,complete_contract_function_AST_equal_except_existing_typed_version_literal_and_label=True,
        original_parent_pin=C.PARENT_PIN,original_runtime_pin=C.RUNTIME_PIN,own_controller_pin=C.CONTROLLER_SOURCE_PIN,
        wire_filename_unchanged=C.STAGE_NAME,stage_receipt_kind=C.STAGE_KIND,source_derivation_version=4,
        original_grade_errors_close_binding_whole_FINAL_hash_cache_waits_preserved=True,new_wire_fields_prefixes_approval_quality_gates=False,
        original_native_resource_ready_worker_wait_seconds=[1800,900,2400],collector_poll_seconds=20,collector_cap_seconds=6000,
        original_full_good20_and_private_finite_EX_C_readonly_preserved=True,selected_E1_runtime_trees=2,eight_role_catalog_only=True,deferred_roles=list(C.DEFERRED),H1_included=False,
        actual_SSH=False,actual_prepare_stage_main=False,actual_controller_or_collector=False,actual_SDK_Torch_GPU_native=False,actual_parent_or_worker_wait=False,
        actual_model_raw_reports_C_locks_signals_Git=False,actual_native_binding='UNKNOWN',actual_quality=None,phase1_Gate1='UNKNOWN',phase1_exact_contract=False,phase1_interface=False,stage2_GO=False)
    with(HERE/'SOURCE_RECEIPT.json').open('x',encoding='utf-8')as stream:json.dump(value,stream,indent=2,allow_nan=False)
    return value


def freeze_or_verify():
    P.verify_sources();rows=[]
    for name in MEMBERS:
        item,_=P.checked_source(HERE/name);rows.append(dict(name=name,bytes=item['bytes'],SHA256=item['SHA256']))
    root=P.member_root(rows);path=HERE/'SOURCE_SEAL.json'
    if path.exists():
        value=json.loads(path.read_bytes());C.need(value.get('files')==rows and value.get('root_SHA256')==root,'immutable V2 SOURCE package differs')
        return value,True
    report=json.loads((HERE/'SOURCE_TEST_REPORT.json').read_bytes());report_check(report)
    source_receipt=json.loads((HERE/'SOURCE_RECEIPT.json').read_bytes())
    C.need(source_receipt.get('tests')==report and source_receipt.get('actual_native_binding')=='UNKNOWN' and source_receipt.get('stage2_GO')is False,'V2 receipt scope differs')
    value=dict(kind='SOURCE_ONLY_GOOD_HOLDOUT_LIFECYCLE_ROUTES_IMMUTABLE_SEAL_V2',status='SOURCE_READY_FOR_PARENT_REVIEW_NOT_NATIVE',
        root_algorithm='SHA256(sorted name TAB bytes TAB SHA256 LF records UTF8)',root_SHA256=root,files=rows,enabled=False,staged=False,dispatched=False,
        previous_routes_V1_12_unchanged=True,D4_final10_unchanged=True,previous_D3_10_and_old_good14_stage_V2_9_unchanged=True,
        D4_mirror_full_SOURCE=90,unread_report_declarations=2,actual_reports_read=False,controller_reader_collector_bytes_equal_V1=True,
        actual_native_binding='UNKNOWN',actual_wait_proof=False,actual_quality=None,stage2_GO=False)
    with path.open('x',encoding='utf-8')as stream:json.dump(value,stream,indent=2,allow_nan=False)
    return value,False


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--receipt',action='store_true');args=parser.parse_args()
    if args.receipt:receipt()
    value,read_only=freeze_or_verify();blob=(HERE/'SOURCE_SEAL.json').read_bytes()
    print(json.dumps(dict(read_only_verify=read_only,members=len(value['files']),root_SHA256=value['root_SHA256'],seal_bytes=len(blob),seal_SHA256=C.H(blob),SOURCE_only=True)))
