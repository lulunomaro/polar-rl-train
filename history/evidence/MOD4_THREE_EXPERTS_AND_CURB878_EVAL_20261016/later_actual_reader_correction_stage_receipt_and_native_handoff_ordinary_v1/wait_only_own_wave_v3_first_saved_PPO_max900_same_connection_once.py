"""One finite own-scope wait, no other hosts, no signals/retries/global polling."""
from pathlib import Path
import getpass,hashlib,json,os,paramiko,shlex,sys,time,traceback
D=Path(__file__).resolve().parent;R=D/'reports';ROOT='/home/lc01/Zonglin Li/zonglin2/tasks/'+D.name+'/wave_episode_reviewed_v3';PREFIX='OWN_WAVE_V3_FIRST_SAVED_PPO_BOUND_WAIT'
CODE=r'''
from pathlib import Path
import json,sys,time,psutil
B=Path(sys.argv[1]);J=B/'job3';R=J/'run';start=time.monotonic();last=None
while True:
 x=dict(epoch=time.time(),scope=str(J),worker_pid=3099125,elapsed_seconds=time.monotonic()-start)
 try:p=psutil.Process(3099125);x['worker']=dict(pid=p.pid,created=p.create_time(),argv=p.cmdline());assert str(B) in ' '.join(p.cmdline())
 except psutil.NoSuchProcess:x['worker']=None
 for name in ('INDEPENDENT_NATIVE_CPU_ADMITTED.json','PPO_POSITIVE_CURRENT.json','FINAL.json'):
  p=R/name
  if p.exists():x[name]=json.loads(p.read_bytes())
 for name in ('WORKER_ORIGINAL_ERROR_BEFORE_APP_CLOSE.json','WORKER_ORIGINAL_ERROR.json','NATIVE_CPU_REJECTED.json'):
  p=J/name
  if p.exists():x[name]=json.loads(p.read_bytes())
 phase='PPO_saved' if 'PPO_POSITIVE_CURRENT.json' in x else 'native_CPU_passed_wait_existing_owner_handoff' if 'INDEPENDENT_NATIVE_CPU_ADMITTED.json' in x else 'native_pending'
 x['phase']=phase;terminal=phase=='PPO_saved' or x['worker'] is None or any('ORIGINAL_ERROR' in k or 'REJECTED' in k for k in x) or x['elapsed_seconds']>=890
 if phase!=last or terminal:print(json.dumps(x),flush=True);last=phase
 if terminal:break
 time.sleep(10)
'''
def put(p,v):
 q=p.with_suffix(p.suffix+'.partial');q.write_text(json.dumps(v,indent=2),encoding='utf8');q.replace(p)
def main():
 assert not (R/(PREFIX+'_STARTED.json')).exists();pw=getpass.getpass('Host72 SSH password (hidden, never saved): ');c=paramiko.SSHClient();c.load_system_host_keys();c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
 try:
  c.connect('10.24.0.72',username='lc01',password=pw,timeout=15,auth_timeout=20,banner_timeout=20,allow_agent=False,look_for_keys=False);pw=None;assert hashlib.sha256(c.get_transport().get_remote_server_key().asbytes()).hexdigest()=='301a9837e8503b664fa4cedde20407769d8f1b86ae59d9a54afb236bdfa41795';put(R/(PREFIX+'_STARTED.json'),dict(epoch=time.time(),local_pid=os.getpid(),argv=sys.argv,maximum_seconds=900,same_connection_own_scope_only=ROOT,no_signal_retry_global_poller_or_other_host_connection=True));si,so,se=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -u -B - '+shlex.quote(ROOT),timeout=910);si.write(CODE);si.flush();si.channel.shutdown_write();rows=[]
  for line in so:
   x=json.loads(line);rows.append(x);put(R/(PREFIX+'_CURRENT.json'),x);print(json.dumps(dict(phase=x['phase'],epoch=x['epoch'],elapsed=x['elapsed_seconds'],worker=x['worker'],native_CPU=x.get('INDEPENDENT_NATIVE_CPU_ADMITTED.json'),PPO=x.get('PPO_POSITIVE_CURRENT.json'),errors={k:v for k,v in x.items() if 'ORIGINAL_ERROR' in k or 'REJECTED' in k})),flush=True)
  err=se.read();rc=so.channel.recv_exit_status();assert rc==0,err.decode();last=rows[-1]
  if last.get('PPO_POSITIVE_CURRENT.json'):
   remote=ROOT+'/job3/run/model_update1.pt';loc=D/'first_independent_models/job3/model_update1.pt';loc.parent.mkdir(exist_ok=True,parents=True);assert not loc.exists();tmp=loc.with_suffix('.pt.partial');sf=c.open_sftp()
   try:sf.get(remote,str(tmp))
   finally:sf.close()
   raw=tmp.read_bytes();sha=hashlib.sha256(raw).hexdigest();row=last['PPO_POSITIVE_CURRENT.json']['row'];assert row['updates']==1 and row['SHA']==sha and row['bytes']==len(raw);tmp.replace(loc);last['immutable_first_model_download']=dict(local_path=str(loc.resolve()),remote_path=remote,bytes=len(raw),SHA=sha)
  put(R/(PREFIX+'_COMPLETE.json'),dict(epoch=time.time(),snapshots=rows,actual_first_model=last.get('immutable_first_model_download'),no_future_PPO_pass_inferred=True))
 finally:pw=None;c.close()
if __name__=='__main__':
 try:main()
 except BaseException:
  put(R/(PREFIX+'_ORIGINAL_ERROR.json'),dict(epoch=time.time(),error=traceback.format_exc(),no_automatic_retry=True));raise
