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
