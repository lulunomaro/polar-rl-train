"""Read own finite cohort once; preserve immutable first models, compact stdout."""
from pathlib import Path
import getpass,hashlib,importlib.util,json,paramiko,sys,time
D=Path(__file__).resolve().parent;R=D/'reports'
s=importlib.util.spec_from_file_location('own_bounded_reader',D/'read_independent_cohort_actual_bounded.py');old=importlib.util.module_from_spec(s);s.loader.exec_module(old)

def H(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4194304),b''):h.update(b)
 return h.hexdigest()

def collect(c,py,root,jobs):
 n=old.read(c,py,root);download=[];sf=c.open_sftp()
 try:
  for job in jobs:
   prefix=root+'/job'+str(job)+'/run/';row=next((x['data']['row'] for x in n['files'] if x['path']==prefix+'PPO_POSITIVE_CURRENT.json'),None)
   if not row:continue
   # Rolling metadata may already point to update25; the immutable first filename remains fixed.
   first=prefix+'model_update1.pt';loc=D/'first_independent_models'/('job'+str(job))/'model_update1.pt'
   loc.parent.mkdir(parents=True,exist_ok=True)
   st=sf.stat(first)
   if not loc.exists():
    tmp=loc.with_suffix('.pt.partial');assert not tmp.exists();sf.get(first,str(tmp));assert tmp.stat().st_size==st.st_size;tmp.replace(loc)
   assert loc.stat().st_size==st.st_size
   # Independently hash the immutable remote first file without any GPU forward or save.
   code="from pathlib import Path;import hashlib,json;p=Path("+repr(first)+");print(json.dumps(dict(bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest())))"
   si,so,se=c.exec_command(old.shlex.quote(py)+' -B -c '+old.shlex.quote(code),timeout=30);raw=so.read();err=se.read();assert so.channel.recv_exit_status()==0,err.decode();remote=json.loads(raw)
   assert H(loc)==remote['SHA'] and loc.stat().st_size==remote['bytes']
   download.append(dict(job=job,remote_path=first,local_path=str(loc.resolve()),**remote,immutable_first_model_not_rolling_metadata=True))
 finally:sf.close()
 n['first_models_actual_twohost_SHA']=download;return n

def brief(n):
 rows=[]
 for f in n['files']:
  if Path(f['path']).name not in ('OWNER_CURRENT.json','NODE72_CURRENT.json'):continue
  z=f['data'];rr=z['rows'];rr=list(rr.values()) if isinstance(rr,dict) else rr
  rows=[dict(job=r['job'],returncode=r['returncode'],native_complete=bool(r.get('NATIVE120_COMPLETE.json')),native_CPU=r.get('INDEPENDENT_NATIVE_CPU_ADMITTED.json'),PPO=r.get('PPO_POSITIVE_CURRENT.json'),error=r.get('ORIGINAL_ERROR')) for r in rr]
 return dict(root=n['root'],epoch=n['epoch'],rows=rows,first_models=n['first_models_actual_twohost_SHA'],errors=[f for f in n['files'] if 'ORIGINAL_ERROR' in f['path'] or 'REJECTED' in f['path']],logtails=[dict(path=l['path'],tail=l['tail'][-1000:]) for l in n['logs']],canonical=n.get('canonical'))

def main():
 nodes=[];c=None
 try:c=old.t.connect();nodes.append(collect(c,old.t.PY,'/mnt/mod4_linux_durable_20261013/'+D.name+'/train',(0,)))
 finally:old.t.close(c)
 c=paramiko.SSHClient();c.load_system_host_keys();c.set_missing_host_key_policy(paramiko.AutoAddPolicy());pw=getpass.getpass('Host72 SSH password (hidden, never saved): ')
 try:
  c.connect('10.24.0.72',username='lc01',password=pw,timeout=15,auth_timeout=20,banner_timeout=20,allow_agent=False,look_for_keys=False);pw=None;assert hashlib.sha256(c.get_transport().get_remote_server_key().asbytes()).hexdigest()=='301a9837e8503b664fa4cedde20407769d8f1b86ae59d9a54afb236bdfa41795';nodes.append(collect(c,'/home/lc01/Zonglin Li/zonglin2/run-python.sh','/home/lc01/Zonglin Li/zonglin2/tasks/'+D.name+'/train',(1,2)))
 finally:pw=None;c.close()
 p=R/('INDEPENDENT_FIRST_MODELS_BOUND_COLLECTION_'+str(time.time_ns())+'.json');p.write_text(json.dumps(dict(epoch=time.time(),nodes=nodes),indent=2),encoding='utf8');print(json.dumps(dict(report=str(p),nodes=[brief(n) for n in nodes])),flush=True)

if __name__=='__main__':main()
