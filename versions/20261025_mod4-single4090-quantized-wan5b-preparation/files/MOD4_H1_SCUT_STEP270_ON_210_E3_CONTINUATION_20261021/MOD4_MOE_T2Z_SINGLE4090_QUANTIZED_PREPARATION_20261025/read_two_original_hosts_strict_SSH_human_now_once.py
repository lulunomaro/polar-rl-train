"""Human current connectivity question: two original pinned SSH endpoints, no jobs."""
from pathlib import Path
import importlib.util,json,os,sys,time,traceback
Q=Path(__file__).resolve().parent;T=Q.parent;W=T.parent;R=Q/'reports'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
put('HUMAN_NOW_TWO_HOSTS_STRICT_SSH_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,human='现在双4090主机和单4090主机谁能连上？'))
sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
spec=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
rows=[]
for label,endpoint in [('dual4090_72','10.24.0.72'),('single4090_210','10.24.4.210')]:
 c=None;secret=None;started=time.time();row=dict(label=label,endpoint=endpoint,check_started_epoch=started)
 try:
  if label=='dual4090_72':secret=m.recover();c=d.connect72(secret);secret=None
  else:c=d.t.connect()
  assert c.get_transport().is_active() and c.get_transport().is_authenticated()
  row.update(strict_original_host_pin_and_SSH_authentication_succeeded=True,remote_commands_executed=0)
 except BaseException as e:row.update(strict_original_host_pin_and_SSH_authentication_succeeded=False,error_type=type(e).__name__,original_error=traceback.format_exc())
 finally:
  secret=None
  if c:c.close()
 row.update(check_finished_epoch=time.time(),elapsed_seconds=time.time()-started);rows.append(row)
result=dict(epoch=time.time(),connectivity_rows=rows,no_GPU_host_identity_model_raw_job_stop_or_budget_command=True,connections_actual_returned=True)
put('HUMAN_NOW_TWO_HOSTS_STRICT_SSH_RETURNED_ACTUAL.json',result)
print(json.dumps(dict(epoch=result['epoch'],rows=[{k:v for k,v in x.items() if k!='original_error'} for x in rows])))
