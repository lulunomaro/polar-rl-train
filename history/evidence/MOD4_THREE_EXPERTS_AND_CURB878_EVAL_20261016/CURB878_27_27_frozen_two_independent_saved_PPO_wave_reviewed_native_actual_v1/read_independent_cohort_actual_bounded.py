from pathlib import Path
import getpass,hashlib,json,paramiko,shlex,sys,time
D=Path(__file__).resolve().parent;R=D/'reports';W=D.parent;sys.path.insert(0,str(W/'MOD4_LINUX_WAVE50_BODYFRAME_RESET_INTEGRATION_20261014'));import transport_bodyframe_root_owned as t
CODE=r'''
from pathlib import Path
import json,sys,time,psutil
B=Path(sys.argv[1]);files=[];logs=[]
for p in sorted(B.glob('*.json'))+sorted(B.glob('job*/*.json'))+sorted(B.glob('job*/run/*.json')):
 if p.stat().st_size<2000000:
  try:files.append(dict(path=str(p),data=json.loads(p.read_bytes())))
  except (OSError,ValueError):pass
for p in sorted(B.glob('*stdout_stderr.log'))+sorted(B.glob('job*/worker.log')):
 with p.open('rb') as f:f.seek(max(0,p.stat().st_size-9000));b=f.read()
 logs.append(dict(path=str(p),bytes=p.stat().st_size,tail=b.decode(errors='replace')))
procs=[]
for p in psutil.process_iter(['pid','create_time','cmdline','cwd']):
 try:
  if str(B) in ' '.join(p.info['cmdline'] or []):procs.append(p.info)
 except psutil.Error:pass
v=dict(epoch=time.time(),root=str(B),files=files,logs=logs,actual_own_processes=procs)
if str(B).startswith('/mnt/'):
 q=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');c=json.loads(q.read_bytes());v['canonical']={k:c[k] for k in ('active_segment','charged_training_seconds','remaining_training_seconds')}
print(json.dumps(v))
'''
def read(c,py,root):
 si,so,se=c.exec_command(shlex.quote(py)+' -B - '+shlex.quote(root),timeout=35);si.write(CODE);si.flush();si.channel.shutdown_write();raw=so.read();err=se.read();assert so.channel.recv_exit_status()==0,err.decode();return json.loads(raw)
def main():
 p=R/('INDEPENDENT_COHORT_ACTUAL_STATE_'+str(time.time_ns())+'.json');rows=[];c=None
 try:c=t.connect();rows.append(read(c,t.PY,'/mnt/mod4_linux_durable_20261013/'+D.name+'/train'))
 finally:t.close(c)
 c=paramiko.SSHClient();c.load_system_host_keys();c.set_missing_host_key_policy(paramiko.AutoAddPolicy());pw=getpass.getpass('Host72 SSH password (hidden, never saved): ')
 try:
  c.connect('10.24.0.72',username='lc01',password=pw,timeout=15,auth_timeout=20,banner_timeout=20,allow_agent=False,look_for_keys=False);pw=None;assert hashlib.sha256(c.get_transport().get_remote_server_key().asbytes()).hexdigest()=='301a9837e8503b664fa4cedde20407769d8f1b86ae59d9a54afb236bdfa41795';rows.append(read(c,'/home/lc01/Zonglin Li/zonglin2/run-python.sh','/home/lc01/Zonglin Li/zonglin2/tasks/'+D.name+'/train'))
 finally:pw=None;c.close()
 p.write_text(json.dumps(dict(epoch=time.time(),nodes=rows),indent=2),encoding='utf8');keep={'OWNER_CURRENT.json','NODE72_CURRENT.json','OWNER_ORIGINAL_ERROR.json','WORKER_ORIGINAL_ERROR.json','NATIVE_CPU_REJECTED.json','PPO_POSITIVE_CURRENT.json','INDEPENDENT_NATIVE_CPU_ADMITTED.json','FINAL.json'};print(json.dumps(dict(report=str(p),nodes=[dict(root=n['root'],procs=n['actual_own_processes'],canonical=n.get('canonical'),files=[r for r in n['files'] if Path(r['path']).name in keep],logs=[dict(path=z['path'],tail=z['tail'][-1200:]) for z in n['logs']]) for n in rows])),flush=True)
if __name__=='__main__':main()
