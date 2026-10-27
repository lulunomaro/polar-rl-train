"""Freeze only small source/reports; binary/model SHA values reuse producer receipts."""
from pathlib import Path
import hashlib,json,time
HERE=Path(__file__).resolve().parent
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(name,value):
 p=HERE/name
 with p.open('x',encoding='utf8') as f:json.dump(value,f,ensure_ascii=False,indent=2)
 return dict(path=str(p),bytes=p.stat().st_size,SHA=H(p))
def main():
 assert not (HERE/'W35_FROZEN_MINIMUM_SOURCE_ADMISSION_INDEX_V1.json').exists()
 prepared=json.loads((HERE/'W35_RUNTIME_AND_WORKER_SOURCE_CPU_PREPARED_V1.json').read_bytes())
 fixture=json.loads((HERE/'W35_SOURCE_ONLY_CPU_FIXTURE_ACTUAL_V1.json').read_bytes());assert fixture['passed'] is True
 runtime=HERE/'runtime_candidate_v1';small=[]
 for p in sorted(runtime.rglob('*')):
  if p.is_file():small.append(dict(local_path=str(p),installed_relative='runtime/'+p.relative_to(runtime).as_posix(),bytes=p.stat().st_size,SHA=H(p)))
 for name,target in [('W35_PPO50_gas400_finite_worker_v1.py','W35_PPO50_gas400_finite_worker_v1.py'),
  ('W35_target_source_SDK_CPU_admission_v1.py','W35_target_source_SDK_CPU_admission_v1.py'),
  ('W35_original_run_manifest_frozen_v1.json','original_run_manifest.json')]:
  p=HERE/name;small.append(dict(local_path=str(p),installed_relative=target,bytes=p.stat().st_size,SHA=H(p)))
 model=dict(prepared['source_model_existing_metadata'],installed_relative='source/W35_N20K_PPO50_GAS400_SOURCE_NOT_GPU_ADMITTED.pt',SHA_reused_not_rehashed=True)
 deps=prepared['binary_dependencies']
 manifest=put('W35_COMPLETE_INSTALL_MANIFEST_V1.json',dict(schema='mod4.W35.PPO50gas400.source_install_manifest.v1',epoch=time.time(),
  status='SOURCE_FROZEN_NOT_TARGET_CPU_OR_GPU_ADMITTED',role='W35',small_source_files=small,model=model,binary_dependencies=deps,
  expected_source_qualification_kind='MOD4_W35_PPO50_GAS400_FULLSTATE_SOURCE_CPU_V1',
  target_admission_report='W35_SOURCE_SDK_CPU_ADMISSION_ACTUAL_V1.json',
  dependency_install_receipt_required=dict(filename='W35_INSTALLED_BINARY_DEPENDENCIES_VERIFIED.json',
   actual_postcopy_fullSHA_verified=True,job_root='EXACT_RESOLVED_NEW_REMOTE_JOB_ROOT',
   files=[dict(relative=r['installed_relative'],bytes=r['bytes'],SHA=r['SHA']) for r in deps],
   meaning='Schema only. Root creates actual receipt only after one actual source copy and actual postcopy fullSHA verification; this object is not that receipt.'),
  original_model_core_STD_17Adam_LR_D1_D7_command_and_G3_state_unchanged=True,constructor_optimizer_LR=.00001,
  source_producer_SHA='a35915e0f25cd5ba25a010eba6125d0ffd74c0be605ae57debd0d5cbb33bfec0',
  source_producer_report=str(HERE.parent/'night_frozen_experts_PPO50_gas400_adaptation_20261027/reports/ORIGINAL_N20K_PPO50_GAS400_SOURCE_CPU_ACTUAL_V1.json'),
  no_model_binary_or_NPZ_read_for_this_manifest=True,no_remote_GPU_GO_or_ledger_operation=True))
 # Index excludes itself and includes every immutable file/error/source under this folder.
 rows=[dict(relative=p.relative_to(HERE).as_posix(),bytes=p.stat().st_size,SHA=H(p)) for p in sorted(HERE.rglob('*')) if p.is_file()]
 value=dict(schema='mod4.W35.PPO50gas400.frozen_minimum_admission_index.v1',epoch=time.time(),status='FROZEN_SOURCE_ONLY',
  files=rows,file_count=len(rows),complete_install_manifest=manifest,model_and_binary_originals_retained_index_only=True,
  source_only_CPU_fixture=dict(path=str(HERE/'W35_SOURCE_ONLY_CPU_FIXTURE_ACTUAL_V1.json'),SHA=H(HERE/'W35_SOURCE_ONLY_CPU_FIXTURE_ACTUAL_V1.json'),passed=True),
  actual_target_CPU_SDK_pending=True,actual_CUDA_fullrestore_native24_and_first_PPO_pending=True,
  original_frozen_W35_label_unchanged=True,new_branch_skill_qualified=False,WM_transition_collection_executed=False,
  no_remote_lease_or_GPU_task_held=True,Git_status='ordinary_supplement_existing89trial_pending_root',
  frozen_bytes_must_not_be_edited=True,next_change_requires_new_additive_namespace=True)
 result=put('W35_FROZEN_MINIMUM_SOURCE_ADMISSION_INDEX_V1.json',value)
 print(json.dumps(dict(frozen_index=result,install_manifest=manifest,file_count=len(rows),small_install_files=len(small),binary_dependencies=len(deps),no_model_or_binary_read=True)))
if __name__=='__main__':main()
