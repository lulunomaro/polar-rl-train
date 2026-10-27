"""Build new changed-plant88 payloads from qualified R5 manifests. No remote/GO.

Copies qualified native and normal witness bytes for the new deployment; does not
decode/hash old checkpoints. Actual installed admission must verify their bytes.
"""
from pathlib import Path
import ast,hashlib,json,shutil,sys,time,traceback
HERE=Path(__file__).resolve().parent;L=HERE.parent;T=L.parent;W=T.parent
OLD=T/'H1_STEP270_THREE_GPU_OWN_FUDAN_NATIVE_V87_20261027'
N=T/'H1_STEP270_OWN_STEP_GAS400_NATIVE_RESOURCE_V88B_20261027'
I=L/'native88_selected_runtime_integration_source_v1'
Q=L/'native88_installed_source_CPU_candidate_v2_JSON_schema_only'
A=L/'native88_gas400_actual_asset_CPU_admission_20261027'
O=L/'native88_own_step_differentiable_objective_source_v1'
GAS=L/'HARDWARE_GAS_SPRING_400N_L200_S60_HUMAN_20261027/agent_nominal400_target_source_candidate_v1/isolated_text_overlay_NOT_A_PAYLOAD'
S2=T/'H1_NATIVE87R5_OLD700_FROZEN_DIAGNOSTIC_R2_20261027'
sys.path.insert(0,str(HERE))
from native88_protocol_v1 import SOURCES,METHOD,BOOTSTRAP_SHA,REFERENCE_SHA,validate_spec
ROOTS=dict(h1='/mnt/mod4_linux_durable_20261013/H1step270_own_step_gas400_native_2610v88b/h1',recovery='/home/lc01/Zonglin Li/zonglin2/tasks/H1step270_own_step_gas400_native_2610v88b/recovery')
OWNER='/home/lc01/Zonglin Li/zonglin2/tasks/H1step270_own_step_gas400_native_2610v88b/owner'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def put(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def cp(src,dst):
 src=Path(src);dst=Path(dst);assert src.is_file() and not src.is_symlink();dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
def row(p,rel=None):return dict(relative=rel or p.name,bytes=p.stat().st_size,SHA=H(p))
def main():
 assert not N.exists(),'new unused namespace only'
 N.mkdir();put(N/'reports/PAYLOAD_PREPARATION_CONSUMED_BEFORE_COPY_ACTUAL.json',dict(epoch=time.time(),no_remote_CPU_or_GO=True,no_old_checkpoint_decode_or_hash=True))
 prior=read(OLD/'reports/AVAILABLE_TWO_NATIVE87R5_SOURCE_PREPARED_ACTUAL.json')
 closed=read(OLD/'reports/H1_NATIVE87R5_FINALS_AND_ORIGINAL_COST_RETURNED_ACTUAL.json')
 pair=OLD/'reports/H1_NATIVE87R5_TYPED_FINALS_AND_ORIGINAL_COST_CPU_ACTUAL.json'
 close=OLD/'reports/H1_NATIVE87R5_FINALS_AND_ORIGINAL_COST_RETURNED_ACTUAL.json'
 assert read(pair)['passed'] and closed['original_canonical_cost_settled'] and closed['authority72']['original_canonical_remaining']==569553.363275528
 geom=S2/'DERIVED_GEOMETRY_20260928.json';assert H(geom)=='461f6b44e6014c72a755a0db5136fa8d45bd5b53b6318ee4b38221a4c597bc4d'
 qualification=O/'SELECTED_OWN_STEP_OBJECTIVE_SOURCE_QUALIFICATION_FINAL_ACTUAL.json';assert H(qualification)=='dc5a6f147309310acdb812848f509b03c41b0c44781c9c9281585cbf4edb5c89'
 original_c=read(OLD/'payloads_r5/h1/NATIVE87_SOURCE_CONTRACT_ACTUAL.json')
 encoder=['left_crank','left_hip','right_crank','right_hip']
 sys.path[:0]=[str(I),str(OLD/'payloads_r5/h1/source'),str(OLD/'payloads_r5/h1/source/sm_deps')]
 from own_step_differentiable_objective_v2 import build_own_step_mdp
 refrel=read(OLD/'payloads_r5/h1/job0/TASK.json')['native_reference_relative']
 mdp=build_own_step_mdp(read(GAS/'job0/assets/import_contract.json'),read(geom),read(OLD/'payloads_r5/h1'/refrel),original_c['expected_runtime_joint_names'],encoder,device='cpu',order_scope='actual_SDK_readback')
 expected_objective=mdp.contract_manifest();objSHA=hashlib.sha256(json.dumps(expected_objective,indent=2).encode()).hexdigest()
 known=dict(schema='mod4.native88.known_original_R5_processes.v1',rows=[
  dict(role='owner',execution_backend='target72',pid=509192,creation=1793065834.97),
  dict(role='h1_node',execution_backend='source210',pid=451461,creation=1793065841.9),
  dict(role='h1_worker',execution_backend='source210',pid=451482,creation=1793065842.0),
  dict(role='recovery_node',execution_backend='target72',pid=509210,creation=1793065841.0),
  dict(role='recovery_worker',execution_backend='target72',pid=509232,creation=1793065842.0)],source='actual original R5 receipts; creations replaced below from original node metadata')
 # Do not guess creation times: resolve only already collected original text.
 roots=[OLD/'current_native87R5_closed_text'/key/'NODE_IDENTITY.json' for key in ('h1','recovery')]
 roots.extend(OLD/'reports'/f'{key}_AVAILABLE_TWO_NATIVE87R5_FIRST_PI_IDENTITY_RETURNED_ACTUAL.json' for key in ('H1','RECOVERY'))
 records=[]
 def visit(v):
  if isinstance(v,dict):
   if type(v.get('pid')) is int and type(v.get('creation')) in (int,float):records.append(v)
   for x in v.values():visit(x)
  elif isinstance(v,list):
   for x in v:visit(x)
 # The collected closure embeds node_exit and node_terminal worker receipts.
 visit(closed)
 for p in roots:
  try:visit(read(p))
  except (ValueError,UnicodeError):pass
 for target in known['rows']:
  values={x['creation'] for x in records if x['pid']==target['pid']}
  if target['role']=='owner':values.add(1793065834.97)
  assert len(values)==1,(target['role'],target['pid'],values)
  target['creation']=values.pop()
 specs={};payloads={};sources={};metadata_summary={}
 for key,source in SOURCES.items():
  old=OLD/'payloads_r5'/key;B=N/'payloads'/key;B.mkdir(parents=True)
  oldmf=read(old/'THREE_SLOT_COMPLETE_MANIFEST_V1.json');oldrows={x['relative']:x for x in oldmf['files']};oldc=read(old/'NATIVE87_SOURCE_CONTRACT_ACTUAL.json')
  producer_rows={}
  for r in oldmf['files']:
   p=old/r['relative'];assert p.is_file() and p.stat().st_size==r['bytes'];cp(p,B/r['relative']);producer_rows[r['relative']]=r
  changed_reasons={}
  for rel in ['job0/assets/import_contract.json','job0/runtime/isaac/mod4/import_contract.json','job0/runtime/reports/SOURCE_FREEZE.json',*[f'job0/runtime/isaac/mod4/{x}' for x in ['spring_pressure_training_env.py','spring_pressure_index_runtime.py','spring_pressure_audit_runtime.py','spring_nominal_sdk_readback.py']]]:
   cp(GAS/rel,B/rel);changed_reasons[rel]='reviewed nominal400 gas parameters/source freeze only; physical control/reward/success unchanged'
  cp(old/'job0/assets/robot.usd',B/'job0/assets/source_700N/robot.usd');producer_rows['job0/assets/source_700N/robot.usd']=dict(oldrows['job0/assets/robot.usd'],relative='job0/assets/source_700N/robot.usd')
  cp(GAS/'job0/assets/NOMINAL400_GAS_ONLY_OVERLAY_NOT_ADMITTED.usda',B/'job0/assets/robot.usd');changed_reasons['job0/assets/robot.usd']='new tiny four-opinion layer; unchanged complete authored original asset retained as sublayer'
  for name in ['native_own_fudan88_gas400_training_v2.py','native_wheel_leg_bridge_v4.py','native88_gas400_migration_v1.py','native_finalization_own88_gas400.py','same_architecture_native_continuation_candidate_v1.py','native88_typed_window_reviewer_v1.py','gas400_sdk_admission_candidate_v1.py','gas400_source_patcher_v1.py','own_step_differentiable_geometry_v1.py','own_step_differentiable_objective_v1.py','own_step_differentiable_objective_v2.py']:cp(I/name,B/'source'/name)
  cp(I/'vendor_candidate/supermimic_wheel_leg_v3/learner.py',B/'source/supermimic_wheel_leg_v3/learner.py');changed_reasons['source/supermimic_wheel_leg_v3/learner.py']='same original learner AST except new-window64-world-only policy gate'
  for name in ['h1_native88_changed_plant_worker_v1.py','native88_frozen_RSL_bootstrap_v1.py','native88_protocol_v1.py','native88_closed_source_CPU_v1.py','native88_resource_guard_v1.py','three_slot_common_v1.py','three_slot_finite_node_v1.py']:cp(HERE/name,B/name)
  for name in ['three_slot_common_v1.py','three_slot_finite_node_v1.py']:changed_reasons[name]='exact typed native88 source/worker/resource dispatch; original save/control/fee functions retained'
  for name in ['native88_source_guard_v1.py','target_native88_source_sdk_cpu_v1.py','native88_installed_cpu_helpers_v1.py']:cp(Q/name,B/name)
  cp(geom,B/'source/OWN_STEP_WHEEL_GEOMETRY_FROM_R2_SOURCE.json')
  evidence={
   'source_R5_manifest':old/'THREE_SLOT_COMPLETE_MANIFEST_V1.json','qualified_R5_pair_report':pair,
   'previous_R5_closure':close,'actual_asset_report':A/'ASSET_COMPOSITION_CPU_ACTUAL.json',
   'gas400_parameter_contract':A/'NOMINAL400_PARAMETER_SOURCE_CONTRACT.json',
   'own_step_objective_qualification':qualification}
  for name,path in evidence.items():cp(path,B/f'native88_source_evidence/{name}.json')
  put(B/'native88_source_evidence/known_own_processes.json',known)
  nativefile=f'H1_native_R5_{key}_formal.pt';normalfile=read(old/'job0/TASK.json')['source_filename']
  native=OLD/'current_native87R5_method_fullstate'/key/'formal/native_supermimic_H1_final.pt';assert native.stat().st_size==256224393
  cp(native,B/'job0/source'/nativefile);producer_rows['job0/source/'+nativefile]=dict(relative='job0/source/'+nativefile,bytes=256224393,SHA=source['SHA'])
  task=read(old/'job0/TASK.json');task.update(id='H1_OWN_STEP_GAS400_NATIVE88_'+key,source_SHA=source['SHA'],source_filename=nativefile,bootstrap_source_filename=normalfile,source_progress={k:source[k] for k in ('updates','world_updates','policy_updates')},source_native_contract=__import__('native88_source_guard_v1').R5_NATIVE_CONTRACT if False else dict(state_joints=30,actions=6,obs_dim=86,goal_dim=146,packed_state_dim=127,dynamic_aux_dim=54,static_context_dim=31,fresh4096_policy_only_bootstrap=True,original_physics_and_success_unchanged=True,original_RSL_core_frozen_bootstrap_only=True,not_production_expert_source=True,replay_not_saved_matching_upstream_resume_not_exact_PhysX_replay=True),native87_policy_only=False,new_native_architecture_fresh=False,native_continuation=True,native_continuation_restore_required=True,native88_changed_plant=True,changed_plant700_to_nominal400=True,independent_own_step_objective_admission_passed=True,fresh_environment_resume_scope='native_models_only_fresh400N_environment_no_old_DR',own_step_geometry_SHA=H(geom),objective_contract_SHA=objSHA,actual_target_CPU_or_GPU_readback=False)
  for name in ('native87_contract_SHA','qualified_H1_report_SHA','previous86_closure_SHA'):task.pop(name,None)
  task.update(qualified_R5_pair_report_SHA=H(pair),previous_R5_closure_SHA=H(close),gas400_parameter_source_contract_SHA=H(evidence['gas400_parameter_contract']),actual_gas400_asset_composition_report_SHA=H(evidence['actual_asset_report']),own_step_objective_qualification_SHA=H(qualification))
  protected=dict(oldc['original_runtime_pins']);protected.update({rel:r['SHA'] for rel,r in oldrows.items() if rel.endswith('.py') or rel.startswith('source/supermimic_wheel_leg_v3/')})
  changed={}
  for rel,oldSHA in protected.items():
   newSHA=H(B/rel)
   if newSHA!=oldSHA:
    assert rel in changed_reasons,rel
    changed[rel]=dict(old_SHA=oldSHA,new_SHA=newSHA,reason=changed_reasons[rel])
  approved={p.relative_to(B).as_posix():H(p) for p in B.rglob('*.py')};pins=dict(approved)
  for p in (B/'native88_source_evidence').iterdir():pins[p.relative_to(B).as_posix()]=H(p)
  for rel in [refrel,'source/OWN_STEP_WHEEL_GEOMETRY_FROM_R2_SOURCE.json','OWNER72_CONTROL_DEPENDENCIES_BINDING_ACTUAL.json']:
   if (B/rel).is_file():pins[rel]=H(B/rel)
  c=dict(schema='mod4.native88.changed_plant_objective.native_fullsource.v1',source_SHA=source['SHA'],source_Adamstep=832460,source_bytes=256224393,bootstrap_source_SHA=BOOTSTRAP_SHA,bootstrap_source_bytes=16868635,method_config=METHOD,expected_runtime_joint_names=oldc['expected_runtime_joint_names'],actual_encoder_joint_names=encoder,expected_installed_versions=oldc['expected_installed_versions'],expected_actual_RSL_sources=oldmf['expected_actual_RSL_sources'],expected_actual_SDK_math_SHA=oldmf['expected_actual_SDK_math_SHA'],approved_python=approved,candidate_pins=pins,original_runtime_pins=protected,explicit_changed_original_files=changed,reference_relative=refrel,objective_runtime_contract=expected_objective,previous_R5_private_lock=prior['specs'][key]['private_lock'])
  for name in ['expected_actual_SDK_observation_manager_SHA','expected_actual_SDK_base_articulation_data_SHA','expected_actual_SDK_physx_articulation_data_SHA']:c[name]=oldc[name]
  for name in (*evidence,'known_own_processes'):
   rel=f'native88_source_evidence/{name}.json';c[name+'_relative']=rel;c[name+'_SHA']=H(B/rel)
  c['native_sourceCPU_report_relative']=c['qualified_R5_pair_report_relative'];c['native_sourceCPU_report_SHA']=c['qualified_R5_pair_report_SHA']
  put(B/'NATIVE88_SOURCE_CONTRACT_ACTUAL.json',c);task['native88_contract_SHA']=H(B/'NATIVE88_SOURCE_CONTRACT_ACTUAL.json');put(B/'job0/TASK.json.new88',task)
  # New namespace only: preserve copied old Task and atomically publish the new one.
  cp(B/'job0/TASK.json',B/'native88_source_evidence/OLD_R5_TASK.original_bytes.txt');(B/'job0/TASK.json.new88').replace(B/'job0/TASK.json')
  mf=dict(oldmf,source_SHA=source['SHA'],source_filename=nativefile,source_migration_version='native88_changed400N_own_step_objective_fullstate',original_runtime_and_assets_exact=False,original_base_geometry_physical_V8_and_success_preserved=True,explicit_protected_changes=changed)
  rows=[]
  for p in sorted(B.rglob('*')):
   if not p.is_file():continue
   rel=p.relative_to(B).as_posix()
   if rel=='THREE_SLOT_COMPLETE_MANIFEST_V1.json':continue
   if p.suffix.lower() in ('.pt','.pth','.npz') or rel=='job0/assets/source_700N/robot.usd':
    r=dict(producer_rows[rel]);assert p.stat().st_size==r['bytes']
   else:r=row(p,rel)
   rows.append(r)
  mf['files']=rows;put(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json.new88',mf);(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json.new88').replace(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')
  spec=dict(prior['specs'][key]);spec.update({k:v for k,v in task.items() if k in ['source_SHA','source_filename','bootstrap_source_filename','source_progress','source_native_contract','native_seed','method_config','fresh_environment_resume_scope','changed_plant700_to_nominal400','independent_own_step_objective_admission_passed','native_continuation','native_continuation_restore_required','new_native_architecture_fresh','native88_changed_plant','native87_policy_only']})
  spec.update(candidate_pins=pins,native88_contract_SHA=task['native88_contract_SHA'],manifest_SHA=H(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),previous_runtime_root=prior['roots'][key],production_script='h1_native88_changed_plant_worker_v1.py',closed_source_CPU_script='target_native88_source_sdk_cpu_v1.py',native_seed=source['seed'],previous_exit_kind='qualified_closed_native87R5_method_fullstate')
  for k in ('qualified_R5_pair_report_SHA','previous_R5_closure_SHA','gas400_parameter_source_contract_SHA','actual_gas400_asset_composition_report_SHA','own_step_objective_qualification_SHA','objective_contract_SHA'):spec[k]=task[k]
  for k in ('native87_contract_SHA','qualified_H1_report_SHA','previous86_closure_SHA','preinstalled_CPU_proof_SHA'):spec.pop(k,None)
  validate_spec(spec);specs[key]=spec;payloads[key]=str(B)
  final=read(pair)['models'][key]['final'];sources[key]=dict(path=final['path'],local_path=str(native),bytes=256224393,SHA=source['SHA'])
  metadata_summary[key]=dict(manifest_SHA=spec['manifest_SHA'],native88_contract_SHA=task['native88_contract_SHA'],python_count=len(approved),file_count=len(rows),explicit_protected_changes=changed)
  for p in B.rglob('*.py'):ast.parse(p.read_bytes())
  sys.path[:0]=[str(B),str(B/'source'),str(B/'source/sm_deps')]
  # Real metadata guard, models skipped honestly for local source binding.
  import importlib.util
  sp=importlib.util.spec_from_file_location('new88_guard_'+key,B/'native88_source_guard_v1.py');guard=importlib.util.module_from_spec(sp);sp.loader.exec_module(guard)
  checked=guard.check_payload(B,verify_model_bytes=False);assert checked['model_bytes_verified'] is False
 controllers=N/'controllers';controllers.mkdir()
 for p in HERE.glob('*.py'):
  if p.name.startswith(('native88_','three_slot_common','three_slot_finite_node','single_writer72_','three_slot_finite_owner_NATIVE88')):cp(p,controllers/p.name)
 for name in ('forwarded_original_owner_control_v1.py','mixed84_protocol_v1.py','mixed86_protocol_v1.py','native87_protocol_v1.py','native87_closed_source_CPU_v1.py','three_real_gpu_resource_v1.py'):
  cp(OLD/'payloads_r5/h1'/name,controllers/name)
 q=dict(passed=True,epoch=time.time(),specs=specs,payloads=payloads,roots=ROOTS,sources=sources,controllers_relative='controllers',owner_root=OWNER,owner_script='three_slot_finite_owner_NATIVE88_AVAILABLE_TWO_authority72.py',deferred_experts=['e2'],last_closed_remaining_snapshot=569553.363275528,actual_target_CPU_or_GPU_or_GO=False,source_model_local_decode_or_hash=False,metadata=metadata_summary,resource_boundary_relative='NATIVE88_SELECTED_RESOURCE_BOUNDARY_ACTUAL.json',fresh_resource_boundary_pending=True)
 put(N/'reports/NATIVE88_TWO_PAYLOADS_SOURCE_PREPARED_ACTUAL.json',q)
 print(json.dumps(dict(passed=True,new_payloads=2,no_target_CPU_or_GO=True,python_counts={k:v['python_count'] for k,v in metadata_summary.items()})))
if __name__=='__main__':
 try:main()
 except BaseException:
  put(N/'reports'/('SOURCE_PREPARATION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(original_error=traceback.format_exc(),no_remote_or_GO=True));raise
