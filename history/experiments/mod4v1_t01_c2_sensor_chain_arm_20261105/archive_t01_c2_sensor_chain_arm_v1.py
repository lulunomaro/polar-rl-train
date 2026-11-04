"""One completed C3->C2 wiring/new ARM-source object stage, no robot QA."""
from pathlib import Path
import importlib.util,json,subprocess,sys
R=Path(__file__).resolve().parent;REPO=R.parent/'repo-lqr-robust';BRANCH='mod4v1-lqr-mpc-robust'
ID='mod4v1-t01-c2-sensor-chain-arm';BASE=Path('history/experiments/mod4v1_t01_c2_sensor_chain_arm_20261105');OUT=REPO/BASE
NOTE='''# Existing C3 estimator to selected C2 requested-torque C99 seam

New thin API calls only existing pc3_estimator_update then pc2_balance_step. Explicit estimator prior initialization is not motor arming/natural stand. Ordinary errors invalidate outputs, latch and disarm estimator; NULL/alias preconditions do not mutate objects. No driver callbacks/queue/CAN/physical enable/disable or feedback publisher. Did NOT insert old pc3_cycle outer DC preclip: original PD-target/D4/current-PD/signed-DC order remains an external actuation requirement. Old C3/CTK/C2 reference/torque sources unchanged, no new control candidate/K/robot case/UI manipulation.

Predeclared C2_SENSOR_CHAIN_AND_ARM_OBJECTS_001:256 fresh synthetic declared mean windows,2 held packet views,258 normal control calls,7001 assertions (mostly per-field/per-call, not independent faults). Both heading modes; state14/requested torque difference0 relative to SAME C3+C2 called directly. This is wiring equivalence, not another independent algorithm oracle; prior Python2300 math evidence is commit6ee0c1dc. Five error propagation/latch scenarios plus NULL/alias/invalid explicit prior. Count20/10ms are synthetic metadata, not5120 physically collected innovations. Host state/result904/368B,whole native0.174722s includes checks/process output,NOT WCET.

Actual armclang C99 O2 Wall Wextra Werror fno-fast-math compiled THREE new source TUs for each Cortex-M4(fpv4-sp-d16 hard)/M7(fpv5-sp-d16 hard),6/6 exit0. New-object52-byte ELF header only checked32bit/little-endian/ET_REL/EM_ARM. M4 object file sizes2068/8672/6516B,M7 2072/8668/6516B; NOT Flash/stack measurements. Targets are accepted compiler options,not discovered board binding. No final ARM link/target execution/WCET/BSP/power/inner-loop/HIL qualification.

Zero physical steps/old case or holdout reads/new K/4th candidate. Original T01 support fail/three-candidate cap/J200 failed landing/36-task state retained. All seven new binaries only actual path,size,unknown SHA,not archival payload reads/hashes. Snapshot small source dependencies/logs/receipts,not standalone complete workspace. Original recorder once,inmemory sparse-add adapter only,own branch+annotated tag atomic nonforce push. Historical PH12 remains pending; postpush receipt not another archive stage.
'''
def main():
 def git(*args):return subprocess.run(['git','-C',str(REPO),*args],check=True,capture_output=True,text=True).stdout.strip()
 if git('branch','--show-current')!=BRANCH or git('diff','--cached','--name-only'):raise RuntimeError('Wrong branch or staged changes')
 if git('tag','--list',f'trial-*-{ID}'):raise RuntimeError('Trial exists; resume its objects')
 OUT.mkdir(parents=True,exist_ok=False);selected=[]
 def put(rel,data):
  p=OUT/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);selected.append(p.relative_to(REPO).as_posix())
 prefix='T01_C2_SENSOR_CHAIN_C99_V1/'
 sources=['TERRAIN_ADAPTATION_TASKS_V1.md']+[prefix+n for n in ['pc2_sensor_chain.h','pc2_sensor_chain.c','host_check.c','build_check.py','README.md','build001/protocol.json','build001/result.json']]
 for stem in ['native_compile','native_run']+[t+'_'+name for t in ['m4','m7'] for name in ['pc2_sensor_chain','pc2_balance','pc2_reference']]:
  sources += [prefix+'build001/'+stem+suffix for suffix in ['.stdout.log','.stderr.log']]
 sources += ['T01_C2_TORQUE_C99_V1/'+n for n in ['pc2_balance.h','pc2_balance.c']]
 sources += ['T01_C2_REFERENCE_C99_V1/'+n for n in ['pc2_reference.h','pc2_reference.c']]
 sources += ['SPR_AUDIT/portable_core_v2_kinematics/'+n for n in ['ct_kinematics.h','ct_kinematics.c']]
 sources += ['SPR_AUDIT/portable_control_v3_current/'+n for n in ['pc3_control.h','pc3_estimator.c','pc3_controller.c','pc3_geometry_data.h','pc3_p25_data.h']]
 for rel in sources:put(Path('payload')/rel,(R/rel).read_bytes())
 binaries=[R/prefix/'build001/chain_host.exe']+[R/prefix/'build001'/('arm_'+t)/(name+'.o') for t in ['m4','m7'] for name in ['pc2_sensor_chain','pc2_balance','pc2_reference']]
 external=[dict(path=str(p),bytes=p.stat().st_size,sha256=None,reason='Not read/hashed for archive; only new ARM ELF headers inspected during build') for p in binaries]
 put('EXTERNAL_ARTIFACTS.json',json.dumps(external,indent=2).encode('utf8'));put('NOTE.md',NOTE.encode('utf8'));put(Path(__file__).name,Path(__file__).read_bytes())
 listing=(BASE/'SELECTED_FILES.txt').as_posix();put('SELECTED_FILES.txt',('\n'.join(selected+[listing])+'\n').encode('utf8'))
 sys.path.insert(0,str(REPO/'archive_tools'));spec=importlib.util.spec_from_file_location('original_c2_sensor_chain_recorder',REPO/'archive_tools/record_experiment.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);original=mod.git
 def adapted(*args):
  if args and args[0]=='add':args=('add','--sparse',*args[1:])
  try:return original(*args)
  except subprocess.CalledProcessError as e:print('HELPER_GIT_FAILURE',e.stdout,e.stderr,flush=True);raise
 mod.git=adapted
 sys.argv=['record_experiment.py','--id',ID,'--title','Wire existing C3 estimator to C2 request math and compile new M4 M7 objects','--kind','diagnostic','--note-file',str(OUT/'NOTE.md'),'--validation','Native compile0/run0,256 new mean windows+2 held views,7001 wiring assertions,6/6 ARM new-source objects.0 physics,no driver/HIL/full T01 qualification.','--files',*selected]
 mod.main();head=git('rev-parse','HEAD');tags=git('tag','--points-at','HEAD','--list',f'trial-*-{ID}').splitlines()
 if len(tags)!=1:raise RuntimeError('Expected one recorder-created tag')
 tag=tags[0];tagobj=git('rev-parse',tag)
 subprocess.run(['git','-C',str(REPO),'push','--atomic','origin',f'HEAD:refs/heads/{BRANCH}',f'refs/tags/{tag}:refs/tags/{tag}'],check=True)
 refs={line.split()[1]:line.split()[0] for line in git('ls-remote','origin',f'refs/heads/{BRANCH}',f'refs/tags/{tag}',f'refs/tags/{tag}^{{}}').splitlines()}
 if refs.get('refs/heads/'+BRANCH)!=head or refs.get('refs/tags/'+tag)!=tagobj or refs.get('refs/tags/'+tag+'^{}')!=head:raise RuntimeError('Remote identity mismatch')
 print(json.dumps(dict(commit=head,tag=tag,tag_object=tagobj,selected_count=len(selected),remote=refs),indent=2),flush=True)
if __name__=='__main__':main()
