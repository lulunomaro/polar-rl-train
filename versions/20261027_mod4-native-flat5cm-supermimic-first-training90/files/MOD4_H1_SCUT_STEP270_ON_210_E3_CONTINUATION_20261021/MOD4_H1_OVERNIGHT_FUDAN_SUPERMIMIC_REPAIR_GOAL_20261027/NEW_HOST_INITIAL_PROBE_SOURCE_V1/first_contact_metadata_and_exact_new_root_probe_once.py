"""ONE future first-contact probe. Credentials only stdin/memory; no auto retry.

Do not execute during source preparation. No keys/known_hosts files are loaded
or modified. Public peer key is saved before authentication for a future pin.
"""
from pathlib import Path
import base64,hashlib,json,os,queue,sys,threading,time,traceback
HERE=Path(__file__).resolve().parent
REPORTS=HERE/'reports'
HOST='10.50.0.86';USER='robemo';ROOT='/data/robemo/polar-rl-train'

REMOTE_SOURCE=r'''import os,sys,json,time,platform,subprocess,shutil,signal,importlib.util,importlib.metadata
from pathlib import Path
ROOT=Path('/data/robemo/polar-rl-train');PARENT=Path('/data/robemo')
probe_id=__PROBE_ID_JSON__
start=time.monotonic();deadline=start+85.
out=dict(schema='mod4.newhost86.initial_metadata_exact_new_root_probe.v1',probe_id=probe_id,host='10.50.0.86',username='robemo',requested_root=str(ROOT),root_modified=False,no_GPU_SDK_Torch_policy_or_ledger=True)
def alarm(signum,frame):raise TimeoutError('finite metadata probe85s elapsed')
def remaining():
 value=deadline-time.monotonic()
 if value<=0:raise TimeoutError('finite metadata probe expired')
 return value
def command(args):
 remaining()
 try:
  r=subprocess.run(args,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=min(12.,remaining()),check=False)
  return dict(argv=args,returncode=r.returncode,stdout=r.stdout[:100000],stderr=r.stderr[:10000])
 except Exception as e:return dict(argv=args,error_type=type(e).__name__,error=str(e))
try:
 if os.name!='posix' or not hasattr(signal,'SIGALRM'):raise RuntimeError('POSIX probe/root contract required; no mutation')
 signal.signal(signal.SIGALRM,alarm);signal.alarm(85)
 out['OS']=dict(system=platform.system(),release=platform.release(),machine=platform.machine(),uname=command(['uname','-srm']))
 if Path('/etc/os-release').is_file():out['OS']['os_release_text']=Path('/etc/os-release').read_text()[:20000]
 out['own_identity']=dict(uid=os.getuid(),gid=os.getgid(),python_executable=sys.executable,python_version=sys.version)
 import pwd
 actual_user=pwd.getpwuid(os.getuid()).pw_name;out['own_identity']['username']=actual_user
 if actual_user!='robemo':raise RuntimeError('wrong account; no mutation')
 if not PARENT.is_dir() or PARENT.resolve(strict=True)!=PARENT:raise RuntimeError('authorized existing parent absent or resolves elsewhere')
 parent_stat=PARENT.stat();out['parent']=dict(path=str(PARENT),resolved=str(PARENT.resolve()),uid=parent_stat.st_uid,gid=parent_stat.st_gid,mode=oct(parent_stat.st_mode&0o7777))
 out['exists_before']=ROOT.exists() or ROOT.is_symlink()
 marker=dict(schema='mod4.robemo.frozen_experts.workspace.v1',host='10.50.0.86',username='robemo',authorized_root=str(ROOT),project='MOD4_frozen_experts_PPO50_gas400',
  first_payload_frozen_index_SHA='8242c696e93883382f3dc9378ccf5fbee9a7f8d63ada08c5966aa44b9f0c9b4c',budget_writer_host='72',canonical_copied=False,initial_probe_id=probe_id)
 marker_path=ROOT/'.MOD4_NEW_HOST_WORKSPACE_MANIFEST_V1.json'
 if out['exists_before']:
  out['created_now']=False
  if ROOT.is_symlink() or not ROOT.is_dir() or ROOT.resolve(strict=True)!=ROOT:raise RuntimeError('existing root not exact resolved directory; untouched')
  same=False
  if marker_path.is_file() and not marker_path.is_symlink() and marker_path.stat().st_size<=65536:
   try:same=json.loads(marker_path.read_bytes())==marker
   except Exception:same=False
  if not same:raise RuntimeError('root already exists without THIS probe marker; untouched, not listed, no overwrite')
  out['same_probe_marker_present']=True
 # Read-only distribution/path metadata; never import torch/SDK packages.
 out['python']=dict(executable=sys.executable,version=sys.version,find_spec={},distributions={})
 for name in ('torch','rsl_rl','isaaclab','isaacsim','numpy','pxr'):
  try:
   s=importlib.util.find_spec(name);out['python']['find_spec'][name]=None if s is None else dict(origin=s.origin,locations=list(s.submodule_search_locations or []))
  except Exception as e:out['python']['find_spec'][name]=dict(error_type=type(e).__name__,error=str(e))
 for name in ('torch','rsl-rl-lib','isaaclab','isaacsim','numpy'):
  try:
   d=importlib.metadata.distribution(name);out['python']['distributions'][name]=dict(version=d.version,metadata_location=str(d.locate_file('')))
  except importlib.metadata.PackageNotFoundError:out['python']['distributions'][name]=None
 out['GPU_UUID_name_memory_util']=command(['nvidia-smi','--query-gpu=uuid,name,memory.total,memory.free,utilization.gpu','--format=csv,noheader,nounits'])
 out['compute_GPU_UUID_only']=command(['nvidia-smi','--query-compute-apps=gpu_uuid','--format=csv,noheader,nounits'])
 disk=shutil.disk_usage(PARENT);out['disk']=dict(path=str(PARENT),total=disk.total,used=disk.used,free=disk.free)
 if Path('/proc/meminfo').is_file():out['RAM_meminfo_text']=Path('/proc/meminfo').read_text()[:20000]
 remaining()
 if not out['exists_before']:
  os.mkdir(ROOT,0o700) # Exactly one child; never mkdir parents/replace/chmod.
  out.update(created_now=True,root_modified=True)
  if ROOT.resolve(strict=True)!=ROOT:raise RuntimeError('created root resolves elsewhere; no follow-up mutation/cleanup')
  flags=os.O_WRONLY|os.O_CREAT|os.O_EXCL|getattr(os,'O_NOFOLLOW',0)
  fd=os.open(marker_path,flags,0o600)
  with os.fdopen(fd,'w',encoding='utf8') as f:json.dump(marker,f,ensure_ascii=False,indent=2);f.flush();os.fsync(f.fileno())
  out['scope_marker_written_exclusively']=True
 out.update(passed_metadata_probe=True,exists_after=ROOT.is_dir(),resolved_root=str(ROOT.resolve(strict=True)),scope_marker=marker,
  no_unknown_PID_argv_exe_process_query=True,no_other_directories_or_system_environment_modified=True,actual_training_or_GPU_admission=False)
except BaseException as e:
 out.update(passed_metadata_probe=False,error_type=type(e).__name__,error=str(e),no_retry_cleanup_or_overwrite=True)
finally:
 try:signal.alarm(0)
 except Exception:pass
 out['probe_wall_seconds']=time.monotonic()-start
 print(json.dumps(out,ensure_ascii=False),flush=True)
sys.exit(0 if out.get('passed_metadata_probe') else 43)
'''

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write(name,value):
 with (REPORTS/name).open('x',encoding='utf8') as f:json.dump(value,f,ensure_ascii=False,indent=2)
