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
    ID = 'wave50-birthframe-native-api-and-derived-cache-repair-dispatched'
    dest = REPO / 'history/evidence' / B.name / 'native_API_cache_repair_dispatch_stage'
    assert not cap.g('status', '--porcelain') and not dest.exists() and not cap.g('tag', '--list', '*' + ID)
    assert (R / 'SDK_BIRTH_DERIVED_CACHE_V5_INDEPENDENT_CPU_REPAIR_ACTUAL.json').is_file()
    assert (R / 'BODYFRAME_PIPELINE_V6_MATERIALIZE_DISPATCH_INTENT.json').is_file()
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
        '--title', 'Preserve Linux20k native ABI failures and deploy independent pose-derived cache repair',
        '--kind', 'repair', '--note-file', str(B / 'BODYFRAME_NATIVE_CACHE_REPAIR_DEPLOYMENT_STAGE.md'),
        '--files', *files,
        '--validation', 'Preserve every V1-V6 source-bound original failure and dispatch receipt. Read-only actual installed ArticulationView API and timestamped cache source captured; original13 GPU restore proofs and saved native/data witnesses retained. Independent CPU cache invalidation changes no simulation timestamp or joint history, SDK source, physical tolerance, RL parameter or source weight. Fresh V6 target CPU full195/107/99 original20k and522runtime SHA passed; unique native144->restore120->formal300 finite parent dispatched. At archive snapshot no new14 startup or savedPPO proof claimed; future actual completion or failure is supplementary. ZeroPPO stages cannot charge canonical; original formal parent only may account its actual unique interval. No oldonce replay, kill, delete, extra GPU worker,70mm, qualification or S4 learning. Large original artifacts retained and indexed; credentials excluded',
        '--push']
    rec.main()
    tag = 'trial-' + datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d') + '-' + ID
    head = cap.g('rev-parse', 'HEAD'); obj = cap.g('rev-parse', tag)
    cap.a.verify(rows, old, head, tag, obj)
    receipt = R / 'BODYFRAME_NATIVE_CACHE_REPAIR_DEPLOYMENT_GIT_RECORDED.json'
    assert not receipt.exists()
    receipt.write_text(json.dumps(dict(epoch=time.time(), commit=head, tag=tag, tagobject=obj,
        actual_remote_main_tag_peeled_verified=True, all_oldtags_preserved=len(old), saved_sources=len(rows),
        later_receipts_require_ordinary_supplement=True), indent=2), encoding='utf8')
    print(json.dumps(dict(commit=head, tag=tag, tagobject=obj, remote_verified=True,
                         oldtags_preserved=len(old), saved_sources=len(rows))))


if __name__ == '__main__':
    main()
