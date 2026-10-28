from pathlib import Path
import ast,json,hashlib,time
T=Path(__file__).resolve().parent;L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
B=L/'TWO99_TWO_NATIVE_FIRST_POLICY_OBSERVER_SOURCE_V1';B.mkdir();(B/'reports').mkdir()
old=(L/'TWO97_H1_E3_COMBINED_FIRST_INLINE_SOURCE_V1/observe_two97_two_policies_inline_and_original_owner_out_once_v1.py').read_text()
tree=ast.parse(old)
values={x.targets[0].id:ast.literal_eval(x.value) for x in tree.body if isinstance(x,ast.Assign) and isinstance(x.targets[0],ast.Name) and x.targets[0].id in ('OWNER','NATIVE')}
owner=values['OWNER'].replace("{'h1','e3'}","{'h1','restart'}")
native=values['NATIVE']
native=native.replace("positive['world_updates']>106920 and positive['policy_updates']>10372","positive['world_updates']>spec['source_progress']['world_updates'] and positive['policy_updates']>spec['source_progress']['policy_updates']")
native=native.replace("win['schema']=='mod4.native93_to_flat05_focused95.objective_window.v1'","win['schema']=='mod4.native99.stance_'+spec['input_start_mode']+'.objective_window.v1'")
needle="assert positive['producer']['task_focused_real_replay']==spec['task_focused_real_replay'] and positive['producer']['native_learning_seed']==27"
assert native.count(needle)==1
native=native.replace(needle,needle+"\n  assert go['input_start_mode']==positive['producer']['input_start_mode']==spec['input_start_mode'] and go['stance_reference_revision']==positive['producer']['stance_reference_revision']==spec['stance_reference_revision']\n  assert win['reference_SHA']==spec['native_reference_SHA']")
body='''from pathlib import Path
import importlib.util,json,sys,time,traceback,threading
B=Path(__file__).resolve().parent;L=B.parent;T=L.parent;W=T.parent;R=B/'reports'
ACT=L/'TWO99_GENUINE_NATIVE_START_COMPARISON_OWNER_SOURCE_V1/reports'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def main():
 request=json.loads((ACT/'TWO99_ACTUAL_CPU_BOUND_SEALED_PUBLIC_REQUEST.json').read_bytes());actual=json.loads((ACT/'TWO99_ACTUAL_OWNER_AND_TWO_NODES_DETACHED.json').read_bytes())
 assert request['run_id']==actual['run_id'] and set(request['experts'])=={'h1','restart'}
 put('TWO99_COMBINED_FIRST_OBSERVER_CONSUMED_ACTUAL.json',dict(epoch=time.time(),run_id=request['run_id']))
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sp=importlib.util.spec_from_file_location('authorized99_memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');sec=importlib.util.module_from_spec(sp);sp.loader.exec_module(sec)
 sp=importlib.util.spec_from_file_location('compressed99_definitions',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);transport,previous=m.install()
 secret=sec.recover();client=None;stop=threading.Event();phase=['owner'];started=time.time();results={}
 def progress():
  while not stop.wait(25):print(json.dumps(dict(stage='TWO99_SAME_FIRST_FINITE',phase=phase[0],epoch=time.time())),flush=True)
 thread=threading.Thread(target=progress,daemon=True);thread.start()
 try:
  client=d.connect72(secret);go=d.code(client,d.PY72,OWNER,dict(owner=request['owner_root'],identity=actual['identities']['owner']['exact_identity'],run_id=request['run_id']),timeout=150)
  put('TWO99_ACTUAL_TWO_GO_OR_ORIGINAL_ERROR_OWNER_RETURNED.json',go)
  for key in ('h1','restart'):
   phase[0]=key;remaining=max(1,min(780,int(1200-(time.time()-started)-30)))
   try:results[key]=d.code(client,d.PY72,NATIVE,dict(spec=request['experts'][key],node=request['node_roots'][key],node_identity=actual['identities'][key]['exact_identity'],go=go['go'].get(key),maxwait=remaining),timeout=remaining+20)
   except BaseException:results[key]=dict(passed_first_NEW_native_policy=False,original_observer_error=traceback.format_exc(),other_healthy_slot_untouched=True)
   put(key+'_TWO99_FIRST_NEW_NATIVE_POLICY_OR_ORIGINAL_ERROR_RETURNED_ACTUAL.json',results[key]);print(json.dumps(dict(stage=key+'_RETURNED',passed=results[key].get('passed_first_NEW_native_policy'))),flush=True)
  signed=go['go'];gates=dict(earliest_normal900=max(x['nominal_end_epoch'] for x in signed.values())-900,latest_save_deadline=max(x['save_deadline'] for x in signed.values()),latest_nominal_end=max(x['nominal_end_epoch'] for x in signed.values())) if signed else None
  put('TWO99_ALL_FIRST_POLICY_OR_ORIGINAL_ERROR_RETURNED_ACTUAL.json',dict(actual_finite_returned=True,run_id=request['run_id'],go=signed,results=results,normal_closing_gates=gates,formals_and_original_cost_pending=True,not_skill_or_causal_proof=True))
  print(json.dumps(dict(actual_returned=True,results={k:v.get('passed_first_NEW_native_policy') for k,v in results.items()},normal_closing_gates=gates)),flush=True)
 finally:
  secret=None;stop.set();thread.join(1)
  if client:client.close()
  transport.SESSION=previous
if __name__=='__main__':
 try:main()
 except BaseException:put('TWO99_FIRST_OBSERVER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_retry_or_slot_interference=True));raise
'''
source='OWNER='+repr(owner)+'\nNATIVE='+repr(native)+'\n'+body
ast.parse(source);ast.parse(owner);ast.parse(native)
entry=B/'observe_two99_two_native_first_policy_metadata_once_v1.py';entry.write_text(source,encoding='utf8')
(B/'FROZEN_TWO99_FIRST_METADATA_SOURCE_INDEX_V1.json').write_text(json.dumps(dict(entry=entry.name,bytes=entry.stat().st_size,SHA=hashlib.sha256(entry.read_bytes()).hexdigest(),original_owner_same_except_registered_keys=True,native_both_types_explicit=True,unused=True),indent=2),encoding='utf8')
print(json.dumps(dict(prepared=True,entry=str(entry))))
