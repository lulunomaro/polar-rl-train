"""One sequential bounded own-root read/collection; no dispatch or runtime mutation."""
from pathlib import Path
import json,time,os,sys,getpass,shlex,hashlib,paramiko,traceback
D=Path(__file__).resolve().parent;R=D/'reports';W=D.parent;S='/mnt/mod4_linux_durable_20261013/'+D.name;T='/home/lc01/Zonglin Li/zonglin2/tasks/'+D.name;C='/mnt/mod4_linux_durable_20261013/MOD4_E1_CURB35_FROM_878_NATIVE_TRAIN_20261016/production_fresh_process_v2'
sys.path.insert(0,str(W/'MOD4_LINUX_WAVE50_BODYFRAME_RESET_INTEGRATION_20261014'));import transport_bodyframe_root_owned as t
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def query(c,py,root):
 code=r'''
from pathlib import Path
import json,psutil,time,hashlib
B=Path(ROOT);files=[]
for p in list(B.glob('OWNER_*.json'))+list(B.glob('NODE_*.json'))+list(B.glob('*WORKER_ORIGINAL_ERROR*.json'))+list(B.glob('job*/*/*.json'))+list(B.glob('job*/*ACTUAL.json'))+list(B.glob('job*/*STARTED.json')):
 if p.stat().st_size<3000000:
  try:files.append(dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest(),value=json.loads(p.read_bytes())))
  except (OSError,ValueError):pass
procs=[]
for p in psutil.process_iter(['pid','create_time','cmdline','cwd']):
 try:
  if any(str(B) in z for z in p.info['cmdline'] or []) and any(z.endswith('.py') for z in p.info['cmdline'] or []):procs.append(p.info)
 except psutil.Error:pass
logs=[]
for p in B.glob('job*/*worker.log'):
 with p.open('rb') as f:f.seek(max(0,p.stat().st_size-2200));value=f.read().decode(errors='replace')
 logs.append(dict(path=str(p),tail=value))
print(json.dumps(dict(epoch=time.time(),root=str(B),files=files,actual_processes=procs,logs=logs)))
'''
 si,so,se=c.exec_command(shlex.quote(py)+' -B -',timeout=60);si.write('ROOT='+repr(root)+'\n'+code);si.flush();si.channel.shutdown_write();raw=so.read();err=se.read();assert so.channel.recv_exit_status()==0,err.decode();return json.loads(raw)
def get_model(c,row,out):
 assert not out.exists();out.parent.mkdir(parents=True,exist_ok=True);sf=c.open_sftp();sf.get_channel().settimeout(120);part=out.with_suffix('.pt.partial')
 try:sf.get(row['path'],str(part));assert part.stat().st_size==row['bytes'] and H(part)==row['SHA'];part.replace(out)
 finally:sf.close()
 return dict(path=str(out.resolve()),bytes=out.stat().st_size,SHA=H(out),remote=row['path'],twohost_bytes_SHA_exact=True)
def main():
 put('INITIAL_TWO_HOST_OWN_SCOPE_COLLECTION_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),finite_readonly_sequential=True));c=None;values={}
 try:
  c=t.connect();values['source_E2']=query(c,t.PY,S);values['source_CURB']=query(c,t.PY,C)
  code="from pathlib import Path;import json;v=json.loads(Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json').read_bytes());print(json.dumps(dict(active=v['active_segment'],charged=v['charged_training_seconds'],remaining=v['remaining_training_seconds'],own_completed=[x for x in v['completed_segments'] if x.get('owner_parent_pid') in (480021,484739)])))"
  si,so,se=c.exec_command(shlex.quote(t.PY)+' -B -',timeout=30);si.write(code);si.flush();si.channel.shutdown_write();raw=so.read();err=se.read();assert so.channel.recv_exit_status()==0,err.decode();values['actual_original_canonical']=json.loads(raw)
  final=next((r['value'] for r in values['source_CURB']['files'] if r['path'].endswith('/job0/production_only/FINAL.json')),None)
  if final and not values['source_CURB']['actual_processes']:values['CURB_final_local_model']=get_model(c,final['final'],D/'collected_closed_CURB35_final/model.pt')
 finally:t.close(c)
 pw=getpass.getpass('Host72 read-only own task password (hidden): ');c=paramiko.SSHClient();c.load_system_host_keys();c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
 try:
  c.connect('10.24.0.72',username='lc01',password=pw,timeout=15,auth_timeout=20,banner_timeout=20,allow_agent=False,look_for_keys=False);pw=None;assert hashlib.sha256(c.get_transport().get_remote_server_key().asbytes()).hexdigest()=='301a9837e8503b664fa4cedde20407769d8f1b86ae59d9a54afb236bdfa41795';values['target72']=query(c,'/home/lc01/Zonglin Li/zonglin2/run-python.sh',T)
  models=[]
  for job in (0,1):
   v=next((r['value'] for r in values['target72']['files'] if r['path'].endswith('/job'+str(job)+'/native/NATIVE144_COMPLETE.json')),None)
   if v:models.append(get_model(c,v['saved'],D/'collected_native_models'/('job'+str(job)+'.pt')))
  values['native_local_models']=models
 finally:pw=None;c.close()
 put('INITIAL_E2_H1_CURB_HANDOFF_ACTUAL_BOUND_COLLECTION.json',values)
 print(json.dumps(dict(source_E2_current=next((r['value'] for r in values['source_E2']['files'] if r['path'].endswith('/OWNER_CURRENT.json')),None),target_actual_processes=values['target72']['actual_processes'],target_errors=[r for r in values['target72']['files'] if 'ORIGINAL_ERROR' in r['path']],native_CPU=[r for r in values['target72']['files'] if r['path'].endswith('/NATIVE_ALL_ROWS_CPU_ADMITTED.json')],CURB_final_local_model=values.get('CURB_final_local_model'),lastlogs=values['target72']['logs'])),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:put('INITIAL_COLLECTION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_replay=True));raise
