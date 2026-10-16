"""One read-only collection after the earlier finite collector naturally returned.

Never starts/repeats any native, GPU, optimizer, or learning parent.
"""
from pathlib import Path
import sys,json,time,hashlib,getpass,paramiko,traceback,os,subprocess
D=Path(__file__).resolve().parent;R=D/'reports';ROOT='/home/lc01/Zonglin Li/zonglin2/tasks/'+D.name;PY='/home/lc01/Zonglin Li/zonglin2/run-python.sh'
sys.path.insert(0,str(D));from deploy_H1_fullstate_native_and_collect_own_scope_finite_v1_once import code,H
def put(name,value):
 with (R/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2)
def main():
 put('H1_NATIVE_POST_BOUND_READONLY_V2_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),creation_UTC=subprocess.check_output(['powershell','-NoProfile','-Command',"(Get-Process -Id %d).StartTime.ToUniversalTime().ToString('o')"%os.getpid()]).decode().strip(),one_readonly_connection=True,no_native_or_PPO_launch=True))
 pw=getpass.getpass('Host72 existing native read-only collection password (hidden): ');c=paramiko.SSHClient();c.load_system_host_keys();c.set_missing_host_key_policy(paramiko.AutoAddPolicy());sf=None
 try:
  c.connect('10.24.0.72',username='lc01',password=pw,timeout=15,auth_timeout=20,banner_timeout=20,look_for_keys=False,allow_agent=False);pw=None;assert hashlib.sha256(c.get_transport().get_remote_server_key().asbytes()).hexdigest()=='301a9837e8503b664fa4cedde20407769d8f1b86ae59d9a54afb236bdfa41795'
  v=code(c,PY,r'''
from pathlib import Path
import sys,json,time,hashlib,psutil,fcntl
B=Path(sys.argv[1]);files=[]
for p in list(B.glob('*.json'))+list((B/'job0/native').glob('*.json')):
 raw=p.read_bytes();row=dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest())
 if p.name!='PAYLOAD_H1_FULLSTATE_MANIFEST_V2.json':
  try:row['value']=json.loads(raw)
  except ValueError:row['json_parse_failed']=True
 files.append(row)
scripts={str(B/n) for n in ('h1_native_finite_parent_v1.py','h1_fullstate_native_worker_v1.py','review_H1_full20k_native_allrows_CPU_v1.py')};procs=[]
for p in psutil.process_iter(['pid','create_time','cmdline','cwd']):
 try:
  if any(x in scripts for x in p.info['cmdline'] or []):procs.append(p.info)
 except psutil.Error:pass
lock=Path('/home/lc01/Zonglin Li/zonglin2/state/finite_environment_validation.lock')
with lock.open('rb+') as f:
 try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
 except BlockingIOError:held=True
 else:held=False;fcntl.flock(f,fcntl.LOCK_UN)
print(json.dumps(dict(epoch=time.time(),files=files,actual_processes=procs,parent_final=(B/'PARENT_FINAL.json').exists(),parent_exit=(B/'PARENT_EXIT_ACTUAL.json').exists(),validation_actual_fcntl_held=held,readonly_no_GPU_or_PPO=True)))
''',ROOT)
  models=[];complete=next((x.get('value') for x in v['files'] if x['path'].endswith('/NATIVE300_COMPLETE_ACTUAL.json')),None)
  if v['parent_exit'] and not v['actual_processes'] and complete:
   out=D/'actual_complete_native_models';out.mkdir(exist_ok=True);sf=c.open_sftp();sf.get_channel().settimeout(120)
   for key in ('initial','saved'):
    row=complete[key];p=out/(key+'.pt');assert not p.exists();tmp=p.with_suffix('.pt.partial');sf.get(row['path'],str(tmp));assert tmp.stat().st_size==row['bytes'] and H(tmp)==row['SHA'];tmp.replace(p);models.append(dict(path=str(p.resolve()),bytes=p.stat().st_size,SHA=H(p),remote=row['path'],twohost_bytes_SHA_exact=True))
   sf.close();sf=None
  v['local_models']=models;put('H1_NATIVE_POST_BOUND_READONLY_V2_COMPLETE_ACTUAL.json',v)
  short=[]
  for row in v['files']:
   n=Path(row['path']).name;x=row.get('value',{})
   if n in ('CURRENT_ACTUAL.json','PARENT_FINAL.json','PARENT_EXIT_ACTUAL.json','H1_NATIVE_FULL20K_ALL_ROWS_CPU_ADMITTED.json') or 'ORIGINAL_ERROR' in n:short.append(dict(name=n,value=x))
  print(json.dumps(dict(parent_final=v['parent_final'],parent_exit=v['parent_exit'],actual_processes=v['actual_processes'],validation_actual_fcntl_held=v['validation_actual_fcntl_held'],selected=short,local_models=models)),flush=True)
 finally:
  pw=None
  if sf:sf.close()
  c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('H1_NATIVE_POST_BOUND_READONLY_V2_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),unknown_mutation_none_readonly=True,no_GPU_replay=True));raise
