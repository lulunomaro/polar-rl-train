"""Sequential bounded own-root reads + immutable first model collection; no launches."""
from pathlib import Path
import getpass,hashlib,importlib.util,json,paramiko,time
D=Path(__file__).resolve().parent;R=D/'reports'
s=importlib.util.spec_from_file_location('first_collection_pure',D/'collect_independent_first_models_and_actual_state_bounded_v1.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def main():
 c=None;nodes=[]
 try:
  c=m.old.t.connect()
  for sub,jobs in (('train',(0,)),('wave_episode_reviewed_v3',())):nodes.append(m.collect(c,m.old.t.PY,'/mnt/mod4_linux_durable_20261013/'+D.name+'/'+sub,jobs))
 finally:m.old.t.close(c)
 pw=getpass.getpass('Host72 SSH password (hidden, never saved): ');c=paramiko.SSHClient();c.load_system_host_keys();c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
 try:
  c.connect('10.24.0.72',username='lc01',password=pw,timeout=15,auth_timeout=20,banner_timeout=20,allow_agent=False,look_for_keys=False);pw=None;assert hashlib.sha256(c.get_transport().get_remote_server_key().asbytes()).hexdigest()=='301a9837e8503b664fa4cedde20407769d8f1b86ae59d9a54afb236bdfa41795'
  for sub,jobs in (('train',(1,)),('wave_episode_reviewed_v3',(3,))):nodes.append(m.collect(c,'/home/lc01/Zonglin Li/zonglin2/run-python.sh','/home/lc01/Zonglin Li/zonglin2/tasks/'+D.name+'/'+sub,jobs))
 finally:pw=None;c.close()
 p=R/('INDEPENDENT_AND_WAVE_REPAIR_ACTUAL_BOUND_COLLECTION_'+str(time.time_ns())+'.json');p.write_text(json.dumps(dict(epoch=time.time(),nodes=nodes),indent=2),encoding='utf8');brief=[]
 for n in nodes:
  if n['root'].endswith('wave_episode_reviewed_v3'):
   curr=[f for f in n['files'] if Path(f['path']).name in ('OWNER_CURRENT.json','NODE_CURRENT.json')]
   ww=[f['data'].get('row',{}) for f in curr]
   v=dict(root=n['root'],epoch=n['epoch'],processes=[dict(pid=z['pid'],created=z['create_time'],argv=z['cmdline']) for z in n['actual_own_processes'] if any(str(a).endswith('.py') for a in z['cmdline'] or [])],rows=[dict(job=r.get('job'),returncode=r.get('returncode'),native=bool(r.get('NATIVE120_COMPLETE.json')),CPU=r.get('INDEPENDENT_NATIVE_CPU_ADMITTED.json'),PPO=r.get('PPO_POSITIVE_CURRENT.json'),error=r.get('WORKER_ORIGINAL_ERROR_BEFORE_APP_CLOSE.json'),FINAL=r.get('FINAL.json')) for r in ww],go=[f['data'].get('go',f['data'].get('reply',{}).get('go')) for f in curr],first_models=n.get('first_models_actual_twohost_SHA'),errors=[f for f in n['files'] if 'ORIGINAL_ERROR' in f['path'] or 'REJECTED' in f['path']],logs=[dict(path=z['path'],tail=z['tail'][-1400:]) for z in n['logs']])
  else:v=m.brief(n)
  brief.append(v)
 print(json.dumps(dict(report=str(p),nodes=brief)),flush=True)
if __name__=='__main__':main()
