"""Start measured chosenN using its complete prePPO source, never benchmark weights."""
from pathlib import Path
import sys,json,time,hashlib,traceback
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent/'MOD4_4090_WINDOWS_REPAIR_20261013'))
from windows4090_native_transport import connect,powershell,upload
R='C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013'
def main():
 decision=json.loads((D/'reports/CAPACITY_SELECTED_MEASURED_DECISION_ACTUAL.json').read_bytes());n=decision['selected_num_envs'];old=decision['selected_scope'];source=decision['production_prePPO_source']
 case=f'capacity{n}_selected_ownstate_production_v1_20261013';new=R+'/'+case
 proof=Path(decision['complete_CPU_review']);assert proof.is_file() and hashlib.sha256(proof.read_bytes()).hexdigest()==decision['complete_CPU_review_SHA']
 code="""from pathlib import Path;import json,hashlib,psutil,msvcrt,shutil,time,ast
r=Path('"""+R+"""');old=Path('"""+old+"""');new=Path('"""+new+"""');N="""+str(n)+"""
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),bytes=p.stat().st_size,sha256=H(p))
rel=json.loads((old/'SEQUENCE_PARENT_OSLOCK_RELEASED_ACTUAL.json').read_bytes());assert rel['OSlock_released'] and rel['all_own_descendants_actual_absent']
parent=rel['parent']
try:p=psutil.Process(parent['pid']);assert p.create_time()!=parent['created']
except psutil.NoSuchProcess:pass
with (r/'WINDOWS4090_GPU_EXCLUSIVE.lock').open('r+b') as f:f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1);f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)
source=Path('"""+source['path'].replace('\\','/')+"""');assert H(source)=='"""+source['sha256']+"""'
assert not new.exists();new.mkdir();(new/'reports').mkdir();(new/'attempts').mkdir();shutil.copytree(old/'runtime2048',new/'runtime2048');shutil.copytree(old/'payload',new/'payload',ignore=shutil.ignore_patterns('__pycache__'))
p=new/'payload/temporary_parent.py';s=p.read_text(encoding='utf8');needle="for phase in ('native', 'fullrestore', 'train'):";assert s.count(needle)==1;s=s.replace(needle,"for phase in ('train',):");compile(s,str(p),'exec');p.write_text(s,encoding='utf8')
mf=json.loads((old/'TEMPORARY_GPU_SEQUENCE_MANIFEST_GRANTED.json').read_bytes());mf.update(scope_root=str(new),epoch=time.time(),source=ref(source),max_formal_updates=256,capacity_benchmark_only=False,production_weights_discarded=False,chosen_num_envs_by_actual_throughput_and_resource=True,strict_same_expanded_source=True,new_native_fullrestore_not_replayed=True,concrete_future_training_trace_upper_bound_bytes=N*256*24*16*4)
import sys;sys.path.insert(0,str(new/'payload'));import torch,temporary_state_binding as b
assert not torch.cuda.is_initialized() and b.N==N;ck=torch.load(source,map_location='cpu',weights_only=False);b.validate(ck,H(source));assert b.floating_count(ck)==107 and len(b.perenv_inventory(ck))==99 and ck['WINDOWS4090_EXPANDED_ENV_BRANCH']['actual_current_GPU_restore_verified'] and not ck['WINDOWS4090_EXPANDED_ENV_BRANCH']['all12_own_CPUCUDA_restore_disk_roundtrip_and_API_offsets_pending']
cpu=dict(epoch=time.time(),passed=True,source=ref(source),chosen_num_envs=N,float107=True,perenv99=True,source_is_own_prePPO_not_discard_benchmark=True,actual_native_fullrestore_proofs_reused_byteSHA=True,old_parent_release_actual=rel)
q=new/'reports/SELECTED_SAME_EXPANDED_TARGET_CPU_ACTUAL.json';q.write_text(json.dumps(cpu,indent=2),encoding='utf8');mf['target_CPU_receipt']=ref(q)
mf['sourcefreeze_files']=[ref(p) for base in (new/'runtime2048',new/'payload',r/'sdk_exact/source',r/'sdk_exact/apps') for p in sorted(base.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and '.egg-info' not in str(p)]
q=new/'TEMPORARY_GPU_SEQUENCE_MANIFEST_GRANTED.json';q.write_text(json.dumps(mf,indent=2),encoding='utf8');lease=new/'TEMPORARY_SEQUENCE_TASK_LEASE_GRANTED.json';lease.write_text(json.dumps(dict(epoch=time.time(),case_id='"""+case+"""',approved_GPU_scope=True,mode='train',scope_root=str(new),environment_root=str(r),shared_gpu_lock=str(r/'WINDOWS4090_GPU_EXCLUSIVE.lock'),manifest_sha256=H(q),human20GB_environment_search_and_training_authorized=True),indent=2),encoding='utf8');print(json.dumps(dict(epoch=time.time(),scope=str(new),targetCPU=ref(new/'reports/SELECTED_SAME_EXPANDED_TARGET_CPU_ACTUAL.json'),num_envs=N,source=ref(source),no_future_PPO_pass_inferred=True)))
"""
 p=D/'selected_production_target_CPU_once.py';assert not p.exists();compile(code,str(p),'exec');p.write_text(code,encoding='utf8');upload(p,R+'/'+p.name,60)
 a=json.loads(powershell(connect(),"[Console]::OutputEncoding=[Text.Encoding]::UTF8;& '"+R+"/env/python.exe' '"+R+'/'+p.name+"'",100))
 ps="& '"+new+"/payload/register_windows4090_demand_task_audited_v6_once.ps1' -LeasePath '"+new+"/TEMPORARY_SEQUENCE_TASK_LEASE_GRANTED.json' -ManifestPath '"+new+"/TEMPORARY_GPU_SEQUENCE_MANIFEST_GRANTED.json' -AttemptPath '"+new+"/attempts/temporary2048_train_v1' -PythonPath '"+R+"/env/python.exe' -RuntimePath '"+new+"/runtime2048' -StageMode train -TrainSeconds 3600 -StartApprovedLease"
 powershell(connect(),ps,35);p=D/'reports/CAPACITY_SELECTED_PRODUCTION_DISPATCH_ACTUAL.json';assert not p.exists();p.write_text(json.dumps(dict(epoch=time.time(),actual=a,one_selected_production_GPU_lease=True),indent=2),encoding='utf8');print(json.dumps(dict(report=str(p),num_envs=n,scope=new)))
if __name__=='__main__':
 try:main()
 except BaseException:
  (D/'reports'/f'SELECTED_PRODUCTION_ORIGINAL_ERROR_{time.time_ns()}.json').write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),inspect_actual_before_continuation=True),indent=2),encoding='utf8');raise
