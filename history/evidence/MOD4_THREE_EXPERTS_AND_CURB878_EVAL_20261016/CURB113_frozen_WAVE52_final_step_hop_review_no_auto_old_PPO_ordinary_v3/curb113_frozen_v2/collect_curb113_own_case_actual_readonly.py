from pathlib import Path
import argparse,hashlib,json,sys,time,traceback
D=Path(__file__).resolve().parent;R=D/'reports';ROOT='D:/MOD4_async_eval/MOD4_THREE_EXPERTS_AND_CURB878_EVAL_20261016/curb113_frozen_v2';sys.path.insert(0,str(D.parents[1]/'MOD4_3060_BODYFRAME_FIRST_FULL80_20261014'));import transport_249_bodyframe_current_terminal_role_v3 as t
CODE=r'''
from pathlib import Path
import hashlib,json,psutil,time,msvcrt
R=Path(ROOT);A=R/'attempts'/CASE;rows=[]
def read(p):return json.loads(p.read_bytes()) if p.exists() else None
for p in [R/(CASE+'_START_INTENT.json'),R/(CASE+'_PARENT_PID.json'),A/'DISPATCH_RECEIPT.json']:
 x=read(p)
 if not x:continue
 for pk,ck in (('pid','creation'),('parent_pid','parent_creation'),('child_pid','child_creation')):
  if pk not in x:continue
  try:q=psutil.Process(x[pk]);same=q.create_time()==x[ck];rows.append(dict(pid=x[pk],expected_creation=x[ck],actual_creation=q.create_time(),same_identity_alive=same,argv=q.cmdline()))
  except psutil.NoSuchProcess:rows.append(dict(pid=x[pk],same_identity_alive=False,absent=True))
parent=read(A/'PARENT_EXIT_RECEIPT.json');launch=read(R/(CASE+'_LAUNCH_EXIT.json'));closed=bool(parent and launch and not any(x['same_identity_alive'] for x in rows));free=False
try:
 with Path('D:/MOD4_async_eval/worker.lock').open('rb') as f:f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1);f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1);free=True
except OSError:pass
files=[]
if closed:
 for p in sorted(A.rglob('*')):
  if p.is_file():files.append(dict(relative=p.relative_to(R).as_posix(),bytes=p.stat().st_size,SHA=hashlib.file_digest(p.open('rb'),'sha256').hexdigest()))
v=dict(epoch=time.time(),case=CASE,parent_exit=parent,launcher_exit=launch,actual_identities=rows,parent_child_launcher_actual_absent=closed,shared_OS_lock_free=free,complete=read(A/'output/COMPLETE_ACTUAL.json'),original_error=read(A/'output/ORIGINAL_ERROR.json'),files=files)
if (A/'worker.log').exists():v['worker_tail']=(A/'worker.log').read_text(encoding='utf8',errors='replace')[-12000:]
print(json.dumps(v))
'''
def main():
 p=argparse.ArgumentParser();p.add_argument('--steps',type=int,choices=(120,1500),required=True);a=p.parse_args();case=f'curb_independent113_{a.steps}_v1';stamp=str(time.time_ns());c=sf=None
 try:
  c=t.connect();v=t.py(c,'ROOT='+repr(ROOT)+'\nCASE='+repr(case)+'\n'+CODE,60)
  if v['parent_child_launcher_actual_absent']:
   out=D/'actual_eval_collections'/case/stamp;out.mkdir(parents=True);sf=c.open_sftp();sf.get_channel().settimeout(120)
   for r in v['files']:
    p=out/r['relative'];p.parent.mkdir(parents=True,exist_ok=True);sf.get(ROOT+'/'+r['relative'],str(p));assert p.stat().st_size==r['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==r['SHA'];r['local_path']=str(p.resolve())
  report=R/(case+'_ACTUAL_BOUNDARY_COLLECTION_'+stamp+'.json');report.write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(dict(report=str(report),case=case,closed=v['parent_child_launcher_actual_absent'],free=v['shared_OS_lock_free'],complete=v['complete'],error=v['original_error'],tail=v.get('worker_tail','')[-3000:])),flush=True)
 finally:
  if sf:sf.close()
  t.close(c)
if __name__=='__main__':
 try:main()
 except BaseException:
  (R/('CURB113_COLLECTOR_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(error=traceback.format_exc(),no_replay=True),indent=2));raise
