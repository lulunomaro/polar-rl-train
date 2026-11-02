"""One-use recovery of a completed, orphaned two-round PPO preflight.

Do not rerun the handover or extend the canonical budget. No production policy
may be taken from preflight_logs. The supervisor is resumed separately.
"""
from pathlib import Path
import fcntl
import json
import re
import sys
import time

ROOT = Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002')
CODE = ROOT / 'isaac/mod4'
REPORTS = ROOT / 'reports'
CANONICAL = Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json')
sys.path.insert(0, str(CODE))
import supervise_spin_rate as rate
base = rate.base


def main():
    receipt_path = REPORTS / 'ARCHIVAL_FAILURE_RECOVERY.json'
    assert not receipt_path.exists(), 'Recovery already recorded; inspect receipt'
    assert not base.trainers() and not rate.helpers.active_processes(rate.PROBES)
    assert not Path('/proc/1524610').exists() and not Path('/proc/1553547').exists()
    rate.helpers.acquire(ROOT / 'rate_supervisor.lock')
    rate.helpers.acquire(CANONICAL.parent / 'native_floor_supervisor.lock')
    ledger = base.budget_state()
    assert ledger['owner_root'] == str(ROOT)
    segment = ledger['active_segment']
    assert segment['pid'] == 1553547 and segment['kind'] == 'rate3_preflight'
    log = Path(segment['log'])
    text = log.read_text(errors='replace')
    times = [float(v) for v in re.findall(r'Iteration time:\s*([0-9.]+)s', text)]
    assert len(times) == 2 and 'SimulationContext cleared' in text
    assert 'Traceback (most recent call last)' not in text
    ck = base.latest(ROOT / 'preflight_logs')
    info = base.checkpoint(ck)
    complete = rate.read(ck.parent / 'latest_complete.json')
    manifest = rate.read(ck.parent / 'run_manifest.json')
    source = Path(rate.read(REPORTS / 'handover_completed.json')['source_checkpoint']['path'])
    source_info = base.checkpoint(source)
    assert source_info['iteration_stored'] == 14200 and info['iteration_stored'] == 14201
    assert complete['pid'] == 1553547 and complete['checkpoint'] == str(ck)
    assert manifest['start_iteration'] == 14200
    assert manifest['env']['RM_KEEP_STD'] == '1'
    assert manifest['env']['RM_MILD_DR_PROFILE'] == 'white_v1'
    assert float(manifest['env']['RM_SPIN_MAX_RAD_S']) == 3.
    # Bounded upper estimate: final app-clear log timestamp plus 0.5 seconds.
    # Exclude all later diagnosis/SSH downtime; the lost exit code is not invented.
    ended = log.stat().st_mtime + .5
    assert segment['accounted_through_epoch'] <= ended < time.time()
    assert ended >= complete['saved_at']
    tail = ended - segment['accounted_through_epoch']
    assert 0 <= tail < 30, 'Unexpected tail requires independent audit'
    base.atomic_json(REPORTS / 'ledger_before_archival_recovery.json', ledger)
    base.atomic_json(REPORTS / 'status_before_archival_recovery.json', rate.read(ROOT / 'status.json'))
    charged_before = ledger['charged_training_seconds']
    segment.update(ended_epoch=ended, accounted_through_epoch=ended,
                   reconciled_by='ARCHIVAL_FAILURE_RECOVERY', exit_code_unavailable=True,
                   last_app_clear_upper_uncertainty_s=.5)
    ledger.setdefault('completed_segments', []).append(segment)
    ledger['active_segment'] = None
    ledger['charged_training_seconds'] += tail
    ledger['remaining_training_seconds'] = ledger['authorized_training_seconds'] - ledger['charged_training_seconds']
    base.atomic_json(CANONICAL, ledger)
    base.atomic_json(REPORTS / 'PPO_PREFLIGHT_128.json', {
        'pass': True, 'discarded_weights': info, 'production_source': str(source),
        'charged_same_ledger': True, 'iteration_time_s': times, 'weights_discarded': True,
        'exit_code_unavailable': True, 'evidence': 'Two iteration logs, finite complete checkpoint, app cleared, child exited',
        'recovered_after_auxiliary_archival_error': True})
    receipt = {'error': 'SameFileError in absolute asset source archival; no physics/reward/PPO change',
               'fixed_snapshot_paths': 'Absolute assets copied under snapshot/_external/hash/name',
               'preflight_weights_discarded': info, 'production_source': source_info,
               'charged_before_s': charged_before, 'tail_charged_s': tail,
               'charged_after_s': ledger['charged_training_seconds'],
               'remaining_effective_s': ledger['remaining_training_seconds'],
               'ended_epoch_upper_estimate': ended, 'end_uncertainty_s': .5,
               'diagnosis_downtime_not_charged_s': time.time() - ended,
               'budget_added': False, 'authorized_effective_s': ledger['authorized_training_seconds']}
    base.atomic_json(receipt_path, receipt)
    print(json.dumps(receipt))


if __name__ == '__main__':
    main()
