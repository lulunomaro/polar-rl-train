"""Bounded actual-state collector; no starts, signals, RPC,210 orGPU import."""
from pathlib import Path
import sys,os,json,time,base64,hashlib,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';C=D/'actual_baseline120_collection'
ROOT='D:/MOD4_async_eval/MOD4_DIRECT_FACTOR_20261013';CASE='native3060_bodypos_worldpos_baseline120_v2'
CODE=r'''
from pathlib import Path
import json,time,psutil,msvcrt,hashlib
root=Path(ROOT);attempt=root/'attempts'/CASE;output=attempt/'output'
def read(p):return json.loads(p.read_bytes()) if p.exists() else None
names=['DEMAND_LAUNCH_ENTERED.json','DEMAND_PARENT_LAUNCH_PID.json','DEMAND_LAUNCH_EXIT.json']
top={n:read(root/n) for n in names}
states={n:read(attempt/n) for n in ['DISPATCH_RECEIPT.json','GUARDIAN_CURRENT.json','PARENT_EXIT_RECEIPT.json','SOURCE_SNAPSHOT_ACTUAL.json']}
outputs={n:read(output/n) for n in ['STARTED.json','QUERY_ACTUAL.json','COMPLETE_ACTUAL.json','SUBSTEP_HARDWARE_COM_ACTUAL.json','ORIGINAL_ERROR.json','EXIT_NATURAL.json']}
locators=[]
for row in [top['DEMAND_LAUNCH_ENTERED.json'],top['DEMAND_PARENT_LAUNCH_PID.json'],states['DISPATCH_RECEIPT.json']]:
 if not row:continue
 for pk,ck in [('pid','creation'),('parent_pid','parent_creation'),('child_pid','child_creation')]:
  if pk not in row:continue
  pid=row[pk];creation=row.get(ck)
  try:
   p=psutil.Process(pid);locators.append(dict(pid=pid,source_creation=creation,actual_creation=p.create_time(),identity_matches=creation is None or abs(creation-p.create_time())<.001,argv=p.cmdline(),cwd=p.cwd(),exe=p.exe(),parent=p.ppid(),running=True))
  except psutil.NoSuchProcess:locators.append(dict(pid=pid,source_creation=creation,running=False))
lock=Path('D:/MOD4_async_eval/worker.lock');free=False;error=None
try:
 with lock.open('rb') as f:f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1);f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)
 free=True
except OSError as e:error=dict(type=type(e).__name__,errno=e.errno,winerror=getattr(e,'winerror',None))
files=[]
for folder in [root,attempt,output]:
 if folder.exists():
  for p in folder.iterdir():
   if p.is_file() and p.name not in ['SOURCE_PACKAGE_5585cc8d.zip']:
    files.append(dict(path=str(p),relative=p.relative_to(root).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),mutable_pending=p.suffix=='.log' or p.name=='GUARDIAN_CURRENT.json'))
tail=[]
for p in [root/'DEMAND_PARENT_CONSOLE.log',attempt/'worker.log']:
 if p.exists():tail.append(dict(path=str(p),tail=p.read_bytes()[-7000:].decode('utf8','replace')))
print(json.dumps(dict(epoch=time.time(),root=str(root),attempt_exists=attempt.exists(),top=top,states=states,outputs=outputs,actual_PID_identities=locators,shared_actual_OS_lock_free=free,lock_probe_error=error,files=files,logs=tail,read_only=True,no_GPU_start_signals_RPC_or210=True)))
'''
def main():
 sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
 secret,_=recover('MOD4_EVAL_SSH_PASSWORD');assert secret;os.environ['MOD4_EVAL_SSH_PASSWORD']=secret
 sys.path.insert(0,str(W/'MOD4_MOE_PLAN_EXECUTION_20261007'));from eval_remote_io import connect_eval
 c=connect_eval();sf=None;stamp=str(time.time_ns())
 try:
  code=CODE.replace('ROOT',repr(ROOT)).replace('CASE',repr(CASE));compile(code,'<readonly actual>','exec');enc=base64.b64encode(code.encode()).decode()
  command='"D:/claude2/fangzhen/.venv-isaaclab/Scripts/python.exe" -X utf8 -c "import base64;exec(base64.b64decode(\''+enc+'\'))"'
  _,o,e=c.exec_command(command,timeout=60);raw=o.read();err=e.read();rc=o.channel.recv_exit_status();assert rc==0,err.decode('utf8','replace')
  a=json.loads(raw);sf=c.open_sftp();copied=[];complete=a['states']['PARENT_EXIT_RECEIPT.json'] is not None
  folder=C/stamp;folder.mkdir(parents=True)
  for row in a['files']:
   if row['mutable_pending'] and not complete:continue
   if row['bytes']>30_000_000 and not complete:continue
   with sf.open(row['path'].replace('\\','/'),'rb') as f:b=f.read()
   assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256'],row['path']
   p=folder/row['relative'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
   copied.append(dict(**row,local_path=str(p),remote_local_byteSHA_exact=True))
  a['local_collected_files']=copied;q=R/('DIRECT3060_BASELINE120_CURRENT_ACTUAL_'+stamp+'.json');q.write_text(json.dumps(a,ensure_ascii=False,indent=2),encoding='utf8')
  print(json.dumps(dict(report=str(q),attempt_exists=a['attempt_exists'],PID=a['actual_PID_identities'],lock_free=a['shared_actual_OS_lock_free'],parent_exit=a['states']['PARENT_EXIT_RECEIPT.json'],outputs={k:v is not None for k,v in a['outputs'].items()},logs=a['logs'])),flush=True)
 except Exception as e:
  q=R/('DIRECT3060_BASELINE120_READER_ORIGINAL_ERROR_'+stamp+'.json');q.write_text(json.dumps(dict(epoch=time.time(),error=repr(e),traceback=traceback.format_exc(),read_only=True),ensure_ascii=False,indent=2),encoding='utf8');raise
 finally:
  if sf:sf.close()
  c.close();os.environ.pop('MOD4_EVAL_SSH_PASSWORD',None)
if __name__=='__main__':main()
