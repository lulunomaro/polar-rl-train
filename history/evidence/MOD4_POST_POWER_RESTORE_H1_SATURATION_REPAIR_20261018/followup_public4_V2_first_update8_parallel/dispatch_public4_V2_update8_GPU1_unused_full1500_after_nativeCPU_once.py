"""Human-authorized GPU1 frozen evaluation; GPU0 training is never stopped or signalled."""
from pathlib import Path
import sys,json,time,getpass,traceback,hashlib
B=Path(__file__).resolve().parent;R=B/'reports';W=B.parent;P=W/'MOD4_H1_HUMAN_REQUESTED_SAME_SCOPE_RESTART_20261017';sys.path.insert(0,str(P));import deploy_human_requested_H1_new_finite_strict_native_reuse_once as d
Q=B/'frozen_public4_update8_linux_v1/payload';TARGET='/home/lc01/Zonglin Li/zonglin2/tasks/H1p8_1810ev1f';GPU='GPU-c27eecbd-6838-7290-1cd2-37e34522213d';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
ADMIT=r'''
from pathlib import Path
import sys,os,json,time,psutil,fcntl,subprocess,shutil
B=Path(sys.argv[1]);owned=Path('/home/lc01/Zonglin Li/zonglin2');gpu=sys.argv[2];old=owned/'tasks/T3_1710v10hr/recovery';assert B.resolve().is_relative_to(owned.resolve()) and not B.exists()
end=json.loads((old/'NATIVE_ONLY_PARENT_EXIT_ACTUAL.json').read_bytes());assert end['all_actual_own_GPU_children_waited'] and end['private_GPU_fcntl_released_if_acquired'] and end['passed_native_CPU'] and not end['original_error']
alive=[]
for p in psutil.process_iter(['pid','create_time','cmdline']):
 try:
  if p.pid!=os.getpid() and any(x.startswith(str(old)+'/') for x in p.info['cmdline'] or []):alive.append(p.info)
 except psutil.Error:pass
assert not alive,alive;locks=[]
for path in (owned/'state'/('three_expert_v2_'+gpu+'.lock'),owned/'state/finite_environment_validation.lock'):
 with path.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN);locks.append(dict(path=str(path),inode=path.stat().st_ino,actual_free=True))
compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']).decode();assert not any(gpu in x for x in compute.splitlines()),compute
line=next(x for x in subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits']).decode().splitlines() if gpu in x);assert int(line.split(',')[-1])>7000 and psutil.virtual_memory().available>8*1024**3 and shutil.disk_usage(owned).free>25*1024**3
B.mkdir(parents=True);print(json.dumps(dict(epoch=time.time(),GPU_UUID=gpu,selected_GPU=line,compute_snapshot=compute,locks=locks,previous_own_E3_native_actual_out=True,target_durable_free=shutil.disk_usage(owned).free,other_GPU_processes_untouched=True,no_task_or_GPU_yet=True)))
'''
CPU=r'''
from pathlib import Path
import os,sys,json,ast,time,hashlib,importlib.metadata as md
os.environ['CUDA_VISIBLE_DEVICES']='';B=Path(sys.argv[1]);H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();M=B/'H1_PUBLIC4_UPDATE8_LINUX4090_MANIFEST_V1.json';m=json.loads(M.read_bytes())
for r in m['files']:
 p=B/r['relative'];assert p.resolve().is_relative_to(B.resolve()) and p.stat().st_size==r['bytes'] and H(p)==r['SHA'],r['relative']
 if p.suffix=='.py':ast.parse(p.read_text('utf8'))
base=Path('/home/lc01/Zonglin Li/zonglin2');sdk=base/'src/fangzhen_linux/third_party/IsaacLab-3.0.0-beta2.patch1/source/isaaclab/isaaclab/utils/math.py';assert H(sdk)=='4ae6fe19d9b18c2747bf6546dc72f75cfe497ee2ba6046e95fabbeb33d958d33'
site=base/'envs/mod4/lib/python3.12/site-packages';bindings=sorted((site/'isaacsim').glob('**/omni/physx/bindings/_physx*.so'));assert len(bindings)==1,[str(p) for p in bindings]
files=[dict(path=str(sdk),bytes=sdk.stat().st_size,SHA=H(sdk))]
for rel,sha in [('rsl_rl/runners/on_policy_runner.py','39358a0a60219fdb360df7acddf80f6a382837aa58e2ec0ccf875df4afee4825'),('rsl_rl/algorithms/ppo.py','a2d35e7ad7b884c80b7434e7d2ce785a6da1e18d93c96f1179fbd3a208669f8c')]:
 p=site/rel;assert H(p)==sha;files.append(dict(path=str(p),bytes=p.stat().st_size,SHA=sha))
versions={};missing=[]
for n in ('torch','numpy','tensordict','rsl-rl','isaacsim'):
 try:versions[n]=md.version(n)
 except md.PackageNotFoundError:missing.append(n)
assert missing==['rsl-rl'],missing
binding=bindings[0];backend=dict(epoch=time.time(),execution_backend='linux72_GPU1_frozen_only',versions=versions,metadata_lookup_missing_explicit=missing,rsl_runner_PPO_files_exact_independent_of_missing_distribution_metadata=True,files=files,native_binding=dict(path=str(binding),bytes=binding.stat().st_size,SHA=H(binding)),Windows3060_backend_not_inherited=True,public_source_to_binary_bitexact_proven=False)
out=B/'EXPECTED_ACTUAL_LINUX72_BACKEND_V1.json';assert not out.exists();out.write_text(json.dumps(backend,indent=2))
import torch
torch.set_num_threads(1);sys.path.insert(0,str(B));from h1_public4_update8_source_guard_v1 import validate_H1_source
p=B/m['source_relative'];assert H(p)==m['source']['SHA'];c=torch.load(p,map_location='cpu',weights_only=False);validate_H1_source(c);assert not torch.cuda.is_initialized()
print(json.dumps(dict(epoch=time.time(),passed_complete_target_CPU_manifest_AST_source_and_actual_Linux_SDK=True,files=len(m['files']),manifest_SHA=H(M),backend=backend,backend_file_SHA=H(out),source_SHA=H(p),no_GPU_or_native_yet=True)))
'''
def main():
 native=json.loads((R/'H1_PUBLIC4U8_LINUX72_120_ALL_PHYSICAL_PUBLIC04_SOURCE_CPU_ACTUAL.json').read_bytes());assert native['passed_complete_data_and_source_CPU'] and native['steps']==120
 put('PUBLIC4U8_LINUX_GPU1_FULL1500_EXISTING_UNUSED_NATIVE120_FINISH_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=__import__('os').getpid(),argv=sys.argv,actual_alive_only_exclusive_all_transport=True,human_4090_eval_parallel_training=True));pw=getpass.getpass('Host72 GPU1 frozen evaluation; training untouched (hidden): ');c=None
 try:
  c=d.a.connect72(pw);pw=None
  admission=d.a.code(c,d.a.PY,ADMIT,TARGET,GPU,timeout=90);put('PUBLIC4U8_LINUX_GPU1_FULL1500_FRESH_RESOURCE_ADMISSION_ACTUAL.json',admission)
  copied=d.a.code(c,d.a.PY,"from pathlib import Path;import json,shutil,hashlib,psutil,os;A=Path('/home/lc01/Zonglin Li/zonglin2/tasks/H1p8_1810ev1');B=Path("+repr(TARGET)+");e=json.loads((A/'native120/PARENT_EXIT_RECEIPT.json').read_bytes());assert e['actual_child_returncode']==0 and not e['original_errors'] and e['all_actual_own_children_waited'] and e['complete'];alive=[p.info for p in psutil.process_iter(['pid','cmdline']) if p.pid!=os.getpid() and any(x.startswith(str(A)+'/') for x in p.info['cmdline'] or [])];assert not alive,alive;m=json.loads((A/'H1_PUBLIC4_UPDATE8_LINUX4090_MANIFEST_V1.json').read_bytes());files=[r['relative'] for r in m['files']]+['H1_PUBLIC4_UPDATE8_LINUX4090_MANIFEST_V1.json'];[( (B/n).parent.mkdir(parents=True,exist_ok=True),shutil.copy2(A/n,B/n)) for n in files];print(json.dumps(dict(actual_native_parent_child_EXIT0_out_before_full=True,only_static_manifest_files_copied_no_native_or_raw_replay=True,files=len(files))))",timeout=120);put('PUBLIC4U8_LINUX_GPU1_FULL1500_NATIVE_EXIT0_STATIC_SOURCE_COPY_ACTUAL.json',copied)
  cpu=d.a.code(c,d.a.PY,CPU,TARGET,timeout=240);put('PUBLIC4U8_LINUX_GPU1_FULL1500_FULL_PACKAGE_SOURCE_ACTUAL_INSTALLED_BACKEND_CPU_ADMITTED.json',cpu)
  m=json.loads((Q/'H1_PUBLIC4_UPDATE8_LINUX4090_MANIFEST_V1.json').read_bytes());case=dict(router_mode='single_eval',kind='jump',steps=1500,num_envs=80,seed=20260928,headless=True,device='cuda:0');lease=dict(target_host='10.24.0.72',execution_backend='linux72_GPU1_frozen_only',GPU_UUID=GPU,namespace='H1_PUBLIC4_UPDATE8_LINUX4090_V1_20261018',GPU_lease_granted_by_root=True,actual_selected_GPU_idle_private_lock_free=True,human_authorized_4090_eval_parallel_training_not_interrupted=True,checkpoint_sha256=m['source']['SHA'],checkpoint_path=TARGET+'/'+m['source_relative'],worker_sha256=H(Q/'h1_linux4090_frozen_worker_v1.py'),source_manifest_sha256=H(Q/'H1_PUBLIC4_UPDATE8_LINUX4090_MANIFEST_V1.json'),actual_Linux_backend_SHA=cpu['backend_file_SHA'],case_id='H1_PUBLIC4_UPDATE8_LINUX72_GPU1_FULL1500_V1_20261018',case_parameters=case,actual_same_backend_source_native120_allrow_CPU_passed=True,native120_actual_exit_childrenout_lockfree=True,native_CPU_report_SHA=H(R/'H1_PUBLIC4U8_LINUX72_120_ALL_PHYSICAL_PUBLIC04_SOURCE_CPU_ACTUAL.json'))
  parent=d.launch(d.a.code,c,d.a.PY,TARGET,'h1_linux4090_frozen_parent_v1.py',dict(role='frozen_eval_only',attempt=TARGET+'/full1500',lease=lease));put('PUBLIC4U8_LINUX_GPU1_H1_FULL1500_DETACHED_ACTUAL.json',dict(epoch=time.time(),parent=parent,root=TARGET,lease=lease,actual_target_CPU_passed=True,no_PPO_or_canonical_charge=True,training_not_stopped_or_signalled=True,full_result_not_yet=True));print(json.dumps(dict(GPU1_frozen_full_dispatched=True,parent=parent,training_untouched=True)),flush=True)
 finally:
  pw=None
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('PUBLIC4U8_LINUX_GPU1_FULL1500_EXISTING_UNUSED_NATIVE120_FINISH_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),unknown_actual_before_new_scope=True,other_GPU_training_untouched=True));raise
