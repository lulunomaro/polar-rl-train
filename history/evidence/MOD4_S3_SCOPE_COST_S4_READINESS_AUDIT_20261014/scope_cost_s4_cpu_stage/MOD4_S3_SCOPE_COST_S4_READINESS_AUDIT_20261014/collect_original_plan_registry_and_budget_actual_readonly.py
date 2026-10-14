"""Sole-root bounded Linux read of original plan/registry/canonical evidence.

No GPU imports, task starts, signals, budget writes or lockfile mutations.
"""
from pathlib import Path
import sys,json,time,hashlib,os,traceback
A=Path(__file__).resolve().parent;W=A.parent;R=A/'reports';R.mkdir(exist_ok=True)
sys.path.insert(0,str(W/'MOD4_LINUX_FULLSTATE_REPAIR_RESUME_20261013'))
from read_linux_resume_boundary_actual import connect_linux_only
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
DISCOVER='''from pathlib import Path
import json,time,hashlib,fcntl,os,socket
B=Path('/home/egde/rl_candidates');roots=[]
for p in sorted(B.iterdir()):
 if p.is_dir() and any(s in p.name for s in ('MOE_PLAN_EXECUTION','EXPERT_REGISTRY','EXPERT_INTERFACE','S1_EXPERT','MOE_EXPERT')):roots.append(p)
files=[]
for root in roots:
 for folder in [root,root/'reports']:
  if not folder.is_dir():continue
  for p in sorted(folder.iterdir()):
   if p.is_file() and p.suffix in ('.json','.md') and any(s in p.name.upper() for s in ('APPROVAL','REGISTRY','EXECUTION_TRACK','EXECUTION_CURRENT','MASTER_PLAN','REVISION_004','REVISION_005','EXPERT_SCOPE')):
    files.append(p)
canonical=B/'MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json';assert canonical.is_file();files.append(canonical)
rows=[]
for p in files:
 assert p.resolve().is_relative_to(B.resolve()) and p.stat().st_size<25000000
 b=p.read_bytes();rows.append(dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest()))
locks=[]
for p in [B/'MOD4_native_floor_continue10h_20260930/native_floor_supervisor.lock',B/'MOD4_scut_spin_rate_20261002/autonomy_controller.lock']:
 held=False;exists=p.is_file()
 if exists:
  fd=os.open(p,os.O_RDONLY)
  try:
   try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
   except BlockingIOError:held=True
   else:fcntl.flock(fd,fcntl.LOCK_UN)
  finally:os.close(fd)
 locks.append(dict(path=str(p),exists=exists,actual_fcntl_held=held))
print(json.dumps(dict(epoch=time.time(),hostname=socket.gethostname(),roots=[str(p) for p in roots],files=rows,canonical_path=str(canonical),locks=locks,read_only=True,no_GPU_PPO_signal_budgetwrite=True)))
'''

def main():
 stamp=str(time.time_ns());c=sf=None
 try:
  c=connect_linux_only();assert c.get_transport().getpeername()[0]=='10.24.4.210'
  si,so,se=c.exec_command('python3 -',timeout=60);si.write(DISCOVER);si.flush();si.channel.shutdown_write()
  raw=so.read();err=se.read();rc=so.channel.recv_exit_status();assert rc==0,err.decode('utf8','replace')
  result=json.loads(raw);folder=A/'actual_original_metadata'/stamp;folder.mkdir(parents=True)
  sf=c.open_sftp();sf.get_channel().settimeout(60);copied=[]
  for i,row in enumerate(result['files']):
   out=folder/(str(i)+'_'+Path(row['path']).name)
   sf.get(row['path'],str(out),max_concurrent_prefetch_requests=16)
   assert out.stat().st_size==row['bytes'] and H(out)==row['sha256']
   copied.append(dict(**row,local_path=str(out.resolve()),two_host_bytes_SHA_exact=True))
  result['local_collected_files']=copied
  p=R/('ORIGINAL_PLAN_REGISTRY_CANONICAL_ACTUAL_COLLECTION_'+stamp+'.json');assert not p.exists();p.write_bytes(json.dumps(result,ensure_ascii=False,indent=2).encode())
  budget=json.loads(next(Path(x['local_path']).read_bytes() for x in copied if x['path']==result['canonical_path']))
  print(json.dumps(dict(report=str(p.resolve()),roots=result['roots'],file_names=[Path(x['path']).name for x in copied],canonical_bytes_SHA_exact=True,canonical_top_keys=list(budget),actual_locks=result['locks'],no_GPU_or_PPO_or_budgetwrite=True)),flush=True)
 except BaseException:
  p=R/('ORIGINAL_PLAN_REGISTRY_READONLY_ERROR_'+stamp+'.json');p.write_bytes(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),read_only=True,no_retry_automatic=True),indent=2).encode());raise
 finally:
  if sf:sf.close()
  if c:c.close()
  os.environ.pop('RM_SSH_PASSWORD',None)

if __name__=='__main__':main()
