"""Readonly new actual stage, no old once import and no GPU initialization."""
from pathlib import Path
import json
from remote_session import execute
R='/mnt/mod4_linux_durable_20261013/MOD4_LINUX_FULLSTATE_REPAIR_RESUME_20261013/left_exploration20k_second_formal_sameidentity_v1'
CODE=r'''
from pathlib import Path
import json,hashlib,time,fcntl,psutil
R=Path(ROOT);a=R/'left_second_formal3600_v1'
def read(p):return json.loads(p.read_bytes()) if p.is_file() else None
files={n:read(R/n) for n in ('LEFT_SECOND_FORMAL_DISPATCH_ACTUAL.json','PARENT_IDENTITY.json','CURRENT_STAGE.json','LEFT_SECOND_FORMAL_PARENT_ERROR.json','LEFT_SECOND_FORMAL_SAVED_REVIEW_READY.json','GUARDIAN_EXIT.json')}
files.update({n:read(a/n) for n in ('DISPATCH_RECEIPT.json','EXIT_RECEIPT.json','GUARDIAN_CURRENT.json')})
folders=[p for p in (a/'learning_logs').glob('*') if p.is_dir()] if (a/'learning_logs').is_dir() else []
if folders:
 assert len(folders)==1
 f=folders[0];files['latest_complete']=read(f/'latest_complete.json');h=read(f/'CLOCK_TRAINING_HEALTH.json')
 files['health_compact']={k:v for k,v in (h or {}).items() if isinstance(v,(str,int,float,bool)) or v is None}
 files['startup_markers']=[p.name for p in f.glob('*STARTUP*VERIFIED.json')];files['log_dir']=str(f)
log=a/'worker_stdout.log'
if log.is_file():
 b=log.read_bytes();files['worker_log']=dict(bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),tail=b[-1800:].decode(errors='replace'),has_traceback=b'Traceback (most recent call last)' in b,capacity_error=any(x in b for x in (b'buffer overflow detected',b'Contacts have been dropped',b'PhysX scene is corrupted',b'CUDA error')))
actual=[]
ids={v['pid'] for x in files.values() if isinstance(x,dict) for v in (x,x.get('parent',{}),x.get('child',{})) if isinstance(v,dict) and isinstance(v.get('pid'),int)}
for pid in sorted(ids):
 try:
  p=psutil.Process(pid);actual.append(dict(pid=pid,created=p.create_time(),start_ticks=int(Path('/proc',str(pid),'stat').read_text().split(') ',1)[1].split()[19]),argv=p.cmdline(),cwd=p.cwd(),children=[dict(pid=c.pid,created=c.create_time(),argv=c.cmdline()) for c in p.children()]))
 except psutil.Error:pass
locks=[]
for p in (Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/native_floor_supervisor.lock'),Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with p.open('r+b') as f:
  try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);held=False;fcntl.flock(f,fcntl.LOCK_UN)
  except BlockingIOError:held=True
  locks.append(dict(path=str(p),held=held))
budget=read(Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json'))
print(json.dumps(dict(epoch=time.time(),root=str(R),files=files,actual_processes=actual,actual_fcntl_locks=locks,canonical_snapshot={k:budget[k] for k in ('authorized_training_seconds','remaining_training_seconds','active_segment')},readonly_no_PPO_signal_or_budgetwrite=True)))
'''
def main():
 v,p=execute('ROOT='+repr(R)+'\n'+CODE,'LEFT_SECOND_SAMEIDENTITY_CURRENT_COMPACT_ACTUAL',45)
 f=v['files'];print(json.dumps(dict(report=str(p),parent_error=f['LEFT_SECOND_FORMAL_PARENT_ERROR.json'],ownfinal=bool(f['LEFT_SECOND_FORMAL_SAVED_REVIEW_READY.json']),phase=(f['CURRENT_STAGE.json'] or {}).get('phase'),latest_complete=f.get('latest_complete'),startup_count=len(f.get('startup_markers',[])),health=f.get('health_compact'),worker=f.get('worker_log'),actual_processes=v['actual_processes'],locks=v['actual_fcntl_locks'],canonical=v['canonical_snapshot'])))
if __name__=='__main__':main()
