"""One bounded read-only admission; no Task, lease, directory, GPU or budget writes."""
from pathlib import Path
import json,sys,time,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports'
sys.path[:0]=[str(W/'MOD4_TWO72_E2_E3_HEALTHY_SAVED_CONTINUATIONS_20261017/curb275_final87_frozen3060_v1'),str(W/'MOD4_3060_BODYFRAME_FIRST_FULL80_20261014')]
import transport_249_fresh_signed_desktop_exact_0112_v8 as t
t.ROOT='D:/MOD4_async_eval/MOD4_TWO72_CLOSED_SOURCES_HEALTHY_NEXT_BLOCK_20261017/E2_CLOSED109_FROZEN_V4'
P=R/'E2_CLOSED109_249_RESOURCE_0818_READONLY_ADMISSION_ACTUAL.json'
assert not P.exists();c=None
v=dict(epoch=time.time(),root=t.ROOT,no_Task_lease_directory_GPU_or_budget_write=True)
try:
 c=t.connect();v['actual_resource']=t.py(c,t.guard_code(),timeout=90);v['passed_readonly_resource_admission']=bool(v['actual_resource']['shared_OS_lock_free'] and v['actual_resource']['new_root_unused'])
except BaseException:
 v.update(passed_readonly_resource_admission=False,original_error=traceback.format_exc(),no_runtime_dispatch=True)
finally:
 t.close(c)
 with P.open('x',encoding='utf8',newline='\n') as f:json.dump(v,f,indent=2)
print(json.dumps(dict(report=str(P),passed=v['passed_readonly_resource_admission'],actual_resource=v.get('actual_resource'),original_error=v.get('original_error')),ensure_ascii=False),flush=True)
