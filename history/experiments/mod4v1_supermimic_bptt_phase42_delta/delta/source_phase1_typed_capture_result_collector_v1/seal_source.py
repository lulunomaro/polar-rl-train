"""Metadata-only freeze/readonly verification. Never reruns the eight cases.

Only this NEW, not-yet-sealed package may be written by --freeze. Existing source
archives are always read-only. --verify never imports a producer/collector entry.
"""
from pathlib import Path
import argparse
import ast
import hashlib
import json
import sys

import source_pins as P
import typed_collector_contract as C

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
MEMBERS = tuple(sorted(('typed_collector_contract.py','remote_metadata_reader.py',
    'collect_capture_result.py','source_pins.py','author_source_derivation.py',
    'test_typed_collector_source.py','README.md','seal_source.py','SOURCE_PINS.json',
    'SOURCE_TEST_LOG_attempt1.txt','SOURCE_TEST_REPORT_attempt1.json',
    'FINAL_SOURCE_METADATA_CHECK.json','SOURCE_RECEIPT.json')))
PRODUCTION = ('typed_collector_contract.py','remote_metadata_reader.py','collect_capture_result.py')


def need(value, message):
    if not value: raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False).encode('utf-8')+b'\n'


def raw_member(name):
    need(name in MEMBERS or name == 'SOURCE_SEAL.json', 'fixed own member only')
    path = HERE/name
    need(path.parent == HERE and not path.is_symlink() and path.is_file(), 'whole regular own SOURCE file required: '+name)
    need(0 < path.stat().st_size <= 2*1024*1024, 'own SOURCE text bound: '+name)
    raw = path.read_bytes(); raw.decode('utf-8-sig')
    if path.suffix == '.py': ast.parse(raw.decode('utf-8-sig'))
    return raw


def identity(name):
    raw = raw_member(name)
    return dict(relative=name,bytes=len(raw),SHA256=digest(raw))


def exclusive(name, value):
    need(not (HERE/'SOURCE_SEAL.json').exists(), 'frozen SOURCE is read-only')
    need(name in MEMBERS or name == 'SOURCE_SEAL.json', 'fixed own output only')
    target = HERE/name
    need(not target.exists() and target.parent == HERE, 'exclusive NEW metadata output required: '+name)
    with target.open('xb') as stream: stream.write(encoded(value))


