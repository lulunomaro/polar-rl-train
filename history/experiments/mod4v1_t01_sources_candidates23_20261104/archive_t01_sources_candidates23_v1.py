"""Reuse the original recorder and prior sparse-add adapter for one C2/C3 stage."""
from pathlib import Path
import importlib.util
import json
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parent/'repo-lqr-robust'
ID='mod4v1-terrain-t01-sources-candidates23'
BASE=Path('history/experiments/mod4v1_t01_sources_candidates23_20261104')
OUT=REPO/BASE
NOTE='''# T01: source reuse, C2 functional improvements and C3 negative result

This records two completed new 12s cases, 1200 controls/24000 physics each, with a fresh model/DR per case. Original gates, robot, KF and actuator PD/D4/DC are unchanged. No holdout or consumed case was rerun.

C2 retained C1 leg leveling and reused the existing FPS heading outer loop (3/s, +/-1.5rad/s). Its pitch/roll peaks are .0187347/.0280186rad, progress1.623630m, lateral.0468113m, steady-speed RMSE.0412814m/s and stop RMS.00554225m/s: every non-contact gate passed. Left/right support.89855/.95515 and 165 below-threshold whole-body force samples still failed. Guide/hard0. Parent collected pwsh-2ce069f872794049 exit0.

C3 directly used the supplied SPR/7z axial length D-on-measurement/J-transpose structure, retaining C2 and own nominal geometry/gains. Added128.1673466Ns/m was derived from own design mass/stiffness; no foreign gains/dimensions copied, no added length P/I. It completed but support.89385/.95210 and177 whole-low-force samples did not improve. Stop RMS.0105791; other non-contact gates passed. C3 is preserved but NOT adopted; C2 remains the best functional candidate. Parent collected pwsh-d441096df6a245f8 exit0. T01 remains incomplete; no fourth parameter grid, no DR expansion, no UI graduation.

Completed C1 stop and C2 contact reductions are included. Each new C2 raw source was streamed once (1200/20000/1200); a nested diagnostic-clock parser gap prevented its optional correspondence analysis, which was explicitly stopped without reread. 0.5-1ms low-force samples are not proof of geometric flight; 2k actual-velocity/DC clip duty remains unknown. The source-reuse inventory is in the canonical 36-task file, not a parallel plan. Source function snapshots used for that inventory are included.

Large control/contact/diagnostic logs are path/size indexed only, SHA unknown, never re-read or hashed for this archive. Old PH12 pending remains pending. Existing recorder is unchanged and called once; known sparse-add adaptation is in memory only. No other worktree/main ref, physics, native build or hardware is touched by archival.
'''


def main():
    def git_read(*args):
        return subprocess.run(['git','-C',str(REPO),*args],check=True,capture_output=True,text=True).stdout.strip()
    if git_read('branch','--show-current')!='mod4v1-lqr-mpc-robust':raise RuntimeError('Wrong branch')
    if git_read('diff','--cached','--name-only'):raise RuntimeError('Existing staged changes: do not mix')
    if (REPO/f'history/experiments/20261104-{ID}.json').exists():raise RuntimeError('Record exists; continue old objects')
    OUT.mkdir(parents=True,exist_ok=False)
    selected=[]
    def put(rel,data):
        p=OUT/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        selected.append(p.relative_to(REPO).as_posix())
    sources=['TERRAIN_ADAPTATION_TASKS_V1.md']
    for name in ('controller_heading_follow_v2.py','controller_axial_damping_v3.py','run_t01_heading_follow_v2.py','run_t01_axial_damping_v3.py'):
        sources.append('RM_ROBUSTNESS_V1/'+name)
    for sub in ('slow_c1_stop_analysis001','c2_contact_analysis001'):
        sources += [f'RM_ROBUSTNESS_V1/{sub}/{name}' for name in ('analysis.json','summary.md')]
    external=[]
    for folder,case in (('heading_follow_v2','t01_c2_nominal_slow_420131_001'),('axial_damping_v3','t01_c3_nominal_slow_420141_001')):
        base=Path('RM_ROBUSTNESS_V1')/folder
        sources += [(base/'T01_PROTOCOL_V1.json').as_posix(),(base/(case+'.console.log')).as_posix()]
        case_dir=base/'runs'/case
        sources += [(case_dir/name).as_posix() for name in ('config.json','protocol.json','meta.json','result.json','candidate_diagnostics.json')]
        for rel in (case_dir/'trace.jsonl',case_dir/'contact_trace.jsonl',base/'diagnostic_logs'/(case+'.jsonl')):
            p=ROOT/rel
            external.append(dict(path=str(p),bytes=p.stat().st_size,sha256=None,sha_status='UNKNOWN_NOT_HASHED_FOR_ARCHIVE'))
    sources += ['SOURCE_REUSE_20261104_1542/spr2_selected/chassis/Task/chassis_task.c','SOURCE_REUSE_20261104_1542/spr2_selected/chassis/Task/chassis_task.h']
    sources += ['SOURCE_REUSE_20261104_1542/chassis7z/readable/chassis/algorithm/'+name for name in ('PID.c','PID.h','leg_force.c','LQR_K.c')]
    for rel in sources:put(Path('payload')/rel,(ROOT/rel).read_bytes())
    put('NOTE.md',NOTE.encode('utf8'))
    put('EXTERNAL_ARTIFACTS.json',(json.dumps(external,indent=2)+'\n').encode('utf8'))
    put(Path(__file__).name,Path(__file__).read_bytes())
    listrel=(BASE/'SELECTED_FILES.txt').as_posix()
    put('SELECTED_FILES.txt',('\n'.join(selected+[listrel])+'\n').encode('utf8'))
    sys.path.insert(0,str(REPO/'archive_tools'))
    spec=importlib.util.spec_from_file_location('original_sources_recorder',REPO/'archive_tools/record_experiment.py')
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    original=mod.git
    def git(*args):
        if args and args[0]=='add':args=('add','--sparse',*args[1:])
        try:return original(*args)
        except subprocess.CalledProcessError as e:
            print('ORIGINAL_HELPER_GIT_FAILURE',e.stdout,e.stderr,flush=True);raise
    mod.git=git
    sys.argv=['record_experiment.py','--id',ID,'--title','Record T01 source reuse, C2 functional improvement and C3 damping failure','--kind','diagnostic','--note-file',str(OUT/'NOTE.md'),'--validation','Two fresh 12s cases; non-contact gates passed but original contact gates still failed. C2 retained, C3 not adopted.','--files',*selected]
    mod.main()


if __name__=='__main__':main()
