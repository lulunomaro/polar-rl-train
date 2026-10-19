"""Prepared finite capacity snapshot only; no model/hash/Task/GO or account writes."""
from pathlib import Path
import getpass,json,os,sys,time,traceback
import deploy_three_next_closed_source_hours_once as d
B=Path(__file__).resolve().parent;R=B/'reports';ID=Path(__file__).stem
def put(s,v):
 with (R/(ID+'_'+s+'.json')).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
READ=r'''
from pathlib import Path
import json,shutil,sys,time,psutil,subprocess,fcntl
B=Path('/home/lc01/Zonglin Li/zonglin2');specs=json.loads(sys.argv[1]);locks=[]
for name in [specs[k]['private_lock'] for k in ('h1','recovery')]+[str(B/'state/finite_environment_validation.lock')]:
 p=Path(name);free=False
 with p.open('rb+') as f:
  try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);free=True;fcntl.flock(f,fcntl.LOCK_UN)
  except BlockingIOError:pass
 locks.append(dict(path=str(p),actual_fcntl_free=free))
compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']).decode()
gpu=subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits']).decode()
memory={line.split(',')[0].strip():int(line.split(',')[-1]) for line in gpu.splitlines()}
disk=shutil.disk_usage(B);ram=psutil.virtual_memory().available
ready=disk.free>25*1024**3 and ram>8*1024**3 and all(x['actual_fcntl_free'] for x in locks) and all(memory[specs[k]['GPU_UUID']]>7000 for k in ('h1','recovery')) and not any(specs['recovery']['GPU_UUID'] in line for line in compute.splitlines())
assert specs['h1']['human_explicit_GPU_sharing'] is True
print(json.dumps(dict(epoch=time.time(),durable=dict(zip(('total','used','free'),disk)),available_RAM_bytes=ram,actual_locks=locks,compute_snapshot=compute,GPU_free_MiB_snapshot=memory,H1_explicit_sharing_retained=True,ready_for_prepared_deployer_resource_checks=bool(ready),source210_and_canonical_must_be_rechecked_by_original_deployer=True,no_other_process_identity_query_or_interference=True,read_only_no_old_PT_raw_hash_download_GPU_Task_or_account_write=True)))
'''
def main():
 assert not (R/(ID+'_STARTED_ACTUAL.json')).exists()
 assert not (R/'THREE_NEXT_HOUR_DEPLOY_STARTED_ACTUAL.json').exists()
 p=json.loads((R/'THREE_NEXT_CLOSED_SOURCES_ONE_HOUR_CPU_PREPARED_ACTUAL.json').read_bytes());assert p['passed']
 put('STARTED_ACTUAL',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,only_actual_alive_finite_owns_all_transport=True,single72_connection_only_capacity_snapshot_no_poll=True))
 pw=getpass.getpass('72 pending capacity snapshot only (hidden): ');c=None
 try:
  c=d.a.connect72(pw);pw=None;c.get_transport().set_keepalive(15)
  out=d.a.code(c,d.a.PY,READ,json.dumps(p['specs']),timeout=60)
 finally:
  pw=None
  if c:c.close()
 out['actual_finite_transport_returned']=True;put('RETURNED_ACTUAL',out)
 print(json.dumps(dict(ready=out['ready_for_prepared_deployer_resource_checks'],free_bytes=out['durable']['free'],only_capacity_checked=True)))
if __name__=='__main__':
 try:main()
 except BaseException:put('ORIGINAL_ERROR',dict(epoch=time.time(),error=traceback.format_exc(),no_automatic_GPU_Task_retry_or_account_change=True));raise
