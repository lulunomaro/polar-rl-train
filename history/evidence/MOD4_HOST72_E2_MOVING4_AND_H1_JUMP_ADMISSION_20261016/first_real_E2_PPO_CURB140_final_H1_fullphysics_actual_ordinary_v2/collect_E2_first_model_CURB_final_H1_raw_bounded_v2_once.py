"""Sequential source handoff collection, then one bounded target own-scope connection."""
from pathlib import Path
import sys,os,json,time,shlex,getpass,paramiko,hashlib,traceback,subprocess
D=Path(__file__).resolve().parent;R=D/'reports';W=D.parent;S='/mnt/mod4_linux_durable_20261013/'+D.name;T='/home/lc01/Zonglin Li/zonglin2/tasks/'+D.name;CURB='/mnt/mod4_linux_durable_20261013/MOD4_E1_CURB35_FROM_878_NATIVE_TRAIN_20261016/production_fresh_process_v2';PY72='/home/lc01/Zonglin Li/zonglin2/run-python.sh'
sys.path.insert(0,str(W/'MOD4_LINUX_WAVE50_BODYFRAME_RESET_INTEGRATION_20261014'));import transport_bodyframe_root_owned as t
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def code(c,py,text):
 si,so,se=c.exec_command(shlex.quote(py)+' -B -',timeout=60);si.write(text);si.flush();si.channel.shutdown_write();raw=so.read();err=se.read();assert so.channel.recv_exit_status()==0,err.decode();return json.loads(raw)
def download(c,row,relative):
 out=D/relative;out.parent.mkdir(parents=True,exist_ok=True);assert not out.exists();part=out.with_suffix(out.suffix+'.partial');sf=c.open_sftp();sf.get_channel().settimeout(120)
 try:sf.get(row['path'],str(part));assert part.stat().st_size==row['bytes'] and H(part)==row['SHA'];part.replace(out)
 finally:sf.close()
 return dict(path=str(out.resolve()),bytes=out.stat().st_size,SHA=H(out),remote=row['path'],twohost_bytes_SHA_exact=True)
