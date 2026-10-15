from pathlib import Path
import getpass,hashlib,json,secrets,shlex,sys,tarfile,time,traceback,paramiko
D=Path(__file__).resolve().parent;Q=D/'payload';R=D/'reports';W=D.parent
sys.path.insert(0,str(W/'MOD4_LINUX_WAVE50_BODYFRAME_RESET_INTEGRATION_20261014'));import transport_bodyframe_root_owned as t
RUNID=D.name;SOURCE='/mnt/mod4_linux_durable_20261013/'+RUNID;TARGET='/home/lc01/Zonglin Li/zonglin2/tasks/'+RUNID
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
EXTRACT=r'''
from pathlib import Path,PurePosixPath
import tarfile,hashlib,json,sys
base=Path(sys.argv[1]);archive=Path(str(base)+'.tar.gz');assert not base.exists();assert hashlib.sha256(archive.read_bytes()).hexdigest()==sys.argv[2];base.mkdir()
with tarfile.open(archive,'r:gz') as t:
 for m in t:
  p=PurePosixPath(m.name);assert m.isfile() and not p.is_absolute() and '..' not in p.parts
  dest=base.joinpath(*p.parts);assert dest.resolve().is_relative_to(base.resolve());dest.parent.mkdir(parents=True,exist_ok=True)
  with dest.open('xb') as f:f.write(t.extractfile(m).read())
spec=json.loads((base/'PAYLOAD_MANIFEST.json').read_bytes())
for x in spec['files']:
 p=base/x['path'];assert p.stat().st_size==x['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==x['SHA']
print(json.dumps(dict(root=str(base),files=len(spec['files']),SHA_exact=True)))
'''
def main():
 assert not (R/'THREE_RANK_DETACHED_DISPATCH_STARTED_ACTUAL.json').exists()
 archive=D/'three_rank_single_CURB20_PPO_v1.tar.gz';assert not archive.exists()
 with tarfile.open(archive,'w:gz',compresslevel=1) as z:
  for p in sorted(Q.rglob('*')):
   if p.is_file():z.add(p,arcname=p.relative_to(Q).as_posix(),recursive=False)
 h=sha(archive);put('SINGLE_PPO_THREE_RANK_PACKAGE_ACTUAL.json',dict(path=str(archive.resolve()),bytes=archive.stat().st_size,SHA=h))
 cfg=dict(run_id=RUNID,auth_token=secrets.token_hex(32));c=None;pw=None
 put('THREE_RANK_DETACHED_DISPATCH_STARTED_ACTUAL.json',dict(epoch=time.time(),local_pid=__import__('os').getpid(),source_root=SOURCE,target_root=TARGET,canonical25200s_one_shared_job=True,capability_secret_in_stdin_memory_only_never_file_log_Git=True))
 try:
  c=t.connect();sf=c.open_sftp();sf.get_channel().settimeout(90)
  with archive.open('rb') as src,sf.open(SOURCE+'.tar.gz','wx') as f:
   while b:=src.read(4*1024*1024):f.write(b)
  sf.close();si,so,se=c.exec_command(shlex.quote(t.PY)+' -B - '+shlex.quote(SOURCE)+' '+h,timeout=120);si.write(EXTRACT);si.flush();si.channel.shutdown_write();out=so.read();err=se.read();rc=so.channel.recv_exit_status();put('SOURCE_THREE_RANK_EXTRACT_ACTUAL.json',dict(rc=rc,stdout=out.decode(errors='replace'),stderr=err.decode(errors='replace')));assert rc==0
 finally:t.close(c)
 # Prepare both nodes fully before starting the durable original owner.
 c=paramiko.SSHClient();c.load_system_host_keys();c.set_missing_host_key_policy(paramiko.AutoAddPolicy());pw=getpass.getpass('Host72 SSH password (hidden, never saved): ')
 try:
  c.connect('10.24.0.72',username='lc01',password=pw,timeout=15,auth_timeout=20,banner_timeout=20,allow_agent=False,look_for_keys=False);pw=None
  assert hashlib.sha256(c.get_transport().get_remote_server_key().asbytes()).hexdigest()=='301a9837e8503b664fa4cedde20407769d8f1b86ae59d9a54afb236bdfa41795'
  sf=c.open_sftp();sf.get_channel().settimeout(90)
  with archive.open('rb') as src,sf.open(TARGET+'.tar.gz','wx') as f:
   while b:=src.read(4*1024*1024):f.write(b)
  sf.close();si,so,se=c.exec_command("'/home/lc01/Zonglin Li/zonglin2/run-python.sh' -B - "+shlex.quote(TARGET)+' '+h,timeout=120);si.write(EXTRACT);si.flush();si.channel.shutdown_write();out=so.read();err=se.read();rc=so.channel.recv_exit_status();put('TARGET_THREE_RANK_EXTRACT_ACTUAL.json',dict(rc=rc,stdout=out.decode(errors='replace'),stderr=err.decode(errors='replace')));assert rc==0
 finally:pw=None;c.close()
 try:
  c=t.connect();si,so,se=c.exec_command(shlex.quote(t.PY)+' -u -B '+shlex.quote(SOURCE+'/remote_single_ppo_owner_v1.py'),timeout=20);si.write(json.dumps(cfg)+'\n');si.flush();si.channel.shutdown_write();out=so.read();err=se.read();rc=so.channel.recv_exit_status();put('ORIGINAL_SOURCE_OWNER_DETACHED_DISPATCH_ACTUAL.json',dict(epoch=time.time(),rc=rc,stdout=out.decode(errors='replace'),stderr=err.decode(errors='replace')));assert rc==0
 finally:t.close(c)
 c=paramiko.SSHClient();c.load_system_host_keys();c.set_missing_host_key_policy(paramiko.AutoAddPolicy());pw=getpass.getpass('Host72 SSH password (hidden, never saved): ')
 try:
  c.connect('10.24.0.72',username='lc01',password=pw,timeout=15,auth_timeout=20,banner_timeout=20,allow_agent=False,look_for_keys=False);pw=None
  assert hashlib.sha256(c.get_transport().get_remote_server_key().asbytes()).hexdigest()=='301a9837e8503b664fa4cedde20407769d8f1b86ae59d9a54afb236bdfa41795'
  si,so,se=c.exec_command("'/home/lc01/Zonglin Li/zonglin2/run-python.sh' -u -B "+shlex.quote(TARGET+'/remote_node72_agent_v1.py'),timeout=20);si.write(json.dumps(cfg)+'\n');si.flush();si.channel.shutdown_write();out=so.read();err=se.read();rc=so.channel.recv_exit_status();put('TARGET_NODE72_AGENT_DETACHED_DISPATCH_ACTUAL.json',dict(epoch=time.time(),rc=rc,stdout=out.decode(errors='replace'),stderr=err.decode(errors='replace')));assert rc==0
 finally:pw=None;c.close();cfg['auth_token']=None
 print(json.dumps(dict(detached_both_nodes=True,source=SOURCE,target=TARGET,probe_then_native_then_single_PPO7h=True,not_yet_PPO_positive=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:put('DETACHED_DISPATCH_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_blind_replay=True));raise
