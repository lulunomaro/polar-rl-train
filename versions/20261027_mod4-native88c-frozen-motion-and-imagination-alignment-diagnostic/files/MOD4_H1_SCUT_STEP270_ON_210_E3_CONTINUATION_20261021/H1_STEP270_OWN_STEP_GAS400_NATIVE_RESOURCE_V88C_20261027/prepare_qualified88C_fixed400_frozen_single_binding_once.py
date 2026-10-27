"""New fixed frozen diagnostic input binding; no actor/SDK/model deserialization."""
from pathlib import Path
import ast,hashlib,importlib.util,json,sys,tarfile,time
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
D=L/'native88C_frozen_single_attempt_source_preparation_v1'
S=T/'H1_NATIVE88C_GAS400_FROZEN_SINGLE_DIAGNOSTIC_20261027'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def put(p,x):
 with Path(p).open('x',encoding='utf8') as f:json.dump(x,f,indent=2,allow_nan=False)
def main():
 assert not S.exists(),'new unused namespace; no replay'
 index=D/'INDEX_SHA256_ACTUAL.json';assert H(index)=='7e31c5269371741bbe058bad907fa03f43c373eac05319c992e72e9c5db7c68d'
 for row in read(index)['files']:
  p=D/row['relative'];assert p.stat().st_size==row['bytes'] and H(p)==row['SHA']
 sys.path.insert(0,str(D))
 from native88C_frozen_acceptance_contract_v1 import select_source,validate_eval_binding,PURPOSE,SCOPE,FINAL_SHA,FINAL_BYTES
 from native88C_own_pid_out_guard_v1 import records_from_evidence
 paths=dict(cpu=R/'NATIVE88C_READER_REPAIRED_TYPED_FINALS_AND_ORIGINAL_COST_CPU_ACTUAL.json',collection=R/'NATIVE88C_CASE_SAFE_COMPLETE_FINALS_AND_ORIGINAL_COST_RETURNED_V2_ACTUAL.json',detached=R/'NATIVE88C_ACTUAL_OWNER_NODES_DETACHED.json',first_identity=R/'NATIVE88_FIRST_NEW_POLICY_FINITE_RETURNED_ACTUAL.json',events_summary=R/'CURRENT_CLOSED88C_ACTUAL_RESULTS_READER_REPAIR_AND_NEXT_DIAGNOSTIC_WORK_ORDER.json')
 values={k:read(p) for k,p in paths.items()};selected=select_source(values['cpu'],values['collection'],values['events_summary']['models'])
 prepared=read(R/'NATIVE88_TWO_PAYLOADS_SOURCE_PREPARED_ACTUAL.json');B=Path(prepared['payloads']['h1'])
 mf=B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json';assert H(mf)==values['detached']['specs']['h1']['manifest_SHA']
 manifest=read(mf);runtime=[r for r in manifest['files'] if Path(r['relative']).suffix.lower() not in ('.pt','.pth','.npz')]
 assert len({r['relative'] for r in runtime})==len(runtime)
 final=selected['source']['final'];assert final['SHA']==FINAL_SHA and final['bytes']==FINAL_BYTES
 producer=final['producer'];objective=N/'current_native88_closed_text/h1/job0/production/NATIVE_OWN_REFERENCE_OBJECTIVE_CONTRACT_ACTUAL.json'
 assert H(objective)==producer['runtime_objective_contract_SHA']
 paths['objective']=objective
 tree=ast.parse((B/'source/native88_gas400_migration_v1.py').read_bytes());node=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='NATIVE_CONTRACT' for t in n.targets));ns={};exec(compile(ast.Module(body=[node],type_ignores=[]),'exact_output_contract','exec'),ns)
 root='/home/lc01/Zonglin Li/zonglin2/tasks/H1native88C_gas400_fixed_single_diagnostic_20261027'
 code_names=read(D/'BINDING_INTERFACE_SOURCE_ONLY.json')['copy_only_eval_code'];codes={name:H(D/name) for name in code_names}
 task=read(B/'job0/TASK.json');q=dict(purpose=PURPOSE,selected_key='h1',selection_scope=SCOPE,seeds=[20260928],episodes_per_seed=1,max_controls=500,max_physics_callbacks=2000,source_model=final,source_run_id=values['collection']['run_id'],source_qualification=dict(formal_FINAL_passed=True,initial_whole_CPU_passed=True,original_fee_allout_passed=True),native_parent_source=producer['initial_native_source'],native_output_contract=ns['NATIVE_CONTRACT'],objective_contract=read(objective),objective_contract_SHA=producer['runtime_objective_contract_SHA'],gas400_parameter_source_contract_SHA=producer['gas400_parameter_source_contract_SHA'],actual_gas400_asset_composition_report_SHA=producer['actual_gas400_asset_composition_report_SHA'],eval_root=root,runtime_root=root+'/runtime',qualified_training_roots=values['detached']['roots'],model_eval_relative='qualified_model/native_supermimic_H1_final.pt',runtime_files=runtime,runtime_source_contract=read(B/'NATIVE88_SOURCE_CONTRACT_ACTUAL.json'),eval_code_pins=codes,reference_relative=task['native_reference_relative'],reference_SHA=producer['reference_artifact_SHA'],own_geometry_relative='source/OWN_STEP_WHEEL_GEOMETRY_FROM_R2_SOURCE.json',own_geometry_SHA=producer['own_step_geometry_SHA'],GPU_UUID='GPU-c27eecbd-6838-7290-1cd2-37e34522213d',execution_backend='target72',original_owner_locks=values['collection']['authority72']['original_locks'],known_qualified_own_processes=records_from_evidence(values),selected_GPU_original_locks=[x['path'] for x in values['collection']['nodes']['recovery']['locks']],action_mode='deterministic_native_mean_no_collection_noise',new_N1_fresh_episode_no_training_environment_restore=True,runtime_is_new_readonly_copy=True,optional_WM_forward_enabled=False,hardware_scope='QUALIFIED88C_NOMINAL400_OWN_WHEEL_V2_FIXED_SINGLE_DIAGNOSTIC',source_runtime_original_local=str(B),source_runtime_original_manifest_SHA=H(mf),actual_closed_balance=values['cpu']['original_fees']['remaining_actual_snapshot'],source_objective_readonly_no_new_reward=True)
 q['evidence_pins']={k:dict(eval_relative='evidence/'+k+'.json',SHA=H(p)) for k,p in paths.items()}
 validate_eval_binding(q)
 S.mkdir();(S/'reports').mkdir();(S/'code').mkdir()
 put(S/'BINDING.json',q)
 files=[]
 def add(p,rel,digest,size=None):
  p=Path(p);assert p.is_file() and not p.is_symlink()
  if size is not None:assert p.stat().st_size==size
  if p.suffix.lower() not in ('.pt','.pth'):assert H(p)==digest
  files.append(dict(local=str(p),relative=rel,bytes=p.stat().st_size,SHA=digest))
 add(S/'BINDING.json','BINDING.json',H(S/'BINDING.json'))
 for name,digest in codes.items():
  dest=S/'code'/name;dest.write_bytes((D/name).read_bytes());add(dest,'code/'+name,digest)
 for key,p in paths.items():add(p,q['evidence_pins'][key]['eval_relative'],q['evidence_pins'][key]['SHA'])
 for row in runtime:add(B/row['relative'],'runtime/'+row['relative'],row['SHA'],row['bytes'])
 # A new-purpose copy of exactly the qualified FINAL; no local rehash or deserialization.
 add(final['local_path'],q['model_eval_relative'],final['SHA'],final['bytes'])
 assert len({r['relative'] for r in files})==len(files)
 archive_path=S/'SOURCE_CODE_EVIDENCE_INPUTS_NO_MODELS.tar'
 with tarfile.open(archive_path,'x') as tar:
  for row in files:
   if row['relative']!=q['model_eval_relative']:tar.add(row['local'],arcname=row['relative'],recursive=False)
 archive=dict(path=str(archive_path),bytes=archive_path.stat().st_size,SHA=H(archive_path))
 put(S/'INPUT_TRANSFER_INDEX.json',dict(epoch=time.time(),files=files,archive=archive,model_transfer_separate=True,model_local_fullhash_not_repeated=True,no_model_deserialization=True))
 put(S/'reports/SOURCE_BOUND_FIXED_SINGLE_NOT_EXECUTED_ACTUAL.json',dict(epoch=time.time(),passed=True,source=final,helper_index_SHA=H(index),case=q['seeds'],runtime_files=len(runtime),runtime_bytes=sum(r['bytes'] for r in runtime),archive=archive,fresh_target_SDK_resource_account_and_N1_reset_before_actor_still_required=True,no_actor_GPU_physics_or_remote_run=True))
 print(json.dumps(dict(prepared=True,root=str(S),code_archive_bytes=archive['bytes'],separate_model_bytes=final['bytes'],case_count=1,no_GPU_or_actor=True)))
if __name__=='__main__':main()
