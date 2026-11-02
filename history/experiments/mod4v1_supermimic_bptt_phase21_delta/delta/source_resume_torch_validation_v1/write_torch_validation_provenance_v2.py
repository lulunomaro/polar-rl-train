"""One-shot source provenance only. No Torch import or checkpoint read."""
import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def identity(path):
    raw = path.read_bytes()
    return dict(path=str(path), bytes=len(raw), SHA256=hashlib.sha256(raw).hexdigest())


pins = {
    'source_resume_torch_validation_v1/test_resume_legacy_torch_cpu_v1.py': '08c89b3603eb7b32b4eb430a9cde112035ca187695272ee992742ceb147079d7',
    'source_resume_torch_validation_v1/test_resume_legacy_torch_cpu_v2.py': '4a4141259410702d2103952a828be31a7ddaf28057272b69bbf8a8bde3109e55',
    'source_runtime/synthetic_cpu_contract_check.py': '4de256764f7fec0dac6fbb624a7a4189d7a686dc9d28bd5570a9a43f8afce10d',
    'source_runtime/native_supermimic_bridge.py': '8211964c2ce3dd78fdb9fee6603ee4a4dcfbca6fa9d7df44f20d3ddb7aaead29',
    'source_resume_runtime_v2/ctx_reward_full_resume_candidate_v2.py': '8116ea358dfe32e0efd568d00661ab1e13b602d267ea4b580ced04ec39e898ac',
    'source_resume_runtime_v2/resume_runtime_contracts_v3.py': 'dc4bc67193457a4fb72b125d23fa482cd3d686363bd1a93eb07268f4e4e26cb7',
    'source_command_review_v1/command_tracking_torch_candidate_v1.py': 'bb7555ff2de598677ea6cfe5dadefe0a9cfe37d37661635d186bcb14c1df2223',
    'source_command_review_v1/ctx_reward_candidate_v1.py': 'c0cc5d201e98598d32f62572a61be633cb7d8bcdf53e5f33883792df12539454',
    'source_command_review_v1/test_command_tracking_torch_cpu_v1.py': '3ac2d347ba10333cc3e10870ac94225c04963570c8d5e6c9263cefadf0595703',
    'source_resume_runtime_v2/SOURCE_RESUME_PROVENANCE_V4.json': '07acd1b6e0dd7f8f1c0f53d0a95671ff36206e59718f33e0ad98eeca276b248d',
    'source_resume_runtime_v2/SHA256SUMS_RESUME_V4.txt': '3b793ceb9202e40f3a1b2956e0b2239106ff258508f54e64ced3ea7d2e009a5f',
}
for relative, sha in pins.items(): assert identity(ROOT / relative)['SHA256'] == sha, relative
sealed = json.loads((ROOT / 'source_resume_runtime_v2/SOURCE_RESUME_PROVENANCE_V4.json').read_bytes())
for row in sealed['new_top_level_artifacts']:
    assert identity(Path(row['path']))['SHA256'] == row['SHA256'], row['path']
for row in sealed['read_only_sources']:
    assert identity(Path(row['path']))['SHA256'] == row['SHA256'], row['path']
read_sources = [ROOT / relative for relative in pins if not relative.startswith('source_resume_torch_validation_v1/')] + [
    ROOT / 'source_core_review/evidence/learner.py', ROOT / 'source_core_review/evidence/networks.py',
    ROOT / 'source_core_review/evidence/geometry.py', ROOT / 'source_core_review/evidence/replay.py',
    ROOT / 'reports/LEGACY_A0_A1_FULL_RESUME_CPU_V1.json',
]
compiled = []
paths = sorted(path for path in HERE.iterdir() if path.is_file() and path.suffix in ('.py', '.json', '.md', '.patch'))
for path in paths:
    if path.suffix == '.py':
        text = path.read_text(encoding='utf-8');ast.parse(text);compile(text, str(path), 'exec');compiled.append(str(path))
local_checks = []
for name, count in [('LOCAL_STDLIB_SOURCE_CHECK_V1.json', 22), ('LOCAL_STDLIB_CONSTRUCTOR_CHECK_V2.json', 7)]:
    value = json.loads((HERE / name).read_bytes())
    assert value['passed'] is True and value['tests_run'] == count and value['Torch_imported'] is False
    local_checks.append(dict(identity(HERE / name), tests_run=count, passed=True))
old_cpu = json.loads((ROOT / 'reports/LEGACY_A0_A1_FULL_RESUME_CPU_V1.json').read_bytes())
assert old_cpu['returncode'] == 1 and old_cpu['receipt']['passed'] is False
provenance = dict(kind='CPU_LEGACY_FULL_RESUME_VALIDATION_SOURCE_BUNDLE_V2_NOT_NATIVE',
    actual_execution_here='STDLIB_AST_COMPILE_ONLY', new_top_level_artifacts=[identity(path) for path in paths],
    source_pins_verified=pins, read_only_reference_sources=[identity(path) for path in read_sources],
    previous_resume_source_top_level_artifacts_SHA_unchanged=len(sealed['new_top_level_artifacts']),
    previous_original_source_hashes_unchanged=True, previous_three_command_frozen_hashes_unchanged=True,
    AST_compile_without_execution=compiled, local_stdlib_source_checks=local_checks,
    CPU_V1=dict(identity(ROOT / 'reports/LEGACY_A0_A1_FULL_RESUME_CPU_V1.json'), passed=False, returncode=1,
                failed_test='v1:364 expected init0; actual vendor constructor init1',
                partial_restore_checks_before_failure_not_entire_suite_PASS=True),
    CPU_V2='PENDING_PARENT_SEPARATE_CPU_RECEIPT',
    new_V2_fix='constructor snapshot1; actual full load/continued collection must not add initialization',
    plan='A0/A1 each H16/hist10 collect8 WMaux20 pi3 -> own synthetic full -> restored3 -> continued4',
    baseline_held_command_aux_sensor_approximation=True, oracle_new_projection_bound_anchor_reward_changes=0,
    native_expert_BPTT_updates_here=0, actual_training_updates_here=0, Torch_imports_here=0,
    SDK_imports_here=0, real_checkpoint_reads_here=0, GPU_operations_here=0,
    original_PT_C_GO_lock_Git_SSH_operations=0,
    runtime_noise_physics_DR_100Hz_getter_original_checkpoint_Appclose_not_validated=True)
output = HERE / 'CPU_VALIDATION_SOURCE_PROVENANCE_V2.json'
with output.open('x', encoding='utf-8') as stream: json.dump(provenance, stream, indent=2)
rows = [identity(path) for path in paths] + [identity(output)]
sha_path = HERE / 'SHA256SUMS_TORCH_VALIDATION_V2.txt'
with sha_path.open('x', encoding='utf-8') as stream:
    for row in rows: stream.write(row['SHA256'] + '  ' + row['path'] + '\n')
print(json.dumps(dict(provenance=identity(output), SHA_inventory=identity(sha_path),
                      new_artifacts=len(paths), compiled_Python=len(compiled), local_stdlib_checks=[22,7],
                      previous_resume_source_files_unchanged=len(sealed['new_top_level_artifacts']),
                      Torch_imports=0, actual_training_updates=0, actual_CPU_V2='PENDING_PARENT'), indent=2))