def sanitized(value,secret):
 if isinstance(value,str):return value.replace(secret,'[REDACTED]') if isinstance(secret,str) and secret else value
 if isinstance(value,dict):return {k:sanitized(v,secret) for k,v in value.items() if k.lower() not in ('password','credential','secret')}
 if isinstance(value,list):return [sanitized(v,secret) for v in value]
 return value

def main():
 REPORTS.mkdir(exist_ok=True)
 entered=REPORTS/'INITIAL_PROBE_ENTERED_ACTUAL.json'
 if entered.exists():raise RuntimeError('first probe already consumed; no retry')
 probe_id='MOD4_NEW_HOST_INITIAL_PROBE_'+str(time.time_ns())
 write(entered.name,dict(epoch=time.time(),probe_id=probe_id,host=HOST,username=USER,source_SHA=sha(__file__),own_local_pid=os.getpid(),credentials_stdin_memory_only=True))
 secret=None;client=None;peer={};started=time.monotonic()
 try:
  line=sys.stdin.readline(65537)
  if not line or len(line)>65536:raise ValueError('one bounded JSON stdin object required')
  request=json.loads(line);line=None
  if set(request)!={'host','username','password'} or request['host']!=HOST or request['username']!=USER:raise ValueError('exact authorized new host/user request required')
  secret=request.pop('password');request=None
  if not isinstance(secret,str) or not secret:raise ValueError('nonempty stdin credential required')
  import paramiko
  import logging
  logger=logging.getLogger('paramiko');logger.addHandler(logging.NullHandler());logger.propagate=False;logger.setLevel(logging.CRITICAL+1)
  class FirstPeer(paramiko.MissingHostKeyPolicy):
   def missing_host_key(self,ssh,hostname,key):
    raw=key.asbytes();peer.update(host=HOST,server_name=hostname,algorithm=key.get_name(),public_key_SHA256=hashlib.sha256(raw).hexdigest(),
     fingerprint_SHA256='SHA256:'+base64.b64encode(hashlib.sha256(raw).digest()).decode().rstrip('='),public_key_base64=key.get_base64(),
     first_contact_accepted_in_memory_only=True,no_old210_or72_pin_used=True,no_known_hosts_file_read_or_write=True)
    write('FIRST_PEER_PUBLIC_HOSTKEY_ACTUAL.json',peer)
  client=paramiko.SSHClient();client.set_missing_host_key_policy(FirstPeer())
  result=queue.Queue(maxsize=1)
  def connect():
   try:
    client.connect(HOST,port=22,username=USER,password=secret,timeout=15,auth_timeout=15,banner_timeout=15,allow_agent=False,look_for_keys=False)
    result.put(None)
   except BaseException as e:result.put(e)
  thread=threading.Thread(target=connect,daemon=True);thread.start();thread.join(15)
  if thread.is_alive():client.close();raise TimeoutError('total connect/auth15s elapsed; no retry')
  error=result.get_nowait()
  if error is not None:raise error
  if not peer:raise RuntimeError('first peer key evidence absent; no probe')
  import shlex
  code=REMOTE_SOURCE.replace('__PROBE_ID_JSON__',json.dumps(probe_id))
  command="p=$(command -v python3) || { printf '%s\\n' '{\"error\":\"python3 absent; no mkdir\"}'; exit 41; }; exec env PYTHONDONTWRITEBYTECODE=1 PYTHONNOUSERSITE=1 \"$p\" -B -u -c "+shlex.quote(code)
  transport=client.get_transport();probe_result=queue.Queue(maxsize=1)
  def probe():
   channel=None
   try:
    channel=transport.open_session(timeout=10);channel.settimeout(90);channel.exec_command(command)
    out=bytearray();err=bytearray();deadline=time.monotonic()+90
    while True:
     if time.monotonic()>deadline:raise TimeoutError('probe90s elapsed')
     if channel.recv_ready():out.extend(channel.recv(65536))
     if channel.recv_stderr_ready():err.extend(channel.recv_stderr(65536))
     if len(out)>2000000 or len(err)>200000:raise RuntimeError('bounded metadata output exceeded')
     if channel.exit_status_ready() and not channel.recv_ready() and not channel.recv_stderr_ready():break
     time.sleep(.05)
    probe_result.put(dict(returncode=channel.recv_exit_status(),stdout=out.decode('utf8','replace'),stderr=err.decode('utf8','replace')))
   except BaseException as e:probe_result.put(e)
   finally:
    if channel:channel.close()
  pt=threading.Thread(target=probe,daemon=True);pt.start();pt.join(90)
  if pt.is_alive():client.close();raise TimeoutError('total probe90s elapsed; no retry')
  response=probe_result.get_nowait()
  if isinstance(response,BaseException):raise response
  try:value=json.loads(response['stdout'])
  except Exception:value=dict(metadata_JSON_missing=True,stdout=response['stdout'])
  receipt=sanitized(dict(epoch=time.time(),probe_id=probe_id,host=HOST,username=USER,public_hostkey=peer,remote=value,
   remote_returncode=response['returncode'],remote_stderr=response['stderr'],transport_returned=True,wall_seconds=time.monotonic()-started,
   no_Torch_SDK_GPUload_training_GO_or_ledger=True,credentials_not_in_argv_files_or_output=True),secret)
  write('INITIAL_NEW_HOST_PROBE_RETURNED_ACTUAL.json',receipt)
  passed=response['returncode']==0 and value.get('passed_metadata_probe') is True
  print(json.dumps(dict(passed=passed,report=str(REPORTS/'INITIAL_NEW_HOST_PROBE_RETURNED_ACTUAL.json'),report_SHA=sha(REPORTS/'INITIAL_NEW_HOST_PROBE_RETURNED_ACTUAL.json'),actual_training=False)),flush=True)
  if not passed:raise RuntimeError('new host probe returned original failure; see sanitized receipt; no retry')
 except BaseException as e:
  value=sanitized(dict(epoch=time.time(),probe_id=probe_id,host=HOST,username=USER,error_type=type(e).__name__,error=str(e),
   traceback=traceback.format_exc(),public_hostkey=peer,no_retry_or_cleanup=True,credentials_not_recorded=True),secret)
  write('INITIAL_NEW_HOST_PROBE_ORIGINAL_ERROR_ACTUAL.json',value)
  print(json.dumps(dict(passed=False,error_report=str(REPORTS/'INITIAL_NEW_HOST_PROBE_ORIGINAL_ERROR_ACTUAL.json'),no_retry=True)),flush=True)
  return 1
 finally:
  if client:client.close()
  secret=None
 return 0
if __name__=='__main__':raise SystemExit(main())
