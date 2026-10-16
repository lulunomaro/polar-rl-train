from pathlib import Path
import sys,os,json,time,getpass,traceback
D=Path(__file__).resolve().parent;R=D/'reports';sys.path.insert(0,str(D));from deploy_two_unused_expert_native_then_original_accounting_once import S,T,A,OLD,PREV,code,H,connect72,t,PY
READ=r'''
from pathlib import Path
import sys,json,time,psutil,hashlib
B=Path(sys.argv[1]);key=sys.argv[2];selected=list(B.glob('*.json'))+list((B/'job0').glob('*.json'));out=B/'job0'/('native20k_then_production' if key=='curb' else 'native');selected+=list(out.glob('*.json'));selected+=list((B/'job0'/('production_only' if key=='curb' else 'production')).glob('*.json'));files=[]
for p in sorted(set(selected)):
 if p.is_file():
  raw=p.read_bytes();files.append(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),value=json.loads(raw)))
procs=[]
for p in psutil.process_iter(['pid','create_time','cmdline','cwd']):
 try:
  if any(str(B)+'/' in x for x in p.info['cmdline'] or []):procs.append(p.info)
 except psutil.Error:pass
logs=[]
for p in (B/'owner_CONSOLE.log',B/'node_CONSOLE.log',B/'job0/native_WORKER.log',B/'job0/native_CPU.log',B/'job0/production_WORKER.log'):
 if p.exists():
  with p.open('rb') as f:f.seek(max(0,p.stat().st_size-10000));tail=f.read().decode('utf8',errors='replace')
  logs.append(dict(path=str(p),bytes=p.stat().st_size,tail=tail))
print(json.dumps(dict(epoch=time.time(),files=files,actual_own_processes=procs,owned_log_tails=logs,readonly=True)))
'''
SOURCE=r'''
from pathlib import Path
import json,time,sys,psutil,fcntl
B=Path(sys.argv[1]);C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');c=json.loads(C.read_bytes());files=[]
for p in sorted(B.glob('*.json')):
 if p.name in ('OWNER_CURRENT.json','OWNER_FINAL.json','OWNER_ORIGINAL_ERROR.json','OWNER_EXIT_ACTUAL.json'):files.append(dict(path=str(p),value=json.loads(p.read_bytes())))
locks=[]
for p in (C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with p.open('rb+') as f:
  try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:held=True
  else:held=False;fcntl.flock(f,fcntl.LOCK_UN)
 locks.append(dict(path=str(p),actual_held=held))
print(json.dumps(dict(epoch=time.time(),old_E2_files=files,original_canonical={k:c[k] for k in ('active_segment','authorized_training_seconds','charged_training_seconds','remaining_training_seconds')},actual_original_two_fcntl=locks,readonly=True)))
'''
def main():
 with (R/'FIRST_NEW_NATIVE_ACTUAL_READONLY_STARTED.json').open('x') as f:json.dump(dict(epoch=time.time(),pid=os.getpid(),actual_alive_only_exclusive_transport=True),f)
 pw=getpass.getpass('Host72 new native state read only (hidden): ');c=None;v={}
 try:c=t.connect();v['curb']=code(c,t.PY,READ,S,'curb');v['old_E2_and_canonical']=code(c,t.PY,SOURCE,'/mnt/mod4_linux_durable_20261013/'+OLD.name+'/e2_from58_plus75_same4_continuation_v2')
 finally:t.close(c);c=None
 try:c=connect72(pw);pw=None;v['recovery']=code(c,PY,READ,T,'recovery')
 finally:
  pw=None
  if c:c.close()
 with (R/'FIRST_TWO_NATIVE_AND_OLD_E2_HANDOFF_READONLY_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
 for key in ('curb','recovery'):
  files=v[key]['files'];current=next((x['value'] for x in files if x['path'].endswith(('/OWNER_CURRENT.json','/NODE_CURRENT.json'))),{});errors=[x for x in files if 'ORIGINAL_ERROR' in x['path']];print(json.dumps(dict(key=key,epoch=v[key]['epoch'],processes=v[key]['actual_own_processes'],current=current,errors=errors,log_tails=v[key]['owned_log_tails'] if errors else [])),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('FIRST_READONLY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_replay=True),f,indent=2)
  raise
