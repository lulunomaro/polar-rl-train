"""Read a genuinely closed first gate scope once; never launch, signal or account.

Large raw rollouts stay on their actual durable host. Their complete index and
actual file sizes are captured here; independent CPU trace consumption follows.
This preparation does not assert that a future final exists or is admitted.
"""
from pathlib import Path
import hashlib, json, shlex, sys, time

D = Path(__file__).resolve().parent
W = D.parent
sys.path.insert(0, str(W / 'MOD4_LINUX_WAVE50_BODYFRAME_RESET_INTEGRATION_20261014'))
import transport_bodyframe_root_owned as transport

ROOT = '/mnt/mod4_linux_durable_20261013/MOD4_S4_E0_WAVE35_FIRST_SUPPORTED_GATE45M_V1_20261015'
SOURCE = '0681d5c0e901aba5ceb96ec8504bc6beb4d30c87ee73dbc0fd652d3011ff02ce'


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def remote_program():
    return 'ROOT = ' + repr(ROOT) + '\nSOURCE = ' + repr(SOURCE) + '\n' + r'''
from pathlib import Path
import fcntl, hashlib, json, psutil, time
r = Path(ROOT); a = r / 'learning_logs'
def read(name): return json.loads((r / name).read_bytes())
def sha(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda: f.read(8 * 1024 * 1024), b''): h.update(b)
    return h.hexdigest()
def alive(row):
    try: return psutil.Process(row['pid']).create_time() == row['created']
    except psutil.NoSuchProcess: return False
required = ['PARENT_IDENTITY_ACTUAL.json', 'DISPATCH_ACTUAL.json',
    'PARENT_EXIT_ACTUAL.json', 'GUARDIAN_EXIT_ACTUAL.json',
    'CHILD_EXIT_AND_UNIQUE_COST_ACTUAL.json', 'FORMAL_COMPLETE_REVIEW_READY_ACTUAL.json']
assert all((r / name).is_file() for name in required), 'Own final/exit is pending; no collection admitted'
assert not (r / 'PARENT_ORIGINAL_ERROR.json').exists()
assert not (a / 'S4_FORMAL_ORIGINAL_ERROR.json').exists()
owner = read('PARENT_IDENTITY_ACTUAL.json'); dispatch = read('DISPATCH_ACTUAL.json')
assert not alive(owner) and not alive(dispatch['child'])
exit_record = read('PARENT_EXIT_ACTUAL.json')
assert exit_record['passed'] is True and exit_record['own_locks_released'] is True
assert exit_record['original_unique_cost_settled'] is True
child_exit = read('CHILD_EXIT_AND_UNIQUE_COST_ACTUAL.json')
assert child_exit['returncode'] == 0 and child_exit['child_actually_absent'] is True
assert child_exit['charged_once'] is True
own_scripts = {str(r / 's4_first_supported_gate_formal_parent_v2.py'),
               str(r / 's4_first_supported_gate_formal_worker_v2.py')}
live = []
for p in psutil.process_iter(['pid', 'create_time', 'cmdline']):
    try:
        if own_scripts.intersection(p.info['cmdline'] or []): live.append(p.info)
    except psutil.NoSuchProcess: pass
assert not live, ('Own parent/guardian/worker still present', live)
budget = Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json')
ledger_raw = budget.read_bytes(); ledger = json.loads(ledger_raw)
assert ledger['active_segment'] is None and ledger['authorized_training_seconds'] == 1188000
assert len(ledger['budget_extensions']) == 7
assert ledger['budget_extensions'][-1]['extension_id'] == 'USER_ADD100H_20261011_7TH'
kind = child_exit['unique_segment_kind']
segments = [v for v in ledger['completed_segments'] if v['kind'] == kind]
assert len(segments) == 1
segment = segments[0]
assert segment['owner_parent_pid'] == owner['pid'] and segment['source_SHA'] == SOURCE
assert segment['ended_epoch'] == segment['accounted_through_epoch']
locks = []
for p in (budget.parent / 'native_floor_supervisor.lock',
          Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
    with p.open('r+b') as f:
        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        fcntl.flock(f, fcntl.LOCK_UN)
    locks.append(dict(path=str(p), held=False))
formal = read('FORMAL_COMPLETE_REVIEW_READY_ACTUAL.json')
final = read('learning_logs/S4_FORMAL_FINAL_ACTUAL.json')
assert formal['passed'] is True and formal['final'] == final and final['passed'] is True
assert final['source_SHA'] == SOURCE and final['updates'] > 0
assert final['complete_controls'] == final['updates'] * 24
assert final['callbacks'] == final['complete_controls'] * 4
ck = Path(final['own_checkpoint']); assert ck.parent == a and sha(ck) == final['own_checkpoint_SHA']
manifest = read('S4_FIRST_FORMAL_ACTUAL_MANIFEST.json')
assert manifest['source_SHA'] == SOURCE and manifest['max_learning_window_seconds'] == 2700
for name, h in manifest['sourcefreeze'].items(): assert sha(r / name) == h, name
assert sha(manifest['source_path']) == SOURCE
index = read('learning_logs/S4_GATE_FULL_ROLLOUT_INDEX_ACTUAL.json')
assert index['source_SHA'] == SOURCE and len(index['rows']) >= final['updates']
for i, row in enumerate(index['rows']):
    assert row['index'] == i and Path(row['path']).stat().st_size == row['bytes']
    assert row['source_SHA'] == SOURCE
assert all(row['optimizer_update_complete'] is True for row in index['rows'][:final['updates']])
retention = read('learning_logs/RETENTION_COMMAND_ACTUAL.json')
retention_files = []
for name in retention['trace_files']:
    p = a / name
    assert p.parent == a and p.is_file()
    retention_files.append(dict(path=str(p), bytes=p.stat().st_size,
        sha256=None, SHA_not_yet_independently_consumed=True))
files = []
paths = {ck, *(r.glob('*.json')), *(a.glob('*.json'))}
for p in sorted(paths):
    assert p == ck or p.stat().st_size < 8000000
    files.append(dict(path=str(p), relative=str(p.relative_to(r)),
        bytes=p.stat().st_size, sha256=sha(p)))
print(json.dumps(dict(epoch=time.time(), root=ROOT, files=files,
    final=final, source_SHA=SOURCE, actual_parent_guardian_child_absent=True,
    parent_exit=exit_record, child_exit=child_exit, actual_two_fcntl_free=locks,
    unique_completed_segment=segment,
    canonical_readonly_snapshot=dict(sha256=hashlib.sha256(ledger_raw).hexdigest(),
        active=None, charged=ledger['charged_training_seconds'], remaining=ledger['remaining_training_seconds']),
    sourcefreeze_all_actual_file_SHA_verified=len(manifest['sourcefreeze']),
    gate_rollout_index=index, retention_raw_files=retention_files,
    large_raw_remote_retained_not_redownloaded_for_duplicate_hash=True,
    full_trace_CPU_review_still_required=True,
    frozen_rule_vs_trained_gate_behavior_still_required=True)))
'''


