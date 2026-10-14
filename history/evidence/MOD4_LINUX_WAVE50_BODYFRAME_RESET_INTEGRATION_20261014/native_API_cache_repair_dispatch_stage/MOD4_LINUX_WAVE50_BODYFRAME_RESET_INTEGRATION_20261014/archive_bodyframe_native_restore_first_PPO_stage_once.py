"""One new actual CPU integration stage; no GPU or training work is repeated."""
from pathlib import Path
import importlib
import json
import subprocess
import sys
import time
from datetime import datetime, timezone, timedelta

B = Path(__file__).resolve().parent; W = B.parent; R = B / 'reports'; REPO = W / 'polar-rl-train'
sys.path.insert(0, str(W / 'MOD4_4090_WINDOWS_REPAIR_20261013'))
import append_large_install_evidence_import_reviewed_git as cap


def main():
    ID = 'wave50-birthframe-linux20k-native-restore-and-first-ppo-window'
    dest = REPO / 'history/evidence' / B.name / 'actual_native_restore_first_PPO_stage'
    assert not cap.g('status', '--porcelain') and not dest.exists() and not cap.g('tag', '--list', '*' + ID)
    final = json.loads((R / 'BODYFRAME_OWN_FINAL_FULLTRACE_LOCAL_CPU_VERIFIED.json').read_bytes())
    assert final['passed'] and final['updates'] > 0 and final['actual_parent_guardian_child_out']
    old = cap.a.gitio.refs(); cap.a.FOLDERS = (B,)
    rows, files = cap.capture_streaming(dest)
    sys.path.insert(0, str(REPO / 'archive_tools'))
    rec = importlib.import_module('record_experiment')
    def git(*args):
        if args[:2] == ('add', '--'):
            result = subprocess.run(['git', '-C', str(REPO), 'add', '--pathspec-from-file=-', '--pathspec-file-nul'],
                input=b''.join(x.encode() + b'\0' for x in args[2:]), check=True, capture_output=True)
            return result.stdout.decode().strip()
        return cap.g(*args)
    rec.git = git
    sys.argv = ['record_experiment.py', '--id', ID,
        '--title', 'Validate birth-only orientation on Linux20k and complete the first bounded PPO repair window',
        '--kind', 'training', '--note-file', str(B / 'BODYFRAME_NATIVE_RESTORE_FIRST_PPO_STAGE.md'),
        '--files', *files,
        '--validation', 'Preserve every independent V1-V6 attempt and original error: pre-Kit eager import, articulation getter ABI, raw quaternion unit representation, stale pose-derived heading cache, and targetCPU stale import. New independently frozen scope keeps original Linux522 runtime and complete source e3 whole20k195/107/99 and original DR reward clock geometry. Own14 startup and whole-state disk proofs, new native144 and owned restore120 zeroPPO, then one finite300s formal with original learner. Independent twohost weight and fulltrace CPU review proves9actor changes,17Adam deltas, continuous controls, exact episode reset union and pre-reset BODY/WORLD/birth orientation exposure histogram. Original own parent unique canonical cost and actual exits/two locks free. No new qualification, route/contact causal claim,70mm, gate learning, SDK modification, oldonce replay, kill or data deletion. Laptop GPU paused and3060 evaluations only. Large artifacts indexed by actual path-size-SHA with originals retained; credentials excluded',
        '--push']
    rec.main()
    tag = 'trial-' + datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d') + '-' + ID
    head = cap.g('rev-parse', 'HEAD'); obj = cap.g('rev-parse', tag)
    cap.a.verify(rows, old, head, tag, obj)
    receipt = R / 'BODYFRAME_NATIVE_RESTORE_FIRST_PPO_STAGE_GIT_RECORDED.json'
    assert not receipt.exists()
    receipt.write_text(json.dumps(dict(epoch=time.time(), commit=head, tag=tag, tagobject=obj,
        actual_remote_main_tag_peeled_verified=True, all_oldtags_preserved=len(old), saved_sources=len(rows),
        later_receipts_require_ordinary_supplement=True), indent=2), encoding='utf8')
    print(json.dumps(dict(commit=head, tag=tag, tagobject=obj, remote_verified=True,
                         oldtags_preserved=len(old), saved_sources=len(rows))))


if __name__ == '__main__':
    main()
