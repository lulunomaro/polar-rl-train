from pathlib import Path
import sys,os,json,time,getpass,traceback
P=Path(__file__).resolve().parent;D=P.parent/'MOD4_THREE4090_CURB_DIRECTION_AND_E3_RECOVERY_20261016';R=P/'reports';sys.path.insert(0,str(D))
from deploy_V9_actual_CPU_status_fix_E2_E3_CURB_deferred_once import ROOTS,code,H,connect72,t,PY
SNAP=r'''
from pathlib import Path
import sys,json,time,hashlib,psutil
B=Path(sys.argv[1]);key=sys.argv[2];O=B/'job0'/('production_only' if key=='curb' else 'production');files=[];names=['OWNER_IDENTITY.json','OWNER_CURRENT.json','COHORT_FINAL.json','OWNER_EXIT_ACTUAL.json','OWNER_ORIGINAL_ERROR.json','NODE_IDENTITY.json','NODE_CURRENT.json','NODE_EXIT_ACTUAL.json','NODE_ORIGINAL_ERROR.json','PARENT_IDENTITY.json','PARENT_CURRENT.json','PARENT_FINAL.json','PARENT_ORIGINAL_ERROR.json','PARENT_EXIT_ACTUAL.json','GO_PRODUCTION_ACTUAL.json','job0/GO_PRODUCTION.json','job0/production_WAITED_EXIT_ACTUAL.json']
for rel in names+['job0/'+O.name+'/'+n for n in ('FINAL.json','latest_complete.json','WORKER_ORIGINAL_ERROR_BEFORE_APP_CLOSE.json','WORKER_ORIGINAL_ERROR.json','PPO_POSITIVE_CURRENT.json')]:
 p=B/rel
 if p.is_file():
  raw=p.read_bytes();files.append(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),value=json.loads(raw) if len(raw)<1000000 else None,large_raw_index_only=len(raw)>=1000000))
procs=[]
for p in psutil.process_iter(['pid','create_time','cmdline','cwd']):
 try:
  if any(str(B)+'/' in x for x in p.info['cmdline'] or []):procs.append(p.info)
 except psutil.Error:pass
models=[]
for name in (('model_update1.pt','own_fresh_startup0.pt') if key=='curb' else ()):
 p=O/name
 if p.is_file():models.append(dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest(),kind='immutable_'+name))
q=O/'FINAL.json'
if q.exists():
 v=json.loads(q.read_bytes());row=v.get('final')
 if row:
  p=Path(row['path']);assert p.is_relative_to(O) and p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['SHA'];models.append(dict(row,kind='actual_final'))
print(json.dumps(dict(epoch=time.time(),root=str(B),key=key,files=files,actual_own_processes=procs,models=models,readonly=True)))
'''
CANON=r'''
from pathlib import Path
import time,json,fcntl,subprocess,psutil
C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');c=json.loads(C.read_bytes());locks=[]
for p in (C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with p.open('rb+') as f:
  try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:held=True
  else:held=False;fcntl.flock(f,fcntl.LOCK_UN)
 locks.append(dict(path=str(p),actual_held=held))
def trim(v):
 if v is None:return None
 return {k:x for k,x in v.items() if k!='actual_terminal_rows'}
last=[trim(s) for s in c['completed_segments'] if s.get('owner_parent_pid') in (576492,581261)];print(json.dumps(dict(epoch=time.time(),active=trim(c['active_segment']),actual_two_fcntl=locks,authorized=c['authorized_training_seconds'],charged=c['charged_training_seconds'],remaining=c['remaining_training_seconds'],extensions=len(c['budget_extensions']),selected_completed=last,GPU_snapshot=subprocess.check_output(['nvidia-smi','--query-gpu=uuid,utilization.gpu,memory.free','--format=csv,noheader,nounits']).decode(),compute_snapshot=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']).decode(),RAM_available=psutil.virtual_memory().available)))
'''
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def collect(c,py,root,key):
 v=code(c,py,SNAP,root,key);v['downloaded_models']=[];folder=P/'actual_hourly0044_models'/key;folder.mkdir(parents=True);sf=c.open_sftp();sf.get_channel().settimeout(120)
 try:
  for row in v['models']:
   p=folder/Path(row['path']).name;q=p.with_suffix('.pt.partial');assert not p.exists() and not q.exists();sf.get(row['path'],str(q));assert q.stat().st_size==row['bytes'] and H(q)==row['SHA'];q.replace(p);v['downloaded_models'].append(dict(row,local_path=str(p),twohost_complete_SHA=True))
 finally:sf.close()
 return v
def main():
 put('HOURLY0044_FINITE_OWN_SCOPE_READONLY_STARTED.json',dict(epoch=time.time(),pid=os.getpid(),actual_alive_only_exclusive_transport=True,readonly_no_new_GPU_or_accounting_or_lock_mutation=True));pw=getpass.getpass('Host72 existing V9 final artifacts read only (hidden): ');c=None;v={}
 try:
  c=t.connect();v['V9_owner']=code(c,t.PY,SNAP,ROOTS['curb'],'curb');v['curb']=collect(c,t.PY,'/mnt/mod4_linux_durable_20261013/C275_1610v2','curb');v['canonical']=code(c,t.PY,CANON)
 finally:t.close(c);c=None
 try:
  c=connect72(pw);pw=None
  for key in ('e2','recovery'):v[key]=collect(c,PY,ROOTS[key],key)
  v['target_resources']=code(c,PY,"import time,json,subprocess,psutil;print(json.dumps(dict(epoch=time.time(),GPU_snapshot=subprocess.check_output(['nvidia-smi','--query-gpu=uuid,utilization.gpu,memory.free','--format=csv,noheader,nounits']).decode(),compute_snapshot=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']).decode(),RAM_available=psutil.virtual_memory().available)))")
 finally:
  pw=None
  if c:c.close()
 v['epoch']=time.time();put('HOURLY0044_V9_ACTUAL_FINALS_CURB275_PRODUCTION_OR_ERROR_COST_EXIT_READONLY.json',v)
 for k in ('curb','e2','recovery'):print(json.dumps(dict(key=k,epoch=v[k]['epoch'],models=v[k]['downloaded_models'],processes=v[k]['actual_own_processes'],errors=[r for r in v[k]['files'] if 'ORIGINAL_ERROR' in r['path']])),flush=True)
 print(json.dumps(dict(canonical=v['canonical'],target_resources=v['target_resources'])),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:put('HOURLY0044_ORIGINAL_READONLY_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),unknown_runtime_not_relaunched=True));raise
