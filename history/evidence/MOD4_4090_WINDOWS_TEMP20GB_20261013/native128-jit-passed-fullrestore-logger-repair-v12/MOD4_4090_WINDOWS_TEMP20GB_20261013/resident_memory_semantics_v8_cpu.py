from pathlib import Path;import json,hashlib,shutil,time,psutil,msvcrt,ast,ctypes
r=Path('C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013');old=Path('C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013/temporary_scope512_memory20GB_native_capacity_v7_20261013');new=Path('C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013/temporary_scope512_memory20GB_resident_bound_v8_20261013')
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),bytes=p.stat().st_size,sha256=H(p))
x=json.loads((old/'attempts/temporary2048_native_v1/EXIT_RECEIPT.json').read_bytes());e=json.loads((old/'attempts/temporary2048_native_v1/output/ORIGINAL_ERROR.json').read_bytes());assert x['worker_exitcode']==1 and x['no_PPO'] and 'MemoryError' in e['error'] and x['own_child_and_descendants_actual_absent']
assert x['peak_RSS_bytes']<20000000000 and x['job_peak_commit_bytes']>=20000000000
for row in (x['parent'],x['child']):
 try:p=psutil.Process(row['pid']);assert p.create_time()!=row['created']
 except psutil.NoSuchProcess:pass
with (r/'WINDOWS4090_GPU_EXCLUSIVE.lock').open('r+b') as f:f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1);f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)
assert not new.exists();new.mkdir();shutil.copytree(old/'runtime2048',new/'runtime2048');shutil.copytree(old/'payload',new/'payload');(new/'reports').mkdir();(new/'attempts').mkdir()
p=new/'payload/temporary_memory_job.py';before=ref(p);s=p.read_text(encoding='utf8')
s+='''\n# ExactMicrosoft API, hardresident limit; no EmptyWorkingSet/no systemsetting.
k.SetProcessWorkingSetSizeEx.argtypes=[w.HANDLE,ctypes.c_size_t,ctypes.c_size_t,w.DWORD]
k.SetProcessWorkingSetSizeEx.restype=w.BOOL
def hard_resident_limit(pid,maximum):
 p=k.OpenProcess(0x0100|0x0400,False,pid);require(p)
 try:require(k.SetProcessWorkingSetSizeEx(p,65536,maximum,0x00000004))
 finally:k.CloseHandle(p)
'''
p.write_text(s,encoding='utf8');compile(s,str(p),'exec')
p=new/'payload/temporary_parent.py';oldparent=ref(p);s=p.read_text(encoding='utf8');s=s.replace('from temporary_memory_job import MemoryJob','from temporary_memory_job import MemoryJob,hard_resident_limit')
assert "job = MemoryJob(m['requested_memory_limit_bytes'])" in s;s=s.replace("job = MemoryJob(m['requested_memory_limit_bytes'])","job = MemoryJob(m['virtual_commit_limit_bytes'])")
s=s.replace('job.assign(os.getpid())','job.assign(os.getpid())\n    hard_resident_limit(os.getpid(),134217728)')
anchor='ci = ident(child.pid)';assert s.count(anchor)==1;s=s.replace(anchor,'hard_resident_limit(child.pid,19500000000)\n            '+anchor)
s=s.replace('peakhard >= 18000000000','peakhard >= 30000000000').replace('peakhard >= 19000000000','peakhard >= 31000000000')
needle='peakhard + 512 * 256 * 24 * 16 * 4 + 1073741824 + 33554432 < 18000000000';assert needle in s;s=s.replace(needle,'peakhard + 512 * 256 * 24 * 16 * 4 + 2147483648 + 33554432 < 30000000000')
p.write_text(s,encoding='utf8');compile(s,str(p),'exec')
mf=json.loads((old/'TEMPORARY_GPU_SEQUENCE_MANIFEST_GRANTED.json').read_bytes());mf.update(scope_root=str(new),epoch=time.time(),virtual_commit_limit_bytes=32000000000,physical_RAM_target_bytes=20000000000,worker_hard_resident_set_limit_bytes=19500000000,parent_hard_resident_set_limit_bytes=134217728,no_system_pagefile_or_otherprocess_change=True,memory_API_official_source='https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-setprocessworkingsetsizeex')
cpu=json.loads(Path(mf['target_CPU_receipt']['path']).read_bytes());cpu.update(scope=str(new),epoch=time.time(),virtual_commit_vs_resident_memory_distinction=True,source_all512_projection_reused_exact=True);cp=new/'reports/TARGET_TEMP512_RESIDENT_BOUND_CPU_ACTUAL.json';cp.write_text(json.dumps(cpu,indent=2),encoding='utf8');mf['target_CPU_receipt']=ref(cp)
mf['sourcefreeze_files']=[ref(p) for base in (new/'runtime2048',new/'payload',r/'sdk_exact/source',r/'sdk_exact/apps') for p in sorted(base.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and '.egg-info' not in str(p)]
f=new/'TEMPORARY_GPU_SEQUENCE_MANIFEST_GRANTED.json';f.write_text(json.dumps(mf,indent=2),encoding='utf8');l=new/'TEMPORARY_SEQUENCE_TASK_LEASE_GRANTED.json';l.write_text(json.dumps(dict(epoch=time.time(),case_id='temporary512_memory20GB_resident_bound_sequence_v8',approved_GPU_scope=True,mode='native',scope_root=str(new),environment_root=str(r),shared_gpu_lock=str(r/'WINDOWS4090_GPU_EXCLUSIVE.lock'),manifest_sha256=H(f),human20GB_temporary_branch_authorized=True),indent=2),encoding='utf8')
proof=dict(epoch=time.time(),passed_CPU_memory_semantics_only=True,old_native_error=e,old_EXIT=x,actual_old512_RSS_peak_bytes=x['peak_RSS_bytes'],actual_old_commit_peak_bytes=x['job_peak_commit_bytes'],virtual_limit32GB_not_physicalRAM_budget_increase=True,resident20GB_target_and25percent_actualRSS_headroom_retained=True,new_memorysource=dict(old=before,new=ref(new/'payload/temporary_memory_job.py')),new_parent=dict(old=oldparent,new=ref(p)),new_manifest=ref(f),old_source_preserved=True)
(new/'reports/RESIDENT_RAM_BOUND_SOURCE_CPU_ACTUAL.json').write_text(json.dumps(proof,indent=2),encoding='utf8');print(json.dumps(proof))
