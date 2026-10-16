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
  v=m.brief(n)
  if n['root'].endswith('wave_episode_reviewed_v3'):
   v['wave_scope_current']=[f for f in n['files'] if Path(f['path']).name in ('OWNER_CURRENT.json','NODE_CURRENT.json','OWNER_IDENTITY.json','NODE_FINAL.json','OWNER_EXIT_ACTUAL.json')]
  brief.append(v)
 print(json.dumps(dict(report=str(p),nodes=brief)),flush=True)
if __name__=='__main__':main()
