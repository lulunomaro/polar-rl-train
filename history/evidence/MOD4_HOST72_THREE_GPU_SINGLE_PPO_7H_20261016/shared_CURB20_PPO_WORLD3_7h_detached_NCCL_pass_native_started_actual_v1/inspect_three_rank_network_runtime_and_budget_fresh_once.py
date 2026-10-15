from pathlib import Path
import getpass,hashlib,json,shlex,sys,time,traceback,paramiko
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';sys.path.insert(0,str(W/'MOD4_LINUX_WAVE50_BODYFRAME_RESET_INTEGRATION_20261014'));import transport_bodyframe_root_owned as t
CODE=r'''
from pathlib import Path
import json,os,subprocess,time,importlib.util,socket
v=dict(epoch=time.time(),host=socket.gethostname(),python=__import__('sys').executable,paramiko_available=importlib.util.find_spec('paramiko') is not None)
for name,cmd in [('GPU',['nvidia-smi','--query-gpu=index,uuid,memory.total,memory.free,utilization.gpu','--format=csv,noheader,nounits']),('compute',['nvidia-smi','--query-compute-apps=gpu_uuid,pid,process_name','--format=csv,noheader']),('route',['ip','route','get',os.environ['PEER_IP']])]:
 p=subprocess.run(cmd,capture_output=True,text=True);v[name]=dict(rc=p.returncode,stdout=p.stdout,stderr=p.stderr)
B=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json')
if B.exists():
 import fcntl,hashlib
 b=json.loads(B.read_bytes());v['canonical']={k:b[k] for k in ('authorized_training_seconds','charged_training_seconds','remaining_training_seconds','active_segment')};v['canonical']['SHA']=hashlib.sha256(B.read_bytes()).hexdigest();v['locks']=[]
 for p in (B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
  with p.open('rb+') as f:
   try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);free=True;fcntl.flock(f,fcntl.LOCK_UN)
   except BlockingIOError:free=False
  v['locks'].append(dict(path=str(p),free=free))
print(json.dumps(v))
'''
def put(n,v):
 with (R/n).open('x') as f:json.dump(v,f,indent=2)
def main():
 assert not (R/'THREE_RANK_FRESH_RUNTIME_NETWORK_BUDGET_ACTUAL.json').exists();c=None;rows=[]
 try:
  c=t.connect();si,so,se=c.exec_command('PEER_IP=10.24.0.72 '+shlex.quote(t.PY)+' -B -',timeout=40);si.write(CODE);si.flush();si.channel.shutdown_write();out=so.read();err=se.read();rc=so.channel.recv_exit_status();assert rc==0,err.decode();rows.append(json.loads(out))
 finally:t.close(c)
 c=paramiko.SSHClient();c.load_system_host_keys();c.set_missing_host_key_policy(paramiko.AutoAddPolicy());pw=getpass.getpass('Host72 SSH password (hidden, never saved): ')
 try:
  c.connect('10.24.0.72',username='lc01',password=pw,timeout=15,auth_timeout=20,banner_timeout=20,allow_agent=False,look_for_keys=False);pw=None
  assert hashlib.sha256(c.get_transport().get_remote_server_key().asbytes()).hexdigest()=='301a9837e8503b664fa4cedde20407769d8f1b86ae59d9a54afb236bdfa41795'
  si,so,se=c.exec_command("PEER_IP=10.24.4.210 '/home/lc01/Zonglin Li/zonglin2/run-python.sh' -B -",timeout=40);si.write(CODE);si.flush();si.channel.shutdown_write();out=so.read();err=se.read();rc=so.channel.recv_exit_status();assert rc==0,err.decode();rows.append(json.loads(out))
 finally:pw=None;c.close()
 put('THREE_RANK_FRESH_RUNTIME_NETWORK_BUDGET_ACTUAL.json',dict(epoch=time.time(),rows=rows,human_authorizes_three_GPU_single_PPO_seven_hours_and_coexistence=True,no_other_process_modified=True));print(json.dumps(rows),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:put('FRESH_RUNTIME_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc()));raise
