"""Original failed precheck->production boundary and models; no restart or ledger writes."""
from pathlib import Path
import hashlib,json,shlex,sys,time
D=Path(__file__).resolve().parent;R=D/'reports';ROOT='/mnt/mod4_linux_durable_20261013/'+D.name
sys.path.insert(0,str(D.parent/'MOD4_LINUX_WAVE50_BODYFRAME_RESET_INTEGRATION_20261014'));import transport_bodyframe_root_owned as t
CODE=r'''
from pathlib import Path
import hashlib,json,time,psutil,fcntl,torch
B=Path(ROOT);files=[]
for p in B.rglob('*.json'):
 if 'runtime' in p.parts or p.stat().st_size>2000000:continue
 try:files.append(dict(path=str(p),value=json.loads(p.read_bytes())))
 except (OSError,ValueError):pass
c=json.loads(Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json').read_bytes());segments=[x for x in c['completed_segments'] if x.get('owner_parent_pid')==477807];own=[]
for p in psutil.process_iter(['pid','create_time','cmdline','cwd']):
 try:
  if any(str(B) in x for x in p.info['cmdline'] or []) and any('curb35_owner.py' in x or 'curb35_worker.py' in x for x in p.info['cmdline'] or []):own.append(p.info)
 except psutil.Error:pass
locks=[]
for path in ('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/native_floor_supervisor.lock','/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock'):
 f=Path(path).open('rb+');free=False
 try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);free=True;fcntl.flock(f,fcntl.LOCK_UN)
 except BlockingIOError:pass
 f.close();locks.append(dict(path=path,actual_fcntl_free=free))
models=[]
for rel,step in [('job0/precheck128/precheck128_discarded.pt',660440),('job0/native20k_then_production/own_native144.pt',660400),('job0/native20k_then_production/precheck20k_discarded.pt',660480)]:
 p=B/rel;v=torch.load(p,map_location='cpu',weights_only=False);count=[0,0]
 def walk(x):
  if torch.is_tensor(x):count[0]+=1;count[1]+=int(x.is_floating_point());assert not x.is_floating_point() or torch.isfinite(x).all()
  elif isinstance(x,dict):
   for z in x.values():walk(z)
  elif isinstance(x,(tuple,list)):
   for z in x:walk(z)
 walk(v);assert len(v['optimizer_state_dict']['state'])==17 and {int(x['step']) for x in v['optimizer_state_dict']['state'].values()}=={step};models.append(dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest(),all_tensor_finite=count,all17Adam=step))
assert not torch.cuda.is_initialized();print(json.dumps(dict(epoch=time.time(),files=files,actual_own_processes=own,canonical=dict(active=c['active_segment'],segments=segments,charged=c['charged_training_seconds'],remaining=c['remaining_training_seconds']),original_locks=locks,models=models,production_not_started=True)))
'''
def main():
 c=sf=None
 try:
  c=t.connect();si,so,se=c.exec_command(shlex.quote(t.PY)+' -B -',timeout=90);si.write('ROOT='+repr(ROOT)+'\n'+CODE);si.flush();si.channel.shutdown_write();raw=so.read();err=se.read();assert so.channel.recv_exit_status()==0,err.decode();v=json.loads(raw);assert not v['actual_own_processes'] and v['canonical']['active'] is None and all(x['actual_fcntl_free'] for x in v['original_locks']);out=D/'prechecks_closed_actual_models';out.mkdir();sf=c.open_sftp();sf.get_channel().settimeout(120)
  for row in v['models']:
   p=out/Path(row['path']).name;part=p.with_suffix('.pt.partial');sf.get(row['path'],str(part));assert part.stat().st_size==row['bytes'] and hashlib.sha256(part.read_bytes()).hexdigest()==row['SHA'];part.replace(p);row['local_path']=str(p.resolve())
  p=R/'POSTPRECHECK_SAME_PROCESS_STARTUP_RESTORE_REJECTION_ACTUAL_CLOSED_CPU_COLLECTION.json'
  with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
  print(json.dumps(dict(actual_closed=True,locks=v['original_locks'],canonical=v['canonical'],models=v['models'])),flush=True)
 finally:
  if sf:sf.close()
  t.close(c)
if __name__=='__main__':main()
