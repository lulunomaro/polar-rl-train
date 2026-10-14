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
    ID = 'wave50-birthframe-first-ppo-frozen-full80-improved26-26'
    dest = REPO / 'history/evidence' / 'MOD4_3060_BODYFRAME_FIRST_FULL80_20261014' / 'full80_complete_stage'
    assert not cap.g('status', '--porcelain') and not dest.exists() and not cap.g('tag', '--list', '*' + ID)
    final = json.loads((R / 'BODYFRAME_OWN_FINAL_FULLTRACE_LOCAL_CPU_VERIFIED.json').read_bytes())
    assert final['passed'] and final['updates'] > 0 and final['actual_parent_guardian_child_out']
    old = cap.a.gitio.refs(); cap.a.FOLDERS = (B, W / 'MOD4_3060_BODYFRAME_FIRST_FULL80_20261014')
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
        '--title', 'Review own first birthframe PPO frozen Wave50 full80 improvement to26/27 in both directions',
        '--kind', 'evaluation', '--note-file', str(W / 'MOD4_3060_BODYFRAME_FIRST_FULL80_20261014/BODYFRAME_FIRST_FULL80_COMPLETE_EVALUATION_STAGE.md'),
        '--files', *files,
        '--validation', 'Own complete firstPPO model32830 f516 source from Linux20k6updates2.88Msteps and independent wholecore195/107/99+ownedBODY state/14startup/fulltrace/unique331.33217s actual parent cost verified. New3060 full80 frozen1500 original15s/6000callbacks all raw/source twohost SHA, query1e-6/contact impulse COMlink native motor bounds/strict1Nbefore-after200mm/all valid failedprefix passed. Direct actual firstphysics fullrootq30params recipesassignment RNGqueues exact to e3:24/26 to26/26, env6/69 improve and no transit regression, ordinary1 remains, failures15/67 remain. Original missingEXIT_NATURAL retained plus independent complete data EXIT0 PIDout nativeOSlockfree closeout. All WDDM remote desktop and interactive terminal guard original rejections and actual exactrole proof, UTF8/escape/sysPath/globalplaceholder CPU errors and only unexecuted publication continuation retained, no GPU replay or interference with otherAI. Frozen0PPO no budget. Three inherited skills still pending; no qualification or70/MoE/globalbest. Large original pathsizesSHA kept and credentials excluded',
        '--push']
    rec.main()
    tag = 'trial-' + datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d') + '-' + ID
    head = cap.g('rev-parse', 'HEAD'); obj = cap.g('rev-parse', tag)
    cap.a.verify(rows, old, head, tag, obj)
    receipt = R / 'BODYFRAME_FIRST_FROZEN_FULL80_COMPLETE_STAGE_GIT_RECORDED.json'
    assert not receipt.exists()
    receipt.write_text(json.dumps(dict(epoch=time.time(), commit=head, tag=tag, tagobject=obj,
        actual_remote_main_tag_peeled_verified=True, all_oldtags_preserved=len(old), saved_sources=len(rows),
        later_receipts_require_ordinary_supplement=True), indent=2), encoding='utf8')
    print(json.dumps(dict(commit=head, tag=tag, tagobject=obj, remote_verified=True,
                         oldtags_preserved=len(old), saved_sources=len(rows))))


if __name__ == '__main__':
    main()
