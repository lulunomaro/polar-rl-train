"""Prepared for natural closure only; never settle or open the offline canonical."""
from pathlib import Path,PurePosixPath
import getpass,json,os,sys,time,traceback
import deploy_available_E2_E3_original_writer_V2_once as d
B=d.B;R=d.R
READ=r'''
from pathlib import Path,PurePosixPath
import json,sys,os,time,psutil
v=json.loads(sys.argv[1]);out={}
for key,root in [('owner',v['owner_root']),('recovery',v['roots']['recovery'])]:
 B=Path(root);rows={p.relative_to(B).as_posix():json.loads(p.read_bytes()) for p in [*B.glob('*.json'),*B.glob('job0/production/**/*.json'),B/'job0/GO_PRODUCTION.json'] if p.is_file()};own=[]
 for p in psutil.process_iter(['pid','create_time','cmdline','cwd']):
  try:
   if p.pid!=os.getpid() and any(x.startswith(str(B)+'/') for x in p.info['cmdline'] or []):own.append(p.info)
  except psutil.Error:pass
 out[key]=dict(root=str(B),rows=rows,actual_own_processes=own)
print(json.dumps(dict(epoch=time.time(),actual=out,readonly_no_original_canonical=True)))
'''
RESOURCE=r'''
from pathlib import Path,PurePosixPath
import sys,json,time,fcntl,shutil,subprocess
v=json.loads(sys.argv[1]);base=Path('/home/lc01/Zonglin Li/zonglin2');locks=[]
for name in [v['specs']['recovery']['private_lock'],str(base/'state/finite_environment_validation.lock')]:
 free=False
 with Path(name).open('rb+') as f:
  try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);free=True;fcntl.flock(f,fcntl.LOCK_UN)
  except BlockingIOError:pass
 locks.append(dict(path=name,actual_fcntl_free=free))
p=base/'state/MOD4_SINGLE_E3_OFFLINE_COST_PENDING_20261020.json';assert p.is_file();r=json.loads(p.read_bytes());assert r['run_id']==v['run_id'];print(json.dumps(dict(epoch=time.time(),locks=locks,disk=dict(zip(('total','used','free'),shutil.disk_usage(base))),compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']).decode(),reservation_retained=r,original_canonical_settled=False)))
'''
def closed(v):
 o=v['actual']['owner'];n=v['actual']['recovery'];r=n['rows'].get('NODE_TERMINAL_ACTUAL.json',{}).get('row',{});e=n['rows'].get('NODE_EXIT_ACTUAL.json',{})
 return bool(o['rows'].get('COHORT_FINAL.json') and o['rows'].get('OWNER_EXIT_ACTUAL.json') and not o['actual_own_processes'] and not n['actual_own_processes'] and r.get('terminal_all_own_children_waited') and e.get('actual_all_own_children_waited') and e.get('validation_fcntl_released_if_acquired'))
def main():
 dispatch=json.loads((R/'APPROVED_SINGLE_E3_LEARNING_DETACHED_ACTUAL.json').read_bytes());assert dispatch['owner']['detached_pid']==108495;d.put('SINGLE_E3_CLOSING_COLLECTOR_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,max_same_connection_wait_seconds=900,actual_alive_only_exclusive_all_transport=True));pw=getpass.getpass('72 closed single E3 final and pending cost only (hidden): ');c=None
 try:
  c=d.a.connect72(pw);pw=None;c.get_transport().set_keepalive(15);begin=time.monotonic();observations=0
  while True:
   v=d.a.code(c,d.a.PY,READ,json.dumps(dispatch),timeout=60);observations+=1
   if closed(v) or time.monotonic()-begin>=900:break
   time.sleep(10)
  v.update(actual_closed=closed(v),observations=observations,model=None,original_canonical_settled=False)
  if closed(v):
   v['resources']=d.a.code(c,d.a.PY,RESOURCE,json.dumps(dispatch),timeout=60);assert all(x['actual_fcntl_free'] for x in v['resources']['locks']);co=v['actual']['owner']['rows']['COHORT_FINAL.json'];assert set(co['go'])=={'recovery'} and co['original_cost_settled'] is False and co['pending_cost_record_complete'];cost=co['pending_cost'];assert cost['run_id']==dispatch['run_id'] and not cost['canonical_settled'];final=v['actual']['recovery']['rows'].get('job0/production/FINAL.json');row=v['actual']['recovery']['rows']['NODE_TERMINAL_ACTUAL.json']['row']
   if final and final.get('passed') and not row['errors'] and row['returncode']==0:
    model=final['final'];remote=PurePosixPath(model['path']);assert remote.is_relative_to(PurePosixPath(dispatch['roots']['recovery'])/'job0/production');local=B/'actual_closed_single_E3_final'/remote.name;assert not local.exists();local.parent.mkdir(exist_ok=True);part=local.with_suffix('.pt.partial');assert not part.exists();sf=c.open_sftp();sf.get_channel().settimeout(120)
    try:sf.get(str(remote),str(part))
    finally:sf.close()
    assert part.stat().st_size==model['bytes'] and d.H(part)==model['SHA'];part.replace(local);v['model']=dict(model,key='recovery',local_path=str(local),twohost_complete_SHA=True)
  v.update(epoch=time.time(),actual_finite_transport_returned=True,no_original_canonical_access_or_reconciliation=True);d.put('SINGLE_E3_CLOSED_FINAL_AND_PENDING_COST_COLLECTION_ACTUAL.json',v);print(json.dumps(dict(actual_closed=v['actual_closed'],model=v['model'],original_canonical_settled=False)),flush=True)
 finally:
  pw=None
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:d.put('SINGLE_E3_CLOSING_COLLECTOR_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_Task_replay_or_canonical_write=True));raise
