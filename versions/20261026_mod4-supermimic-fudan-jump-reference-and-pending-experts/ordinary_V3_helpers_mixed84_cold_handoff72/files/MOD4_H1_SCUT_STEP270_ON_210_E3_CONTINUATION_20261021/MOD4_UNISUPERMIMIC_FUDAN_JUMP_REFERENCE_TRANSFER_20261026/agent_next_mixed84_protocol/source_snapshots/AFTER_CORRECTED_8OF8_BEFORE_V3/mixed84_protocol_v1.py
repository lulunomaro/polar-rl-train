"""SOURCE TEMPLATE: stateless mixed84 metadata gates; no I/O or admission on import."""
from pathlib import PurePosixPath
import hashlib
import json
import re

NAMESPACE = 'H1step270_mixed_supermimic_fudan_2610v84'
LOCAL_STAGE = 'H1_STEP270_MIXED_FUDAN_SUPERMIMIC_RESOURCE_V84_20261026'
PREVIOUS_NAMESPACE = 'H1step270_three_experts_2610v83b'
METADATA_BYTES = 2536
METADATA_SHA = 'c6e421115263e6bfd0fb31630882087fb644efbfb3a56bfbd39643c4478c891e'
MIN_REMAINING_STRICT = 86412.86069250107
CLOSED_REMAINING_SNAPSHOT = 595256.8240613937
CLOSED_FEE = 10943.796510219574
PREVIOUS_OWNER = dict(pid=1493851, creation=1792994651.61)
CAP_SECONDS = 3900
SAVE_SECONDS = 3600
EXIT_SECONDS = 300
SOURCES = {
    'h1': dict(SHA='8bb9869ac683550c1e7be1c9dffae9a5eac022e0de0fc8f251cd2005cfa6d4c6', Adam=829700, updates=130),
    'e2': dict(SHA='72f4cbefeb5bf02af6f39a9d2922faa8032e36e81cb9a142df45154158998c9f', Adam=857460, updates=90),
    'recovery': dict(SHA='68d95156fc5dd294e43b21ad39691da8f1df1c5b85667db3001335796521ea49', Adam=860800, updates=83),
}
GPUS = dict(h1='GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e',
            e2='GPU-16828f91-2b45-b646-8dc0-9481138e2842',
            recovery='GPU-c27eecbd-6838-7290-1cd2-37e34522213d')
FUDAN_REPO_SHA = '8204e853dfd2ed06d85a322e1a998c3d20a3be2c'


def digest(value):
    return hashlib.sha256(json.dumps(value, indent=2).encode()).hexdigest()


def sha(value):
    assert isinstance(value, str) and re.fullmatch('[0-9a-f]{64}', value), 'Actual SHA pin required'
    return value


def relative(value):
    path = PurePosixPath(value)
    assert value and not path.is_absolute() and '..' not in path.parts and '\\' not in value
    return value


def validate_objective_contract(contract):
    assert contract['schema'] == 'mod4.supermimic.partial_reference_objective_contract.v1'
    assert (contract['native_goal_dim'], contract['native_obs_dim'], contract['native_history'],
            contract['native_actions'], contract['native_joints']) == (73, 128, 10, 6, 30)
    assert contract['own_task_analytic_height_curve'] == 'excluded_from_this_imagination_surrogate'
    assert contract['own_task_forward'] == 'existing_native_base_goal_X_and_Y0_only_not_Fudan_coverage'
    assert contract['demo_XY_and_XY_velocity_and_unobserved_spins'] == 'excluded_by_explicit_mask'
    assert contract['native_world_model'] == 'only_actual_own_plant_executed_transitions'
    assert contract['physical_reward'] == 'existing_V8_RewardManager_unchanged'
    assert contract['physical_H1'] == '2.5ms_TGS32_4_100Hz_decimation4_unchanged'
    assert contract['does_not_admit_environment_training_or_skill_graduation']
    metadata = contract['reference_metadata']
    mask = metadata['conditioning_feature_mask73']
    assert len(mask) == 73 and all(type(value) is bool for value in mask)
    assert all(mask[index] is False for index in (0, 1, 7, 8))
    assert metadata['foreign_transitions_for_native_world_model'] is False
    assert metadata['target_control_dt_s'] == .01
    assert metadata['clock_alignment']['native_frame_anchor'] == 100
    assert metadata['clock_alignment']['reference_time_anchor_s'] == .5
    assert metadata['clock_alignment']['uses_future_actions_or_gate_choices'] is False
    return True


