from pathlib import Path
import sys,json,hashlib,ast,time
D=Path(__file__).resolve().parent;R=D/'reports';root='D:/MOD4_async_eval/closure_episode_clock2500_v15'
assert not (R/'EVALUATOR_STAGED.json').exists();sys.path.insert(0,str(D.parent/'MOD4_MOE_PLAN_EXECUTION_20261007'));from eval_remote_io import connect_eval
for n in ('eval_worker_closure2500.py','handover_eval_idle.py'):ast.parse((D/n).read_text(encoding='utf8'))
c=connect_eval()
try:
 with c.open_sftp() as sf:
  try:sf.stat(root);raise AssertionError('New evaluator already exists; no repeat')
  except FileNotFoundError:pass
  sf.mkdir(root)
  for n in ('eval_worker_closure2500.py','handover_eval_idle.py'):sf.put(str(D/n),root+'/'+n)
 v=dict(epoch=time.time(),root=root,source_sha256={n:hashlib.sha256((D/n).read_bytes()).hexdigest() for n in ('eval_worker_closure2500.py','handover_eval_idle.py')},namespace='clk2500-closure-episode-d3-',clock=.0025,solver=[32,4],staged_only=True,existing_GPU_jobs_not_interrupted=True,no_canonical_write_or_training_launch_authority=True)
 (R/'EVALUATOR_STAGED.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(v))
finally:c.close()
