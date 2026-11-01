from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;V=N.parent/'NEW272_FUTURE_SAFE_WM_CUDA_ADMISSION_V274V2_20261101'
old=json.loads((N/'reports/ROOT274_NEW272_ACTUAL_H32_CUDA_OR_ORIGINAL_ERROR_RETURNED.json').read_bytes())
assert old['passed'] is False and old['result'] is None and old['wait']['all_own_children_waited']
assert not old['wait']['private_shared_EX_acquired'] and old['wait']['all_owned_locks_released']
assert 'FileNotFoundError' in old['original_parent_stdout'] and 'mod4_single_canonical_authority_20261026/three_expert_v2_' in old['original_parent_stdout']
V.mkdir(exist_ok=False);files=[]
for name in ('worker274_new272_H32_CUDA_no_optimizer_once.py','prepare274_frozen_new272_CUDA_admission_source_once.py','parent274_new272_model_only_once.py','run_ROOT274_new272_CUDA_admission_once.py'):
 b=(N/name).read_bytes()
 if name=='parent274_new272_model_only_once.py':
  a="canonical.parent/('three_expert_v2_'+T['GPU_UUID']+'.lock')";c="canonical.parent.parent/('three_expert_v2_'+T['GPU_UUID']+'.lock')"
  assert b.count(a.encode())==1;b=b.replace(a.encode(),c.encode())
 if name=='run_ROOT274_new272_CUDA_admission_once.py':
  a='MOD4_NEW272_FUTURE_SAFE_WM274_ADMISSION_20261101';c='MOD4_NEW272_FUTURE_SAFE_WM274V2_ADMISSION_20261101'
  assert b.count(a.encode())==1;b=b.replace(a.encode(),c.encode())
 ast.parse(b,filename=name);(V/name).write_bytes(b);files.append(dict(path=str(V/name),bytes=len(b),SHA=hashlib.sha256(b).hexdigest()))
with(V/'BEFORE_USE274V2_ONLY_LOCK_PATH_AND_NEW_NAMESPACE.json').open('x',encoding='utf8')as f:
 json.dump(dict(epoch=time.time(),original_false_path=str(N/'reports/ROOT274_NEW272_ACTUAL_H32_CUDA_OR_ORIGINAL_ERROR_RETURNED.json'),original_worker_started=False,original_raw_model_GPU_reads=0,raw_first_use_not_consumed=True,worker_unchanged=True,parent_fix='private lock is in state, not canonical subdirectory; matches actual272 original path',new_namespace=True,files=files),f,indent=2)
print(json.dumps(dict(passed=True,path=str(V))))
