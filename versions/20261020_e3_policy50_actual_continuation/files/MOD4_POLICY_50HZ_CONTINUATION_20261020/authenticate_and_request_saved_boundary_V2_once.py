"""Explicit supplied SSH credential via hidden stdin only; request the authorized save boundary once."""
from pathlib import Path
import getpass,hashlib,json,os,shlex,sys,time,traceback
import paramiko
B=Path(__file__).resolve().parent;R=B/'reports'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
READ=r'''
from pathlib import Path
import json,os,psutil,time,subprocess,shutil
C=Path('/home/lc01/Zonglin Li/zonglin2/tasks/E3auto_2010v26/controller');owned=Path('/home/lc01/Zonglin Li/zonglin2');assert C.resolve().is_relative_to(owned.resolve()) and not C.is_symlink();read=lambda p:json.loads(p.read_bytes());identity=read(C/'SERIES_IDENTITY.json');live=False
try:
 p=psutil.Process(identity['pid']);live=abs(p.create_time()-identity['creation'])<.01 and p.cmdline()[-1]==str(C/'auto_E3_serial_supervisor_v1.py')
except psutil.NoSuchProcess:pass
q=C/'STOP_SERIES_AFTER_CURRENT.json';created=False
if live and not q.exists():
 with q.open('x') as f:json.dump(dict(epoch=time.time(),human_instruction='换成50hz继续训吧',reason='normal complete-save boundary before separately admitted 50Hz policy continuation',no_force_kill=True),f);f.flush();os.fsync(f.fileno())
 created=True
own=[]
for p in psutil.process_iter(['pid','create_time','cmdline','exe']):
 try:
  if p.pid!=os.getpid() and any(x.startswith(str(C.parent)+'/') for x in p.info['cmdline'] or []):own.append(p.info)
 except psutil.Error:pass
print(json.dumps(dict(epoch=time.time(),identity=identity,parent_actual_identity_live=live,boundary_flag_created=created,boundary_flag=read(q) if q.exists() else None,series_current=read(C/'SERIES_CURRENT.json'),series_exit=read(C/'SERIES_EXIT_ACTUAL.json') if (C/'SERIES_EXIT_ACTUAL.json').exists() else None,actual_own_processes=own,compute_snapshot=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']).decode(),disk_free=shutil.disk_usage(owned).free,no_live_worker_or_canonical_changes=True)))
'''
def main():
 put('PASSWORD_V2_BOUNDARY_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,credential_via_hidden_stdin_only=True))
 pw=getpass.getpass('72 SSH credential (hidden; memory only): ');c=paramiko.SSHClient();c.load_system_host_keys();c.set_missing_host_key_policy(paramiko.RejectPolicy())
 try:
  c.connect('10.24.0.72',username='lc01',password=pw,look_for_keys=False,allow_agent=False,timeout=15,auth_timeout=20,banner_timeout=20);pw=None
  sha=hashlib.sha256(c.get_transport().get_remote_server_key().asbytes()).hexdigest();assert sha=='301a9837e8503b664fa4cedde20407769d8f1b86ae59d9a54afb236bdfa41795';c.get_transport().set_keepalive(15)
  _,out,err=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(READ),timeout=60);raw=out.read().decode();error=err.read().decode();rc=out.channel.recv_exit_status();put('PASSWORD_V2_BOUNDARY_RETURNED_ACTUAL.json',dict(epoch=time.time(),authenticated=True,host_key_SHA=sha,returncode=rc,actual=json.loads(raw) if rc==0 else None,stdout_original=raw,stderr_original=error,actual_finite_transport_returned=True));assert rc==0
  v=json.loads(raw);print(json.dumps(dict(authenticated=True,parent_identity_live=v['parent_actual_identity_live'],boundary_flag_created=v['boundary_flag_created'],active_window=(v['series_current'].get('active') or {}).get('index'),status=v['series_current']['status'],closed_windows=len(v['series_current']['completed']))),flush=True)
 finally:pw=None;c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('PASSWORD_V2_BOUNDARY_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),error=traceback.format_exc(),do_not_replay_once=True));raise
