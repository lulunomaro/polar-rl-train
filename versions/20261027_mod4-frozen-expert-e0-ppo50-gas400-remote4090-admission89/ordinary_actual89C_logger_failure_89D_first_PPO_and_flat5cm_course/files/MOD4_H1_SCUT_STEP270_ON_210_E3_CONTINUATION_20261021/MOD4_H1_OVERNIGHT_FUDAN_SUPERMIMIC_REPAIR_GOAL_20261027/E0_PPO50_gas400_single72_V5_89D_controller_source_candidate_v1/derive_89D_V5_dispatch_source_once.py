"""New89D source only; previous89C failed run is cost evidence, never model source."""
from pathlib import Path
import ast,hashlib,json,shutil,time
HERE=Path(__file__).resolve().parent
OLD=HERE.parent/'E0_PPO50_gas400_single72_controller_source_preparation_v1/V2_LR'
BASE_JOB='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E0_PPO50_GAS400_2610v89c/e0'
JOB='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E0_PPO50_GAS400_2610v89d/e0'
V4='87748712b51a0b36c2ec609cd56773471ac8b41ba60d35b21884403423462d19'
V5='ec8eba0365f0129b2799ef4e1ae7f3673beb585f87d4e25d2c36cf7bdb33b08c'
COST='e90bda2d34777c60661880f9aa390bd6974437e21a4a9adfade71b933d096ef1'
NAME='E0_PPO50_gas400_finite_worker_v5_writer_before_presave.py'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def segment(s,name):
 tree=ast.parse(s);node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name)
 return ast.get_source_segment(s,node)
