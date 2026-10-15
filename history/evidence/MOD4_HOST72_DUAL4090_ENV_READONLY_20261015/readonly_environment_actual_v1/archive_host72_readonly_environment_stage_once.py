"""Unique diagnostic stage for the human-requested new-host inspection."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import importlib
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
BASE = '411ca16b760c43aaea4454485604e6e6a434ee46'
ID = 'host72-dual4090-readonly-environment-audit'
DEST = REPO / 'history/evidence' / D.name / 'readonly_environment_actual_v1'
spec = importlib.util.spec_from_file_location('host72_pure_archive_tools',
    W / 'MOD4_S5_NOMINAL_AUDIT_SOURCE_ADAPTER_CPU_20261015/archive_nominal_isolated_source_target_native_and_unused29_stage_once.py')
n = importlib.util.module_from_spec(spec)
spec.loader.exec_module(n)
git = n.git


def main():
    assert git('rev-parse', 'HEAD') == BASE and not git('status', '--porcelain')
    assert not git('tag', '--list', '*' + ID) and not DEST.exists()
    assert json.loads((R / 'HOST72_DUAL4090_ENVIRONMENT_SUMMARY_ACTUAL.json').read_bytes())['credentials_not_saved']
    old = {}
    for line in git('for-each-ref', '--format=%(refname) %(objectname) %(*objectname)', 'refs/tags/').splitlines():
        parts = line.split()
        old[parts[0]] = parts[1], parts[2] if len(parts) > 2 else parts[1]
    assert len(old) == 1347
    sys.path.insert(0, str(REPO / 'archive_tools'))
    from capture_history import redact
    rows, files = [], []
    DEST.mkdir(parents=True)
    for p in sorted(p for p in D.rglob('*') if p.is_file() and '__pycache__' not in p.parts):
        raw = p.read_bytes()
        text = raw.decode('utf8')
        clean, count = redact(text)
        data = clean.encode('utf8') if count else raw
        out = DEST / p.relative_to(D)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(data)
        rel = out.relative_to(REPO).as_posix()
        files.append(rel)
        rows.append(dict(source_path=str(p.resolve()), bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest(),
            Git_path=rel, archived_sha256=hashlib.sha256(data).hexdigest(),
            capture='redacted_full' if count else 'complete_exact_bytes', redactions=count))
    index = DEST / 'REPORT_CAPTURE_INDEX.json'
    index.write_text(json.dumps(dict(epoch=time.time(), entries=rows, credentials_excluded=True,
        all_saved_readers_success_failures_permission_denials_and_reports_at_snapshot_captured=True), indent=2), encoding='utf8')
    files.append(index.relative_to(REPO).as_posix())
    n.m.cap.g = git
    n.m.cap.a.gitio.g = git
    rec = importlib.import_module('record_experiment')
    rec.git = git
    sys.argv = ['record_experiment.py', '--id', ID, '--title', 'Inspect human-authorized dual4090 host72 without deployment or training',
        '--kind', 'diagnostic', '--note-file', str(D / 'HOST72_READONLY_STAGE_NOTE.txt'), '--files', *files,
        '--validation', 'Actual SSH hardware2x4090/Ubuntu20.04/driver535/no compute jobs. ExistingTorch2.0.1cu118 and2.7.1cu126 both enumerate2GPUs; no tensor kernels or Isaac run. Python37 metadata-reader errors and empty pytorch_env preserved with independent legacy-reader repair; scoped Isaac absence and data/Docker permission limitations retained. No remote install, source, process signal, training or budget mutation. Credential supplied hidden, never saved.', '--push']
    rec.main()
    head = git('rev-parse', 'HEAD')
    tag = 'trial-' + datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d') + '-' + ID
    obj = git('rev-parse', tag)
    n.m.cap.a.verify(rows, old, head, tag, obj)
    print(json.dumps(dict(commit=head, tag=tag, tagobject=obj,
        actual_remote_main_tag_peel_all1347_oldtags_and_trackedSHA_verified=True,
        saved_sources=len(rows), credentials_excluded=True, final_verification_retained_as_tool_output=True)), flush=True)


if __name__ == '__main__':
    try:
        main()
    except BaseException:
        with (R / ('HOST72_ARCHIVE_ORIGINAL_ERROR_' + str(time.time_ns()) + '.json')).open('x', encoding='utf8') as f:
            json.dump(dict(error=traceback.format_exc(), resume_existing_objects_if_created=True,
                           do_not_repeat_record_tag_commit=True, no_runtime_or_budget_action=True), f, indent=2)
        raise
