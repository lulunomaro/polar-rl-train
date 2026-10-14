"""Root-only readonly metadata and completed artifact collection."""
from pathlib import Path
import argparse,sys,json,time,hashlib,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports'
sys.path.insert(0,str(D));import transport_249_own_phase_final_retention as t
t.ROOT='D:/MOD4_async_eval/MOD4_3060_BODYFRAME_PHASE_FINAL_RETENTION_20261015'
CODE=r'''
from pathlib import Path
import json,hashlib,time,psutil,msvcrt
R=Path(ROOT);A=R/'attempts'/CASE;O=A/'output'
def read(p):return json.loads(p.read_bytes()) if p.exists() else None
top={n:read(R/(CASE+'_'+n+'.json')) for n in ('START_INTENT','PARENT_PID','LAUNCH_EXIT')}
states={n:read(A/n) for n in ('DISPATCH_RECEIPT.json','GUARDIAN_CURRENT.json','PARENT_EXIT_RECEIPT.json')}
outputs={n:read(O/n) for n in ('STARTED.json','COMPLETE_ACTUAL.json','ORIGINAL_ERROR.json','EXIT_NATURAL.json')}
locators=[]
for row in (top['START_INTENT'],top['PARENT_PID'],states['DISPATCH_RECEIPT.json']):
 if not row:continue
 for pk,ck in (('pid','creation'),('parent_pid','parent_creation'),('child_pid','child_creation')):
  if pk not in row:continue
  try:
   p=psutil.Process(row[pk]);locators.append(dict(pid=p.pid,creation=p.create_time(),argv=p.cmdline(),cwd=p.cwd(),expected_creation=row.get(ck),actual_alive=True))
  except psutil.NoSuchProcess:locators.append(dict(pid=row[pk],actual_alive=False))
free=False
try:
 with Path('D:/MOD4_async_eval/worker.lock').open('r+b') as f:f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1);f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)
 free=True
except OSError:pass
files=[];complete=states['PARENT_EXIT_RECEIPT.json'] is not None
for folder in (R,A,O,A/'source_snapshot'):
 if folder.exists():
  for p in (folder.rglob('*') if folder.name=='source_snapshot' else folder.iterdir()):
   if p.is_file() and p.suffix!='.zip' and (complete or p.suffix!='.npz'):
    b=p.read_bytes();files.append(dict(path=str(p),relative=p.relative_to(R).as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),mutable_pending=p.name=='GUARDIAN_CURRENT.json' or p.suffix=='.log'))
log=A/'worker.log';tail=log.read_bytes()[-2500:].decode(errors='replace') if log.exists() else ''
print(json.dumps(dict(epoch=time.time(),root=str(R),case=CASE,top=top,states=states,outputs=outputs,actual_PID_identities=locators,shared_OS_lock_free=free,files=files,worker_tail=tail,readonly=True)))
'''
def main():
 a=argparse.ArgumentParser();a.add_argument('--case',required=True);a.add_argument('--execute-root-readonly-collection',action='store_true');a=a.parse_args();assert a.execute_root_readonly_collection,'Explicit root readonly collection flag required';assert a.case.replace('_','').isalnum()
 c=t.connect();sf=None;stamp=str(time.time_ns())
 try:
  v=t.py(c,'ROOT='+repr(t.ROOT)+'\nCASE='+repr(a.case)+'\n'+CODE,70)
  complete=v['states']['PARENT_EXIT_RECEIPT.json'] is not None;rows=[]
  if complete:
   dest=D/'actual_collections'/a.case/stamp;dest.mkdir(parents=True);sf=c.open_sftp();sf.get_channel().settimeout(60)
   for row in v['files']:
    p=dest/row['relative'];p.parent.mkdir(parents=True,exist_ok=True);sf.get(row['path'].replace('\\','/'),str(p),max_concurrent_prefetch_requests=16)
    assert p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
    rows.append(dict(**row,local_path=str(p),two_host_byteSHA_exact=True))
  v['collected_files']=rows;report=R/(a.case+'_CURRENT_ACTUAL_'+stamp+'.json');report.write_text(json.dumps(v,indent=2),encoding='utf8')
  if complete:
   identities=v['actual_PID_identities'];boundary=dict(actual_parent_absent=all(not x['actual_alive'] for x in identities),actual_child_absent=all(not x['actual_alive'] for x in identities),shared_OS_lock_free=v['shared_OS_lock_free'],original_EXIT_NATURAL_missing=v['outputs']['EXIT_NATURAL.json'] is None,actual_parent_exit=v['states']['PARENT_EXIT_RECEIPT.json'],all_PID_identities=identities,complete_dataset_present=v['outputs']['COMPLETE_ACTUAL.json'] is not None,original_failure=v['outputs']['ORIGINAL_ERROR.json'])
   q=R/(a.case+'_INDEPENDENT_BOUNDARY.json');assert not q.exists();q.write_text(json.dumps(boundary,indent=2),encoding='utf8')
   attempt=dest/'attempts'/a.case
  else:q=None;attempt=None
  print(json.dumps(dict(report=str(report),complete=complete,outputs={k:z is not None for k,z in v['outputs'].items()},parent_exit=v['states']['PARENT_EXIT_RECEIPT.json'],actual_PIDs=v['actual_PID_identities'],lock_free=v['shared_OS_lock_free'],boundary=str(q) if q else None,local_attempt=str(attempt) if attempt else None,worker_tail=v['worker_tail'])))
 except BaseException:
  (R/(a.case+'_ORIGINAL_READER_ERROR_'+stamp+'.json')).write_text(json.dumps(dict(error=traceback.format_exc(),readonly=True),indent=2),encoding='utf8');raise
 finally:
  if sf:sf.close()
  t.close(c)
if __name__=='__main__':main()
