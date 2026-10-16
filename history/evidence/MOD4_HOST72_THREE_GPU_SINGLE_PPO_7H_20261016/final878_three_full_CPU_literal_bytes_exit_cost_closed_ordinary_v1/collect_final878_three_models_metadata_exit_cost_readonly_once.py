"""Collect immutable final artifacts and actual closure; never re-dispatch any runtime."""
from pathlib import Path
import getpass,hashlib,json,shlex,sys,time,traceback,paramiko
D=Path(__file__).resolve().parent;R=D/'reports';W=D.parent
sys.path.insert(0,str(W/'MOD4_LINUX_WAVE50_BODYFRAME_RESET_INTEGRATION_20261014'));import transport_bodyframe_root_owned as t
CODE=r'''
from pathlib import Path
import fcntl,hashlib,json,os,psutil,sys,time
B=Path(sys.argv[1]);source=str(B).startswith('/mnt/');paths=set(B.glob('*.json'))|set(B.glob('rank*/*.json'))|set(B.glob('rank*/logs/**/*.json'))|set(B.glob('*.log'))|set(B.glob('rank*/*.log'));files=[]
def H(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4194304),b''):h.update(b)
 return h.hexdigest()
for p in sorted(paths):
 if p.is_file() and not p.name.endswith('.partial'):files.append(dict(path=str(p),relative=p.relative_to(B).as_posix(),bytes=p.stat().st_size,SHA=H(p),collect=p.stat().st_size<8388608))
finals=[]
for p in sorted(B.glob('rank*/FINAL_SINGLE_PPO.json')):
 x=json.loads(p.read_bytes());assert x['passed'];r=x['final'];q=Path(r['checkpoint']);assert r['updates']==878 and H(q)==r['SHA'] and q.stat().st_size==r['bytes'];finals.append(r)
ids=[395924,396065] if source else [3067441,3067619,3067626];actual=[]
for pid in ids:
 try:
  p=psutil.Process(pid);actual.append(dict(pid=pid,created=p.create_time(),argv=p.cmdline(),status=p.status()))
 except psutil.NoSuchProcess:actual.append(dict(pid=pid,absent=True))
v=dict(epoch=time.time(),root=str(B),files=files,finals=finals,exact_historical_PID_actual=actual)
if source:
 C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');x=json.loads(C.read_bytes());kind='Linux_DDPPO_CURB20_WORLD3_7H_1792087765528217480';segments=[s for s in x['completed_segments'] if s['kind']==kind];assert x['active_segment'] is None and len(segments)==1;v['canonical']=dict(path=str(C),bytes=C.stat().st_size,SHA=H(C),authorized=x['authorized_training_seconds'],extensions=len(x['budget_extensions']),active=x['active_segment'],charged=x['charged_training_seconds'],remaining=x['remaining_training_seconds'],own_unique_completed=segments)
 locks=[]
 for p in [C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')]:
  with p.open('rb+') as f:
   try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
   except BlockingIOError:locks.append(dict(path=str(p),free=False))
   else:locks.append(dict(path=str(p),free=True));fcntl.flock(f,fcntl.LOCK_UN)
 v['actual_fcntl']=locks
print(json.dumps(v))
'''
def collect(c,py,root,out):
 si,so,se=c.exec_command(shlex.quote(py)+' -B - '+shlex.quote(root),timeout=60);si.write(CODE);si.flush();si.channel.shutdown_write();raw=so.read();err=se.read();assert so.channel.recv_exit_status()==0,err.decode();v=json.loads(raw);sf=c.open_sftp();sf.get_channel().settimeout(90)
 try:
  refs=[dict(r,relative='rank'+str(r['rank'])+'/'+Path(r['checkpoint']).name,path=r['checkpoint'],collect=True) for r in v['finals']]
  for r in v['files']+refs:
   if not r['collect']:continue
   p=out/r['relative'];p.parent.mkdir(parents=True,exist_ok=True);h=hashlib.sha256();n=0
   with sf.open(r['path'],'rb') as f,p.open('xb') as g:
    while b:=f.read(4194304):g.write(b);h.update(b);n+=len(b)
   assert n==r['bytes'] and h.hexdigest()==r['SHA'],r['relative'];r['local_path']=str(p.resolve())
  v['final_downloads']=refs
 finally:sf.close()
 return v
def main():
 p=R/'FINAL878_THREE_MODELS_METADATA_ACTUAL_EXIT_LOCKS_COST_INPUTS.json';assert not p.exists();out=D/'final878_actual';out.mkdir();nodes=[];c=None
 try:c=t.connect();nodes.append(collect(c,t.PY,'/mnt/mod4_linux_durable_20261013/'+D.name,out/'source210'))
 finally:t.close(c)
 c=paramiko.SSHClient();c.load_system_host_keys();c.set_missing_host_key_policy(paramiko.AutoAddPolicy());pw=getpass.getpass('Host72 SSH password (hidden, never saved): ')
 try:
  c.connect('10.24.0.72',username='lc01',password=pw,timeout=15,auth_timeout=20,banner_timeout=20,allow_agent=False,look_for_keys=False);pw=None
  assert hashlib.sha256(c.get_transport().get_remote_server_key().asbytes()).hexdigest()=='301a9837e8503b664fa4cedde20407769d8f1b86ae59d9a54afb236bdfa41795'
  nodes.append(collect(c,'/home/lc01/Zonglin Li/zonglin2/run-python.sh','/home/lc01/Zonglin Li/zonglin2/tasks/'+D.name,out/'target72'))
 finally:pw=None;c.close()
 p.write_text(json.dumps(dict(epoch=time.time(),nodes=nodes,all_transferred_size_SHA_exact=True,no_runtime_mutation_or_new_PPO=True),indent=2),encoding='utf8');print(json.dumps(dict(report=str(p),final_ranks=[r['rank'] for n in nodes for r in n['finals']],source_canonical=nodes[0]['canonical'],locks=nodes[0]['actual_fcntl'],pids=[n['exact_historical_PID_actual'] for n in nodes])),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('FINAL878_COLLECTOR_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x') as f:json.dump(dict(error=traceback.format_exc(),no_runtime_replay=True),f,indent=2)
  raise
