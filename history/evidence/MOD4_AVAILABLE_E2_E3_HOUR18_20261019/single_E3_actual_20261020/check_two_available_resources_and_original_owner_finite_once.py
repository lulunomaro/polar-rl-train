"""One finite read-only preflight for the two explicitly scheduled GPUs."""
from pathlib import Path
import getpass,json,os,sys,time,traceback
import deploy_available_E2_E3_original_writer_V2_once as d
B=d.B;R=d.R
READ=r'''
from pathlib import Path
import json,sys,time,psutil,fcntl,shutil,subprocess
v=json.loads(sys.argv[1]);key=sys.argv[2];spec=v['specs'][key];base=Path('/mnt/mod4_linux_durable_20261013' if key=='e2' else '/home/lc01/Zonglin Li/zonglin2');root=Path(v['roots'][key]);assert root.resolve().is_relative_to(base.resolve());assert not root.exists();old=Path(spec['previous_runtime_root']);e=json.loads((old/'NODE_EXIT_ACTUAL.json').read_bytes());t=json.loads((old/'NODE_TERMINAL_ACTUAL.json').read_bytes())['row'];own=[]
for p in psutil.process_iter(['pid','cmdline','create_time']):
 try:
  if p.pid!=__import__('os').getpid() and any(x.startswith(str(old)+'/') for x in p.info['cmdline'] or []):own.append(p.info)
 except psutil.Error:pass
assert not own and e['actual_all_own_children_waited'] and e['validation_fcntl_released_if_acquired'] and t['returncode']==0 and not t['errors'] and t['final']['passed'] and t['final']['final']['SHA']==spec['source_SHA'];paths=[spec['private_lock']]
if key=='recovery':paths.append(str(base/'state/finite_environment_validation.lock'))
else:paths.extend(['/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/native_floor_supervisor.lock','/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock'])
locks=[]
for path in paths:
 with Path(path).open('rb+') as f:
  free=False
  try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);free=True;fcntl.flock(f,fcntl.LOCK_UN)
  except BlockingIOError:pass
  locks.append(dict(path=path,actual_fcntl_free=free))
compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']).decode();line=next(x for x in subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits']).decode().splitlines() if spec['GPU_UUID'] in x);disk=shutil.disk_usage(base);ram=psutil.virtual_memory().available;checks=dict(old_actual_out=True,new_target_unused=True,GPU_empty=not any(spec['GPU_UUID'] in x for x in compute.splitlines()),GPU_free_over7000=int(line.split(',')[-1])>7000,RAM_over8GiB=ram>8*1024**3,disk_over25GiB=disk.free>25*1024**3,real_locks_free=all(x['actual_fcntl_free'] for x in locks))
canonical=None
if key=='e2':
 c=json.loads(Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json').read_bytes());canonical=dict(active_segment=c['active_segment'],authorized_training_seconds=c['authorized_training_seconds'],extensions=len(c['budget_extensions']),remaining_snapshot=c['remaining_training_seconds']);checks['canonical_none_original_budget']=c['active_segment'] is None and c['authorized_training_seconds']==1188000 and len(c['budget_extensions'])==7
print(json.dumps(dict(epoch=time.time(),key=key,checks=checks,ready=all(checks.values()),GPU_line=line,compute_snapshot=compute,durable=dict(zip(('total','used','free'),disk)),available_RAM_bytes=ram,locks=locks,canonical=canonical,no_GPU_Task_modelhash_account_write_or_peer_identity_query=True)))
'''
def main():
 assert not (R/'AVAILABLE_TWO_RESOURCE_PREFLIGHT_STARTED_ACTUAL.json').exists();v=json.loads((R/'TWO_AVAILABLE_SOURCE_PAYLOADS_CPU_PREPARED_ACTUAL.json').read_bytes());assert v['passed'];proof=json.loads((R/'AVAILABLE_TWO_OWNER_SCHEDULING_CPU_ACTUAL.json').read_bytes());assert proof['passed'];d.put('AVAILABLE_TWO_RESOURCE_PREFLIGHT_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,actual_alive_only_exclusive_all_transport=True));pw=getpass.getpass('72 available E3 and original E2 resource preflight (hidden): ');c=None;out={}
 try:c=d.a.connect72(pw);pw=None;c.get_transport().set_keepalive(15);out['recovery']=d.a.code(c,d.a.PY,READ,json.dumps(v),'recovery',timeout=60)
 finally:
  pw=None
  if c:c.close();c=None
 try:c=d.a.t.connect();out['e2']=d.a.code(c,d.a.t.PY,READ,json.dumps(v),'e2',timeout=60)
 finally:
  if c:d.a.t.close(c)
 out=dict(epoch=time.time(),experts=out,ready=all(x['ready'] for x in out.values()),only_scheduled_two_GPUs_gate_dispatch=True,H1_deferred_does_not_block_other_experts=True,actual_finite_transport_returned=True);d.put('AVAILABLE_TWO_RESOURCES_AND_ORIGINAL_CANONICAL_PREFLIGHT_ACTUAL.json',out);print(json.dumps(out),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:d.put('AVAILABLE_TWO_RESOURCE_PREFLIGHT_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_Task_or_account_mutation=True));raise
