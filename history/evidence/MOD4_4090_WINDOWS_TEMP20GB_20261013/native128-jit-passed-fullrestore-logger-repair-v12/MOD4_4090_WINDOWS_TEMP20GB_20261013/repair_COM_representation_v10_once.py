"""New independent observer arithmetic phase, same1e-5 tolerance/physics source."""
from pathlib import Path
import json,time,sys,hashlib,traceback
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent/'MOD4_4090_WINDOWS_REPAIR_20261013'))
from windows4090_native_transport import connect,powershell,upload
R='C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013';OLD=R+'/temporary_scope128_memory20GB_resident_v9_20261013';NEW=R+'/temporary_scope128_memory20GB_COM_repr_v10_20261013'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 receipt=D/'reports/COM_REPRESENTATION_V10_CPU_DISPATCH_ACTUAL.json';assert not receipt.exists()
 proof=json.loads((D/'reports/NATIVE128_COM_REPRESENTATION_CPU_REPLAY_ACTUAL.json').read_bytes());assert proof['passed'] and proof['original_COM_tolerance_m']==1e-5
 code="""from pathlib import Path;import json,hashlib,shutil,time,psutil,msvcrt,ast
r=Path('"""+R+"""');old=Path('"""+OLD+"""');new=Path('"""+NEW+"""')
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),bytes=p.stat().st_size,sha256=H(p))
x=json.loads((old/'attempts/temporary2048_native_v1/EXIT_RECEIPT.json').read_bytes());e=json.loads((old/'attempts/temporary2048_native_v1/output/ORIGINAL_ERROR.json').read_bytes());assert x['worker_exitcode']==1 and x['no_PPO'] and 'COM world formula tolerance' in e['error'] and x['own_child_and_descendants_actual_absent']
for row in (x['parent'],x['child']):
 try:p=psutil.Process(row['pid']);assert p.create_time()!=row['created']
 except psutil.NoSuchProcess:pass
with (r/'WINDOWS4090_GPU_EXCLUSIVE.lock').open('r+b') as f:f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1);f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)
assert not new.exists();new.mkdir();shutil.copytree(old/'runtime2048',new/'runtime2048');shutil.copytree(old/'payload',new/'payload');(new/'reports').mkdir();(new/'attempts').mkdir()
p=new/'payload/windows4090_substep_readback_v6.py';before=ref(p);s=p.read_text(encoding='utf8')
anchor='expected = expected_double.to(world_dtype).double()';assert s.count(anchor)==1
s=s.replace(anchor,"api_link=link.to(world_dtype)\\n    api_local=lc.to(world_dtype)\\n    twice_cross=torch.cross(api_link[...,4:7],api_local[...,:3],dim=-1)*2\\n    rotated_local=api_local[...,:3]+api_link[...,3:4]*twice_cross+torch.cross(api_link[...,4:7],twice_cross,dim=-1)\\n    expected=(api_link[...,:3]+rotated_local).double()")
# Fixed arithmetic representation derives onlyfromlink+localCOM, never actualCOMoutput.
p.write_text(s,encoding='utf8');compile(s,str(p),'exec')
mf=json.loads((old/'TEMPORARY_GPU_SEQUENCE_MANIFEST_GRANTED.json').read_bytes());mf.update(scope_root=str(new),epoch=time.time(),COM_observer_representation_only=dict(old=before,new=ref(p),original_tolerance_m=1e-5,expected_from_link_and_localCOM_only=True,independent_float32_API_operation_order=True,unrounded_double_diagnostic_retained=True,no_actual_output_used_to_select_expected=True,no_physics_or_SDK_setter_change=True))
cpu=json.loads(Path(mf['target_CPU_receipt']['path']).read_bytes());cpu.update(scope=str(new),epoch=time.time(),new_observer_representation_only=True);cp=new/'reports/TARGET_TEMP128_COM_REPR_CPU_ACTUAL.json';cp.write_text(json.dumps(cpu,indent=2),encoding='utf8');mf['target_CPU_receipt']=ref(cp);mf['substep_readback_V6']['source_sha256']=H(new/'payload/windows4090_substep_readback_v6.py')
mf['sourcefreeze_files']=[ref(p) for base in (new/'runtime2048',new/'payload',r/'sdk_exact/source',r/'sdk_exact/apps') for p in sorted(base.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and '.egg-info' not in str(p)]
f=new/'TEMPORARY_GPU_SEQUENCE_MANIFEST_GRANTED.json';f.write_text(json.dumps(mf,indent=2),encoding='utf8');l=new/'TEMPORARY_SEQUENCE_TASK_LEASE_GRANTED.json';l.write_text(json.dumps(dict(epoch=time.time(),case_id='temporary128_memory20GB_COM_repr_sequence_v10',approved_GPU_scope=True,mode='native',scope_root=str(new),environment_root=str(r),shared_gpu_lock=str(r/'WINDOWS4090_GPU_EXCLUSIVE.lock'),manifest_sha256=H(f),human20GB_temporary_branch_authorized=True),indent=2),encoding='utf8')
proof=dict(epoch=time.time(),passed_CPU_observer_representation_only=True,old_error=e,old_EXIT=x,new_observer=mf['COM_observer_representation_only'],manifest=ref(f),original_sources_false_and_raw_retained=True,no_GPU_pass_inferred=True)
(new/'reports/COM_REPRESENTATION_OBSERVER_CPU_ACTUAL.json').write_text(json.dumps(proof,indent=2),encoding='utf8');print(json.dumps(proof))
"""
 f=D/'COM_representation_v10_cpu.py';assert not f.exists();f.write_text(code,encoding='utf8');compile(code,str(f),'exec');remote=R+'/'+f.name;upload(f,remote,60)
 actual=json.loads(powershell(connect(),"[Console]::OutputEncoding=[Text.Encoding]::UTF8;& '"+R+"/env/python.exe' '"+remote+"'",90))
 ps="& '"+NEW+"/payload/register_windows4090_demand_task_audited_v6_once.ps1' -LeasePath '"+NEW+"/TEMPORARY_SEQUENCE_TASK_LEASE_GRANTED.json' -ManifestPath '"+NEW+"/TEMPORARY_GPU_SEQUENCE_MANIFEST_GRANTED.json' -AttemptPath '"+NEW+"/attempts/temporary2048_native_v1' -PythonPath '"+R+"/env/python.exe' -RuntimePath '"+NEW+"/runtime2048' -StageMode native -TrainSeconds 3600 -StartApprovedLease"
 powershell(connect(),ps,35);receipt.write_text(json.dumps(dict(epoch=time.time(),actual=actual,independent_saved_witness_CPU_review=proof,new_native_requested_once=True,old_sdk_not_replayed=True,old_sources_failures_preserved=True),indent=2),encoding='utf8');print(json.dumps(dict(report=str(receipt),new_scope=NEW,N128_native_requested=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  (D/'reports'/('COM_REPR_V10_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),inspect_no_replay=True),indent=2),encoding='utf8');raise
