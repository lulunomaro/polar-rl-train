"""Reuse captured actual SDK compute source locally; no new host read or model inference."""
from pathlib import Path
import hashlib,importlib.util,json,time,traceback
import torch
S=Path(__file__).resolve().parent;T=S.parent;C=S/'candidate_v4';R=S/'reports'
def put(path,value):
 with Path(path).open('x',encoding='utf8') as f:json.dump(value,f,ensure_ascii=False,indent=2)
try:
 torch.set_num_threads(2)
 sdk=T/'H1_STEP270_POST67_TIMING_REPAIR_PREPARATION_20261025/reports/ACTUAL_CURRENT_INSTALLED_REWARD_MANAGER_SOURCE.py'
 digest=hashlib.sha256(sdk.read_bytes()).hexdigest();assert digest=='6be44a98df5aed8a0ebac2913ebea33010633e007e816697a6d99f7ccfd731db'
 old=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V74B_20261026/payloads/h1'
 current=json.loads((T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V74B_20261026/reports/H1_FULL_INSTALLED_SOURCE_SDK_RSL_CPU_ACTUAL.json').read_bytes())
 assert current['passed_CPU_only'] and current['new_reward_integration_CPU']['SDK_compute_source_SHA']==digest
 spec=importlib.util.spec_from_file_location('V8_saved_actual_SDK_reward_checker',C/'step270_reward_installed_CPU_v1.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 result=m.check(C,sdk_reward_path=sdk,reference_path=old/'reference_sources/V5_h1_step270_path_reward_v1.py')
 assert result['actual_installed_sampled_excess_SDK_compute_tested'] and result['sampled_excess_SDK']['passed'] and not torch.cuda.is_initialized()
 receipt=dict(epoch=time.time(),passed_local_CPU_with_saved_actual_installed_SDK_source=True,
  captured_actual_SDK_source_path=str(sdk),actual_SDK_source_SHA=digest,
  same_source_SHA_confirmed_by_existing_current74b_installed_CPU_receipt=True,
  result=result,new_V8_not_installed_or_GPU_executed=True,
  fresh_next_payload_target_SDK_fullsource_CPU_and_resource_admission_still_required=True,
  not_new_remote_admission_or_learning_success=True,no_policy_model_PPO_PhysX_GPU_remote_or_budget_action=True)
 put(R/'V8_SAVED_ACTUAL_SDK_COMPUTE_LOCAL_CPU_ACTUAL.json',receipt)
 print(json.dumps(dict(local_saved_actual_SDK_compute_passed=True,source_SHA=digest,new_V8_target_install_and_learning_still_pending=True)))
except BaseException:
 put(R/('V8_SAVED_SDK_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),no_repeat_same_once_or_training_action=True));raise
