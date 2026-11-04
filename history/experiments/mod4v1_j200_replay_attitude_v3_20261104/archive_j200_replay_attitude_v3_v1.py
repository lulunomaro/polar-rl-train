"""One completed replay/V3 cutoff. No simulation, old raw hash or helper modification."""
from pathlib import Path
import importlib.util
import json
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parent/'repo-lqr-robust'
ID='mod4v1-j200-replay-attitude-v3'
BASE=Path('history/experiments/mod4v1_j200_replay_attitude_v3_20261104')
OUT=REPO/BASE
BRANCH='mod4v1-lqr-mpc-robust'
NOTE='''# Recorded J200 MuJoCo delivery and failed attitude candidate V3

Human21:22 requested viewing the achieved jump. New independent no-Tk viewer reads complete37-coordinate recorded poses, interpolates for display, and calls no mj_step/controller. Actual capture replay PID54056/window21114258 responded, READY and empty stderr at initial inspection. Default0.5x looping; the playback is not a new physical/reliability case. Original capture/baseline cases and scores are unchanged. User-folder shortcut is included. Do not stop the requested viewer for bookkeeping.

The old latestCAD FPS player's worker-Tk revision still failed at exit with Tcl_AsyncDelete after actual user interaction; its log and pre-main-Tk backup are preserved. A main-Tk rewrite was only proposed, not implemented/tested. Replay has no Tk dependency; this is not a claim that the old FPS app was repaired.

Human21:34 asked the existing jump child to reduce body tilt. Exactly one additional nominal10s/1000control/20000physics case completed. V3 uses existing0.6accel/2jerk continuous speed reference and incoming-velocity landing handoff, same K/push/200mm fixture/1.4 target/PD-D4-doubleDC/motor/model. Longer runup(-2.5/2.0 versus-.8/.3), duration10s versus8s are explicit input/timing changes, not a same-condition single-variable proof. Against captureV2, push pitch peak16.69->3.40deg and predicted-air15.21->6.52deg improved; landing17.79->22.95deg and terminal stable3.86->1.34s worsened. Guide43ticks/peak23.354kN, hard0; full mesh clearance3.91s survives, >=2s stability does not. V3 overall FAILED and is frozen/not adopted/not installed in replay. Ground MPC approach351accepted/0fallback, landing537/67(19iteration+48domain), not aerial MPC or hard WCET. Exact2k liftoff root velocity was not logged; explicit100Hz bracketing is retained, never estimated velocity relabeled as truth.

Old2traces were each reduced once for the new attitude question, new1000trace/contact each once. No second newcase/tail extension/grid/DR/new repository/agent. Child sent complete frozen result paths before service closing failed; no rerun for that closing failure. Cumulative J20052020physics includes prior20-step software failure. T01 strict contact gate still fails; its other35tasks were not reset.

Archive includes small completed sources/config/results/derived summaries and the updated task ledger. Huge raw trajectories remain at original paths with byte sizes and producer SHA when already available from a small result, never re-read/hash for archival. No old case/holdout replay or other worktree/index/main. Original recorder is invoked once with existing in-memory sparse-add adaptation, unique annotated trial, own-branch/tag atomic nonforce push. Older PH12 pending remains pending; no receipt-to-archive loop.
'''

