"""One-shot stdlib provenance: hashes/AST/compile only, no checkpoint or runtime."""
import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def identity(path):
    raw = path.read_bytes()
    return dict(path=str(path), bytes=len(raw), SHA256=hashlib.sha256(raw).hexdigest())


def tree(path): return ast.parse(path.read_text(encoding='utf-8'))
def dump(node): return ast.dump(node, include_attributes=False)
def methods(path, class_name):
    node = next(n for n in tree(path).body if isinstance(n, ast.ClassDef) and n.name == class_name)
    return {n.name: n for n in node.body if isinstance(n, ast.FunctionDef)}

pinned = {
    'source_core_review/ctx_reward_learner.py': '2603308f1adfe65f576eaf2aa3e0275d8465f110e6edd6e3db38304bf3e72039',
    'source_runtime/supermimic_original_owner.py': 'c8b3512abea803151f7a6a1fc05563cd8c16d5f68ad5e40b2e18f7cdc6f92087',
    'source_runtime/supermimic_original_owner_shared_v2.py': '5e4e77d86ed993236bfc09dee8d264db6b23989ff52c3bff5cbb279b11b3bf54',
    'source_runtime/worker_supermimic_bptt.py': 'c372db143195a1ce2c52ae3f0dd26af8eb763f571e2f48275b9f0d39a1eb2534',
    'source_command_review_v1/command_tracking_torch_candidate_v1.py': 'bb7555ff2de598677ea6cfe5dadefe0a9cfe37d37661635d186bcb14c1df2223',
    'source_command_review_v1/ctx_reward_candidate_v1.py': 'c0cc5d201e98598d32f62572a61be633cb7d8bcdf53e5f33883792df12539454',
    'source_command_review_v1/test_command_tracking_torch_cpu_v1.py': '3ac2d347ba10333cc3e10870ac94225c04963570c8d5e6c9263cefadf0595703',
}
for relative, sha in pinned.items(): assert identity(ROOT / relative)['SHA256'] == sha, relative
source_paths = [ROOT / relative for relative in pinned] + [
    ROOT / 'source_runtime/native_supermimic_bridge.py',
    ROOT / 'source_runtime/original_role_command_binding_candidate_v2.py',
    ROOT / 'reports/FIRST_NATIVE_WINDOW_CLOSED_TRUTH_V1.json',
    ROOT / 'reports/COMMAND_CANDIDATE_CORE_INTEGRATION_CPU_V3.json',
]
old_methods = methods(ROOT / 'source_core_review/ctx_reward_learner.py', 'ContextRewardLearner')
new_methods = methods(HERE / 'ctx_reward_full_resume_candidate_v2.py', 'ContextRewardLearner')
assert all(dump(node) == dump(new_methods[name]) for name, node in old_methods.items() if name != 'load')
assert [dump(n) for n in old_methods['load'].body[1:]] == [dump(n) for n in new_methods['load_full_checkpoint'].body]
owner_checks = []
for new_name, old_name in [
    ('supermimic_original_owner_pre_reset_candidate_v4.py', 'supermimic_original_owner.py'),
    ('supermimic_original_owner_shared_pre_reset_candidate_v4.py', 'supermimic_original_owner_shared_v2.py'),
]:
    old = tree(ROOT / 'source_runtime' / old_name)
    new = tree(HERE / new_name)
    protected = lambda t: [dump(n) for n in t.body if isinstance(n, (ast.FunctionDef, ast.Assign)) and getattr(n, 'name', None) != 'main']
    assert protected(old) == protected(new)
    owner_checks.append(dict(candidate=new_name, original=old_name, all_nonmain_functions_and_global_assignments_AST_identical=True))
