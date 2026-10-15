"""One bounded, exclusively named owned-root payload with complete failure collection."""
from pathlib import Path
import argparse,getpass,hashlib,json,os,shlex,subprocess,sys,threading,time,traceback,paramiko
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';ROOT='/home/lc01/Zonglin Li/zonglin2'
def put(name,v):
 with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--label',required=True);a=p.parse_args()
 assert Path(a.source).name==a.source and a.source.endswith('.py') and a.label.replace('_','').isalnum()
 prefix='OWNED72_'+a.label;assert not (R/(prefix+'_STARTED.json')).exists()
 source=D/'payload'/a.source;raw=source.read_bytes()
 prev=json.loads((W/'MOD4_HOST72_DUAL4090_ENV_READONLY_20261015/reports/HOST72_READONLY_DISCOVERY_ACTUAL.json').read_bytes())
 c=paramiko.SSHClient();c.load_system_host_keys();c.set_missing_host_key_policy(paramiko.AutoAddPolicy());sf=None
 pw=getpass.getpass('Host72 SSH password (hidden, not saved): ')
 try:
  c.connect(prev['host'],username=prev['user'],password=pw,timeout=15,auth_timeout=20,banner_timeout=20,allow_agent=False,look_for_keys=False);pw=None
  assert hashlib.sha256(c.get_transport().get_remote_server_key().asbytes()).hexdigest()==prev['remote_host_key_SHA256_hex']
  sf=c.open_sftp();sf.get_channel().settimeout(60);target=ROOT+'/audit/'+a.source
  with sf.open(target,'wx') as f:f.write(raw)
  ci=subprocess.run(['powershell','-NoProfile','-Command','$p=Get-CimInstance Win32_Process -Filter "ProcessId = '+str(os.getpid())+'";$p|Select-Object ProcessId,CreationDate,CommandLine|ConvertTo-Json -Compress'],capture_output=True,text=True,encoding='utf8',check=True)
  put(prefix+'_STARTED.json',dict(epoch=time.time(),pid=os.getpid(),actual_CIM=json.loads(ci.stdout),argv=sys.argv,source_SHA=hashlib.sha256(raw).hexdigest(),target=target,exclusive_target72_transport_while_actual_alive=True))
  _,so,se=c.exec_command('python3 -B '+shlex.quote(target),timeout=600)
  errors=[];t=threading.Thread(target=lambda:errors.append(se.read()),daemon=True);t.start();out=so.read();t.join();err=b''.join(errors);rc=so.channel.recv_exit_status()
  put(prefix+'_COMMAND_ACTUAL.json',dict(epoch=time.time(),returncode=rc,stdout=out.decode(errors='replace'),stderr=err.decode(errors='replace')))
  rows=[];deferred=[]
  for folder in ('audit','logs'):
   for s in sf.listdir_attr(ROOT+'/'+folder):
    if s.st_mode&0o170000!=0o100000:continue
    remote=ROOT+'/'+folder+'/'+s.filename
    if s.filename.endswith('.py') or s.st_size>8*1024*1024:
     deferred.append(dict(path=remote,bytes=s.st_size,reason='source_already_local_or_large_index_pending_final_stream_SHA'));continue
    with sf.open(remote,'rb') as f:b=f.read()
    local=D/'actual_target72'/prefix/folder/s.filename;local.parent.mkdir(parents=True,exist_ok=True);assert not local.exists();local.write_bytes(b)
    rows.append(dict(remote_path=remote,local_path=str(local),bytes=len(b),sha256=hashlib.sha256(b).hexdigest()))
  put(prefix+'_BOUNDARY_COLLECTED_ACTUAL.json',dict(epoch=time.time(),returncode=rc,files=rows,deferred=deferred,no_delete_signal_budget_or_runtime_replay=True))
  print(json.dumps(dict(label=a.label,returncode=rc,collected=len(rows),stdout=out.decode(errors='replace')[-2500:],stderr=err.decode(errors='replace')[-3500:])),flush=True)
  assert rc==0,'Read preserved actual outputs before any new scope.'
 finally:
  pw=None
  if sf:sf.close()
  c.close()
if __name__=='__main__':
 try:main()
 except BaseException:
  put('OWNED72_FRESH_PAYLOAD_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_blind_replay_delete_signal_or_budget=True));raise