def main():
    def git_read(*args):
        return subprocess.run(['git','-C',str(REPO),*args],check=True,capture_output=True,text=True).stdout.strip()
    if git_read('branch','--show-current')!=BRANCH:raise RuntimeError('Wrong branch')
    if git_read('diff','--cached','--name-only'):raise RuntimeError('Existing staged changes')
    if (REPO/f'history/experiments/20261104-{ID}.json').exists():raise RuntimeError('Existing record; resume same objects instead')
    OUT.mkdir(parents=True,exist_ok=False)
    selected=[]
    def put(rel,data):
        dest=OUT/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
        selected.append(dest.relative_to(REPO).as_posix())
    sources=['TERRAIN_ADAPTATION_TASKS_V1.md']
    sources += ['JUMP200_REPLAY_V1/'+name for name in ('play.py','Start_J200_Replay.bat','README.md','replay_20261104_212837.stdout.log','replay_20261104_212837.stderr.log')]
    sources += ['RM_FPS_PLAYER_V1/'+name for name in ('revisions/player_c2fps_before_main_tk001.py','player_c2fps_tkowner_20261104_205204.stdout.log','player_c2fps_tkowner_20261104_205204.stderr.log')]
    sources += ['JUMP200_LQR_MPC_V1/'+name for name in ('derive_attitude_v3.py','run_attitude_v3.py','attitude_v3_001.json','attitude_metrics.py','reduce_attitude_v3_once.py','ATTITUDE_OLD_TWO_ONCE.json','ATTITUDE_V3_COMPARISON.json','ATTITUDE_V3_MINIMUM.json','attitude_old_two_once.log','attitude_v3_001.log','attitude_v3_reduction_once.log')]
    case=Path('JUMP200_LQR_MPC_V1/runs/j200_attitude_v3_nominal_200003')
    sources += [(case/name).as_posix() for name in ('config.json','SOURCE_MANIFEST.json','result.json')]
    for rel in sources:put(Path('payload')/rel,(ROOT/rel).read_bytes())
    shortcut=Path('C:/Users/lulu/Desktop/claude/mjcf/MOD4_LOCAL_LATEST_MOE_PLAYER_REQUESTED_20261023/看200mm跳台回放.bat')
    put('payload/user_launcher/看200mm跳台回放.bat',shortcut.read_bytes())
    result=json.loads((ROOT/case/'result.json').read_bytes())
    external=[]
    for field in ('raw_trace','physics_contact_audit'):
        known=result[field];p=Path(known['path'])
        external.append(dict(path=str(p),bytes=p.stat().st_size,sha256=known.get('SHA'),sha_status='PRODUCER_REPORTED_NO_ARCHIVE_PAYLOAD_READ',field=field))
    put('NOTE.md',NOTE.encode('utf8'))
    put('EXTERNAL_ARTIFACTS.json',(json.dumps(external,indent=2)+'\n').encode('utf8'))
    put(Path(__file__).name,Path(__file__).read_bytes())
    listrel=(BASE/'SELECTED_FILES.txt').as_posix()
    put('SELECTED_FILES.txt',('\n'.join(selected+[listrel])+'\n').encode('utf8'))
    sys.path.insert(0,str(REPO/'archive_tools'))
    spec=importlib.util.spec_from_file_location('original_j200_replay_recorder',REPO/'archive_tools/record_experiment.py')
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    original=mod.git
    def git(*args):
        if args and args[0]=='add':args=('add','--sparse',*args[1:])
        try:return original(*args)
        except subprocess.CalledProcessError as error:
            print('ORIGINAL_HELPER_GIT_FAILURE',error.stdout,error.stderr,flush=True);raise
    mod.git=git
    sys.argv=['record_experiment.py','--id',ID,'--title','Deliver recorded J200 MuJoCo playback; retain failed V3 landing attitude result','--kind','diagnostic','--note-file',str(OUT/'NOTE.md'),'--validation','Native recorded-pose viewer verified; one new nominal V3 complete but landing tilt and2s stability failed; no physics rerun for archive.','--files',*selected]
    mod.main()
    tag='trial-20261104-'+ID;head=git_read('rev-parse','HEAD');tagobj=git_read('rev-parse',tag)
    subprocess.run(['git','-C',str(REPO),'push','--atomic','origin',f'HEAD:refs/heads/{BRANCH}',f'refs/tags/{tag}:refs/tags/{tag}'],check=True)
    refs={line.split()[1]:line.split()[0] for line in git_read('ls-remote','origin',f'refs/heads/{BRANCH}',f'refs/tags/{tag}',f'refs/tags/{tag}^{{}}').splitlines()}
    if refs.get('refs/heads/'+BRANCH)!=head or refs.get('refs/tags/'+tag)!=tagobj or refs.get('refs/tags/'+tag+'^{}')!=head:raise RuntimeError('Remote identity mismatch')
    print(json.dumps(dict(commit=head,tag=tag,tag_object=tagobj,selected_count=len(selected),remote=refs),indent=2),flush=True)

if __name__=='__main__':main()
