"""Bounded target-only inspection after actual SDK errors; no SDK launch or mutation."""
from pathlib import Path
import getpass,hashlib,json,shlex,time,traceback,paramiko
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';ROOT='/home/lc01/Zonglin Li/zonglin2'
CODE=r'''
from pathlib import Path
import hashlib,json,os,subprocess,time,fcntl
r=Path('/home/lc01/Zonglin Li/zonglin2');s=r/'envs/mod4/lib/python3.12/site-packages/isaacsim'
v=dict(epoch=time.time(),apps=[str(p) for p in sorted((s/'apps').glob('*.kit'))],files=[],processes=[],no_SDK_launch_GPU_or_deletion=True)
paths=list((s/'apps').glob('*python*.kit'))+list((s/'apps').glob('*headless*.kit'))
paths+=list((s/'exts').glob('isaacsim.core.simulation_manager/isaacsim/core/simulation_manager/simulation_manager.py'))
paths+=list((s/'exts').glob('isaacsim.core.api/isaacsim/core/api/world/world.py'))
paths+=list((s/'exts').glob('isaacsim.simulation_app/isaacsim/simulation_app/simulation_app.py'))
for p in sorted(set(paths)):
 b=p.read_bytes();v['files'].append(dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),text=b.decode(errors='replace') if len(b)<250000 else None))
for a in sorted((r/'audit').glob('*STARTED.json')):
 try:x=json.loads(a.read_bytes())
 except Exception:continue
 pid=x.get('pid')
 if pid is None:continue
 q=Path('/proc')/str(pid)
 row=dict(receipt=str(a),pid=pid,actual_proc_exists=q.exists())
 if q.exists():
  try:row.update(stat=(q/'stat').read_text(),cmdline=(q/'cmdline').read_bytes().replace(b'\0',b' ').decode(errors='replace'))
  except FileNotFoundError:row['exited_during_read']=True
 v['processes'].append(row)
lock=r/'state/finite_environment_validation.lock'
with lock.open('rb+') as f:
 try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);v['actual_validation_fcntl_free']=True;fcntl.flock(f,fcntl.LOCK_UN)
 except BlockingIOError:v['actual_validation_fcntl_free']=False
p=subprocess.run(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,process_name','--format=csv,noheader'],capture_output=True,text=True)
v['actual_nvidia_compute_snapshot']=dict(returncode=p.returncode,stdout=p.stdout,stderr=p.stderr)
with (r/'audit/SDK_V3_FAILURE_CONFIG_API_EXIT_LOCK_READONLY_ACTUAL.json').open('x') as f:json.dump(v,f,indent=2)
print(json.dumps(v))
'''
def main():
 assert (R/'OWNED72_FINITE_SDK_BOUNDARY_COLLECTED_ACTUAL.json').exists()
 assert not (R/'SDK_V3_FAILURE_CONFIG_API_EXIT_LOCK_READONLY_ACTUAL.json').exists()
 p=json.loads((W/'MOD4_HOST72_DUAL4090_ENV_READONLY_20261015/reports/HOST72_READONLY_DISCOVERY_ACTUAL.json').read_bytes())
 c=paramiko.SSHClient();c.load_system_host_keys();c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
 pw=getpass.getpass('Host72 SSH password (hidden, not saved): ')
 try:
  c.connect(p['host'],username=p['user'],password=pw,timeout=15,auth_timeout=20,banner_timeout=20,look_for_keys=False,allow_agent=False);pw=None
  assert hashlib.sha256(c.get_transport().get_remote_server_key().asbytes()).hexdigest()==p['remote_host_key_SHA256_hex']
  si,so,se=c.exec_command('python3 -B -',timeout=90);si.write(CODE);si.flush();si.channel.shutdown_write()
  out=so.read();err=se.read();rc=so.channel.recv_exit_status()
  assert rc==0,err.decode(errors='replace')
  v=json.loads(out)
  with (R/'SDK_V3_FAILURE_CONFIG_API_EXIT_LOCK_READONLY_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
  print(json.dumps(dict(files=len(v['files']),actual_validation_fcntl_free=v['actual_validation_fcntl_free'],actual_compute=v['actual_nvidia_compute_snapshot'])),flush=True)
 finally:pw=None;c.close()
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('SDK_V3_POSTFAILURE_INSPECTION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x') as f:json.dump(dict(error=traceback.format_exc()),f,indent=2)
  raise
