"""One completed C99 reference-component stage, including its precompile failure."""
from pathlib import Path
import importlib.util,json,subprocess,sys
R=Path(__file__).resolve().parent
REPO=R.parent/'repo-lqr-robust';BRANCH='mod4v1-lqr-mpc-robust'
ID='mod4v1-t01-c2-reference-c99';BASE=Path('history/experiments/mod4v1_t01_c2_reference_c99_20261104');OUT=REPO/BASE
NOTE='''# T01 current C1/C2 reference generation, C99 component only

Migrates selected sensor-only C1 differential leg references plus optional C2 intent-heading outer loop; directly reuses existing immutable CTK FK/Jacobian/public nominal geometry. No fourth physical control candidate, terrain K, model/solver/PD/D4/DC change, new robot case, old trace/holdout replay, driver/BSP patch or V3-viewer manipulation. Original T01 strict support gate remains failed; T02-T36 not graduated. pc3_p25_step is NOT a drop-in current coord_soft torque backend; this component does not implement estimator/full balance torque/arming/driver/deadline/HIL. Caller disables this outer heading loop when FPS already supplies it.

Predeclared C2REF_NATIVE_COMPONENT_MATH_001 thresholds, four NEW synthetic sequences/1080 calls, original Python C1/C2 comparison, 16 native fault contracts. GCC C99 -O2 -Wall -Wextra -Werror -fno-fast-math compiled0/native0. Worst reference4 5.9936994e-7rad, corrected yaw2.9965257e-8rad/s; inverse-acceptance decisions match. Common-q error1.51195e-8rad. Host state/input/output64/88/52B; native whole0.24169s includes process/file I/O/fault checks, NOT ARM WCET or robot speedup. Zero physics/old cases. Binary32 FK FD=.001 retained, Python original FD unchanged; invalid sample handling explicitly stricter/transactional, not all-fault-path bit identity.

validation001 stopped BEFORE compile/physics with test-only KeyError('K'); failed source/protocol/result preserved. Only actual pack key K_6x14 corrected, independent002 output, same input recipe/thresholds. Both original jobs collected. This is mathematical component evidence, not complete C2 torque/robot/DR/board qualification. Large new synthetic/native output and executable are path/size/unknown-SHA metadata only; no archival payload hash. Existing sources/gains are small text dependencies. No extra agents/dependencies/hardware. Original recorder once, sparse-add adapter only in memory; own branch/tag atomic nonforce push, historical PH12 remains pending. Post-push ledger receipt is not another archive stage.
'''
def main():
 def git(*args):return subprocess.run(['git','-C',str(REPO),*args],check=True,capture_output=True,text=True).stdout.strip()
 if git('branch','--show-current')!=BRANCH or git('diff','--cached','--name-only'):raise RuntimeError('Wrong branch or staged changes')
 if (REPO/f'history/experiments/20261104-{ID}.json').exists():raise RuntimeError('Record exists; resume same objects')
 OUT.mkdir(parents=True,exist_ok=False);selected=[]
 def put(rel,data):
  p=OUT/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);selected.append(p.relative_to(REPO).as_posix())
 prefix='T01_C2_REFERENCE_C99_V1/'
 sources=['TERRAIN_ADAPTATION_TASKS_V1.md']
 sources += [prefix+n for n in ['pc2_reference.h','pc2_reference.c','host_check.c','verify_component.py','verify_component_retry002.py','README.md','revisions/verify_component_before_pack_key001.py','validation001/protocol.json','validation001/result.json','validation002/protocol.json','validation002/result.json','validation002/compile.stdout.log','validation002/compile.stderr.log','validation002/native.stdout.log','validation002/native.stderr.log']]
 sources += ['SPR_AUDIT/portable_core_v2_kinematics/'+n for n in ['ct_kinematics.h','ct_kinematics.c']]
 sources += ['SPR_AUDIT/portable_control_v3_current/pc3_geometry_data.h','RM_ROBUSTNESS_V1/controller_roll_follow_v1.py','RM_ROBUSTNESS_V1/controller_heading_follow_v2.py','FLAT_STABILITY_FIX_V1/controller.py','FLAT_STABILITY_FIX_V1/controller_v2.py','ground_controller_v4.py','physics_bridge.py','sensor_core_v4.py','nominal_gain_v1.json','NORMAL_P25_HOLDOUT_V1/CONTROLLER_PACK.json']
 for rel in sources:put(Path('payload')/rel,(R/rel).read_bytes())
 external=[]
 for name in ['new_synthetic_input.txt','native_output.jsonl','pc2_native_check.exe']:
  p=R/prefix/'validation002'/name
  external.append(dict(path=str(p),bytes=p.stat().st_size,sha256=None,reason='Not read/hashed for archive; formula/new executable identity not a robot trial'))
 put('EXTERNAL_ARTIFACTS.json',json.dumps(external,indent=2).encode('utf8'))
 put('NOTE.md',NOTE.encode('utf8'));put(Path(__file__).name,Path(__file__).read_bytes())
 listing=(BASE/'SELECTED_FILES.txt').as_posix();put('SELECTED_FILES.txt',('\n'.join(selected+[listing])+'\n').encode('utf8'))
 sys.path.insert(0,str(REPO/'archive_tools'))
 spec=importlib.util.spec_from_file_location('original_c2_reference_recorder',REPO/'archive_tools/record_experiment.py')
 mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);original=mod.git
 def adapted(*args):
  if args and args[0]=='add':args=('add','--sparse',*args[1:])
  try:return original(*args)
  except subprocess.CalledProcessError as e:print('HELPER_GIT_FAILURE',e.stdout,e.stderr,flush=True);raise
 mod.git=adapted
 sys.argv=['record_experiment.py','--id',ID,'--title','Port selected T01 C1/C2 reference slice to C99 and compare 1080 synthetic inputs','--kind','diagnostic','--note-file',str(OUT/'NOTE.md'),'--validation','Native compile/run exit0,1080 new synthetic rows and16 fault contracts pass; precompile config-key failure preserved.0 physics,no full T01/board qualification.','--files',*selected]
 mod.main();tag='trial-20261104-'+ID;head=git('rev-parse','HEAD');tagobj=git('rev-parse',tag)
 subprocess.run(['git','-C',str(REPO),'push','--atomic','origin',f'HEAD:refs/heads/{BRANCH}',f'refs/tags/{tag}:refs/tags/{tag}'],check=True)
 refs={line.split()[1]:line.split()[0] for line in git('ls-remote','origin',f'refs/heads/{BRANCH}',f'refs/tags/{tag}',f'refs/tags/{tag}^{{}}').splitlines()}
 if refs.get('refs/heads/'+BRANCH)!=head or refs.get('refs/tags/'+tag)!=tagobj or refs.get('refs/tags/'+tag+'^{}')!=head:raise RuntimeError('Remote identity mismatch')
 print(json.dumps(dict(commit=head,tag=tag,tag_object=tagobj,selected_count=len(selected),remote=refs),indent=2),flush=True)
if __name__=='__main__':main()
