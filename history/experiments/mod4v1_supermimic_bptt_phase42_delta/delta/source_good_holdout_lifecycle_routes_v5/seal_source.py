"""Whole SOURCE metadata binding and exclusive seal; never runs the test suite.

D7/component final pins must arrive before any final output is admitted.
PREP's first twelve tests and final metadata checks remain separate evidence.
"""
from pathlib import Path
import ast
import copy
import json
import sys
import good_holdout_contract as C
import source_pins as P

HERE = Path(__file__).resolve().parent
MEMBERS = (
    'good_holdout_contract.py', 'good_holdout_parent_actual_wait_controller_v1.py',
    'good_holdout_remote_reader.py', 'collect_good_holdout_result.py',
    'source_pins.py', 'test_v5_case_final_size_source.py', 'seal_source.py',
    'README.md', 'SOURCE_PINS.json', 'PREP_SOURCE_TEST_LOG.txt',
    'PREP_SOURCE_TEST_REPORT.json', 'FINAL_PIN_BINDING_CHECK.json',
    'SOURCE_RECEIPT.json',
)


def own_raw(name):
    C.need(name in MEMBERS or name == 'SOURCE_SEAL.json', 'fixed own SOURCE output only')
    path = HERE / name
    C.need(not path.is_symlink(), 'own SOURCE symlink rejected')
    C.need(0 < path.stat().st_size <= P.MAX_SOURCE, 'own SOURCE text bound')
    return path.read_bytes()


def identity(name):
    raw = own_raw(name)
    if name.endswith('.py'):
        ast.parse(raw.decode('utf-8-sig'), filename=name)
    return dict(name=name, bytes=len(raw), SHA256=C.H(raw))


def exclusive_json(name, value):
    C.need(name in MEMBERS and not (HERE / 'SOURCE_SEAL.json').exists(), 'no writes after SOURCE seal')
    with (HERE / name).open('x', encoding='utf-8', newline='\n') as writer:
        json.dump(value, writer, ensure_ascii=False, indent=2, allow_nan=False)
        writer.write('\n')


def normalized_contract(source):
    # Match the existing PREP Path.read_text() universal-newline representation;
    # byte-based whole-file identities are kept separate and never substituted.
    source = source.replace('\r\n', '\n').replace('\r', '\n')
    tree = ast.parse(source)
    normalized = copy.deepcopy(tree)
    changed = []
    for node in normalized.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if name in ('RUNTIME_PIN', 'INDEX_PIN', 'STAGER_SOURCE_PINS'):
                node.value = ast.Constant(value=None)
                changed.append(name)
            elif name == 'OVERLAY_PINS':
                C.need(isinstance(node.value, ast.Dict), 'whole overlay literal required')
                matches = [i for i, key in enumerate(node.value.keys) if isinstance(key, ast.Constant) and key.value == 'good_expert_holdout_runtime_v1.py']
                C.need(len(matches) == 1, 'single runtime overlay row required')
                node.value.values[matches[0]] = ast.Constant(value=None)
                changed.append('OVERLAY_PINS/runtime')
    C.need(set(changed) == {'RUNTIME_PIN', 'INDEX_PIN', 'STAGER_SOURCE_PINS', 'OVERLAY_PINS/runtime'} and len(changed) == 4, 'only exact pending pin metadata normalized')
    functions = {node.name: C.H(ast.get_source_segment(source, node).encode()) for node in tree.body if isinstance(node, (ast.FunctionDef, ast.ClassDef))}
    return C.H(ast.dump(normalized, include_attributes=False).encode()), functions


