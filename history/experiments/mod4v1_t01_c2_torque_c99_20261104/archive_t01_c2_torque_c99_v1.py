"""One real completed selected-C2 torque math stage; no robot replay/large hash."""
from pathlib import Path
import importlib.util,json,subprocess,sys
R=Path(__file__).resolve().parent;REPO=R.parent/'repo-lqr-robust';BRANCH='mod4v1-lqr-mpc-robust'
ID='mod4v1-t01-c2-torque-c99';BASE=Path('history/experiments/mod4v1_t01_c2_torque_c99_20261104');OUT=REPO/BASE
NOTE='''# Selected nominal T01 C2 requested-torque mathematics, C99

Directly reuses immutable PC2 reference, CTK FK/6x14 LQR, frozen P25 data and PC3 row mapping. Implements original coord_soft jerk/acceleration shaping, independent local park integrator/bleed, projected wheel-speed envelope, common sagittal feedback, yaw PI/antiwindup/feedforward, original FIRST clip then differential-only PD120/4 then SECOND clip. Does not call old pc3_p25_step or overwrite common leg balance with fixed PD. heading=0 if FPS already supplies corrected yaw rate. Explicit 100Hz/clock/age/finite/geometry/domain guards and latched error; NULL/alias preconditions do not mutate callers. Requested Nm only: no actual driver disable/current/PVT, BSP/cycle wiring, inner PD/target delay/DC/power/arming/estimator or simulator execution. New state type is not a drop-in pc3_cycle controller. Code is selected nominal profile, not full gait/length/mode scheduling.

Predeclared C2_TORQUE_NATIVE_MATH_001,2300 NEW synthetic inputs/original Python C1/C2 comparison,33 native fault assertions (15 trigger+15 latch+3 precondition/init), GCC C99 O2 Wall Wextra Werror fno-fast-math compile0/native0. Worst torque difference8.8702421e-5Nm vs2e-3 gate; zero invalid/bounds rows.1040 request-saturation rows/386 envelope projections actually covered. Reference14 mixes SI units;3.54679e-5 largest per-component numerical difference is NOT robot attitude tracking error. Host state192B/native entire0.493328s includes launch/ASCII I/O/assertions, NOT ARM WCET. Rate-only high-command synthetic stress is not a physics/FPS dynamics trajectory.

Zero physical steps/old-case reads/new K/terrain/control candidates. T01 strict contact failure and3/3 cap remain, original protocols/results/holdouts/model/gains/J200 failures/UI/viewer untouched. ARM/full cycle/BSP/HIL and independent DR remain unqualified. Large new synthetic/native output/executable are only actual path/size/unknown SHA, no archive payload reads. Small selected dependencies/compare sources are a snapshot, not a standalone full workspace package. Original recorder once, only in-memory sparse add adapter, own branch/tag atomic nonforce push; historical PH12 pending retained. Post-push receipt is not another archive cycle.
'''
def main():
 def git(*args):return subprocess.run(['git','-C',str(REPO),*args],check=True,capture_output=True,text=True).stdout.strip()
 if git('branch','--show-current')!=BRANCH or git('diff','--cached','--name-only'):raise RuntimeError('Wrong branch or staged changes')
 if git('tag','--list',f'trial-*-{ID}'):raise RuntimeError('Trial exists; resume its objects')
 OUT.mkdir(parents=True,exist_ok=False);selected=[]
 def put(rel,data):
  p=OUT/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);selected.append(p.relative_to(REPO).as_posix())
 prefix='T01_C2_TORQUE_C99_V1/'
 sources=['TERRAIN_ADAPTATION_TASKS_V1.md']
 sources += [prefix+n for n in ['pc2_balance.h','pc2_balance.c','host_check.c','verify_torque.py','README.md','validation001/protocol.json','validation001/result.json','validation001/compile.stdout.log','validation001/compile.stderr.log','validation001/native.stdout.log','validation001/native.stderr.log']]
 sources += ['T01_C2_REFERENCE_C99_V1/'+n for n in ['pc2_reference.h','pc2_reference.c']]
 sources += ['SPR_AUDIT/portable_core_v2_kinematics/'+n for n in ['ct_kinematics.h','ct_kinematics.c']]
 sources += ['SPR_AUDIT/portable_control_v3_current/'+n for n in ['pc3_control.h','pc3_controller.c','pc3_p25_data.h','pc3_geometry_data.h']]
 sources += ['RM_ROBUSTNESS_V1/controller_roll_follow_v1.py','RM_ROBUSTNESS_V1/controller_heading_follow_v2.py','FLAT_STABILITY_FIX_V1/controller.py','FLAT_STABILITY_FIX_V1/controller_v2.py','ground_controller_v4.py','physics_bridge.py','sensor_core_v4.py','nominal_gain_v1.json','NORMAL_P25_HOLDOUT_V1/CONTROLLER_PACK.json']
 for rel in sources:put(Path('payload')/rel,(R/rel).read_bytes())
 external=[]
 for name in ['new_synthetic_input.txt','native_output.jsonl','pc2_torque_host.exe']:
  p=R/prefix/'validation001'/name;external.append(dict(path=str(p),bytes=p.stat().st_size,sha256=None,reason='Not read/hashed for archival bookkeeping'))
 put('EXTERNAL_ARTIFACTS.json',json.dumps(external,indent=2).encode('utf8'));put('NOTE.md',NOTE.encode('utf8'));put(Path(__file__).name,Path(__file__).read_bytes())
 listing=(BASE/'SELECTED_FILES.txt').as_posix();put('SELECTED_FILES.txt',('\n'.join(selected+[listing])+'\n').encode('utf8'))
 sys.path.insert(0,str(REPO/'archive_tools'));spec=importlib.util.spec_from_file_location('original_c2_torque_recorder',REPO/'archive_tools/record_experiment.py')
 mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);original=mod.git
 def adapted(*args):
  if args and args[0]=='add':args=('add','--sparse',*args[1:])
  try:return original(*args)
  except subprocess.CalledProcessError as e:print('HELPER_GIT_FAILURE',e.stdout,e.stderr,flush=True);raise
 mod.git=adapted
 sys.argv=['record_experiment.py','--id',ID,'--title','Port selected T01 C2 requested torque chain to C99 and compare 2300 new synthetic inputs','--kind','diagnostic','--note-file',str(OUT/'NOTE.md'),'--validation','Native compile0/run0,2300 new synthetic rows,33 fault assertions,max torque error8.8702421e-5Nm.0 physical steps; original T01 strict support still failed; no full driver/ARM/HIL qualification.','--files',*selected]
 mod.main();head=git('rev-parse','HEAD');tags=git('tag','--points-at','HEAD','--list',f'trial-*-{ID}').splitlines()
 if len(tags)!=1:raise RuntimeError('Expected one recorder-created tag')
 tag=tags[0];tagobj=git('rev-parse',tag)
 subprocess.run(['git','-C',str(REPO),'push','--atomic','origin',f'HEAD:refs/heads/{BRANCH}',f'refs/tags/{tag}:refs/tags/{tag}'],check=True)
 refs={line.split()[1]:line.split()[0] for line in git('ls-remote','origin',f'refs/heads/{BRANCH}',f'refs/tags/{tag}',f'refs/tags/{tag}^{{}}').splitlines()}
 if refs.get('refs/heads/'+BRANCH)!=head or refs.get('refs/tags/'+tag)!=tagobj or refs.get('refs/tags/'+tag+'^{}')!=head:raise RuntimeError('Remote identity mismatch')
 print(json.dumps(dict(commit=head,tag=tag,tag_object=tagobj,selected_count=len(selected),remote=refs),indent=2),flush=True)
if __name__=='__main__':main()