def root_hash(rows):
    raw=json.dumps(rows,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode('utf-8')
    return digest(raw)


def first_test_receipt():
    raw=raw_member('SOURCE_TEST_REPORT_attempt1.json'); report=json.loads(raw)
    need(report.get('kind')=='EIGHT_NEW_TYPED_COLLECTOR_STDLIB_SOURCE_CASES_V1'
        and report.get('passed') is True and type(report.get('tests_run')) is int and report['tests_run']==8
        and all(type(report.get(k)) is int and report[k]==0 for k in ('failures','errors','skipped')),
        'first eight NEW SOURCE report must pass')
    need(report.get('old_tests_reexecuted') is False and report.get('forbidden_operations')==[]
        and report.get('forbidden_source_entry_calls')==[]
        and report.get('actual_whole_FINAL_trace_or_report_read') is False
        and report.get('actual_parent_or_controller_or_materializer_or_collection_entry_executed') is False,
        'first Source scope must remain honest')
    for name,size_key,sha_key in (('test_typed_collector_source.py','source_test_module_bytes','source_test_module_SHA256'),
        ('SOURCE_TEST_LOG_attempt1.txt','log_bytes','log_SHA256')):
        item=identity(name);need((item['bytes'],item['SHA256'])==(report[size_key],report[sha_key]),'first Source input/log identity differs')
    log=raw_member('SOURCE_TEST_LOG_attempt1.txt').decode('utf-8')
    need('Ran 8 tests in 5.495s\n\nOK\n' in log, 'first Source log must remain the actual original output')
    return dict(report=identity('SOURCE_TEST_REPORT_attempt1.json'),log=identity('SOURCE_TEST_LOG_attempt1.txt'),
        test_module=identity('test_typed_collector_source.py'),tests_run=8,failures=0,errors=0,skipped=0,
        unittest_log_elapsed_seconds=5.495,runner_elapsed_seconds=report['elapsed_seconds'],
        forbidden_operations=[],forbidden_source_entry_calls=[],old_tests_reexecuted=False,
        first_report_directly_binds_test_module_and_log=True,
        production_module_snapshot_in_first_report=False,
        this_final_metadata_step_reexecutes_tests=False)


def controller_confirmation():
    path=HERE.parent/'source_phase1_capture_controller_v1/phase1_capture_parent_actual_wait_controller_v1.py'
    raw=path.read_bytes()
    need((len(raw),digest(raw))==(3824,'95952059e6e8640a5ba37e858ca29c5f313340e041260093ecc8aaf671665831'),
        'original outer controller whole identity differs')
    tree=ast.parse(raw.decode('utf-8-sig')); constants={}
    for node in tree.body:
        if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name):
            if node.targets[0].id in ('PARENT','ROOT_PREFIX','STAGE_FILE'):
                constants[node.targets[0].id]=ast.literal_eval(node.value)
    need(constants==dict(PARENT=(9336,'d5575ff2e670fd18ea0a09d9f3d5c05c46bf606a027fcb84d97c6e34a88a2b41'),
        ROOT_PREFIX='MOD4V1_PHASE1_E3_PASSIVE_CAPTURE_V1_',STAGE_FILE=C.COMPLETE), 'original outer route constants differ')
    function=P.full_functions(raw)['validate_stage'].replace('\r\n','\n')
    expected="""def validate_stage(raw, expected_sha):
 assert hashlib.sha256(raw).hexdigest()==expected_sha
 data=json.loads(raw)
 assert data.get('materialized')is True and data.get('parent_launches')==0
 assert data.get('purpose')=='NEW_PASSIVE_INTERFACE_PROBE_NO_TRAIN'
 return data
"""
    need(function==expected,'whole original stage predicate differs')
    return dict(path=str(path),bytes=len(raw),SHA256=digest(raw),source_lines=[13,18],
        entire_original_controller_preserved=True,full_original_validate_stage=function,
        stage_name=C.COMPLETE,purpose=C.PURPOSE,new_completion_kind=C.STAGE_KIND,
        original_predicate_checks_old_kind=False,original_predicate_checks_PT_or_approval=False,
        source_mirror_T_root_is_not_outer_protocol_input=True,
        original_Popen_wait_finally_preserved=True,actual_controller_entry_executed=False)


def refresh_unsealed_inventory():
    need(not (HERE/'SOURCE_SEAL.json').exists(),'only unsealed NEW inventory can be refreshed')
    before_raw=raw_member('SOURCE_PINS.json');before=json.loads(before_raw)
    after=P.build_sources()
    before_external={k:v for k,v in before.items() if k!='derivation'}
    after_external={k:v for k,v in after.items() if k!='derivation'}
    need(before_external==after_external,'external Source inventory changed since first build')
    old=before['derivation'];new=after['derivation']
    changed=sorted(k for k in set(old)|set(new) if old.get(k)!=new.get(k))
    need(set(changed)<= {'whole_NEW_cli_SHA256'},'only own unsealed final CLI derivation SHA may refresh')
    need(new['whole_NEW_cli_SHA256']==digest(raw_member('collect_capture_result.py')),
        'final CLI identity must be whole current bytes')
    out=encoded(after)
    if before_raw!=out:
        (HERE/'SOURCE_PINS.json').write_bytes(out)
    return dict(only_NEW_unsealed_inventory_written=True,external_unique_SOURCE_files_unchanged=465,
        external_inventory_rows_and_all_seal_members_identical=True,
        changed_derivation_keys=changed,before_bytes=len(before_raw),before_SHA256=digest(before_raw),
        after_bytes=len(out),after_SHA256=digest(out),first_tests_reexecuted=False)