def check_prep_and_code():
    prep = json.loads(own_raw('PREP_SOURCE_TEST_REPORT.json'))
    C.need(prep.get('kind') == 'GOOD_HOLDOUT_LIFECYCLE_V5_PREP_FIRST_EXECUTION_RECEIPT' and type(prep.get('tests')) is int and prep['tests'] == 12 and prep.get('passed') is True, 'first PREP twelve-result receipt required')
    C.need(all(type(prep.get(k)) is int and prep[k] == 0 for k in ('failures', 'errors', 'skipped')) and prep.get('excluded_test_names') == [] and prep.get('declared_suite') == 12, 'PREP failure/skip/exclusion count')
    audit = prep.get('audit', {})
    C.need(set(audit) == {'native_imports', 'forbidden_artifact_accesses', 'process_network_signal_or_lock_operations', 'forbidden_production_calls'} and all(type(v) is int and v == 0 for v in audit.values()), 'PREP audit must be strict zero')
    C.need(prep.get('D7_final_pins_received') is False and prep.get('no_test_rerun_to_create_this_receipt') is True and prep.get('original_stream_bytes_captured') is False and prep.get('receipt_origin') == 'TRANSCRIPTION_OF_RETAINED_FIRST_EXECUTION_TOOL_STDOUT_NOT_A_RERUN', 'first receipt provenance must not be rewritten as final-pin execution')
    log = own_raw('PREP_SOURCE_TEST_LOG.txt')
    C.need(prep.get('PREP_SOURCE_TEST_LOG') == dict(bytes=len(log), SHA256=C.H(log)), 'PREP transcribed log identity differs')
    rows = prep.get('source_identities_observed_after_first_execution', [])
    C.need(len(rows) == 5 and len({r.get('name') for r in rows}) == 5, 'five first-execution source identities required')
    unchanged = []
    for row in rows:
        if row['name'] == 'good_holdout_contract.py':
            continue
        actual = identity(row['name'])
        C.need(actual == row, 'previously tested SOURCE whole bytes changed: ' + row['name'])
        unchanged.append(actual)
    structure = prep.get('PREP_contract_structure', {})
    normalized, functions = normalized_contract(own_raw('good_holdout_contract.py').decode('utf-8-sig'))
    C.need(normalized == structure.get('normalized_whole_module_AST_SHA256') and functions == structure.get('complete_function_source_SHA256'), 'contract differs beyond final pin metadata from the already-tested PREP')
    return dict(PREP_report=identity('PREP_SOURCE_TEST_REPORT.json'), PREP_tests=12,
                PREP_elapsed_seconds=prep['elapsed_seconds'], PREP_D7_pins_received=False,
                PREP_receipt_origin=prep['receipt_origin'], tests_rerun=False,
                unchanged_complete_tested_sources=unchanged,
                complete_contract_functions_unchanged=True,
                contract_full_module_AST_unchanged_except_four_pin_metadata_values=True,
                contract_normalized_whole_AST_SHA256=normalized)


def final_pin_binding_check():
    C.require_final_pins()
    inventory = P.verify_sources()
    preserved = check_prep_and_code()
    return dict(kind='GOOD_HOLDOUT_LIFECYCLE_V5_FINAL_PIN_BINDING_SOURCE_CHECK',
                scope='FULL_SOURCE_IDENTITIES_AND_METADATA_ONLY_NOT_ANOTHER_TWELVE_TEST_RUN',
                passed=True, final_pin_binding_received=True, preserved_PREP=preserved,
                SOURCE_inventory=identity('SOURCE_PINS.json'),
                SOURCE_inventory_kind=inventory.get('kind'),
                active_index_pin=list(C.INDEX_PIN), active_runtime_pin=list(C.RUNTIME_PIN),
                stager_source_pins=C.STAGER_SOURCE_PINS,
                case_FINAL_MAX=C.CASE_FINAL_MAX, PLAN_MAX=C.PLAN_MAX,
                GROUP_MAX=C.GROUP_MAX, EXPORT_MAX=C.EXPORT_MAX,
                actual_native_binding='UNKNOWN', actual_quality=None, stage2_GO=False,
                original_reports_or_FINALs_read=False,
                controller_watch_collect_task_or_main_executed=False,
                native_or_original_metadata_closure_imported=False,
                test_modules_imported_or_replayed=False)


def bind_final():
    exclusive_json('FINAL_PIN_BINDING_CHECK.json', final_pin_binding_check())


