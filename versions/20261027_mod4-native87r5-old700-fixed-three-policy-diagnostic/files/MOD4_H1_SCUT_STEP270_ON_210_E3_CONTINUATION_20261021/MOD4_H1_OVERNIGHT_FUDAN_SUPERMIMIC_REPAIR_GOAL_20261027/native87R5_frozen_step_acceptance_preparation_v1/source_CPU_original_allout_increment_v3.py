"""New original all-node exit/locks metadata boundary; no models or old fixture."""
from pathlib import Path
import copy,json,sys,traceback
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE));out=HERE/'SOURCE_CPU_ORIGINAL_ALLOUT_INCREMENT_V3_ACTUAL.json';assert not out.exists()
from native87R5_frozen_acceptance_contract_v1 import SOURCE_SHA,CANONICAL,select_source
checks=[]
def refuse(name,cpu,col):
 try:select_source(cpu,col,{})
 except ValueError:checks.append(name);return
 raise AssertionError('unexpected accepted '+name)
try:
 models={};rows={};nodes={};loads=[]
 for key,ch in [('h1','a'),('recovery','b')]:
  final=dict(SHA=ch*64,bytes=1,formal_manifest_passed=True,twohost_complete_SHA=True,policy_updates=1,world_updates=1)
  models[key]=dict(passed=True,source_SHA=SOURCE_SHA,frozen_bootstrap=dict(Adam=832460),native_fullstate_finite=True,NATIVE_CONTRACT_strict_type_and_values=True,native_modules=dict(WM_Pi_Critic_strict_CPU_state_load=True),final=final);rows[key]=[final]
  nodes[key]=dict(all_selected_target_processes_actual_out=True,node_exit=dict(actual_all_own_children_waited=True,validation_fcntl_released_if_acquired=True),locks=[dict(actual_fcntl_free=True)],node_terminal=dict(row=dict(terminal_all_own_children_waited=True,original_error=False,errors=[],final=dict(passed=True,final=final))))
  loads.append(dict(role=key+'_native_FINAL',producer_SHA=final['SHA'],completed=True,initial_load_attempted=True))
 cpu=dict(original_fees=dict(passed=True),original_canonical_cost_settled=True,models=models,initial_model_load_records=loads)
 col=dict(actual_finite_transport_returned=True,original_canonical_cost_settled=True,authority72=dict(all_authority72_owner_children_actual_out=True,canonical_active_segment=None,canonical_path=CANONICAL,original_locks=[dict(actual_fcntl_free=True)]*2),nodes=nodes,native_H1_method_fullstate=rows)
 assert select_source(cpu,col,{})['selected_key']=='h1';checks.append('both_original_native_nodes_out_all_original_locks_free')
 bad=copy.deepcopy(col);bad['nodes']['recovery']['all_selected_target_processes_actual_out']=False;refuse('healthy_h1_still_requires_other_original_node_out',cpu,bad)
 bad=copy.deepcopy(col);bad['nodes']['h1']['locks'][0]['actual_fcntl_free']=False;refuse('original_H1_private_lease_not_free_refused',cpu,bad)
 bad=copy.deepcopy(col);bad['original_canonical_cost_settled']=False;refuse('original_collection_cost_false_stays_false',cpu,bad)
 with out.open('x',encoding='utf8') as f:json.dump(dict(passed=True,checks=len(checks),check_names=checks,metadata_only=True,no_runtime_model_policy_GPU_or_account=True),f,indent=2)
 print(json.dumps(dict(passed=True,checks=len(checks),metadata_only=True)))
except BaseException:
 with (HERE/'SOURCE_CPU_ALLOUT_V3_ORIGINAL_ERROR.json').open('x',encoding='utf8') as f:json.dump(dict(passed=False,error=traceback.format_exc(),checks=checks),f,indent=2)
 raise