def main():
    connection = sftp = None
    stamp = str(time.time_ns())
    try:
        connection = transport.connect()
        stdin, stdout, stderr = connection.exec_command(
            'CUDA_VISIBLE_DEVICES= ' + shlex.quote(transport.PY) + ' -', timeout=60)
        stdin.write(remote_program()); stdin.flush(); stdin.channel.shutdown_write()
        raw = stdout.read(); err = stderr.read(); rc = stdout.channel.recv_exit_status()
        transcript = D / 'reports' / ('S4_FIRST_GATE_CLOSED_FINAL_COLLECTION_TRANSPORT_' + stamp + '.json')
        transcript.write_text(json.dumps(dict(rc=rc, stdout=raw.decode('utf8', 'replace'),
            stderr=err.decode('utf8', 'replace')), indent=2), encoding='utf8')
        assert rc == 0, str(transcript)
        value = json.loads(raw)
        target = D / 'own_gate_closed_final_actual' / stamp
        target.mkdir(parents=True)
        sftp = connection.open_sftp(); sftp.get_channel().settimeout(60)
        for row in value['files']:
            p = target / row['relative']; p.parent.mkdir(parents=True, exist_ok=True)
            sftp.get(row['path'], str(p), max_concurrent_prefetch_requests=16)
            assert p.stat().st_size == row['bytes'] and digest(p) == row['sha256']
            row.update(local_path=str(p), twohost_SHA_exact=True)
        value['all_collected_twohost_SHA_exact'] = True
        out = D / 'reports' / ('S4_FIRST_GATE_CLOSED_FINAL_ALL_INPUTS_TWOHOST_ACTUAL_' + stamp + '.json')
        out.write_text(json.dumps(value, indent=2), encoding='utf8')
        print(json.dumps(dict(report=str(out), files=len(value['files']),
            updates=value['final']['updates'], final_SHA=value['final']['own_checkpoint_SHA'],
            canonical_unique_seconds=value['unique_completed_segment']['ended_epoch'] - value['unique_completed_segment']['started_epoch'],
            full_trace_and_behavior_not_yet_verified=True)))
    finally:
        if sftp: sftp.close()
        transport.close(connection)


if __name__ == '__main__': main()