def receipt():
    expected = final_pin_binding_check()
    C.need(json.loads(own_raw('FINAL_PIN_BINDING_CHECK.json')) == expected, 'complete final binding check differs')
    value = dict(kind='GOOD_HOLDOUT_LIFECYCLE_V5_SOURCE_RECEIPT', status='SOURCE_READY_NOT_NATIVE',
                 PREP_first_tests=dict(count=12, passed=True, elapsed_seconds=0.722,
                                      D7_final_pins_received=False, tests_rerun=False,
                                      report=identity('PREP_SOURCE_TEST_REPORT.json')),
                 separate_final_pin_binding=identity('FINAL_PIN_BINDING_CHECK.json'),
                 final_pin_binding_not_an_additional_test_suite=True,
                 source_inventory=identity('SOURCE_PINS.json'),
                 preserved_whole_controller_and_collector=True,
                 reader_only_exact_case_maximum_selector_changed=True,
                 generic_read_complete_export_print_and_validation_functions_unchanged=True,
                 no_intent_backfill_no_regrade_no_historical_failure_upgrade=True,
                 parent_reported_D6_case_bytes=dict(CURB_PROTECTED878=802787, SLOPE135=509289),
                 parent_reported_D6_close_error_grade_false_outer_wait_RC1_preserved=True,
                 parent_reported_native_counts_not_retested_or_new_lifecycle_evidence=True,
                 actual_source_runtime_binding='UNKNOWN', actual_native_binding='UNKNOWN',
                 actual_quality=None, Gate1='UNKNOWN', exact_GO=False, interface_GO=False,
                 stage2_GO=False, SOURCE_approval_or_native_GO_created=False,
                 SSH_SDK_Torch_GPU_model_raw_report_C_lock_Git_operations=False,
                 actual_controller_watch_collect_or_native_main_executed=False,
                 code_authoring_history=['Copied-source initial edit required reading new target; exact retry only',
                                         'Version-label literal indent mismatch corrected by reading actual source',
                                         'README offset85 out of range: actual77 lines; read from1 then targeted edit',
                                         'SOURCE sealer edit observation required reading current file before exact retry'],
                 final_metadata_binding_authoring_history=[
                     dict(attempt='inventory1', error='complete declaration row only', cause='MD audit digest transcription omitted 962', correction='restored exact64hex fixed D7 mirror digest; no gate relaxation'),
                     dict(attempt='inventory2', error='only D7 typed labels in complete function: preflight_summary', cause='normalizer used uppercase constant name rather than existing lowercase keyword', correction='exact source_derivation_version=7 to6 representation; production functions unchanged'),
                     dict(attempt='final_binding1', error='contract differs beyond final pin metadata from the already-tested PREP', cause='PREP function-source hashes use Path.read_text universal LF; checker initially used raw CRLF', correction='same PREP universal-newline source representation; full AST already matched and raw file identities remain separate')],
                 final_metadata_checks_are_not_new_test_runs=True,
                 new_test_failures=0, new_test_errors=0)
    exclusive_json('SOURCE_RECEIPT.json', value)


def freeze_or_verify():
    C.require_final_pins()
    expected_check = final_pin_binding_check()
    C.need(json.loads(own_raw('FINAL_PIN_BINDING_CHECK.json')) == expected_check, 'final SOURCE metadata changed')
    rows = [identity(name) for name in MEMBERS]
    seal = dict(kind='GOOD_HOLDOUT_LIFECYCLE_ROUTES_V5_SOURCE_SEAL',
                status='SOURCE_READY_NOT_NATIVE', files=rows, root_SHA256=P.member_root(rows),
                count=len(MEMBERS), PREP_tests=12, final_metadata_checks_not_tests=True,
                actual_native_binding='UNKNOWN', actual_quality=None, stage2_GO=False)
    path = HERE / 'SOURCE_SEAL.json'
    existing = path.exists()
    if existing:
        C.need(json.loads(own_raw('SOURCE_SEAL.json')) == seal, 'entire immutable SOURCE seal differs')
    else:
        with path.open('x', encoding='utf-8', newline='\n') as writer:
            json.dump(seal, writer, ensure_ascii=False, indent=2, allow_nan=False)
            writer.write('\n')
    raw = own_raw('SOURCE_SEAL.json')
    return dict(read_only_verify=existing, SOURCE_SEAL=dict(bytes=len(raw), SHA256=C.H(raw)),
                members=len(rows), root_SHA256=seal['root_SHA256'])


if __name__ == '__main__':
    if sys.argv[1:] == ['--bind-final']:
        bind_final()
    elif sys.argv[1:] == ['--receipt']:
        receipt()
    elif not sys.argv[1:]:
        print(json.dumps(freeze_or_verify()))
    else:
        raise SystemExit('SOURCE-only usage: --bind-final | --receipt | no args for seal/read-only verify')