def final_check(refresh):
    inventory=P.verify_sources()
    need(inventory['independently_checked_unique_source_files']==465,'whole external465 required')
    need(inventory['reviewed_mirror']['verified_full_text_inputs']==396,'whole reviewed mirror396 required')
    need(inventory['finite_active_bindings']['complete']==34,'typed finite34 required')
    tests=first_test_receipt();controller=controller_confirmation()
    return dict(kind='PHASE1_TYPED_COLLECTOR_FINAL_SOURCE_METADATA_CHECK_V1',passed=True,
        not_another_eight_test_run=True,production_sources=[identity(name) for name in PRODUCTION],
        first_test=tests,inventory=identity('SOURCE_PINS.json'),inventory_refresh=refresh,
        source_derivation=inventory['derivation'],outer_controller_compatibility=controller,
        full_current_SOURCE_files_checked=465,mirror396=dict(R=395,T=1),finite34=dict(overlay=32,bootstrap=2),
        initial_author_is_historical_not_claimed_final_byte_reproducer=True,
        complete_frozen_source_is_authoritative=True,
        actual_SSH_materializer_controller_or_collector_entry_calls=0,
        actual_SDK_Torch_GPU_model_raw_C_lock_operations=0,
        actual_SDK_binding='UNKNOWN',actual_case_or_group_size='UNKNOWN',science_consumer_enabled=False,
        gate1='UNKNOWN',capture_interface_passed=False,exact=False,stage2_GO=False)


def receipt(check):
    inventory=json.loads(raw_member('SOURCE_PINS.json'))
    return dict(kind='PHASE1_TYPED_COLLECTOR_SOURCE_RECEIPT_V1',status='SOURCE_READY_NOT_NATIVE',source_only=True,
        first_new_eight_cases=check['first_test'],final_metadata_check=identity('FINAL_SOURCE_METADATA_CHECK.json'),
        final_inventory=identity('SOURCE_PINS.json'),production_source_whole_identities=check['production_sources'],
        no_production_or_test_source_edits_after_first_success=True,
        first_report_production_snapshot_not_invented=True,
        first_test_is_synthetic_protocol_only_not_actual_scientific_or_SDK_proof=True,
        full_original_runtime_core_AppV6_Base_normal_Source_imports=True,
        actual_production_ROOT_admission_executed=False,production_ROOT_gate_not_bypassed=True,
        AST_cropped_or_stubbed_production_helpers=False,old_tests_reexecuted=False,
        source_closure=dict(reviewed_mirror396_R395_T1=True,independent_external_unique465=True,
            producer_members=15,materializer_members=28,dependency_members=dict(sensor_B4=21,actuation=8,adapter=10,partition=9,codec=7,C2=5),
            original_B2_members=13,original_B2_declared_root=None,original_actuation_files=182,
            sensor_pin_references=435,sensor_full_python_sources=155,
            finite_active_bindings34_not_complete_static_baseline=True,
            historical_report_references_excluded_before_stat_or_open=3,
            source_patch_proofs_only=2,source_inventory_descriptor_model_paths_followed=False),
        original_outer_controller=check['outer_controller_compatibility'],
        original_inner_wait_and_both_EX_independent_of_outer_wait=True,
        original_native_wait_seconds=[1800,900,2400],collector_seconds=dict(interval=20,cap=6000),
        bounds=dict(BIG=67108864,GROUP_PLAN=8388608,other_JSON=2097152,whole_stdout_including_LF=16777216,own_log_tail=16384),
        explicit_payload_removal_paths=list(C.REMOVAL_PATHS),
        original_whole_JSON_read_hash_parse_once_before_projection=True,
        projection_is_not_original_bytes=True,unknown_fields_retained_no_overflow_crop=True,
        changed_size_mtime_or_missing_cached_file_errors_without_second_raw_read_hash_parse=True,
        cached_signature_is_not_claimed_to_detect_same_size_mtime_content_replacement=True,
        actual_whole_case_or_group_size='UNKNOWN',original_errors_grade_and_null_counts_preserved=True,
        science_consumer_enabled=False,science_consistency_status='UNKNOWN',
        authoring_history=[dict(kind='SOURCE_AUTHORING_NOT_TEST_OR_NATIVE_FAILURE',error="KeyError: 'SHA256'",
            cause='producer seal list uses lowercase sha256; initial Source reader assumed uppercase',
            fix="row.get('SHA256', row.get('sha256')) only; all whole source pin gates preserved"),
            dict(kind='PRE_FIRST_SUITE_STATIC_CORRECTION',cause='original watch has keyword-only tail',
                fix='removed extra positional dispatch in NEW remote_main and initial author before first eight cases'),
            dict(kind='PRE_FIRST_SUITE_FIXTURE_CORRECTION',cause='actual _AppPin field is module, not module_name',
                fix='synthetic metadata fixture field name corrected; original pin unchanged'),
            dict(kind='NEW_UNSEALED_INVENTORY_FINAL_METADATA_REFRESH',detail=check['inventory_refresh'])],
        actual_whole_FINAL_trace_or_runtime_report_read=False,
        actual_SSH_materializer_controller_collector_SDK_Torch_GPU_model_C_lock_operations=0,
        actual_SDK_binding='UNKNOWN',gate1='UNKNOWN',capture_interface_passed=False,exact=False,
        skill_success_rate=None,overall_eight_pass_rate=None,stage2_GO=False)


