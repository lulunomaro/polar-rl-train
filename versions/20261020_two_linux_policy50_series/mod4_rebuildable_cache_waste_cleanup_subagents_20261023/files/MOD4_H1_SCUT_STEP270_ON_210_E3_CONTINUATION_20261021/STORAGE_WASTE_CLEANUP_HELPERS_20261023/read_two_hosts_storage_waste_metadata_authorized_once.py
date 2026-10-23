from pathlib import Path
import ast,hashlib,importlib.util,json,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;S=W/'MOD4_STORAGE_WASTE_CLEANUP_SUBAGENTS_AUTHORIZED_20261023';R=S/'reports'
sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
def put(name,v):
 with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def main():
 put('TWO_HOSTS_METADATA_AUDIT_STARTED_ACTUAL.json',dict(epoch=time.time(),new_explicit_human_cleanup_scope=True,no_delete=True,one_connection_at_a_time=True))
 for host,source,py in [('210',R/'host210_agent/remote_210_readonly_waste_audit_v1.py',d.t.PY),('72',R/'host72_agent/host72_readonly_waste_audit_remote.py',d.PY72)]:
  code=source.read_text('utf8');ast.parse(code);c=None;secret=None
  try:
   if host=='210':c=d.t.connect()
   else:
    spec=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);secret=m.recover();c=d.connect72(secret);secret=None
   result=d.code(c,py,code,{},timeout=100)
   put('HOST'+host+'_FRESH_READONLY_METADATA_AUDIT_ACTUAL.json',dict(epoch=time.time(),source=str(source),source_SHA=hashlib.sha256(code.encode()).hexdigest(),remote=result,actual_call_returned=True,no_delete_or_GPU_or_training_change=True))
   print(json.dumps(dict(host=host,actual_readonly_returned=True)),flush=True)
  except BaseException:
   put('HOST'+host+'_METADATA_AUDIT_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),error=traceback.format_exc(),read_only=True,no_retry_old_once=True));raise
  finally:
   secret=None
   if c:c.close()
 put('TWO_HOSTS_METADATA_AUDIT_ALL_CONNECTIONS_RETURNED_ACTUAL.json',dict(epoch=time.time(),passed=True,all_own_audit_connections_closed=True,no_delete_or_training_or_budget_mutation=True))
if __name__=='__main__':main()
