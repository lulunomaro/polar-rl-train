"""Archive the consumed v2 support reduction and single failed M1 case once.
Continue existing objects after any push failure: never repeat the recorder.
"""
from pathlib import Path
import importlib.util,json,subprocess,sys
R=Path(__file__).resolve().parent;W=R.parent;V1=W/'mod4v1_lqr_mpc_robust_20261102'
REPO=W/'repo-lqr-robust';BRANCH='mod4v1-lqr-mpc-robust'
ID='mod4v2-lqr-m1-roll-force';BASE=Path('history/experiments/mod4v2_lqr_m1_roll_force_20261106');OUT=REPO/BASE
CASE='v2_t01_roll_force_nominal_slow_520121_001';C=R/'T01_ROLL_FORCE_V1/runs'/CASE
NOTE='''# MOD4v2 support-timing reduction and bounded roll-force candidate M1: failed, not adopted

Same human-requested all-traditional-LQR MOD4v2 goal revision29 active, max40;36 motion tasks formally0/36, T01 only. No RL/GPU/SSH/new agent/old QA/holdout replay/hardware flash or motor traffic. This stage does not qualify T24 or any other motion task. Original v1 history, first v2 a362ef38 and older pending archive gaps remain.

One pass of NEW v2 failed low-speed trace1200 + contact trace20000,0new models/physics/old raw: reproduced all1200 requested torques with max difference0 using estimated state/roll and zero unlogged gyro only because both old roll coefficients are0. This is controller replay, not a full sensor/dynamics oracle. Both main-wheel low-normal samples are bracketed by support within2ms; most positive-force geom sets do not change. Recorded data omits zero-force contacts, so this is not geometric-gap or root-cause proof. Left low-normal1686/right393/whole unsupported92;79/92whole samples occur7-8s. Equivalent old differential-PD axial stiffness2294-2538N/m,not the discarded speculative ultra-stiff hypothesis. Actual2kHz motor saturation was not logged and stays unknown.

Source reuse: SPR chassis_task.c919,972-973 roll PD-on-measurement and +/- leg-force structure only. No foreign gains/rod lengths/gas-force formulas/units. New candidate inherits current v2 heading/coord_soft LQR and adds an IMU-only bounded roll moment mapped through this robot's public Jacobians. Nominal point-mass design h=.238543198,m=14.294140289,Kp66.899686,Kd7.302493 is explicitly not identified COM/inertia. Per-side force cap.2mg=28.0451N,filter.03s,extra joint cap6Nm,whole couple scaled together by available headroom;wheel extras0. This is an active-ground T01 hypothesis, not calibrated support force/contact identity/flight control. Original gain,shaper,physics,CAD,gas,clock,collision representation and PD-target/D4/current-PD/double-DC chain unchanged;root/contact truth private grading only. Delivered P0 cylinder tires.0625/.01 and guide.015/.9 are not the old v1 faceted-tire collision representation. Original P0 scene remains untouched.

ONLY one NEW12s nominal case520121 ran:1200control/24000physics/fresh model and FullDR each1/wall46.0042187s. All noncontact checks pass,roll peak.02984551->.02207289rad/RMS.00941665->.00734366;speed RMSE.04067886->.03975924m/s. Left/right support91.570/98.035->91.640/98.160 percent,whole unsupported92->84;guide/hard0. Original each-wheel95% and zero whole-unsupported gates still FAIL. Candidate not adopted, original runtime preserved, no second mechanism/DR/gain sweep/micrometer probe. One nominal pair is not independent reliability or proven causality. V2 total3nominal cases3600control/72000physics,0/36closed.

One NEW M1 control-telemetry pass1200rows/0physics/0oldraw:all packet+gyro rows present,requested force-couple peak6.28299N/extra joint1.11153Nm/headroom scaling0calls. Requests are not measured support;actual2kHz motor clipping duty remains unknown. Both one-pass reductions are consumed;use compact results,not repeated raw scans.

Software prefix retained: first preparation expected3leading spaces at a comment anchor but actual runtime uses2;asserted before new model/physics/case. Original failed generator and error JSON preserved. One separate recovery uses actual semantic line indentation and known prefix only,then runs the unique case. No preparation/case/one-pass reduction rerun for archival.

Reused existing E4 child is independently adapting CONTACT_PROXY_V2 nominal public parameters and at most3static0-step poses,confidence cap<=.55 and domain/calibration/timing restrictions retained. It is not connected to control and has no contact-identity qualification. Its LIVE directory is intentionally excluded from this snapshot;no child Git or physics.

Selected small source/protocol/results/logs/provenance only,not a standalone full-asset workspace. Raw and original P0/CAD are path/size/producer-known-SHA-or-null indices;no large payload read/hash for archival. Original recorder unchanged,one invocation,in-memory sparse-add adapter,only own branch+unique annotated trial atomic nonforce push and exact remote own/tag/peeled verification. No main or RL-worktree modification;main only read-only observation. Postreceipt task edit rides next real stage,not a receipt-archive loop.
'''
def main():
 def git(*args):return subprocess.run(['git','-C',str(REPO),*args],check=True,capture_output=True,text=True).stdout.strip()
 if git('branch','--show-current')!=BRANCH or git('diff','--cached','--name-only'):raise RuntimeError('Wrong branch or staged changes')
 if git('tag','--list',f'trial-*-{ID}') or OUT.exists():raise RuntimeError('Archive exists: resume original objects instead of rerecording')
 b=json.loads((C/'result.json').read_text(encoding='utf-8'))
 if not b['complete'] or b['controls']!=1200 or b['physics_steps']!=24000 or b['case_screen_pass']:raise RuntimeError('Expected collected M1 contact failure')
 OUT.mkdir(parents=True,exist_ok=False);selected=[]
 def put(rel,data):
  p=OUT/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);selected.append(p.relative_to(REPO).as_posix())
 def copy(source,rel):
  if source.stat().st_size>2_000_000:raise RuntimeError('Large payload must remain external: '+str(source))
  put(rel,source.read_bytes())
 root=['TERRAIN_ADAPTATION_TASKS_V2.md','controller_roll_force_v1.py','runtime_roll_force_v1.py','prepare_roll_force_v1.py','prepare_roll_force_retry001.py',
 'nominal_gain_v2.json','runtime_v2.py','bridge_v2.py','model_builder_v2.py','dr_v2.py','controller_base_v2.py','controller_coord_v2.py','controller_roll_v2.py','controller_heading_v2.py']
 root += ['T01_SUPPORT_TIMING_V1/'+p for p in ['reduce_once.py','reduce_once_001.log','reduction001/START.json','reduction001/RESULT.json']]
 root += ['T01_ROLL_FORCE_V1/'+p for p in ['run_t01_roll_force.py','T01_PROTOCOL_V1.json','PREP_ATTEMPT001.json','README.md','summarize_once.py','M1_REDUCTION001.json','summarize_once_001.log',CASE+'.console.log']]
 root += ['T01_ROLL_FORCE_V1/runs/'+CASE+'/'+p for p in ['config.json','protocol.json','meta.json','result.json']]
 for rel in root:copy(R/rel,Path('payload/v2')/rel)
 copy(R/'T01_V2/runs/v2_t01_nominal_slow_520111_001/result.json',Path('provenance/baseline_v2_result.json'))
 copy(R/'T01_V2/T01_PROTOCOL_V1.json',Path('provenance/baseline_T01_protocol.json'))
 for rel in ['sensor_core_v4.py','RM_ROBUSTNESS_V1/t01_contact_audit.py','SOURCE_REUSE_20261104_1542/spr2_selected/chassis/Task/chassis_task.c']:
  copy(V1/rel,Path('provenance/v1')/rel)
 external=[]
 for name in ['trace.jsonl','contact_trace.jsonl']:
  p=C/name;external.append(dict(path=str(p),bytes=p.stat().st_size,sha256=None,reason='No producer raw SHA; not read or hashed for archival'))
 for p,sha in [(W/'mod4v2_p0_mechanical_limits_20261105/candidates/HW300N60/package/mjcf/scene.xml','c19c72d2690dce90fdef56bebd3b36e4c319d47b8ac7152cf42b2d01f6dfd125'),
 (Path(r'C:\Users\lulu\Desktop\claude\mjcf\MOD4_LOCAL_LATEST_MOE_PLAYER_REQUESTED_20261023\player\rm7v7_latest_moe.xml'),None)]:
  external.append(dict(path=str(p),bytes=p.stat().st_size,sha256=sha,reason='External original asset; known runtime identity/publication SHA or null, no archival payload read'))
 put('EXTERNAL_ARTIFACTS.json',json.dumps(external,indent=2).encode('utf-8'));put('NOTE.md',NOTE.encode('utf-8'));put(Path(__file__).name,Path(__file__).read_bytes())
 listing=(BASE/'SELECTED_FILES.txt').as_posix();put('SELECTED_FILES.txt',('\n'.join(selected+[listing])+'\n').encode('utf-8'))
 sys.path.insert(0,str(REPO/'archive_tools'));spec=importlib.util.spec_from_file_location('original_mod4v2_m1_recorder',REPO/'archive_tools/record_experiment.py')
 mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);original=mod.git
 def adapted(*args):
  if args and args[0]=='add':args=('add','--sparse',*args[1:])
  try:return original(*args)
  except subprocess.CalledProcessError as e:print('HELPER_GIT_FAILURE',e.stdout,e.stderr,flush=True);raise
 mod.git=adapted
 sys.argv=['record_experiment.py','--id',ID,'--title','Preserve v2 support timing and one bounded roll-force candidate failing unchanged contact gates','--kind','evaluation','--note-file',str(OUT/'NOTE.md'),
 '--validation','One new nominal M1 case1200control/24000physics;roll improved but support91.64/98.16 percent and84 unsupported ticks fail unchanged gates;not adopted,DRpaused,0of36;two one-pass reductions,no old QA/hardware.', '--files',*selected]
 mod.main();head=git('rev-parse','HEAD');tags=git('tag','--points-at','HEAD','--list',f'trial-*-{ID}').splitlines()
 if len(tags)!=1:raise RuntimeError('Expected unique recorder tag')
 tag=tags[0];tagobj=git('rev-parse',tag)
 subprocess.run(['git','-C',str(REPO),'push','--atomic','origin',f'HEAD:refs/heads/{BRANCH}',f'refs/tags/{tag}:refs/tags/{tag}'],check=True)
 refs={line.split()[1]:line.split()[0]for line in git('ls-remote','origin','refs/heads/main',f'refs/heads/{BRANCH}',f'refs/tags/{tag}',f'refs/tags/{tag}^{{}}').splitlines()}
 if refs.get('refs/heads/'+BRANCH)!=head or refs.get('refs/tags/'+tag)!=tagobj or refs.get('refs/tags/'+tag+'^{}')!=head:raise RuntimeError('Remote identity mismatch')
 print(json.dumps(dict(commit=head,tag=tag,tag_object=tagobj,selected_count=len(selected),remote=refs,main_observed_readonly=True),indent=2),flush=True)
if __name__=='__main__':main()
