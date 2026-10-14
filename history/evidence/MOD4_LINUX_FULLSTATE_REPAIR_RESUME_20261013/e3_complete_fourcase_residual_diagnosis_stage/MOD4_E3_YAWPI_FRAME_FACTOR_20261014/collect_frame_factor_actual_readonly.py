"""One bounded own-case read; source snapshots and complete data byte-SHA."""
from pathlib import Path
import sys,json,time,hashlib,traceback,os,argparse
P=Path(__file__).resolve().parent;R=P/'reports';W=P.parent
sys.path.insert(0,str(W/'MOD4_3060_LINUX_RESUME_REFERENCE_20261014'))
import transport_249_only as t
t.ROOT='D:/MOD4_async_eval/MOD4_E3_YAWPI_FRAME_FACTOR_20261014'
CODE='''from pathlib import Path
import json,time,hashlib,psutil,msvcrt
root=Path(ROOT);attempt=root/'attempts'/CASE;output=attempt/'output'
def read(p):return json.loads(p.read_bytes()) if p.exists() else None
top={n:read(root/n) for n in ['NATIVE120_LAUNCH_ENTERED.json','NATIVE120_PARENT_LAUNCH_PID.json','NATIVE120_LAUNCH_EXIT.json','FULL1500_LAUNCH_ENTERED.json','FULL1500_PARENT_LAUNCH_PID.json','FULL1500_LAUNCH_EXIT.json']}
states={n:read(attempt/n) for n in ['DISPATCH_RECEIPT.json','GUARDIAN_CURRENT.json','PARENT_EXIT_RECEIPT.json','SOURCE_SNAPSHOT_ACTUAL.json']}
outputs={n:read(output/n) for n in ['STARTED.json','QUERY_ACTUAL.json','COMPLETE_ACTUAL.json','SUBSTEP_HARDWARE_COM_ACTUAL.json','FROZEN_POLICY_SOURCE_ACTUAL.json','FIRST_PHYSICS_INITIAL_ACTUAL.json','YAWPI_FACTOR_FIRST_PHYSICS_ACTUAL.json','ORIGINAL_ERROR.json','EXIT_NATURAL.json']}
locators=[]
for row in list(top.values())+[states['DISPATCH_RECEIPT.json'],outputs['STARTED.json']]:
 if not row:continue
 for pk,ck in [('pid','creation'),('parent_pid','parent_creation'),('child_pid','child_creation')]:
  if pk not in row:continue
  pid=row[pk];creation=row.get(ck)
  try:
   p=psutil.Process(pid);locators.append(dict(pid=pid,source_creation=creation,actual_creation=p.create_time(),identity_matches=creation is None or abs(creation-p.create_time())<.001,argv=p.cmdline(),cwd=p.cwd(),exe=p.exe(),parent=p.ppid(),running=True))
  except psutil.NoSuchProcess:locators.append(dict(pid=pid,source_creation=creation,running=False))
free=False;error=None;lock=Path('D:/MOD4_async_eval/worker.lock')
try:
 with lock.open('r+b') as f:f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1);f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)
 free=True
except OSError as e:error=dict(type=type(e).__name__,errno=e.errno,winerror=getattr(e,'winerror',None))
files=[]
for folder in [root,attempt,output,attempt/'source_snapshot']:
 if folder.exists():
  for p in folder.iterdir():
   if p.is_file() and p.suffix!='.zip':
    hh=hashlib.sha256()
    with p.open('rb') as f:
     while block:=f.read(8388608):hh.update(block)
    files.append(dict(path=str(p),relative=p.relative_to(root).as_posix(),bytes=p.stat().st_size,sha256=hh.hexdigest(),mutable_pending=p.suffix=='.log' or p.name=='GUARDIAN_CURRENT.json'))
tail=[]
for p in [root/'NATIVE120_PARENT_CONSOLE.log',root/'FULL1500_PARENT_CONSOLE.log',attempt/'worker.log']:
 if p.exists():
  with p.open('rb') as f:f.seek(max(0,p.stat().st_size-7000));b=f.read()
  tail.append(dict(path=str(p),tail=b.decode('utf8','replace')))
print(json.dumps(dict(epoch=time.time(),root=str(root),case=CASE,attempt_exists=attempt.exists(),top=top,states=states,outputs=outputs,actual_PID_identities=locators,shared_actual_OS_lock_free=free,lock_probe_error=error,files=files,logs=tail,read_only=True,no_GPU_start_signals_RPC_or210=True)))
'''

def main():
 p=argparse.ArgumentParser();p.add_argument('--case',choices=['e3_yawpi_same_world_native120_v2','e3_yawpi_same_world_full1500_v2'],required=True);args=p.parse_args()
 stamp=str(time.time_ns());c=sf=None
 try:
  c=t.connect();code=CODE.replace('ROOT',repr(t.ROOT)).replace('CASE',repr(args.case));a=t.py(c,code)
  sf=c.open_sftp();sf.get_channel().settimeout(60);folder=P/'actual_collections'/stamp;folder.mkdir(parents=True);copied=[]
  complete=a['states']['PARENT_EXIT_RECEIPT.json'] is not None
  for row in a['files']:
   if row['mutable_pending'] and not complete:continue
   if row['bytes']>30_000_000 and not complete:continue
   out=folder/row['relative'];out.parent.mkdir(parents=True,exist_ok=True)
   sf.get(row['path'].replace('\\','/'),str(out),max_concurrent_prefetch_requests=16)
   hh=hashlib.sha256()
   with out.open('rb') as f:
    while block:=f.read(8388608):hh.update(block)
   assert out.stat().st_size==row['bytes'] and hh.hexdigest()==row['sha256'],row['path']
   copied.append(dict(**row,local_path=str(out),remote_local_byteSHA_exact=True))
  a['local_collected_files']=copied;out=R/('FRAME_'+args.case+'_ACTUAL_COLLECTION_'+stamp+'.json');assert not out.exists();out.write_bytes(json.dumps(a,ensure_ascii=False,indent=2).encode())
  print(json.dumps(dict(report=str(out),case=args.case,actual_PID=a['actual_PID_identities'],lock_free=a['shared_actual_OS_lock_free'],parent_exit=a['states']['PARENT_EXIT_RECEIPT.json'],outputs={k:v is not None for k,v in a['outputs'].items()},logs=a['logs'])),flush=True)
 except BaseException:
  out=R/('FRAME_READER_ORIGINAL_ERROR_'+stamp+'.json');out.write_bytes(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),read_only=True),indent=2).encode());raise
 finally:
  if sf:sf.close()
  t.close(c)

if __name__=='__main__':main()
