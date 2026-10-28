from pathlib import Path
import ast,hashlib,importlib.util,json,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027';R=N/'reports';A=L/'TWO104_FUDAN270_LIGHT_OCCUPANCY_ORIGINAL_OWNER_SOURCE_V1';Q=L/'TWO104_FUDAN270_FIRST_CLOSING_INITIAL_CPU_SOURCE_V2'
def put(name,v):
 with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def mod(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 first=mod('only_original104_reader_definitions',Q/'observe_TWO103_fudan270_first_NEW_native_policy_UNUSED_once.py');old=first.NATIVE
 assert old.count('mod4.native103_to_fudan270.target103.objective_window.v1')==1
 code=old.replace('mod4.native103_to_fudan270.target103.objective_window.v1','mod4.native101_to_fudan270.target103.objective_window.v1')
 code=code.replace('while True:','for _new_existing_metadata_read in range(1):')
 ast.parse(code)
 request=json.loads((A/'reports/TWO104_ACTUAL_CPU_BOUND_SEALED_PUBLIC_REQUEST.json').read_bytes());actual=json.loads((A/'reports/TWO104_ACTUAL_OWNER_AND_TWO_NODES_DETACHED.json').read_bytes());prior=json.loads((Q/'reports/TWO103_ACTUAL_TWO_GO_OR_ORIGINAL_ERROR_OWNER_RETURNED.json').read_bytes());go=prior['go'];assert set(go)==set(request['experts'])=={'h1','h1_seed28'}
 put('TWO104_EXISTING_FIRST_METADATA_SCHEMA_REPAIR_ENTRY_CONSUMED_ACTUAL.json',dict(epoch=time.time(),original_two_readers_false_preserved=True,original_reader_line22_schema_typo=True,correct_schema='mod4.native101_to_fudan270.target103.objective_window.v1',one_existing_metadata_read_per_slot_no_poll=True,no_training_or_model_mutation=True))
 wrapper=mod('104_metadata_only_compressed_transport',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py');transport,previous=wrapper.install();sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sec=mod('104_metadata_existing_authorized_memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');secret=sec.recover();client=None;results={}
 try:
  client=d.connect72(secret);secret=None
  for key in ('h1','h1_seed28'):
   result=d.code(client,d.PY72,code,dict(spec=request['experts'][key],node=request['node_roots'][key],node_identity=actual['identities'][key]['exact_identity'],go=go[key],maxwait=1),timeout=45)
   results[key]=result;put(key+'_TWO104_EXISTING_FIRST_POLICY_SCHEMA_REPAIRED_RETURNED_ACTUAL.json',result);assert result['passed_first_NEW_native_policy']
  put('TWO104_ALL_FIRST_NATIVE_UPDATES_SCHEMA_REPAIRED_RETURNED_ACTUAL.json',dict(epoch=time.time(),actual_finite_returned=True,run_id=request['run_id'],go=go,results=results,normal_closing_gates=dict(earliest_normal900=max(x['nominal_end_epoch'] for x in go.values())-900,latest_save_deadline=max(x['save_deadline'] for x in go.values()),latest_nominal_end=max(x['nominal_end_epoch'] for x in go.values())),no_model_read_or_account_write=True,original_schema_reader_false_retained=True,full_FINAL_cost_and_skill_pending=True))
  print(json.dumps(dict(actual_returned=True,new_policy_updates={k:r['positive']['native88_migration_window']['counters']['new_policy_updates'] for k,r in results.items()},new_WM_updates={k:r['positive']['native88_migration_window']['counters']['new_world_updates'] for k,r in results.items()},GPU_snapshots={k:r['GPU_snapshot'] for k,r in results.items()})))
 finally:
  secret=None
  if client:client.close()
  transport.SESSION=previous
if __name__=='__main__':
 try:main()
 except BaseException:put('TWO104_METADATA_SCHEMA_REPAIR_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_auto_retry_or_GPU_interference=True));raise