def validate_closed83B(proof, owner_identity):
    assert proof['passed'] and set(proof['models']) == {'h1', 'e2', 'recovery'}
    assert proof['all_owner_nodes_children_actual_out'] and proof['original_canonical_cost_settled']
    assert proof['all_original_private_shared_locks_free']
    assert owner_identity['pid'] == PREVIOUS_OWNER['pid'] and owner_identity['creation'] == PREVIOUS_OWNER['creation']
    total = 0.
    for key, pin in SOURCES.items():
        model = proof['models'][key]
        final = model['final']
        assert model['Adam'] == pin['Adam'] and model['updates'] == pin['updates']
        assert final['SHA'] == pin['SHA'] and final['twohost_complete_SHA'] and final['bytes'] > 0
        assert PREVIOUS_NAMESPACE + '/' + key + '/' in final['path']
        cost = model['actual_cost']
        assert cost['actual_returncode'] == 0 and cost['duration_bound_passed']
        assert 0 < cost['charged_seconds'] <= CAP_SECONDS
        total += cost['charged_seconds']
    assert abs(total - proof['actual_cost_sumonce']) < 1e-5 and abs(total - CLOSED_FEE) < 1e-5
    assert proof['remaining_actual_snapshot'] == CLOSED_REMAINING_SNAPSHOT
    return dict(source_metadata_qualified_only=True, original83B_cost_not_recharged=True)


def validate_reference_preparation(bundle):
    """Called before source binding. Pending/null inputs always reject."""
    assert bundle['status'] == 'ACTUAL_REFERENCE_AND_ADAPTER_CPU_VALIDATED'
    reference = bundle['reference']
    assert reference['passed'] and reference['teacher_CPU_rollout_actual']
    assert reference['repository_commit'] == FUDAN_REPO_SHA
    assert reference['original_teacher_ONNX_used'] and reference['required_assets_complete']
    assert reference['selected_original_source_timestep_s'] == .002
    assert reference['source_is_partial_standing_jump_not_H1_step270_or_stable_recovery_proof']
    assert reference['not_our_policy_inference'] and reference['not_forced_action_or_trajectory_clamp']
    sha(reference['teacher_ONNX_SHA'])
    sha(reference['asset_provenance_SHA'])
    sha(reference['reference_artifact_SHA'])
    sha(reference['reference_provenance_report_SHA'])
    relative(reference['artifact_relative'])
    assert reference['artifact_bytes'] > 0
    adapter = bundle['adapter_CPU']
    assert adapter['passed'] and adapter['CPU_only'] and not adapter['CUDA_initialized']
    assert adapter['actual_reference_loaded'] and adapter['reference_reader_schema_verified']
    assert adapter['reference_artifact_SHA'] == reference['reference_artifact_SHA']
    assert adapter['source_robot'] == 'Fudan_wheel_legged' and adapter['target_robot'] == 'MOD4_H1'
    assert adapter['state_joints'] == 30 and adapter['actions'] == 6
    assert adapter['no_forced_actions'] and adapter['original_goal_machine_unchanged']
    sha(adapter['retargeting_protocol_SHA'])
    sha(adapter['adapter_source_SHA'])
    sha(adapter['report_SHA'])
    sha(adapter['objective_contract_SHA'])
    validate_objective_contract(bundle['objective_contract'])
    for name in ('bridge_source_SHA', 'finalization_source_SHA', 'native_CPU_source_SHA'):
        sha(bundle['candidate_pins'][name])
    assert bundle['native_bootstrap_source_SHA'] == SOURCES['h1']['SHA']
    assert bundle['native_bootstrap_Adam'] == SOURCES['h1']['Adam']
    assert bundle['native_bootstrap_kind'] == 'qualified83B_H1_frozen_PPO_core_only'
    assert bundle['old82Q_native_prefix_or_unknown_final_used'] is False
    assert bundle['candidate_V10_reward_used'] is False
    lifecycle = bundle['finalization_CPU']
    assert lifecycle['passed'] and lifecycle['CPU_only'] and lifecycle['passed_count'] == lifecycle['count'] >= 21
    assert lifecycle['finalization_source_SHA'] == bundle['candidate_pins']['finalization_source_SHA']
    sha(lifecycle['report_SHA'])
    return dict(reference_preparation_validated=True,
                reference_artifact_SHA=reference['reference_artifact_SHA'],
                adapter_CPU_report_SHA=adapter['report_SHA'],
                not_target_admission_or_GO=True)


