"""Install one new evaluator authority after proving old processes and lock exited."""
from pathlib import Path
import sys,json,hashlib
D=Path(__file__).resolve().parent;R=D/'reports'
assert not (R/'JOB_IDENTIFIER_REVIEW_WORKER_ADMITTED.json').exists()
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
sys.path.insert(0,str(D.parent/'MOD4_MOE_PLAN_EXECUTION_20261007'));from eval_remote_io import connect_eval
n=connect();w=connect_eval();W='D:/MOD4_async_eval/closure_episode_clock2500_v15'
try:
 with n.open_sftp() as nf,w.open_sftp() as wf:
  actual=nf.open('/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/artifact_service.py').read()
  assert actual==(D.parent/'MOD4_MOE_PLAN_EXECUTION_20261007/artifact_service.py').read_bytes()
  (R/'artifact_service_identifier_snapshot.py').write_bytes(actual)
  files={name:(D/name).read_bytes() for name in ('job_identifier_contract.py','test_job_identifier_contract.py','eval_worker_job_identifier_review.py','admit_job_identifier_review_once.py')}
  files['artifact_service_identifier_snapshot.py']=actual
  for name,raw in files.items():
   compile(raw.decode('utf8'),name,'exec')
   try:wf.stat(W+'/'+name)
   except FileNotFoundError:pass
   else:raise AssertionError('Already staged; inspect instead of rerun: '+name)
   with wf.open(W+'/'+name,'wb') as f:f.write(raw)
   assert wf.open(W+'/'+name).read()==raw
  hashes={k:hashlib.sha256(v).hexdigest() for k,v in files.items()}
 for name,args,receipt in [('test_job_identifier_contract.py',' "'+W+'/artifact_service_identifier_snapshot.py"','JOB_IDENTIFIER_REVIEW_TARGET_CPU_PASSED.json'),('admit_job_identifier_review_once.py','','JOB_IDENTIFIER_REVIEW_WORKER_ADMITTED.json')]:
  _,o,e=w.exec_command('"D:/claude2/fangzhen/.venv-isaaclab/Scripts/python.exe" "'+W+'/'+name+'"'+args,timeout=45)
  raw=o.read();err=e.read();rc=o.channel.recv_exit_status()
  if rc:
   (R/'JOB_IDENTIFIER_DEPLOY_ATTENTION.json').write_text(json.dumps(dict(entry=name,returncode=rc,stdout=raw.decode(errors='replace'),stderr=err.decode(errors='replace')),indent=2),encoding='utf8')
   raise RuntimeError((raw+err).decode(errors='replace'))
  v=json.loads(raw);v['new_source_sha256']=hashes
  (R/receipt).write_text(json.dumps(v,indent=2),encoding='utf8')
  print(json.dumps(dict(receipt=receipt,CPU_cases=v.get('CPU_cases'),new_worker=v.get('new_worker'),new_task=v.get('new_task'),no_4090_runtime_PPO_or_budget_mutation=True)))
finally:w.close();n.close()
