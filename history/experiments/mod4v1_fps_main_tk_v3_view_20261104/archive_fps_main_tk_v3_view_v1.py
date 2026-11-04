"""Completed main-Tk lifecycle / explicitly requested V3 view; no physics replay."""
from pathlib import Path
import importlib.util,json,subprocess,sys
R=Path(__file__).resolve().parent
REPO=R.parent/'repo-lqr-robust'
ID='mod4v1-fps-main-tk-v3-view'
BASE=Path('history/experiments/mod4v1_fps_main_tk_v3_view_20261104')
OUT=REPO/BASE
BRANCH='mod4v1-lqr-mpc-robust'
NOTE='''# Main-thread Tk lifecycle and requested V3 recorded-pose view

New FPS entry reuses frozen layout/render/GLFW helpers, while Tk/allVariables/widgets live only on process main thread and GLFW/context/Engine on one non-daemon worker. Plain input/status/action messages cross the boundary; worker closes GL before main destroys Tcl and joins. Engine/K/KF/PD/D4/DC/robot/solver/limits unchanged. One actual hidden paused latestCAD/c2_fps lifecycle: PID69912, Tk69916/GL70356,47600geoms/37nq, READY->worker closed->main Tk closed, exit0/stderr empty,0controls/0physics/sim_time0. This proves only that lifecycle path, not driving/fullGUI/performance/T01 acceptance. Old exit failure/source remain; launcher now chooses the new entry, desktop wrapper unchanged.

Human22:21 explicitly requested V3 takeoff playback, overriding earlier visual nonreplacement only for viewing, NOT adoption. Viewer now supports case3/start timestamp/follow; capture default unchanged. V3 starts recorded2.4s,1.11s before push,0.5x follow loop. No controller/mj_step or new physics run. V3 remains the previously archived FAILED candidate(landing22.95deg/endstable1.34s/guide43), current physical result unchanged. First launch50652 reached READY but was absent on process inspection with no closing/error line; cause unknown, logs kept. Second launch10548/1120612 was actually verified responding with exact command and READY/empty stderr. No speculation about first exit cause or new physical sample.

Small source/docs/logs/shortcuts only; no raw trajectory/CAD/model read/hash for archival. Original case/source/results already in b954dc0e5e5f16d73400a6c2d1c34144c3079725. Original recorder once, in-memory sparse-add adapter, unique annotated tag, own branch/tag atomic nonforce push. No other worktree/index/main, no old holdout/case rerun, no extra agents/dependencies/hardware. T01 strict support gate still failed and older PH12 pending remains pending. Post-push ledger receipt is next-stage material, not an archive loop.
'''
def main():
    def git(*args):return subprocess.run(['git','-C',str(REPO),*args],check=True,capture_output=True,text=True).stdout.strip()
    if git('branch','--show-current')!=BRANCH or git('diff','--cached','--name-only'):raise RuntimeError('Wrong branch or staged changes')
    if (REPO/f'history/experiments/20261104-{ID}.json').exists():raise RuntimeError('Record exists; resume same objects')
    OUT.mkdir(parents=True,exist_ok=False);selected=[]
    def put(rel,data):
        p=OUT/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);selected.append(p.relative_to(REPO).as_posix())
    sources=['TERRAIN_ADAPTATION_TASKS_V1.md']
    sources+=['RM_FPS_PLAYER_V1/'+n for n in ('player_main_tk_v1.py','player.py','runtime.py','Start_RM_FPS.bat','MAIN_TK_LIFECYCLE_V1.md','main_tk_lifecycle001.stdout.log','main_tk_lifecycle001.stderr.log')]
    sources+=['JUMP200_REPLAY_V1/'+n for n in ('play.py','Start_J200_V3.bat','README.md','v3_replay001.stdout.log','v3_replay001.stderr.log','v3_replay002.stdout.log','v3_replay002.stderr.log')]
    for rel in sources:put(Path('payload')/rel,(R/rel).read_bytes())
    shortcut=Path('C:/Users/lulu/Desktop/claude/mjcf/MOD4_LOCAL_LATEST_MOE_PLAYER_REQUESTED_20261023/看V3起跳回放.bat')
    put('payload/user_launcher/看V3起跳回放.bat',shortcut.read_bytes())
    put('NOTE.md',NOTE.encode('utf8'));put(Path(__file__).name,Path(__file__).read_bytes())
    listing=(BASE/'SELECTED_FILES.txt').as_posix();put('SELECTED_FILES.txt',('\n'.join(selected+[listing])+'\n').encode('utf8'))
    sys.path.insert(0,str(REPO/'archive_tools'))
    spec=importlib.util.spec_from_file_location('original_main_tk_recorder',REPO/'archive_tools/record_experiment.py')
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);original=mod.git
    def adapted(*args):
        if args and args[0]=='add':args=('add','--sparse',*args[1:])
        try:return original(*args)
        except subprocess.CalledProcessError as e:print('HELPER_GIT_FAILURE',e.stdout,e.stderr,flush=True);raise
    mod.git=adapted
    sys.argv=['record_experiment.py','--id',ID,'--title','Fix main-thread Tk lifecycle and show requested failed V3 recorded takeoff','--kind','diagnostic','--note-file',str(OUT/'NOTE.md'),'--validation','Real latestCAD hidden paused lifecycle exit0/empty stderr/zero physics; requested V3 pose viewer verified. No control qualification or physics rerun.','--files',*selected]
    mod.main();tag='trial-20261104-'+ID;head=git('rev-parse','HEAD');tagobj=git('rev-parse',tag)
    subprocess.run(['git','-C',str(REPO),'push','--atomic','origin',f'HEAD:refs/heads/{BRANCH}',f'refs/tags/{tag}:refs/tags/{tag}'],check=True)
    refs={line.split()[1]:line.split()[0] for line in git('ls-remote','origin',f'refs/heads/{BRANCH}',f'refs/tags/{tag}',f'refs/tags/{tag}^{{}}').splitlines()}
    if refs.get('refs/heads/'+BRANCH)!=head or refs.get('refs/tags/'+tag)!=tagobj or refs.get('refs/tags/'+tag+'^{}')!=head:raise RuntimeError('Remote identity mismatch')
    print(json.dumps(dict(commit=head,tag=tag,tag_object=tagobj,selected_count=len(selected),remote=refs),indent=2),flush=True)
if __name__=='__main__':main()
