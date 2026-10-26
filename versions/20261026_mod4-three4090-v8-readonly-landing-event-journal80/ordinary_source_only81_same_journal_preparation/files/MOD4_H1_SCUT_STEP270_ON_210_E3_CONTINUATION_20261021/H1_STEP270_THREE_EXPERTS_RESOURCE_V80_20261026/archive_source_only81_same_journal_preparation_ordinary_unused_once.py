"""Ordinary source-only81 preparation supplement. No trial/record or training actions."""
from pathlib import Path
import hashlib
import json
import time
import tomllib
import traceback

N = Path(__file__).resolve().parent
T = N.parent
W = T.parent
G = W / 'polar-rl-train'
R = N / 'reports'
F = T / 'H1_STEP270_THREE_EXPERTS_RESOURCE_V81_20261026'
S = G / 'versions/20261026_mod4-three4090-v8-readonly-landing-event-journal80'
dest = S / 'ordinary_source_only81_same_journal_preparation'
engine = T / 'MOD4_SAMPLING_THROUGHPUT_OPTIMIZATION_PREPARATION_20261025/archive_current_implementation_and_MOE_preparation_stages_unique_once.py'
ns = dict(__name__='ordinary81_capture_utilities_only', __file__=str(engine))
exec(compile(engine.read_text('utf8'), str(engine), 'exec'), ns)
git, H, redact = ns['git'], ns['H'], ns['redact']