def main():
 put('E2_FIRST_FULLMODEL_AND_H1_RAW_COLLECTION_V2_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),creation_UTC=subprocess.check_output(['powershell','-NoProfile','-Command',"(Get-Process -Id %d).StartTime.ToUniversalTime().ToString('o')"%os.getpid()]).decode().strip(),bounded_target_seconds=900,root_sequential_transport_owner_while_actual_alive=True));result={};c=None
 try:
  c=t.connect();result['source']=code(c,t.PY,'S='+repr(S)+'\nC='+repr(CURB)+r'''
from pathlib import Path
import json,time,psutil
S=Path(S);C=Path(C)
def read(p):return json.loads(p.read_bytes()) if p.exists() else None
procs=[]
for p in psutil.process_iter(['pid','create_time','cmdline','cwd']):
 try:
  if any(str(C) in z or str(S) in z for z in p.info['cmdline'] or []):procs.append(p.info)
 except psutil.Error:pass
b=read(Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json'))
print(json.dumps(dict(epoch=time.time(),CURB_final=read(C/'job0/production_only/FINAL.json'),CURB_owner_final=read(C/'OWNER_FINAL.json'),CURB_owner_exit=read(C/'OWNER_EXIT_ACTUAL.json'),CURB_worker_exit=read(C/'WORKER_EXIT_ACTUAL.json'),E2_current=read(S/'OWNER_CURRENT.json'),E2_original_error=read(S/'OWNER_ORIGINAL_ERROR.json'),actual_own_processes=procs,canonical=dict(active=b['active_segment'],charged=b['charged_training_seconds'],remaining=b['remaining_training_seconds'],own_completed=[x for x in b['completed_segments'] if x.get('owner_parent_pid') in (480021,484739)]))))
''')
  src=result['source'];row=src.get('CURB_final')
  if row and src['CURB_owner_exit'] and not any(any(CURB in z for z in p.get('cmdline') or []) for p in src['actual_own_processes']):result['CURB_final_model']=download(c,row['final'],'closed_CURB35_actual_final/model.pt')
 finally:t.close(c)
 pw=getpass.getpass('Host72 own bounded source collection password (hidden): ');c=paramiko.SSHClient();c.load_system_host_keys();c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
 try:
  c.connect('10.24.0.72',username='lc01',password=pw,timeout=15,auth_timeout=20,banner_timeout=20,look_for_keys=False,allow_agent=False);pw=None;assert hashlib.sha256(c.get_transport().get_remote_server_key().asbytes()).hexdigest()=='301a9837e8503b664fa4cedde20407769d8f1b86ae59d9a54afb236bdfa41795';start=time.monotonic()
  script='ROOT='+repr(T)+'\n'+r'''
from pathlib import Path
import json,hashlib,time,psutil
B=Path(ROOT);files=[]
for p in list(B.glob('NODE_*.json'))+list(B.glob('*ORIGINAL_ERROR*.json'))+list(B.glob('job*/*/*.json'))+list(B.glob('job*/*ACTUAL.json'))+list(B.glob('job*/*STARTED.json')):
 if p.stat().st_size<15000000:
  try:files.append(dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest(),value=json.loads(p.read_bytes())))
  except (OSError,ValueError):pass
first=B/'job0/production/model_update1.pt';one=None
if first.exists() and not first.with_suffix('.pt.partial').exists():one=dict(path=str(first),bytes=first.stat().st_size,SHA=hashlib.sha256(first.read_bytes()).hexdigest())
procs=[]
for p in psutil.process_iter(['pid','create_time','cmdline','cwd']):
 try:
  if any(str(B) in z for z in p.info['cmdline'] or []):procs.append(p.info)
 except psutil.Error:pass
logs=[]
for p in B.glob('job*/*worker.log'):
 with p.open('rb') as f:f.seek(max(0,p.stat().st_size-2000));s=f.read().decode(errors='replace')
 logs.append(dict(path=str(p),tail=s))
print(json.dumps(dict(epoch=time.time(),files=files,first_production=one,actual_processes=procs,logs=logs,errors=[f for f in files if 'ORIGINAL_ERROR' in f['path']])))
'''
  while True:
   v=code(c,PY72,script)
   if v['first_production'] or v['errors'] or time.monotonic()-start>=900:break
   time.sleep(15)
  result['target72']=v;models=[]
  if v['first_production']:models.append(download(c,v['first_production'],'E2_complete_first_models/production_update1.pt'))
  for phase,name in [('native','own_native144.pt'),('precheck128','model_update2.pt'),('precheck20k','model_update4.pt')]:
   row=next((x['value'] for x in v['files'] if x['path'].endswith('/job0/'+phase+'/latest_complete.json')),None)
   if row and row['path'].endswith('/'+name):models.append(download(c,row,'E2_complete_first_models/'+phase+'.pt'))
  result['E2_local_models']=models;h1=next((x['value'] for x in v['files'] if x['path'].endswith('/job1/native/NATIVE144_COMPLETE.json')),None);raw=[]
  if h1:
   for i,row in enumerate(h1['chunks']):raw.append(download(c,row,'H1_native80_actual_raw/native_chunk_'+str(i)+'.npz'))
  result['H1_complete_raw_twohost']=raw
 finally:pw=None;c.close()
 put('E2_FIRST_FULLMODEL_H1_RAW_CURB_FINAL_V2_ACTUAL_BOUND_COLLECTION.json',result);print(json.dumps(dict(E2_models=result['E2_local_models'],H1_raw_files=len(raw),CURB_final_model=result.get('CURB_final_model'),target_errors=[r['path'] for r in v['errors']],lastlogs=v['logs'])),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:put('E2_FIRST_MODEL_H1_RAW_V2_COLLECTION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_PPO_or_budget_replay=True));raise