def main():
 copied=['three_slot_common_v1.py','single_writer72_authority_V85M_source.py','E0_single72_finite_owner_authority72_v1.py',
  'E0_single72_finite_node_v1.py','E0_single72_resource_guard_v1.py','E0_single72_detached_launcher_v1.py','E0_first_metadata_observer_readonly_v1.py','E0_ACTUAL89C_CPU_RETURNED_PROOF.json']
 for name in copied:assert not (HERE/name).exists();shutil.copy2(OLD/name,HERE/name);assert H(HERE/name)==H(OLD/name)
 source=(OLD/'E0_single72_protocol_v1.py').read_text('utf8')
 source=source.replace("JOB='"+BASE_JOB+"'","JOB='"+JOB+"'\nBASE_JOB='"+BASE_JOB+"'")
 source=source.replace("WORKER='"+V4+"'","WORKER='"+V5+"'\nBASE_V4_WORKER='"+V4+"'")
 spec=segment(source,'validate_spec');fixed=spec.replace("s.get('source_CPU_SHA')==CPU","valid_source_extension_sha(s.get('source_CPU_SHA'))").replace('E0_PPO50_gas400_finite_worker_v4_preserved_LR_scalar.py',NAME)
 assert fixed!=spec;source=source.replace(spec,fixed)
 payload=segment(source,'validate_payload');fixed=payload.replace("manifest['source_CPU_SHA']==CPU","manifest['source_CPU_SHA']==spec['source_CPU_SHA']").replace("task['source_CPU_SHA']==CPU","task['source_CPU_SHA']==spec['source_CPU_SHA']")
 source=source.replace(payload,fixed)
 oldvalidator=segment(source,'validate_cpu_value');newvalidator=oldvalidator.replace('def validate_cpu_value(v):','def validate_V4_base_source_migration(v):').replace("v.get('target_worker_SHA')==WORKER","v.get('target_worker_SHA')==BASE_V4_WORKER").replace("==JOB+'/E0_SOURCE_SDK_CPU_ADMISSION_ACTUAL_V2.json'","==BASE_JOB+'/E0_SOURCE_SDK_CPU_ADMISSION_ACTUAL_V2.json'")
 source=source.replace(oldvalidator,newvalidator)
 source+='''
# New89D exact source-only V5 repair, original54f remains the model source.
FAILED89C_ENDING_SHA='e90bda2d34777c60661880f9aa390bd6974437e21a4a9adfade71b933d096ef1'
V5_EXTENSION_NAME='E0_V5_WRITER_PRESAVE_SOURCE_MIGRATION_ACTUAL.json'
def valid_source_extension_sha(v):return isinstance(v,str) and len(v)==64 and all(x in '0123456789abcdef' for x in v)
def validate_cpu_value(v):
 require(v.get('passed') is True and v.get('kind')==KIND and v.get('source_SHA')==SOURCE,'actual V5 source-only extension, model still54f')
 require(v.get('base_actual_fullstate_CPU_SHA')==BASE_CPU and v.get('base_worker_SHA')==BASE_V4_WORKER and v.get('target_worker_SHA')==WORKER,'original fullstate/baseV4/targetV5 source binding')
 require(v.get('target_worker_filename')=='E0_PPO50_gas400_finite_worker_v5_writer_before_presave.py' and v.get('exact_existing_writer_assignment_move') is True,'only existing writer assignment moved before save')
 require(v.get('no_model_reload') is True and v.get('no_new_fullstate_CPU_load_claim') is True and v.get('actual_CUDA_fullrestore_pending') is True,'actual new runtime restore still required')
 require(v.get('new_job_root')==JOB and v.get('failed89C_resource_cost_only') is True and v.get('failed89C_original_ending_SHA')==FAILED89C_ENDING_SHA,'new unused89D, failed89C never a model source')
 base=v.get('base_actual_fullstate_CPU_value') or {};validate_base_cpu_value(base)
 require(digest(base)==BASE_CPU and v.get('base_actual_fullstate_CPU_path')==BASE_JOB+'/E0_SOURCE_SDK_CPU_ADMISSION_ACTUAL_V2.json','complete original89C modelCPU witness unchanged')
 previous=v.get('base_V4_worker_only_LR_source_migration_value') or {};validate_V4_base_source_migration(previous)
 require(v.get('base_V4_worker_only_LR_source_migration_SHA')==CPU and digest(previous)==CPU,'actual233 CLI LR migration unchanged')
 require(v.get('base_V4_worker_only_LR_source_migration_path')==BASE_JOB+'/E0_V4_WORKER_ONLY_LR_SOURCE_MIGRATION_ACTUAL.json','exact original V4 migration path')
 return True
def E0_valid_ready(row,spec):
 try:
  validate_spec(spec);e=row.get('closed_source_CPU') or {};v=e.get('value') or {};validate_cpu_value(v)
  require(row.get('key')==KEY and row.get('phase')=='ready' and row.get('manifest_SHA')==spec['manifest_SHA'] and not row.get('original_error'),'ready identity')
  require(row.get('actual_validation_fcntl_held') is True and e.get('actual_CPU_waited_EXIT0') is True and e.get('SHA')==spec['source_CPU_SHA']==digest(v),'actual baseCPU+source-only extension and lock')
  return True
 except (ValueError,KeyError,TypeError):return False
def load_E0_preinstalled_CPU(spec,B):
 validate_spec(spec);B=Path(B)
 path=Path(JOB)/V5_EXTENSION_NAME;require(H(path)==spec['source_CPU_SHA'],'actual published89D V5 source-only extension SHA')
 value=json.loads(path.read_bytes());validate_cpu_value(value)
 base=Path(BASE_JOB)/'E0_SOURCE_SDK_CPU_ADMISSION_ACTUAL_V2.json';require(H(base)==BASE_CPU and json.loads(base.read_bytes())==value['base_actual_fullstate_CPU_value'],'original89C fullstateCPU never rewritten')
 lr=Path(BASE_JOB)/'E0_V4_WORKER_ONLY_LR_SOURCE_MIGRATION_ACTUAL.json';require(H(lr)==CPU and json.loads(lr.read_bytes())==value['base_V4_worker_only_LR_source_migration_value'],'actualV4 LR extension untouched')
 returned=B/'E0_ACTUAL89C_CPU_RETURNED_PROOF.json';require(H(returned)==spec['CPU_returned_proof_SHA'],'original89C CPU return pin')
 witness=json.loads(returned.read_bytes());require(witness.get('actual_finite_returned') is True and witness.get('source_CPU_SHA')==BASE_CPU and witness.get('worker_V3_SHA')==BASE_WORKER and witness.get('root')==BASE_JOB,'base CPU actual return')
 close=B/'E0_89C_RESOURCE_COST_SETTLED_ACTUAL.json';require(H(close)==FAILED89C_ENDING_SHA,'actual failed89C resource/cost proof')
 ending=json.loads(close.read_bytes());require(ending.get('actual_early_error_ending_returned') is True and ending.get('original_error_not_skill_result') is True and ending.get('canonical_None') is True and ending.get('all_original_locks_free') is True,'actual89C settled/allout prerequisite')
 require(ending.get('original_fee_seconds')==397.61036682128906 and ending.get('closed_remaining_snapshot')==561777.961785078,'original full fee, no refund or new model')
 return dict(value=value,path=str(path),SHA=spec['source_CPU_SHA'],actual_CPU_waited_EXIT0=True,base_actual_CPU_waited_EXIT0=True,
  scope='original actual89C fullstateCPU + actualV4 LR + new V5 source-only move; no new modelCPU load',no_model_reload=True,failed_previous_scope='resource_cost_only')
'''
 (HERE/'E0_single72_protocol_v1.py').write_bytes(source.encode());ast.parse(source)
 cfg=(OLD/'E0_single72_bound_cfg_v1.py').read_text('utf8')
 cfg=cfg.replace('source_CPU_SHA=CPU,',"source_CPU_SHA=request['source_CPU_SHA'],").replace('E0_PPO50_gas400_finite_worker_v4_preserved_LR_scalar.py',NAME)
 (HERE/'E0_single72_bound_cfg_v1.py').write_bytes(cfg.encode());ast.parse(cfg)
 report=dict(epoch=time.time(),new_unused_job=JOB,source_only_candidate=True,source_extension_SHA_bound_from_request_not_guessed=True,
  target_worker_SHA=V5,target_worker_filename=NAME,model_source_54f_unchanged=True,failed89C_cost_proof_SHA=COST,
  common_owner_node_authority_resource_launcher_and_observer_entire_bytes_unchanged=copied,
  no_PT_GPU_SDK_remote_or_ledger_IO=True,Git_status='ordinary_supplement_existing89trial')
 (HERE/'E0_89D_V5_CONTROLLER_CANDIDATE_SOURCE_DERIVATION_ACTUAL.json').write_text(json.dumps(report,indent=2),encoding='utf8')
 print(json.dumps(report))
if __name__=='__main__':main()
