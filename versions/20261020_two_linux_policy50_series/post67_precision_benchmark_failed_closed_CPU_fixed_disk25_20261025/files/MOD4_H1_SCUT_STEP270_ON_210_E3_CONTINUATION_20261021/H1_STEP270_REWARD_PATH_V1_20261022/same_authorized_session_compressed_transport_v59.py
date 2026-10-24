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
        'collect_pair31_missing_after_local_compressed_session_CPU_V120_once.py',
        'relocate_selected_pair_closed_forensics_unused_once.py',
        'read_E3_resource_only_after_actual_H1_closed_CPU_once.py',
        'deploy_selected_pair_unused_once.py',
        'deploy_selected_H1_only_unused_once.py',
        'collect_selected_pair_first_PPO_unused_once.py',
        'collect_selected_H1_first_PPO_unused_once.py',
        'collect_selected_pair_finals_unused_once.py',
        'extract_latest65_retained_motion_CPU_unused_once.py',
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
    module, previous = install()
    original_argv = sys.argv
    sys.argv = [str(target)]
    try:
        runpy.run_path(str(target), run_name='__main__')
    finally:
        module.SESSION = previous
        sys.argv = original_argv


if __name__ == '__main__':
    main()
