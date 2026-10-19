"""One missing-only resource snapshot after the original finite actually returned; never launch or touch a peer."""
from pathlib import Path
import getpass,json,os,sys,time,traceback
import deploy_three_next_closed_source_hours_once as d
B=Path(__file__).resolve().parent;R=B/'reports'
CODE=r'''
from pathlib import Path
import sys,json,time,psutil,fcntl,shutil,subprocess,os
specs=json.loads(sys.argv[1]);rows={};locks=[];owned=Path('/home/lc01/Zonglin Li/zonglin2')
for key in ('h1','recovery'):
 s=specs[key];root=Path(s['previous_runtime_root']);t=json.loads((root/'NODE_TERMINAL_ACTUAL.json').read_bytes())['row'];e=json.loads((root/'NODE_EXIT_ACTUAL.json').read_bytes());own=[]
 for p in psutil.process_iter(['pid','create_time','cmdline']):
  try:
   if p.pid!=os.getpid() and any(x.startswith(str(root)+'/') for x in p.info['cmdline'] or []):own.append(p.info)
  except psutil.Error:pass
 rows[key]=dict(root=str(root),actual_own_processes=own,previous_final_SHA=t['final']['final']['SHA'],matches_complete_source=t['final']['final']['SHA']==s['source_SHA'],actual_closed=bool(t['returncode']==0 and not t['errors'] and t['final']['passed'] and t['terminal_all_own_children_waited'] and e['actual_all_own_children_waited'] and e['validation_fcntl_released_if_acquired'] and not own))
for q in dict.fromkeys([specs[k]['private_lock'] for k in ('h1','recovery')]+[str(owned/'state/finite_environment_validation.lock')]):
 free=False
 with Path(q).open('rb+') as f:
  try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);free=True;fcntl.flock(f,fcntl.LOCK_UN)
  except BlockingIOError:pass
 locks.append(dict(path=q,actual_fcntl_free=free))
compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']).decode();disk=shutil.disk_usage(owned).free;ram=psutil.virtual_memory().available
empty={k:not any(specs[k]['GPU_UUID'] in line for line in compute.splitlines()) for k in ('h1','recovery')}
nonGPU=bool(all(x['actual_closed'] and x['matches_complete_source'] for x in rows.values()) and all(x['actual_fcntl_free'] for x in locks) and disk>25*1024**3 and ram>8*1024**3)
print(json.dumps(dict(epoch=time.time(),previous_nodes=rows,actual_locks=locks,compute_snapshot=compute,target_GPU_empty=empty,durable_free_bytes=disk,RAM_available_bytes=ram,non_GPU_original_admission_ready=nonGPU,target_admission_snapshot_ready=bool(nonGPU and all(empty.values())),no_peer_identity_or_workload_inference=True,no_process_signal_lock_delete_PT_or_account_write=True)))
'''
def put(name,value):
 with (R/name).open('x',encoding='utf8') as stream:json.dump(value,stream,indent=2)
def main():
 assert not (R/'TENTH_TARGET_MISSING_RESOURCE_SNAPSHOT_V2_STARTED_ACTUAL.json').exists()
 p=json.loads((R/'THREE_NEXT_CLOSED_SOURCES_ONE_HOUR_CPU_PREPARED_ACTUAL.json').read_bytes());assert p['passed']
 put('TENTH_TARGET_MISSING_RESOURCE_SNAPSHOT_V2_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,limit_seconds=0,single_72_connection_only=True,append_only_observations=True,no_second_watcher=True))
 pw=getpass.getpass('72 missing target admission only (hidden): ');c=None;start=time.monotonic();count=0;last=None
 try:
  c=d.a.connect72(pw);pw=None;c.get_transport().set_keepalive(15)
  while True:
   last=d.a.code(c,d.a.PY,CODE,json.dumps(p['specs']),timeout=60);count+=1
   with (R/'TENTH_TARGET_MISSING_RESOURCE_SNAPSHOT_V2_OBSERVATIONS.jsonl').open('a',encoding='utf8') as stream:stream.write(json.dumps(last)+'\n');stream.flush();os.fsync(stream.fileno())
   if last['target_admission_snapshot_ready'] or not last['non_GPU_original_admission_ready'] or time.monotonic()-start>=0:break
   time.sleep(min(30,max(0,0-(time.monotonic()-start))))
 finally:
  pw=None
  if c:c.close()
 out=dict(epoch=time.time(),observations=count,last=last,actual_finite_transport_returned=True,target_snapshot_ready=last['target_admission_snapshot_ready'],no_deployment_owner_node_worker_GO_or_budget_change=True,not_a_permanent_GPU_free_or_peer_liveness_claim=True)
 put('TENTH_TARGET_MISSING_RESOURCE_SNAPSHOT_V2_RETURNED_ACTUAL.json',out);print(json.dumps(out),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  put('TENTH_TARGET_MISSING_RESOURCE_SNAPSHOT_V2_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),previous_observations_retained=True,no_automatic_retry_or_peer_interference=True));raise
