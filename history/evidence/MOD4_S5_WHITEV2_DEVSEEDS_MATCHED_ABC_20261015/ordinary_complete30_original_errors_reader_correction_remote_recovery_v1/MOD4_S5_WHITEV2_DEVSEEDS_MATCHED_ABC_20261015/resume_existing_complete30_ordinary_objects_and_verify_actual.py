"""One bounded recovery of already-created objects; no record, tag or commit."""
from pathlib import Path
import importlib.util
import json
import time
import traceback

D = Path(__file__).resolve().parent
R = D / 'reports'
p = D / 'archive_whitev2_native_fixed30_stage_actual_v2_continue_pre_record_once.py'
s = importlib.util.spec_from_file_location('whitev2_capture_existing_complete30_recovery', p)
m = importlib.util.module_from_spec(s)
s.loader.exec_module(m)
HEAD = 'e411cb07f275b287f3644a69c4159737a3b0edc3'
BASE = 'd3b0066cc49284b7b1a21c1efb7ebe66d4f1baab'
TAG = 'trial-20261015-s5-two-devseeds-reviewed-whitev2-frozen-abc-started'
OBJ = '0b9f7b0a5b29d4cb124cb8ed40ffa0cca98c6b60'


def save(name, value):
    with (R / name).open('x', encoding='utf8') as f:
        json.dump(value, f, indent=2)


def main():
    assert m.g('rev-parse', 'HEAD') == HEAD and not m.g('status', '--porcelain')
    old = {}
    for line in m.g('for-each-ref', '--format=%(refname) %(objectname) %(*objectname)', 'refs/tags/').splitlines():
        v = line.split()
        old[v[0]] = (v[1], v[2] if len(v) > 2 else v[1])
    assert len(old) == 1346 and old['refs/tags/' + TAG] == (OBJ, '57acae57199508c239dc864778cfd791bb4c7fe0')
    index = m.REPO / 'history/evidence' / D.name / 'ordinary_complete30_two_profile_audit_and_next_admission_v1/REPORT_CAPTURE_INDEX.json'
    rows = json.loads(index.read_bytes())['entries']
    # Validate already-tracked capture bytes before any new network attempt.
    checked = 0
    for row in rows:
        if 'Git_path' in row:
            assert m.H(m.REPO / row['Git_path']) == row['archived_sha256']
            checked += 1
    raw = m.g('ls-remote', 'origin', 'refs/heads/main', 'refs/tags/*')
    remote = dict(line.split()[::-1] for line in raw.splitlines())
    assert remote['refs/heads/main'] in (BASE, HEAD), 'Concurrent remote change; never force.'
    for tag, (obj, peeled) in old.items():
        assert remote[tag] == obj and remote.get(tag + '^{}', obj) == peeled
    pushed_existing = remote['refs/heads/main'] == BASE
    if pushed_existing:
        m.g('push', 'origin', 'HEAD')
    m.cap.a.verify(rows, old, HEAD, TAG, OBJ)
    v = dict(epoch=time.time(), existing_ordinary_commit=HEAD,
             actual_remote_main_stage_tag_peeled_all1346oldtags_and_trackedSHA_verified=True,
             source_index_entries=len(rows), tracked_capture_rows=checked,
             pushed_existing_objects_only=pushed_existing, record_tag_commit_repeated=False,
             no_GPU_SSH210_249_or_budget=True)
    save('WHITEV2_COMPLETE30_EXISTING_ORDINARY_REMOTE_RECOVERED_ACTUAL.json', v)
    print(json.dumps(v))


if __name__ == '__main__':
    try:
        main()
    except BaseException:
        save('WHITEV2_COMPLETE30_EXISTING_ORDINARY_RECOVERY_ORIGINAL_ERROR_' + str(time.time_ns()) + '.json',
             dict(error=traceback.format_exc(), existing_commit=HEAD,
                  no_record_tag_commit_replay=True, no_GPU_or_budget=True))
        raise
