"""Final source index and saved267 JSON/source ABI join only; no tensor imports."""
from pathlib import Path
import ast
import hashlib
import json
import time

N = Path(__file__).resolve().parent
R = N / 'reports'
C = N.parent / 'OWN_MOD4_FULLSTATE_DEPTH_COLLECTOR_V267_20261101'


def row(path, data=None):
    data = path.read_bytes() if data is None else data
    return dict(path=str(path), bytes=len(data), SHA=hashlib.sha256(data).hexdigest())


def write(path, value):
    with path.open('x', encoding='utf8') as f:
        json.dump(value, f, indent=2, allow_nan=False)


actual_path = C / 'reports/ROOT267_NEW240_MEAN_REGRESSION_PARENT_OR_ORIGINAL_ERROR_RETURNED_ACTUAL.json'
schema_path = C / 'source/measured224_schema267.py'
actual_bytes = actual_path.read_bytes()
schema_bytes = schema_path.read_bytes()
actual = json.loads(actual_bytes)
parent = json.loads(actual['original_parent_stdout'])
result = parent['result']
tree = ast.parse(schema_bytes.decode('utf8'))
layout = ast.literal_eval(next(n.value for n in tree.body if isinstance(n, ast.Assign)
    and any(isinstance(t, ast.Name) and t.id == 'LAYOUT' for t in n.targets)))
expected = dict(physical73=(0, 73), contact_history18=(73, 91), applied_torque30=(91, 121),
    old_processed_targets6=(121, 127), L02=(127, 129), theta2=(129, 131),
    BODY_contact31x3_div400=(131, 224))
cpu_path = R / 'ACTUAL268_NEW_MEASURED224_SYNTHETIC_CPU_RETURNED.json'
cpu = json.loads(cpu_path.read_bytes())
join = dict(epoch=time.time(), kind='SAVED267_JSON_AND_SOURCE_AST_ABI_JOIN_ONLY_NOT_A_NEW_PHYSICS_CASE',
    passed=bool(actual['passed_execution'] and parent['passed_execution'] and result['passed']
                and layout == expected and cpu['passed']),
    actual267=row(actual_path, actual_bytes), schema267=row(schema_path, schema_bytes),
    explicit_layout={k: list(v) for k, v in layout.items()},
    exact_slices_compatible=layout == expected,
    ROOT267_fact_projection={k: result[k] for k in (
        'kind', 'model_SHA', 'model_byte_reads', 'model_decodes', 'optimizer_steps',
        'account_writes', 'controls', 'own_transitions', 'physics_callbacks',
        'feedback_samples', 'camera_reads', 'terminated', 'truncated',
        'depth_valid_input_controls', 'pre_reset_terminal_state_not_reset_pose',
        'literal_reward_inputs_and_memory_recorded', 'full_sensor_queue_component_memory_separate',
        'state224_not_all_sensor_Markov_memory_claim', 'actor_frozen_exact',
        'new_dataset_not_complete_WM_population_or_skill', 'real_SuperMimic_Pi_or_WM_updates')},
    ROOT267_original_wait=parent['wait'],
    metadata_only_original_producers={k: result[k] for k in ('producer', 'component_producer')},
    child268_actual_artifacts_opened_or_copied=0,
    old255_259_or267_case_replayed=0, actual_numeric_motor_binding_still_requires_ROOT_witness=True,
    context_for_policy_imagination='EXPLICIT_PENDING; no later actual depth9',
    limits='One N1 trajectory; not population/WM/Pi/skill qualification',
    authoring_errors_preserved=[dict(kind='apply_patch_verification_failed',
        scope='HANDOFF-only patch included an unrelated expected line; tool rejected atomically, no source or test changed',
        corrected='Subsequent HANDOFF-only patch; no CPU fixture rerun')])
write(R / 'SOURCE268_ACTUAL267_SAVED_METADATA_ABI_JOIN.json', join)
assert join['passed'], 'Saved metadata/source ABI join failed; preserve report and do not freeze ready'
paths = sorted([p for p in N.rglob('*') if p.is_file()])
index = N / 'INDEX268_MEASURED224_WM50_SOURCE_FROZEN.json'
write(index, dict(epoch=time.time(), kind='FROZEN_SOURCE_AND_SYNTHETIC_CPU_ONLY_MEASURED224_AUX151_WM50_V268',
    source_status='SOURCE_READY_SUPERVISED_WM_INTERFACE_ONLY',
    synthetic_CPU_passed=True, groups=5, refusals=15, synthetic_pairs=64, synthetic_WM_updates=1,
    actual_Pi_WM_updates=0, actual_models_raw_assets_SDK_GPU_SSH_Git_by_child=0,
    actual267='separate ROOT collector saved-JSON/source ABI cited; no artifact reads',
    runtime_or_skill_qualified=False, full_SuperMimic_conversion_complete=False,
    policy_future_safe_depth_context='EXPLICIT_PENDING',
    files=[row(p) for p in paths],
    immutable_external_reference_manifest=row(N / 'SOURCE268_PINNED_REFERENCE_BINDINGS.json'),
    actual267_reference_join=row(R / 'SOURCE268_ACTUAL267_SAVED_METADATA_ABI_JOIN.json'),
    Git_status='PENDING_ROOT_ORDINARY_APPEND; child made no Git calls',
    rerun_existing_once=False))
print(json.dumps(dict(passed=True, index=row(index), files=len(paths),
    source224_aux151=True, actual_Pi_WM_updates=0, Pi_depth_context='EXPLICIT_PENDING')))
