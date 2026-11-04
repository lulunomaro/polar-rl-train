"""One frozen delivery cutoff; original recorder unchanged; no physics/raw replay."""
from pathlib import Path
import importlib.util
import json
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parent/'repo-lqr-robust'
ID='mod4v1-terrain-t01-c2fps-j200-delivery'
BASE=Path('history/experiments/mod4v1_t01_c2fps_j200_delivery_20261104')
OUT=REPO/BASE
NOTE='''# Actual C2-style FPS delivery and nominal200mm jump motion

T01 original strict contact gates remain failed; C2 non-contact gates passed earlier. The completed420152 read-only native-distance probe found at most4.77544/3.04452 micrometre wheel gaps, without changing the robot/solver/control/gates. It is deterministic nominal observation, not an independent reliability draw. Stop further same-kind probes and blind tuning.

The actual latestCAD player now assembles C1 leg following with its existing FPS heading outer loop (the C2 mechanism), not two cascaded heading loops. Engine default coord_soft is retained for old formal adapters. The panel explicitly labels limited0.3m/s nominal evidence; full command range remains2m/s, not a claim of high-speed/DR qualification. Initial live PID18668 ran52.65simseconds then crashed natively in Python3.14 Tk.update/PyEval_RestoreThread; source/logs preserved. Revised code separates Tk/GLFW Win32 message-owner threads and removes nested update; actual new PID51820/latest_rm/c2_fps was verified responding, stderr empty at inspection, with continued BALANCE/user turn logs. About10-11FPS on this fullCAD, not real-time/60FPS or exhaustive GUI proof. Live logs here are bounded copies at this archive cutoff, not formal acceptance traces.

J200 source is frozen by its reused child: two completed new nominal800control/16000physics cases on an explicitly added200mm box, not originalCAD. Both fully cross the edge with the real tire meshes and end bearing on two main wheels for3.01/3.86s. This is nominal jump-on-and-stand motion achieved, NOT clean landing or DR reliability. Guide13/36ticks, hard0; baseline guide peak20.36kN, no collision improvement claim. Actual ground-only horizon15 scalar MPC is used during approach/recovery, not aerial/contact MPC. Candidate2 has real iteration-limit/domain fallbacks and solver peak6.5975ms, not hard WCET. Initial software attempt20PHY/zero complete rows is retained; total32020newPHY. No thirdcase/DR/oldcase/holdout rerun. Baseline buffered-trace/phase-label caveats are documented in its README; original scores unchanged.

Small selected source/config/results and failures are archived. Large JSONL traces remain external with path/size only, hash unknown here; no raw payload read or archive-only rehash. Earlier PH12 pending stays pending. Original record_experiment.py is imported once, with only the existing in-memory sparse-add adapter, and a unique annotated tag. Push only the own branch/tag, atomically and without force. No other worktree/index/main, dependency install, hardware or simulation is touched by archival.
'''

