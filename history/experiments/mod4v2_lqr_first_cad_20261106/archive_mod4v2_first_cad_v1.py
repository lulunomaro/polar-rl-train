"""Archive this real model/gain/case stage once; no physics, raw reads or old QA.
Continue an existing commit/tag after push failure; never rerun this recorder.
"""
from pathlib import Path
import importlib.util,json,subprocess,sys
R=Path(__file__).resolve().parent;W=R.parent;V1=W/'mod4v1_lqr_mpc_robust_20261102'
REPO=W/'repo-lqr-robust';BRANCH='mod4v1-lqr-mpc-robust'
ID='mod4v2-lqr-first-cad-baseline';BASE=Path('history/experiments/mod4v2_lqr_first_cad_20261106');OUT=REPO/BASE
CASES=['v2_t01_nominal_stand_520110_001','v2_t01_nominal_slow_520111_001']
NOTE='''# MOD4v2 traditional LQR model switch and first actual CAD baselines

Human withdrew the mistaken dual-GPU/RL migration request, requested all LQR tuning on MOD4v2 and a persistent goal. Existing goal edited/resumed revision29, active/armed, cap40 with old20 rounds retained. Same36 motion tasks; no RL migration, GPU, SSH, new agent, firmware flash, hardware motor traffic or old QA/holdout replay. Original v1 history and this independent branch preserved. Reused the existing static-gain child only; it stopped after completion.

Actual P0 HW300N60 source:300N nominal/60mm/140-200mm eyes, springref.1706394410901294, k2000/d3 still unmeasured approximations, physical crank-minus-hip branch[-1.0863195404360622,+.49192233306644084]. No legacy400N/50mm or old active-angle hard window. Actual delivered P0 MJCF has radius.0625/halfwidth.01 CYLINDER tires and guide radius.015/friction.9, NOT the v1 faceted tire/.0637/.016/.02 collision representation. Results are specific to that delivered representation, not full tire-mesh/PhysX/hardware qualification. P0 source not modified. Independent runtime copy explicitly uses.5ms implicitfast/Newton100,100Hz control,IMU(.03,0,.04);source P0 uses2.5ms/Newton32. Full31-body robot plus world,nq37/nv36/nu6,6connect+4mimic,14.294140288606286kg retained; actual latest29x16m CAD includes47289 static meshes/47282 collision prisms,47600 total geoms. No fake ground slab.

New static/14state dynamics/DARE generated once with actual P0 absolute hip/crank setter and radius.0625;old projected dynamics/Q/R/ZOH structure reused,not old K/trim. At delta-.2,hip.2503281103649727,trimNm[3.02146310898,-4.06509848466,~0,3.00195105489,-4.04937209735,~0]. Static residual1.66141e-9,relative DARE residual1.035e-15,local closed-loop spectral radius.992779681593. 558 P0 setters/1716 forwards/zero integration in synthesis. Runtime re-solves on fresh v2 Ad/Bd with existing P25 settings;old pack K not assigned. This static/local linear proof is not closed-loop qualification.

Reused sensor-window,estimator,coord_soft common sagittal LQR+differential-leg PD,park bleed,jerk shaper,roll reference and heading math. New mechanical target projection uses encoder feedback branch and P0 limits;retains inverse nominal PD -> processed target D4 -> current PD -> signed DC -> independent motor gain -> signed DC. Six load-side joint torques/real limits retained. Root/contact truth is private grading only;explicit supported-upright spawn is not natural standup. Four DR TRAIN cases were predeclared but NOT started after nominal failure.

Two independent12s latest-CAD nominal cases completed1200 controls/24000 physics each,48000 total. Standing520110 passed all15 case checks:2-12s pitch peak.0005654336rad,roll.0052261008rad,XY drift.01015754m,vx RMS.0008806573m/s,both main wheels100% >1N support,guide/hard/whole-body unsupported0 at20000 grading samples. Wall39.2952s.

Low-speed520111 kept same gains/controller/gates:0-2s stand,2-8s+.3m/s,8-12s stop. All noncontact checks passed:pitch peak.01708866rad,roll.02984551rad,steady speed RMSE.04067886m/s,progress1.62258568m,lateral.04106813m,final vx RMS.01932536m/s. CONTACT FAILED:left/right support91.570%/98.035%,left below95%;92 all-body-normal-sum<=1N samples,longest.5ms,original zero-event gate not met. Guide/hard0. Main normal-force peaks2363.21/235.60N are simulator outputs,not a hardware soft-contact limit. Wall43.5892s. Do not interpret isolated.5ms unsupported samples as macroscopic flight,or assert v1 tire faceting was a unique proven cause. Do not lower gates or turn rc0 into pass. Both fresh models and DR constructions each1. Overall0/36,T01ongoing,35pending,DR520112-520115paused. No fourth blind v1 control or repeated micrometer probes.

Software failure retained:prepare_t01_v2.py generated runner/protocol,then counted40 table rows because regex included4 historical reuse rows in addition to36 canonical rows.0physics at failure. Original script/prefix preserved;new retry only recovered absent ledger by canonical-section scope,not rerunning runtime/protocol generation. One host file-observation denial was resolved by reading generated DR source before metadata-only schema-label correction;no physics retry or ACL repair. Existing nominal cases are consumed,never rerun for archival.

Snapshot contains selected small source/config/results/logs only and provenance dependencies;not a standalone asset/whole-workspace archive. Four large new raw traces and original P0/CAD sources are indexed by real path/size and known producer SHA or null;no payload reads/hashes for archival. Original recorder unchanged and invoked once,with in-memory sparse-add adapter. Only own branch+unique annotated trial atomic nonforce push,remote own/tag/peeled exact checks;main merely observed read-only,never restored or pushed. Prior c0fe82d7 and older pending historical archive gaps remain. Post-push receipt edit rides next real stage;no receipt-archive loop. Next substantive work:one bounded reduction of NEW failure control/support timing before at most one evidence-based narrow mechanism;not old QA or another micro-gap probe.
'''
def main():
 def git(*args):return subprocess.run(['git','-C',str(REPO),*args],check=True,capture_output=True,text=True).stdout.strip()
 if git('branch','--show-current')!=BRANCH or git('diff','--cached','--name-only'):raise RuntimeError('Wrong branch or staged changes')
 if git('tag','--list',f'trial-*-{ID}'):raise RuntimeError('Trial already exists: resume original objects')
 if OUT.exists():raise RuntimeError('Archive prefix exists: inspect instead of rerunning')
 for case in CASES:
  p=R/'T01_V2/runs'/case/'result.json';result=json.loads(p.read_text(encoding='utf-8'))
  if not result['complete'] or result['physics_steps']!=24000:raise RuntimeError('Expected collected actual case, not partial')
 OUT.mkdir(parents=True,exist_ok=False);selected=[]
 def put(rel,data):
  p=OUT/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);selected.append(p.relative_to(REPO).as_posix())
 def copy(source,rel):
  if source.stat().st_size>2_000_000:raise RuntimeError('Large payload must stay external: '+str(source))
  put(rel,source.read_bytes())
 sources=['TERRAIN_ADAPTATION_TASKS_V2.md','model_builder_v2.py','v2_linearization.py','prepare_nominal_gain_v2.py','nominal_gain_v2.json',
 'bridge_v2.py','runtime_v2.py','dr_v2.py','controller_base_v2.py','controller_coord_v2.py','controller_roll_v2.py','controller_heading_v2.py',
 'prepare_runtime_v2.py','prepare_t01_v2.py','prepare_ledger_v2_retry001.py','RUNTIME_REUSE_MAP.json','PREP_T01_LEDGER_ATTEMPT001.json',
 'nominal_generation_attempt001/START.json','nominal_generation_attempt001/STATIC_PREFIX.json','prepare_nominal_gain_v2_001.log',
 'T01_V2/run_t01_v2.py','T01_V2/T01_PROTOCOL_V1.json']
 for case in CASES:
  sources += ['T01_V2/runs/'+case+'/'+n for n in ['config.json','protocol.json','meta.json','result.json']]
  sources += ['T01_V2/'+case+'.console.log']
 for rel in sources:copy(R/rel,Path('payload/v2')/rel)
 old=['TERRAIN_ADAPTATION_TASKS_V1.md','physics_bridge.py','physics_bridge_v3.py','physics_bridge_v4_grade.py','sensor_core_v4.py','sensor_core_jump_v1.py',
 'RM_FPS_PLAYER_V1/terrain.py','NORMAL_P25_HOLDOUT_V1/CONTROLLER_PACK.json']
 for rel in old:copy(V1/rel,Path('provenance/v1')/rel)
 for name in ['control_core.py','full_lqr.py','kinematics.py']:
  copy(W/'traditional_control_20261101'/name,Path('provenance/projected_dynamics')/name)
 package=W/'mod4v2_p0_mechanical_limits_20261105/candidates/HW300N60/package'
 for name in ['kinematics_v2.py','runtime_adapter_v2.py']:copy(package/name,Path('provenance/P0')/name)
 copy(W/'mod4v2_p0_mechanical_limits_20261105/MOD4V2_P0_RELEASE_REPORT_V1.md',Path('provenance/P0/MOD4V2_P0_RELEASE_REPORT_V1.md'))
 external=[]
 for case in CASES:
  for name in ['trace.jsonl','contact_trace.jsonl']:
   p=R/'T01_V2/runs'/case/name
   external.append(dict(path=str(p),bytes=p.stat().st_size,sha256=None,reason='Producer did not supply SHA; not read or hashed for archival'))
 for p,known in [(package/'mjcf/scene.xml','c19c72d2690dce90fdef56bebd3b36e4c319d47b8ac7152cf42b2d01f6dfd125'),
 (Path(r'C:\Users\lulu\Desktop\claude\mjcf\MOD4_LOCAL_LATEST_MOE_PLAYER_REQUESTED_20261023\player\rm7v7_latest_moe.xml'),None)]:
  external.append(dict(path=str(p),bytes=p.stat().st_size,sha256=known,reason='Original asset retained externally; SHA from runtime identity/public release if known, no archival payload read'))
 put('EXTERNAL_ARTIFACTS.json',json.dumps(external,indent=2).encode('utf-8'));put('NOTE.md',NOTE.encode('utf-8'))
 put(Path(__file__).name,Path(__file__).read_bytes())
 listing=(BASE/'SELECTED_FILES.txt').as_posix();put('SELECTED_FILES.txt',('\n'.join(selected+[listing])+'\n').encode('utf-8'))
 sys.path.insert(0,str(REPO/'archive_tools'));spec=importlib.util.spec_from_file_location('original_v2_baseline_recorder',REPO/'archive_tools/record_experiment.py')
 mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);original=mod.git
 def adapted(*args):
  if args and args[0]=='add':args=('add','--sparse',*args[1:])
  try:return original(*args)
  except subprocess.CalledProcessError as e:print('HELPER_GIT_FAILURE',e.stdout,e.stderr,flush=True);raise
 mod.git=adapted
 sys.argv=['record_experiment.py','--id',ID,'--title','Adapt traditional LQR to MOD4v2 and retain first actual CAD stand pass and slow contact failure',
 '--kind','evaluation','--note-file',str(OUT/'NOTE.md'),'--validation','New P0 statics/14state DARE0steps;actual latest-CAD nominal stand PASS and slow support FAIL,2400control/48000physics;DRpaused,0of36 closed,no hardware qualification.', '--files',*selected]
 mod.main();head=git('rev-parse','HEAD');tags=git('tag','--points-at','HEAD','--list',f'trial-*-{ID}').splitlines()
 if len(tags)!=1:raise RuntimeError('Expected one recorder tag')
 tag=tags[0];tagobj=git('rev-parse',tag)
 subprocess.run(['git','-C',str(REPO),'push','--atomic','origin',f'HEAD:refs/heads/{BRANCH}',f'refs/tags/{tag}:refs/tags/{tag}'],check=True)
 refs={line.split()[1]:line.split()[0]for line in git('ls-remote','origin','refs/heads/main',f'refs/heads/{BRANCH}',f'refs/tags/{tag}',f'refs/tags/{tag}^{{}}').splitlines()}
 if refs.get('refs/heads/'+BRANCH)!=head or refs.get('refs/tags/'+tag)!=tagobj or refs.get('refs/tags/'+tag+'^{}')!=head:raise RuntimeError('Remote identity mismatch')
 print(json.dumps(dict(commit=head,tag=tag,tag_object=tagobj,selected_count=len(selected),remote=refs,main_observed_readonly=True),indent=2),flush=True)
if __name__=='__main__':main()
