"""One bounded host72 connection; request a normal save boundary for authorized 50 Hz migration."""
from pathlib import Path
import hashlib,json,os,sys,time,traceback
import paramiko
B=Path(__file__).resolve().parent; R=B/'reports'; R.mkdir(exist_ok=True)
def put(name,value):
 with (R/name).open('x',encoding='utf8') as f: json.dump(value,f,ensure_ascii=False,indent=2)
def main():
 put('BOUNDARY_AND_INVENTORY_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv))
 c=paramiko.SSHClient();c.load_system_host_keys();c.set_missing_host_key_policy(paramiko.RejectPolicy())
 try:
  key=Path.home()/'.ssh/id_ed25519_lulu'
  c.connect('10.24.0.72',username='lc01',key_filename=str(key),allow_agent=False,look_for_keys=False,timeout=12,auth_timeout=12,banner_timeout=12)
  assert hashlib.sha256(c.get_transport().get_remote_server_key().asbytes()).hexdigest()=='301a9837e8503b664fa4cedde20407769d8f1b86ae59d9a54afb236bdfa41795'
  code="""from pathlib import Path
import json,os,time,psutil
B=Path('/home/lc01/Zonglin Li/zonglin2/tasks/E3auto_2010v26/controller')
read=lambda p:json.loads(p.read_bytes())
identity=read(B/'SERIES_IDENTITY.json');p=psutil.Process(identity['pid']);assert abs(p.create_time()-identity['creation'])<.01 and p.cmdline()[-1]==str(B/'auto_E3_serial_supervisor_v1.py')
q=B/'STOP_SERIES_AFTER_CURRENT.json'
value=dict(epoch=time.time(),human_instruction='换成50hz继续训吧',reason='complete current 100Hz save/SDK close and cost before isolated 50Hz continuation',no_force_kill=True)
with q.open('x') as f:json.dump(value,f);f.flush();os.fsync(f.fileno())
print(json.dumps(dict(epoch=time.time(),boundary_request=read(q),series_current=read(B/'SERIES_CURRENT.json'),identity=identity,no_current_worker_mutation=True)))
"""
  import shlex
  command="'/home/lc01/Zonglin Li/zonglin2/run-python.sh' -B -c "+shlex.quote(code)
  _,stdout,stderr=c.exec_command(command,timeout=60);out=stdout.read().decode();err=stderr.read().decode();rc=stdout.channel.recv_exit_status()
  put('BOUNDARY_AND_INVENTORY_REMOTE_ACTUAL.json',dict(epoch=time.time(),returncode=rc,stdout=out,stderr=err,actual_finite_returned=True));assert rc==0
  print(out)
 finally:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:
  put('BOUNDARY_AND_INVENTORY_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),error=traceback.format_exc(),do_not_replay_once=True));raise
