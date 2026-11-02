"""Reconcile the October 1 shutdown, then resume the already-validated recipe.

Run inside the active task with its Isaac Lab Python. No hardware, reward,
contact, PPO, old checkpoint, or budget authorization is changed here.
"""
from pathlib import Path
import datetime
import fcntl
import json
import os
import re
import subprocess
import sys
import time
import traceback

sys.path.insert(0, str(Path(__file__).resolve().parent))
import supervise_native_floor as m

ROOT = m.ROOT
EXPECTED_CHECKPOINT_SHA = '8fd1100cf8a843531986235757c3922fc400dc5c4b13e95636c21e808f4757d6'


def main():
    lock = (ROOT / 'native_floor_reboot_recovery.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    assert not m.trainers(), 'active trainer exists; refuse recovery'
    for cmd in Path('/proc').glob('[0-9]*/cmdline'):
        try:
            argv = cmd.read_bytes().split(b'\0')
        except OSError:
            continue
        assert not any(a.endswith(b'/supervise_native_floor.py') for a in argv), 'supervisor already running'

    b = m.budget_state()
    old_status = json.loads((ROOT / 'status.json').read_text())
    ck = m.latest(ROOT / 'logs')
    info = m.checkpoint(ck)
    assert info['sha256'] == EXPECTED_CHECKPOINT_SHA and info['iteration_stored'] == 8700
    folder = ck.parent
    manifest = json.loads((folder / 'run_manifest.json').read_text())
    cfg = json.loads((m.CODE / 'env.json').read_text())
    assert all(str(v) == str(manifest['env'].get(k)) for k, v in cfg.items()), 'runtime configuration changed'
    m.runtime_env()
    usd = Path(manifest['robot_usd'])
    verified = {}
    for name, expected in manifest['src_sha256'].items():
        path = usd if name == 'robot.usd' else (usd.parent / name if name == 'import_contract.json' else m.CODE / name)
        actual = m.sha(path)
        assert actual == expected, 'production source or asset drift: ' + str(path)
        verified[str(path)] = actual
    auxiliary = json.loads((folder / 'native_floor_source_freeze.json').read_text())
    for name, expected in auxiliary['sha256'].items():
        actual = m.sha(m.CODE / name)
        assert actual == expected, 'auxiliary source drift: ' + name
        verified[str(m.CODE / name)] = actual

    assert json.loads((m.REPORTS / 'native_floor_20k_ppo.json').read_text())['pass']
    assert json.loads((m.REPORTS / 'native_floor_20k_physics_acceptance.json').read_text())['physical_smoke_pass']
    assert m.physics_gate(json.loads((m.REPORTS / 'native_floor_8648_baseline15s.json').read_text()))
    active = b.get('active_segment')
    assert active and active['pid'] == 50274 and active['kind'] == 'production'
    previous_log = Path(active['log'])
    text = previous_log.read_text(errors='replace')
    iterations = re.findall(r'Learning iteration\s+(\d+)/', text)
    last_logged_iteration = int(iterations[-1])
    last_log_epoch = previous_log.stat().st_mtime
    last_accounted = float(active['accounted_through_epoch'])

    journal = subprocess.run(['journalctl', '-b', '-1', '-n', '500', '--no-pager', '-o', 'json'],
                             capture_output=True, text=True, check=True)
    entries = [json.loads(line) for line in journal.stdout.splitlines() if line.strip()]
    shutdown = [(int(e['__REALTIME_TIMESTAMP']) / 1e6, e.get('MESSAGE', '')) for e in entries
                if isinstance(e.get('MESSAGE'), str) and 'Reached target poweroff.target' in e['MESSAGE']]
    assert shutdown, 'no previous-boot poweroff evidence; cannot reconcile automatically'
    end_epoch = max(t for t, _ in shutdown)
    assert last_accounted <= last_log_epoch <= end_epoch
    assert end_epoch - last_log_epoch < 30, 'shutdown does not match latest training log'
    assert end_epoch - last_accounted < 30, 'unaccounted training interval too large'
    boot_epoch = time.time() - float(Path('/proc/uptime').read_text().split()[0])
    assert end_epoch < boot_epoch

    receipt = ROOT / 'reports/REBOOT_RECOVERY_20261001.json'
    assert not receipt.exists(), 'recovery already reconciled; inspect status before another launch'
    snapshot = ROOT / 'reports/TRAINING_BUDGET_BEFORE_REBOOT_RECONCILIATION_20261001.json'
    assert not snapshot.exists()
    m.atomic_json(snapshot, b)
    m.atomic_json(ROOT / 'reports/STATUS_BEFORE_REBOOT_RECOVERY_20261001.json', old_status)
    delta = end_epoch - last_accounted
    charged = float(b['charged_training_seconds']) + delta
    segment = dict(active)
    segment.update(ended_epoch=end_epoch, accounted_through_epoch=end_epoch,
                   end_reason='system poweroff; upper bound from previous boot journal',
                   last_training_log_epoch=last_log_epoch,
                   accounting_uncertainty_seconds=end_epoch - last_log_epoch)
    b.setdefault('completed_segments', []).append(segment)
    b['active_segment'] = None
    b['charged_training_seconds'] = charged
    b['remaining_training_seconds'] = max(0., 36000 - charged)
    b['deadline_before_reboot_epoch'] = b.get('deadline_epoch')
    b['deadline_epoch'] = None
    b['reconciliation_report'] = str(receipt)
    m.atomic_json(m.BUDGET_PATH, b)
    m.atomic_json(receipt, {
        'reconciled_at_epoch': time.time(), 'previous_poweroff_epoch': end_epoch,
        'current_boot_epoch_estimate': boot_epoch, 'resume_checkpoint': info,
        'last_logged_iteration': last_logged_iteration,
        'unsaved_iteration_span': [info['iteration_stored'] + 1, last_logged_iteration],
        'charged_training_seconds': charged, 'remaining_training_seconds': b['remaining_training_seconds'],
        'incremental_shutdown_tail_seconds': delta,
        'shutdown_tail_uncertainty_seconds': end_epoch - last_log_epoch,
        'accounting_method': 'Existing charged time plus shutdown tail up to journal poweroff; offline/reconnection time excluded. Tail is a conservative upper bound, not exact trainer exit time.',
        'config_and_source_hashes_verified': verified,
        'cached_preflight_reused': True, 'new_ppo_preflight_performed': False,
        'actor_critic_optimizer_std_iteration_restored': True,
        'physics_reward_ppo_changes': False, 'authorized_total_seconds': 36000,
        'contact_integrated_and_eager5ms_enabled': True,
        'time_zone': 'Asia/Shanghai', 'no_automatic_2m_dr_rough_promotion': True,
    })
    print('RECOVERY_ACCEPTED', json.dumps({'checkpoint': str(ck), 'remaining_seconds': b['remaining_training_seconds']}), flush=True)
    m.main()


if __name__ == '__main__':
    try:
        main()
    except BaseException:
        m.status(stage='attention_required', error=traceback.format_exc())
        raise
