from pathlib import Path
import os,sys,json,time,getpass,traceback
D=Path(__file__).resolve().parent;R=D/'reports';sys.path.insert(0,str(D));from deploy_V7_three_experts_corrected_E3_admission_finite_once import ROOTS,code,H,connect72,t,PY
from collect_first_two_native_and_E2_handoff_actual_readonly_once import READ
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
CANON=r'''
from pathlib import Path
import json,time,fcntl,subprocess,psutil
C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');v=json.loads(C.read_bytes());locks=[]
for p in (C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with p.open('rb+') as f:
  try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:held=True
  else:held=False;fcntl.flock(f,fcntl.LOCK_UN)
 locks.append(dict(path=str(p),actual_held=held))
print(json.dumps(dict(epoch=time.time(),active=v['active_segment'],authorized=v['authorized_training_seconds'],charged=v['charged_training_seconds'],remaining=v['remaining_training_seconds'],extensions=len(v['budget_extensions']),last_completed=v['completed_segments'][-1],actual_two_fcntl=locks,GPU_snapshot=subprocess.check_output(['nvidia-smi','--query-gpu=uuid,utilization.gpu,memory.free','--format=csv,noheader,nounits']).decode(),compute_snapshot=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']).decode(),RAM_available=psutil.virtual_memory().available)))
'''
FINALS=r'''
from pathlib import Path
import json,time,sys,hashlib
B=Path(sys.argv[1]);O=B/'job0'/('production_only' if sys.argv[2]=='curb' else 'production');p=O/'FINAL.json';v=json.loads(p.read_bytes()) if p.exists() else None;row=None
if v and v.get('passed'):
 row=v['final'];q=Path(row['path']);assert q.is_relative_to(O) and q.stat().st_size==row['bytes'] and hashlib.sha256(q.read_bytes()).hexdigest()==row['SHA']
print(json.dumps(dict(epoch=time.time(),final=v,complete_model=row)))
'''
def collect(c,py,key):
 v=code(c,py,READ,ROOTS[key],key);row=code(c,py,FINALS,ROOTS[key],key);v['final_model']=None
 if row['complete_model']:
  row=row['complete_model'];folder=D/'actual_hourly2223_V7_final_models';folder.mkdir(exist_ok=True);p=folder/(key+'_final.pt');tmp=p.with_suffix('.pt.partial');assert not p.exists() and not tmp.exists();sf=c.open_sftp();sf.get_channel().settimeout(120)
  try:sf.get(row['path'],str(tmp));assert tmp.stat().st_size==row['bytes'] and H(tmp)==row['SHA'];tmp.replace(p)
  finally:sf.close()
  v['final_model']=dict(**row,local_path=str(p),twohost_complete_bytes_SHA_exact=True)
 return v
def main():
 put('HOURLY2223_V7_FINITE_READONLY_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),actual_alive_only_exclusive_transport_owner=True,one_sequential_source_then_target_connection_no_runtime_mutation=True));pw=getpass.getpass('Host72 current V7 finals read only (hidden): ');c=None;v={}
 try:c=t.connect();v['curb']=collect(c,t.PY,'curb');v['canonical']=code(c,t.PY,CANON)
 finally:t.close(c);c=None
 try:
  c=connect72(pw);pw=None
  for key in ('e2','recovery'):v[key]=collect(c,PY,key)
  v['target_resources']=code(c,PY,"import json,time,subprocess,psutil;print(json.dumps(dict(epoch=time.time(),GPU_snapshot=subprocess.check_output(['nvidia-smi','--query-gpu=uuid,utilization.gpu,memory.free','--format=csv,noheader,nounits']).decode(),compute_snapshot=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']).decode(),RAM_available=psutil.virtual_memory().available)))")
 finally:
  pw=None
  if c:c.close()
 v['epoch']=time.time();put('HOURLY2223_V7_THREE_ACTUAL_FINAL_MODELS_COST_EXIT_RESOURCES_READONLY_ACTUAL.json',v);print(json.dumps(dict(epoch=v['epoch'],finals={k:v[k]['final_model'] for k in ROOTS},processes={k:v[k]['actual_own_processes'] for k in ROOTS},canonical=v['canonical'],target_resources=v['target_resources'])),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:put('HOURLY2223_V7_READONLY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),unknown_runtime_not_relaunched=True));raise
