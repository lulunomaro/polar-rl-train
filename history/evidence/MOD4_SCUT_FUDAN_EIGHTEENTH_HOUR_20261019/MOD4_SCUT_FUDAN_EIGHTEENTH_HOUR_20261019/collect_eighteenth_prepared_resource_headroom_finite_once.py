"""One bounded resource admission snapshot, no install or GPU task."""
from pathlib import Path
import getpass,json,os,sys,time,traceback
import deploy_three_next_closed_source_hours_once as d
B=Path(__file__).resolve().parent;R=B/'reports'
READ=r'''
from pathlib import Path
import fcntl,json,psutil,shutil,subprocess,sys,time
base=Path('/home/lc01/Zonglin Li/zonglin2');v=json.loads(sys.argv[1]);spec=v['specs'];roots={};locks=[]
for key in ('h1','recovery'):
 p=Path(v['roots'][key]);assert p.resolve().is_relative_to(base/'tasks');roots[key]=dict(path=str(p),exists=p.exists())
for name in [spec[k]['private_lock'] for k in ('h1','recovery')]+[str(base/'state/finite_environment_validation.lock')]:
 with Path(name).open('rb+') as f:
  free=False
  try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);free=True;fcntl.flock(f,fcntl.LOCK_UN)
  except BlockingIOError:pass
  locks.append(dict(path=name,actual_fcntl_free=free))
compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']).decode();gpu=subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits']).decode();memory={x.split(',')[0].strip():int(x.split(',')[-1]) for x in gpu.splitlines()};disk=shutil.disk_usage(base);ram=psutil.virtual_memory().available;floor=spec['h1']['H1_empirical_start_free_MiB'];assert floor==15669 and spec['h1']['human_explicit_GPU_sharing'] is True
checks=dict(original_disk_over25GiB=disk.free>25*1024**3,original_RAM_over8GiB=ram>8*1024**3,H1_original_GPU_free_over7000MiB=memory[spec['h1']['GPU_UUID']]>7000,H1_additional_empirical_free_at_least15669MiB=memory[spec['h1']['GPU_UUID']]>=floor,E3_original_GPU_free_over7000MiB=memory[spec['recovery']['GPU_UUID']]>7000,E3_original_GPU_empty=not any(spec['recovery']['GPU_UUID'] in x for x in compute.splitlines()),original_private_shared_locks_free=all(x['actual_fcntl_free'] for x in locks),new_target_roots_still_unused=all(not x['exists'] for x in roots.values()))
print(json.dumps(dict(epoch=time.time(),checks=checks,ready_for_unused_deployer_resource_checks=all(checks.values()),GPU_free_MiB=memory,compute_snapshot=compute,available_RAM_bytes=ram,durable=dict(zip(('total','used','free'),disk)),original_locks=locks,actual_target_roots=roots,H1_human_sharing_and_original_guards_preserved=True,added_headroom_from_previous_healthy_snapshot_not_an_OOM_guarantee=True,no_peer_identity_query_or_GPU_Task_PT_hash_or_account_write=True)))
'''
def main():
 assert not (R/'EIGHTEENTH_RESOURCE_READER_STARTED_ACTUAL.json').exists() and not (R/'THREE_NEXT_HOUR_DEPLOY_STARTED_ACTUAL.json').exists()
 p=json.loads((R/'THREE_NEXT_CLOSED_SOURCES_ONE_HOUR_CPU_PREPARED_ACTUAL.json').read_bytes());assert p['passed'] and p['specs']['h1']['H1_empirical_start_free_MiB']==15669
 d.put('EIGHTEENTH_RESOURCE_READER_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,actual_finite_alive_only_exclusive_all_transports=True,no_install_or_GPU_or_account_write=True));pw=getpass.getpass('72 next-hour original and empirical headroom resources (hidden): ');c=None
 try:c=d.a.connect72(pw);pw=None;c.get_transport().set_keepalive(15);out=d.a.code(c,d.a.PY,READ,json.dumps(p),timeout=60)
 finally:
  pw=None
  if c:c.close()
 out['actual_finite_transport_returned']=True;d.put('EIGHTEENTH_PREPARED_RESOURCES_AND_EMPIRICAL_H1_HEADROOM_ACTUAL.json',out);print(json.dumps(out),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:d.put('EIGHTEENTH_RESOURCE_READER_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_replay_or_deployment=True));raise
