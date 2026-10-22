from pathlib import Path
import hashlib, json, os, subprocess, sys, time, traceback

T = Path(__file__).resolve().parent
W = T.parent
G = W / 'polar-rl-train'
R = T / 'reports'
NAME = Path(__file__).stem
BASE = '55703d994a0760d1045c53cdef20f190f86aba2e'
D = G / 'versions/20261020_two_linux_policy50_series/H1_COMPLETE121_ACTUAL_RETENTION_PAIR13_V103_POST_GIT_MONITOR_20261022'
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
    direct = []
    changes = {line[3:] for line in git('status', '--porcelain').splitlines()}
    assert changes == set(direct), changes
    tags = git('for-each-ref', '--format=%(refname) %(objectname) %(*objectname)', 'refs/tags')
    assert len(tags.splitlines()) == 1421
    receipt = json.loads((R / 'V103_EXISTING_MONITOR_EXACT_READBACK_ACTUAL.json').read_bytes())
    assert receipt['all_fields_raw_exact'] and receipt['automation_id'] == 'mod4-10'
    put(started, dict(epoch=time.time(), pid=os.getpid(), argv=sys.argv, base_HEAD=BASE,
                      ordinary_only=True, no_record_tag_GPU_transport_or_ledger_write=True))
    files = [
        T / 'prepare_V103_existing_monitor_actual_retention_once.py',
        T / 'verify_V103_monitor_and_prepare_one_postGit_once.py',
        Path(__file__).resolve(),
        R / 'V103_GIT_MAIN_ALL_TAGS_AND_TEXT_BLOBS_VERIFIED_RECEIPT_ACTUAL.json',
        R / 'V103_EXISTING_MONITOR_UPDATE_ARGS.json',
        R / 'V103_EXISTING_MONITOR_APP_RECEIPT_ACTUAL.json',
        R / 'V103_EXISTING_MONITOR_EXACT_READBACK_ACTUAL.json',
        started,
    ]
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
    index = dict(epoch=time.time(),kind='H1_complete121_E3_complete71_actual_bounded_retention_passed_pair13_BOTH_PPO_postGit',entries=entries,ordinary_followup_only=True,no_new_record_or_tag=True,no_training_host_transport_GPU_PPO_or_account_write=True,existing_monitor_updated_and_raw_exact_readback_verified=True,first_pair12_actual_retention_directory_receipts_passed=True,current_pair13_future_FINAL_or_retention_counts_not_claimed=True,no_formal_270mm_claim=True,deferred=['e2'])
    path = D / 'COMPLETE_FILE_CAPTURE_INDEX.json'
    put(path, index)
    blobs[path.relative_to(G).as_posix()] = sha(path.read_bytes())
    paths = list(blobs)
    git('add', '--pathspec-from-file=-', '--pathspec-file-nul',
        input=b'\0'.join(p.encode('utf8') for p in paths) + b'\0')
    git('commit', '-m', 'Archive complete121 actual bounded retention and pair13 Git receipt with same monitor exact readback')
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