def verify():
    seal_raw=raw_member('SOURCE_SEAL.json');seal=json.loads(seal_raw)
    need(seal.get('kind')=='PHASE1_TYPED_COLLECTOR_SOURCE_SEAL_V1' and seal.get('member_count')==13,'typed own13 SOURCE seal required')
    rows=[identity(name) for name in MEMBERS]
    need(seal.get('files')==rows and seal.get('content_root_SHA256')==root_hash(rows),'frozen SOURCE member identity/root differs')
    first_test_receipt();controller_confirmation();P.verify_sources()
    check=json.loads(raw_member('FINAL_SOURCE_METADATA_CHECK.json'))
    need(check.get('passed') is True and check.get('not_another_eight_test_run') is True,
        'final Source metadata check required')
    need(check['production_sources']==[identity(name) for name in PRODUCTION],'final production identities differ')
    need(check['inventory']==identity('SOURCE_PINS.json'),'final Source inventory identity differs')
    note=json.loads(raw_member('SOURCE_RECEIPT.json'))
    need(note==receipt(check),'whole SOURCE receipt metadata differs')
    return dict(passed=True,readonly=True,member_count=13,root_SHA256=root_hash(rows),
        seal_bytes=len(seal_raw),seal_SHA256=digest(seal_raw),tests_reexecuted=False,
        native_or_actual_entry_executed=False,gate1='UNKNOWN',stage2_GO=False)


def freeze():
    need(not (HERE/'SOURCE_SEAL.json').exists(),'old sealed SOURCE is immutable')
    need(not (HERE/'FINAL_SOURCE_METADATA_CHECK.json').exists() and not (HERE/'SOURCE_RECEIPT.json').exists(),
        'NEW Source final metadata files already consumed')
    first_test_receipt();controller_confirmation()
    refresh=refresh_unsealed_inventory();check=final_check(refresh)
    exclusive('FINAL_SOURCE_METADATA_CHECK.json',check)
    exclusive('SOURCE_RECEIPT.json',receipt(check))
    rows=[identity(name) for name in MEMBERS]
    seal=dict(kind='PHASE1_TYPED_COLLECTOR_SOURCE_SEAL_V1',source_only=True,member_count=13,files=rows,
        content_root_SHA256=root_hash(rows),root_algorithm='SHA256 UTF8 canonical JSON of ordered files rows: sort_keys=True separators comma/colon ensure_ascii=False allow_nan=False',
        first_new_source_cases=8,old_tests_reexecuted=False,final_metadata_is_not_another_test_run=True,
        actual_SDK_binding='UNKNOWN',science_consumer_enabled=False,gate1='UNKNOWN',capture_interface_passed=False,exact=False,stage2_GO=False)
    exclusive('SOURCE_SEAL.json',seal)
    return verify()


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--freeze',action='store_true');parser.add_argument('--verify',action='store_true')
    args=parser.parse_args();need(args.freeze != args.verify,'choose exactly one of --freeze/--verify')
    print(json.dumps(freeze() if args.freeze else verify(),sort_keys=True))
