"""Freeze this NEW SOURCE package once; subsequent runs are read-only verification."""
from pathlib import Path
import json
import good_holdout_contract as C
import source_pins as P

HERE=Path(__file__).resolve().parent
MEMBERS=('good_holdout_contract.py','good_holdout_parent_actual_wait_controller_v1.py','good_holdout_remote_reader.py',
 'collect_good_holdout_result.py','source_pins.py','test_good_holdout_routes_source.py','seal_source.py','README.md',
 'SOURCE_PINS.json','SOURCE_TEST_LOG.txt','SOURCE_TEST_REPORT.json','SOURCE_RECEIPT.json')
EXPECTED_TESTS=40
HISTORY=[dict(scope='FIRST_35_SOURCE_TESTS_BEFORE_NEW_INVENTORY_TESTS',tests=35,failures=0,errors=1,
 error="KeyError: 'whole_skill_rate'",cause='NEW test_30 assumed a nonexisting original summary key; original API is pooled_whole_skill_rate',
 fix='Only NEW test assertion key corrected; original summary and acceptance untouched',success_receipt_written=False),
 dict(scope='RERUN_35_SOURCE_TESTS_AFTER_KEY_CORRECTION_AND_TERMINAL_IMMUTABILITY_HARDENING',tests=35,failures=0,errors=0,passed=True,success_receipt_written=False)]


def receipt():
    C.need(not(HERE/'SOURCE_RECEIPT.json').exists(),'NEW SOURCE receipt already exists')
    inventory=P.verify_sources();report=json.loads((HERE/'SOURCE_TEST_REPORT.json').read_bytes());log=(HERE/'SOURCE_TEST_LOG.txt').read_bytes()
    C.need(report.get('passed')is True and report.get('tests')==EXPECTED_TESTS and all(report.get(k)==0 for k in ('failures','errors','skipped')),'own complete40 SOURCE suite required')
    C.need(report.get('audit')==dict(native_imports=0,model_raw_report_budget_lock_accesses=0,process_network_signals_or_locks=0),'SOURCE test audit not zero')
    C.need(report.get('SOURCE_test_log')==dict(bytes=len(log),SHA256=C.H(log)),'actual on-disk SOURCE test log differs')
    value=dict(kind='GOOD_HOLDOUT_LIFECYCLE_ROUTES_SOURCE_RECEIPT_V1',status='SOURCE_READY_FOR_PARENT_REVIEW_NOT_NATIVE_ADMISSION',
        tests=report,pre_seal_test_history=HISTORY,upstream_D664_32_or_good_subset_tests_not_counted_as_own_40=True,
        source_inventory=dict(good20=20,good_original_seal_members=14,D664_final_seal_members=10,old_V2_seal_members=9,
            D664_mirror_declared=79,D664_mirror_full_allowed_SOURCE=78,old_actual_plan_declaration_only=1,old_actual_plan_read_or_stat=False,
            groups_are_not_disjoint_sum=True,all79_full_bytes_read=False),
        final_D664_materializer_source_pins=C.STAGER_SOURCE_PINS,own_controller_pin=C.CONTROLLER_SOURCE_PIN,
        original_good_parent_pin=C.PARENT_PIN,original_good_runtime_pin=C.RUNTIME_PIN,
        controller_derivation='Complete original9595 identity and Popen/wait/except/finally AST retained; only typed routes/literals and good materialization prechecks',
        original_source_grade_and_errors_preserved=True,whole_original_FINAL_once_cached_hashed_and_parsed=True,whole_FINAL_projection=False,
        complete_original_runtime_core_AppV6_Base_guard_reference_modules=True,AST_cropped_or_stubbed=False,
        old_producer_IO_predicates_rerun=False,original_summary_only_after_two_externally_qualified_groups=True,
        original_native_resource_ready_worker_wait_seconds=[1800,900,2400],collector_poll_seconds=20,collector_cap_seconds=6000,
        original_private_and_global_finite_EX_owned_by_original_parent=True,controller_or_collector_owns_resource_or_C=False,
        eight_role_catalog_only=True,selected_E1_runtime_trees=2,deferred_roles=list(C.DEFERRED),H1_included=False,
        actual_SSH=False,actual_stage=False,actual_dispatch=False,actual_controller_or_collector=False,
        actual_parent_or_SDK_child_wait=False,actual_Torch_SDK_GPU_native=False,actual_model_raw_replay_or_reports_read=False,
        actual_C_ledger_or_lock_or_signal_or_Git_operation=False,actual_native_binding='UNKNOWN',actual_quality=None,
        phase1_Gate1='UNKNOWN',phase1_exact_contract=False,phase1_interface=False,stage2_GO=False)
    with(HERE/'SOURCE_RECEIPT.json').open('x',encoding='utf-8')as stream:json.dump(value,stream,indent=2,allow_nan=False)
    return value


def freeze_or_verify():
    inventory=P.verify_sources();rows=[]
    for name in MEMBERS:
        item,_=P.checked_source(HERE/name);rows.append(dict(name=name,bytes=item['bytes'],SHA256=item['SHA256']))
    root=P.member_root(rows);seal=HERE/'SOURCE_SEAL.json'
    if seal.exists():
        value=json.loads(seal.read_bytes());C.need(value.get('files')==rows and value.get('root_SHA256')==root,'immutable SOURCE package differs')
        return value,True
    report=json.loads((HERE/'SOURCE_TEST_REPORT.json').read_bytes());source_receipt=json.loads((HERE/'SOURCE_RECEIPT.json').read_bytes())
    C.need(report.get('passed')is True and report.get('tests')==EXPECTED_TESTS and all(report.get(k)==0 for k in ('failures','errors','skipped')),'own complete40 SOURCE suite required')
    C.need(source_receipt.get('tests')==report and source_receipt.get('stage2_GO')is False and source_receipt.get('actual_native_binding')=='UNKNOWN','SOURCE receipt/test/native scope differs')
    value=dict(kind='SOURCE_ONLY_GOOD_HOLDOUT_LIFECYCLE_ROUTES_IMMUTABLE_SEAL_V1',status='SOURCE_READY_FOR_PARENT_REVIEW_NOT_NATIVE',
        root_algorithm='SHA256(sorted name TAB bytes TAB SHA256 LF records UTF8)',root_SHA256=root,files=rows,
        enabled=False,staged=False,dispatched=False,actual_native_binding='UNKNOWN',actual_wait_proof=False,actual_quality=None,
        original_good20_unchanged=True,D664_final10_unchanged=True,old_good14_and_stage_V2_9_unchanged=True,
        D664_mirror_full_SOURCE=78,old_actual_plan_declaration_only=1,old_actual_plan_opened=False,whole_original_FINAL_projection=False,stage2_GO=False)
    with seal.open('x',encoding='utf-8')as stream:json.dump(value,stream,indent=2,allow_nan=False)
    return value,False


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--receipt',action='store_true');args=parser.parse_args()
    if args.receipt:receipt()
    value,read_only=freeze_or_verify();blob=(HERE/'SOURCE_SEAL.json').read_bytes()
    print(json.dumps(dict(read_only_verify=read_only,members=len(value['files']),root_SHA256=value['root_SHA256'],seal_bytes=len(blob),seal_SHA256=C.H(blob),SOURCE_only=True)))
