"""Use actual89C fullstate witness plus actual worker-onlyV4 LR migration."""
from pathlib import Path
import ast,hashlib,json,shutil,time
HERE=Path(__file__).resolve().parent;OLD=HERE.parent
NEW_WORKER='87748712b51a0b36c2ec609cd56773471ac8b41ba60d35b21884403423462d19'
BASE_WORKER='1858c6395083bb7104385ec82d3dce6db4f79898a6346a250916ad7217524152'
BASE_CPU='d06aa8550f915258b0b42a711d73b9859f5fbce68fbcea6289b8647cd0f4208c'
EXT='5509f4a793be9d9e5e858bc75bfa326440267f1caeff040979935b2bed6f3c8e'
NAME='E0_PPO50_gas400_finite_worker_v4_preserved_LR_scalar.py'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rows(paths):return [dict(path=str(p),bytes=p.stat().st_size,SHA=H(p)) for p in paths]
def main():
 frozen=OLD/'E0_CONTROLLER_V1_PRE_LR_FROZEN_INDEX.json';assert not frozen.exists()
 files=sorted(p for p in OLD.iterdir() if p.is_file())
 frozen.write_text(json.dumps(dict(epoch=time.time(),frozen=True,files=rows(files),
  source_controller_and_fixtures_V1_preserved=True,actual_GO=False,LR_V3_semantic_gap_rejected_before_deployment=True,
  reader_errors=[dict(tool_chunk='3d77f0',error='rg received PowerShell -ErrorAction as grep flag; unknown encoding rrorAction, metadata search only'),dict(tool_chunk='398d85',error='Synthetic Popen spy lacked STDOUT; before real spawn'),dict(tool_chunk='21bbc5',error='Synthetic fake path lacked __str__; fixture argv mismatch only')],
  Git_status='ordinary_supplement_existing89trial_no_new_tag'),indent=2),encoding='utf8')
 names=['E0_single72_finite_owner_authority72_v1.py','E0_single72_finite_node_v1.py','three_slot_common_v1.py',
  'single_writer72_authority_V85M_source.py','E0_single72_resource_guard_v1.py','E0_single72_bound_cfg_v1.py','E0_single72_detached_launcher_v1.py']
 for name in names:assert not (HERE/name).exists();shutil.copy2(OLD/name,HERE/name)
 protocol=(OLD/'E0_single72_protocol_v1.py').read_text('utf8')
 protocol=protocol.replace("WORKER='"+BASE_WORKER+"'","WORKER='"+NEW_WORKER+"'\nBASE_WORKER='"+BASE_WORKER+"'")
 protocol=protocol.replace("CPU='"+BASE_CPU+"'","CPU='"+EXT+"'\nBASE_CPU='"+BASE_CPU+"'")
 protocol=protocol.replace('E0_PPO50_gas400_finite_worker_v1.py',NAME)
 protocol=protocol.replace('def validate_cpu_value(v):','def validate_base_cpu_value(v):')
 protocol=protocol.replace("v.get('worker_SHA')==WORKER,'actual89C CPU result'","v.get('worker_SHA')==BASE_WORKER,'actual89C CPU result'")
 protocol+='''
# Typed additive worker-only source migration. Base modelCPU witness stays V3.
EXTENSION_NAME='E0_V4_WORKER_ONLY_LR_SOURCE_MIGRATION_ACTUAL.json'
def validate_cpu_value(v):
 require(v.get('passed') is True and v.get('kind')==KIND and v.get('source_SHA')==SOURCE,'actual source-only migration result')
 require(v.get('base_actual_fullstate_CPU_SHA')==BASE_CPU and v.get('base_worker_SHA')==BASE_WORKER and v.get('target_worker_SHA')==WORKER,'baseCPU and exactV4 worker source')
 require(v.get('target_worker_filename')=='E0_PPO50_gas400_finite_worker_v4_preserved_LR_scalar.py' and v.get('original_optimizer_LR_and_required_constructor_scalar')==.00038443359375000017,'only originalLR constructor literal migration')
 require(v.get('exact_single_CLI_literal_change') is True and v.get('no_model_reload') is True and v.get('no_new_fullstate_CPU_load_claim') is True and v.get('actual_CUDA_fullrestore_pending') is True,'honest extension scope')
 base=v.get('base_actual_fullstate_CPU_value') or {};validate_base_cpu_value(base)
 require(digest(base)==BASE_CPU and v.get('base_actual_fullstate_CPU_path')==JOB+'/E0_SOURCE_SDK_CPU_ADMISSION_ACTUAL_V2.json','original entire baseCPU unchanged')
 return True
def load_E0_preinstalled_CPU(spec,B):
 validate_spec(spec);B=Path(B)
 base_path=Path(JOB)/'E0_SOURCE_SDK_CPU_ADMISSION_ACTUAL_V2.json';require(H(base_path)==BASE_CPU,'actual89C fullstate witness unchanged')
 original=json.loads(base_path.read_bytes());validate_base_cpu_value(original)
 path=Path(JOB)/EXTENSION_NAME;require(H(path)==CPU==spec['source_CPU_SHA'],'actual233 worker-only migration byteSHA')
 value=json.loads(path.read_bytes());validate_cpu_value(value);require(value['base_actual_fullstate_CPU_value']==original,'embedded base is original89C')
 proof=B/'E0_ACTUAL89C_CPU_RETURNED_PROOF.json';require(H(proof)==spec['CPU_returned_proof_SHA'],'actual89C returned witness pin')
 v=json.loads(proof.read_bytes());require(v.get('actual_finite_returned') is True and v.get('actual_source_SDK_CPU_passed') is True and v.get('source_CPU_SHA')==BASE_CPU and v.get('worker_V3_SHA')==BASE_WORKER and v.get('root')==JOB,'actual89C return, distinct from worker-only migration')
 return dict(value=value,path=str(path),SHA=CPU,actual_CPU_waited_EXIT0=True,base_actual_CPU_waited_EXIT0=True,
  original_returned_proof_SHA=H(proof),scope='actual89C fullstate CPU plus actual233 worker-only source migration; no new modelCPU load',no_model_reload=True)
'''
 (HERE/'E0_single72_protocol_v1.py').write_bytes(protocol.encode())
 # Everything that owns account, locks, node loops and spawning remains exact.
 for name in names:assert H(HERE/name)==H(OLD/name)
 for p in HERE.glob('*.py'):ast.parse(p.read_bytes())
 proof=dict(epoch=time.time(),V1_frozen_index=dict(path=str(frozen),SHA=H(frozen)),
  changed_only='typed protocol baseCPU+worker-only extension constants/validation/new dispatch basename; bound_cfg imports those constants',
  owner_common_node_authority_resourceguard_boundcfg_launcher_all_bytes_exact=names,
  charge_values_account_lock_loop_caps_save_exit_unchanged=True,base_fullstate_CPU_SHA=BASE_CPU,actual_worker_only_extension_SHA=EXT,
  target_worker_SHA=NEW_WORKER,target_worker_filename=NAME,no_PT_GPU_SDK_remote_or_ledger_IO=True,
  files=rows(sorted(HERE.glob('*.py'))),Git_status='ordinary_supplement_existing89trial_no_new_tag')
 (HERE/'E0_CONTROLLER_V2_LR_DERIVATION_SOURCE_ACTUAL.json').write_text(json.dumps(proof,indent=2),encoding='utf8')
 print(json.dumps(dict(V2=str(HERE),baseCPU=BASE_CPU,extension=EXT,worker=NEW_WORKER,unchanged_controller_files=len(names))))
if __name__=='__main__':main()
