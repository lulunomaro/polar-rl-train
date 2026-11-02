"""One-shot stdlib provenance for NEW isolated review files; no Torch/training."""
import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
EXPECTED_BASE_CORE = '2603308f1adfe65f576eaf2aa3e0275d8465f110e6edd6e3db38304bf3e72039'
FROZEN = {
    'command_tracking_torch_candidate_v1.py': 'bb7555ff2de598677ea6cfe5dadefe0a9cfe37d37661635d186bcb14c1df2223',
    'ctx_reward_candidate_v1.py': 'c0cc5d201e98598d32f62572a61be633cb7d8bcdf53e5f33883792df12539454',
    'test_command_tracking_torch_cpu_v1.py': '3ac2d347ba10333cc3e10870ac94225c04963570c8d5e6c9263cefadf0595703',
}
SOURCE_PATHS = [
    'source_runtime/native_supermimic_bridge.py',
    'source_runtime/worker_supermimic_bptt.py',
    'source_runtime/synthetic_cpu_contract_check.py',
    'source_core_review/ctx_reward_learner.py',
    'source_core_review/teacher_residual.py',
    'source_core_review/evidence/geometry.py',
    'source_core_review/evidence/networks.py',
    'source_core_review/evidence/learner.py',
    'source_core_review/evidence/replay.py',
    'source_core_review/evidence/contract.py',
    'source_core_review/evidence/lqr_reference_mdp.py',
    'source_measurement_review_v1/SOURCE_EVIDENCE_AND_GAPS_V1.json',
    'source_measurement_review_v1/MEASUREMENT_IMPLEMENTATION_PLAN_V1.md',
    'discovery/reward_command_audit_v1/E2/runtime/isaac/mod4/e2_directional_spin_runtime_v1.py',
    'discovery/reward_command_audit_v1/E2/runtime/isaac/mod4/spin_translation_math.py',
    'discovery/reward_command_audit_v1/E2/runtime/isaac/mod4/mod4_task.py',
    'discovery/reward_command_audit_v1/E2/runtime/isaac/mod4/feedback_delay_runtime.py',
    'discovery/reward_command_audit_v1/E2/runtime/isaac/mod4/feedback_delay_mild.py',
    'discovery/reward_command_audit_v1/E2/runtime/isaac/mod4/sensor_mild_math.py',
    'discovery/reward_command_audit_v1/E2/runtime/isaac/mod4/scut_flat_rescue.py',
    'discovery/reward_command_audit_v1/W35/runtime/isaac/mod4/command208_v3.py',
    'discovery/reward_command_audit_v1/W35/runtime/isaac/mod4/terrain208_v3.py',
    'discovery/reward_command_audit_v1/W35/runtime/isaac/mod4/config_mod4v1_w35.py',
    'discovery/reward_command_audit_v1/W35/runtime/isaac/mod4/learning208_v3.py',
    'discovery/reward_command_audit_v1/W35/runtime/isaac/mod4/retained_flat_command_math.py',
    'discovery/sdk_reward_command_call_order_v1/envs/manager_based_rl_env.py',
    'discovery/sdk_reward_command_call_order_v1/managers/command_manager.py',
    'discovery/sdk_reward_command_call_order_v1/envs/mdp/observations.py',
    'reports/SDK_REWARD_COMMAND_SOURCE_READ_V1.json',
]
ARTIFACT_NAMES = [
    'command_observation_math_v1.py', 'command_tracking_math_reference_v1.py',
    'command_tracking_torch_candidate_v1.py', 'ctx_reward_candidate_v1.py',
    'build_candidate_copy_v1.py', 'SOURCE_TO_CANDIDATE_DIFF_V1.patch',
    'BUILD_CANDIDATE_RECEIPT_V1.json', 'test_command_tracking_stdlib_v1.py',
    'TEST_RESULTS_STDLIB_V1.json', 'test_command_tracking_torch_cpu_v1.py',
    'test_command_tracking_core_integration_cpu_v1.py',
    'SOURCE_COMMAND_REWARD_AUDIT_V1.md', 'SOURCE_EVIDENCE_AND_GAPS_V1.json',
    'write_source_provenance_v1.py',
]


def entry(path):
    raw = path.read_bytes()
    return {'path': str(path), 'bytes': len(raw), 'SHA256': hashlib.sha256(raw).hexdigest()}


def new_json(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False)
        stream.write('\n')


sources = [entry(ROOT / p) for p in SOURCE_PATHS]
base_core = next(x for x in sources if x['path'] == str(ROOT / 'source_core_review/ctx_reward_learner.py'))
assert base_core['SHA256'] == EXPECTED_BASE_CORE
artifacts = [entry(HERE / name) for name in ARTIFACT_NAMES]
for name, expected in FROZEN.items():
    assert next(x['SHA256'] for x in artifacts if x['path'] == str(HERE / name)) == expected, name
compiles = []
for name in ARTIFACT_NAMES:
    if name.endswith('.py'):
        text = (HERE / name).read_text(encoding='utf-8')
        ast.parse(text)
        compile(text, str(HERE / name), 'exec')
        compiles.append(name)
check = {'kind': 'LOCAL_STDLIB_SOURCE_AST_COMPILE_ONLY_NO_TORCH', 'passed': True,
         'frozen_three_SHA256_unchanged': True, 'original_core_SHA256_unchanged': True,
         'compiled_sources_without_execution': compiles,
         'integration_source': entry(HERE / 'test_command_tracking_core_integration_cpu_v1.py'),
         'Torch_imported': False, 'integration_executed_locally': False, 'native_training_updates': 0}
new_json(HERE / 'CORE_INTEGRATION_SOURCE_CHECK_V1.json', check)
artifacts.append(entry(HERE / 'CORE_INTEGRATION_SOURCE_CHECK_V1.json'))
provenance = {'kind': 'READ_ONLY_SOURCE_AND_NEW_CANDIDATE_PROVENANCE_NOT_RUNTIME_BINDING',
              'source_files': sources, 'new_artifacts': artifacts,
              'frozen_three_SHA256_unchanged': True, 'original_core_SHA256_unchanged': True,
              'scope': 'source_command_review_v1 only writes',
              'source_hashes_do_not_prove_live_import_binding': True,
              'self_hash_excluded_to_avoid_recursion': True}
new_json(HERE / 'SOURCE_PROVENANCE_V1.json', provenance)
artifacts.append(entry(HERE / 'SOURCE_PROVENANCE_V1.json'))
with (HERE / 'SHA256SUMS_V1.txt').open('x', encoding='utf-8') as stream:
    stream.write('# New review artifacts only. This list excludes its own hash.\n')
    for item in artifacts:
        stream.write(item['SHA256'] + '  ' + item['path'] + '\n')
print(json.dumps({'passed': True, 'source_files_hashed': len(sources),
                  'new_files_listed': len(artifacts), 'compiled_only': len(compiles),
                  'frozen_three_unchanged': True, 'original_core_unchanged': True,
                  'Torch_imported': False, 'training_updates': 0,
                  'provenance': entry(HERE / 'SOURCE_PROVENANCE_V1.json'),
                  'SHA256SUMS': entry(HERE / 'SHA256SUMS_V1.txt')}, indent=2))
