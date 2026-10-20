"""One max600s missing-evidence reader; no training, mutation or model downloads."""
from pathlib import Path,PurePosixPath
import getpass,hashlib,json,os,shlex,sys,time,traceback
import paramiko
B=Path(__file__).resolve().parent;R=B/'reports'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
READ=r'''
from pathlib import Path
import sys,time,json,psutil,os,subprocess,hashlib
C=Path(sys.argv[1]);read=lambda p:json.loads(p.read_bytes()) if p.is_file() else None;until=time.monotonic()+580
while True:
 current=read(C/'SERIES_CURRENT.json') or {};error=read(C/'SERIES_ORIGINAL_ERROR.json');active=current.get('active') or {};window=C.parent/'windows/hour0001';node=window/'recovery';nc=read(node/'NODE_CURRENT.json') or {};row=nc.get('row') or {};go=read(node/'job0/GO_PRODUCTION.json');saved=read(node/'job0/production/PPO_POSITIVE_CURRENT.json');native=read(node/'POLICY50_CLOCK_RUNTIME_CPU_ADMITTED_ACTUAL.json');clock=read(node/'job0/production/POLICY50_ACTUAL_CLOCK_AND_INHERITANCE.json');errors=[str(p) for folder in (node,node/'job0/clock_native50',node/'job0/production') for p in folder.glob('*ORIGINAL_ERROR*.json')];complete=bool(go and saved and saved.get('updates',0)>0 and native and native['passed'] and clock and clock['policy_hz']==50)
 if complete or error or errors or (C/'SERIES_EXIT_ACTUAL.json').exists() or time.monotonic()>=until:break
 time.sleep(3)
own=[]
for p in psutil.process_iter(['pid','create_time','cmdline','exe']):
 try:
  if p.pid!=os.getpid() and any(x.startswith(str(C.parent)+'/') for x in p.info['cmdline'] or []):own.append(p.info)
 except psutil.Error:pass
compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']).decode();worker=row.get('worker') or {};identity=read(C/'SERIES_IDENTITY.json') or {};worker_ok=any(p['pid']==worker.get('pid') and abs(p['create_time']-worker.get('creation',-1))<.01 and p['cmdline']==worker.get('argv') for p in own);compute_ok=any(len(z:=line.split(','))>=2 and z[0].strip()=='GPU-c27eecbd-6838-7290-1cd2-37e34522213d' and z[1].strip()==str(worker.get('pid')) for line in compute.splitlines());parent_ok=any(p['pid']==identity.get('pid') and abs(p['create_time']-identity.get('creation',-1))<.01 and p['cmdline'][-1]==str(C/'auto_E3_serial_supervisor_v1.py') for p in own)
texts=[];allowed={'.py','.json','.jsonl','.log','.txt','.md','.sh','.yaml','.yml','.toml','.csv'}
for root in (C,window):
 if not root.exists():continue
 for p in sorted(root.rglob('*')):
  if p.is_file() and not p.is_symlink() and '__pycache__' not in p.parts and p.suffix in allowed:
   raw=p.read_bytes();texts.append(dict(path=str(p),relative=p.relative_to(C.parent).as_posix(),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
print(json.dumps(dict(epoch=time.time(),root=str(C),series_current=current,series_error=error,series_exit=read(C/'SERIES_EXIT_ACTUAL.json'),GO=go,latest_PPO=saved,actual_clock=clock,actual_clock_native_CPU=native,node_current=nc,worker=worker,identity=identity,actual_own_processes=own,compute_snapshot=compute,positive_PPO=bool(complete),matching_worker_creation_argv=worker_ok,matching_GPU_UUID_compute=compute_ok,matching_parent_identity=parent_ok,actual_50Hz_learning_verified=complete and worker_ok and compute_ok and parent_ok,errors=errors,text_files=texts,no_GPU_or_Task_or_model_or_canonical_write=True)))
'''
def main():
 dispatch=json.loads((R/'POLICY50_V4_SERIAL_PARENT_DEPLOYED_ACTUAL.json').read_bytes());put('POLICY50_V4_FIRST_METADATA_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,max_remote_seconds=600));pw=getpass.getpass('72 first 50Hz evidence (hidden): ');c=paramiko.SSHClient();c.load_system_host_keys();c.set_missing_host_key_policy(paramiko.RejectPolicy())
 try:
  c.connect('10.24.0.72',username='lc01',password=pw,look_for_keys=False,allow_agent=False,timeout=15,auth_timeout=20,banner_timeout=20);pw=None;assert hashlib.sha256(c.get_transport().get_remote_server_key().asbytes()).hexdigest()=='301a9837e8503b664fa4cedde20407769d8f1b86ae59d9a54afb236bdfa41795';c.get_transport().set_keepalive(15)
  cmd=shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -u -B -c '+shlex.quote(READ)+' '+shlex.quote(dispatch['root']);_,out,err=c.exec_command(cmd,timeout=600);raw=out.read().decode();error=err.read().decode();rc=out.channel.recv_exit_status();assert rc==0,(raw,error);v=json.loads(raw);put('POLICY50_V4_FIRST_METADATA_REMOTE_ACTUAL.json',v);sf=c.open_sftp();sf.get_channel().settimeout(90);captured=[]
  try:
   for row in v['text_files']:
    rel=PurePosixPath(row['relative']);assert not rel.is_absolute() and '..' not in rel.parts;p=B/'remote_snapshot_policy50_V4'/Path(*rel.parts);p.parent.mkdir(parents=True,exist_ok=True)
    with sf.file(row['path'],'rb') as f:data=f.read()
    with p.open('xb') as f:f.write(data)
    captured.append(dict(remote_path=row['path'],local_path=str(p),inventory_SHA=row['SHA'],captured_SHA=hashlib.sha256(data).hexdigest(),bytes=len(data),snapshot_changed=hashlib.sha256(data).hexdigest()!=row['SHA']))
  finally:sf.close()
  put('POLICY50_V4_FIRST_METADATA_FINITE_RETURNED_ACTUAL.json',dict(epoch=time.time(),actual=v,captured_texts=captured,actual_finite_transport_returned=True,no_model_download_or_GPU_or_canonical_write=True));print(json.dumps(dict(actual_50Hz_learning_verified=v['actual_50Hz_learning_verified'],positive_PPO=v['positive_PPO'],matching_worker=v['matching_worker_creation_argv'],matching_GPU=v['matching_GPU_UUID_compute'],errors=v['errors'],captured_texts=len(captured))),flush=True)
 finally:pw=None;c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('POLICY50_V4_FIRST_METADATA_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_replay_once_or_GPU=True));raise
