"""Derive source only; no payload, model, asset, SDK, account or GO."""
from pathlib import Path
import ast,hashlib,json,time,traceback
S=Path(__file__).resolve().parent;L=S.parent;T=L.parent
N=T/'H1_STEP270_THREE_GPU_OWN_FUDAN_NATIVE_V87_20261027';P=N/'payloads_r5/h1';C=N/'controllers_r5';R=S/'reports'
def H(raw):return hashlib.sha256(raw).hexdigest()
def put(name,value):
 with (R/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2)
def replace(text,a,b,count=1):
 assert text.count(a)==count,(a,text.count(a));return text.replace(a,b)
def write(name,text):
 ast.parse(text)
 p=S/name
 if p.exists():assert p.read_bytes()==text.encode('utf8'),'partial source must remain byteexact'
 else:
  with p.open('x',encoding='utf8',newline='') as f:f.write(text)
 return dict(path=name,bytes=len(text.encode('utf8')),SHA=H(text.encode('utf8')))
def functions(text):
 return {x.name:ast.dump(x,include_attributes=False) for x in ast.parse(text).body if isinstance(x,(ast.FunctionDef,ast.ClassDef))}
def main():
 R.mkdir(exist_ok=True);put('SOURCE_V2_ENTRY_CONSUMED_BEFORE_DERIVATION_ACTUAL.json',dict(epoch=time.time(),source_only=True))
 rows=[]
 old=(P/'h1_native_own87_worker_v1.py').read_text('utf8')
 worker=replace(old,"choices=('policy_only_fresh_environment',)","choices=('native_models_only_fresh400N_environment',)")
 worker=replace(worker,'from native87_source_guard_v1','from native88_source_guard_v1',2)
 worker=replace(worker,"src=J/'source'/task['source_filename'];assert H(src)==go['bootstrap_SHA'];","src=J/'source'/task['source_filename'];bootstrap=J/'source'/task['bootstrap_source_filename'];assert H(src)==go['source_SHA'] and H(bootstrap)==go['bootstrap_SHA'];")
 worker=replace(worker,"'--init_checkpoint',str(src)","'--init_checkpoint',str(bootstrap)")
 worker=replace(worker,'from native_own_fudan87_training import run','from native_own_fudan88_gas400_training_v2 import run')
 worker=worker.replace('Prepared only: requires a new actual original-owner GO and admitted native source.','SOURCE ONLY: native R5 models + separate frozen normal86 RSL bootstrap; fresh400N physics.')
 rows.append(write('h1_native88_changed_plant_worker_v1.py',worker))
 # The exact original fresh4096 bootstrap function still receives only the
 # original normal86 file; native R5 is passed separately to the native entry.
 assert "checkpoint_API.resume_h1_new_episode=resume_policy_only_fresh4096" in worker
 assert "'--init_checkpoint',str(bootstrap)" in worker and "out,task,go,src,phase)" in worker
 old=(C/'three_slot_common_v1.py').read_text('utf8')
 common=replace(old,"def valid_ready(row,spec):\n","def valid_ready(row,spec):\n if spec.get('native88_changed_plant'):\n  from native88_protocol_v1 import native88_valid_ready\n  return native88_valid_ready(row,spec)\n")
 common=replace(common," if spec.get('native87_policy_only'):args+="," if spec.get('native88_changed_plant'):args+=['--slot',spec['key'],'--phase',phase,'--num-envs','4096','--seed',str(spec['seed']),'--source-scope','native_models_only_fresh400N_environment']\n elif spec.get('native87_policy_only'):args+=")
 common=replace(common,"(32 if spec.get('native87_policy_only') else 8)","(32 if spec.get('native87_policy_only') or spec.get('native88_changed_plant') else 8)")
 before=functions(old);after=functions(common)
 assert {k for k in before if before[k]!=after[k]}=={'valid_ready','spawn'}
 rows.append(write('three_slot_common_v1.py',common))
 old=(C/'three_slot_finite_node_v1.py').read_text('utf8')
 node=replace(old,'from three_real_gpu_resource_v1 import acquire','from native88_resource_guard_v1 import acquire')
 node=replace(node,"  if spec.get('native87_policy_only'):\n","  if spec.get('native88_changed_plant'):\n   from native88_closed_source_CPU_v1 import load\n   closed=load(spec,B);phase='ready'\n  elif spec.get('native87_policy_only'):\n")
 # No modifications to original sends, wait, stop/fullsave, terminal retry or finally bodies.
 n0=next(x for x in ast.parse(old).body if isinstance(x,ast.FunctionDef) and x.name=='node')
 n1=next(x for x in ast.parse(node).body if isinstance(x,ast.FunctionDef) and x.name=='node')
 assert ast.dump(ast.Module(body=next(x for x in n0.body if isinstance(x,ast.Try)).finalbody,type_ignores=[]))==ast.dump(ast.Module(body=next(x for x in n1.body if isinstance(x,ast.Try)).finalbody,type_ignores=[]))
 rows.append(write('three_slot_finite_node_v1.py',node))
 old=(C/'three_slot_finite_owner_NATIVE87_AVAILABLE_TWO_authority72.py').read_text('utf8')
 owner=replace(old,'from native87_available_two_schedule_v1 import validate_schedule','from native88_protocol_v1 import validate_schedule,native88_go_fields')
 marker="actual_H1_step270_scope_admitted=key=='h1');account()"
 owner=replace(owner,marker,"actual_H1_step270_scope_admitted=key=='h1');shared['go'][key].update(native88_go_fields(spec));account()")
 rows.append(write('three_slot_finite_owner_NATIVE88_AVAILABLE_TWO_authority72.py',owner))
 # Original authority module and accounting function are copied byteexact.
 original=(C/'single_writer72_authority_V85M_source.py').read_bytes()
 p=S/'single_writer72_authority_V85M_source.py'
 if p.exists():assert p.read_bytes()==original
 else:
  with p.open('xb') as f:f.write(original)
 rows.append(dict(path='single_writer72_authority_V85M_source.py',bytes=len(original),SHA=H(original),old_bytes_exact=True))
 assert functions((C/'three_slot_common_v1.py').read_text('utf8'))['charge_values']==functions(common)['charge_values']
 old=(C/'native87_closed_source_CPU_v1.py').read_text('utf8')
 loader=old.replace('native87_protocol_v1','native88_protocol_v1').replace('native87_valid_ready','native88_valid_ready')
 loader=loader.replace('mod4.native87.actual_waited_preinstalled_CPU.v1','mod4.native88.actual_waited_preinstalled_CPU.v1')
 loader=loader.replace('NATIVE87_POLICY_ONLY_FRESH4096_SOURCE_SDK_CPU_ACTUAL','NATIVE88_CHANGED_PLANT_SOURCE_SDK_CPU_ACTUAL')
 loader=loader.replace('native87_SOURCE_CPU','native88_SOURCE_CPU').replace('NATIVE87_ACTUAL_PREINSTALLED_SOURCE_CPU_PROOF','NATIVE88_ACTUAL_PREINSTALLED_SOURCE_CPU_PROOF')
 loader=replace(loader,"'--source-scope','policy_only_fresh_environment'","'--source-scope','native_models_only_fresh400N_environment'")
 loader=replace(loader,"assert proof['source_SHA']==spec['source_SHA']==spec['bootstrap_source_SHA']","assert proof['source_SHA']==spec['source_SHA'] and proof['bootstrap_SHA']==spec['bootstrap_source_SHA']")
 loader=replace(loader,"source_SHA=spec['source_SHA'],report_relative=","source_SHA=spec['source_SHA'],bootstrap_SHA=spec['bootstrap_source_SHA'],report_relative=")
 rows.append(write('native88_closed_source_CPU_v1.py',loader))
 # Same exact approved72 wrapper interpreter and fresh Process per identity poll.
 for name in ('expected_exec_identity','wait_exact_exec_identity'):
  assert functions(old)[name]==functions(loader)[name]
 # Use already-proven original parameter reader's Warp/Tensor/Proxy view for raw
 # PhysX getters; keep strict DR tensor helper for the ordinary in-memory data.
 original=(L/'native88_gas400_typed_native_migration_bridge_source_v1/gas400_sdk_admission_candidate_v1.py').read_text('utf8')
 checker=replace(original," from gas400_source_patcher_v1", " from gas400_source_patcher_v1",0) if False else original
 checker=replace(checker," import torch\n"," import torch\n from spring_nominal_sdk_readback import tensor as backend_tensor\n")
 for method in ('get_dof_stiffnesses','get_dof_dampings','get_dof_limits','get_dof_max_forces','get_dof_armatures'):
  checker=replace(checker,"tensor(robot.root_view."+method+"())","backend_tensor(robot.root_view."+method+"())")
 rows.append(write('gas400_sdk_admission_candidate_v2.py',checker))
 put('EXACT_DERIVED_WORKER_CONTROL_AND_CPU_LOADER_SOURCE_ACTUAL.json',dict(epoch=time.time(),source_only=True,files=rows,original_charge_values_AST_exact=True,original72authority_bytes_exact=True,original_node_finally_AST_exact=True,original_wrapper_identity_functions_AST_exact=True,separate_RSL_bootstrap_and_native_fullstate_inputs=True,no_old700N_DR_restore=True,source_R5_formal_models_not_reopened=True,old_global_resource_process_scan_not_used_by_new_node=True,raw_PhysX_getters_use_original_known_Warp_adapter=True,target_source_guard_objective_integration_and_installedSDK_still_pending=True))
 print(json.dumps(dict(source_only=True,derived_files=len(rows),charge_and_node_finally_preserved=True,no_payload_or_GO=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  R.mkdir(exist_ok=True);put('SOURCE_DERIVATION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_remote_model_or_Go=True));raise
