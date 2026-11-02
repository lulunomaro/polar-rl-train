"""One-shot source/metadata sealing only. No deployment, model or resource operations."""
from pathlib import Path
import ast
import difflib
import hashlib
import importlib.util
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT.parent

def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec); spec.loader.exec_module(value)
    return value

B = module('seal_builder_source_only', HERE / 'build_frozen_eval_candidates_v2.py')
R = module('seal_runtime_source_only', HERE / 'a1_frozen_eval_runtime_v2.py')

def small(path, maximum=262144):
    assert path.suffix.lower() in ('.py', '.json', '.md', '.patch', '.txt'), str(path)
    with path.open('rb') as stream: raw = stream.read(maximum+1)
    assert len(raw) <= maximum, str(path)
    return raw

def identity(path, *, alias=None, expected=None):
    raw = small(path)
    result = dict(path=str(path.resolve()), bytes=len(raw), SHA256=hashlib.sha256(raw).hexdigest())
    if expected is not None: assert (result['bytes'], result['SHA256']) == expected, str(path)
    if path.suffix == '.py':
        text = raw.decode('utf-8'); ast.parse(text, filename=str(path)); compile(text, str(path), 'exec')
    if alias is not None: result['installed_alias'] = alias
    return result

def save(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)


def main():
    output_names = ('FROZEN_EVAL_FINAL_WHITELIST_DIFF_V2.patch', 'FROZEN_EVAL_SEALED_SOURCE_INDEX_V2.json',
                    'FROZEN_EVAL_SOURCE_PROVENANCE_FINAL_V2.json', 'SHA256_FROZEN_EVAL_FINAL_V2.txt')
    assert not any((HERE / name).exists() for name in output_names), 'existing final seal is immutable'
    mapping = dict(formal='worker_formal_a1_frozen_candidate_v2.py', e1='e1_parallel_worker_a1_frozen_candidate_v2.py',
                   bridge='e1_fresh_bridge_a1_frozen_candidate_v2.py', parent='single_gpu_eight_a1_frozen_parent_candidate_v2.py')
    aliases = dict(formal='worker_sources/parent/worker_five_original_n80.py', e1='worker_sources/e1/e1_parallel_worker_safe.py',
                   bridge='worker_sources/e1/e1_fresh_runtime_bridge.py', parent='single_gpu_group_supervisor.py')
    baseline = {key: identity(value[0], expected=(value[1], value[2])) for key, value in B.PINS.items()}
    source_entries = [identity(HERE / mapping[key], alias=aliases[key]) for key in mapping]
    source_entries += [
        identity(HERE / 'a1_frozen_eval_runtime_v2.py', alias='a1_frozen_eval_runtime_v2.py'),
        identity(ROOT / 'source_eval_a1_raw35_v1' / 'frozen_a1_raw35_v1.py', alias='frozen_a1_raw35_v1.py', expected=R.HELPER_PIN),
        identity(ROOT / 'source_native_v6_runtime_compat' / 'pose_cache_runtime_adapter_v4.py', alias='pose_cache_runtime_adapter_v3.py', expected=R.POSE_PIN),
        identity(ROOT / 'source_app_close_runtime_compat_v6' / 'app_close_semantics_v6.py', alias='app_close_semantics_v5.py', expected=R.APP_PIN),
        identity(ROOT / 'source_native_v6_runtime_compat' / '_SOURCE_INPUT' / 'sealed_source' / 'native_supermimic_bridge.py',
                 alias='native_supermimic_bridge.py', expected=(13125, '8211964c2ce3dd78fdb9fee6603ee4a4dcfbca6fa9d7df44f20d3ddb7aaead29')),
        identity(ROOT / 'source_core_review' / 'evidence' / 'networks.py', alias='supermimic_vendor_v2/networks.py',
                 expected=(8609, 'c7829e6a1bb9166d724a931858b76424439f371669dfb4bb534b9e76c5c74706')),
        identity(ROOT / 'source_core_review' / 'evidence' / 'geometry.py', alias='supermimic_vendor_v2/geometry.py'),
        identity(ROOT / 'source_core_review' / 'evidence' / 'contract.py', alias='supermimic_vendor_v2/contract.py')]
    assert len(source_entries) == len({v['installed_alias'] for v in source_entries}) == 12
    evidence = BASE / 'mod4v1_experts_fulldr_rm70_20261101' / 'reports' / 'NINE_SINGLE_GPU_V8_CLOSED_20261102_101543' / 'GROUP_PLAN.json'
    group = json.loads(small(evidence)); manifest_hashes = {row['SHA'] for row in group['worker_files']}
    assert all(row['SHA256'] in manifest_hashes for row in baseline.values())
    cpu = ROOT / 'reports' / 'A1_FROZEN_MEAN_POLICY_CPU_V1.json'; cpu_data = json.loads(small(cpu))
    assert cpu_data['receipt']['passed'] and cpu_data['receipt']['CPU_mean_controls'] == 4 and cpu_data['receipt']['max_reference_error'] == 0.0
    for key, value in R.APPROVED_RSL_MODEL_SOURCE.items():
        assert cpu_data['receipt']['source_bindings']['rsl_rl.models.MLPModel'][key] == value
    selection = ROOT / 'reports' / 'EVAL_RSL_REFERENCE_SOURCE_SELECTION_V1.json'; selected = json.loads(small(selection))
    assert selected['selected_by'] == R.APPROVED_REFERENCE_PROVENANCE['selected_by']
    assert selected['native_GPU_previous_teacher_class_source_observed'] is None
    tests_path = HERE / 'TEST_RESULTS_STDLIB_FINAL_V2.json'; tests = json.loads(small(tests_path))
    assert tests['passed'] is True and tests['tests_run'] == 45 and tests['Torch_imported'] is False
    assert tests['actual_frozen_evaluation_runs'] == 0
    # Exact final-original diff, not the historical initial builder snapshot.
    diffs = []
    for key, candidate_name in mapping.items():
        original = B.read_pinned(key)
        candidate = (HERE / candidate_name).read_text(encoding='utf-8')
        diffs.extend(difflib.unified_diff(original.splitlines(True), candidate.splitlines(True),
                       fromfile=str(B.PINS[key][0]), tofile=str(HERE / candidate_name)))
    with (HERE / output_names[0]).open('x', encoding='utf-8', newline='\n') as stream: stream.write(''.join(diffs))
    index = dict(kind='SEALED_A1_FROZEN_EVAL_SOURCE_CANDIDATE_INDEX_V2_NOT_INSTALLED', entries=source_entries,
                 original_remaining_worker_files_must_be_retained_and_verified=True,
                 old_RSL_PPO_checkpoint_loader_must_not_be_called=True,
                 approved_RSL_model_source=R.APPROVED_RSL_MODEL_SOURCE,
                 approved_reference_provenance=R.APPROVED_REFERENCE_PROVENANCE,
                 actual_eval_RSL_source_binding=None, actual_paired_reference=None,
                 strict_current_parent_scope='ALL_EIGHT_ORIGINAL_ROLES_EXCLUDING_H1_NOT_MICROBATCH_PARENT',
                 new_batch_parent_or_actual_stage_executor_implemented=False)
    save(HERE / output_names[1], index)
    local_files = [identity(HERE / name) for name in (*mapping.values(), 'a1_frozen_eval_runtime_v2.py',
         'build_frozen_eval_candidates_v2.py', 'test_frozen_eval_integration_stdlib_v2.py', 'seal_frozen_eval_sources_v2.py',
         'SOURCE_A1_FROZEN_EVAL_INTEGRATION_V2.md', tests_path.name, output_names[0], output_names[1])]
    provenance = dict(kind='SOURCE_ONLY_FINAL_FROZEN_EVAL_INTEGRATION_SEAL_V2', original_sources=baseline,
         original_actual_group_plan=identity(evidence), CPU_reference_report=identity(cpu), parent_source_selection_report=identity(selection),
         sealed_source_entries=source_entries, local_final_artifacts=local_files,
         tests=dict(passed=True, stdlib_cases=45, actual_seconds=tests['seconds'], actual_Torch_test_runs=0, actual_frozen_evaluation_runs=0),
         preserved=dict(original_eight_scope_DR_physics_accepted_denominator=True,
                        original_parent_admission_finally_LF_text_AST_identical=True,
                        original_E1_whole_control_loop_AST_identical=True,
                        original_geometry_factories_E2_W35_endpoint_unchanged=True,
                        earlier_sealed_V6_and_frozen_helper_unchanged=True),
         history=dict(initial_builder_receipt_and_initial_diff_are_not_final_seal=True, source_builder_replay_exact_in_new_fixture=True),
         remaining=dict(actual_success_A1_FULL_FINAL_each_role=None, actual_eval_source_binding=None,
                        actual_native_N80_actor_and_caches=None, actual_paired_mother_same_pose_seed_UID_cache=None,
                        actual_canonical_parent_cost_close_and_wait=None, new_smallbatch_stage_executor=None,
                        teacher_from_same_cache_reference_worker_and_CPU_validation=None, aggregate_skill_pass_rate=None),
         original_PT_raw_JSONL_NPZ_C_SDK_GPU_SSH_Git_or_native_operations=0)
    save(HERE / output_names[2], provenance)
    all_receipts = local_files + [identity(HERE / output_names[2])]
    with (HERE / output_names[3]).open('x', encoding='utf-8', newline='\n') as stream:
        for row in all_receipts: stream.write(row['SHA256'] + '  ' + str(row['bytes']) + '  ' + row['path'] + '\n')
    print(json.dumps(dict(passed=True, source_entries=12, tests=45, runtime=identity(HERE / 'a1_frozen_eval_runtime_v2.py'),
         outputs=[identity(HERE / name) for name in output_names]), indent=2))

if __name__ == '__main__':
    main()
