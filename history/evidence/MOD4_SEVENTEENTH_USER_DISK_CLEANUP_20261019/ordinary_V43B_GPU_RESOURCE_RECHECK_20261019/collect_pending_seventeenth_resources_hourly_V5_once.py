"""One missing resource/root snapshot after a consumed preinstall-only rejection."""
from pathlib import Path
import getpass,json,os,sys,time,traceback
B=Path(__file__).resolve().parent;R=B/'reports';Q=B.parent/'MOD4_SCUT_FUDAN_SEVENTEENTH_HOUR_20261019'
sys.path.insert(0,str(Q));import deploy_three_next_closed_source_hours_once as d
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
READ=r'''
from pathlib import Path
import fcntl,json,psutil,shutil,subprocess,sys,time
B=Path('/home/lc01/Zonglin Li/zonglin2');v=json.loads(sys.argv[1]);specs=v['specs'];locks=[];roots={}
for k in ('h1','recovery'):
 p=Path(v['roots'][k]);assert p.resolve().is_relative_to(B/'tasks')
 roots[k]=dict(path=str(p),exists=p.exists(),production_exists=(p/'job0/production').exists(),rows={q.name:json.loads(q.read_bytes()) for q in [p/'NODE_CURRENT.json',p/'NODE_ORIGINAL_ERROR.json',p/'NODE_EXIT_ACTUAL.json',p/'GO_PRODUCTION.json'] if q.is_file()})
for name in [specs[k]['private_lock'] for k in ('h1','recovery')]+[str(B/'state/finite_environment_validation.lock')]:
 p=Path(name);free=False
 with p.open('rb+') as f:
  try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);free=True;fcntl.flock(f,fcntl.LOCK_UN)
  except BlockingIOError:pass
 locks.append(dict(path=str(p),actual_fcntl_free=free))
compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']).decode();gpu=subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits']).decode();memory={x.split(',')[0].strip():int(x.split(',')[-1]) for x in gpu.splitlines()};disk=shutil.disk_usage(B);ram=psutil.virtual_memory().available
checks=dict(original_disk_over25GiB=disk.free>25*1024**3,original_RAM_over8GiB=ram>8*1024**3,H1_original_GPU_free_over7000MiB=memory[specs['h1']['GPU_UUID']]>7000,E3_original_GPU_free_over7000MiB=memory[specs['recovery']['GPU_UUID']]>7000,E3_original_GPU_empty=not any(specs['recovery']['GPU_UUID'] in x for x in compute.splitlines()),original_private_shared_locks_free=all(x['actual_fcntl_free'] for x in locks),new_target_roots_still_unused=all(not x['exists'] for x in roots.values()))
assert specs['h1']['human_explicit_GPU_sharing'] is True
print(json.dumps(dict(epoch=time.time(),checks=checks,ready_for_unused_deployer_resource_checks=all(checks.values()),GPU_free_MiB=memory,compute_snapshot=compute,available_RAM_bytes=ram,durable=dict(zip(('total','used','free'),disk)),original_locks=locks,actual_target_roots=roots,H1_explicit_sharing_retained=True,no_peer_identity_query_no_GPU_Task_model_hash_or_account_write=True)))
'''
def main():
 assert not (R/'HOURLY_V5_RESOURCE_READER_STARTED_ACTUAL.json').exists()
 assert list((Q/'reports').glob('THREE_NEXT_HOUR_DEPLOY_ORIGINAL_ERROR_*.json')) and not (Q/'reports/THREE_NEXT_HOUR_CLOSED_SOURCE_LEARNING_DETACHED_ACTUAL.json').exists()
 v=json.loads((Q/'reports/THREE_NEXT_CLOSED_SOURCES_ONE_HOUR_CPU_PREPARED_ACTUAL.json').read_bytes())
 put('HOURLY_V5_RESOURCE_READER_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,actual_alive_finite_only_exclusive_all_transport=True,reason='First deployer failed before any target install/GO; read only missing resource and unused-root facts. Old capacityV3 refused locally because its no-deploy-start guard is now stale; no SSH from that refusal.'))
 pw=getpass.getpass('72 missing resources after preinstall rejection (hidden): ');c=None
 try:c=d.a.connect72(pw);pw=None;c.get_transport().set_keepalive(15);out=d.a.code(c,d.a.PY,READ,json.dumps(v),timeout=60)
 finally:
  pw=None
  if c:c.close()
 out['actual_finite_transport_returned']=True;put('HOURLY_V5_RESOURCE_AND_UNUSED_ROOTS_ACTUAL.json',out);print(json.dumps(out),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:put('HOURLY_V5_RESOURCE_READER_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_deployer_GPU_or_Task_replay=True));raise
