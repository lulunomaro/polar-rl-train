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
    ID = 'wave50-birthframe-reset-and-whole20k-restore-chain-cpu-prepared'
    dest = REPO / 'history/evidence' / B.name / 'reset_restore_CPU_stage'
    assert not cap.g('status', '--porcelain') and not dest.exists() and not cap.g('tag', '--list', '*' + ID)
    first = json.loads((R / 'BODYFRAME_WHOLE20K_RESET_COMMAND_SAVE_CHAIN_CPU_ACTUAL.json').read_bytes())
    second = json.loads((R / 'BODYFRAME_TWO_STAGE_OLD_RESTORE_FIRST_SAVE_RESUME_COMPOSITION_CPU_ACTUAL.json').read_bytes())
    work = json.loads((B / 'NEXT_BODYFRAME_ACTUAL_TARGET_CPU_NATIVE_FULLRESTORE_WORK_ORDER.json').read_bytes())
    assert first['passed_CPU_reset_command_checkpoint_component'] and second['passed_CPU_restore_save_resume_composition']
    assert work['actual_target_or_GPU_or_PPO_admitted'] is False
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
        '--title', 'Prepare birth-only Wave50 orientation reset and whole20k restore/save composition on CPU',
        '--kind', 'diagnostic', '--note-file', str(B / 'BODYFRAME_RESET_AND_RESTORE_CPU_STAGE.md'),
        '--files', *files,
        '--validation', 'Actual whole e3 source195tensors107float99perenv N20000 and real25200point collision bank unchanged. Synthetic CPU scene only: original reset once then episode increment,1410pi/1410unrotated among2820 Wave births,15selected reset rows preserve nonselected roots/state, command subset idempotence, explicit BODY/WORLD audit,3control12callback fixture histogram before reset, owned checkpoint disk roundtrip. First-transition and own-scope restore/save callback compositions preserve actorcriticstdAdam/left initialization and consume exactly one original new birth each; CPU/globalRNG exact/no CUDA,19 negative cases across components. CPU fixture checkpoints forbidden as GPU sources, no actual thirteen CUDA receipts or real PhysX pass claimed. Original adapter SHA restored/preserved and separate backend-guard v2 prepared; shell quoting/schema KeyError/nativeworker v1 SyntaxError original failures and independent fixes kept. Nativeworker v2 compiled zeroPPO-only; actual target/sourcefreeze/resources/two-fcntl/budget/native getter-heading-setter/fullstate/physical raw review still required. No remote transport/GPU/PPO/canonical mutation/kill/delete or S4 learning. Large PT index-only original retained, credentials excluded.',
        '--push']
    rec.main()
    tag = 'trial-' + datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d') + '-' + ID
    head = cap.g('rev-parse', 'HEAD'); obj = cap.g('rev-parse', tag)
    cap.a.verify(rows, old, head, tag, obj)
    receipt = R / 'BODYFRAME_RESET_RESTORE_CPU_STAGE_GIT_RECORDED.json'
    assert not receipt.exists()
    receipt.write_text(json.dumps(dict(epoch=time.time(), commit=head, tag=tag, tagobject=obj,
        actual_remote_main_tag_peeled_verified=True, all_oldtags_preserved=len(old), saved_sources=len(rows),
        later_receipts_require_ordinary_supplement=True), indent=2), encoding='utf8')
    print(json.dumps(dict(commit=head, tag=tag, tagobject=obj, remote_verified=True,
                         oldtags_preserved=len(old), saved_sources=len(rows))))


if __name__ == '__main__':
    main()
