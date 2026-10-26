"""Read the same authorized historical tool input after local zstd compaction.

No new credential selection, disk extraction, remote policy, or host-pin change.
The original recovery function and its filtering stay intact.
"""
from pathlib import Path
from compression import zstd
import importlib, runpy, sys

B = Path(__file__).resolve().parent
W = B.parent.parent
ORIGINAL = Path('C:/Users/lulu/.codex/sessions/2026/09/07/rollout-2026-09-07T12-43-21-01a07a2d-9036-7531-a012-692df9f56353.jsonl')


class SameCompressedSession:
    def open(self, *, encoding):
        assert encoding == 'utf8'
        return zstd.open(str(ORIGINAL) + '.zst', 'rt', encoding=encoding)


def install():
    sys.path.insert(0, str(W / 'RM2026_TERRAIN_AUDIT_20261009'))
    module = importlib.import_module('reuse_authorized_session_transport')
    assert module.SESSION == ORIGINAL
    assert not ORIGINAL.exists() and Path(str(ORIGINAL) + '.zst').is_file()
    previous = module.SESSION
    module.SESSION = SameCompressedSession()
    return module, previous


def main():
    target = Path(sys.argv[1]).resolve()
    assert target.is_relative_to(B.parent.resolve())
    assert target.name in {
        'install_dual72_V85_source_SDK_native_CPU_only_UNUSED.py',
        'read_current_original_account_and_dual72_for_V85_new_request_once.py',
        'stage_new_E2_supermimic_source_only72_missing_once.py',
        'stage_single4090_needed_runtime_to72_before_disconnect_unused_once.py',
        'observe_mixed84_baselines_native_first_finite_V2_UNUSED.py',
        'relocate_missing_closed_NPZ_for84_TLS_V5_v2_unused_once.py',
        'relocate_minimal_closed82Q_83B_NPZ_for84_TLS_V5_unused_once.py',
        'read_fresh83B_closed_disk_before_mixed84_unused_once.py',
        'deploy_mixed84_original_writer_TEMPLATE.py',
        'observe_mixed84_baselines_native_first_finite_TEMPLATE.py',
        'collect_mixed84_finals_original_cost_TEMPLATE.py',
        'resume_only_two_missing_Fudan_assets_pinned_mirror_and_CPU_v3_unused_once.py',
        'resume_missing_Fudan_reference_assets_raw_transport_and_CPU_v2_unused_once.py',
        'prepare72_and_capture_pinned_Fudan_jump_reference_CPU_finite_unused_once.py',
        'extract_closed83B_last_two_saved_prefixes_CPU_unused_once.py',
        'collect_closed83B_landing_event_journal_small_CPU_unused_once.py',
        'deploy_actual_three83B_normal_experts_qualified82Q_80_original_writer_unused_once.py',
        'collect_actual_three83B_normal_experts_first_PPO_finite_unused_once.py',
        'collect_actual_three83B_finals_original_cost_unused_once.py',

        'read_actual81o_failed_method_error_and_original_terminal_cost_unused_once.py',
        'deploy_actual_three83_normal_experts_qualified82Q_80_original_writer_unused_once.py',
        'collect_actual_three83_normal_experts_first_PPO_finite_unused_once.py',
        'collect_actual_three83_finals_original_cost_unused_once.py',
        'relocate_minimal_closed81O_82Q_NPZ_for83_TLS_V5_unused_once.py',

        'collect_last82q_native_complete_preupdate_execution_evidence_missing_only_unused_once.py',
        'collect_actual82q_native_policy_first_20min_finite_v2_unused_once.py',
        'collect_actual82q_H1_PPO_native_method_E3_original_cost_unused_once.py',
        'deploy_actual82q_checkpoint_context_fixed_H1_method_original_writer_unused_once.py',
        'collect_actual82q_PPO_and_native_H1_policy_first_finite_unused_once.py',

        'relocate_minimal_closed80_79c_NPZ_for82Q_same_approved_TLS_V5_unused_once.py',
        'read_missing82p_preGO_resource_rejection_and_installed_CPU_outputs_unused_once.py',
        'deploy_actual82p_checkpoint_context_fixed_H1_method_original_writer_unused_once.py',
        'collect_actual82p_PPO_and_native_H1_policy_first_finite_unused_once.py',

        'read_missing81o_healthy_PPO_identities_and_all_original_GO_clocks_unused_once.py',
        'collect_closed81o_healthy_FINALs_failed_method_original_all_cost_unused_once.py',
        'deploy_actual_mixed81o_H1_method_original_writer_unused_once.py',
        'collect_actual_mixed81o_PPO_and_H1_native_policy_first_finite_unused_once.py',
        'deploy_actual_mixed81n_H1_method_original_writer_unused_once.py',
        'collect_actual_mixed81n_PPO_and_H1_native_policy_first_finite_unused_once.py',
        'collect_actual_mixed81m_finals_original_cost_unused_once.py',
        'run_pinned_single4090_method_test_original_owner_finite_unused_once.py',
        'deploy_actual_three_experts81_same_V8_journal_original_writer_unused_once.py',
        'collect_three_experts81_same_V8_journal_first_PPO_finite_unused_once.py',
        'collect_actual_three81_finals_original_cost_unused_once.py',
        'collect_pair31_missing_after_local_compressed_session_CPU_V120_once.py',
        'relocate_selected_pair_closed_forensics_unused_once.py',
        'read_E3_resource_only_after_actual_H1_closed_CPU_once.py',
        'deploy_selected_pair_unused_once.py',
        'deploy_selected_H1_only_unused_once.py',
        'collect_selected_pair_first_PPO_unused_once.py',
        'collect_selected_H1_first_PPO_unused_once.py',
        'collect_selected_pair_finals_unused_once.py',
        'extract_latest65_retained_motion_CPU_unused_once.py',
        'extract_latest67_retained_motion_CPU_unused_once.py',
        'read_closed_precision_only_artifacts_for_new_scope_plan_unused_once.py',
        'audit_new_authorized_replay_waste_210_72_metadata_unused_once.py',
        'apply_reviewed_obsolete_replay_prune_batch1_unused_once.py',
        'apply_reviewed_obsolete_replay_prune_batch1_missing_only_v2_unused_once.py',
        'apply_reviewed_obsolete_replay_prune_batch2_missing_only_unused_once.py',
        'apply_reviewed_obsolete_replay_and_closed_cache_batch3_unused_once.py',
        'read_M4_missing_half_E3_resource_unused_once.py',
        'deploy_M4_missing_half_pair_unused_once.py',
        'read_M4_missing_half_own_GO_identity_progress_unused_once.py',
        'collect_M4_missing_half_text_cost_allout_unused_once.py',
        'read_current_actual_reward_manager_V6A_source_unused_once.py',
        'read_sagittal_V6A_next68_E3_resource_unused_once.py',
        'deploy_sagittal_V6A_next68_pair_unused_once.py',
        'collect_sagittal_V6A_next68_first_PPO_unused_once.py',
        'prepare_whole_MOE_T2Z_host72_source_unused_once.py',
        'run_whole_MOE_T2Z_host72_finite_preparation_phase.py',
        'run_whole_MOE_T2Z_reviewed_stage_finite.py',
        'run_verified_public_cache_weight_batch_finite.py',
        'run_single4090_quantized_Q8_only_finite_batch.py',
        'relay_exact_Q8_only_Windows_to72_finite_batch.py',
        'relay_exact_Q8_only_parallel_ranges_to72_finite_v2.py',
        'read_verified_Q8_header_and_clear_cancelled_own_partial_once.py',
        'read_current68_owner_H1_original_account_after_network_retry_once.py',
        'read_two_original_hosts_strict_SSH_human_now_once.py',
        'collect_missing_Q8_producer_text_receipts_only_once.py',
        'read_user_forwarded210_4090_strict_hostkey_once.py',
        'read_current68_after_user_forwarded_route_restored_once.py',
        'inspect_exact68_original_owner_handoff_capabilities_once.py',
        'inspect_exact68_owner_missing_psutil_legacy_v2_once.py',
        'relay_exact68_saved_terminals_to_original_live_writer_once.py',
        'collect_closed68_after_actual_original_handoff_once.py',
        'read69_E3_resource_and_forwarded_control_prerequisites_once.py',
        'prepare_isolated72_forwarded_owner_control_dependencies_once.py',
        'verify72_pinned_owner_SSH_control_channel_CPU_once.py',
        'deploy_combined69_through_pinned_forwarded_route_once.py',
        'deploy_combined69b_root_path_invocation_fixed_once.py',
        'deploy_combined69c_exact_network_scope_once.py',
        'deploy_combined69d_nested_runtime_report_fixed_once.py',
        'collect69d_first_PPO_over_forwarded_route_once.py',
        'collect_current69d_finals_original_cost_unused_once.py',
        'extract_closed69d_last_two_saved_prefixes_CPU_unused_once.py',
        'read_current69d_timing_snapshot_for_human_once.py',
        'deploy_same_optimized70_pinned_route_once.py',
        'collect70_first_PPO_pinned_route_once.py',
        'collect_current70_finals_original_cost_unused_once.py',
        'extract_closed70_last_two_saved_prefixes_CPU_unused_once.py',
        'deploy_same_optimized71_network_fixed_once.py',
        'collect71_first_PPO_pinned_route_once.py',
        'collect_current71_finals_original_cost_unused_once.py',
        'read_three4090_nonidentifying_utilization_for_human_once.py',
        'read_authorized_third_GPU_and_original_locks_once.py',
        'install_E2_on_third72_CPU_only_unused_once.py',
        'deploy_actual_three_experts72_original_writer_once.py',
        'collect_three_experts72_first_PPO_finite_once.py',
        'collect_actual_three72_finals_original_cost_unused_once.py',
        'collect_actual_three73_finals_original_cost_unused_once.py',
        'deploy_actual_three_experts73b_original_writer_unused_once.py',
        'collect_three_experts73b_first_PPO_finite_unused_once.py',
        'collect_actual_three73b_finals_original_cost_unused_once.py',
        'extract_closed73b_last_two_saved_prefixes_CPU_unused_once.py',
        'deploy_actual_three_experts74_original_writer_unused_once.py',
        'collect_three_experts74_first_PPO_finite_unused_once.py',
        'collect_actual_three74_finals_original_cost_unused_once.py',
        'deploy_actual_three_experts74b_original_writer_unused_once.py',
        'collect_three_experts74b_first_PPO_finite_unused_once.py',
        'collect_actual_three74b_finals_original_cost_unused_once.py',
        'extract_closed74b_last_two_saved_prefixes_CPU_unused_once.py',
        'deploy_actual_three_experts75_H1_V8_original_writer_unused_once.py',
        'collect_three_experts75_V8_first_PPO_finite_V2_unused_once.py',
        'collect_actual_three75_finals_original_cost_unused_once.py',
        'extract_closed75_last_two_saved_prefixes_CPU_unused_once.py',
        'deploy_actual_three_experts76_same_V8_original_writer_unused_once.py',
        'collect_three_experts76_same_V8_first_PPO_finite_unused_once.py',
        'collect_actual_three76_finals_original_cost_unused_once.py',
        'extract_closed76_last_two_saved_prefixes_CPU_unused_once.py',
        'deploy_actual_three_experts77_same_V8_original_writer_unused_once.py',
        'collect_three_experts77_same_V8_first_PPO_finite_unused_once.py',
        'collect_actual_three77_finals_original_cost_unused_once.py',
        'extract_closed77_last_two_saved_prefixes_CPU_unused_once.py',
        'deploy_actual_three_experts78_V8_lifetime_diag_original_writer_unused_once.py',
        'collect_three_experts78_V8_lifetime_diag_first_PPO_finite_unused_once.py',
        'collect_actual_three78_finals_original_cost_unused_once.py',
        'extract_closed78_last_two_saved_prefixes_CPU_unused_once.py',
        'deploy_actual_three_experts79_same_V8_lifetime_diag_original_writer_unused_once.py',
        'collect_three_experts79_same_V8_lifetime_diag_first_PPO_finite_unused_once.py',
        'collect_actual_three79_finals_original_cost_unused_once.py',
        'deploy_actual_three_experts79c_same_V8_exact_metadata_original_writer_unused_once.py',
        'collect_three_experts79c_same_V8_lifetime_diag_first_PPO_finite_unused_once.py',
        'collect_actual_three79c_finals_original_cost_unused_once.py',
        'extract_closed79c_last_two_saved_prefixes_CPU_unused_once.py',
        'deploy_actual_three_experts80_V8_readonly_landing_journal_original_writer_unused_once.py',
        'collect_three_experts80_readonly_landing_journal_first_PPO_finite_unused_once.py',
        'collect_actual_three80_finals_original_cost_unused_once.py',
        'collect_closed80_landing_event_journal_small_CPU_unused_once.py',




        'extract_closed72_last_two_saved_prefixes_CPU_unused_once.py',
        'deploy_actual_three_experts73_original_writer_unused_once.py',
        'collect_three_experts73_first_PPO_finite_unused_once.py',
        'read_exact_preparation_network_and_current210_reachability_unused_once.py',
        'read_current68_E3_own_state_and_pinned_weight_mirror_CPU_once.py',
        'request_current68_normal_fullsave_for_sampling_optimization_unused_once.py',
        'collect_current68_requested_fullsave_original_cost_allout_unused_once.py',
        'read_actual_delayed_leg_action_SDK_source_unused_once.py',
        'relocate_missing_current66_old26_30_after_closed66_TLS_V5_unused_once.py',
        'relocate_missing_current67_old30_after_closed67_TLS_V5_unused_once.py',
        'read_benchmark_own_GO_identity_and_progress_unused_once.py',
        'read_E3_benchmark_preexec_identity_schema_corrected_V2_unused_once.py',
        'collect_benchmark_text_cost_and_allout_unused_once.py',
        'collect_benchmark_profile_then_text_cost_allout_V2_unused_once.py',
        'read_actual_RSL_logger_API_and_closed_benchmark_resources_unused_once.py',
        'read_own_failed_benchmark_cache_metadata_unused_once.py',
        'read_own_failed_benchmark_missing_data_home_metadata_unused_once.py',
        'read_exact_closed67_preupdate_metadata_for_permission_unused_once.py',
        'relocate_approved_two_preupdate_and_cleanup_own_benchmark_cache_unused_once.py',
        'read_failed66_listener_no_nodes_actual_out_V2_once.py',
        'read_failed66_listener_no_nodes_actual_out_once.py',
        'relocate_missing_current65_old63_26_after_closed65_TLS_V5_once.py',
        'relocate_missing_current64_old63_26_after_closed64_TLS_V5_once.py',
        'relocate_failed64_copy_headroom_missing_only_once.py',
        'read_failed64_preowner_no_GO_allout_once.py',
        'relocate_missing_closed62_26_after_closed63_NINTH_TLS_V2_once.py',
        'relocate_missing_closed62_26_after_closed63_NINTH_TLS_once.py',
        'relocate_closed63_after_ninth_extension_unused_once.py',
        'probe_original_budget_ninth_boundary_V2_once.py',
        'probe_original_budget_ninth_boundary_once.py',
        'apply_ninth_extension_original_two_locks_once.py',
        'relocate_missing_closed61_26_after_closed62_TLS_V4_once.py',
        'relocate_missing_closed60_36_after_closed61_TLS_V4_once.py',
        'relocate_missing_closed59_39_after_closed60_TLS_V4_once.py',
        'relocate_missing_closed58_39_after_closed59_TLS_V4_once.py',
        'relocate_missing_closed56_57_after_closed58_TLS_V4_once.py',
        'relocate_missing_closed55_56_after_closed57_TLS_V4_once.py',
        'relocate_missing_closed54_53_after_closed56_TLS_V4_once.py',
        'relocate_missing_closed52_53_after_closed55_TLS_V4_once.py',
        'collect_selected_H1_final_unused_once.py',
        'relocate_missing_closed_pair11_after_closed31_TLS_V120_once.py',
        'relocate_missing_closed_pair11_after_closed32_TLS_REPLAY_V2_once.py',
        'relocate_selected_H1_closed_forensics_unused_once.py',
        'relocate_missing_closed_pair11_after_closed36_TLS_LEG_TUCK_once.py',
        'extract_new_closed36_leg_tuck_recorded_motion_CPU_bounded_once.py',
        'read_failed38_preowner_no_GO_allout_once.py',
        'collect_pair39_missing_GO_PPO_after_tuck_weight_reader_v3_once.py',
        'relocate_missing_closed32_after_closed39_TLS_TUCK_V3_once.py',
        'relocate_missing_closed30_after_closed39_TLS_TUCK_V3_once.py',
        'extract_new_closed39_actual_tuck_selected_motion_CPU_bounded_once.py','relocate_missing_closed36_28_after_closed41_TLS_V4_once.py','relocate_missing_closed39_41_after_closed42_TLS_V4_once.py','read_two_hosts_storage_waste_metadata_authorized_once.py','read_missing_cache_metadata_authorized_once.py','cleanup_exact_rebuildable_caches_authorized_once.py',
        'collect_closed43_missing_text_and_final_after_log_mismatch_once.py',
        'probe_moe_4090_eval_environment_unused_once.py',
        'read_saved_4090_body_xbody_pose_unused_once.py',
        'read_missing_saved_pose_velocity_frame_V2_unused_once.py',
        'deploy_confirmed_series_baseline_4090_unused_once.py',
        'deploy_small_curb_contact_4090_unused_once.py',
        'deploy_small_curb_contact_V2_4090_unused_once.py',
        'deploy_small_curb_contact_V3_4090_unused_once.py',
        'deploy_small_curb_contact_V4_4090_unused_once.py',
        'deploy_small_curb_contact_V5_4090_unused_once.py',
        'relocate_missing_closed48_44_after_closed49_TLS_V4_once.py',
        'diagnose_preowner_space_after_failed50_unused_once.py',
        'relocate_missing_install_headroom_after_failed50_TLS_V4_once.py',
        'relocate_missing_closed49_44_after_closed51_TLS_V4_once.py',
        'relocate_missing_closed43_45_after_closed52_TLS_V4_once.py',
        'relocate_missing_closed42_47_after_closed53_TLS_V4_once.py',
        'relocate_missing_closed51_42_after_closed54_TLS_V4_once.py',
        'deploy_moe_router_matched_4090_unused_once.py',
        'relocate_missing_closed46_45_after_closed48_TLS_V4_once.py',
    }
    # Latest human scope: one quantized model, never the old full13 plan.
    assert target.name != 'run_verified_public_cache_weight_batch_finite.py', 'Old full-precision13 download cancelled by latest human instruction'
    if target.name == 'run_whole_MOE_T2Z_reviewed_stage_finite.py':
        assert len(sys.argv)==3 and not sys.argv[2].startswith('download') and sys.argv[2]!='verify-final', 'Old full13 download/verification scope cancelled'
    module, previous = install()
    original_argv = sys.argv
    if target.name == 'run_whole_MOE_T2Z_host72_finite_preparation_phase.py':
        assert len(original_argv) == 3 and original_argv[2] in {'bootstrap','torch','requirements','check'}
        sys.argv = [str(target), original_argv[2]]
    elif target.name == 'run_whole_MOE_T2Z_reviewed_stage_finite.py':
        allowed={'stage-method','cpu-imports','method-tests','verify-final'} | {'download'+str(i).zfill(2) for i in range(1,21)}
        assert len(original_argv)==3 and original_argv[2] in allowed
        sys.argv=[str(target),original_argv[2]]
    elif target.name=='run_verified_public_cache_weight_batch_finite.py':
        assert len(original_argv)==3 and original_argv[2] in {str(i).zfill(2) for i in range(1,21)}
        sys.argv=[str(target),original_argv[2]]
    elif target.name in {'run_single4090_quantized_Q8_only_finite_batch.py','relay_exact_Q8_only_Windows_to72_finite_batch.py','relay_exact_Q8_only_parallel_ranges_to72_finite_v2.py'}:
        assert len(original_argv)==3 and original_argv[2] in {str(i).zfill(2) for i in range(1,11)}
        sys.argv=[str(target),original_argv[2]]
    else:
        sys.argv = [str(target)]
    try:
        runpy.run_path(str(target), run_name='__main__')
    finally:
        module.SESSION = previous
        sys.argv = original_argv


if __name__ == '__main__':
    main()
