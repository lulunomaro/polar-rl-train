"""New unused source integration. No model decode, remote, GPU or Task/GO."""
from pathlib import Path
import ast,hashlib,json,shutil,time,traceback
L=Path(__file__).resolve().parent;T=L.parent
P=L/'native88_two_available_H1_runtime_protocol_source_v1';I=L/'native88_selected_runtime_integration_source_v1';Q=L/'native88_installed_source_CPU_candidate_v2_JSON_schema_only'
C=L/'native88C_two_available_H1_runtime_protocol_source_v1';IC=L/'native88C_selected_runtime_integration_source_v1';QC=L/'native88C_installed_source_CPU_candidate_v1'
D=L/'native88_gas400_reset_bank_exact_compatibility_source_v1';OLD=T/'H1_STEP270_OWN_STEP_GAS400_NATIVE_RESOURCE_V88B_20261027'
FAIL=OLD/'reports/NATIVE88B_ACTUAL_EARLY_RESET_FAILURE_ORIGINAL_COST_ALLOUT_QUALIFIED_FOR_NEXT_PREPARATION.json'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def copy(src,dst):dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
def edit(p,a,b,n=1):
 s=p.read_text('utf8');assert s.count(a)==n,(str(p),a,s.count(a));s=s.replace(a,b);ast.parse(s);p.write_bytes(s.encode())
