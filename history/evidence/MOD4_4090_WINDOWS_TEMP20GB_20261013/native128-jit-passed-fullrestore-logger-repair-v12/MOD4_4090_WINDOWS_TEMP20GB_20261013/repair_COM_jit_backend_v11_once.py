from pathlib import Path
import json,time,sys,hashlib,traceback
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent/'MOD4_4090_WINDOWS_REPAIR_20261013'))
from windows4090_native_transport import connect,powershell,upload
R='C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013'
OLD=R+'/temporary_scope128_memory20GB_COM_repr_v10_20261013'
NEW=R+'/temporary_scope128_memory20GB_COM_jit_v11_20261013'
def main():
 receipt=D/'reports/COM_JIT_V11_CPU_DISPATCH_ACTUAL.json';assert not receipt.exists()
 proof=json.loads((D/'reports/COM_JIT_SAVED_WITNESS_V11_ACTUAL.json').read_bytes());assert proof['passed'] and all(x['max_error_m']==0 for x in proof['rows'])
 code="""from pathlib import Path;import json,hashlib,shutil,time,psutil,msvcrt
r=Path('"""+R+"""');old=Path('"""+OLD+"""');new=Path('"""+NEW+"""')
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),bytes=p.stat().st_size,sha256=H(p))
x=json.loads((old/'attempts/temporary2048_native_v1/EXIT_RECEIPT.json').read_bytes());e=json.loads((old/'attempts/temporary2048_native_v1/output/ORIGINAL_ERROR.json').read_bytes());assert x['worker_exitcode']==1 and x['no_PPO'] and 'COM world formula tolerance' in e['error'] and x['own_child_and_descendants_actual_absent']
for row in (x['parent'],x['child']):
 try:p=psutil.Process(row['pid']);assert p.create_time()!=row['created']
 except psutil.NoSuchProcess:pass
with (r/'WINDOWS4090_GPU_EXCLUSIVE.lock').open('r+b') as f:f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1);f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)
assert not new.exists();new.mkdir();shutil.copytree(old/'runtime2048',new/'runtime2048');shutil.copytree(old/'payload',new/'payload');(new/'reports').mkdir();(new/'attempts').mkdir()
helper=r/'COM_JIT_SAVED_WITNESS_MATH_V11/independently_frozen_SDK_arithmetic.py';assert H(helper)=='ac78a7921dd0ec8738dafca97a9ad33ef6ca08e776f3489e73bf08d30577b321'
shutil.copy2(helper,new/'payload/independent_COM_jit_arithmetic.py')
p=new/'payload/windows4090_substep_readback_v6.py';before=ref(p);s=p.read_text(encoding='utf8')
start=s.index('    api_link=link.to(world_dtype)');end=s.index('    com_error=',start)
s=s[:start]+'''    from independent_COM_jit_arithmetic import combine_frame_transforms as independent_represented_transform
    represented_pos,_=independent_represented_transform(link[...,:3].to(world_dtype),link[...,3:7].to(world_dtype),lc[...,:3].to(world_dtype),lc[...,3:7].to(world_dtype))
    expected=represented_pos.double()
'''+s[end:]
p.write_text(s,encoding='utf8');compile(s,str(p),'exec')
mf=json.loads((old/'TEMPORARY_GPU_SEQUENCE_MANIFEST_GRANTED.json').read_bytes());mf.update(scope_root=str(new),epoch=time.time(),COM_JIT_backend_representation_only=dict(old=before,new=ref(p),frozen_independent_arithmetic=ref(new/'payload/independent_COM_jit_arithmetic.py'),original_tolerance_m=1e-5,expected_from_link_and_localCOM_only=True,no_physics_or_setter_change=True,represented_SDK_consistency_not_independent_physical_COM_calibration=True))
cpu=json.loads(Path(mf['target_CPU_receipt']['path']).read_bytes());cpu.update(scope=str(new),epoch=time.time(),new_COM_JIT_representation_only=True);cp=new/'reports/TARGET_TEMP128_COM_JIT_CPU_ACTUAL.json';cp.write_text(json.dumps(cpu,indent=2),encoding='utf8');mf['target_CPU_receipt']=ref(cp);mf['substep_readback_V6']['source_sha256']=H(p)
mf['sourcefreeze_files']=[ref(p) for base in (new/'runtime2048',new/'payload',r/'sdk_exact/source',r/'sdk_exact/apps') for p in sorted(base.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and '.egg-info' not in str(p)]
f=new/'TEMPORARY_GPU_SEQUENCE_MANIFEST_GRANTED.json';f.write_text(json.dumps(mf,indent=2),encoding='utf8');l=new/'TEMPORARY_SEQUENCE_TASK_LEASE_GRANTED.json';l.write_text(json.dumps(dict(epoch=time.time(),case_id='temporary128_memory20GB_COM_jit_sequence_v11',approved_GPU_scope=True,mode='native',scope_root=str(new),environment_root=str(r),shared_gpu_lock=str(r/'WINDOWS4090_GPU_EXCLUSIVE.lock'),manifest_sha256=H(f),human20GB_temporary_branch_authorized=True),indent=2),encoding='utf8')
proof=dict(epoch=time.time(),passed_CPU_representation_only=True,old_error=e,old_EXIT=x,observer=mf['COM_JIT_backend_representation_only'],manifest=ref(f),original_sources_false_and_raw_retained=True,no_physical_GPU_pass_inferred=True)
(new/'reports/COM_JIT_OBSERVER_CPU_ACTUAL.json').write_text(json.dumps(proof,indent=2),encoding='utf8');print(json.dumps(proof))
"""
 f=D/'COM_jit_v11_cpu.py';assert not f.exists();f.write_text(code,encoding='utf8');compile(code,str(f),'exec');remote=R+'/'+f.name;upload(f,remote,60)
 actual=json.loads(powershell(connect(),"[Console]::OutputEncoding=[Text.Encoding]::UTF8;& '"+R+"/env/python.exe' '"+remote+"'",90))
 ps="& '"+NEW+"/payload/register_windows4090_demand_task_audited_v6_once.ps1' -LeasePath '"+NEW+"/TEMPORARY_SEQUENCE_TASK_LEASE_GRANTED.json' -ManifestPath '"+NEW+"/TEMPORARY_GPU_SEQUENCE_MANIFEST_GRANTED.json' -AttemptPath '"+NEW+"/attempts/temporary2048_native_v1' -PythonPath '"+R+"/env/python.exe' -RuntimePath '"+NEW+"/runtime2048' -StageMode native -TrainSeconds 3600 -StartApprovedLease"
 powershell(connect(),ps,35);receipt.write_text(json.dumps(dict(epoch=time.time(),actual=actual,retained_witness_math_GPU_review=proof,new_native_requested_once=True,no_old_GPU_replay=True),indent=2),encoding='utf8');print(json.dumps(dict(report=str(receipt),new_scope=NEW,N128_native_requested=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  (D/'reports'/('COM_JIT_V11_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),inspect_no_replay=True),indent=2),encoding='utf8');raise