def require_native_manifest_pins(manifest, bundle):
    validate_reference_preparation(bundle)
    rows = {row['relative']: row for row in manifest['files']}
    assert manifest['key'] == 'e2' and manifest['source_SHA'] == SOURCES['h1']['SHA']
    ref = bundle['reference']
    artifact = rows[ref['artifact_relative']]
    assert artifact['SHA'] == ref['reference_artifact_SHA'] and artifact['bytes'] == ref['artifact_bytes']
    names = dict(bridge_source_SHA='source/h1_supermimic_bridge_v1.py',
                 finalization_source_SHA='source/native_finalization_v1.py',
                 native_CPU_source_SHA='test_native_h1_fudan_reference_CPU_v84.py')
    for key, name in names.items():
        assert rows[name]['SHA'] == bundle['candidate_pins'][key]
    assert rows['FUDAN_REFERENCE_PROVENANCE_ACTUAL.json']['SHA'] == ref['reference_provenance_report_SHA']
    assert rows['FUDAN_ADAPTER_CPU_ACTUAL.json']['SHA'] == bundle['adapter_CPU']['report_SHA']
    assert rows['FUDAN_PARTIAL_OBJECTIVE_CONTRACT_ACTUAL.json']['SHA'] == bundle['adapter_CPU']['objective_contract_SHA']
    assert rows['NATIVE_FINALIZATION_CPU_PROOF_ACTUAL.json']['SHA'] == bundle['finalization_CPU']['report_SHA']
    assert rows['source/supermimic_reference_adapter_v1.py']['SHA'] == bundle['adapter_CPU']['adapter_source_SHA']
    return True


def validate_installed_native(sdk, native_cpu, spec, manifest_sha, bundle):
    validate_reference_preparation(bundle)
    assert spec['key'] == 'e2' and spec['finite_method_test'] and spec['h1_step270_method_test']
    assert spec['source_SHA'] == SOURCES['h1']['SHA'] and spec['source_Adamstep'] == SOURCES['h1']['Adam']
    assert spec['execution_backend'] == 'target72' and spec['GPU_UUID'] == GPUS['e2']
    assert not spec.get('cross_host_qualified_source'), 'This is not cross-host E2 policy qualification'
    assert sdk['passed_CPU_only'] and sdk['source_SHA'] == spec['source_SHA'] and sdk['all17Adam'] == spec['source_Adamstep']
    assert sdk['manifest_SHA'] == manifest_sha == spec['manifest_SHA']
    assert sdk['sampling_acceleration_CPU']['passed'] and len(sdk['actual_RSL_sources']) == 2
    assert sdk['new_reward_integration_CPU']['actual_installed_sampled_excess_SDK_compute_tested']
    assert native_cpu['passed'] and native_cpu['actual_installed_CPU_passed'] and not native_cpu['CUDA_initialized']
    assert native_cpu['manifest_SHA'] == manifest_sha and native_cpu['source_SHA'] == spec['source_SHA']
    assert native_cpu['reference_artifact_SHA'] == bundle['reference']['reference_artifact_SHA']
    assert native_cpu['adapter_CPU_report_SHA'] == bundle['adapter_CPU']['report_SHA']
    assert native_cpu['objective_contract_SHA'] == bundle['adapter_CPU']['objective_contract_SHA']
    assert native_cpu['offline_named_mapping_verified']
    assert native_cpu['actual_runtime_order_readback'] is False
    validate_objective_contract(native_cpu['offline_objective_contract'])
    assert native_cpu['offline_objective_contract']['reference_metadata']['sdk_joint_order_verified'] is False
    assert native_cpu['candidate_pins'] == bundle['candidate_pins']
    assert native_cpu['original_physics_and_success_unchanged'] and native_cpu['finalization_lifecycle_CPU_passed']
    assert native_cpu['partial_mask_objective_actual_CPU_admitted']
    return True


