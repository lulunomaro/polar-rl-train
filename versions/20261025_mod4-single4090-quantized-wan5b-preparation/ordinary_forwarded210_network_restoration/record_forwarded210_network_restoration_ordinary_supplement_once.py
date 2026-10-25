"""Existing quantized/network-stage ordinary supplement: no record_experiment or new tag."""
from pathlib import Path
import hashlib, json, subprocess, sys, time, tomllib

Q = Path(__file__).resolve().parent
T, W = Q.parent, Q.parent.parent
G, R = W / 'polar-rl-train', Q / 'reports'
B = T / 'H1_STEP270_REWARD_PATH_V1_20261022'

def git(*args):
    p = subprocess.run(['git', '-C', str(G), *args], capture_output=True)
    assert p.returncode == 0, p.stderr.decode('utf8', 'replace')
    return p.stdout.decode('utf8').strip()

assert git('rev-parse', 'HEAD') == '1e96d4e29695c9284f188a1e525495854d2255c4'
assert not git('status', '--porcelain')
tags = git('for-each-ref', '--format=%(refname) %(objectname) %(*objectname)', 'refs/tags')
assert len(tags.splitlines()) == 1440
mon = tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
source = R / 'POST_FORWARDED210_NETWORK_RESTORATION_MONITOR_SOURCE_ACTUAL.txt'
assert mon['prompt'] == source.read_text('utf8')
assert mon['status'] == 'ACTIVE' and mon['rrule'] == 'FREQ=HOURLY;INTERVAL=1'
assert mon['target_thread_id'] == '01a07a2d-9036-7531-a012-692df9f56353'

sources = [Q / name for name in (
    'USER_FORWARD_INITIAL_TCP_INLINE_SOURCE_CAPTURE.py',
    'read_user_forwarded210_4090_strict_hostkey_once.py',
    'strict_user_forwarded_original210_transport_v1.py',
    'read_current68_after_user_forwarded_route_restored_once.py',
    'record_forwarded210_network_restoration_ordinary_supplement_once.py',
)]
sources += [B / ('same_authorized_session_compressed_transport_v' + str(v) + '.py') for v in (84, 85)]
sources += [R / name for name in (
    'USER_FORWARD4090_BEFORE_INTERNAL22_TCP_REFUSED_ACTUAL.json',
    'USER_FORWARD4090_INTERNAL22_STRICT_SSH_STARTED_ACTUAL.json',
    'USER_FORWARD4090_INTERNAL22_STRICT_SSH_RETURNED_ACTUAL.json',
    'CURRENT68_FORWARDED_ROUTE_RESTORED_READER_STARTED_ACTUAL.json',
    'CURRENT68_FORWARDED_ROUTE_RESTORED_READER_RETURNED_ACTUAL.json',
    'USER_FORWARD_SOURCE_READER_PATH_ERROR_AND_TRUNCATION_ACTUAL.json',
    'FORWARDED210_AUTHENTICATED_CURRENT68_PENDING_ORIGINAL_HANDOFF_WORK_ORDER_ACTUAL.json',
    'POST_FORWARDED210_NETWORK_RESTORATION_MONITOR_SOURCE_ACTUAL.txt',
)]
assert len(sources) == 15 and all(p.is_file() for p in sources)
D = G / 'versions/20261025_mod4-single4090-quantized-wan5b-preparation/ordinary_forwarded210_network_restoration'
D.mkdir()
sys.path.insert(0, str(G / 'archive_tools'))
from capture_history import redact
entries, saved = [], []
for p in sources:
    raw = p.read_bytes()
    clean, count = redact(raw.decode('utf8'))
    data = clean.encode('utf8')
    target = D / p.name
    with target.open('xb') as f:
        f.write(data)
    saved.append(target)
    entries.append({'path': str(p), 'bytes': len(raw), 'SHA': hashlib.sha256(raw).hexdigest(),
                    'archive': target.relative_to(G).as_posix(),
                    'archive_SHA': hashlib.sha256(data).hexdigest(),
                    'redaction_count': count, 'original_retained': True})
index = D / 'ORDINARY_CAPTURE_INDEX.json'
with index.open('x', encoding='utf8') as f:
    json.dump({'epoch': time.time(), 'kind': 'existing_stage_network_restoration_ordinary_supplement_no_new_trial',
               'entries': entries, 'all_actual_original_failures_preserved': True,
               'same_original_pinned210_now_authenticated_via_human_port_forward': True,
               'original68_owner_still_active_waiting_terminals': True,
               'current68_FINAL_producers_not_wholeCPU_qualified': True,
               'no_model_PT_raw_GPU_host_query_or_canonical_write_for_Git': True,
               'automation_same_ACTIVE_hourly_original_target_prompt_verified': True}, f, ensure_ascii=False, indent=2)
saved.append(index)
git('add', '--', *[p.relative_to(G).as_posix() for p in saved])
git('commit', '-m', 'Record forwarded210 SSH restoration and original68 pending terminal handoff')
git('push', 'origin', 'HEAD:main')
head = git('rev-parse', 'HEAD')
remote = {x.split()[1]: x.split()[0] for x in git('ls-remote', 'origin', 'refs/heads/main', 'refs/tags/*').splitlines()}
assert remote['refs/heads/main'] == head
for line in tags.splitlines():
    x = line.split()
    assert remote[x[0]] == x[1]
    if len(x) > 2:
        assert remote[x[0] + '^{}'] == x[2]
for p in saved:
    assert subprocess.check_output(['git', '-C', str(G), 'show', head + ':' + p.relative_to(G).as_posix()]) == p.read_bytes()
assert not git('status', '--porcelain')
print(json.dumps({'remote_main': head, 'ordinary_text_entries': len(entries), 'committed_files': len(saved),
                  'all1440_tag_objects_and_peels_unchanged': True, 'no_new_trial_or_tag': True,
                  'all_committed_blobs_match': True, 'workingtree_clean': True}))
