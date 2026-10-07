"""Deploy the separate reviewed worker on the authorized evaluation host."""
from pathlib import Path
import sys,json,hashlib
D=Path(__file__).resolve().parent;R=D/'reports';W=D.parent
assert not (R/'CLOCK1000_WORKER_DEPLOYED.json').exists()
proof=json.loads((R/'CLOCK1000_PACKAGE_STAGED.json').read_text());assert not proof['queue_published']
source_review=json.loads((R/'CLOCK1000_WORKER_SOURCE_REVIEW.json').read_text())
assert hashlib.sha256((D/'eval_worker_clock1000.py').read_bytes()).hexdigest()==source_review['new_worker_sha256']
sys.path.insert(0,str(W/'MOD4_MOE_PLAN_EXECUTION_20261007'));from eval_remote_io import connect_eval
c=connect_eval();root='D:/MOD4_async_eval/history_clock1000_v15'
try:
 with c.open_sftp() as s:
  try:s.stat(root)
  except FileNotFoundError:pass
  else:raise AssertionError('New root already exists; inspect before any retry')
  s.mkdir(root)
  for n in ['eval_worker_clock1000.py','handover_eval_worker_clock1000_once.py']:s.put(str(D/n),root+'/'+n)
  s.put(str(R/'CLOCK1000_WORKER_SOURCE_REVIEW.json'),root+'/WORKER_SOURCE_REVIEW.json')
 _,o,e=c.exec_command('"D:/claude2/fangzhen/.venv-isaaclab/Scripts/python.exe" "'+root+'/handover_eval_worker_clock1000_once.py"',timeout=50)
 raw=o.read();err=e.read();rc=o.channel.recv_exit_status()
 if rc:
  (R/'CLOCK1000_WORKER_FIRST_DEPLOY_ERROR.txt').write_bytes(raw+err);raise AssertionError((raw+err).decode(errors='replace'))
 v=json.loads(raw);(R/'CLOCK1000_WORKER_DEPLOYED.json').write_text(json.dumps(v,indent=2),encoding='utf8')
 print(json.dumps(v))
finally:c.close()