def validate_fresh_resources(resources):
    assert resources['actual_fresh_snapshot'] and resources['all_expected_GPU_empty']
    assert resources['free_MiB']['h1'] > 15669 and resources['free_MiB']['e2'] > 15669
    assert resources['free_MiB']['recovery'] > 7000
    assert resources['RAM_available_bytes'] > 8 * 1024**3
    assert resources['postcopy_disk_free_bytes'] > 25 * 1024**3
    assert resources['runtime_fullsave_disk_floor_bytes'] == 8 * 1024**3
    assert resources['canonical_active_segment'] is None and resources['original_locks_actual_free']
    assert resources['remaining_actual_snapshot'] > MIN_REMAINING_STRICT
    return True


def native_ready_value(spec, bundle, sdk, unit, manifest_sha):
    validate_installed_native(sdk, unit, spec, manifest_sha, bundle)
    return dict(kind='UNISUPERMIMIC_FUDAN_H1_83B_CROSSHOST_SOURCE_SDK_CPU_V84',
                passed=True, source_SHA=spec['source_SHA'], GPU_UUID=spec['GPU_UUID'],
                execution_backend=spec['execution_backend'],
                actual_installed_CPU_passed=True, actual_H1_source_SDK_CPU_passed=True,
                native_joint_states=30, actions=6,
                source_closed83B_healthy_three_original_cost_allout_passed=True,
                not_production_E2_source_or_skill_qualification=True,
                original_H1_270_physics_source_exact=True,
                reference_artifact_SHA=bundle['reference']['reference_artifact_SHA'],
                adapter_CPU_report_SHA=bundle['adapter_CPU']['report_SHA'],
                objective_contract_SHA=bundle['adapter_CPU']['objective_contract_SHA'],
                offline_named_mapping_verified=True,
                actual_runtime_order_readback=False,
                candidate_pins=bundle['candidate_pins'],
                reference_and_adapter_actual_CPU_validated=True)


def native_valid_ready(row, spec):
    envelope = row.get('closed_source_CPU') or {}
    value = envelope.get('value') or {}
    return bool(spec.get('finite_method_test') and spec['key'] == 'e2'
                and spec['source_SHA'] == SOURCES['h1']['SHA']
                and spec['source_Adamstep'] == SOURCES['h1']['Adam']
                and spec['GPU_UUID'] == GPUS['e2'] and spec['execution_backend'] == 'target72'
                and row.get('key') == 'e2' and row.get('phase') == 'ready'
                and not row.get('original_error') and row.get('manifest_SHA') == spec['manifest_SHA']
                and envelope.get('actual_CPU_waited_EXIT0') and envelope.get('SHA') == digest(value)
                and value.get('passed') and value.get('kind') == 'UNISUPERMIMIC_FUDAN_H1_83B_CROSSHOST_SOURCE_SDK_CPU_V84'
                and value.get('source_SHA') == spec['source_SHA'] and value.get('GPU_UUID') == spec['GPU_UUID']
                and value.get('actual_installed_CPU_passed') and value.get('actual_H1_source_SDK_CPU_passed')
                and value.get('source_closed83B_healthy_three_original_cost_allout_passed')
                and value.get('not_production_E2_source_or_skill_qualification')
                and value.get('original_H1_270_physics_source_exact')
                and value.get('reference_and_adapter_actual_CPU_validated')
                and value.get('reference_artifact_SHA') == spec.get('reference_artifact_SHA')
                and value.get('adapter_CPU_report_SHA') == spec.get('adapter_CPU_report_SHA')
                and value.get('objective_contract_SHA') == spec.get('objective_contract_SHA')
                and value.get('offline_named_mapping_verified')
                and value.get('actual_runtime_order_readback') is False
                and value.get('candidate_pins') == spec.get('candidate_pins'))


def split_collected_results(normal_models, native_method, original_cost):
    assert set(normal_models) == {'h1', 'recovery'}, 'Native H1 is not a production E2 model'
    assert set(original_cost) == {'h1', 'e2', 'recovery'}
    assert all(row['duration_bound_passed'] for row in original_cost.values())
    assert native_method['not_production_H1_or_E2_source']
    return dict(models=normal_models, native_method=native_method,
                original_slots_cost=original_cost,
                normal_E2_83B_source_preserved_paused=SOURCES['e2'],
                qualification_scope='normal83B_H1_E3_baselines_and_separate_Fudan_native_H1_method',
                no_all_unfinished_experts_training_claim=True)
