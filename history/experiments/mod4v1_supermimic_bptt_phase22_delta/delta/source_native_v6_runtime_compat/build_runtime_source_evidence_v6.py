"""One-shot bounded source/evidence receipt. No SDK import, model, authority or native work."""
from __future__ import annotations
import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent


def main():
    specs = {
        'actual_closed_result': 'reports/ACTUAL_A1_NATIVE_V5_20261102_215643/CLOSED_RESULT.json',
        'actual_cohort_final': 'reports/ACTUAL_A1_NATIVE_V5_20261102_215643/COHORT_FINAL.json',
        'actual_parent_fetch_report': 'reports/A1_V5_CLOSED_TIMESTAMP_APPCLOSE_DIAGNOSIS_V1.json',
        'sealed_worker': 'source_app_close_semantics_v5/worker_supermimic_bptt_app_close_candidate_v5.py',
        'sealed_adapter_v3': 'source_pose_cache_runtime_adapter_v3/pose_cache_runtime_adapter_v3.py',
        'e3_train': 'discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/train_mod4v1_e3.py',
        'e3_recovery': 'discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/e3_recovery_runtime_v1.py',
        'e3_chassis_pd': 'discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/chassis_pd_training_env.py',
        'e3_chassis_com': 'discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/chassis_com_pose_roundtrip_sdk_adapter.py',
        'w35_chassis_com': 'discovery/reward_command_audit_v1/W35/runtime/isaac/mod4/chassis_com_pose_roundtrip_sdk_adapter.py',
        'sdk_data': 'discovery/sdk_reset_cache_backend_v2/backend/articulation_data.py',
        'warp_buffer': 'discovery/sdk_warp_timestamp_actual_v4/timestamped_buffer_warp.py',
        'torch_buffer': 'discovery/sdk_warp_timestamp_actual_v4/timestamped_buffer.py',
        'launcher': 'discovery/sdk_app_launcher_actual_v6/app_launcher.py',
        'isaacsim_expose_api': 'discovery/sdk_reset_cache_backend_v2/isaacsim/package_init.py',
    }
    rows = [];texts = {}
    for label, relative in specs.items():
        path = PROJECT / relative;raw = path.read_bytes();text = raw.decode('utf-8')
        if path.suffix == '.py': ast.parse(text)
        else: json.loads(text)
        texts[label] = text
        rows.append(dict(label=label, path=str(path), SHA=hashlib.sha256(raw).hexdigest(), bytes=len(raw)))
    assert 'NON_NATIVE_FINITE_TIMESTAMP: _root_link_vel_w' in texts['actual_closed_result']
    assert 'actual application exact class differs' in texts['actual_parent_fetch_report']
    assert "timestamp=-float('inf')" in texts['e3_chassis_com'].replace(' ', '')
    assert "timestamp=-float('inf')" in texts['w35_chassis_com'].replace(' ', '')
    assert 'self.timestamp = -1.0' in texts['warp_buffer']
    assert 'self.timestamp: float = -1.0' in texts['torch_buffer'] or 'timestamp: float = -1.0' in texts['torch_buffer']
    assert 'if self._root_link_vel_w.timestamp < self._sim_timestamp:' in texts['sdk_data']
    assert 'from simulation_app import AppFramework, SimulationApp' in texts['isaacsim_expose_api']
    assert 'from isaacsim import SimulationApp' in texts['launcher']
    receipt = dict(kind='V6_MANUALLY_REVIEWED_SOURCE_EVIDENCE_WITH_EXACT_SMALL_FILE_HASHES_NOT_LIVE_BINDING',
        passed=True, sources=rows,
        historical_V5=dict(observed_error='NON_NATIVE_FINITE_TIMESTAMP: _root_link_vel_w',
            observed_roles=['E3', 'W35'], actual_returncodes=[0, 0], semantic_error_gate_blocked_other_six=True,
            observed_pose_event_counts=dict(installed=0, write_returned=0, install_rejected=1),
            startup_counts_iteration_final_producer_fields=None,
            new_BPTT_zero_is_phase_inference_not_producer_count=True,
            SDK_env_constructed=True, only_explicit_env_reset_reached=False,
            teacher_construction_reached=False, learner_construction_reached=False,
            history_raw_timestamp_python_type=None, history_raw_timestamp_value=None,
            all_own_children_waited_cost_settled_leases_released=True,
            gravity_frame_quaternion_physics_or_skill_failure_proven=False),
        source_chain=dict(original_ChassisCOM_ctor_reset_apply_invalidate=True,
            original_ChassisCOM_native_negative_infinity_stale_write=True,
            Warp_and_Torch_buffer_constructor_default=-1.0,
            SDK_stale_comparison='timestamp < _sim_timestamp',
            source_consistent_explanation_not_historical_raw_value_measurement=True),
        minimal_pose_candidate=dict(SHA='7357827a72a03f6300ce3f7c6da3ad2a05a551480a1aad04a91dbaac4a497e2f',
            bytes=18161, only_native_float_negative_infinity_buffer_sentinel_accepted=True,
            finite_nonnegative_clock_requirement_unchanged=True, JSON_tag_only_no_install_timestamp_normalization=True,
            original_binding_pins_and_after_original_write_eight_stamp_mutation_unchanged=True,
            physical_frame_DR_getter_reset_RNG_gravity_threshold_unchanged=True),
        App_module_source_supported_whitelist=['isaacsim.simulation_app.simulation_app', 'simulation_app.simulation_app'],
        App_exact_class_MRO_full_source_close_definition_pins_still_required=True,
        history_actual_App_module=None, actual_new_native_type_value_App_class_receipt=None,
        actual_SDK_GPU_native_install_steps_originalPT_C_locks_Git_SSH_operations=0)
    target = HERE / 'RUNTIME_SOURCE_EVIDENCE_V6.json'
    with target.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(receipt, stream, ensure_ascii=False, indent=2);stream.write('\n')
    print(json.dumps(dict(passed=True, sources=len(rows), target=str(target),
        SHA=hashlib.sha256(target.read_bytes()).hexdigest(), native_operations=0), ensure_ascii=False))


if __name__ == '__main__': main()
