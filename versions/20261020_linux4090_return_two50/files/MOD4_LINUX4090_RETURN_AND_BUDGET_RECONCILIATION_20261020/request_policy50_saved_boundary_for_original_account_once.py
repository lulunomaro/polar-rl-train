from pathlib import Path
import getpass,hashlib,json,os,shlex,sys,time,traceback,paramiko
B=Path(__file__).resolve().parent;R=B/'reports'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
CODE=r'''
from pathlib import Path
import json,os,psutil,time
C=Path('/home/lc01/Zonglin Li/zonglin2/tasks/E3auto50_2010v30/controller');identity=json.loads((C/'SERIES_IDENTITY.json').read_bytes());p=psutil.Process(identity['pid']);assert abs(p.create_time()-identity['creation'])<.01 and p.cmdline()[-1]==str(C/'auto_E3_serial_supervisor_v1.py');stop=C/'STOP_SERIES_AFTER_CURRENT.json';existed=stop.exists()
if not existed:
 fd=os.open(stop,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
 with os.fdopen(fd,'w') as f:json.dump(dict(epoch=time.time(),reason='Original Linux210 returned; reconcile distinct pending costs under original canonical two locks after full saved boundary',no_kill_or_hotpatch=True),f);f.flush();os.fsync(f.fileno())
state=json.loads((C/'SERIES_CURRENT.json').read_bytes());print(json.dumps(dict(epoch=time.time(),parent_actual_identity=dict(pid=p.pid,creation=p.create_time(),argv=p.cmdline()),stop_path=str(stop),already_existed=existed,request=json.loads(stop.read_bytes()),current=state,current_window_not_interrupted=True,no_GPU_or_Task_or_canonical_change=True)))
'''
def main():
 put('POLICY50_ORIGINAL_ACCOUNT_SAVED_BOUNDARY_REQUEST_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv));pw=getpass.getpass('72 saved boundary for original account return (hidden): ');c=paramiko.SSHClient();c.load_system_host_keys();c.set_missing_host_key_policy(paramiko.RejectPolicy())
 try:
  c.connect('10.24.0.72',username='lc01',password=pw,look_for_keys=False,allow_agent=False,timeout=15,banner_timeout=20,auth_timeout=20);pw=None;assert hashlib.sha256(c.get_transport().get_remote_server_key().asbytes()).hexdigest()=='301a9837e8503b664fa4cedde20407769d8f1b86ae59d9a54afb236bdfa41795';_,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -u -B -c '+shlex.quote(CODE),timeout=60);raw=o.read().decode();error=e.read().decode();assert o.channel.recv_exit_status()==0,(raw,error);v=json.loads(raw);put('POLICY50_ORIGINAL_ACCOUNT_SAVED_BOUNDARY_REQUEST_ACTUAL.json',dict(epoch=time.time(),actual=v,actual_finite_transport_returned=True));a=v['current'].get('active') or {};print(json.dumps(dict(saved_boundary_requested=True,current_index=a.get('index'),GO=a.get('GO'),no_hotpatch_or_kill=True)),flush=True)
 finally:pw=None;c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('POLICY50_SAVED_BOUNDARY_REQUEST_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),error=traceback.format_exc(),no_once_replay=True));raise
