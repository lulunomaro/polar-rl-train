from pathlib import Path
import getpass,hashlib,importlib.util,json,os,shlex,subprocess,sys,time,traceback
import paramiko
B=Path(__file__).resolve().parent;R=B/'reports';R.mkdir(exist_ok=True)
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
READ=r'''
from pathlib import Path
import fcntl,json,os,psutil,shutil,subprocess,time
base=Path('/home/lc01/Zonglin Li/zonglin2');series=base/'tasks/E3auto50_2010v30';locks=[]
for name in ('three_expert_v2_GPU-16828f91-2b45-b646-8dc0-9481138e2842.lock','three_expert_v2_GPU-c27eecbd-6838-7290-1cd2-37e34522213d.lock','finite_environment_validation.lock'):
 p=base/'state'/name;row=dict(path=str(p),exists=p.exists())
 if p.exists():
  with p.open('rb+') as f:
   try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);row['actual_fcntl_free']=True;fcntl.flock(f,fcntl.LOCK_UN)
   except BlockingIOError:row['actual_fcntl_free']=False
 locks.append(row)
own=[]
for p in psutil.process_iter(['pid','create_time','cmdline','exe']):
 try:
  if p.pid!=os.getpid() and any(x.startswith(str(series)+'/') for x in p.info['cmdline'] or []):own.append(p.info)
 except psutil.Error:pass
def run(args):return subprocess.check_output(args,timeout=20,text=True).strip()
print(json.dumps(dict(epoch=time.time(),GPU=run(['nvidia-smi','--query-gpu=index,name,uuid,memory.total,memory.used,memory.free,utilization.gpu','--format=csv,noheader,nounits']),compute=run(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']),RAM_available_bytes=psutil.virtual_memory().available,disk=dict(zip(('total','used','free'),shutil.disk_usage(base))),locks=locks,only_project_own_process_identities=own,peer_identities_not_queried=True,no_training_or_model_or_account_changes=True)))
'''
def main():
 put('GPU_AVAILABILITY_READER_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,one_finite_reader_no_training_dispatch=True))
 pw=getpass.getpass('72 read-only GPU availability (hidden): ');result=dict(local_receipt_epoch=time.time())
 try:
  try:result['local_GPU']=subprocess.check_output(['nvidia-smi','--query-gpu=index,name,uuid,memory.total,memory.used,memory.free,utilization.gpu','--format=csv,noheader,nounits'],timeout=20,text=True).strip()
  except Exception:result['local_GPU_error']=traceback.format_exc()
  c=paramiko.SSHClient();c.load_system_host_keys();c.set_missing_host_key_policy(paramiko.RejectPolicy())
  try:
   c.connect('10.24.0.72',username='lc01',password=pw,look_for_keys=False,allow_agent=False,timeout=15,auth_timeout=20,banner_timeout=20);pw=None
   assert hashlib.sha256(c.get_transport().get_remote_server_key().asbytes()).hexdigest()=='301a9837e8503b664fa4cedde20407769d8f1b86ae59d9a54afb236bdfa41795'
   c.get_transport().set_keepalive(15);cmd=shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -u -B -c '+shlex.quote(READ);_,out,err=c.exec_command(cmd,timeout=60);raw=out.read().decode();error=err.read().decode();rc=out.channel.recv_exit_status();assert rc==0,(raw,error);result['host72']=json.loads(raw)
  finally:c.close();pw=None
  try:
   p=B.parent/'MOD4_4090_WINDOWS_REPAIR_20261013/windows4090_native_transport.py';sp=importlib.util.spec_from_file_location('existing_pinned_210_readonly_transport',p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
   code="[Console]::OutputEncoding=[System.Text.UTF8Encoding]::new($false); $os=Get-CimInstance Win32_OperatingSystem; [ordered]@{caption=$os.Caption;version=$os.Version;GPU=((& nvidia-smi.exe --query-gpu=index,name,uuid,memory.total,memory.used,memory.free,utilization.gpu --format=csv,noheader,nounits) -join [Environment]::NewLine);compute=((& nvidia-smi.exe --query-compute-apps=gpu_uuid,pid,used_gpu_memory --format=csv,noheader,nounits) -join [Environment]::NewLine)}|ConvertTo-Json -Depth 4"
   before=time.time();raw=m.powershell(None,code,timeout=60);result['host210']=dict(local_before_epoch=before,local_after_epoch=time.time(),actual=json.loads(raw),strict_existing_Windows_pin=True,original_Linux_pin_untouched=True)
  except Exception:result['host210_error']=traceback.format_exc()
  result.update(epoch=time.time(),actual_finite_transport_returned=True,no_training_or_model_or_canonical_or_peer_identity_changes=True,all_values_are_instant_snapshots=True,host249_not_queried=True);put('CURRENT_GPU_AVAILABILITY_READONLY_RETURNED_ACTUAL.json',result);print(json.dumps(result,ensure_ascii=False),flush=True)
 finally:pw=None
if __name__=='__main__':
 try:main()
 except BaseException:put('GPU_AVAILABILITY_READER_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),error=traceback.format_exc(),no_replay_once=True));raise
