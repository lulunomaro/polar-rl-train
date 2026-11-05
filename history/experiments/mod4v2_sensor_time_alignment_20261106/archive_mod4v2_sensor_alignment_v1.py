"""Seal completed source-time metadata and bounded-history receiver ONCE.
Both components stopped/reviewed; no old QA/model/episode rerun.
Resume existing commit/tag after push failure, never re-invoke recorder ID.
"""
from pathlib import Path
import importlib.util,json,subprocess,sys
R=Path(__file__).resolve().parent;W=R.parent;V1=W/'mod4v1_lqr_mpc_robust_20261102'
REPO=W/'repo-lqr-robust';BRANCH='mod4v1-lqr-mpc-robust'
ID='mod4v2-sensor-time-alignment';BASE=Path('history/experiments/mod4v2_sensor_time_alignment_20261106');OUT=REPO/BASE
NOTE='''# MOD4v2 source-time metadata and bounded-history PUBLIC observation receiver

Same all-traditional-LQR MOD4v2 goal revision29 active/max40,overall0/36 formally closed,T01 ongoing,35pending. Latest actual M1 contact gates still fail and M1 is not adopted. Three v2 nominal physical cases remain3600control/72000physics. This stage adds no integration/model/forward/force evaluation/old raw or QA/controller candidate/M2/DR/GPU/SSH/new agent/hardware/motor traffic. Reused E4 delivered/stopped its new optional source-time observer;parent reviewed actual source/result/contract after completion before this ONE recorder invocation. Previously sealed CONTACT_PROXY_V2 three-pose check is not reopened. Old v1 history,489236bc/f4a6bcca/a362ef38 and historical pending gaps remain.

Parent signal_alignment_v1.py is stdlib only. Per-channel bounded history retains original center,start/end,count,provenance and optional clock/noise/curvature bounds. Query chooses a common evaluation time and ACTUALLY interpolates values from bracketing observations;no extrapolation/no timestamp-only relabeling. Missing metadata or bounds stay unknown;changed duplicate/rollback latch;held views do not manufacture new derivative samples. Default age30ms/gap20ms/capacity8. Continuous hip/crank input is not silently wrapped.

NEW parent check001:224 assertions/affine maxdifference2.7755575615628914e-17;constant acceleration position has bounded linear-interpolation error,curved gyro mean retains8.3125e-7 sample-window bias. Shared10ms arrival latency stays age15.25ms. Reported signal envelopes are conditional ANALYTICAL bounds,not certified floating-point/hardware total uncertainty;comparisons use predeclared1e-11 arithmetic tolerance. Unknown bounds None;force_input_ready/hardware_sync_proven alwaysFalse/alphaNone. No lever-arm proper-at-origin transformation,actual output-torque calibration,contact identity,force/FSM/controller binding or raised proxy3ms/.55/.8 thresholds is supplied. Sim held driver command is not measured torque,even if its time label is known.

NEW child producer stub14tests/83explicit assertion calls/30predetermined source calls,0failures/errors/realmodel/FK/forward/physics/DR/oldQA/hardware. Optional mixin defaultOFF delegates original sensor_packet once and returns SAME original packet;enabled side metadata reads clocks/window counters only. N20 centers t-5.25ms;N0 IMU cache/initial torque source unknown,qd fallback endpoint. Legacy D3 nominal packet epoch can differ from actual previous source under dropped/repeated calls. The one-previous-source ledger uses observed clock/history,not hidden random delay parameters;ambiguous/mismatched epochs None/unusable,known source diagnostic separate. Torque is not in the five-channel D3 queue;role remains SIM ctrl hold,not measured output torque. Original packet/DR/RNG/source/actuation unchanged. Source time bookkeeping is not hardware acquisition calibration.

These are TWO independently checked interfaces,NOT an end-to-end actual Plant test. Producer endpoint/sampled_boxcar/held_command schemas still need explicit receiver normalization and role validation;no automatic packet-to-force adapter exists. Original runtime is not wired to either component. Alpha/calibration/torque-role uncertainty stays unknown;synthetic count/clock tests are not physical trajectories or hardware delivery. No original gyro/encoder/actuator timestamps are rewritten.

Selected small source,protocol,result,log,contract and source-provenance only;not standalone asset workspace. Large P0 XML indexed by actual path/size/existing published SHA,no archival payload hash. Original recorder unchanged and invoked once,in-memory sparse-add adapter only. Atomic/nonforce push only own branch+unique annotated trial;remote ownbranch/tag/peeled exactly verified. No RL worktree/index/main reset/push. Postreceipt edit rides next real stage,no receipt archive loop. Never rerun consumed checks for archival housekeeping.
'''
def main():
 def git(*args):return subprocess.run(['git','-C',str(REPO),*args],check=True,capture_output=True,text=True).stdout.strip()
 if git('branch','--show-current')!=BRANCH or git('diff','--cached','--name-only'):raise RuntimeError('Wrong branch or staged changes')
 if OUT.exists()or git('tag','--list',f'trial-*-{ID}'):raise RuntimeError('Existing prefix/tag: resume existing objects, do not rerecord')
 result=json.loads((R/'SENSOR_ALIGNMENT_V1/check001/result.json').read_text(encoding='utf-8'))
 child=json.loads((R/'SENSOR_TIME_METADATA_V1/STUB_RESULT.json').read_text(encoding='utf-8'))
 if not result['passed']or result['assertions']!=224 or result['real_physics_steps']!=0 or result['force_model_calls']!=0:raise RuntimeError('Unexpected alignment receipt')
 if not child['passed']or child['tests']!=14 or child['assertion_calls']!=83 or child['new_model_FK_forward_physics_DR_oldQA_Git_agents_hardware_calls']!=0:raise RuntimeError('Unexpected producer stub receipt')
 OUT.mkdir(parents=True,exist_ok=False);selected=[]
 def put(rel,data):
  p=OUT/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);selected.append(p.relative_to(REPO).as_posix())
 def copy(source,rel):
  if source.stat().st_size>2_000_000:raise RuntimeError('Large payload remains external: '+str(source))
  put(rel,source.read_bytes())
 root=['TERRAIN_ADAPTATION_TASKS_V2.md','signal_alignment_v1.py','verify_signal_alignment_v1.py','verify_signal_alignment_v1_001.log',
 'SENSOR_ALIGNMENT_V1/README.md','SENSOR_ALIGNMENT_V1/check001/protocol.json','SENSOR_ALIGNMENT_V1/check001/result.json',
 'bridge_v2.py','dr_v2.py','runtime_v2.py']
 root+=['SENSOR_TIME_METADATA_V1/'+p for p in ['publisher.py','test_publisher.py','STUB_RESULT.json','STUB_RUN_STARTED.json','CONTRACT.md']]
 for rel in root:copy(R/rel,Path('payload/v2')/rel)
 for name in ['physics_bridge.py','physics_bridge_v3.py','sensor_core.py']:
  copy(V1/name,Path('provenance/v1')/name)
 xml=W/'mod4v2_p0_mechanical_limits_20261105/candidates/HW300N60/package/mjcf/scene.xml'
 put('EXTERNAL_ARTIFACTS.json',json.dumps([dict(path=str(xml),bytes=xml.stat().st_size,
  sha256='c19c72d2690dce90fdef56bebd3b36e4c319d47b8ac7152cf42b2d01f6dfd125',reason='Original P0 asset;published identity only,no archival payload read')],indent=2).encode('utf-8'))
 put('NOTE.md',NOTE.encode('utf-8'));put(Path(__file__).name,Path(__file__).read_bytes())
 listing=(BASE/'SELECTED_FILES.txt').as_posix();put('SELECTED_FILES.txt',('\n'.join(selected+[listing])+'\n').encode('utf-8'))
 sys.path.insert(0,str(REPO/'archive_tools'));spec=importlib.util.spec_from_file_location('original_v2_sensor_time_recorder',REPO/'archive_tools/record_experiment.py')
 mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);original=mod.git
 def adapted(*args):
  if args and args[0]=='add':args=('add','--sparse',*args[1:])
  try:return original(*args)
  except subprocess.CalledProcessError as e:print('HELPER_GIT_FAILURE',e.stdout,e.stderr,flush=True);raise
 mod.git=adapted
 sys.argv=['record_experiment.py','--id',ID,'--title','Seal MOD4v2 explicit source metadata and bounded signal alignment','--kind','evaluation','--note-file',str(OUT/'NOTE.md'),
 '--validation','New receiver224asserts;new optional publisher14tests/83asserts/30stubcalls;no actual Plant connection;unknown calibration/alpha/bounds;0models/physics/force/oldraw;not hardware sync or force authority;0of36.', '--files',*selected]
 mod.main();head=git('rev-parse','HEAD');tags=git('tag','--points-at','HEAD','--list',f'trial-*-{ID}').splitlines()
 if len(tags)!=1:raise RuntimeError('Expected unique annotated trial')
 tag=tags[0];tagobj=git('rev-parse',tag)
 subprocess.run(['git','-C',str(REPO),'push','--atomic','origin',f'HEAD:refs/heads/{BRANCH}',f'refs/tags/{tag}:refs/tags/{tag}'],check=True)
 refs={line.split()[1]:line.split()[0]for line in git('ls-remote','origin','refs/heads/main',f'refs/heads/{BRANCH}',f'refs/tags/{tag}',f'refs/tags/{tag}^{{}}').splitlines()}
 if refs.get('refs/heads/'+BRANCH)!=head or refs.get('refs/tags/'+tag)!=tagobj or refs.get('refs/tags/'+tag+'^{}')!=head:raise RuntimeError('Remote identity mismatch')
 print(json.dumps(dict(commit=head,tag=tag,tag_object=tagobj,selected_count=len(selected),remote=refs,main_observed_readonly=True),indent=2),flush=True)
if __name__=='__main__':main()
