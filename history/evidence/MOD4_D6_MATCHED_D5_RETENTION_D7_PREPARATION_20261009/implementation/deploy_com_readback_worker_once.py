"""Install one new frozen authority after prior real worker/child/lock exit."""
from pathlib import Path
import sys,json,hashlib
D=Path(__file__).resolve().parent;R=D/'reports'
assert not (R/'COM_READBACK_REVIEW_WORKER_ADMITTED.json').exists()
sys.path.insert(0,str(D.parent/'MOD4_MOE_PLAN_EXECUTION_20261007'));from eval_remote_io import connect_eval
w=connect_eval();W='D:/MOD4_async_eval/closure_episode_clock2500_v15'
try:
 with w.open_sftp() as f:
  files={name:(D/name).read_bytes() for name in ('eval_worker_com_readback_review.py','admit_com_readback_worker_once.py')}
  for name,raw in files.items():
   compile(raw.decode('utf8'),name,'exec')
   try:f.stat(W+'/'+name)
   except FileNotFoundError:pass
   else:raise AssertionError('Already staged; inspect instead of rerun: '+name)
   with f.open(W+'/'+name,'wb') as o:o.write(raw)
   assert f.open(W+'/'+name).read()==raw
 _,o,e=w.exec_command('"D:/claude2/fangzhen/.venv-isaaclab/Scripts/python.exe" "'+W+'/admit_com_readback_worker_once.py"',timeout=45)
 raw=o.read();err=e.read();rc=o.channel.recv_exit_status()
 if rc:
  (R/'COM_READBACK_REVIEW_DEPLOY_ATTENTION.json').write_text(json.dumps(dict(returncode=rc,stdout=raw.decode(errors='replace'),stderr=err.decode(errors='replace')),indent=2),encoding='utf8')
  raise RuntimeError((raw+err).decode(errors='replace'))
 v=json.loads(raw);v['new_source_sha256']={name:hashlib.sha256(raw).hexdigest() for name,raw in files.items()}
 (R/'COM_READBACK_REVIEW_WORKER_ADMITTED.json').write_text(json.dumps(v,indent=2),encoding='utf8')
 print(json.dumps(dict(new_worker=v['new_worker'],new_task=v['new_task'],old_failed_SDK_retained=True,production_and_budget_unchanged=True)))
finally:w.close()
