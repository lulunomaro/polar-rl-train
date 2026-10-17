"""One source then one72 read of only the missing complete H1 final and original handoff."""
from pathlib import Path
import os,sys,time,json,getpass,traceback,importlib.util
B=Path(__file__).resolve().parent;R=B/'reports';R.mkdir(exist_ok=True);W=B.parent.parent;O=W/'MOD4_H1_CLOSED24_TARGET72_SAME_SCOPE_FINITE_20261017';M=W/'MOD4_RECOVERY_CLOSED_FINAL_H1_STORAGE_BOUNDED_HANDOFF_20261017';sys.path[:0]=[str(B),str(M)]
from deploy_parallel_d723_H1_new_finite_strict_native_reuse_once import a,SOURCE,TARGET
from collect_new_H1_bounded_native_first_and_recovery85_native_only_finite_once import SNAP
G=W/'MOD4_TWO72_CLOSED_SOURCES_HEALTHY_NEXT_BLOCK_20261017';sys.path.insert(0,str(G));sp=importlib.util.spec_from_file_location('existing_original_account_functions_only_parallel_d723',G/'collect_existing_v5_actual_terminal_original_handoff_bounded_missing_final_only_once.py');f=importlib.util.module_from_spec(sp);sp.loader.exec_module(f)
def save(n,v):
 with (R/n).open('x',encoding='utf8') as h:json.dump(v,h,indent=2)
HASH=r'''
from pathlib import Path
import sys,os,json,hashlib
p=Path(sys.argv[1]);h=hashlib.sha256()
with p.open('rb') as f:
 s=os.fstat(f.fileno())
 for z in iter(lambda:f.read(4194304),b''):h.update(z)
 e=os.fstat(f.fileno());assert(s.st_size,s.st_mtime_ns)==(e.st_size,e.st_mtime_ns)
print(json.dumps(dict(path=str(p),bytes=s.st_size,SHA=h.hexdigest())))
'''
RES=r'''
from pathlib import Path
import sys,json,time,shutil,subprocess,fcntl
source=sys.argv[1]=='source';base=Path('/mnt/mod4_linux_durable_20261013' if source else '/home/lc01/Zonglin Li/zonglin2');locks=[]
if not source:
 for p in (base/'state/three_expert_v2_GPU-16828f91-2b45-b646-8dc0-9481138e2842.lock',base/'state/finite_environment_validation.lock'):
  free=False
  with p.open('rb+') as f:
   try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);free=True;fcntl.flock(f,fcntl.LOCK_UN)
   except BlockingIOError:pass
  locks.append(dict(path=str(p),actual_fcntl_free=free))
print(json.dumps(dict(epoch=time.time(),durable=dict(zip(('total','used','free'),shutil.disk_usage(base))),actual_target_private_shared_validation_locks=locks,gpu=subprocess.check_output(['nvidia-smi','--query-gpu=index,uuid,utilization.gpu,memory.used,memory.total','--format=csv,noheader,nounits']).decode(),compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']).decode())))
'''
def main():
 save('TARGET72_H1_CLOSING_parallel_d723_READER_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),actual_alive_only_exclusive_all_host_transport=True,one_source_then_one_target_bounded_no_poll=True,no_GPU_Task_native_budget_or_complete_old_PT_replay=True));pw=getpass.getpass('Host72 existing H1 final only (hidden): ');c=None;v={};models=[]
 try:c=a.t.connect();v['owner']=a.code(c,a.t.PY,SNAP,SOURCE,'metadata',timeout=90);v['account']=a.code(c,a.t.PY,f.ACCOUNT,timeout=90);v['source_resources']=a.code(c,a.t.PY,RES,'source',timeout=45)
 finally:a.t.close(c);c=None
 try:
  c=a.connect72(pw);pw=None;v['h1']=a.code(c,a.PY,SNAP,TARGET,'metadata',timeout=90);v['target_resources']=a.code(c,a.PY,RES,'target',timeout=45);final=next((x['value'] for x in v['h1']['files'] if x['path'].endswith('/job0/production/FINAL.json')),None)
  if final:
   row=a.code(c,a.PY,HASH,final['final']['path'],timeout=90);p=B/'actual_closed_H1_final'/Path(row['path']).name;p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists();part=p.with_suffix('.pt.partial');assert not part.exists();sf=c.open_sftp();sf.get_channel().settimeout(120)
   try:sf.get(row['path'],str(part))
   finally:sf.close()
   assert part.stat().st_size==row['bytes'] and a.H(part)==row['SHA'];part.replace(p);models.append(dict(row,local_path=str(p),twohost_complete_SHA=True))
 finally:
  pw=None
  if c:c.close()
 done=next((x['value'] for x in v['owner']['files'] if x['path'].endswith('/COHORT_FINAL.json')),None);v.update(epoch=time.time(),downloaded_final_models=models,actual_return_hands_all_transport_back=True,no_old_native_first_PT_or_raw_hash_or_download=True,actual_closed=bool(done and models and not v['owner']['actual_own_processes'] and not v['h1']['actual_own_processes'] and v['account']['original_canonical']['active_segment'] is None and all(x['actual_fcntl_free'] for x in v['account']['actual_locks']) and all(x['actual_fcntl_free'] for x in v['target_resources']['actual_target_private_shared_validation_locks'])))
 save('PARALLEL_D723_H1_FINAL_ORIGINAL_COST_EXIT_BOUND_COLLECTION_ACTUAL.json',v);print(json.dumps(dict(actual_closed=v['actual_closed'],models=models,canonical_active=v['account']['original_canonical']['active_segment'],source_free=v['source_resources']['durable']['free'],target_free=v['target_resources']['durable']['free'],source_compute=v['source_resources']['compute'],target_compute=v['target_resources']['compute'])),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:save('TARGET72_H1_FINAL_parallel_d723_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),unknown_outcome_no_GPU_replay=True));raise