worker = tree(HERE / 'worker_supermimic_bptt_pre_reset_candidate_v4.py')
old_worker = tree(ROOT / 'source_runtime/worker_supermimic_bptt.py')
config = lambda t: next(n for n in ast.walk(t) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'SuperMimicConfig')
assert dump(config(worker)) == dump(config(old_worker))
first_guard = lambda t: next(n for n in ast.walk(t) if isinstance(n, ast.FunctionDef) and n.name == 'before_action').body[0]
assert dump(first_guard(worker)) == dump(first_guard(old_worker))
resets = [n for n in ast.walk(worker) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Name) and n.func.value.id == 'env' and n.func.attr == 'reset']
assert len(resets) == 1
worker_text = (HERE / 'worker_supermimic_bptt_pre_reset_candidate_v4.py').read_text(encoding='utf-8')
assert worker_text.index('install_optional_pose_cache_runtime_adapter(env,task,J') < worker_text.index('reset=env.reset()') < worker_text.index('bind_original_command_after_fresh_reset(env,role,obs)') < worker_text.index('bridge=BridgeClass(')
assert 'torch.equal(current[key],value)' in worker_text and 'value.detach().clone() for key,value in actor.state_dict().items()' in worker_text
receipts = []
for name, count in [('TEST_RESULTS_STDLIB_RESUME_RECHECK_V2.json', 50),
                    ('TEST_RESULTS_ACTOR_VARIANTS_STDLIB_V3.json', 71),
                    ('TEST_RESULTS_PRE_RESET_INSTALLER_STDLIB_V4.json', 12)]:
    result = json.loads((HERE / name).read_bytes())
    assert result['passed'] is True and result['tests_run'] == count and result['Torch_imported'] is False
    receipts.append(dict(identity(HERE / name), tests_run=count, passed=True))

artifact_paths = sorted(path for path in HERE.iterdir() if path.is_file() and path.suffix in ('.py', '.json', '.md', '.patch'))
compiled = []
for path in artifact_paths:
    if path.suffix == '.py':
        source = path.read_text(encoding='utf-8');ast.parse(source);compile(source, str(path), 'exec')
        compiled.append(str(path))
provenance = dict(kind='SOURCE_ONLY_RESUME_ACTOR_VARIANT_AND_PRE_RESET_HOOK_FINAL_PROVENANCE_V4',
                  read_only_sources=[identity(path) for path in source_paths],
                  new_top_level_artifacts=[identity(path) for path in artifact_paths],
                  synthetic_fixture_subdirectories_excluded_from_artifact_inventory=True,
                  original_and_three_frozen_SHA_verified_unchanged=pinned,
                  core_original_methods_except_load_AST_identical=True,
                  decoded_full_loader_body_original_after_decode_AST_identical=True,
                  owner_protected_AST=owner_checks,
                  original_worker_config_and_finite_guard_AST_identical=True,
                  only_original_env_reset_count=1,
                  stable_installer_before_only_reset_then_original_C113_binding_then_bridge=True,
                  actual_teacher_weights_and_buffers_value_check_after_load=True,
                  stdlib_test_receipts=receipts, distinct_tests=83,
                  initial_selector_failure_preserved='TEST_RESULTS_STDLIB_RESUME_V2.json',
                  AST_compile_without_execution=compiled,
                  Torch_imports=0, SDK_imports=0, real_checkpoint_reads=0, GPU_operations=0,
                  native_runs=0, training_updates=0, original_account_C_GO_lock_operations=0,
                  actual_Torch_full_restore='PENDING_CPU_SOFTWARE_VALIDATION',
                  actual_A1_legacy_core_integration='PENDING_CPU_SOFTWARE_VALIDATION',
                  actual_adapter_binding_and_native_restore='PENDING_PARENT_OWN_NEW_WINDOW',
                  prior_command_core_CPU_V3_is_separate_not_native=True)
provenance_path = HERE / 'SOURCE_RESUME_PROVENANCE_V4.json'
with provenance_path.open('x', encoding='utf-8') as stream: json.dump(provenance, stream, indent=2)
rows = [identity(path) for path in artifact_paths] + [identity(provenance_path)]
with (HERE / 'SHA256SUMS_RESUME_V4.txt').open('x', encoding='utf-8') as stream:
    for row in rows: stream.write(row['SHA256'] + '  ' + row['path'] + '\n')
print(json.dumps(dict(provenance=identity(provenance_path), SHA_inventory=identity(HERE / 'SHA256SUMS_RESUME_V4.txt'),
                      top_level_artifacts=len(artifact_paths), source_files=len(source_paths), compiled_Python=len(compiled),
                      distinct_stdlib_tests=83, original_and_frozen_unchanged=True, Torch_imports=0,
                      actual_native_or_training=0), indent=2))
