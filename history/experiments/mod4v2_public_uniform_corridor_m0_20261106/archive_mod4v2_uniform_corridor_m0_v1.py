"""ONE R26 real stage only. Existing recorder untouched; resume objects after commit."""
from pathlib import Path
import importlib.util,json,subprocess,sys
R=Path(__file__).resolve().parent;W=R.parent;V1=W/'mod4v1_lqr_mpc_robust_20261102'
REPO=W/'repo-lqr-robust';BRANCH='mod4v1-lqr-mpc-robust';ID='mod4v2-public-uniform-corridor-m0'
BASE=Path('history/experiments/mod4v2_public_uniform_corridor_m0_20261106');OUT=REPO/BASE
CASE=R/'T01_UNIFORM_CORRIDOR_V1/runs/v2_t01_uniform_corridor_m0_nominal_520160_001'

def main():
 def git(*a):return subprocess.run(['git','-C',str(REPO),*a],check=True,capture_output=True,text=True).stdout.strip()
 if git('branch','--show-current')!=BRANCH or git('diff','--cached','--name-only'):raise RuntimeError('Wrongbranch/stageddata')
 if OUT.exists()or git('tag','--list',f'trial-*-{ID}'):raise RuntimeError('Existingprefix/tag:resumeobjects,no recorderretry')
 planresult=json.loads((R/'PUBLIC_UNIFORM_CORRIDOR_V1/NUMERIC_BOUNDARY_RETRY001/RESULT.json').read_text(encoding='utf-8'))
 result=json.loads((CASE/'result.json').read_text(encoding='utf-8'))if(CASE/'result.json').is_file()else None
 if planresult['chosen_plan']is not None and result is None:raise RuntimeError('A planned case must be collected/documented before archive')
 if result is not None and(result['controls']!=1200 or result['physics_steps']!=24000 or result['controller_changed']is not False or not result['previous_three_mechanisms_frozen']):raise RuntimeError('Unexpected newscenario receipt')
 root=['TERRAIN_ADAPTATION_TASKS_V2.md','plan_public_uniform_corridor_once.py','prepare_uniform_corridor_case_once.py',
  'UNIFORM_CORRIDOR_SCENARIO_V1.md','plan_public_uniform_corridor_001.log','runtime_v2.py','model_builder_v2.py','bridge_v2.py','dr_v2.py',
  'v2_linearization.py','nominal_gain_v2.json','controller_base_v2.py','controller_coord_v2.py','controller_roll_v2.py','controller_heading_v2.py',
  'observed_bridge_v1.py','actuation_telemetry_v1.py','public_signal_adapter_v1.py','signal_alignment_v1.py','diagnostic_stream_v1.py','SENSOR_TIME_METADATA_V1/publisher.py']
 for dirname in('NOMINAL_COLLISION_ENVELOPE_V1','PUBLIC_UNIFORM_CORRIDOR_V1','T01_UNIFORM_CORRIDOR_V1'):
  folder=R/dirname
  if folder.exists():
   root.extend(p.relative_to(R).as_posix()for p in sorted(folder.rglob('*'))if p.is_file()and p.suffix in('.py','.json','.md','.log')and p.name not in('trace.jsonl','contact_trace.jsonl','motor_trace.jsonl'))
 for optional in('prepare_uniform_corridor_case_001.log',):
  if(R/optional).is_file():root.append(optional)
 root.extend(['inspect_corridor_blocker_heights_once.py','inspect_corridor_blocker_heights_001.log','plan_public_uniform_corridor_numeric_retry001.py',
  'plan_public_uniform_corridor_numeric_retry001.log','plan_public_uniform_corridor_numeric_prepare_recovery001.py',
  'plan_public_uniform_corridor_numeric_prepare_recovery001.log','PUBLIC_UNIFORM_CORRIDOR_NUMERIC_PREP_ERROR001.json'])
 root=list(dict.fromkeys(root));provenance=['physics_bridge.py','physics_bridge_v3.py','physics_bridge_v4_grade.py','sensor_core.py','sensor_core_v4.py',
  'RM_ROBUSTNESS_V1/t01_contact_audit.py','NORMAL_P25_HOLDOUT_V1/CONTROLLER_PACK.json','RM_FPS_PLAYER_V1/terrain.py']
 for p in [R/rel for rel in root]+[V1/rel for rel in provenance]:
  if not p.is_file()or p.stat().st_size>2_000_000:raise RuntimeError('Missing/large selected source:'+str(p))
 note='''# MOD4v2 R26: public CAD corridor planning, unchanged M0 in an explicit new scenario

Whole36formal0/36,T01ongoing35pending,goal29activearmed/max40. Old route failures and M1/M2/M3=3/3 frozen;not a fourth mechanism,not matched old-route tuning improvement. OriginalP0/cylinder tires/300N60mm/k2000d3 unmeasured/source and fullCAD/PD-target-D4-currentPD-twoDC/100Hz and.5msNewton100 unchanged. Source geometric corridor includes all-robot nominal AABB plus stated pose/lateral margins,not full joint-domain/continuous dynamic/hardware swept-volume qualification. New geometry-only routing consumes no old QA/raw or old case.

Private geom bounds/root/contact and motor observations are grading only;no controller/proxy/FSM connection. Uniform authored floor is a tilted plane,not z0 fake slab. Original default runtime/UI/BSP unchanged. Even a case screen pass does not graduate T01/full36/95% reliability/hardware. Explicit supported spawn is not natural rise. Unknownalpha/errorbudgets/outputtorque calibration remain unknown and force readiness false.

Original literal source-height screening393LP/199hulls reported NO_CORRIDOR. ONE bounded structural source check identified a1mm numeric boundary,not an overhead obstacle. A newdeclared10nm source comparison tolerance (NOTcertified native source/contact total error) resolved8nearboundary solids but still NO_CORRIDOR380LP/191hulls:remaining floorYwidth.761808772m < required nominalpose+lateral+clearance width1.298668442m. No margins/contact gates relaxed,520160reserved UNUSED/no derivedcase/no physics. This is only fixedX/singlefloor/constantY/full-height exclusion family,not absenceofanymaproute. Original software SyntaxError beforeSDK and numeric-prep3vs2-space anchor error before sourcequery retained,each one exactcause recovery,no nativequery replay.

Actual final numeric source-plan result (not controller score-based route search):
'''+json.dumps(dict(status=planresult['status'],chosen_plan=planresult['chosen_plan'],LP_calls=planresult['LP_calls'],selected_hull_builds=planresult['selected_hull_builds']),indent=2)+'\n\nActual new case receipt:\n'
 note+=json.dumps(None if result is None else{k:result.get(k)for k in('status','complete','controls','physics_steps','case_screen_pass','new_scenario_scope_valid','checks','contact_metrics','metrics','source_plan_private_scope','case_wall_s')},indent=2)
 note+='\n\nLarge raw/source/binaries only path/size/existing producer SHA,never archival payload rehash. Original helper once/inmemory sparse add/atomic nonforce ownbranch+tag/remote three identities. No RL index/main/reset/force/GPU/SSH/newagent/hardware;older pending states retained.\n'
 OUT.mkdir(parents=True,exist_ok=False);selected=[]
 def put(rel,data):
  p=OUT/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);selected.append(p.relative_to(REPO).as_posix())
 for rel in root:put(Path('payload/v2')/rel,(R/rel).read_bytes())
 for rel in provenance:put(Path('provenance/v1')/rel,(V1/rel).read_bytes())
 receipts=[]
 if result:
  for rc in result['producer_raw_receipts']:
   if Path(rc['path']).stat().st_size!=rc['bytes']:raise RuntimeError('Closed raw size changed')
   receipts.append(dict(rc,archival_payload_read=False,archival_payload_hash=False))
 xml=W/'mod4v2_p0_mechanical_limits_20261105/candidates/HW300N60/package/mjcf/scene.xml';cad=Path('C:/Users/lulu/Desktop/claude/mjcf/MOD4_LOCAL_LATEST_MOE_PLAYER_REQUESTED_20261023/player/rm7v7_latest_moe.xml')
 receipts.extend([dict(path=str(xml),bytes=xml.stat().st_size,sha256='c19c72d2690dce90fdef56bebd3b36e4c319d47b8ac7152cf42b2d01f6dfd125',archival_payload_read=False,archival_payload_hash=False),
  dict(path=str(cad),bytes=cad.stat().st_size,sha256=None,archival_payload_read=False,archival_payload_hash=False)])
 put('EXTERNAL_ARTIFACTS.json',json.dumps(receipts,indent=2).encode('utf-8'));put('NOTE.md',note.encode('utf-8'))
 put(Path(__file__).name,Path(__file__).read_bytes());listing=(BASE/'SELECTED_FILES.txt').as_posix();put('SELECTED_FILES.txt',('\n'.join(selected+[listing])+'\n').encode('utf-8'))
 sys.path.insert(0,str(REPO/'archive_tools'));spec=importlib.util.spec_from_file_location('original_v2_uniform_corridor_recorder',REPO/'archive_tools/record_experiment.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);original=mod.git
 def adapted(*a):
  if a and a[0]=='add':a=('add','--sparse',*a[1:])
  try:return original(*a)
  except subprocess.CalledProcessError as e:print('HELPER_GIT_FAILURE',e.stdout,e.stderr,flush=True);raise
 mod.git=adapted
 validation='Public CAD corridor geometry-only planning;originalM0 and oldcase gates unchanged;3of3 frozen;'
 validation+=('no physicalcase'if result is None else f"new520160nominal1200ctrl24000physics,originalscreen={result['case_screen_pass']},scope={result['new_scenario_scope_valid']}")
 title='MOD4v2 public CAD corridor screen: no admissible full-envelope path, M0 case not run'if result is None else'MOD4v2 public CAD uniform corridor with unchanged M0, explicit new scenario'
 sys.argv=['record_experiment.py','--id',ID,'--title',title,
  '--kind','evaluation','--note-file',str(OUT/'NOTE.md'),'--validation',validation,'--files',*selected]
 mod.main();head=git('rev-parse','HEAD');tags=git('tag','--points-at','HEAD','--list',f'trial-*-{ID}').splitlines()
 if len(tags)!=1:raise RuntimeError('Expected unique annotatedtrial')
 tag=tags[0];tagobj=git('rev-parse',tag)
 subprocess.run(['git','-C',str(REPO),'push','--atomic','origin',f'HEAD:refs/heads/{BRANCH}',f'refs/tags/{tag}:refs/tags/{tag}'],check=True)
 refs={line.split()[1]:line.split()[0]for line in git('ls-remote','origin','refs/heads/main',f'refs/heads/{BRANCH}',f'refs/tags/{tag}',f'refs/tags/{tag}^{{}}').splitlines()}
 if refs.get('refs/heads/'+BRANCH)!=head or refs.get('refs/tags/'+tag)!=tagobj or refs.get('refs/tags/'+tag+'^{}')!=head:raise RuntimeError('Remoteidentitymismatch')
 print(json.dumps(dict(commit=head,tag=tag,tag_object=tagobj,selected_count=len(selected),remote=refs,main_observed_readonly=True),indent=2),flush=True)
if __name__=='__main__':main()
