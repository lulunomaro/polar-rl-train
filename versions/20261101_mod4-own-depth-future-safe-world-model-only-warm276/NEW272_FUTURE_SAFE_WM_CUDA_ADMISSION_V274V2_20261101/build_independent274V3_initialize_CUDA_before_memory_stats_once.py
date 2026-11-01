from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;V=N.parent/'NEW272_FUTURE_SAFE_WM_CUDA_ADMISSION_V274V3_20261101'
j=json.loads((N/'reports/ROOT274_NEW272_ACTUAL_H32_CUDA_OR_ORIGINAL_ERROR_RETURNED.json').read_bytes())
assert j['passed'] is False and j['result'] is None and j['wait']['all_own_children_waited'] and j['wait']['all_owned_locks_released']
e=next(json.loads(x['UTF8'])for x in j['full_UTF8']if x['path'].endswith('/ORIGINAL274_WORKER_ERROR.json'))
assert 'reset_peak_memory_stats' in e['error'] and 'Invalid device argument' in e['error']
V.mkdir(exist_ok=False)
for name in ('worker274_new272_H32_CUDA_no_optimizer_once.py','prepare274_frozen_new272_CUDA_admission_source_once.py','parent274_new272_model_only_once.py','run_ROOT274_new272_CUDA_admission_once.py'):
 b=(N/name).read_bytes()
 if name.startswith('worker274'):
  a="device=torch.device('cuda:0');torch.cuda.reset_peak_memory_stats(device)";c="device=torch.device('cuda:0');torch.cuda.init();torch.cuda.set_device(device);torch.cuda.reset_peak_memory_stats(device)"
  assert b.count(a.encode())==1;b=b.replace(a.encode(),c.encode())
 if name.startswith('prepare274'):
  b=b.replace(b"BEFORE_USE274V2_ONLY_LOCK_PATH_AND_NEW_NAMESPACE.json",b"BEFORE_USE274V3_EXPLICIT_NEW_RAW_READ_AFTER_PRECUDA_INIT_ERROR.json")
  a="optimizer_steps_allowed=0)";c="optimizer_steps_allowed=0,previous274V2_dataset_reads_consumed=1,new_necessary_read_purpose='Complete actual CUDA H32 admission after pre-init allocator-metadata failure; not statistics/Git or replay of old entry')"
  assert b.count(a.encode())==1;b=b.replace(a.encode(),c.encode())
 if name.startswith('run_ROOT274'):
  b=b.replace(b'MOD4_NEW272_FUTURE_SAFE_WM274V2_ADMISSION_20261101',b'MOD4_NEW272_FUTURE_SAFE_WM274V3_ADMISSION_20261101')
  b=b.replace(b'ROOT274_NEW272_FIRST_RAW_CUDA_PURPOSE_FROZEN_BEFORE_NETWORK.json',b'ROOT274V3_NEW272_NEW_NECESSARY_CUDA_READ_PURPOSE_FROZEN_BEFORE_NETWORK.json')
 ast.parse(b,filename=name);(V/name).write_bytes(b)
with(V/'BEFORE_USE274V3_EXPLICIT_NEW_RAW_READ_AFTER_PRECUDA_INIT_ERROR.json').open('x',encoding='utf8')as f:
 json.dump(dict(epoch=time.time(),original_false=str(N/'reports/ROOT274_NEW272_ACTUAL_H32_CUDA_OR_ORIGINAL_ERROR_RETURNED.json'),old_entry_consumed=True,prior_dataset_byte_open_np_load=1,prior_optimizer_steps=0,prior_WM_constructed=False,prior_GPU_model_or_physics_reads=0,new_necessary_dataset_byte_open_np_load_max=1,new_purpose='Finish H32 CUDA admission with explicit CUDA init before memory-stat query',new_namespace=True,parent_and_learner_algorithm_unchanged=True,no_statistics_Git_read=True),f,indent=2)
print(json.dumps(dict(passed=True,path=str(V))))
