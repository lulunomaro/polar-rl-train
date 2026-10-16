"""Original hourly bounded read of the existing H1 job; no launches or retries.

One source connection then one target connection. Never clears accounting, replays
native/prechecks, sends a stop, or assumes an elapsed deadline means actual exit.
"""
from pathlib import Path
import sys,os,json,time,hashlib,getpass,traceback,subprocess
D=Path(__file__).resolve().parent;R=D/'reports';PREFIX='H1_HOURLY1525_EXISTING_SCOPE_READONLY'
sys.path.insert(0,str(D));from deploy_H1_admitted_first1800_original_owner_fresh_chain_once import code,H,connect72,t,S,T,PY
def put(suffix,v):
 with (R/(PREFIX+'_'+suffix+'.json')).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
SOURCE_READ=r'''
from pathlib import Path
import sys,json,time,hashlib,psutil,fcntl
B=Path(sys.argv[1]);files=[]
for name in ('OWNER_IDENTITY.json','OWNER_CURRENT.json','OWNER_FINAL.json','OWNER_EXIT_ACTUAL.json','OWNER_ORIGINAL_ERROR.json','OWNER_NOT_GRANTED_TERMINAL.json','HUMAN_H1_FIRST1800_ORIGINAL_CANONICAL_CONTRACT.json'):
 p=B/name
 if p.is_file():
  raw=p.read_bytes();files.append(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),value=json.loads(raw)))
procs=[];script=str(B/'h1_first1800_original_canonical_owner_v1.py')
for p in psutil.process_iter(['pid','create_time','cmdline','cwd']):
 try:
  if script in (p.info['cmdline'] or []):procs.append(p.info)
 except psutil.Error:pass
C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');c=json.loads(C.read_bytes());segments=[x for x in c['completed_segments'] if x.get('owner_parent_pid')==499426 and str(x.get('kind','')).startswith('Linux_HOST72_H1_FLAT_PUBLIC_REQUEST_FIRST1800_')];locks=[]
for path in (C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with path.open('rb+') as f:
  try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:held=True
  else:held=False;fcntl.flock(f,fcntl.LOCK_UN)
 locks.append(dict(path=str(path),actual_held=held))
print(json.dumps(dict(epoch=time.time(),files=files,actual_owner_processes=procs,original_canonical_snapshot={k:c[k] for k in ('active_segment','authorized_training_seconds','charged_training_seconds','remaining_training_seconds')},own_matching_completed_segments=segments,actual_two_fcntl=locks,readonly_no_budget_write=True)))
'''
TARGET_READ=r'''
from pathlib import Path
import sys,json,time,hashlib,psutil,fcntl
B=Path(sys.argv[1]);files=[];models=[]
selected=list(B.glob('*.json'))
for phase in ('precheck128','precheck20k','production'):
 out=B/'job0'/phase;selected+=list(out.glob('*.json'))
 if (out/'control_prefix_raw/CONTROL_VALID_PREFIX_INDEX_ACTUAL.json').exists():selected.append(out/'control_prefix_raw/CONTROL_VALID_PREFIX_INDEX_ACTUAL.json')
 for log in (out/'logs').glob('*'):selected+=list(log.glob('*STARTUP_VERIFIED.json'))+list(log.glob('run_manifest.json'))
for p in sorted(set(selected)):
 raw=p.read_bytes();row=dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest())
 try:row['value']=json.loads(raw)
 except ValueError:row['parse_failed']=True
 files.append(row)
for name in ('own_H1_startup0.pt','model_update1.pt'):
 p=B/'job0/production'/name
 if p.is_file():models.append(dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest(),role='production_'+name))
final=B/'job0/production/FINAL.json'
if final.exists():
 row=json.loads(final.read_bytes())['final'];p=Path(row['path'])
 if p.is_file() and str(p) not in [x['path'] for x in models]:models.append(dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest(),role='production_final'))
scripts={str(B/n) for n in ('h1_first1800_node72_finite_v1.py','h1_learning_phase_worker_v1.py')};procs=[]
for p in psutil.process_iter(['pid','create_time','cmdline','cwd']):
 try:
  if any(x in scripts for x in p.info['cmdline'] or []):procs.append(p.info)
 except psutil.Error:pass
with Path('/home/lc01/Zonglin Li/zonglin2/state/finite_environment_validation.lock').open('rb+') as f:
 try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
 except BlockingIOError:held=True
 else:held=False;fcntl.flock(f,fcntl.LOCK_UN)
print(json.dumps(dict(epoch=time.time(),files=files,models=models,actual_own_processes=procs,validation_actual_fcntl_held=held,readonly_no_GPU_or_optimizer_or_runtime_mutation=True)))
'''
def main():
 put('STARTED_ACTUAL',dict(epoch=time.time(),pid=os.getpid(),creation_UTC=subprocess.check_output(['powershell','-NoProfile','-Command',"(Get-Process -Id %d).StartTime.ToUniversalTime().ToString('o')"%os.getpid()]).decode().strip(),one_source_then_one_target_connection_only=True,no_learning_launch_or_retry=True));pw=getpass.getpass('Existing H1 hourly target read-only password (hidden): ');c=None;sf=None;result={}
 try:
  try:c=t.connect();result['source']=code(c,t.PY,SOURCE_READ,S,timeout=75)
  except BaseException:result['source_connection_or_read_original_error']=traceback.format_exc()
  finally:t.close(c);c=None
  try:
   c=connect72(pw);pw=None;result['target']=code(c,PY,TARGET_READ,T,timeout=90);models=result['target']['models'];local=[]
   if models:
    folder=D/'actual_complete_first_production_models';folder.mkdir(exist_ok=True);sf=c.open_sftp();sf.get_channel().settimeout(120)
    for row in models:
     p=folder/Path(row['path']).name
     if p.exists():assert p.stat().st_size==row['bytes'] and H(p)==row['SHA']
     else:
      tmp=p.with_suffix('.pt.partial');assert not tmp.exists();sf.get(row['path'],str(tmp));assert tmp.stat().st_size==row['bytes'] and H(tmp)==row['SHA'];tmp.replace(p)
     local.append(dict(path=str(p.resolve()),remote=row['path'],bytes=row['bytes'],SHA=row['SHA'],twohost_bytes_SHA_exact=True,role=row['role']))
    sf.close();sf=None
   result['target']['local_models']=local
  except BaseException:result['target_connection_or_read_original_error']=traceback.format_exc()
  finally:
   pw=None
   if sf:sf.close()
   if c:c.close()
  result.update(epoch=time.time(),no_runtime_launch_stop_GPU_replay_or_budget_write=True);put('COMPLETE_ORIGINAL_ERRORS_ACTUAL',result);summary=dict(source_reachable='source' in result,target_reachable='target' in result,source_actual_owner_procs=result.get('source',{}).get('actual_owner_processes'),target_actual_procs=result.get('target',{}).get('actual_own_processes'),local_models=result.get('target',{}).get('local_models',[]));print(json.dumps(summary),flush=True)
 finally:pw=None
if __name__=='__main__':main()
