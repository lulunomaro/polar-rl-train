"""Ordinary118 supplement. No trial tag or experiment/model/runtime execution.

If commit succeeds but push/verification fails, resume the existing commit;
never rerun this capture or create another tag.
"""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys
import time

T = Path(__file__).resolve().parent
W = T.parent
G = W / 'polar-rl-train'
L = T / 'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
D119 = L / 'native119_pre_request_neutral_X_goal_source_v1'
D120 = L / 'native120_original_closure_vs_imagined_stop_CPU_review_v1'
M = T / 'MOD4_READONLY_FOUR4090_TERMINAL_V117_20261029'
REL = Path('versions/20261029_mod4-native116-latest-user-mujoco-actual-blue-imagination118/ordinary_source119120_core_failure_review_v1')
DEST = G / REL
BASE = '306b79e2aa75ca7992a740d03eedf0e43518130e'
TAG118 = 'trial-20261029-mod4-native116-latest-user-mujoco-actual-blue-imagination118'
TAG118OBJ = '645a0cc1750de3f4539c425fe475b27f689caa17'
R = D120 / 'reports'
MARKER = R / 'ORDINARY118_SOURCE119120_CAPTURE_CONSUMED.json'


def git(*args, binary=False):
    p = subprocess.run(['git', *args], cwd=G, capture_output=True, check=False)
    if p.returncode:
        raise RuntimeError('git command failed: ' + args[0] + ': ' + p.stderr.decode('utf-8', 'replace')[-1800:])
    return p.stdout if binary else p.stdout.decode('utf-8', 'strict').strip()


def sha(b):
    return hashlib.sha256(b).hexdigest()


def local_tags():
    rows = {}
    out = git('for-each-ref', '--format=%(refname) %(objectname) %(*objectname)', 'refs/tags')
    for line in out.splitlines():
        parts = line.split()
        rows[parts[0]] = {'object': parts[1], 'peeled': parts[2] if len(parts) == 3 else None}
    return rows


def remote_refs():
    out = git('ls-remote', 'origin', 'refs/heads/main', 'refs/tags/*')
    refs = dict(line.split()[::-1] for line in out.splitlines())
    tags = {}
    for name, obj in refs.items():
        if name.startswith('refs/tags/') and not name.endswith('^{}'):
            tags[name] = {'object': obj, 'peeled': refs.get(name+'^{}')}
    return refs['refs/heads/main'], tags


