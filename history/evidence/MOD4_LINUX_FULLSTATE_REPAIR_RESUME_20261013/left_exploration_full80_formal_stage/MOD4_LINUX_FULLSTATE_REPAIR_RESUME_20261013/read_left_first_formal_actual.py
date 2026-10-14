"""Readonly compact actual formal state. Never import old once controllers."""
from pathlib import Path
import json,os,time
from remote_session import execute
R='/mnt/mod4_linux_durable_20261013/MOD4_LINUX_FULLSTATE_REPAIR_RESUME_20261013/left_exploration20k_first_formal_v1'
CODE=r'''
from pathlib import Path
import json,hashlib,time,fcntl
R=Path(ROOT);a=R/'left_formal3600_v1'
def read(p):return json.loads(p.read_bytes()) if p.exists() else None
files={n:read(R/n) for n in ('LEFT_FORMAL_DISPATCH_ACTUAL.json','CURRENT_STAGE.json','LEFT_FORMAL_PARENT_ERROR.json','LEFT_FORMAL_SAVED_REVIEW_READY.json')}
files.update({n:read(a/n) for n in ('DISPATCH_RECEIPT.json','EXIT_RECEIPT.json','GUARDIAN_CURRENT.json')})
folders=list((a/'learning_logs').glob('*')) if (a/'learning_logs').exists() else []
if folders:
 assert len(folders)==1
 f=folders[0];files['latest_complete']=read(f/'latest_complete.json');h=read(f/'CLOCK_TRAINING_HEALTH.json');files['health_compact']={k:v for k,v in (h or {}).items() if isinstance(v,(str,int,float,bool)) or v is None}
 files['startup_markers']=[p.name for p in f.glob('*STARTUP*VERIFIED.json')]
 files['log_dir']=str(f)
log=a/'worker_stdout.log'
if log.exists():
 b=log.read_bytes();files['worker_log']=dict(bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),tail=b[-2600:].decode(errors='replace'),has_traceback=b'Traceback (most recent call last)' in b,capacity_error=any(x in b for x in (b'buffer overflow detected',b'Contacts have been dropped',b'PhysX scene is corrupted',b'CUDA error')))
actual=[]
for pid in sorted({v['pid'] for x in files.values() if isinstance(x,dict) for v in (x,x.get('parent',{}),x.get('child',{})) if isinstance(v,dict) and 'pid' in v}):
 p=Path('/proc')/str(pid)
 if p.exists():actual.append(dict(pid=pid,start_ticks=int((p/'stat').read_text().split(') ',1)[1].split()[19]),argv=(p/'cmdline').read_bytes().replace(b'\0',b' ').decode(errors='replace')))
locks=[]
for p in (Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/native_floor_supervisor.lock'),Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with p.open('r+b') as f:
  try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);held=False;fcntl.flock(f,fcntl.LOCK_UN)
  except BlockingIOError:held=True
  locks.append(dict(path=str(p),held=held))
print(json.dumps(dict(epoch=time.time(),root=str(R),files=files,actual_processes=actual,actual_fcntl_locks=locks,readonly_no_PPO_or_signal=True)))
'''
def main():
 v,p=execute('ROOT='+repr(R)+'\n'+CODE,'LEFT_FIRST_FORMAL_CURRENT_ACTUAL',40)
 f=v['files'];print(json.dumps(dict(report=str(p),parent_error=f['LEFT_FORMAL_PARENT_ERROR.json'],phase=(f['CURRENT_STAGE.json'] or {}).get('phase'),ownfinal=bool(f['LEFT_FORMAL_SAVED_REVIEW_READY.json']),latest_complete=f.get('latest_complete'),startup_count=len(f.get('startup_markers',[])),health=f.get('health_compact'),worker=f.get('worker_log'),actual_processes=v['actual_processes'],locks=v['actual_fcntl_locks'])))
if __name__=='__main__':main()