def main():
    def git_read(*args):
        return subprocess.run(['git','-C',str(REPO),*args],check=True,capture_output=True,text=True).stdout.strip()
    branch='mod4v1-lqr-mpc-robust'
    if git_read('branch','--show-current')!=branch: raise RuntimeError('Wrong branch')
    if git_read('diff','--cached','--name-only'): raise RuntimeError('Existing staged changes')
    if (REPO/f'history/experiments/20261104-{ID}.json').exists(): raise RuntimeError('Record exists; continue existing objects')
    OUT.mkdir(parents=True,exist_ok=False)
    selected=[]
    def put(rel,data):
        p=OUT/rel; p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(data)
        selected.append(p.relative_to(REPO).as_posix())
    sources=['TERRAIN_ADAPTATION_TASKS_V1.md']
    sources += ['RM_FPS_PLAYER_V1/'+name for name in ('runtime.py','player.py','Start_RM_FPS.bat','revisions/player_c2fps_before_tk_thread001.py','player_c2fps_20261104_204056.stdout.log','player_c2fps_20261104_204056.stderr.log','player_c2fps_tkowner_20261104_205204.stdout.log','player_c2fps_tkowner_20261104_205204.stderr.log')]
    sources += ['RM_ROBUSTNESS_V1/run_t01_contact_distance_probe_v2.py','RM_ROBUSTNESS_V1/contact_distance_probe_v2/T01_PROTOCOL_V1.json']
    probe=Path('RM_ROBUSTNESS_V1/contact_distance_probe_v2/runs/t01_c2_contact_distance_420152_probe002')
    sources += [(probe/name).as_posix() for name in ('config.json','protocol.json','meta.json','result.json','contact_distance_summary.json')]
    jdir=Path('JUMP200_LQR_MPC_V1')
    sources += [(jdir/name).as_posix() for name in ('bridge200.py','derive_baseline_once.py','run_case.py','baseline001.json','derive_capture_v2.py','run_capture_v2.py','capture_v2_001.json','README.md','STAGE_RESULT.json','revisions/run_case_before_telemetry_fix001.py','baseline001.log','baseline001_attempt002.log','capture_v2_001.log')]
    failed=jdir/'runs/j200_nominal_baseline_200001'
    sources += [(failed/name).as_posix() for name in ('config.json','SOURCE_MANIFEST.json','ERROR.json')]
    complete=[jdir/'runs'/name for name in ('j200_nominal_baseline_200001_attempt002','j200_capture_v2_nominal_200002')]
    for case in complete:
        sources += [(case/name).as_posix() for name in ('config.json','SOURCE_MANIFEST.json','result.json')]
    sources += [(complete[0]/'guide_events_saved.json').as_posix()]
    external=[]
    raw_paths=[probe/'trace.jsonl',probe/'contact_trace.jsonl']
    for case in complete: raw_paths += [case/'trace.jsonl',case/'physics_contact_audit.jsonl']
    for rel in raw_paths:
        p=ROOT/rel
        external.append(dict(path=str(p),bytes=p.stat().st_size,sha256=None,sha_status='UNKNOWN_NOT_READ_OR_HASHED_FOR_ARCHIVE'))
    for rel in sources: put(Path('payload')/rel,(ROOT/rel).read_bytes())
    put('NOTE.md',NOTE.encode('utf8'))
    put('EXTERNAL_ARTIFACTS.json',(json.dumps(external,indent=2)+'\n').encode('utf8'))
    put(Path(__file__).name,Path(__file__).read_bytes())
    listrel=(BASE/'SELECTED_FILES.txt').as_posix()
    put('SELECTED_FILES.txt',('\n'.join(selected+[listrel])+'\n').encode('utf8'))
    sys.path.insert(0,str(REPO/'archive_tools'))
    spec=importlib.util.spec_from_file_location('original_delivery_recorder',REPO/'archive_tools/record_experiment.py')
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    original=mod.git
    def git(*args):
        if args and args[0]=='add': args=('add','--sparse',*args[1:])
        try: return original(*args)
        except subprocess.CalledProcessError as e:
            print('ORIGINAL_HELPER_GIT_FAILURE',e.stdout,e.stderr,flush=True); raise
    mod.git=git
    sys.argv=['record_experiment.py','--id',ID,'--title','Deliver C2-style FPS control and nominal200mm LQR-ground-MPC motion','--kind','diagnostic','--note-file',str(OUT/'NOTE.md'),'--validation','Actual latestCAD GUI plus two completed nominal200mm jumps; original strict contact/clean/DR gaps retained. No physics rerun for archive.','--files',*selected]
    mod.main()
    tag='trial-20261104-'+ID
    head=git_read('rev-parse','HEAD'); tagobj=git_read('rev-parse',tag)
    subprocess.run(['git','-C',str(REPO),'push','--atomic','origin',f'HEAD:refs/heads/{branch}',f'refs/tags/{tag}:refs/tags/{tag}'],check=True)
    remote=git_read('ls-remote','origin',f'refs/heads/{branch}',f'refs/tags/{tag}',f'refs/tags/{tag}^{{}}')
    refs={line.split()[1]:line.split()[0] for line in remote.splitlines()}
    if refs.get('refs/heads/'+branch)!=head or refs.get('refs/tags/'+tag)!=tagobj or refs.get('refs/tags/'+tag+'^{}')!=head: raise RuntimeError('Remote identity mismatch')
    print(json.dumps(dict(commit=head,tag=tag,tag_object=tagobj,selected_count=len(selected),remote=refs),indent=2),flush=True)

if __name__=='__main__': main()
