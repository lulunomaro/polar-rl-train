"""ONE R27 real evaluation stage. Recorder once; resume existing objects after commit."""
from pathlib import Path
import importlib.util,json,subprocess,sys
R=Path(__file__).resolve().parent;W=R.parent;V1=W/'mod4v1_lqr_mpc_robust_20261102'
REPO=W/'repo-lqr-robust';BRANCH='mod4v1-lqr-mpc-robust';ID='mod4v2-nominal-band-m0'
BASE=Path('history/experiments/mod4v2_nominal_band_m0_20261106');OUT=REPO/BASE
CASE=R/'T01_NOMINAL_BAND_M0_V1/runs/v2_t01_nominal_band_m0_520180_001'
def main():
 def git(*a):return subprocess.run(['git','-C',str(REPO),*a],check=True,capture_output=True,text=True).stdout.strip()
 if git('branch','--show-current')!=BRANCH or git('diff','--cached','--name-only'):raise RuntimeError('Wrongbranch/stageddata')
 if OUT.exists()or git('tag','--list',f'trial-*-{ID}'):raise RuntimeError('Existingprefix/tag:resumeobjects,no recorderretry')
 result=json.loads((CASE/'result.json').read_text(encoding='utf-8'))
 if result['controls']!=1200 or result['physics_steps']!=24000 or result['controller_changed']is not False or result['robust_corridor_certified']is not False or not result['previous_three_mechanisms_frozen']:raise RuntimeError('Unexpected case receipt')
 root=['TERRAIN_ADAPTATION_TASKS_V2.md','plan_public_upperdeck_once.py','plan_public_upperdeck_001.log','inspect_upperdeck_datum_once.py','inspect_upperdeck_datum_001.log',
  'prepare_upperdeck_case_once.py','create_public_band_experiment_once.py','create_public_band_experiment_001.log','prepare_nominal_band_case_once.py','prepare_nominal_band_case_001.log',
  'prepare_nominal_band_case_recovery001.py','prepare_nominal_band_case_recovery001.log','NOMINAL_BAND_PREP_ATTEMPT001.json','prepare_uniform_corridor_case_once.py',
  'runtime_v2.py','model_builder_v2.py','bridge_v2.py','dr_v2.py','v2_linearization.py','nominal_gain_v2.json',
  'controller_base_v2.py','controller_coord_v2.py','controller_roll_v2.py','controller_heading_v2.py','observed_bridge_v1.py','actuation_telemetry_v1.py',
  'public_signal_adapter_v1.py','signal_alignment_v1.py','diagnostic_stream_v1.py','SENSOR_TIME_METADATA_V1/publisher.py',
  'NOMINAL_COLLISION_ENVELOPE_V1/RESULT.json','PUBLIC_UNIFORM_CORRIDOR_V1/NUMERIC_BOUNDARY_RETRY001/RESULT.json','PUBLIC_UNIFORM_CORRIDOR_V1/HEIGHT_INSPECT001/RESULT.json',
  'T01_OBSERVABILITY_V1/run_reverse_observe.py','T01_OBSERVABILITY_V1/PROTOCOL.json']
 for dirname in('PUBLIC_UPPERDECK_CORRIDOR_V1','PUBLIC_NOMINAL_BAND_EXPERIMENT_V1','T01_NOMINAL_BAND_M0_V1'):
  root.extend(p.relative_to(R).as_posix()for p in sorted((R/dirname).rglob('*'))if p.is_file()and p.suffix in('.py','.json','.md','.log'))
 root=list(dict.fromkeys(root));provenance=['physics_bridge.py','physics_bridge_v3.py','physics_bridge_v4_grade.py','sensor_core.py','sensor_core_v4.py',
  'RM_ROBUSTNESS_V1/t01_contact_audit.py','NORMAL_P25_HOLDOUT_V1/CONTROLLER_PACK.json','RM_FPS_PLAYER_V1/terrain.py']
 p0=W/'mod4v2_p0_mechanical_limits_20261105/candidates/HW300N60/package'
 routes=Path('C:/Users/lulu/Desktop/claude/mjcf/MOD4_LOCAL_LATEST_MOE_PLAYER_REQUESTED_20261023/player/routes.json')
 additional=[(Path('provenance/P0/kinematics_v2.py'),p0/'kinematics_v2.py'),(Path('provenance/P0/runtime_adapter_v2.py'),p0/'runtime_adapter_v2.py'),(Path('provenance/latest_routes.json'),routes)]
 for p in [R/rel for rel in root]+[V1/rel for rel in provenance]+[p for _,p in additional]:
  if not p.is_file()or p.stat().st_size>2_000_000:raise RuntimeError('Missing/large selected source:'+str(p))
 note='''# MOD4v2 R27: unchanged M0 nominal-band original-gate PASS, no robust corridor certificate

Whole36formal0/36,T01ongoing35pending,goal29activearmed/max40. Latesthuman ALLMOD4v2traditionalLQR,not withdrawn GPU/RL migration. SameP0c19source,300N60mm/k2000d3UNMEASURED,cylinder.0625/.01+guide.015/.9,full31robotbody+world/6connect4mimic/full29x16CAD47289statics. Runtime.5msNewton100/100Hz/originalinverseNomPD-target-D4-currentPD-signedDC-gain-sameDC. Newv2K/trim/originalM0unchanged,not M1/M2/M3 or M4;3of3 failures frozen. Supporteduprightspawn not naturalrise. UI/BSP/sourceassets unchanged/nohardware.

First new fixed public upper-deck source question no anchor within1um/6hulls/LP0. Bounded2point datum diagnosis24hulls/0modelPHY:publishedanchor[-1.5,0]top.40002 vs.40000000596,plannedcenter[0,0]highest.19002,not continuous.4mdeck. Stop520170 with no derivedcase. 520160 also unused. Preserve all code/results including unexecuted preparer;no source query reruns.

New explicit nominal experiment instead of making a worst-case corridor certificate mandatory for any simulation. Choose Y=-1.353424328589362 from midpoint of alreadycomputedsourcefreeband,not controller-scoresearch/newsourceparse. Groundplane real3553,originalX-9to-5.5. Nominal fullgeom box+4cm fits,while oldR26 declared pose/lateral1.2987m requirement still FAILS. This is NOT old route performance improvement/robust planning proof/margin-threshold relaxation. Source robust_corridor_certified=false remains in actual result. Actual1200cached311geometry scopes stayedinside but100HzPREage.5ms is not continuous sweep/allpossibleposes;root/contact/motor/alignment are private observations/no actor/proxy/FSM return. Forcefalse/alpha and hardware torque calibration unknown.

ONEnew520180nominal12s1200control24000truephysics/freshmodel+FullDR1/45.5548swall:all16originalchecksPASS. Score2-12s LRmain99.82/99.85%,whole0/guidehard0,pitchpeak.01264145/roll.00614466rad. vxRMSE.01038096/progress1.832456/lateral.01016065/final9-12stopRMS.0128689. Entire24000physics bothDC6axis changed0,notrail/current/thermal/delivery/hardware measured torque. Actual1198aligned/2startupunknown,forcefalse. Onecase does not graduateT01/full36/95%reliability/T36 orrealhardware/ARMtime. Wholecase45.55sfor12ssim not wallclock100Hzqualification.

Preparation inherited unexecutedR26 metadata17-spacecontinuations vs actual16;compile failedBEFOREnewprefix/model/physics. Original source/log kept,NOMINAL_BAND_PREP_ATTEMPT001,one exactASTrecovery2literal/3continuations followed by sole actualcase. No oldQA/raw/holdout/newagent/GPU/SSH/PPO/flash. Sevenv2nominal8400ctrl168000physicalnow;oldfailuresstillfail. Newraw NOTadditionallyreduced or payloadreread/hashedforarchive. Next freeze new nominalstand and boundednewTRAIN_DR,no old520112..115replay/noM4.

Actual small case receipt:
'''
 note+=json.dumps({k:result.get(k)for k in('status','complete','controls','physics_steps','counts','total_case_wall_s','checks','case_screen_pass','metrics','contact_metrics','source_plan_private_scope','new_scenario_scope_valid','robust_corridor_certified')},indent=2)
 note+='\n\nOriginalhelperonce/inmemorysparseadd/atomicnonforceownbranch+tag/remote3identities. main readonly concurrent observation only;noRLworktree/index/main/reset/force. Olderpending stages remainpending;this is not a standalone asset workspace.\n'
 OUT.mkdir(parents=True,exist_ok=False);selected=[]
 def put(rel,data):
  p=OUT/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);selected.append(p.relative_to(REPO).as_posix())
 for rel in root:put(Path('payload/v2')/rel,(R/rel).read_bytes())
 for rel in provenance:put(Path('provenance/v1')/rel,(V1/rel).read_bytes())
 for rel,p in additional:put(rel,p.read_bytes())
 receipts=[]
 for rc in result['producer_raw_receipts']:
  if Path(rc['path']).stat().st_size!=rc['bytes']:raise RuntimeError('Closed raw size changed')
  receipts.append(dict(rc,archival_payload_read=False,archival_payload_hash=False))
 xml=p0/'mjcf/scene.xml';cad=routes.parent/'rm7v7_latest_moe.xml'
 receipts.extend([dict(path=str(xml),bytes=xml.stat().st_size,sha256='c19c72d2690dce90fdef56bebd3b36e4c319d47b8ac7152cf42b2d01f6dfd125',archival_payload_read=False,archival_payload_hash=False),
  dict(path=str(cad),bytes=cad.stat().st_size,sha256=None,archival_payload_read=False,archival_payload_hash=False)])
 put('EXTERNAL_ARTIFACTS.json',json.dumps(receipts,indent=2).encode('utf-8'));put('NOTE.md',note.encode('utf-8'))
 put(Path(__file__).name,Path(__file__).read_bytes());listing=(BASE/'SELECTED_FILES.txt').as_posix();put('SELECTED_FILES.txt',('\n'.join(selected+[listing])+'\n').encode('utf-8'))
 sys.path.insert(0,str(REPO/'archive_tools'));spec=importlib.util.spec_from_file_location('original_v2_nominal_band_recorder',REPO/'archive_tools/record_experiment.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);original=mod.git
 def adapted(*a):
  if a and a[0]=='add':a=('add','--sparse',*a[1:])
  try:return original(*a)
  except subprocess.CalledProcessError as e:print('HELPER_GIT_FAILURE',e.stdout,e.stderr,flush=True);raise
 mod.git=adapted
 sys.argv=['record_experiment.py','--id',ID,'--title','MOD4v2 unchanged M0 nominal-band original-gate PASS, robust corridor not certified',
  '--kind','evaluation','--note-file',str(OUT/'NOTE.md'),'--validation',
  'ONE520180nominal12s1200ctrl24000physics/original16checksPASS/main99.82+99.85/wholeguidehard0/newscopeobservedtrue/robustcorridorfalse/allDCchanged0;sourceupperdeckrejected;0oldQA/newagent/hardware;overall0of36.', '--files',*selected]
 mod.main();head=git('rev-parse','HEAD');tags=git('tag','--points-at','HEAD','--list',f'trial-*-{ID}').splitlines()
 if len(tags)!=1:raise RuntimeError('Expected unique annotatedtrial')
 tag=tags[0];tagobj=git('rev-parse',tag)
 subprocess.run(['git','-C',str(REPO),'push','--atomic','origin',f'HEAD:refs/heads/{BRANCH}',f'refs/tags/{tag}:refs/tags/{tag}'],check=True)
 refs={line.split()[1]:line.split()[0]for line in git('ls-remote','origin','refs/heads/main',f'refs/heads/{BRANCH}',f'refs/tags/{tag}',f'refs/tags/{tag}^{{}}').splitlines()}
 if refs.get('refs/heads/'+BRANCH)!=head or refs.get('refs/tags/'+tag)!=tagobj or refs.get('refs/tags/'+tag+'^{}')!=head:raise RuntimeError('Remoteidentitymismatch')
 print(json.dumps(dict(commit=head,tag=tag,tag_object=tagobj,selected_count=len(selected),remote=refs,main_observed_readonly=True),indent=2),flush=True)
if __name__=='__main__':main()
