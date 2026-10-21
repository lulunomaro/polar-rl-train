from pathlib import Path
import hashlib, json, os, subprocess, sys, time, traceback

T = Path(__file__).resolve().parent
W = T.parent
G = W / 'polar-rl-train'
R = T / 'reports'
NAME = Path(__file__).stem
BASE = 'd733e83079cecdc99c4d6bfbbb545c30f4e333ed'
D = G / 'versions/20261020_two_linux_policy50_series/HUMAN_CONFIRMED_THRESHOLD_SCOPE_V91_20261021'
sha = lambda b: hashlib.sha256(b).hexdigest()

def git(*args, input=None):
    p = subprocess.run(['git', '-C', str(G), *args], input=input, capture_output=True)
    assert p.returncode == 0, p.stderr.decode('utf8', 'replace')
    return p.stdout.decode('utf8').rstrip('\r\n')

def put(path, value):
    with path.open('x', encoding='utf8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)

def main():
    started = R / (NAME + '_STARTED_ACTUAL.json')
    assert not started.exists() and not D.exists()
    assert git('rev-parse', 'HEAD') == BASE
    direct = ['AGENTS.md', 'docs/NUMERICAL_AUDIT_AND_TRAINING_GUARDS_20261021.md']
    changes = {line[3:] for line in git('status', '--porcelain').splitlines()}
    assert changes == set(direct), changes
    tags = git('for-each-ref', '--format=%(refname) %(objectname) %(*objectname)', 'refs/tags')
    assert len(tags.splitlines()) == 1421
    receipt = json.loads((R / 'V91_EXISTING_MONITOR_EXACT_READBACK_ACTUAL.json').read_bytes())
    assert receipt['all_updated_fields_exact_readback'] and receipt['automation_id'] == 'mod4-10'
    put(started, dict(epoch=time.time(), pid=os.getpid(), argv=sys.argv, base_HEAD=BASE,
                      ordinary_only=True, no_record_tag_GPU_transport_or_ledger_write=True))
    files = [
        W / 'AGENTS.md',
        T / 'prepare_V91_human_confirmed_threshold_scope_records_once.py',
        Path(__file__).resolve(),
        R / 'V91_HUMAN_CONFIRMED_THRESHOLD_SCOPE_AND_REUSE_ACTUAL.json',
        R / 'NEXT_ACTUAL_HUMAN_CONFIRMED_THRESHOLD_SCOPE_AND_H1_E3_CONTINUATION_V91_WORK_ORDER.json',
        R / 'V91_EXISTING_MONITOR_UPDATE_ARGS.json',
        R / 'V91_EXISTING_MONITOR_APP_RECEIPT_ACTUAL.json',
        R / 'V91_EXISTING_MONITOR_EXACT_READBACK_ACTUAL.json',
        started,
    ]
    files.append(T / 'append_V91_threshold_scope_authorized_continuation_ordinary_once.py')
    files.extend(sorted(R.glob('append_V91_threshold_scope_authorized_continuation_ordinary_once_ORIGINAL_ERROR_*.json')))
    sys.path.insert(0, str(G / 'archive_tools'))
    from capture_history import redact
    entries = []
    blobs = {}
    for path in files:
        assert path.resolve().is_relative_to(W.resolve()) and path.suffix not in ('.pt', '.npz', '.usd', '.zip')
        raw = path.read_bytes()
        assert len(raw) < 2_000_000
        clean, count = redact(raw.decode('utf8'))
        data = clean.encode('utf8')
        dest = D / 'files' / path.relative_to(W)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        rel = dest.relative_to(G).as_posix()
        blobs[rel] = sha(data)
        entries.append(dict(path=str(path), bytes=len(raw), SHA=sha(raw), archive=rel,
                            archive_SHA=sha(data), mode='redacted' if count else 'full',
                            redaction_count=count, original_retained=True,
                            source_mtime_ns=path.stat().st_mtime_ns))
    for rel in direct:
        path = G / rel
        raw = path.read_bytes()
        _, count = redact(raw.decode('utf8'))
        assert count == 0, 'Direct policy files must not contain credentials'
        blobs[rel] = sha(raw)
        entries.append(dict(path=str(path), bytes=len(raw), SHA=sha(raw), archive=rel,
                            archive_SHA=sha(raw), mode='full', original_retained=True,
                            source_mtime_ns=path.stat().st_mtime_ns))
    index = dict(epoch=time.time(), kind='human_confirmed_threshold_scope_and_evidence_reuse',
                 entries=entries, ordinary_followup_only=True, no_new_record_or_tag=True,
                 no_training_host_transport_GPU_PPO_or_account_write=True,
                 existing_monitor_updated_and_exact_readback=True,
                 no_new_H1_GO_or_skill_result=True, deferred=[])
    path = D / 'COMPLETE_FILE_CAPTURE_INDEX.json'
    put(path, index)
    blobs[path.relative_to(G).as_posix()] = sha(path.read_bytes())
    paths = list(blobs)
    git('add', '--pathspec-from-file=-', '--pathspec-file-nul',
        input=b'\0'.join(p.encode('utf8') for p in paths) + b'\0')
    git('commit', '-m', 'docs: preserve approved tolerance scope and reuse passed H1 evidence')
    head = git('rev-parse', 'HEAD')
    git('push', 'origin', 'HEAD:main')
    remote = {x.split()[1]: x.split()[0] for x in git('ls-remote', 'origin', 'refs/heads/main', 'refs/tags/*').splitlines()}
    assert remote['refs/heads/main'] == head
    assert git('for-each-ref', '--format=%(refname) %(objectname) %(*objectname)', 'refs/tags') == tags
    for line in tags.splitlines():
        p = line.split()
        assert remote[p[0]] == p[1]
        if len(p) > 2:
            assert remote[p[0] + '^{}'] == p[2]
    batch = subprocess.run(['git', '-C', str(G), 'cat-file', '--batch'],
                           input=''.join(head + ':' + p + '\n' for p in paths).encode(),
                           capture_output=True, check=True).stdout
    offset = 0
    for rel in paths:
        end = batch.index(b'\n', offset)
        header = batch[offset:end].split()
        assert header[1] == b'blob'
        size = int(header[2])
        offset = end + 1
        assert sha(batch[offset:offset + size]) == blobs[rel]
        offset += size + 1
    assert not git('status', '--porcelain')
    print(json.dumps(dict(remote_main=head, tags=1421, all_original_tag_objects_and_peels_unchanged=True,
                          all_new_Git_blobs_verified=True, text_entries=len(entries), new_Git_files=len(blobs),
                          same_monitor_ACTIVE_hourly=True, no_new_training_result_claim=True)))

if __name__ == '__main__':
    try:
        main()
    except BaseException:
        put(R / (NAME + '_ORIGINAL_ERROR_' + str(time.time_ns()) + '.json'),
            dict(epoch=time.time(), error=traceback.format_exc(), HEAD=git('rev-parse', 'HEAD'),
                 do_not_rerun_once_or_record_tag_resume_existing_objects_only=True))
        raise
