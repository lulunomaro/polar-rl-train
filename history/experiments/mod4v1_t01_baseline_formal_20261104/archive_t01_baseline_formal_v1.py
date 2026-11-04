"""Archive the two collected T01 baselines once; never run physics or retry records."""
from pathlib import Path
import importlib.util
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent / 'repo-lqr-robust'
IDENT = 'mod4v1-terrain-t01-baseline-formal'
PREFIX = Path('history/experiments/mod4v1_t01_baseline_formal_20261104')
OUT = REPO / PREFIX
CASES = ('t01_formal_nominal_stand_420110_001', 't01_formal_nominal_slow_420111_001')
NOTE = '''# T01 full-CAD formal baseline: stand passed, low-speed failed

This is a failure-preserving intermediate checkpoint, not completion of T01.

## Exact execution and unchanged mechanism

The original latest_rm CAD flat_run spawn, 0.5 ms physics, 100 Hz control, source robot, closed chains, motor limits, processed-target D4/PD/DC path and coord_soft controller were retained. Only read-only post-step contact grading was added. Environment contacts cover every collidable world-body geom, not the single ground alias. The source contact-stable MULTICCD-disabled flag is specific to latest_rm.

Each case built one fresh model and one FullDR instance, was nominal, ran 12 s / 1200 controls / 24000 physics steps, and completed with exit 0. Both parent jobs were collected: pwsh-1a4b8120d4384f4d and pwsh-5b05560b4857418a. Each has 20000 contact samples over the predeclared 2–12 s window; current freejoint truth and cached dynamics epochs remain distinguished. Control receives no truth/contact grading.

## Results under unchanged T01_ENGINEERING_SCREEN_V1 gates

- nominal_stand, seed 420110: all case checks passed. Scored pitch peak .0025984496573422055 rad, roll peak .026160619362879636 rad, XY maximum .013051287089074883 m. Both main wheels supported for 100% of the scored window; guide, hard and unsupported sample counts were zero. Whole case wall time 39.5285068 s.
- nominal_slow, seed 420111: robot screen FAILED, not a software error. Progress 1.5033886882398866 m, steady speed RMSE .043550267135277 m/s and final speed RMS .007874197799045423 m/s passed. Roll peak .4257021439501015 rad and RMS .27322424819159674 rad failed. Main wheel support duty .87535/.92525 failed. There were 370 unsupported normal-force samples; the longest consecutive run was only .0005 s, so this is not labeled a continuous .185 s flight. Guide/hard counts were zero. Whole case wall time 40.708311 s.
- The original protocol was not relaxed. The remaining four DR cases were paused after this baseline failure. T01 is still in progress, with one passed and one failed baseline; T02–T36 have not started.

## Next bounded action and preservation

Analyze the saved failing trace once, then form at most three mechanism-grounded candidates. Do not rerun the pilot or these consumed IDs. Do not transfer a passing stationary result to moving robustness. Old frozen gains, heldouts, model, failed records, UI sources and other pending hardware work are untouched. Moving-jump candidate remains unexecuted.

The prior ledger/pilot/flat-source checkpoint is commit 4e4916361e505175e7203ae602377f95ec6b258a, annotated tag trial-20261104-mod4v1-terrain-ledger-t01-pilot. This checkpoint adds the final audit/runner, the actual two formal cases and updated task state. Active trace analysis and future candidate source/results are excluded until complete. Older PH12 pending work is not represented as archived.

Raw traces are indexed by actual path and size only; no large payload was reopened or hashed for this archive. Original record_experiment.py is unchanged. Its add call receives only a narrow in-memory --sparse insertion because this own worktree's sparse-checkout exclusion was already observed. No sparse configuration, old index, RL worktree, main ref or dependency was modified. Record helper is called once, without --push; push existing objects separately to explicit own branch/tag only. No physics, QA, native build or hardware execution occurs here.
'''


def main():
    branch = subprocess.run(['git', '-C', str(REPO), 'branch', '--show-current'], check=True, capture_output=True, text=True).stdout.strip()
    if branch != 'mod4v1-lqr-mpc-robust':
        raise RuntimeError('Wrong worktree branch')
    if (REPO/'history/experiments/20261104-mod4v1-terrain-t01-baseline-formal.json').exists():
        raise RuntimeError('Record already exists; continue its objects, never rerun helper')
    OUT.mkdir(parents=True, exist_ok=False)
    selected = []
    def put(rel, data):
        dest = OUT/rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        selected.append(dest.relative_to(REPO).as_posix())
    def copy_source(rel):
        src = ROOT/rel
        if not src.is_file():
            raise RuntimeError('Missing selected evidence: '+str(src))
        put(Path('payload')/rel, src.read_bytes())
    for rel in ('TERRAIN_ADAPTATION_TASKS_V1.md', 'RM_ROBUSTNESS_V1/T01_PROTOCOL_V1.json',
                'RM_ROBUSTNESS_V1/run_t01_formal.py', 'RM_ROBUSTNESS_V1/t01_contact_audit.py',
                'physics_bridge_contact_audit_v1.py', 'physics_bridge_v4_grade.py',
                'RM_FPS_PLAYER_V1/runtime.py'):
        copy_source(rel)
    external = []
    for case in CASES:
        rel = Path('RM_ROBUSTNESS_V1/runs')/case
        for name in ('config.json', 'protocol.json', 'meta.json', 'result.json'):
            copy_source(rel/name)
        copy_source(Path('RM_ROBUSTNESS_V1')/(case+'.console.log'))
        for name in ('trace.jsonl', 'contact_trace.jsonl'):
            src = ROOT/rel/name
            external.append(dict(path=str(src), bytes=src.stat().st_size,
                sha256=None, sha_status='UNKNOWN_NOT_READ_OR_HASHED_FOR_ARCHIVE',
                kind='100Hz_control' if name=='trace.jsonl' else '2kHz_contact_scoring_window'))
    put('NOTE.md', NOTE.encode('utf-8'))
    put('EXTERNAL_ARTIFACTS.json', (json.dumps(external, indent=2)+'\n').encode('utf-8'))
    put('archive_t01_baseline_formal_v1.py', Path(__file__).read_bytes())
    # Include the path list itself without hashing any external trace.
    list_rel = (PREFIX/'SELECTED_FILES.txt').as_posix()
    put('SELECTED_FILES.txt', ('\n'.join(selected+[list_rel])+'\n').encode('utf-8'))
    sys.path.insert(0, str(REPO/'archive_tools'))
    spec = importlib.util.spec_from_file_location('t01_original_recorder', REPO/'archive_tools/record_experiment.py')
    recorder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(recorder)
    original_git = recorder.git
    def git(*args):
        if args and args[0] == 'add':
            args = ('add', '--sparse', *args[1:])
        try:
            return original_git(*args)
        except subprocess.CalledProcessError as exc:
            print('ORIGINAL_HELPER_GIT_FAILURE stdout=', exc.stdout, 'stderr=', exc.stderr, flush=True)
            raise
    recorder.git = git
    sys.argv = ['record_experiment.py', '--id', IDENT,
        '--title', 'Record T01 full-CAD stand pass and low-speed roll/support failure',
        '--kind', 'diagnostic', '--note-file', str(OUT/'NOTE.md'),
        '--validation', 'Two 12s cases, 2400 controls/48000 physics, 40000 scored contacts; stand passed, slow roll/support failed; T01 in progress.',
        '--files', *selected]
    recorder.main()


if __name__ == '__main__':
    main()
