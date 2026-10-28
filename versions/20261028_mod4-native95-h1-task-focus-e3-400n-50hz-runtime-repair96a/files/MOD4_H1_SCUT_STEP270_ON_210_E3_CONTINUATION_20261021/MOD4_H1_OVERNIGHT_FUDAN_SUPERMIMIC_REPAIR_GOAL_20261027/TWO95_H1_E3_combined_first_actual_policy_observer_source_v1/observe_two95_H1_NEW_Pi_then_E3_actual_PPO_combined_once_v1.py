"""One serial bounded metadata reader. Does not control any healthy slot."""
from pathlib import Path
import importlib.util,json,sys,threading,time,traceback
from OWNER_read_only_CODE_v1 import OWNER
from NATIVE_read_only_CODE_v1 import NATIVE
from E3_read_only_CODE_v1 import E3
B=Path(__file__).resolve().parent;L=B.parent;T=L.parent;W=T.parent;R=B/'reports'
ACT=L/'THREE95_H1_E3_mixed72_source_v1/reports'
def put(name,value):
 with (R/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2,allow_nan=False)
def main():
 request=json.loads((ACT/'TWO95_ACTUAL_CPU_BOUND_SEALED_PUBLIC_REQUEST.json').read_bytes())
 actual=json.loads((ACT/'TWO95_ACTUAL_OWNER_AND_TWO_NODES_DETACHED.json').read_bytes())
 assert actual['run_id']==request['run_id'] and set(request['experts'])=={'h1','e3'}
 put('TWO95_COMBINED_FIRST_OBSERVER_CONSUMED_ACTUAL.json',dict(epoch=time.time(),one_combined_first_reader=True,run_id=request['run_id']))
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sp=importlib.util.spec_from_file_location('two95_first_existing_authorized_memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');sec=importlib.util.module_from_spec(sp);sp.loader.exec_module(sec)
 sp=importlib.util.spec_from_file_location('two95_first_same_compressed_transport_install_only',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);transport,previous=m.install()
 secret=sec.recover();client=None;stop=threading.Event();phase=['owner_signed_GO'];started=time.time();results={}
 def progress():
  while not stop.wait(25):print(json.dumps(dict(stage='SAME_COMBINED_FIRST_FINITE',phase=phase[0],epoch=time.time())),flush=True)
 thread=threading.Thread(target=progress,daemon=True);thread.start()
 try:
  client=d.connect72(secret)
  go=d.code(client,d.PY72,OWNER,dict(owner=request['owner_root'],identity=actual['identities']['owner']['exact_identity'],run_id=request['run_id']),timeout=150)
  put('TWO95_ACTUAL_TWO_GO_OWNER_METADATA_RETURNED.json',go)
  phase[0]='h1_first_NEW_native_Pi'
  remaining=max(1,min(780,int(1200-(time.time()-started)-30)))
  try:
   results['h1']=d.code(client,d.PY72,NATIVE,dict(spec=request['experts']['h1'],node=request['node_roots']['h1'],node_identity=actual['identities']['h1']['exact_identity'],go=go['go'].get('h1'),maxwait=remaining),timeout=remaining+20)
  except BaseException:results['h1']=dict(passed_first_NEW_native_policy=False,original_observer_error=traceback.format_exc(),other_healthy_slot_untouched=True)
  put('H1_TWO95_FIRST_NEW_NATIVE_POLICY_RETURNED_ACTUAL.json',results['h1'])
  print(json.dumps(dict(stage='H1_FIRST_RETURNED',passed=results['h1'].get('passed_first_NEW_native_policy'))),flush=True)
  phase[0]='e3_first_actual_CUDA_fullrestore_native24_PPO'
  remaining=max(1,min(780,int(1200-(time.time()-started)-30)))
  try:
   results['e3']=d.code(client,d.PY72,E3,dict(request=dict(owner_root=request['owner_root'],node_root=request['node_roots']['e3'],run_id=request['run_id']),actual=dict(owner=actual['identities']['owner']['exact_identity'],node=actual['identities']['e3']['exact_identity']),maxwait=remaining),timeout=remaining+20)
  except BaseException:results['e3']=dict(passed_first_E3_real_PPO=False,original_observer_error=traceback.format_exc(),other_healthy_slot_untouched=True)
  put('E3_TWO95_FIRST_ACTUAL_CUDA_NATIVE24_PPO_RETURNED_ACTUAL.json',results['e3'])
  signed=go['go'];gates=dict(earliest_normal900=max(x['nominal_end_epoch'] for x in signed.values())-900,latest_save_deadline=max(x['save_deadline'] for x in signed.values()),latest_nominal_end=max(x['nominal_end_epoch'] for x in signed.values())) if signed else None
  value=dict(actual_finite_returned=True,run_id=request['run_id'],go=signed,results=results,normal_closing_gates=gates,original_fee_and_formals_still_pending=True,no_model_GPU_launch_or_account_write=True,skill_and_complete_WM_data_not_claimed=True)
  put('TWO95_ALL_FIRST_POLICY_OR_ORIGINAL_ERROR_RETURNED_ACTUAL.json',value)
  print(json.dumps(dict(actual_returned=True,H1_first_NEW_Pi=results['h1'].get('passed_first_NEW_native_policy'),E3_first_actual_PPO=results['e3'].get('passed_first_E3_real_PPO'),normal_closing_gates=gates)),flush=True)
 finally:
  secret=None;stop.set();thread.join(1)
  if client:client.close()
  transport.SESSION=previous
if __name__=='__main__':
 try:main()
 except BaseException:put('TWO95_COMBINED_FIRST_OBSERVER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_repeat_first_metadata_or_slot_interference=True));raise
