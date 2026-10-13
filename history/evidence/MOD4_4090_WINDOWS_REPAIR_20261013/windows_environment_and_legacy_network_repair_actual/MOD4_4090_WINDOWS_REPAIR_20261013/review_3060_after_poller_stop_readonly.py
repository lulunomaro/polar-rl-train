from pathlib import Path
import sys,os,json,time,base64,hashlib,traceback
D=Path(__file__).resolve().parent; W=D.parent
CODE=r'''
import psutil,time,json,socket,subprocess,importlib.metadata as m,hashlib
from pathlib import Path
def identity(pid):
 try:
  p=psutil.Process(pid); argv=p.cmdline(); safe=[]; hidden=False
  for v in argv:
   if hidden: safe.append('[REDACTED]');hidden=False;continue
   if any(w in v.lower() for w in ['password','passwd','secret','token=','private key']):safe.append('[REDACTED_ARGUMENT]');hidden=True
   else:safe.append(v)
  return dict(pid=pid,creation=p.create_time(),exe=p.exe(),argv=safe,parent=p.ppid())
 except Exception as e:return dict(pid=pid,error=type(e).__name__)
rows=[]; errors=[]
try:
 for c in psutil.net_connections(kind='tcp'):
  if c.raddr and c.raddr.ip in ('10.24.4.210','172.27.131.74'):
   rows.append(dict(local=list(c.laddr),remote=list(c.raddr),status=c.status,pid=c.pid,process=identity(c.pid) if c.pid else None))
except Exception as e:errors.append(dict(scope='net_connections',error=repr(e)))
versions={}
for n in ['isaacsim','isaaclab','isaaclab-rl','torch','tensordict','rsl-rl-lib','warp-lang','numpy','scipy','gymnasium']:
 try:versions[n]=m.version(n)
 except m.PackageNotFoundError:versions[n]=None
old=[]
for pid,creation in [(2924,1791772440.1488748),(8664,1791772440.1525493)]:
 try:p=psutil.Process(pid); old.append(dict(pid=pid,original_identity_present=abs(p.create_time()-creation)<.001,current=identity(pid)))
 except psutil.NoSuchProcess:old.append(dict(pid=pid,original_identity_present=False))
task=subprocess.run(['schtasks','/Query','/TN','MOD4_AsyncFrozenEvaluation_v15_e1_wave50_query_review','/XML'],capture_output=True)
print(json.dumps(dict(epoch=time.time(),hostname=socket.gethostname(),target_210_or_ZT_outbound_connections=rows,metadata_versions=versions,old_poller_identities=old,task_query_returncode=task.returncode,task_disabled_XML_contains_false=(b'<Enabled>false</Enabled>' in task.stdout or '<Enabled>false</Enabled>'.encode('utf16le') in task.stdout),task_XML_sha256=hashlib.sha256(task.stdout).hexdigest(),errors=errors,read_only=True,no_connect_to_210_from_3060=True,no_GPU_import_or_launch=True,no_service_or_process_mutation=True)))
'''
def main():
 sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'))
 from reuse_authorized_session_transport import recover
 secret,_=recover('MOD4_EVAL_SSH_PASSWORD');assert secret;os.environ['MOD4_EVAL_SSH_PASSWORD']=secret
 sys.path.insert(0,str(W/'MOD4_MOE_PLAN_EXECUTION_20261007'))
 from eval_remote_io import connect_eval
 c=connect_eval(); stamp=str(time.time_ns())
 try:
  enc=base64.b64encode(CODE.encode()).decode()
  cmd='"D:/claude2/fangzhen/.venv-isaaclab/Scripts/python.exe" -X utf8 -c "import base64;exec(base64.b64decode(\''+enc+'\'))"'
  _,o,e=c.exec_command(cmd,timeout=45);raw=o.read();err=e.read();rc=o.channel.recv_exit_status()
  if rc:raise RuntimeError('readonly collector returned '+str(rc)+': '+err.decode('utf8','replace'))
  a=json.loads(raw); sf=c.open_sftp(); indexed=[]
  try:
   for name in ['ORIGINAL_OLD_POLLER_TASK.xml','DISABLED_OLD_POLLER_TASK.xml']:
    remote='D:/MOD4_async_eval/windows4090_transition_20261013/'+name
    with sf.open(remote,'rb') as f:b=f.read()
    local=D/'reports'/name
    if local.exists():assert local.read_bytes()==b
    else:local.write_bytes(b)
    indexed.append(dict(path=str(local),remote_path=remote,size_bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),remote_bytes_local_exact=True))
  finally:sf.close()
  a['retired_task_XML_collected']=indexed
  p=D/'reports'/('3060_POST_RETIREMENT_OUTBOUND_READONLY_ACTUAL_'+stamp+'.json');p.write_text(json.dumps(a,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(a,ensure_ascii=False))
 except Exception as e:
  p=D/'reports'/('3060_POST_RETIREMENT_READER_ERROR_'+stamp+'.json');p.write_text(json.dumps(dict(epoch=time.time(),error=repr(e),traceback=traceback.format_exc(),read_only=True)),encoding='utf8');raise
 finally:c.close();os.environ.pop('MOD4_EVAL_SSH_PASSWORD',None)
if __name__=='__main__':main()
