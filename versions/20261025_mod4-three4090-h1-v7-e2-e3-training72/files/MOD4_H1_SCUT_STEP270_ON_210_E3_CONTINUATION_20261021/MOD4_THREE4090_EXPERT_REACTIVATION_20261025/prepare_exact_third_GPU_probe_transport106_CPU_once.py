from pathlib import Path
import ast,json,time
S=Path(__file__).resolve().parent;B=S.parent/'H1_STEP270_REWARD_PATH_V1_20261022';(S/'reports').mkdir(exist_ok=True)
old=B/'same_authorized_session_compressed_transport_v105.py';new=B/'same_authorized_session_compressed_transport_v106.py';s=old.read_text('utf8');needle="        'read_three4090_nonidentifying_utilization_for_human_once.py',";assert s.count(needle)==1;s=s.replace(needle,needle+"\n        'read_authorized_third_GPU_and_original_locks_once.py',",1);ast.parse(s)
with new.open('x',encoding='utf8') as f:f.write(s)
with (S/'reports/NEW_THREE_GPU_TASK_LOCAL_READER_ERRORS_AND_TRANSPORT106_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),exact_new_basename='read_authorized_third_GPU_and_original_locks_once.py',original_local_reader_errors=[dict(operation='Broad rg source inventory',error='Output exceeded budget and truncated; narrowed to selected named files afterwards, no training or data mutation'),dict(operation='Get-Content',path='MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021/two50_payloads/e2/e2_world_moving_worker_v1.py',error='Path absent. Actual spec production_script native_admission_worker.py was then read.')],same_session_memory_secret_strict_pin_unchanged=True),f,indent=2)
print(json.dumps(dict(prepared=True,exact_one_new_resource_reader=True)))
