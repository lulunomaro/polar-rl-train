"""One combined finite: exact root H1 reader once, independent W35 reader next."""
from pathlib import Path
import sys,json,os,time,threading,traceback,importlib.util
HERE=Path(__file__).resolve().parent;W=HERE.parents[2];T=HERE.parents[1];R=HERE/'reports'
N=T/'MOD4_H1_FLAT05_MASK_AWARE_MIXED72_RESOURCE_V91_20261027'
W35_CODE=r"""import sys,json
from pathlib import Path
r=v['request'];sys.path.insert(0,r['owner_root'])
from W35_first_real_GPU_PPO_metadata_observer_v2 import watch
value=watch(r,max_wait_seconds=v['maxwait'])
value['actual_cohort_GO']=(json.loads((Path(r['owner_root'])/'OWNER_CURRENT.json').read_bytes()).get('go') or {})
print(json.dumps(value))
"""
def save(path,value):
 with Path(path).open('x',encoding='utf8') as f:json.dump(value,f,ensure_ascii=False,indent=2)
def main():
 assert len(sys.argv)==1
 marker=N/'reports/NATIVE91_FIRST_NATIVE_POLICY_OBSERVER_CONSUMED_ONCE_BY_COMBINED_V2.json'
 save(marker,dict(epoch=time.time(),own_pid=os.getpid(),exact_reader='native91_first_native_policy_remote_reader_source.py',read_once=True,no_model_or_GPU_or_account_write=True))
 request=json.loads((HERE/'ACTUAL_MIXED72_PUBLIC_REQUEST_POSIX_SEALED_V3.json').read_bytes());watch=json.loads((HERE/'ACTUAL_MIXED72_OBSERVER_REQUEST_POSIX_SEALED_V3.json').read_bytes())
 actual=json.loads((R/'MIXED72_ONE_OWNER_TWO_NODES_LAUNCHED_ACTUAL_V4.json').read_bytes())
 spec=importlib.util.spec_from_file_location('root_exact_native91_readonly_source',N/'native91_first_native_policy_remote_reader_source.py');root=importlib.util.module_from_spec(spec);spec.loader.exec_module(root)
 save(R/'COMBINED_FIRST_OBSERVER_ENTERED_ACTUAL_V2.json',dict(epoch=time.time(),own_pid=os.getpid(),script=str(Path(__file__).resolve()),one_exact_H1_reader_then_independent_W35_reader=True))
 phase=['connect'];stop=threading.Event()
 def heartbeat():
  while not stop.wait(25):
   row=dict(stage='SAME_FINITE_HANDLE_PROGRESS_ONLY',phase=phase[0],epoch=time.time(),no_second_remote_watcher=True)
   with (R/'COMBINED_FIRST_OBSERVER_LOCAL_PROGRESS_ONLY_ACTUAL_V2.jsonl').open('a',encoding='utf8') as f:f.write(json.dumps(row)+chr(10))
   print(json.dumps(row),flush=True)
 thread=threading.Thread(target=heartbeat,daemon=True);thread.start()
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sp=importlib.util.spec_from_file_location('same_authorized_memory_combined_first_v2',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');sec=importlib.util.module_from_spec(sp);sp.loader.exec_module(sec)
 secret=sec.recover();c=None;started=time.time();h1=None;w35=None
 try:
  c=d.connect72(secret);secret=None;phase[0]='exact_H1_first_CODE_once'
  try:
   h1=d.code(c,d.PY72,root.CODE,dict(actual={'owner':actual['owner'],'node':actual['nodes']['h1']},owner=request['owner_root'],node=request['h1_node_root'],job=request['h1_spec']['job_root'],run_id=request['run_id']),timeout=960)
  except BaseException:h1=dict(passed_first_native_flat_policy=False,original_observer_error=traceback.format_exc(),healthy_W35_must_continue_unchanged=True)
  save(N/'reports/NATIVE91_FIRST_ACTUAL_NATIVE_POLICY_RETURNED_ACTUAL.json',h1);save(R/'H1_FIRST_EXACT_READER_RETURNED_ACTUAL_V2.json',h1)
  print(json.dumps(dict(stage='H1_EXACT_FIRST_READER_RETURNED',passed=h1.get('passed_first_native_flat_policy'))),flush=True)
  phase[0]='independent_W35_first_real_PPO_metadata'
  remaining=max(1,min(780,int(960-(time.time()-started)-20)))
  try:w35=d.code(c,d.PY72,W35_CODE,dict(request=watch,maxwait=remaining),timeout=remaining+15)
  except BaseException:w35=dict(first_positive_PPO_observed=False,original_observer_error=traceback.format_exc(),healthy_slots_unchanged_no_retry=True)
  save(R/'W35_FIRST_REAL_PPO_RETURNED_ACTUAL_COMBINED_V2.json',w35)
  go=w35.get('actual_cohort_GO') or ((h1.get('owner_current') or {}).get('go')) or {}
  gates={k:g['learning_started_epoch']+900 for k,g in go.items()}
  result=dict(actual_finite_returned=True,epoch=time.time(),run_id=request['run_id'],H1_first=h1,W35_first=w35,actual_GO=go,normal900_closing_gate_by_slot=gates,normal_combined_earliest=max(gates.values()) if gates else None,source_model_normalizer_GPU_and_account_untouched=True)
  save(R/'COMBINED_TWO_SLOT_FIRST_OBSERVER_RETURNED_ACTUAL_V2.json',result)
  print(json.dumps(dict(stage='COMBINED_FIRST_OBSERVER_RETURNED',actual_finite_returned=True,H1_first=h1.get('passed_first_native_flat_policy'),W35_first=w35.get('first_positive_PPO_observed'),normal900_closing_gates=gates)),flush=True)
 finally:
  secret=None;stop.set();thread.join(timeout=1)
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:save(R/'COMBINED_FIRST_OBSERVER_LOCAL_ORIGINAL_ERROR_ACTUAL_V2.json',dict(epoch=time.time(),error=traceback.format_exc(),no_automatic_retry_or_other_watcher=True));raise