def write_new(path, value):
    assert not path.exists(), str(path)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def main():
    assert git('rev-parse', 'HEAD') == BASE
    assert git('symbolic-ref', '--short', 'HEAD') == 'main'
    assert not git('status', '--porcelain=v1'), 'Preserve unexpected repository changes'
    assert git('config', '--get', 'core.autocrlf') == 'false'
    assert (G / '.gitattributes').read_text(encoding='utf-8').strip() == '* -text'
    old_tags = local_tags()
    assert len(old_tags) == 1484
    assert old_tags['refs/tags/'+TAG118] == {'object': TAG118OBJ, 'peeled': BASE}
    remote_head, remote_tags = remote_refs()
    assert remote_head == BASE and remote_tags == old_tags, 'Remote changed; do not overwrite'
    assert not DEST.exists() and not MARKER.exists(), 'Consumed supplement: continue existing objects instead'

    required = [D119 / 'reports/SOURCE119_PRE_REQUEST_BACKWARD_GOAL_CUE_AND_NARROW_CANDIDATE_CPU_ACTUAL.json',
        D120 / 'reports/SOURCE120_CLOSURE_STOP_CANDIDATE_SAVED_FAILURE_GRACE_NEUTRAL_CPU_ACTUAL.json',
        D120 / 'reports/AUTOMATION_CURRENT120_ACTUAL_PERSISTED_CHECK.json',
        D120 / 'reports/ACTUAL116_LEARNER_CALL_CHAIN_AND_FUTURE_RETURN_SOURCE_ONLY.json']
    for p in required:
        assert p.is_file(), str(p)
    assert json.loads(required[1].read_bytes())['passed_source_CPU_only'] is True
    assert json.loads(required[2].read_bytes())['passed'] is True

    write_new(MARKER, dict(epoch=time.time(), mode='ordinary_append_to_consumed118', previous_HEAD=BASE,
        protected_old_tag_count=len(old_tags), new_tag_count=0,
        tag118_object=TAG118OBJ, output=str(DEST),
        source119_secondary_NOT_SELECTED_for_next_learning=True,
        source120_CPU_candidate_NOT_runtime_admitted=True,
        human_primary_issue='stands tall and charges, then closure terminal; not jump270 success',
        no_experiment_or_model_raw_GPU_host_query_or_training_for_Git=True,
        postcommit_push_failure_policy='Continue existing commit; no recapture/re-record/re-tag.',
        postGit_verification='Conversation-only; no new saved verification file chasing HEAD.'))

    roots = [D119, D120, M / 'reports/selected_v8']
    extra = [T / 'prepare_native119_pre_request_neutral_X_SOURCE_ONLY_once.py',
        T / 'review_native120_actual_closure_vs_imagined_stop_CPU_once.py',
        T / 'prepare_native120_imagined_closure_stop_SOURCE_ONLY_once.py',
        T / 'record_native120_learner_binding_SOURCE_ONLY_once.py',
        M / 'refresh_serial_dashboard_v8_known_viewer_source119.py', Path(__file__).resolve()]
    sources = set(extra)
    for root in roots:
        assert root.is_dir(), str(root)
        sources.update(p for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    assert all(p.is_file() for p in sources)

    DEST.mkdir(parents=True, exist_ok=False)
    (DEST / 'files').mkdir()
    index = []
    extensions = {'.py', '.md', '.json', '.txt', '.toml', '.ps1'}
    credential_patterns = [rb'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----',
        rb'gh[pousr]_[A-Za-z0-9]{30,}', rb'github_pat_[A-Za-z0-9_]{30,}',
        rb'\bsk-[A-Za-z0-9_-]{32,}']
    for p in sorted(sources, key=lambda x: str(x).lower()):
        before = p.stat()
        origin = str(p)
        if p.suffix.lower() not in extensions:
            # No binary content read or fresh binary hash for archival.
            index.append(dict(origin=origin, bytes=before.st_size, SHA256='unknown',
                archive_status='metadata_only_no_content_read', reason='non-text extension'))
            continue
        raw = p.read_bytes()
        raw.decode('utf-8-sig', 'strict')
        assert b'\x00' not in raw
        assert not any(re.search(pattern, raw) for pattern in credential_patterns), 'Credential-shaped value; no unsafe archive'
        after = p.stat()
        assert (before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns), 'Source changed during capture'
        assert len(raw) == before.st_size
        name = sha(origin.encode('utf-8'))[:20] + p.suffix.lower()
        dst = DEST / 'files' / name
        dst.write_bytes(raw)
        index.append(dict(origin=origin, original_name=p.name, bytes=len(raw), SHA256=sha(raw),
            archive_path=(REL / 'files' / name).as_posix(), archived_SHA256=sha(raw),
            archive_status='complete_UTF8_exact_bytes', source_mtime_ns=before.st_mtime_ns))

    info = dict(phase='ordinary118_source119120_core_failure_review_v1', epoch=time.time(),
        previous_HEAD=BASE, no_new_tag=True, protected_tags=old_tags,
        findings=dict(actual118_closure_terminal_s=4.31, actual_anchor_error_m=.00223560375161469,
            original_threshold_m=.002, original_imagined_stop_probability=.00009594196308171377,
            source120_candidate_stop_on_same_saved_failure=1.0,
            source120_not_runtime_or_newlearning=True,
            unresolved='WM false-stop calibration and valid-jump/cross/landing process alignment before any learning.',
            source119_secondary_not_selected=True,
            small_saved_terminal_text_reads_across_two_explicit_diagnostic_purposes=2,
            checkpoint_raw_JSONL_NPZ_GPU_SDK_physics_reads_this_phase=0,
            monitor3060_original_viewer_out_no_restart_other_host_queries_skipped=True),
        roots=[str(x) for x in roots], extra_sources=[str(x) for x in extra], entries=index,
        binary_policy='Only actual path/stat bytes/existing producer SHA or unknown; no binary content/hash for Git.')
    (DEST / 'ORDINARY_CAPTURE_INDEX.json').write_text(json.dumps(info, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    (DEST / 'README.md').write_text(
        '# Source119/120 supplement to consumed actual118\n\n'
        'The human-observed behavior is standing tall, charging forward and ending on closure, not a successful jump. '
        'The genuine saved4.31s terminal has2.2356mm original closure error, while the current imagined-stop function returns0.00009594. '
        'The actual116 learner uses this function for future-reward continuation and critic survival.\n\n'
        'Source120 adds the original2mm/grace boundary using own q-FK. It catches this saved failure in CPU fixtures, '
        'but is not deployed or training-ready: WM-predicted closure false-stops must be calibrated, and valid jump/cross history remains unresolved. '
        'Source119 initial X cue is secondary and not selected as a sufficient jump fix. No new learning, GO, budget write or model/raw read occurred.\n\n'
        'All source, CPU reports, original lookup errors, priority corrections, app receipt and closed3060viewer receipt are indexed in ORDINARY_CAPTURE_INDEX.json. '
        'The files directory preserves exact UTF8 bytes; names are mapped by that index. No new trial tag is created.\n', encoding='utf-8')

    # Check staging contains only this new ordinary supplement.
    git('add', '--', REL.as_posix())
    staged = git('diff', '--cached', '--name-only').splitlines()
    assert staged and all(x.startswith(REL.as_posix()+'/') for x in staged)
    git('diff', '--cached', '--check')
    git('commit', '-m', 'Record H1 closure planning mismatch and source-only corrections')
    commit = git('rev-parse', 'HEAD')
    assert commit != BASE and git('rev-parse', 'HEAD^') == BASE
    print(json.dumps(dict(stage='committed_existing_objects', commit=commit,
        archived_text_entries=sum(x['archive_status']=='complete_UTF8_exact_bytes' for x in index),
        metadata_only_entries=sum(x['archive_status']!='complete_UTF8_exact_bytes' for x in index)), ensure_ascii=False), flush=True)
    git('push', 'origin', 'HEAD:refs/heads/main')

    # Verify each new committed blob against the captured exact bytes; no source/model reread.
    committed = git('ls-tree', '-r', '--name-only', 'HEAD', '--', REL.as_posix()).splitlines()
    for name in committed:
        expected = (G / name).read_bytes()
        actual = git('show', 'HEAD:'+name, binary=True)
        assert len(actual) == len(expected) and sha(actual) == sha(expected), name
    for row in index:
        if row['archive_status'] == 'complete_UTF8_exact_bytes':
            actual = git('show', 'HEAD:'+row['archive_path'], binary=True)
            assert sha(actual) == row['SHA256'] and len(actual) == row['bytes']
    assert local_tags() == old_tags, 'Old local tag objects/peels must remain exact'
    final_head, final_tags = remote_refs()
    assert final_head == commit and final_tags == old_tags
    assert not git('status', '--porcelain=v1')
    # Final verification is tool output only. Do not create another saved report.
    print(json.dumps(dict(passed=True, commit=commit, remote_main=final_head,
        old_tag_objects_and_peels_preserved=len(old_tags), new_tags=0,
        verified_new_committed_blobs=len(committed), exact_text_entries=len(index),
        repository_clean=True, archive_path=REL.as_posix(),
        no_new_learning_or_binary_model_read_for_Git=True), ensure_ascii=False), flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        # Preserve a failed archive attempt. If a commit already exists, append
        # this later as an ordinary supplement rather than rerunning capture.
        error = dict(epoch=time.time(), passed=False, error_type=type(exc).__name__,
            error=str(exc), rule='Do not rerun consumed capture or retag; inspect actual HEAD/index and continue existing objects.')
        p = R / ('ORDINARY119120_ARCHIVE_ERROR_'+str(time.time_ns())+'.json')
        p.write_text(json.dumps(error, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        print(json.dumps(error, ensure_ascii=False), file=sys.stderr, flush=True)
        raise
