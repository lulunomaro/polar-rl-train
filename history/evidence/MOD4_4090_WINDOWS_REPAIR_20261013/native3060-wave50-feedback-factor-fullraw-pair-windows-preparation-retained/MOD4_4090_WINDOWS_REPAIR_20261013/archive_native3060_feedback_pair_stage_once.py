"""One annotated real evaluation stage; stream large retained originals."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import importlib, json, subprocess, sys, time, traceback

D = Path(__file__).resolve().parent
W = D.parent
REPO = W / 'polar-rl-train'
E = W / 'MOD4_3060_DIRECT_FACTOR_20261013'
ID = 'native3060-wave50-feedback-factor-fullraw-pair-windows-preparation-retained'
DEST = REPO / 'history/evidence' / D.name / ID

def main():
    sys.path.insert(0, str(D))
    import append_large_install_evidence_import_reviewed_git as safe
    g = safe.g
    assert not g('status', '--porcelain') and not g('tag', '--list', '*' + ID)
    assert not DEST.exists(), 'consumed capture; resume existing Git objects'
    names = ('DIRECT3060_BASELINE120_COMPLETE_INDEPENDENT_CPU_ACTUAL_REVIEW.json',
             'DIRECT3060_BASELINE1500_COMPLETE_INDEPENDENT_CPU_ACTUAL_REVIEW.json',
             'DIRECT3060_D3CURRENT1500_COMPLETE_PAIRED_CPU_ACTUAL_REVIEW.json')
    reviews = {name: json.loads((E / 'reports' / name).read_bytes()) for name in names}
    assert all(row['passed'] for row in reviews.values())
    pair = reviews[names[-1]]
    assert pair['controls'] == 1500 and pair['envs'] == 8 and pair['callbacks'] == 6000
    assert pair['initial_full_qXYZ_DR_queue_captured_RNG_exact_to_reference']
    assert pair['ordinary_events'] == 0 and pair['truncation_unique'] == 0
    assert pair['fullroute']['complete_double1N_envs'] == 3
    note = D / 'NATIVE3060_FEEDBACK_PAIR_ACTUAL_STAGE_REPORT.md'
    assert not note.exists()
    note.write_text('''# Native3060 Wave50 frozen-policy feedback factor pair

Human authorized isolated factors on shared GPU, then paused all local GPU work and moved evaluations to3060. Newly admitted direct-local native3060 backend uses pinned Sim6.0.1/Lab6.1.14/Torch2.10/TD.14, original91d actor, original MOD4 robot/geometry/clock/white3 initialization. No legacy Linux RPC, old poller or mirror restored. New120control admission completed, then distinct1500control baseline and D3-current factor each once under original shared OSlock. Actual complete raw/query and parent exits retained; original missing EXIT_NATURAL after Kit app.close remains false and independent closeout uses exit0/fullraw/actual parent-child absence/lockfree.

Eight environments include seven moving and one standing. Original50mm peak-trough tenwaves2.406422727m/.4m approach/15s/bothwheels1N/after200mm/query1e-6/6000callbacks/contact integration/COM and hardware bounds retained. Baseline moving completion2/7(env0,5), D3-current3/7(env0,4,5); only env4 newly completes. Initial q/XYZ/allDR/queues and25 actually captured RNG stream bytes exact. Ordinary and truncation0; all effective failed prefixes/raw costs retained. This is small paired evidence of feedback-latency sensitivity, not a unique cause or50mm qualification. No production DR, reward, command, tolerances or expert weights changed by this evaluation. Baseline and factor fresh-white3 actor inference are not complete training-DR restore, not cross-backend PhysX equivalence. Parent unique costs/noPPO classifications and all original errors remain.

Windows4090 environment and full20k target preparation are captured at their actual current stages, including download/installer/wheel metadata/CPU source proofs and failures. The complete coherent d05c20k107/99 donor remains original; no128-to20k splice. TargetCPU/SDK/native/CUDA/fullrestore/PPO statuses come only from actual receipts; preparation is not future pass. New backend readback gaps and their independent preparation must retain the original V5 bytes. Local laptop GPU remains paused, WASD untouched, original Linux main/once/canonical not resumed. Original005 total1188000/seven extensions unchanged, pending parent costs are evidence rather than second canonical authority. All large originals retained with actual path/bytes/streamSHA only; no credentials archived.

All saved success/failure/false/errors/rejections/unused source/reports/receipts captured; subsequent new reports require ordinary supplements. Push failure continues existing commit/tag objects without replaying record or experiment. Git is independent of training.
''', encoding='utf8')
    old = safe.a.gitio.refs()
    rows, files = safe.capture_streaming(DEST)
    sys.path.insert(0, str(REPO / 'archive_tools'))
    rec = importlib.import_module('record_experiment')
    def recorded_git(*args):
        if args[:2] == ('add', '--'):
            p = subprocess.run(['git', '-C', str(REPO), 'add', '--pathspec-from-file=-', '--pathspec-file-nul'], input=b''.join(str(x).encode('utf8') + b'\0' for x in args[2:]), capture_output=True, check=True)
            return p.stdout.decode('utf8').strip()
        return g(*args)
    rec.git = recorded_git
    sys.argv = ['record_experiment.py', '--id', ID, '--title', 'Audit new native3060 Wave50 feedback factor pair and retain Windows preparation', '--kind', 'evaluation', '--note-file', str(note), '--files', *files, '--validation', 'New120 admission and distinct1500 baseline/D3 factor fullraw actual complete; original physics thresholds, initialization, captured stream bytes, failed prefixes, parent exit and shared OSlock reviewed. Baseline2/7 to factor3/7 only env4. No qualification or production DR change. Windows installation/target proofs and original false retained at actual stages; no local GPU or canonical mutation.', '--push']
    rec.main()
    tag = 'trial-' + datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d') + '-' + ID
    head, obj = g('rev-parse', 'HEAD'), g('rev-parse', tag)
    safe.a.verify(rows, old, head, tag, obj)
    result = dict(epoch=time.time(), commit=head, tag=tag, tagobject=obj, actual_remote_main_tag_peeled_verified=True, actual_tracked_SHA_verified=True, all_old_tags_preserved=len(old), saved_sources=len(rows), later_reports_require_supplement=True)
    (D / 'reports/NATIVE3060_FEEDBACK_PAIR_STAGE_GIT_RECORDED.json').write_text(json.dumps(result, indent=2), encoding='utf8')
    print(json.dumps(result))

if __name__ == '__main__':
    try:
        main()
    except BaseException:
        (D / 'reports' / ('NATIVE3060_PAIR_STAGE_GIT_ERROR_' + str(time.time_ns()) + '.json')).write_text(json.dumps(dict(epoch=time.time(), error=traceback.format_exc(), continue_existing_objects_do_not_record_tag_commit_or_GPU_replay=True), indent=2), encoding='utf8')
        raise
