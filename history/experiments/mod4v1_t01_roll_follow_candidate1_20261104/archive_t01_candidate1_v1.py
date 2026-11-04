"""One real C1 checkpoint, original recorder with narrow sparse-add adapter only."""
from pathlib import Path
import importlib.util
import json
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parent/'repo-lqr-robust'
BASE=Path('history/experiments/mod4v1_t01_roll_follow_candidate1_20261104')
OUT=REPO/BASE
CASE=Path('RM_ROBUSTNESS_V1/roll_follow_v1/runs/t01_c1_nominal_slow_420121_001')
NOTE='''# T01 candidate 1: much less roll, but overall low-speed screen still failed

Parent retained the failing nominal baseline and its frozen gates. Bounded saved-data analysis found actual persistent roll rather than a large attitude-estimator error; it did not identify terrain height or prove unique causality. The baseline analysis JSON/short note are included, with no old raw reread for this archive.

## Candidate change

The new sensor-only controller uses public linkage FK and estimated orientation to infer relative wheel-center height. It adjusts opposite left/right joint references, retaining their exact common nominal hip/crank reference, original common sagittal P25 K, shaper, yaw loop, estimator, motor limits and processed-target PD/D4/DC path. It has a bounded height filter/slew, public linkage inverse and reference-rate limit. Its bilateral-ground prior is not an online contact detector, terrain-height measurement or flight policy. It is not wired into the live UI or moving-jump action. Original baseline source and protocol were not edited.

A new protocol version predeclared this candidate and fresh seed range 420120–420125; ALL command, duration, score-window and gate values remain the same as the original T01. Only nominal_slow420121_001 was run; other cases paused after its failure.

## Actual result

One new fresh model/DR instance, 12 seconds, 1200 controls, 24000 physics steps; parent job pwsh-6dca99d9f4dd45ac completed exit 0 and was collected. There are 20000 scored 2kHz contact points. Whole-case time 43.6168595 s; command time 4.9888272 s is aggregate Python wall time, not ARM WCET.

- Roll peak dropped from baseline .42570214395 rad to .04726674114 rad (about 24.39 to 2.71 deg); roll RMS .01617054809 rad. Pitch peak .07901136977 rad and RMS .02771260975 rad. All four attitude gates passed.
- Steady velocity RMSE .04317897167 m/s passed.
- Overall case_screen_pass=false: progress 1.10562613554 m, lateral .24011704880 m and final speed RMS .138384049998 m/s failed their original gates.
- Main-wheel support .8771/.92795 failed; unsupported samples 270, each run at most .0005 s. Guide duty .0073 and longest .0015 s passed their gates; hard contact 0. Peak summed guide normal 268.502 N and total normal 724.898 N are simulated samples, not a hardware impact qualification.
- Inverse diagnostics: no hold, no height clip, max residual below 1e-7 m, max joint reference delta .26963109 rad. A successful inverse is not successful whole-body behavior.

## Stop and next step

Candidate count is 1/3. Do not run the remaining stationary/DR cases yet. Compare saved C1 stop-window estimated velocity, true velocity, yaw/lateral motion and leg states in one bounded new-trace read before selecting a second mechanism. Do not reopen old baseline raw or relax the gates. T01 is not complete and T02–T36 have not started.

The durable task file is included up to this checkpoint. Source/results/analysis of the two original formal baselines were already pushed in commit 5779f03e9e1eaa5a98febe0c338b08564e83dbe5. This new checkpoint adds completed baseline diagnosis, candidate source/protocol and its actual failure. Active C1 stop analysis is excluded and pending the next real stage. Other old PH12 pending work remains pending.

Large traces are indexed by known path/size with SHA unknown; no archive-only payload read/hash. Original record_experiment.py stays unchanged; one in-memory git add --sparse insertion handles the known own-worktree sparse exclusion. No sparse config, other worktree/index or main ref was modified. The helper runs once without push; push existing objects explicitly to own branch/tag. No physics/QA/native/hardware is executed by this archive script.
'''


def main():
    branch=subprocess.run(['git','-C',str(REPO),'branch','--show-current'],check=True,capture_output=True,text=True).stdout.strip()
    if branch!='mod4v1-lqr-mpc-robust':raise RuntimeError('Wrong branch')
    dest=REPO/'history/experiments/20261104-mod4v1-terrain-t01-candidate1.json'
    if dest.exists():raise RuntimeError('Record exists: continue objects, never reinvoke helper')
    OUT.mkdir(parents=True,exist_ok=False)
    selected=[]
    def put(rel,data):
        p=OUT/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        selected.append(p.relative_to(REPO).as_posix())
    sources=['TERRAIN_ADAPTATION_TASKS_V1.md','RM_ROBUSTNESS_V1/controller_roll_follow_v1.py',
      'RM_ROBUSTNESS_V1/run_t01_roll_follow_v1.py','RM_ROBUSTNESS_V1/roll_follow_v1/T01_PROTOCOL_V1.json',
      'RM_ROBUSTNESS_V1/slow_failure_analysis001/analysis.json','RM_ROBUSTNESS_V1/slow_failure_analysis001/summary.md']
    sources += [(CASE/name).as_posix() for name in ('config.json','protocol.json','meta.json','result.json','candidate_diagnostics.json')]
    sources += ['RM_ROBUSTNESS_V1/roll_follow_v1/t01_c1_nominal_slow_420121_001.console.log']
    for rel in sources:put(Path('payload')/rel,(ROOT/rel).read_bytes())
    external=[dict(path=str(ROOT/CASE/name),bytes=(ROOT/CASE/name).stat().st_size,sha256=None,
      sha_status='UNKNOWN_NOT_READ_OR_HASHED_FOR_ARCHIVE') for name in ('trace.jsonl','contact_trace.jsonl')]
    put('NOTE.md',NOTE.encode('utf8'))
    put('EXTERNAL_ARTIFACTS.json',(json.dumps(external,indent=2)+'\n').encode('utf8'))
    put(Path(__file__).name,Path(__file__).read_bytes())
    listrel=(BASE/'SELECTED_FILES.txt').as_posix()
    put('SELECTED_FILES.txt',('\n'.join(selected+[listrel])+'\n').encode('utf8'))
    sys.path.insert(0,str(REPO/'archive_tools'))
    spec=importlib.util.spec_from_file_location('original_c1_recorder',REPO/'archive_tools/record_experiment.py')
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    original=mod.git
    def git(*args):
        if args and args[0]=='add':args=('add','--sparse',*args[1:])
        try:return original(*args)
        except subprocess.CalledProcessError as e:
            print('ORIGINAL_HELPER_GIT_FAILURE stdout=',e.stdout,'stderr=',e.stderr,flush=True);raise
    mod.git=git
    sys.argv=['record_experiment.py','--id','mod4v1-terrain-t01-candidate1','--title',
      'Record T01 candidate1 roll improvement and remaining stop/support failures','--kind','diagnostic',
      '--note-file',str(OUT/'NOTE.md'),'--validation',
      'New 12s/1200-control/24000-physics candidate: attitude passed, overall stop/lateral/support failed; T01 still in progress.',
      '--files',*selected]
    mod.main()


if __name__=='__main__':main()
