"""Build future sharing-permitted owner source; never replace active owner or GO.
Tests are stdlib/fixture-only. No SSH, SDK, GPU, model or canonical operations.
"""
from pathlib import Path
import ast,hashlib,json,sys
R=Path(__file__).resolve().parent;S=R/'source_runtime';out=S/'supermimic_original_owner_shared_v2.py';report=R/'reports/FUTURE_SHARED_GPU_ADMISSION_SOURCE_V2.json'
assert not out.exists()and not report.exists()
src=S/'supermimic_original_owner.py';original=src.read_text(encoding='utf-8');tree=ast.parse(original);target=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='gpu');lines=original.splitlines(keepends=True)
new=''.join(lines[:target.lineno-1])+'''def gpu(uuid):
 from shared_gpu_admission_v1 import admit_shared_gpu
 return admit_shared_gpu(uuid,B)
'''+''.join(lines[target.end_lineno:]);ast.parse(new);out.write_text(new,encoding='utf-8',newline='\n')
sys.path.insert(0,str(S));from shared_gpu_admission_v1 import evaluate_resource_snapshot
u='GPU-16828f91-2b45-b646-8dc0-9481138e2842';ram=70*1024**3;disk=80*1024**3;checks=[]
def check(name,fn,exception=None):
 try:v=fn()
 except Exception as e:
  assert exception and isinstance(e,exception),(name,type(e));checks.append(dict(name=name,passed=True,expected_exception=type(e).__name__));return
 assert exception is None,name;checks.append(dict(name=name,passed=True));return v
empty=check('empty_GPU_original_headroom',lambda:evaluate_resource_snapshot(u,f'{u},NVIDIA GeForce RTX 4090,24203,0','',ram,disk));assert empty['compute_empty']
shared=check('low_load_foreign_compute_now_allowed',lambda:evaluate_resource_snapshot(u,f'{u},NVIDIA GeForce RTX 4090,19653,14',f'{u},1474057,4542',ram,disk));assert not shared['compute_empty']and len(shared['preexisting_compute_processes'])==1
check('utilization_over30_still_waits',lambda:evaluate_resource_snapshot(u,f'{u},NVIDIA GeForce RTX 4090,19653,31',f'{u},1474057,4542',ram,disk),BlockingIOError)
check('insufficient_free_memory_still_waits',lambda:evaluate_resource_snapshot(u,f'{u},NVIDIA GeForce RTX 4090,15669,0','',ram,disk),BlockingIOError)
check('RAM_boundary_still_waits',lambda:evaluate_resource_snapshot(u,f'{u},NVIDIA GeForce RTX 4090,24203,0','',64*1024**3,disk),BlockingIOError)
check('disk_boundary_still_waits',lambda:evaluate_resource_snapshot(u,f'{u},NVIDIA GeForce RTX 4090,24203,0','',ram,50*1024**3),BlockingIOError)
check('wrong_GPU_rejected',lambda:evaluate_resource_snapshot(u,'OTHER,NVIDIA GeForce RTX 4090,24203,0','',ram,disk),RuntimeError)
newtree=ast.parse(new)
for before in [n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name!='gpu']:
 after=next(n for n in newtree.body if isinstance(n,ast.FunctionDef)and n.name==before.name);assert ast.dump(before,include_attributes=False)==ast.dump(after,include_attributes=False),before.name
checks.append(dict(name='all_non_gpu_functions_AST_identical_including_main_locks_budget_accounting',passed=True))
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
v=dict(kind='SOURCE_ONLY_FUTURE_LOW_LOAD_GPU_SHARING_NOT_ACTIVE_HOTPATCH',human_request='2026-11-02T18:48:07+08:00',original_source_SHA=H(src),future_owner_path=str(out),future_owner_bytes=out.stat().st_size,future_owner_SHA=H(out),admission_library_path=str(S/'shared_gpu_admission_v1.py'),admission_library_SHA=H(S/'shared_gpu_admission_v1.py'),checks=checks,source_PT_raw_SDK_GPU_C_GO_or_active_process_operations=0,active_owner_unchanged=True,activation='ONLY in a future unused source manifest/window; not uploaded or executed as owner')
report.write_text(json.dumps(v,indent=2),encoding='utf-8');print(json.dumps(v,indent=2))
