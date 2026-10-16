"""One hourly bounded existing-root collection, only missing immutable artifacts."""
from pathlib import Path
import os,time,json,getpass,traceback
F=Path(__file__).resolve().parent;R=F/'reports'
from collect_two72_new_native_first_models_existing_chain_finite_once import a,READ,SOURCE,ROOTS
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
LOCK_READ=r'''
from pathlib import Path
import os,json,time,fcntl,psutil,shutil
B=Path('/mnt/mod4_linux_durable_20261013/T3_1710v3r72/owner');C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');v=json.loads(C.read_bytes());locks=[]
for path in (C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 held=False
 with path.open('rb+') as f:
  try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
  except BlockingIOError:held=True
 st=path.stat();lines=[s for s in Path('/proc/locks').read_text().splitlines() if (format(os.major(st.st_dev),'02x')+':'+format(os.minor(st.st_dev),'02x')+':'+str(st.st_ino)) in s];locks.append(dict(path=str(path),actual_held=held,device=st.st_dev,inode=st.st_ino,actual_proc_lock_lines=lines))
print(json.dumps(dict(epoch=time.time(),canonical_authorized=v['authorized_training_seconds'],extensions=len(v['budget_extensions']),charged=v['charged_training_seconds'],remaining=v['remaining_training_seconds'],active=v['active_segment'],locks=locks,source_durable_free=shutil.disk_usage('/mnt/mod4_linux_durable_20261013').free,readonly_no_budget_process_signal_or_training_mutation=True)))
'''
def get(c,row,key):
 models=[];folder=F/'actual_safe72_first_models'/key
 if row['models']:folder.mkdir(parents=True,exist_ok=True)
 sf=c.open_sftp();sf.get_channel().settimeout(120)
 try:
  for r in row['models']:
   p=folder/Path(r['path']).name
   if p.exists():assert p.stat().st_size==r['bytes'] and a.H(p)==r['SHA'];models.append(dict(r,local_path=str(p),twohost_complete_SHA=True,existing_complete_not_downloaded_again=True));continue
   tmp=p.with_suffix('.pt.partial');assert not tmp.exists();sf.get(r['path'],str(tmp));assert tmp.stat().st_size==r['bytes'] and a.H(tmp)==r['SHA'];tmp.replace(p);models.append(dict(r,local_path=str(p),twohost_complete_SHA=True))
 finally:sf.close()
 return models
def main():
 put('HOURLY0610_EXISTING_TWO72_READONLY_COLLECTOR_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),actual_alive_only_exclusive_transport=True,one_source_then_one_target_connection_no_poll=True));pw=getpass.getpass('Host72 existing immutable models only (hidden): ');c=None;v={};models={}
 try:c=a.t.connect();v['owner']=a.code(c,a.t.PY,READ,SOURCE,'owner');v['original_owner_actual_canonical_locks']=a.code(c,a.t.PY,LOCK_READ)
 finally:a.t.close(c);c=None
 try:
  c=a.connect72(pw);pw=None
  for key in ROOTS:v[key]=a.code(c,a.PY,READ,ROOTS[key],key);models[key]=get(c,v[key],key)
 finally:
  pw=None
  if c:c.close()
 v.update(epoch=time.time(),downloaded_models=models,H1_preGO_resource_rejected_no_training=True,readonly_existing_scopes_no_GPU_or_budget_mutation=True);put('SAFE72_HOURLY0610_EXISTING_SCOPE_MISSING_MODELS_ORIGINAL_OWNER_BOUND_COLLECTION_ACTUAL.json',v);print(json.dumps(dict(epoch=v['epoch'],models=models,errors={k:[x for x in v[k]['files'] if 'ORIGINAL_ERROR' in x['path']] for k in ROOTS},original=dict(active_owner=(v['original_owner_actual_canonical_locks']['active'] or {}).get('owner_parent_pid'),source_durable_free=v['original_owner_actual_canonical_locks']['source_durable_free'],locks=v['original_owner_actual_canonical_locks']['locks']))),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:put('HOURLY0610_EXISTING_TWO72_COLLECTION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_once_replay=True));raise
