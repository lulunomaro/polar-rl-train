"""Prepared only: after the hour, collect missing closed finals and original accounting."""
from pathlib import Path
import sys,os,json,time,getpass,traceback,importlib.util
B=Path(__file__).resolve().parent;R=B/'reports';W=B.parent
import deploy_three_actual_hour_learning_closed_H1_continuation_V2_once as d
sp=importlib.util.spec_from_file_location('closed_hour_original_readonly_account_helpers',W/'MOD4_POST_POWER_RESTORE_H1_SATURATION_REPAIR_20261018/hour2_h1_fe778_v1/collect_H1_hour2_only_missing_final_after_transport_return_V2_once.py');old=importlib.util.module_from_spec(sp);sp.loader.exec_module(old)
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
META=r'''
from pathlib import Path
import sys,json,os,time,psutil
B=Path(sys.argv[1]);rows={};own=[]
for p in [*B.glob('*.json'),*B.glob('job0/production/**/*.json')]:
 if p.is_file():rows[p.relative_to(B).as_posix()]=json.loads(p.read_bytes())
for p in psutil.process_iter(['pid','create_time','cmdline','cwd']):
 try:
  if p.pid!=os.getpid() and any(x.startswith(str(B)+'/') for x in p.info['cmdline'] or []):own.append(p.info)
 except psutil.Error:pass
print(json.dumps(dict(epoch=time.time(),root=str(B),rows=rows,actual_own_processes=own,readonly=True)))
'''
RES=r'''
from pathlib import Path
import sys,json,time,shutil,subprocess,fcntl
base=Path(sys.argv[1]);locks=[]
for q in json.loads(sys.argv[2]):
 p=Path(q);free=False
 with p.open('rb+') as f:
  try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);free=True;fcntl.flock(f,fcntl.LOCK_UN)
  except BlockingIOError:pass
 locks.append(dict(path=str(p),actual_fcntl_free=free))
print(json.dumps(dict(epoch=time.time(),durable=dict(zip(('total','used','free'),shutil.disk_usage(base))),actual_locks=locks,compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']).decode())))
'''
def terminal(x):
 t=x['rows'].get('NODE_TERMINAL_ACTUAL.json',{}).get('row',{});e=x['rows'].get('NODE_EXIT_ACTUAL.json',{})
 return bool(not x['actual_own_processes'] and t.get('terminal_all_own_children_waited') and e.get('actual_all_own_children_waited') and e.get('validation_fcntl_released_if_acquired'))
def get_missing(c,py,key,x,models):
 f=x['rows'].get('job0/production/FINAL.json')
 if not f or not f.get('passed') or not terminal(x):return
 row=f['final'];p=B/'actual_closed_three_finals'/key/Path(row['path']).name
 if p.exists():
  assert p.stat().st_size==row['bytes'];prior=json.loads((R/'THREE_HOUR_MISSING_CLOSED_FINAL_COLLECTION_ACTUAL.json').read_bytes());known=next(z for z in prior['models'] if z['key']==key and z['SHA']==row['SHA']);models.append(known);return
 actual=d.a.code(c,py,old.HASH,row['path'],timeout=90);assert actual['SHA']==row['SHA'] and actual['bytes']==row['bytes'];p.parent.mkdir(parents=True,exist_ok=True);part=p.with_suffix('.pt.partial');assert not part.exists();sf=c.open_sftp();sf.get_channel().settimeout(120)
 try:sf.get(row['path'],str(part))
 finally:sf.close()
 assert part.stat().st_size==actual['bytes'] and d.H(part)==actual['SHA'];part.replace(p);models.append(dict(actual,key=key,local_path=str(p),twohost_complete_SHA=True))
def main():
 assert not (R/'THREE_HOUR_MISSING_CLOSED_FINAL_COLLECTION_ACTUAL.json').exists()
 v=json.loads((R/'THREE_REAL_GPU_ONE_HOUR_NATIVE_REUSE_AND_LEARNING_DETACHED_ACTUAL.json').read_bytes());assert v['owner']['detached_pid']==137670
 put('THREE_HOUR_FINAL_COLLECTOR_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,actual_alive_only_exclusive_all_transports=True,after_actual_hour_only_no_Task_native_or_old_model_replay=True));pw=getpass.getpass('72 only missing hour-final models (hidden): ');c=None;out=dict(experts={},models=[])
 try:
  c=d.a.t.connect();c.get_transport().set_keepalive(15);out['owner']=d.a.code(c,d.a.t.PY,META,v['source_root'],timeout=90);out['experts']['e2']=d.a.code(c,d.a.t.PY,META,v['roots']['e2'],timeout=90);out['account']=d.a.code(c,d.a.t.PY,old.f.ACCOUNT,timeout=90);out['source_resources']=d.a.code(c,d.a.t.PY,RES,'/mnt/mod4_linux_durable_20261013',json.dumps([v['specs']['e2']['private_lock']]),timeout=45)
  if out['owner']['rows'].get('COHORT_FINAL.json') and not out['owner']['actual_own_processes']:get_missing(c,d.a.t.PY,'e2',out['experts']['e2'],out['models'])
 finally:
  if c:d.a.t.close(c);c=None
 try:
  c=d.a.connect72(pw);pw=None
  for key in ('h1','recovery'):out['experts'][key]=d.a.code(c,d.a.PY,META,v['roots'][key],timeout=90)
  out['target_resources']=d.a.code(c,d.a.PY,RES,'/home/lc01/Zonglin Li/zonglin2',json.dumps([v['specs'][k]['private_lock'] for k in ('h1','recovery')]+['/home/lc01/Zonglin Li/zonglin2/state/finite_environment_validation.lock']),timeout=45)
  if out['owner']['rows'].get('COHORT_FINAL.json') and not out['owner']['actual_own_processes']:
   for key in ('h1','recovery'):get_missing(c,d.a.PY,key,out['experts'][key],out['models'])
 finally:
  pw=None
  if c:c.close()
 out.update(epoch=time.time(),actual_closed=bool(out['owner']['rows'].get('COHORT_FINAL.json') and not out['owner']['actual_own_processes'] and all(terminal(x) for x in out['experts'].values()) and len(out['models'])==3 and out['account']['original_canonical']['active_segment'] is None and all(x['actual_fcntl_free'] for x in out['account']['actual_locks']+out['source_resources']['actual_locks']+out['target_resources']['actual_locks'])),actual_finite_transport_returned=True,no_old_PT_or_native_or_raw_rehashed_or_downloaded=True)
 put('THREE_HOUR_MISSING_CLOSED_FINAL_COLLECTION_ACTUAL.json',out);print(json.dumps(dict(actual_closed=out['actual_closed'],models=out['models'],canonical_active=out['account']['original_canonical']['active_segment'])),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:put('THREE_HOUR_FINAL_COLLECTION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_automatic_GPU_retry_or_account_mutation=True));raise
