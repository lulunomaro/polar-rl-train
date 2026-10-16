from pathlib import Path
import sys,os,json,time,getpass,traceback
D=Path(__file__).resolve().parent;R=D/'reports';sys.path.insert(0,str(D));from deploy_new_E2_closed75_same4_native_then_single_bounded_learning_once import S,T,PY,t,code,H,connect72;from collect_two_new_native_and_first_production_same_source900_once import READ
def put(n,v,rolling=False):
 p=R/n
 if rolling:q=p.with_suffix('.json.partial');q.write_text(json.dumps(v,indent=2),encoding='utf8');q.replace(p)
 else:
  with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
SOURCE=r'''
from pathlib import Path
import sys,json,time,psutil,hashlib,fcntl
B=Path(sys.argv[1]);files=[]
for p in sorted(B.glob('*.json')):
 raw=p.read_bytes();files.append(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),value=json.loads(raw)))
procs=[]
for p in psutil.process_iter(['pid','create_time','cmdline','cwd']):
 try:
  if str(B/'e2_single_original_canonical_owner_node_v2.py') in (p.info['cmdline'] or []):procs.append(p.info)
 except psutil.Error:pass
C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');c=json.loads(C.read_bytes());locks=[]
for path in (C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with path.open('rb+') as f:
  try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:held=True
  else:held=False;fcntl.flock(f,fcntl.LOCK_UN)
 locks.append(dict(path=str(path),actual_held=held))
print(json.dumps(dict(epoch=time.time(),files=files,actual_owner_processes=procs,actual_original_two_fcntl=locks,canonical={k:c[k] for k in ('active_segment','authorized_training_seconds','charged_training_seconds','remaining_training_seconds')},no_runtime_or_budget_write=True)))
'''
def main():
 put('E2_CLOSED75_FIRST_NATIVE_PPO_FINITE_COLLECTOR_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),actual_alive_only_exclusive_210_72_249_transport_owner=True,max_source_same_connection600s=True,no_runtime_launch_or_signal=True));pw=getpass.getpass('Host72 new E2 native and first immutable model password (hidden): ');c=sf=None;result={}
 try:
  c=t.connect();begun=time.monotonic()
  while True:
   v=code(c,t.PY,SOURCE,S);put('E2_CLOSED75_SOURCE_CURRENT_FINITE_LOCAL_ACTUAL.json',v,True);current=next((x['value'] for x in v['files'] if x['path'].endswith('/OWNER_CURRENT.json')),{});row=current.get('row') or {};positive=row.get('phase')=='production' and (row.get('latest_save') or {}).get('updates',0)>=1
   if positive or any(x['path'].endswith(('/OWNER_ORIGINAL_ERROR.json','/OWNER_EXIT_ACTUAL.json')) for x in v['files']) or time.monotonic()-begun>=600:break
   time.sleep(15)
  result['source']=v
 finally:t.close(c);c=None
 try:
  c=connect72(pw);pw=None;v=code(c,PY,READ.replace("'own_restored0.pt'","'own_startup0.pt'"),T,'e2');folder=D/'actual_E2_closed75_native_and_first_models';folder.mkdir();sf=c.open_sftp();sf.get_channel().settimeout(120);local=[]
  for row in v['models']:
   p=folder/row['role'].replace('/','_');tmp=p.with_suffix('.pt.partial');assert not p.exists() and not tmp.exists();sf.get(row['path'],str(tmp));assert tmp.stat().st_size==row['bytes'] and H(tmp)==row['SHA'];tmp.replace(p);local.append(dict(path=str(p),remote=row['path'],role=row['role'],bytes=row['bytes'],SHA=row['SHA'],twohost_complete_exact=True))
  sf.close();sf=None;v['local_models']=local;result.update(epoch=time.time(),target=v,no_native_replay_or_budget_write=True);put('E2_CLOSED75_NATIVE_CPU_FIRST_MODELS_COMPLETE_BOUND_COLLECTION_ACTUAL.json',result);print(json.dumps(dict(epoch=result['epoch'],models=local,target_actual_own_processes=v['actual_own_processes'])),flush=True)
 finally:
  pw=None
  if sf:sf.close()
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('E2_CLOSED75_FIRST_COLLECT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_runtime_retry=True));raise
