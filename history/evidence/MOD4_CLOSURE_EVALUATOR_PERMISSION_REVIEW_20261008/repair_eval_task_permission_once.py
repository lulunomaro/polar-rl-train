from pathlib import Path
import sys,json,hashlib
D=Path(__file__).resolve().parent;R=D/'reports';root='D:/MOD4_async_eval/closure_episode_clock2500_v15'
assert not (R/'EVALUATOR_PERMISSION_REPAIRED.json').exists();sys.path.insert(0,str(D.parent/'MOD4_MOE_PLAN_EXECUTION_20261007'));from eval_remote_io import connect_eval
c=connect_eval()
try:
 with c.open_sftp() as sf:
  sf.put(str(D/'handover_eval_permission_review.py'),root+'/handover_eval_permission_review.py')
 # Run in the authorized SSH administration context, not the limited bootstrap task.
 _,o,e=c.exec_command('"D:/claude2/fangzhen/.venv-isaaclab/Scripts/python.exe" "'+root+'/handover_eval_permission_review.py"',timeout=45);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
 with c.open_sftp() as sf:
  for n in ('HANDOVER_COMPLETE.json','HANDOVER_PERMISSION_REVIEW_STARTED.json','HANDOVER_ATTENTION.json','OLD_TASK_RETAINED.xml','BOOTSTRAP_TASK_RETAINED.xml'):
   sf.get(root+'/'+n,str(R/n))
 v=json.loads((R/'HANDOVER_COMPLETE.json').read_text());v['permission_reader_source_sha256']=hashlib.sha256((D/'handover_eval_permission_review.py').read_bytes()).hexdigest();v['limited_bootstrap_permission_failure_retained']=True;v['completed_bootstrap_task_removed']=True;v['training_runtime_unmodified']=True
 (R/'EVALUATOR_PERMISSION_REPAIRED.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(v))
finally:c.close()
