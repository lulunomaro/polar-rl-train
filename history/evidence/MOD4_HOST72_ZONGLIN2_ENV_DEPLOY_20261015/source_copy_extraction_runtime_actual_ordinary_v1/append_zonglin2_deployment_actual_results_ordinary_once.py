"""Append this deployment's actual results to the existing stage, without a new trial."""
from pathlib import Path
import hashlib
import importlib.util
import json
import subprocess
import sys
import time
import traceback

D = Path(__file__).resolve().parent
W = D.parent
R = D / 'reports'
REPO = W / 'polar-rl-train'
BASE = '4205677b5f41519429e5c975f8e880bf4a4c3502'
DEST = REPO / 'history/evidence' / D.name / 'source_copy_extraction_runtime_actual_ordinary_v1'
spec = importlib.util.spec_from_file_location('zonglin2_existing_archive_helpers',
    W / 'MOD4_S5_NOMINAL_AUDIT_SOURCE_ADAPTER_CPU_20261015/archive_nominal_isolated_source_target_native_and_unused29_stage_once.py')
n = importlib.util.module_from_spec(spec)
spec.loader.exec_module(n)
git = n.git


def main():
    assert git('rev-parse', 'HEAD') == BASE and not git('status', '--porcelain')
    assert not DEST.exists(), 'Existing capture/commit must be recovered, never replay this append.'
    assert (R / 'ZONGLIN2_HUMAN_DEPLOYMENT_FINAL_ACTUAL.json').exists()
    old = {}
    for line in git('for-each-ref', '--format=%(refname) %(objectname) %(*objectname)', 'refs/tags/').splitlines():
        v = line.split()
        old[v[0]] = (v[1], v[2] if len(v) > 2 else v[1])
    assert len(old) == 1349
    sys.path.insert(0, str(REPO / 'archive_tools'))
    from capture_history import redact
    DEST.mkdir(parents=True)
    rows, files = [], []
    for p in sorted(x for x in D.rglob('*') if x.is_file() and '__pycache__' not in x.parts):
        raw = p.read_bytes()
        row = dict(source_path=str(p.resolve()), bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
        if len(raw) > 8 * 1024 * 1024:
            row.update(capture='large_original_path_size_SHA_index_only', original_retained=True)
            rows.append(row)
            continue
        try:
            clean, count = redact(raw.decode('utf8'))
        except UnicodeDecodeError:
            row.update(capture='binary_original_path_size_SHA_index_only', original_retained=True)
            rows.append(row)
            continue
        data = clean.encode('utf8') if count else raw
        out = DEST / p.relative_to(D)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(data)
        rel = out.relative_to(REPO).as_posix()
        files.append(rel)
        row.update(Git_path=rel, archived_sha256=hashlib.sha256(data).hexdigest(),
            capture='redacted_full' if count else 'complete_exact_bytes', redactions=count)
        rows.append(row)
    index = DEST / 'REPORT_CAPTURE_INDEX.json'
    index.write_text(json.dumps(dict(epoch=time.time(), entries=rows,
        existing_stage_commit=BASE, ordinary_supplement_no_new_trial_tag=True,
        credentials_excluded=True, large_originals_retained=True), indent=2), encoding='utf8')
    files.append(index.relative_to(REPO).as_posix())
    add = subprocess.run(['git', '-C', str(REPO), 'add', '--pathspec-from-file=-', '--pathspec-file-nul'],
        input=('\0'.join(files) + '\0').encode('utf8'), capture_output=True, check=False)
    assert add.returncode == 0, add.stderr.decode('utf8', 'replace')
    git('commit', '-m', 'Append zonglin2 migration, preserved errors and actual runtime validation')
    head = git('rev-parse', 'HEAD')
    # One push of the newly created existing objects; recovery never creates another commit/tag.
    git('push', 'origin', 'main')
    n.m.cap.g = git
    n.m.cap.a.gitio.g = git
    n.m.cap.a.verify(rows, old, head)
    print(json.dumps(dict(commit=head, actual_remote_main_all1349_original_tag_peels_tracked_SHA_verified=True,
        sources=len(rows), ordinary_append_only=True, no_runtime_replay=True)), flush=True)


if __name__ == '__main__':
    try:
        main()
    except BaseException:
        with (R / ('ZONGLIN2_ORDINARY_APPEND_ORIGINAL_ERROR_' + str(time.time_ns()) + '.json')).open('x', encoding='utf8') as f:
            json.dump(dict(epoch=time.time(), error=traceback.format_exc(),
                recover_existing_capture_commit_objects_only=True, no_repeat_record_tag_commit_or_runtime=True), f, indent=2)
        raise
