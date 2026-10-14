"""Compact, readonly actual boundary; saved originals remain complete."""
from pathlib import Path
import json,os,time
from read_linux_resume_boundary_actual import connect_linux_only
D=Path(__file__).resolve().parent
R='/mnt/mod4_linux_durable_20261013/MOD4_LINUX_FULLSTATE_REPAIR_RESUME_20261013/left_exploration20k_target_CPU_v1'
code=r'''
from pathlib import Path
import json,hashlib,os,fcntl,time
R=Path(ROOT)
names=('LEFT_NATIVE0PPO_DISPATCH_RECEIPT.json','left_native0PPO_v1/DISPATCH_RECEIPT.json','left_native0PPO_v1/EXIT_RECEIPT.json','left_native0PPO_v1/GUARDIAN_CURRENT.json','LEFT_NATIVE_ORIGINAL_ERROR.json','LEFT_NATIVE_OWN_FULLSAVE0PPO_PASSED.json')
files={n:json.loads((R/n).read_bytes()) if (R/n).exists() else None for n in names}
for n in ('left_native_parent_stdout.log','left_native0PPO_v1/worker_stdout.log'):
 p=R/n
 if p.exists():
  b=p.read_bytes();files[n]=dict(bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),tail=b[-3500:].decode(errors='replace'))
procs=[]
for x in files.values():
 if not isinstance(x,dict):continue
 for v in (x,x.get('child'),x.get('parent')):
  if isinstance(v,dict) and 'pid'in v:
   p=Path('/proc')/str(v['pid'])
   if p.exists():procs.append(dict(pid=v['pid'],cmdline=(p/'cmdline').read_bytes().replace(b'\0',b' ').decode(errors='replace'),stat=(p/'stat').read_text()))
locks=[]
for p in (Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/native_floor_supervisor.lock'),Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with p.open('r+b') as f:
  try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);held=False;fcntl.flock(f,fcntl.LOCK_UN)
  except BlockingIOError:held=True
  locks.append(dict(path=str(p),actual_held=held))
print(json.dumps(dict(epoch=time.time(),files=files,actual_processes=procs,actual_OSlocks=locks,readonly_no_PPO_or_signal=True)))
'''
def main():
 c=connect_linux_only()
 try:
  si,so,se=c.exec_command('python3 -',timeout=30);si.write('ROOT='+repr(R)+'\n'+code);si.flush();si.channel.shutdown_write();out=so.read();err=se.read();rc=so.channel.recv_exit_status()
  p=D/'reports'/('LEFT_NATIVE0PPO_CURRENT_ACTUAL_'+str(time.time_ns())+'.json');p.write_text(json.dumps(dict(code=rc,stdout=out.decode(),stderr=err.decode()),indent=2),encoding='utf8');assert rc==0,str(p)
  v=json.loads(out);f=v['files'];passed=f['LEFT_NATIVE_OWN_FULLSAVE0PPO_PASSED.json'];error=f['LEFT_NATIVE_ORIGINAL_ERROR.json']
  print(json.dumps(dict(report=str(p),own_native_passed=bool(passed),error=error,exit=f['left_native0PPO_v1/EXIT_RECEIPT.json'],processes=[x['pid'] for x in v['actual_processes']],locks=v['actual_OSlocks'],worker_tail=f.get('left_native0PPO_v1/worker_stdout.log',{}).get('tail'))))
 finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':main()
