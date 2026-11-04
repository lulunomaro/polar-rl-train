"""Record completed request-cycle guard seam once; never replay old QA."""
from pathlib import Path
import importlib.util,json,subprocess,sys
R=Path(__file__).resolve().parent;REPO=R.parent/'repo-lqr-robust';BRANCH='mod4v1-lqr-mpc-robust'
ID='mod4v1-t01-c2-request-cycle';BASE=Path('history/experiments/mod4v1_t01_c2_request_cycle_20261105');OUT=REPO/BASE
NOTE='''# C2-specific request cycle, existing guard reuse

Adapted frozen pc3_dispatch guard order to existing C3->C2 sensor/control chain. Distinct requested-frame/callback types,declared-binding+actuation-order defaultUNBOUND,command deadline/sequence/enable,feedback age/finite,pre/post-enqueue clock guards,at-most-one attempt,invalidate/latch on errors. NO extra outer DC preclip. Original inverse nominal PD -> target D4 -> current PD -> signed DC -> motor gain -> signed DC remains external. No shipped physical binding/BSP call site/CAN codec/motor enable or driver-rate implementation. Declaration bits are not proof of hardware implementation/calibration.

Fresh C2_REQUEST_CYCLE_MOCK_001:Native strictGCC compile0/run0,3 normal requests,16 fault scenarios,2 alias/NULL preconditions,246 assertions. Requested torque difference0 relative to SAME existing C3+C2 direct call,not independent algorithm oracle. Host cycle928/frame72B,whole run0.097096s includes checks/process output,not WCET. Synthetic20rad/s feedback intentionally inconsistent with encoder fixture only tests no additional DC preclip,not valid robot dynamics. Fake callback copies memory and invalidates pending memory; does NOT prove real hardware stop,TX delivery/cancel,concurrency or atomicity. NULL/alias/uninitialized preconditions require caller inhibit on status failure,not physical emergency-stop proof.

Only newly added request-cycle TU compiled via actual armclang for Cortex-M4(fpv4-sp-d16 hard)/M7(fpv5-sp-d16 hard),2/2 exit0,new ET_REL objects3940/3988B. Only52-byte ELF32/little/ET_REL/EM_ARM header inspected. Not Flash/stack/WCET/link/runtime/BSP/HIL qualification. No old ARM/math QA rerun;dependencies compiled only for NEW mock executable. Zero physics/old raw or holdout reads/new K/4th physical candidate/real hardware transmissions. No UI/replay changes.

User asked whether localtodo meant36 tasks nearly done. Corrected UI+canonical summary explicitly:0/36 formally closed,T01ongoing,T02-36pending35;historical abilities retained. Local C migration/testing/archive steps are not motion-task completion. Original strict T01 support fail and3-candidate cap unchanged,J200 failed clean landing retained. Goal read revision26activearmed/20of20,not completed/extended.

Small source/log/protocol/result snapshot only;three new binaries external actual path/size/SHAunknown,not payload-read/hashed for archival. Recorder original unchanged/once,inmemory sparse-add adapter,own branch+annotated trial atomic nonforce push with remote identities. Prior8b0ec0e6 retained;historicalPH12pending,postreceipt changes ride next real stage,no archive receipt loop.
'''
def main():
 def git(*args):return subprocess.run(['git','-C',str(REPO),*args],check=True,capture_output=True,text=True).stdout.strip()
 if git('branch','--show-current')!=BRANCH or git('diff','--cached','--name-only'):raise RuntimeError('Wrong branch or staged changes')
 if git('tag','--list',f'trial-*-{ID}'):raise RuntimeError('Trial exists; resume existing objects')
 OUT.mkdir(parents=True,exist_ok=False);selected=[]
 def put(rel,data):
  p=OUT/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);selected.append(p.relative_to(REPO).as_posix())
 prefix='T01_C2_REQUEST_CYCLE_C99_V1/'
 sources=['TERRAIN_ADAPTATION_TASKS_V1.md']+[prefix+n for n in ['pc2_request_cycle.h','pc2_request_cycle.c','host_check.c','build_check.py','README.md','build001/protocol.json','build001/result.json']]
 for stem in ['native_compile','native_run','arm_m4','arm_m7']:
  sources += [prefix+'build001/'+stem+suffix for suffix in ['.stdout.log','.stderr.log']]
 sources += ['T01_C2_SENSOR_CHAIN_C99_V1/'+n for n in ['pc2_sensor_chain.h','pc2_sensor_chain.c']]
 sources += ['T01_C2_TORQUE_C99_V1/'+n for n in ['pc2_balance.h','pc2_balance.c']]
 sources += ['T01_C2_REFERENCE_C99_V1/'+n for n in ['pc2_reference.h','pc2_reference.c']]
 sources += ['SPR_AUDIT/portable_core_v2_kinematics/'+n for n in ['ct_kinematics.h','ct_kinematics.c']]
 sources += ['SPR_AUDIT/portable_control_v3_current/'+n for n in ['pc3_control.h','pc3_estimator.c','pc3_controller.c','pc3_geometry_data.h','pc3_p25_data.h','pc3_dispatch.c']]
 for rel in sources:put(Path('payload')/rel,(R/rel).read_bytes())
 binaries=[R/prefix/'build001/request_host.exe']+[R/prefix/'build001'/('pc2_request_cycle_'+t+'.o') for t in ['m4','m7']]
 external=[dict(path=str(p),bytes=p.stat().st_size,sha256=None,reason='Not read/hashed for archive; only new ARM header inspected during build') for p in binaries]
 put('EXTERNAL_ARTIFACTS.json',json.dumps(external,indent=2).encode('utf8'));put('NOTE.md',NOTE.encode('utf8'));put(Path(__file__).name,Path(__file__).read_bytes())
 listing=(BASE/'SELECTED_FILES.txt').as_posix();put('SELECTED_FILES.txt',('\n'.join(selected+[listing])+'\n').encode('utf8'))
 sys.path.insert(0,str(REPO/'archive_tools'));spec=importlib.util.spec_from_file_location('original_c2_request_recorder',REPO/'archive_tools/record_experiment.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);original=mod.git
 def adapted(*args):
  if args and args[0]=='add':args=('add','--sparse',*args[1:])
  try:return original(*args)
  except subprocess.CalledProcessError as e:print('HELPER_GIT_FAILURE',e.stdout,e.stderr,flush=True);raise
 mod.git=adapted
 sys.argv=['record_experiment.py','--id',ID,'--title','Port existing command deadline invalidation guards to C2 requested cycle','--kind','diagnostic','--note-file',str(OUT/'NOTE.md'),'--validation','Native compile0/run0:3 normal+16 fault+2 precondition scenarios,246 assertions,new M4/M7 TU2of2.0 physics/real hardware,no full T01 qualification;36tasks0 formallyclosed.','--files',*selected]
 mod.main();head=git('rev-parse','HEAD');tags=git('tag','--points-at','HEAD','--list',f'trial-*-{ID}').splitlines()
 if len(tags)!=1:raise RuntimeError('Expected one recorder-created tag')
 tag=tags[0];tagobj=git('rev-parse',tag)
 subprocess.run(['git','-C',str(REPO),'push','--atomic','origin',f'HEAD:refs/heads/{BRANCH}',f'refs/tags/{tag}:refs/tags/{tag}'],check=True)
 refs={line.split()[1]:line.split()[0] for line in git('ls-remote','origin',f'refs/heads/{BRANCH}',f'refs/tags/{tag}',f'refs/tags/{tag}^{{}}').splitlines()}
 if refs.get('refs/heads/'+BRANCH)!=head or refs.get('refs/tags/'+tag)!=tagobj or refs.get('refs/tags/'+tag+'^{}')!=head:raise RuntimeError('Remote identity mismatch')
 print(json.dumps(dict(commit=head,tag=tag,tag_object=tagobj,selected_count=len(selected),remote=refs),indent=2),flush=True)
if __name__=='__main__':main()