def main():
    assert git('rev-parse', 'HEAD') == 'd90e500f36d55a02565e6bc48035b3a9871c04a8'
    assert not git('status', '--porcelain') and not dest.exists()
    tags = git('for-each-ref', '--format=%(refname) %(objectname) %(*objectname)', 'refs/tags')
    assert len(tags.splitlines()) == 1452
    assert json.loads((F / 'reports/SOURCE_ONLY81_SAME_JOURNAL_LINEAGE_AND_REJECTION_CPU_ACTUAL.json').read_bytes())['passed_source_only_CPU']
    assert all(not (F / x).exists() for x in ('payloads', 'controllers', 'job0'))
    a = tomllib.loads((Path.home() / '.codex/automations/mod4-10/automation.toml').read_text('utf8'))
    source = R / 'CURRENT_ACTUAL80_THREE4090_V8_JOURNAL_AND_SOURCE_ONLY81_MONITOR_SOURCE_V2.txt'
    assert a['status'] == 'ACTIVE' and a['rrule'] == 'FREQ=HOURLY;INTERVAL=1'
    assert a['target_thread_id'] == '01a07a2d-9036-7531-a012-692df9f56353'
    assert a['prompt'] == source.read_text('utf8')
    with (R / 'SOURCE_ONLY81_MONITOR_V2_UPDATED_EXACT_PREARCHIVE_ACTUAL.json').open('x', encoding='utf8') as f:
        json.dump(dict(epoch=time.time(), automation_id='mod4-10', status=a['status'], rrule=a['rrule'], target_thread_id=a['target_thread_id'], saved_source_exact=True, source_SHA=H(source), current80_source_firstPPO_not_reread_remotely=True, no_runtime_or_budget_action=True), f, indent=2)
    prior_path = S / 'COMPLETE_FILE_CAPTURE_INDEX.json'
    ns['prior'](prior_path)
    old_index = ns['read_capture_index'](prior_path, G)
    old_binary = {str(Path(row['path'])).casefold(): row for row in old_index.get('external_binary_index', [])}
    files, entries, binaries, splits = {}, [], [], []
    def add(p, data):
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open('xb') as f:
            f.write(data)
        files[p.relative_to(G).as_posix()] = H(data)
    paths = sorted({p for root in (N, F) for p in root.rglob('*') if p.is_file() and not p.is_symlink() and '__pycache__' not in p.parts} | {T / 'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v125.py'})
    text_suffixes = {'.py', '.json', '.jsonl', '.log', '.txt', '.md', '.sh', '.yaml', '.yml', '.toml', '.csv', '.diff', '.patch', '.ini', '.cfg'}
    dest.mkdir()
    for p in paths:
        st = p.stat()
        if p.suffix.lower() not in text_suffixes:
            previous = old_binary.get(str(p).casefold())
            assert previous and previous['bytes'] == st.st_size, p
            binaries.append(dict(previous, no_content_read_for_this_Git_supplement=True))
            continue
        raw = p.read_bytes()
        digest = H(raw)
        row = dict(path=str(p), bytes=len(raw), SHA=digest, source_mtime_ns=st.st_mtime_ns, original_retained=True)
        old = ns['prior_entries'].get((str(p), digest))
        if old:
            row.update(archive=old['archive'], archive_SHA=old.get('archive_SHA', digest), mode='previous_same_SHA_full_capture_reference')
            entries.append(row)
            continue
        clean, count = redact(raw.decode('utf8'))
        data = clean.encode('utf8')
        out = dest / 'files' / p.relative_to(W)
        if len(data) <= 49_000_000:
            add(out, data)
            row.update(archive=out.relative_to(G).as_posix(), archive_SHA=H(data), mode='redacted' if count else 'full', redaction_count=count)
        else:
            parts, position, assembled = [], 0, hashlib.sha256()
            while position < len(data):
                end = min(position + 24_000_000, len(data))
                if end < len(data):
                    while data[end] & 0xc0 == 0x80:
                        end -= 1
                block = data[position:end]
                block.decode('utf8')
                part = out.with_name(out.name + '.utf8part' + str(len(parts)).zfill(4) + '.txt')
                add(part, block)
                parts.append(dict(path=part.relative_to(G).as_posix(), bytes=len(block), SHA=H(block)))
                assembled.update(block)
                position = end
            assert assembled.hexdigest() == H(data)
            desc = dict(original_path=str(p), original_bytes=len(raw), original_SHA=digest, archived_bytes=len(data), archived_SHA=H(data), ordered_UTF8_parts=parts, full_reassembled_SHA_verified=True, redaction_count=count)
            out = out.with_name(out.name + '.ordered_parts.json')
            add(out, json.dumps(desc, ensure_ascii=False, indent=2).encode())
            splits.append(desc)
            row.update(archive=out.relative_to(G).as_posix(), archive_SHA=H(data), mode='full_ordered_UTF8_parts', redaction_count=count)
        assert p.stat().st_size == st.st_size and p.stat().st_mtime_ns == st.st_mtime_ns, p
        entries.append(row)
    ns['write_capture_index'](dest / 'ORDINARY_CAPTURE_INDEX.json', dict(epoch=time.time(), kind='ordinary_source_only81_same_journal_preparation', entries=entries, external_binary_index=binaries, previous_full_captures=ns['prior_descriptors'], no_new_trial_tag_training_or_remote_query=True), add, splits, G)
    add(dest / 'EXTERNAL_BINARY_EXISTING_PRODUCER_SHA_INDEX.json', json.dumps(binaries, ensure_ascii=False, indent=2).encode())
    note = 'While80 remains in its original finite training window, prepare only a possible same-V8 continuation81. No payload, model, controller, Task, source80 checkpoint binding, GO or fee. The candidate inherits80 journal/counter/checker/trace/auth bytes, allowing only the original source guard role and exact E3 saved-Adam assertion changes. It validates the historical pre-journal counter/sampler base links without reapplying a migration or normalizing metadata.27 actual saved-text lineage and negative metadata/AST cases pass; they do not substitute for complete80 models/CPU/original cost/allout or actual next target SDK/resources/valid_ready. Inspect completed80 landing evidence before deciding whether the same continuation is appropriate. Transport125 adds three exact future entry basenames only, unexecuted. Existing current80 collector/deadlines/optional diagnostic handling and all training/accounting/physics/success rules remain. Monitor retained ACTIVE/hourly/original target with quiet pending policy. Ordinary supplement to consumed80 trial, no record/tag. No model/raw/GPU/host action for Git.\n'
    add(dest / 'ACTUAL_RESULT_NOTE.md', note.encode())
    git('add', '--pathspec-from-file=-', '--pathspec-file-nul', input=b'\0'.join(x.encode() for x in files) + b'\0')
    git('commit', '-m', 'Prepare source-only81 byte-exact journal continuation without active80 changes')
    git('push', 'origin', 'HEAD:main')
    head = git('rev-parse', 'HEAD')
    remote = {line.split()[1]: line.split()[0] for line in git('ls-remote', 'origin', 'refs/heads/main', 'refs/tags/*').splitlines()}
    assert remote['refs/heads/main'] == head
    for line in tags.splitlines():
        ref = line.split()
        assert remote[ref[0]] == ref[1]
        if len(ref) > 2:
            assert remote[ref[0] + '^{}'] == ref[2]
    ns['committed_blob_check'](head, files)
    assert len(git('tag', '--list').splitlines()) == 1452 and not git('status', '--porcelain')
    print(json.dumps(dict(remote_main=head, ordinary_text_entries=len(entries), new_files=len(files), binary_metadata_entries=len(binaries), all1452_old_tag_objects_peels_unchanged=True, no_new_trial_or_tag=True, all_committed_blobs_verified=True, workingtree_clean=True)))

if __name__ == '__main__':
    try:
        main()
    except BaseException:
        with (R / ('ORDINARY_SOURCE_ONLY81_ARCHIVE_ORIGINAL_ERROR_' + str(time.time_ns()) + '.json')).open('x', encoding='utf8') as f:
            json.dump(dict(epoch=time.time(), error=traceback.format_exc(), actual_HEAD=git('rev-parse', 'HEAD'), resume_existing_objects_if_commit_started=True, no_repeat_record_or_tag=True), f, indent=2)
        raise
