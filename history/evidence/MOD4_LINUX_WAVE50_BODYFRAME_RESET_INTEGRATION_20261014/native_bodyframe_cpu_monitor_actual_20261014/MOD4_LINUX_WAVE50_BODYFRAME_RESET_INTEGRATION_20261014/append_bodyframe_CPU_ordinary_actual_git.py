"""Append saved supplementary evidence without recording another trial/tag."""
from pathlib import Path
import json
import subprocess
import sys
import time
import archive_bodyframe_reset_restore_CPU_stage_once as stage

B = stage.B; REPO = stage.REPO; cap = stage.cap


def main():
    label = sys.argv[1]
    assert label.replace('_', '').replace('-', '').isalnum() and not cap.g('status', '--porcelain')
    dest = REPO / 'history/evidence' / B.name / label
    assert not dest.exists()
    old = cap.a.gitio.refs(); cap.a.FOLDERS = (B,)
    rows, files = cap.capture_streaming(dest)
    subprocess.run(['git', '-C', str(REPO), 'add', '--pathspec-from-file=-', '--pathspec-file-nul'],
        input=b''.join(x.encode() + b'\0' for x in files), check=True, capture_output=True)
    cap.g('commit', '-m', 'Append birthframe CPU integration monitor and source evidence: ' + label)
    cap.g('push', 'origin', 'HEAD')
    head = cap.g('rev-parse', 'HEAD'); cap.a.verify(rows, old, head)
    print(json.dumps(dict(epoch=time.time(), commit=head, remote_main_verified=True,
        all_oldtags_preserved=len(old), saved_sources=len(rows), tracked_SHA_verified=True, no_new_trial_or_tag=True)))


if __name__ == '__main__':
    main()
