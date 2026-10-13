"""Identify actual guarded outbound owner, read-only249; no GPU or signals."""
from pathlib import Path
import sys, os, time, json, traceback, base64, importlib.util
P = Path(__file__).resolve().parent; W = P.parent
spec = importlib.util.spec_from_file_location('prior_guard_readonly', W / 'MOD4_3060_DIRECT_FACTOR_20261013/deploy_direct3060_baseline120_WDDM_guard_reviewed_once.py')
g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
sys.path.insert(0, str(W / 'RM2026_TERRAIN_AUDIT_20261009'))
from reuse_authorized_session_transport import recover
secret, _ = recover('MOD4_EVAL_SSH_PASSWORD'); assert secret
os.environ['MOD4_EVAL_SSH_PASSWORD'] = secret
sys.path.insert(0, str(W / 'MOD4_MOE_PLAN_EXECUTION_20261007'))
from eval_remote_io import connect_eval
q = P / 'reports/REFERENCE17B_ACTUAL_EXISTING_OUTBOUND_OWNER_READONLY.json'
assert not q.exists()
code = r'''
import json,time,psutil,msvcrt,subprocess
from pathlib import Path
rows=[]
for connection in psutil.net_connections(kind='tcp'):
 if connection.raddr and connection.raddr.ip in ['10.24.4.210','172.27.131.74']:
  row=dict(pid=connection.pid,remote=list(connection.raddr),local=list(connection.laddr),status=connection.status)
  try:
   p=psutil.Process(connection.pid);row.update(creation=p.create_time(),argv=p.cmdline(),cwd=p.cwd(),exe=p.exe(),parent=p.ppid())
  except psutil.Error as error:row['process_read_error']=repr(error)
  rows.append(row)
lock=Path('D:/MOD4_async_eval/worker.lock');free=False
try:
 with lock.open('rb') as f:f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1);f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)
 free=True
except OSError:pass
workers=[]
for p in psutil.process_iter(['pid','create_time','name','cmdline','ppid']):
 try:
  x=p.info;s=' '.join(x.get('cmdline') or []).lower()
  if any(w in s for w in ['paired_direct3060','run_direct3060','eval_worker','mirror_target_tui.py','kit.exe']):workers.append(x)
 except psutil.Error:pass
print(json.dumps(dict(epoch=time.time(),outbound=rows,shared_actual_OS_lock_free=free,actual_workers=workers,
 no_signals_GPU_or_Task_changes=True,read_only249=True)))
'''
c = None
try:
 c=connect_eval();result=g.py(c,code);q.write_text(json.dumps(result,indent=2),encoding='utf8')
 print(json.dumps(dict(report=str(q),**result)))
finally:
 if c:c.close()
 os.environ.pop('MOD4_EVAL_SSH_PASSWORD',None)