def main():
 for root in (C,IC,QC):assert not root.exists();root.mkdir()
 put(C/'reports/SOURCE_DERIVATION_CONSUMED_BEFORE_WRITE_ACTUAL.json',dict(epoch=time.time(),no_payload_Task_GO_remote_or_models=True))
 f=json.loads(FAIL.read_bytes());assert f['passed_original_cost_allout_only'] and f['closing_remaining']==569391.7559990883 and f['both_failed_before_first_control_and_NEW_Pi'] and not f['formal_FINALs']
 assert H(D/'INDEX_SHA256_ACTUAL.json')=='24c84db75dbfab22eaad9de9497e639c3c2216aa1e080fd90da95361cb2f9a9e'
 for name in ['native88_protocol_v1.py','native88_resource_guard_v1.py','native88_closed_source_CPU_v1.py','native88_frozen_RSL_bootstrap_v1.py','h1_native88_changed_plant_worker_v1.py','three_slot_common_v1.py','three_slot_finite_node_v1.py','three_slot_finite_owner_NATIVE88_AVAILABLE_TWO_authority72.py','single_writer72_authority_V85M_source.py','native88_install_activate_support_v1.py']:copy(P/name,C/name)
 for p in I.rglob('*.py'):
  if p.name.startswith('integrate_'):continue
  copy(p,IC/p.relative_to(I))
 for name in ('native88_source_guard_v1.py','target_native88_source_sdk_cpu_v1.py','native88_installed_cpu_helpers_v1.py'):copy(Q/name,QC/name)
 # New current RESOURCE failure, unchanged qualified R5 MODEL source.
 for p in (C/'native88_protocol_v1.py',C/'native88_install_activate_support_v1.py'):
  s=p.read_text();assert '569553.363275528' in s;s=s.replace('569553.363275528','569391.7559990883');ast.parse(s);p.write_bytes(s.encode())
 p=C/'native88_protocol_v1.py'
 s=p.read_text();assert s.count("'objective_contract_SHA')")==3
 s=s.replace("'objective_contract_SHA')","'objective_contract_SHA','previous_failed88B_cost_allout_SHA','reset_bank_source_qualification_SHA')")
 anchor="'actual_fresh_GPU_before_first_control_still_required')";assert s.count(anchor)==1;s=s.replace(anchor,"'exact_gas400_reset_bank_source_CPU_passed',"+anchor)
 s=s.replace("return True\n\ndef validate_schedule", "require(isinstance(s.get('previous_failed_runtime_root'),str) and 'own_step_gas400_native_2610v88b/' in s['previous_failed_runtime_root'],'exact latest failed resource root required')\n return True\n\ndef validate_schedule",1)
 ast.parse(s);p.write_bytes(s.encode())
 # Actual source-bank check occurs before any new model CPU decode.
 p=QC/'target_native88_source_sdk_cpu_v1.py'
 edit(p,"    # This file is an unused actual target entry.","    from gas400_reset_bank_exact_compatibility_v1 import check_runtime_source\n    bank=check_runtime_source(J/'runtime/isaac/mod4')\n    require(bank['passed'] is True and bank['source_only'] is True and bank['actual_SDK_scene_reset_or_PhysX_validated'] is False,'exact actual installed resetbank source proof')\n    # This file is an unused actual target entry.")
 edit(p,"        actual_fresh_GPU_before_first_control_still_required=not torch.cuda.is_initialized())","        exact_gas400_reset_bank_source_CPU_passed=bank['passed'],\n        actual_fresh_GPU_before_first_control_still_required=not torch.cuda.is_initialized())")
 edit(p,"asset_CPU_readback=asset,new_objective_source_CPU=objective","asset_CPU_readback=asset,reset_bank_exact_compatibility_source_CPU=bank,new_objective_source_CPU=objective")
 # Require actual completed original reset, not the source-only flag.
 p=QC/'native88_source_guard_v1.py'
 edit(p,"'own_step_objective_qualification','known_own_processes'):","'own_step_objective_qualification','known_own_processes','previous_failed88B_cost_allout','reset_bank_source_qualification'):")
 edit(p,"    validate_saved_source_evidence(c,task,docs)\n","    validate_saved_source_evidence(c,task,docs)\n    validate_failed_resource_and_reset_source(c,task,docs)\n")
 edit(p,"    audit=env._mild_dr.audit();", "    from gas400_reset_bank_exact_compatibility_v1 import check_runtime_source\n    bank=check_runtime_source(Path(B)/'job0/runtime/isaac/mod4')\n    cache=getattr(env,'_rescue_reset_bank',None);resetq=getattr(env,'_rescue_reset_q',None)\n    require(isinstance(cache,tuple) and len(cache)==2 and tuple(cache[0].shape)==(74,30) and tuple(cache[1].shape)==(74,) and resetq is not None and tuple(resetq.shape)==(4096,30),'actual first original reset cache and writes required')\n    audit=env._mild_dr.audit();")
 edit(p,"return dict(passed=True,actual_environment_count=4096,actual_runtime30joint_order_passed=True,","return dict(passed=True,actual_environment_count=4096,original_first_reset_completed=True,reset_bank_exact_compatibility_source_CPU=bank,actual_runtime30joint_order_passed=True,")
 with p.open('ab') as out:out.write(b'''\n\ndef validate_failed_resource_and_reset_source(c,task,docs):
    failed=docs['previous_failed88B_cost_allout'];q=docs['reset_bank_source_qualification']
    require(failed['passed_original_cost_allout_only'] is True and failed['both_failed_before_first_control_and_NEW_Pi'] is True and failed['formal_FINALs'] is False and failed['source_models_remain_qualified_R5'] is True,'failed88B is resource/cost only, never model source')
    require(failed['run_id']=='AVAILABLE_TWO_H1_GAS400_OWN_STEP_NATIVE88B_1793079421832793100' and failed['original_owner']['pid']==523069 and failed['original_owner']['creation']==1793079430.42,'exact latest original failed owner')
    require(failed['fee_sumonce']==161.60727643966675 and failed['closing_remaining']==569391.7559990883 and failed['actual_nodes_owner_workers_out'] and failed['canonical_None'] and failed['original_locks_free'] and failed['original_normal_duration_flags_unchanged'],'original failed fee/allout and latest balance')
    require(q['passed'] is True and q['count']==17 and q['no_model_PT_USD_raw_actor_or_physics_read_or_run'] is True,'exact17 source-only resetbank CPU proof')
    for name in ('previous_failed88B_cost_allout','reset_bank_source_qualification'):require(task[name+'_SHA']==c[name+'_SHA'],'Task new resource/reset pin '+name)
    return True
''')
 ast.parse(p.read_bytes())
 p=C/'h1_native88_changed_plant_worker_v1.py'
 edit(p,"  put(out/'NATIVE87_ACTUAL_BEFORE_FIRST_CONTROL_ADMISSION.json',validate_precontrol_actual(runner,created[0],task,go,B))","  admission=validate_precontrol_actual(runner,created[0],task,go,B)\n  created[0]._native88_actual_precontrol=admission\n  put(out/'NATIVE87_ACTUAL_BEFORE_FIRST_CONTROL_ADMISSION.json',admission)")
 p=IC/'native_own_fudan88_gas400_training_v2.py'
 edit(p,"    objective=mdp.contract_manifest()","    precontrol=getattr(env,'_native88_actual_precontrol',None)\n    if not isinstance(precontrol,dict) or precontrol.get('original_first_reset_completed') is not True:raise ValueError('actual original first reset completion receipt required')\n    objective=mdp.contract_manifest()")
 edit(p,"        actual_GPU_runtime_readback_passed=True,before_first_native_physical_control_and_Pi=True,","        actual_GPU_runtime_readback_passed=True,before_first_native_physical_control_and_Pi=True,\n        original_first_reset_completed=precontrol['original_first_reset_completed'],\n        reset_bank_exact_compatibility_source_CPU=precontrol['reset_bank_exact_compatibility_source_CPU'],")
 # Additional latest failed runtime closure is checked by the fresh resource guard.
 failure_check=""" previous=Path(spec['previous_failed_runtime_root']).resolve();require(previous.is_relative_to(owned.resolve()) and previous!=source,'failed88B resource root separate from qualified R5 source')
 failedreport=B/contract['previous_failed88B_cost_allout_relative'];require(H(failedreport)==contract['previous_failed88B_cost_allout_SHA']==spec['previous_failed88B_cost_allout_SHA'],'exact failed resource cost proof')
 proof=json.loads(failedreport.read_bytes());require(proof['passed_original_cost_allout_only'] and proof['canonical_None'] and proof['closing_remaining']==569391.7559990883,'failed resource original cost/allout')
 fe=json.loads((previous/'NODE_EXIT_ACTUAL.json').read_bytes());ft=json.loads((previous/'NODE_TERMINAL_ACTUAL.json').read_bytes())['row'];error=json.loads((previous/'job0/production/ORIGINAL_ERROR_BEFORE_APP_CLOSE.json').read_bytes())['error']
 require(fe['actual_all_own_children_waited'] and fe['validation_fcntl_released_if_acquired'] and ft['terminal_all_own_children_waited'] and ft['original_error'] and ft['final'] is None and 'reset-bank contract hash mismatch' in error,'exact previous failed88B terminal, never passed model')
 require(not (previous/'job0/production/FIRST_NATIVE_SUPERMIMIC_POLICY_UPDATE_POSITIVE_ACTUAL.json').exists(),'previous failed resource must not conceal native training')
"""
 p=C/'native88_resource_guard_v1.py';edit(p," rowpath=B/contract['known_own_processes_relative'];",failure_check+" rowpath=B/contract['known_own_processes_relative'];")
 p=C/'native88_install_activate_support_v1.py'
 marker="assert s['private_lock']==v['original_R5_private_lock']"
 addition="""previous=Path(s['previous_failed_runtime_root']);assert previous.resolve().is_relative_to(owned.resolve()) and previous!=old
failed=v['current_failed_cost_allout'];assert failed['passed_original_cost_allout_only'] and failed['closing_remaining']==569391.7559990883 and failed['canonical_None'] and failed['actual_nodes_owner_workers_out']
fe=json.loads((previous/'NODE_EXIT_ACTUAL.json').read_bytes());ft=json.loads((previous/'NODE_TERMINAL_ACTUAL.json').read_bytes())['row'];primary=json.loads((previous/'job0/production/ORIGINAL_ERROR_BEFORE_APP_CLOSE.json').read_bytes())['error']
assert fe['actual_all_own_children_waited'] and ft['terminal_all_own_children_waited'] and ft['original_error'] and ft['final'] is None and 'reset-bank contract hash mismatch' in primary
"""
 edit(p,marker,addition+marker)
 # Adapt the already successful local binding pipeline; actual SDK remains pending.
 s=(P/'prepare_native88B_exact_two_payloads_JSON_schema_fixed_unused_once.py').read_text()
 s=s.replace('H1_STEP270_OWN_STEP_GAS400_NATIVE_RESOURCE_V88B_20261027','H1_STEP270_OWN_STEP_GAS400_NATIVE_RESOURCE_V88C_20261027').replace('native88_installed_source_CPU_candidate_v2_JSON_schema_only','native88C_installed_source_CPU_candidate_v1').replace('native88_selected_runtime_integration_source_v1','native88C_selected_runtime_integration_source_v1').replace('own_step_gas400_native_2610v88b/','own_step_gas400_native_2610v88c/')
 # Source original closed R5 is still569553; only new resource launch snapshot changes.
 s=s.replace("last_closed_remaining_snapshot=569553.363275528","last_closed_remaining_snapshot=569391.7559990883")
 anchor="  cp(geom,B/'source/OWN_STEP_WHEEL_GEOMETRY_FROM_R2_SOURCE.json')"
 assert s.count(anchor)==1
 inject="""  bankdir=L/'native88_gas400_reset_bank_exact_compatibility_source_v1'
  for rel,name in [('job0/runtime/isaac/mod4/scut_flat_rescue.py','candidate_runtime_NOT_A_PAYLOAD/scut_flat_rescue.py'),('job0/runtime/reports/SOURCE_FREEZE.json','candidate_SOURCE_FREEZE.json'),('job0/runtime/isaac/mod4/gas400_reset_bank_exact_compatibility_v1.py','candidate_runtime_NOT_A_PAYLOAD/gas400_reset_bank_exact_compatibility_v1.py'),('job0/runtime/isaac/mod4/RESET_BANK_700N_ORIGINAL_IMPORT_CONTRACT_EXACT.json','candidate_runtime_NOT_A_PAYLOAD/RESET_BANK_700N_ORIGINAL_IMPORT_CONTRACT_EXACT.json')]:
   cp(bankdir/name,B/rel);changed_reasons[rel]='exact approved four-gas-scalar resetbank compatibility, original poses/reset/RNG unchanged'
"""
 s=s.replace(anchor,inject+anchor,1)
 anchor="'own_step_objective_qualification':qualification}"
 assert s.count(anchor)==1
 s=s.replace(anchor,"'own_step_objective_qualification':qualification,'reset_bank_source_qualification':bankdir/'RESET_BANK_EXACT_COMPATIBILITY_SOURCE_CPU_ACTUAL.json','previous_failed88B_cost_allout':T/'H1_STEP270_OWN_STEP_GAS400_NATIVE_RESOURCE_V88B_20261027/reports/NATIVE88B_ACTUAL_EARLY_RESET_FAILURE_ORIGINAL_COST_ALLOUT_QUALIFIED_FOR_NEXT_PREPARATION.json'}",1)
 anchor="  put(B/'native88_source_evidence/known_own_processes.json',known)";assert s.count(anchor)==1
 s=s.replace(anchor,"""  failed_obs=read(T/'H1_STEP270_OWN_STEP_GAS400_NATIVE_RESOURCE_V88B_20261027/reports/NATIVE88_FIRST_NEW_POLICY_FINITE_RETURNED_ACTUAL.json')
  known_current=json.loads(json.dumps(known));known_current['rows'].append(dict(role='failed88B_owner',execution_backend='target72',pid=523069,creation=1793079430.42))
  for failedkey,failedtarget in failed_obs['targets'].items():
   for label in ('node_identity','worker_identity'):
    r=failedtarget[label]['recorded'];known_current['rows'].append(dict(role='failed88B_'+failedkey+'_'+label,execution_backend='source210' if failedkey=='h1' else 'target72',pid=r['pid'],creation=r['creation']))
  put(B/'native88_source_evidence/known_own_processes.json',known_current)""",1)
 anchor="  put(B/'NATIVE88_SOURCE_CONTRACT_ACTUAL.json',c);";assert s.count(anchor)==1
 s=s.replace(anchor,"  task.update(previous_failed88B_cost_allout_SHA=c['previous_failed88B_cost_allout_SHA'],reset_bank_source_qualification_SHA=c['reset_bank_source_qualification_SHA'])\n"+anchor,1)
 anchor="'own_step_objective_qualification_SHA','objective_contract_SHA'):spec[k]=task[k]";assert s.count(anchor)==1
 s=s.replace(anchor,"'own_step_objective_qualification_SHA','objective_contract_SHA','previous_failed88B_cost_allout_SHA','reset_bank_source_qualification_SHA'):spec[k]=task[k]\n  spec['previous_failed_runtime_root']=read(T/'H1_STEP270_OWN_STEP_GAS400_NATIVE_RESOURCE_V88B_20261027/reports/NATIVE88B_ACTUAL_OWNER_NODES_DETACHED.json')['roots'][key]",1)
 ast.parse(s);copy(P/'prepare_native88B_exact_two_payloads_JSON_schema_fixed_unused_once.py',C/'ORIGINAL_88B_BINDER.source_bytes.txt')
 with (C/'prepare_native88C_exact_reset_two_payloads_unused_once.py').open('xb') as out:out.write(s.encode())
 # Preserve source-level protected lifecycle/fee functions; parse every new file.
 rows=[]
 for root in (C,IC,QC):
  for p in root.rglob('*.py'):ast.parse(p.read_bytes());rows.append(dict(path=str(p),bytes=p.stat().st_size,SHA=H(p)))
 put(C/'reports/SOURCE_ONLY88C_EXACT_BANK_AND_FAILED_RESOURCE_DERIVATION_ACTUAL.json',dict(epoch=time.time(),passed_source_AST=True,files=rows,qualified_R5_native_source_unchanged=True,failed88B_resource_and_cost_separate=True,actual_GPU_reset_or_training=False,no_payload_Task_GO=True,latest_balance=569391.7559990883))
 print(json.dumps(dict(source_only=True,source_files=len(rows),new88C_payload_not_built=True)))
if __name__=='__main__':
 try:main()
 except BaseException:put(C/'reports'/('SOURCE_DERIVATION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(original_error=traceback.format_exc(),no_remote_or_payload_or_GO=True));raise
