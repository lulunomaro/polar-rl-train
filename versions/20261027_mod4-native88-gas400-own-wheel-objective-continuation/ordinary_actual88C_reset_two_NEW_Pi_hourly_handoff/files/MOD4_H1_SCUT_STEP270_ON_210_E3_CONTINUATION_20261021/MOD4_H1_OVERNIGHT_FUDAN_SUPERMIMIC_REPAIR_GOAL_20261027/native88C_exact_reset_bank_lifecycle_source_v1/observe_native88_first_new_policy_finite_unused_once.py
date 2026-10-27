"""UNUSED actual-GO-bound first new Pi observer; one finite serial text read."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import argparse,json,hashlib,importlib.util,time,traceback,os
from native88_closing_protocol_v1 import validate_detached,validate_actual_GO_binding,bind_prepared_detached,KEYS
D=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_bytes())
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(R,name,v):
 with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def extract_go(v):
 if isinstance(v.get('go'),dict):return v['go']
 if 'current' in v and v['current']:return v['current']['go']
 if 'owner' in v:return v['owner']['current']['go']
 return v['authority72']['cohort']['go']
def main():
 p=argparse.ArgumentParser()
 for name in ('stage','prepared-report','detached-report','go-report'):p.add_argument('--'+name,required=True)
 a=p.parse_args();N=Path(a.stage).resolve();R=N/'reports';require_name='H1_STEP270_OWN_STEP_GAS400_NATIVE_RESOURCE_V88C_20261027';assert N.name==require_name
 paths=[Path(x).resolve() for x in (a.prepared_report,a.detached_report,a.go_report)];assert all(x.is_relative_to(R) and x.is_file() and not x.is_symlink() for x in paths)
 prepared,q,gvalue=map(read,paths);q=bind_prepared_detached(q,prepared);validate_detached(q,prepared);go=extract_go(gvalue);validate_actual_GO_binding(go,q)
 begin=time.time();deadline=begin+1200
 put(R,'NATIVE88_FIRST_NEW_POLICY_OBSERVER_STARTED_ACTUAL.json',dict(epoch=begin,pid=os.getpid(),argv=sys.argv,run_id=q['run_id'],deadline_epoch=deadline,max_first_positive_wait_s=1200,
  active_keys=list(KEYS),deferred_experts=['e2'],source_global_counters_are_not_new_progress=True,actual_GO_report_SHA=H(paths[2]),metadata_only=True))
 # All actual-GO/source checks precede transport/credential import.
 T=N.parent;W=T.parent
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
 sp=importlib.util.spec_from_file_location('native88_observer_existing_memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');memory=importlib.util.module_from_spec(sp);sp.loader.exec_module(memory)
 remote=(D/'native88_closing_protocol_v1.py').read_text('utf8')+'\n'+(D/'native88_observer_readonly_remote_v1.py').read_text('utf8')
 secret=memory.recover();c=None;targets={};owner=None
 try:
  c=d.connect72(secret)
  try:owner=d.code(c,d.PY72,remote+'\nprint(__import__("json").dumps(observe_owner_readonly(v)))',dict(q=q,deadline_epoch=deadline),timeout=max(30,int(deadline-time.time())+30))
  except BaseException:owner=dict(status='owner_transport_primary_preserved',observation_error=traceback.format_exc())
  put(R,'NATIVE88_FIRST_OWNER_ACTUAL_GO_AND_IDENTITY_RETURNED_ACTUAL.json',owner);c.close();c=None
  # Both routes are serial, with one global deadline. No first-metadata rearm.
  for key in ('h1','recovery'):
   try:
    c=route.connect() if key=='h1' else d.connect72(secret);py=route.PY if key=='h1' else d.PY72
    v=dict(root=q['roots'][key],spec=q['specs'][key],detached_node=q['nodes'][key],run_id=q['run_id'],go=go[key],row=(((owner.get('current') or {}).get('rows') or {}).get(key) or {}),deadline_epoch=deadline)
    targets[key]=d.code(c,py,remote+'\nprint(__import__("json").dumps(observe_target_readonly(v)))',v,timeout=max(30,int(deadline-time.time())+30))
   except BaseException:targets[key]=dict(key=key,passed=False,status='target_transport_primary_preserved',observation_error=traceback.format_exc(),no_retry=True)
   finally:
    if c:c.close();c=None
   put(R,'NATIVE88_'+key.upper()+'_FIRST_NEW_PI_FINITE_TEXT_RETURNED_ACTUAL.json',targets[key])
  passed=all(targets.get(k,{}).get('passed') is True for k in KEYS) and (owner.get('owner_identity') or {}).get('passed') is True
  result=dict(epoch=time.time(),passed=passed,actual_finite_returned=True,run_id=q['run_id'],owner=owner,targets=targets,actual_GO=go,
   publication_index_ordering_pending_is_not_training_failure=True,restored_positive_counters_not_new_progress=True,
   no_PT_raw_or_checkpoint_hash_read=True,no_signal_retry_or_account_write=True,not_FINAL_or_skill_or_continuous_alive=True)
  put(R,'NATIVE88_FIRST_NEW_POLICY_FINITE_RETURNED_ACTUAL.json',result)
  print(json.dumps(dict(passed=passed,status={k:v.get('status') for k,v in targets.items()})))
 finally:
  secret=None
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:
  if '--stage' in sys.argv:
   R=Path(sys.argv[sys.argv.index('--stage')+1])/'reports'
   if R.is_dir():put(R,'NATIVE88_FIRST_OBSERVER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_retry_or_training_failure_inference=True))
  raise
