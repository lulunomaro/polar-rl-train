"""One sequential own-scope source wait and closed target final collection; no runtime mutation."""
from pathlib import Path
import importlib.util,json,time,os,shlex,getpass,paramiko,hashlib,traceback,subprocess
D=Path(__file__).resolve().parent;R=D/'reports';S='/mnt/mod4_linux_durable_20261013/'+D.name;T='/home/lc01/Zonglin Li/zonglin2/tasks/'+D.name;PY72='/home/lc01/Zonglin Li/zonglin2/run-python.sh'
s=importlib.util.spec_from_file_location('first_model_pure_read_helpers',D/'collect_E2_first_model_CURB_final_H1_raw_bounded_v2_once.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 put('E2_NATURAL_FINAL_BOUND_COLLECTION_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),creation_UTC=subprocess.check_output(['powershell','-NoProfile','-Command',"(Get-Process -Id %d).StartTime.ToUniversalTime().ToString('o')"%os.getpid()]).decode().strip(),max_source_seconds=900,actual_alive_only_sole_sequential_transport_owner=True))
 c=None;v={}
 try:
  c=m.t.connect();start=time.monotonic();code='ROOT='+repr(S)+'\n'+r'''
from pathlib import Path
import json,time,psutil,fcntl
B=Path(ROOT);C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json')
def read(p):return json.loads(p.read_bytes()) if p.exists() else None
procs=[]
for p in psutil.process_iter(['pid','create_time','cmdline','cwd']):
 try:
  if any(str(B) in z for z in p.info['cmdline'] or []):procs.append(p.info)
 except psutil.Error:pass
state=read(C);ex=read(B/'OWNER_EXIT_ACTUAL.json');locks=[]
if ex and not procs:
 for path in (C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
  f=path.open('rb+')
  try:
   try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
   except BlockingIOError:held=True
   else:held=False;fcntl.flock(f,fcntl.LOCK_UN)
   locks.append(dict(path=str(path),actual_held=held))
  finally:f.close()
print(json.dumps(dict(epoch=time.time(),current=read(B/'OWNER_CURRENT.json'),final=read(B/'OWNER_FINAL.json'),exit=ex,original_error=read(B/'OWNER_ORIGINAL_ERROR.json'),actual_processes=procs,actual_fcntl=locks,canonical=dict(active=state['active_segment'],authorized=state['authorized_training_seconds'],charged=state['charged_training_seconds'],remaining=state['remaining_training_seconds'],own_completed=[x for x in state['completed_segments'] if x.get('owner_parent_pid')==484739]))))
'''
  while True:
   v['source']=m.code(c,m.t.PY,code);x=v['source']
   if (x['exit'] and not x['actual_processes']) or x['original_error'] or time.monotonic()-start>=900:break
   time.sleep(15)
 finally:m.t.close(c)
 pw=getpass.getpass('Host72 closed E2 final model collection password (hidden): ');c=paramiko.SSHClient();c.load_system_host_keys();c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
 try:
  c.connect('10.24.0.72',username='lc01',password=pw,timeout=15,auth_timeout=20,banner_timeout=20,look_for_keys=False,allow_agent=False);pw=None;assert hashlib.sha256(c.get_transport().get_remote_server_key().asbytes()).hexdigest()=='301a9837e8503b664fa4cedde20407769d8f1b86ae59d9a54afb236bdfa41795'
  v['target']=m.code(c,PY72,'ROOT='+repr(T)+'\n'+r'''
from pathlib import Path
import json,time,psutil,hashlib
B=Path(ROOT)
def read(p):return json.loads(p.read_bytes()) if p.exists() else None
procs=[]
for p in psutil.process_iter(['pid','create_time','cmdline','cwd']):
 try:
  if any(str(B) in z for z in p.info['cmdline'] or []):procs.append(p.info)
 except psutil.Error:pass
errors=[dict(path=str(p),value=read(p)) for p in list(B.glob('*ORIGINAL_ERROR*.json'))+list((B/'job0/production').glob('*ORIGINAL_ERROR*.json'))]
print(json.dumps(dict(epoch=time.time(),node_final=read(B/'NODE_FINAL.json'),node_exit=read(B/'NODE_EXIT_ACTUAL.json'),production_final=read(B/'job0/production/FINAL.json'),production_worker_exit=read(B/'job0/production_WORKER_EXIT_ACTUAL.json'),actual_processes=procs,errors=errors)))
''')
  x=v['target']
  if x['production_final'] and x['production_worker_exit'] and not x['actual_processes'] and not x['errors']:v['local_final_model']=m.download(c,x['production_final']['final'],'E2_closed_first_scope_final/model.pt')
 finally:pw=None;c.close()
 put('E2_FIRST_SCOPE_NATURAL_FINAL_MODEL_AND_ACTUAL_COST_COLLECTION.json',v);print(json.dumps(v,default=str),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:put('E2_NATURAL_FINAL_BOUND_COLLECTION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_retry_or_runtime_mutation=True));raise
