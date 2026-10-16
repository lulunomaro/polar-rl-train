"""Only after previous local collector exits: source once, target own-root bound."""
from pathlib import Path
import os,sys,json,time,hashlib,getpass,traceback,subprocess
D=Path(__file__).resolve().parent;R=D/'reports';sys.path.insert(0,str(D));from deploy_grounded_H1_V2_new_native_CPU_then_finite1800_once import code,H,connect72,t,S,T,PY
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
  if str(B/'h1_prelaunch_v2_original_canonical_owner_v1.py') in (p.info['cmdline'] or []):procs.append(p.info)
 except psutil.Error:pass
C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');b=json.loads(C.read_bytes());locks=[]
for path in (C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with path.open('rb+') as f:
  try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:held=True
  else:held=False;fcntl.flock(f,fcntl.LOCK_UN)
 locks.append(dict(path=str(path),actual_held=held))
print(json.dumps(dict(epoch=time.time(),files=files,actual_owner_processes=procs,original_canonical_snapshot={k:b[k] for k in ('active_segment','authorized_training_seconds','charged_training_seconds','remaining_training_seconds')},own_matching_completed_segments=[x for x in b['completed_segments'] if str(x.get('kind','')).startswith('Linux_HOST72_H1_GROUND_PRELAUNCH_V2_FIRST1800_')],actual_two_fcntl=locks,readonly_no_budget_write=True)))
'''
TARGET=r'''
from pathlib import Path
import sys,json,time,psutil,hashlib,fcntl
B=Path(sys.argv[1]);selected=list(B.glob('*.json'));models=[];files=[]
for phase in ('native','production'):
 out=B/'job0'/phase;selected+=list(out.glob('*.json'))
 for log in (out/'logs').glob('*'):selected+=list(log.glob('*STARTUP_VERIFIED.json'))+list(log.glob('run_manifest.json'))
 if phase=='production':selected+=list((out/'control_prefix_raw').glob('*INDEX*.json'))
for p in sorted(set(selected)):
 raw=p.read_bytes();row=dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest())
 try:row['value']=json.loads(raw)
 except ValueError:row['parse_failed']=True
 files.append(row)
for rel in ('native/own_source_full20k_startup0.pt','native/own_H1_ground_prelaunch_v2_native180.pt','production/own_H1_startup0.pt','production/model_update1.pt'):
 p=B/'job0'/rel
 if p.is_file():models.append(dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest(),role=rel))
final=B/'job0/production/FINAL.json'
if final.is_file():
 v=json.loads(final.read_bytes())['final'];p=Path(v['path'])
 if p.is_file() and str(p) not in [x['path'] for x in models]:models.append(dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest(),role='production_final'))
scripts={str(B/n) for n in ('h1_prelaunch_v2_native_CPU_production_node_v1.py','h1_ground_prelaunch_v2_native_worker_v1.py','review_H1_prelaunch_v2_native_allrows_CPU_v1.py','h1_prelaunch_v2_production_worker_v1.py')};procs=[]
for p in psutil.process_iter(['pid','create_time','cmdline','cwd']):
 try:
  if any(x in scripts for x in p.info['cmdline'] or []):procs.append(p.info)
 except psutil.Error:pass
with Path('/home/lc01/Zonglin Li/zonglin2/state/finite_environment_validation.lock').open('rb+') as f:
 try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
 except BlockingIOError:held=True
 else:held=False;fcntl.flock(f,fcntl.LOCK_UN)
logs=[]
if any('ERROR' in x['path'] for x in files) or not procs:
 for p in [B/'NODE_CONSOLE.log',*list((B/'job0').glob('*WORKER.log'))]:
  if p.is_file():logs.append(dict(path=str(p),tail=p.read_bytes()[-5000:].decode('utf8','replace')))
print(json.dumps(dict(epoch=time.time(),files=files,models=models,actual_own_processes=procs,validation_actual_fcntl_held=held,readonly_ownroot_only=True,error_context_log_tails=logs)))
'''
def main():
 put('V2_NATIVE_CPU_FIRST_IMMUTABLE_READONLY_FINITE_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),creation_UTC=subprocess.check_output(['powershell','-NoProfile','-Command',"(Get-Process -Id %d).StartTime.ToUniversalTime().ToString('o')"%os.getpid()]).decode().strip(),actual_alive_only_transport_owner_all210_72_249=True,max_same_target_connection600s=True,no_GPU_launch_or_retry_or_raw_rehash=True));pw=getpass.getpass('V2 own first model read-only target password (hidden): ');c=sf=None;v={}
 try:
  c=t.connect();v['source']=code(c,t.PY,SOURCE,S)
 finally:t.close(c);c=None
 try:
  c=connect72(pw);pw=None;begun=time.monotonic()
  while True:
   target=code(c,PY,TARGET,T,timeout=120);put('V2_NATIVE_CPU_FIRST_IMMUTABLE_LOCAL_CURRENT_ACTUAL.json',target,True)
   if any(x['role']=='production/model_update1.pt' for x in target['models']) or not target['actual_own_processes'] or any('ORIGINAL_ERROR' in x['path'] for x in target['files']) or time.monotonic()-begun>=600:break
   time.sleep(15)
  folder=D/'actual_complete_native_and_first_models';folder.mkdir(exist_ok=True);sf=c.open_sftp();sf.get_channel().settimeout(120);local=[]
  for row in target['models']:
   p=folder/(row['role'].replace('/','_') if '/' in row['role'] else Path(row['path']).name)
   if p.exists():assert p.stat().st_size==row['bytes'] and H(p)==row['SHA']
   else:
    tmp=p.with_suffix('.pt.partial');assert not tmp.exists();sf.get(row['path'],str(tmp));assert tmp.stat().st_size==row['bytes'] and H(tmp)==row['SHA'];tmp.replace(p)
   local.append(dict(path=str(p.resolve()),remote=row['path'],bytes=row['bytes'],SHA=row['SHA'],twohost_bytes_SHA_exact=True,role=row['role']))
  sf.close();sf=None;target['local_models']=local;v.update(epoch=time.time(),target=target,no_runtime_launch_or_stop_or_optimizer_or_canonical_write=True);put('V2_NATIVE_CPU_FIRST_IMMUTABLE_COMPLETE_BOUND_COLLECTION_ACTUAL.json',v);print(json.dumps(dict(epoch=v['epoch'],actual_own_processes=target['actual_own_processes'],local_models=local)),flush=True)
 finally:
  pw=None
  if sf:sf.close()
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('V2_NATIVE_CPU_FIRST_COLLECTION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),unknown_state_no_runtime_retry_or_signal=True));raise
