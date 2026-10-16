"""New CPU-admitted E3 scope, exact samehost base reuse, no E3 learning."""
from pathlib import Path
import sys,os,json,time,getpass,traceback,shlex,hashlib
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';E=D/'e3_legal_fall_reset_admission';ROOT='/home/lc01/Zonglin Li/zonglin2/tasks/'+D.name+'/e3_legal_pose_contact_v1';BASE='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_HOST72_E2_MOVING4_AND_H1_JUMP_ADMISSION_20261016/h1_flat_XYZW_fullpose_calibration_v3';PY='/home/lc01/Zonglin Li/zonglin2/run-python.sh';sys.path.insert(0,str(W/'MOD4_H1_GROUNDED_PRELAUNCH_PROGRESS_V2_20261016'));from deploy_grounded_H1_V2_new_native_CPU_then_finite1800_once import code,H,connect72
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
CREATE=r'''
from pathlib import Path
import os,sys,json,time,shutil,subprocess,hashlib,psutil
B=Path(sys.argv[1]);A=Path(sys.argv[2]);OWN=Path('/home/lc01/Zonglin Li/zonglin2');assert B.resolve().is_relative_to(OWN.resolve()) and not B.exists();GPU='GPU-c27eecbd-6838-7290-1cd2-37e34522213d';raw=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']).decode();assert not any(GPU in x for x in raw.splitlines());assert psutil.virtual_memory().available>4*1024**3
assert hashlib.sha256((A/'job1/source/E0_full_source.pt').read_bytes()).hexdigest()=='b10958d2a8631b12c0f9502bf7fa9230d9a7a1ae9863443bb68388604bed61f8'
for name in ('job1','lib'):
 for p in (A/name).rglob('*'):assert p.resolve().is_relative_to(OWN.resolve())
B.mkdir();shutil.copytree(A/'job1',B/'job1',ignore=shutil.ignore_patterns('home','tmp','cache','config','data','__pycache__'));shutil.copytree(A/'lib',B/'lib');task=json.loads((B/'job1/TASK.json').read_bytes());(B/'job1/ORIGINAL_CALIBRATION_TASK_REFERENCE.json').write_text(json.dumps(task,indent=2));task.update(kind='E3_LEGAL_FALLEN_RESET_ADMISSION',GPU_UUID=GPU,approved_for_PPO=False,template_approved_GPU=False,no_reward_termination_or_hardware_change=True);(B/'job1/TASK.json').write_text(json.dumps(task,indent=2));print(json.dumps(dict(epoch=time.time(),new_root=str(B),source_samehost_bytes_reused=True,no_GPU_or_native_yet=True,original_GPU1_snapshot_compute=raw)))
'''
VERIFY=r'''
from pathlib import Path
import os,sys,json,time,ast,hashlib
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
B=Path(sys.argv[1]);m=json.loads((B/'OWN_E3_FILES_CPU_MANIFEST.json').read_bytes());torch.set_num_threads(2);rng=torch.get_rng_state().clone()
for r in m['files']:
 p=B/r['relative'];assert p.stat().st_size==r['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==r['SHA'];ast.parse(p.read_text('utf8'))
s=B/'job1/source/E0_full_source.pt';assert hashlib.sha256(s.read_bytes()).hexdigest()=='b10958d2a8631b12c0f9502bf7fa9230d9a7a1ae9863443bb68388604bed61f8';v=torch.load(s,map_location='cpu',weights_only=False);assert len(v['actor_state_dict'])==9 and len(v['critic_state_dict'])==8 and len(v['optimizer_state_dict']['state'])==17 and {int(x['step']) for x in v['optimizer_state_dict']['state'].values()}=={639560};count=[0,0]
def walk(x):
 if torch.is_tensor(x):count[0]+=1;count[1]+=int(x.is_floating_point());assert not x.is_floating_point() or torch.isfinite(x).all()
 elif isinstance(x,dict):
  for y in x.values():walk(y)
 elif isinstance(x,(tuple,list)):
  for y in x:walk(y)
walk(v);rows=[]
for p in sorted(B.rglob('*')):
 if p.is_file() and not any(x in ('home','tmp','cache','config','data') for x in p.relative_to(B).parts):rows.append(dict(relative=p.relative_to(B).as_posix(),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest()))
assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized();out=dict(epoch=time.time(),passed_target_CPU_only=True,source_all_finite_tensor_counts=count,source_Adam639560=True,all_target_files=rows,no_native_or_PPO_claim=True);(B/'TARGET_COMPLETE_SOURCE_CPU_ACTUAL.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
'''
def main():
 assert json.loads((R/'E3_GPU1_FINITE_RESOURCE_LOCK_NEGATIVES_CPU_ACTUAL.json').read_bytes())['passed_CPU_only'];put('E3_FINITE_TRANSPORT_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),only_actual_alive_exclusive_210_72_249_transport=True,no_E3_learning_or_canonical_write=True));pw=getpass.getpass('Host72 E3 legal pose admission password (hidden): ');c=sf=None
 try:
  c=connect72(pw);pw=None;put('E3_NEW_SCOPE_SOURCE_REUSE_ACTUAL.json',code(c,PY,CREATE,ROOT,BASE));files=[];sf=c.open_sftp();sf.get_channel().settimeout(120)
  for p in sorted(E.glob('*.py')):sf.put(str(p),ROOT+'/'+p.name);files.append(dict(relative=p.name,bytes=p.stat().st_size,SHA=H(p)))
  manifest=E/'OWN_E3_FILES_CPU_MANIFEST.json';manifest.write_text(json.dumps(dict(epoch=time.time(),files=files),indent=2),encoding='utf8');sf.put(str(manifest),ROOT+'/'+manifest.name);sf.close();sf=None;cpu=code(c,PY,VERIFY,ROOT,timeout=150);put('E3_ALL_TARGET_SOURCE_CPU_ACTUAL.json',cpu);launch="from pathlib import Path;import subprocess,json,sys;B=Path(sys.argv[1]);p=subprocess.run([sys.argv[2],'-u','-B',str(B/'e3_gpu1_pose_contact_finite_parent_v1.py')],cwd=B,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=30);assert p.returncode==0,p.stderr.decode('utf8','replace');print(p.stdout.decode().strip())";v=code(c,PY,launch,ROOT,PY);put('E3_LEGAL_POSE_CONTACT_ACTUAL_DETACHED_DISPATCH.json',dict(epoch=time.time(),launch=v,CPU_target_passed=True,native_not_yet_passed=True,no_PPO_or_canonical_change=True));print(json.dumps(dict(new_E3_finite_parent=v,no_PPO=True)),flush=True)
 finally:
  pw=None
  if sf:sf.close()
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('E3_NEW_DEPLOY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_blind_redeploy_or_native_replay=True));raise
