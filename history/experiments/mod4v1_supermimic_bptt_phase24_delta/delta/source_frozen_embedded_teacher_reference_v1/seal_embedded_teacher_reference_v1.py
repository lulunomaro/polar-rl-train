"""Source/metadata-only seal. Never import or run the future Torch fixture."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
EXPECTED_NAME = 'source_frozen_embedded_teacher_reference_v1'

def need(value, message):
    if not value: raise ValueError(message)

def digest(raw): return hashlib.sha256(raw).hexdigest()

def item(path):
    need(path.suffix.lower() in ('.py', '.md', '.json', '.patch'), 'small source/metadata only')
    raw = path.read_bytes()
    need(len(raw) < 262144, 'bounded source/metadata file required')
    return dict(path=str(path), bytes=len(raw), SHA256=digest(raw), lines=len(raw.splitlines()))

def output(name, value):
    with (HERE / name).open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False); stream.write('\n')


def main():
    need(HERE.name == EXPECTED_NAME, 'seal must run in the exact NEW source directory')
    inputs = [
        ('source_eval_a1_raw35_v1/frozen_a1_raw35_v1.py', (19226, '1ea4bcfa1081d63d0da2136fedf8c9fafa508d7bb2155095352da496327e4a21')),
        ('source_eval_a1_raw35_v1/remote_cpu_synthetic_check_v1.py', (6145, 'c8bcfed4826b2e37f0231c20967bdcb76934656be40aced2400312bf7d48d899')),
        ('source_eval_a1_raw35_v1/DELIVERABLES_SHA256_V1.json', None),
        ('source_a1_frozen_eval_integration_v2/a1_frozen_eval_runtime_v2.py', (37927, '7a092364cf63e9621481dc0a5554b56a22e4412cf89870c3db9a124864074b2e')),
        ('source_a1_frozen_eval_integration_v2/SOURCE_A1_FROZEN_EVAL_INTEGRATION_V2.md', (15535, '46556f62a6602561cb327e8dd0d0dbb92c405fc5fdea2ad4106405cdb53a8c68')),
        ('source_native_v6_runtime_compat/_SOURCE_INPUT/sealed_source/native_supermimic_bridge.py', (13125, '8211964c2ce3dd78fdb9fee6603ee4a4dcfbca6fa9d7df44f20d3ddb7aaead29')),
        ('source_resume_runtime_v2/worker_supermimic_bptt_pre_reset_candidate_v4.py', (17416, '9b5793ac3f9228124bc3bb927373b8914d8ff36bb1c3df74cb83c761329e431e')),
        ('source_w35_original_row_split_consumer_v1/w35_original_row_split_consumer_v1.py', (26594, '8b593a95c62981434dc99fc2475f1b7808b30f809109897e54c9db1f7d9ce879')),
        ('reports/EMBEDDED_TEACHER_REFERENCE_CPU_V1.json', None),
        ('reports/EMBEDDED_TEACHER_REFERENCE_CPU_V2.json', None),
    ]
    evidence = []
    for relative, expected in inputs:
        path = (ROOT / relative).resolve(); need(path.is_relative_to(ROOT), 'explicit project source only')
        value = item(path)
        if expected is not None: need((value['bytes'], value['SHA256']) == expected, 'previous sealed input differs: ' + str(path))
        value['previous_known_PIN_matched'] = True if expected is not None else None
        evidence.append(value)
    own = [
        'embedded_teacher_reference_v1.py', 'test_embedded_teacher_reference_stdlib_v1.py',
        'remote_cpu_embedded_teacher_synthetic_v1.py', 'API_CONTRACT_EMBEDDED_TEACHER_REFERENCE_V1.json',
        'EMBEDDED_TEACHER_REFERENCE_SOURCE_V1.md', 'CPU_TEST_EXECUTION_HISTORY_V1.json',
        'CPU_TEST_RESULTS_V1.json', 'CPU_TEST_RESULTS_FINAL_V1.json', 'CPU_TEST_RESULTS_HARDENED_V1.json',
        'seal_embedded_teacher_reference_v1.py', 'remote_cpu_embedded_teacher_synthetic_v2.py',
        'build_remote_cpu_fixture_v2.py', 'BUILD_CPU_FIXTURE_V2.json', 'REMOTE_CPU_FIXTURE_V1_TO_V2.patch',
        'CPU_FIXTURE_V2_DELTA_AND_ACTUAL_RECEIPT.md', 'API_CONTRACT_CPU_FIXTURE_DELTA_V2.json',
        'CPU_SOFTWARE_TEST_HISTORY_V2.json',
    ]
    compiled = []
    for name in own:
        path = HERE / name; data = path.read_text(encoding='utf-8')
        if path.suffix == '.py': compile(data, str(path), 'exec'); compiled.append(name)
        elif path.suffix == '.json': json.loads(data)
    tests = json.loads((HERE / 'CPU_TEST_RESULTS_HARDENED_V1.json').read_text(encoding='utf-8'))
    need(tests['tests_run'] == 42 and tests['passed'] is True and tests['failures'] == tests['errors'] == 0
         and tests['Torch_imported'] is False, 'final 42 stdlib-only tests required')
    for name, expected in [
        ('embedded_teacher_reference_v1.py', (16333, '400e06ea2c04edaab8330022a53455e13629b7f35d3ac7066f51df1acfcd0407')),
        ('remote_cpu_embedded_teacher_synthetic_v1.py', (11051, 'aa982495175d694b8327a545d4291f4bc8f0760d8a18df0fe0234c2d44a78d83')),
        ('remote_cpu_embedded_teacher_synthetic_v2.py', (16128, '246f8a305d0fed032da964c92b899d731bc81cab61804d901558d1be01dd8a2c')),
    ]:
        got = item(HERE / name); need((got['bytes'], got['SHA256']) == expected, 'pinned reference/fixture changed: ' + name)
    parent_v1 = json.loads((ROOT / 'reports/EMBEDDED_TEACHER_REFERENCE_CPU_V1.json').read_text(encoding='utf-8'))
    parent_v2 = json.loads((ROOT / 'reports/EMBEDDED_TEACHER_REFERENCE_CPU_V2.json').read_text(encoding='utf-8'))
    need(parent_v1['returncode'] == 1 and 'original teacher norm/std state missing' in parent_v1['stderr'], 'V1 failure history differs')
    need(type(parent_v2['returncode']) is int and parent_v2['returncode'] == 0 and parent_v2['stderr'] == '', 'parent V2 CPU not successful')
    cpu = parent_v2['receipt']; need(cpu == json.loads(parent_v2['stdout']), 'parent stdout/structured receipt differ')
    need(parent_v2['source_pins']['embedded_teacher_reference_v1.py'] == {'bytes': 16333, 'SHA': '400e06ea2c04edaab8330022a53455e13629b7f35d3ac7066f51df1acfcd0407'}, 'actual CPU adapter pin differs')
    need(parent_v2['source_pins']['remote_cpu_embedded_teacher_synthetic_v2.py'] == {'bytes': 16128, 'SHA': '246f8a305d0fed032da964c92b899d731bc81cab61804d901558d1be01dd8a2c'}, 'actual CPU fixture pin differs')
    need(cpu['passed'] is True and cpu['CPU_reference_controls'] == 4 and cpu['maximum_original_RSL_teacher_error'] == 0.0, 'CPU teacher math differs')
    need(cpu['maximum_candidate_math_teacher_difference'] == 0.1559954136610031 and cpu['candidate_math_difference_is_not_skill_or_reward_effect'] is True, 'CPU math difference incorrectly classified')
    need(cpu['teacher_normalization'] == 'identity_no_persistent_teacher_norm_state_observed' and cpu['teacher_norm_state_names'] == []
         and len(cpu['actual_teacher_state_keys']) == 9 and cpu['teacher_buffer_case']['actual_teacher_named_buffers'] == []
         and cpu['teacher_buffer_case']['status'] == 'not_applicable' and cpu['teacher_buffer_mutation_detected'] is None, 'actual optional teacher buffer schema differs')
    need(cpu['teacher_std_value_mutation_detected'] is True and cpu['std_full_value_error'] == 'full embedded teacher value differs: distribution.std_param'
         and cpu['std_original_frozen_guard_detected'] is True and cpu['sticky_failure_detected'] is True
         and cpu['residual_buffer_case'] == {'mutated_name': 'residual.obs_norm.mean', 'isolated': True, 'detected': True, 'error': 'cached/live actor tensor identity/version changed'}
         and cpu['caller_RNG_unchanged'] is True, 'independent negative/RNG proof differs')
    need(cpu['actual_training_producer_evidence'] is None and cpu['actual_frozen_reference_evaluation'] is None
         and cpu['actual_paired_environment_comparison'] is None and cpu['policy_semantic']['qualified_reference_execution'] is None
         and cpu['policy_semantic']['actual_paired_protocol_UID_match'] is None and cpu['policy_semantic']['relative_improvement'] is None, 'CPU fixture promoted to actual reference/effect')
    parent_cpu_summary = dict(report=str(ROOT / 'reports/EMBEDDED_TEACHER_REFERENCE_CPU_V2.json'), returncode=0,
        controls=4, num_envs=80, maximum_teacher_error=0.0, candidate_math_difference=0.1559954136610031,
        difference_is_skill_or_reward_effect=False, teacher_buffer_case='not_applicable',
        independent_STD_and_isolated_residual_buffer_negatives=True, RNG_unchanged=True,
        actual_native_reference=None, qualified_reference_execution=None, relative_improvement=None)
    doc = '\n'.join((HERE / name).read_text(encoding='utf-8') for name in
        ('EMBEDDED_TEACHER_REFERENCE_SOURCE_V1.md', 'CPU_FIXTURE_V2_DELTA_AND_ACTUAL_RECEIPT.md'))
    links = []
    for target in re.findall(r'\]\(<([^>]+)>\)', doc):
        source, _, fragment = target.partition('#')
        path = Path(source).resolve(); need(path.is_relative_to(ROOT), 'doc link outside project')
        record = item(path)
        if fragment:
            match = re.fullmatch(r'L(\d+)(?:-L(\d+))?', fragment); need(match is not None, 'bad source line link')
            lo, hi = int(match[1]), int(match[2] or match[1])
            need(1 <= lo <= hi <= record['lines'], 'doc line link outside file: ' + target)
        links.append(target)
    output('AUDIT_INPUTS_SHA256_V1.json', dict(kind='EXPLICIT_SMALL_TEXT_SOURCE_INPUTS_ONLY_V1', inputs=evidence,
           source_input_files=len(evidence), PT_raw_NPZ_SDK_GPU_remote_C_account_Git_operations=0))
    verification = dict(kind='SOURCE_ONLY_EMBEDDED_TEACHER_REFERENCE_VERIFICATION_V1', passed=True,
        previous_known_source_PINS_unchanged=True, explicit_bounded_input_files=len(evidence),
        own_source_compiled_not_executed=compiled, doc_links_and_lines_verified=len(links),
        stdlib_tests=tests, fixture_executed_or_rerun_by_child=False, parent_actual_CPU_V2=parent_cpu_summary, actual_native_reference=None,
        qualified_reference_execution=None, actual_paired_protocol_UID_match=None, relative_improvement=None,
        writes_outside_this_NEW_directory=False, original_native_worker_parent_or_accepted_loop_edits=False)
    output('SOURCE_REVIEW_VERIFICATION_V1.json', verification)
    own += ['AUDIT_INPUTS_SHA256_V1.json', 'SOURCE_REVIEW_VERIFICATION_V1.json']
    files = []
    for name in own:
        record = item(HERE / name); record['relative'] = name; files.append(record)
    canonical = json.dumps(files, sort_keys=True, separators=(',', ':')).encode()
    manifest = dict(kind='SOURCE_ONLY_SEALED_EMBEDDED_TEACHER_REFERENCE_V1', created_UTC=datetime.now(timezone.utc).isoformat(),
        source_root=str(HERE), files=files, entries=len(files), canonical_files_SHA256=digest(canonical),
        source_only_work_by_child=True, parent_actual_CPU_Torch_math=parent_cpu_summary, actual_native_reference=None,
        actual_paired_protocol_UID_match=None, relative_improvement=None,
        old_sealed_files_edited=False, rerun_only_in_NEW_copies=True)
    output('DELIVERABLES_SHA256_V1.json', manifest)
    final = item(HERE / 'DELIVERABLES_SHA256_V1.json')
    print(json.dumps(dict(passed=True, manifest=final, bundle_SHA256=manifest['canonical_files_SHA256'],
                         sealed_entries=len(files), source_inputs=len(evidence), doc_links=len(links), tests=tests), indent=2))


if __name__ == '__main__': main()
