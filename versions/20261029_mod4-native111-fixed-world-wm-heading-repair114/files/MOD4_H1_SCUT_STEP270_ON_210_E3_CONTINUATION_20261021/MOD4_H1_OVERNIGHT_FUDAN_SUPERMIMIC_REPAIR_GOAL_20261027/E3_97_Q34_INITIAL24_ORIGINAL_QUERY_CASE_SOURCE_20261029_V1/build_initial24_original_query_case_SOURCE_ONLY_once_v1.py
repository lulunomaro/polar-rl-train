"""LOCAL text-only assembly. Never opens/stats model, NPZ, USD or saved raw."""
from pathlib import Path
import ast,hashlib,json,traceback,time
B=Path(__file__).resolve().parent;L=B.parent
OLD=L/'E3_97_SOURCE210_ENTRY_RECEIPT_CLI_CLOSURE_REPAIR_SOURCE_20261029_V4'
Q=L/'E3_97_RESET34_NUMERICAL_AND_ORIGINAL_QUERY_DIAGNOSTIC_SOURCE_20261029_V1'
OLDJOB='/mnt/mod4_linux_durable_20261013/MOD4_E3_ADAPTED97_RECIPE_DOMAIN_20261029v4/e3'
JOB='/mnt/mod4_linux_durable_20261013/MOD4_E3_ADAPTED97_Q34_INITIAL24_ORIGINAL_QUERY_20261029v1/e3'
OLDK='MOD4_E3_ADAPTED97_SOURCE210_FROZEN_RECIPE_DOMAIN_V1'
KIND='MOD4_E3_ADAPTED97_SOURCE210_Q34_INITIAL24_ORIGINAL_QUERY_V1'
WORK0='evaluate_E3_adapted97_source210_frozen600_once_v1.py'
WORK='evaluate_E3_adapted97_source210_initial24_original_queries_once_v1.py'
CPU='E3_source210_target_source_SDK_metadata_admission_v1.py'
SUP='detached_E3_source210_frozen_recipe_supervisor_once_v1.py'
CODE='E3_source210_actual_receipts_readonly_CODE_v4.py'
REMOTE='remote_E3_source210_verify_metadata_CPU_and_detach_v4_exactEntryReceipt.py'
ENTRY='install_E3_source210_frozen_recipe_metadata_detach_UNUSED_once_v4_exactEntryReceipt.py'
INDEX='FROZEN_E3_Q34_INITIAL24_COMPLETE_SOURCE_INDEX_V1.json'
MF='E3_SOURCE210_COMPLETE_INPUT_MANIFEST_V1.json'
HOOK='e3_declared_fall_existing_query_observer_v1.py'
edits=[]
def H(b):return hashlib.sha256(b).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def save(n,x):
 with (B/n).open('x',encoding='utf8',newline='\n') as f:json.dump(x,f,indent=2,allow_nan=False)
def write(n,raw):
 with (B/n).open('xb') as f:f.write(raw)
def change(s,a,b,n=None):
 count=s.count(a);assert count and (n is None or count==n),(a,count,n)
 edits.append(dict(old=a,new=b,count=count));return s.replace(a,b)
def main():
 base=read(OLD/MF);m=json.loads(json.dumps(base));m['target_root']=m['target_stage']=JOB
 selected={WORK0,CPU,SUP,CODE,REMOTE,ENTRY,'run_E3_source210_readonly_v4.py','read_E3_source210_FIRST_native24_recipe_queue_UNUSED_once_v4.py','collect_E3_source210_TERMINAL_recipe_fulltext_UNUSED_once_v4.py','e3_declared_entry_receipt_cli_contract_v1.py','source210_project_launch_helpers_v1.py','zonglin2_app_launcher.py','e3_frozen_worker_call_guard_v1.py','e3_recipe_domain_telemetry_v1.py','e3_original_recipe_phase_catalog_v1.py','lossless_snapshot_pinned75d683.py','original_flat_height_provider_v1.py','selected_telemetry_constructor_API_fixture_v1.py','GROUND_PROVIDER_SOURCE_CONTRACT.json','E3_97_QUALIFIED_FORMAL_CPU_WITNESS.json','ORIGINAL_E3_PRODUCTION_ENTRY_COMMAND_AND_DECLARED_CLOSURE_CONTRACT.json','AUTH72_CURRENT_KNOWN_OWNER_READONLY_CODE_v1.py','PRE210_UNUSED_MOUNT_LIGHT_RESOURCE_CODE_v1.py'}
 per_file=[]
 for name in sorted(selected):
  start=len(edits)
  raw=(OLD/name).read_bytes()
  if name.endswith('.py'):
   s=raw.decode('utf8')
   if OLDJOB in s:s=change(s,OLDJOB,JOB)
   if OLDK in s:s=change(s,OLDK,KIND)
   if WORK0 in s:s=change(s,WORK0,WORK)
   if 'FROZEN_E3_97_SOURCE210_RECIPE_DOMAIN_SOURCE_INDEX_V4.json' in s:s=change(s,'FROZEN_E3_97_SOURCE210_RECIPE_DOMAIN_SOURCE_INDEX_V4.json',INDEX)
   if name==WORK0:
    s=change(s,"task['controls']==600 and task['warmup_controls']==100","task['controls']==24 and task['warmup_controls']==24",1)
    s=change(s,'for i in range(600):','for i in range(24):',1)
    s=change(s,'requested_controls=600,controls=completed','requested_controls=24,controls=completed',1)
    s=change(s,'wall_time_limited=completed<600','wall_time_limited=completed<24',1)
    s=change(s,"len(real.e3_shapes)==34 and real.recovery.recipe.shape==(20000,)","len(real.e3_shapes)==34 and real.recovery.recipe.shape==(20000,)\n  assert task['query_observer_SHA']==H(job/'"+HOOK+"') and task['initial_diagnostic_only'] and task['maximum_selected_IDs_per_recipe']==2",1)
    s=change(s,"want)\n  assert cmd.manual", "want);bind_original_limits(real,limits[:,gas_ids])\n  assert cmd.manual",1)
    integration=""" from e3_recovery_runtime_v1 import RecoveryEnv
 import mod4_task
 from h1_authored_full_collider_plane_reference_v1 import evaluate as original_authored_evaluate
 from e3_declared_fall_existing_query_observer_v1 import install_before_resume,ExistingQueryObserver
 def observer_factory(real):
  return ExistingQueryObserver(real,torch,OUT/'q34_existing_queries',None,original_authored_evaluate)
 finish_queries,overlay_proof,bind_original_limits=install_before_resume(RecoveryEnv,mod4_task,(mod/'mod4_task.py').read_bytes(),observer_factory)
 put('E3_ORIGINAL_QUERY_HOOK_INSTALLED_BEFORE_RESUME.json',dict(passed=True,hook_SHA=H(job/'e3_declared_fall_existing_query_observer_v1.py'),original_module_SHA=H(mod/'mod4_task.py'),overlay_inverse_AST=overlay_proof,controls=24,num_envs=20000,maximum_selected_IDs_per_recipe=2,no_extra_physics_actor_RNG_or_SDK_query=True,no_pre_firstphysics_or_each_substep_proof=True))
"""
    s=change(s,' rescue_training.learn=work\n',integration+' rescue_training.learn=work\n',1)
    s=change(s," finally:put('APP_CLOSING.json',dict(epoch=time.time()));ns['app'].close()", """ finally:
  try:
   query_results=finish_queries()
   put('E3_INITIAL24_ORIGINAL_QUERY_FINALIZATION_ACTUAL.json',dict(passed_hook_finalization=True,observers=len(query_results),diagnostic_valid=len(query_results)==1 and query_results[0]['diagnostic_valid'],retention_limited=any(x['retention_limited'] for x in query_results),query_reports=['q34_existing_queries/E3_RESET_REQUEST_EXISTING_CLOSURE_QUERY_DIAGNOSTIC_ACTUAL.json'] if query_results else [],physical_substep_or_postwrite_state_not_observed=True,original_methods_restored=True,skill_graduation=False))
  finally:put('APP_CLOSING.json',dict(epoch=time.time()));ns['app'].close()""",1)
   if name==SUP:
    s=change(s,"task['controls']==600","task['controls']==24",1)
    s=change(s,"and not errors,result=json.loads", "and not errors and (out/'E3_INITIAL24_ORIGINAL_QUERY_FINALIZATION_ACTUAL.json').exists() and json.loads((out/'E3_INITIAL24_ORIGINAL_QUERY_FINALIZATION_ACTUAL.json').read_bytes())['diagnostic_valid'],result=json.loads",1)
   if name==REMOTE:
    s=change(s,'controls=600,warmup_controls=100','controls=24,warmup_controls=24',1)
    s=change(s,'full_WM_tap_included=False)',"full_WM_tap_included=False,initial_diagnostic_only=True,maximum_selected_IDs_per_recipe=2,query_observer_SHA=H(J/'"+HOOK+"'),diagnostic_source_contract_SHA=H(J/'E3_INITIAL_QUERY_SOURCE_CONTRACT.json'))",1)
   if name==CPU:
    s=change(s,' from e3_declared_entry_receipt_cli_contract_v1 import validate_installed_entry_contract'," from e3_initial_query_integration_contract_v1 import validate_installed_query_contract\n query_contract=validate_installed_query_contract(J,m)\n from e3_declared_entry_receipt_cli_contract_v1 import validate_installed_entry_contract",1)
    s=change(s,'declared_entry_dependency_CLI_hook_receipt_contract=entry_closure,','declared_entry_dependency_CLI_hook_receipt_contract=entry_closure,query_observer_source_and_base_actual_CPU_metadata_contract=query_contract,',1)
   if name==CODE:
    s=change(s,"task['controls']==600 and task['warmup_controls']==100","task['controls']==24 and task['warmup_controls']==24",1)
    s=change(s,"result.get('controls')==600 and result.get('requested_controls')==600 and result.get('warmup_controls')==100 and result.get('steady_controls')==500","result.get('controls')==24 and result.get('requested_controls')==24 and result.get('warmup_controls')==24 and result.get('steady_controls')==0",1)
    s=change(s,'requested600_controls_100warm_500steady_complete=full','requested24_initial_controls_complete=full',1)
   ast.parse(s);raw=s.encode()
  write(WORK if name==WORK0 else name,raw)
  per_file.append(dict(source_name=name,target_name=WORK if name==WORK0 else name,source_SHA=H((OLD/name).read_bytes()),selected_SHA=H(raw),operations=edits[start:]))
 write(HOOK,(Q/HOOK).read_bytes())
 # Preserve exact old actual metadata report/wait bytes from saved UTF8 text only.
 startup=read(OLD/'reports/E3_SOURCE210_ACTUAL_METADATA_CPU_AND_FINITE_DETACHED_RETURNED_ACTUAL.json')
 for oldname,newname in [('E3_TARGET_SOURCE_SDK_METADATA_ACTUAL.json','BASE_E3_V4_SOURCE_SDK_CPU_ACTUAL.json'),('E3_SOURCE210_CPU_ORIGINAL_WAIT_PROOF.json','BASE_E3_V4_CPU_ORIGINAL_WAIT_ACTUAL.json')]:
  row=next(x for x in startup['complete_original_UTF8'] if x['path']==OLDJOB+'/'+oldname);raw=row['UTF8'].encode();assert len(raw)==row['bytes'] and H(raw)==row['SHA'];write(newname,raw)
 cpu=read(B/'BASE_E3_V4_SOURCE_SDK_CPU_ACTUAL.json');wait=read(B/'BASE_E3_V4_CPU_ORIGINAL_WAIT_ACTUAL.json');assert cpu['passed'] and wait['passed'] and wait['returncode']==0 and wait['actual_waited'] and cpu['model_loads_this_metadata_admission']==0
 save('E3_INITIAL_QUERY_SOURCE_CONTRACT.json',dict(kind=KIND,job_root=JOB,base_target_source210_root=OLDJOB,base_actual_CPU_SHA=H((B/'BASE_E3_V4_SOURCE_SDK_CPU_ACTUAL.json').read_bytes()),base_actual_CPU_wait_SHA=H((B/'BASE_E3_V4_CPU_ORIGINAL_WAIT_ACTUAL.json').read_bytes()),base_target_actual_CPU_original_identity=wait['actual_worker_identity'],base_manifest_SHA=H((OLD/MF).read_bytes()),source_SHA=base['model_SHA'],original_Adam=866060,original_LR=.0002562890625000001,num_envs=20000,controls=24,warmup_controls=24,steady_controls=0,simulated_seconds=.48,maximum_worker_seconds=1680,maximum_supervisor_seconds=1800,first_wait_seconds360=True,normal_remaining900_wait850=True,hook_SHA=H((B/HOOK).read_bytes()),original_task_SHA='30ce41126a1a9b78a1c2b446281b28f4555c28052bfaa7c0e9a76079cf561fc5',original_recovery_SHA='7e1d28e8ef1622f7923c00358f2683ea8682cf4553f0e1aacf40e68446b2ae2d',numeric_q34_original_NPZ_purpose_already_completed_do_not_repeat=True,numeric_q34_report_path=str(Q/'E3_Q34_ONE_NPZ_NUMERICAL_GAS400_F32_OWNFK_ACTUAL.json'),numeric_q34_report_SHA='03de4cacc2200326dcb21e8a362840ed7d7314d74e1d7b91e7e0836bce3b1aa0',plant_physics_actions_actor_original=True,actual_postwrite_or_first_substep_FK_unknown=True,source_only_not_target_ready=True))
 m['kind']='E3_97_original_q34_write_existing_query_initial24_source_only_v1';m['scope']=dict(num_envs=20000,controls=24,warmup=24,steady=0,initial_window_seconds=.48,recipe13_original_request3s_stabilitypoint5s_unchanged_not_fully_covered=True,no_PPO_or_Cwrite=True,skill_graduation=False);m['source_version']='NEW original-query diagnostic, original full20k restore domain';m['only_final97_model_metadata_and_owned_launcher_and_frozen_eval_sources_changed']=False;m['first_native24_read_wait_maximum_seconds']=360
 for row in m['files']:
  oldrel=row['relative'];name=Path(str(row['local_path'])).name
  if name in selected:
   newname=WORK if name==WORK0 else name;p=B/newname
   row.update(local_path=str(p),bytes=p.stat().st_size,SHA=H(p.read_bytes()))
   if oldrel==WORK0:row['relative']=WORK
 additions=[HOOK,'E3_INITIAL_QUERY_SOURCE_CONTRACT.json','BASE_E3_V4_SOURCE_SDK_CPU_ACTUAL.json','BASE_E3_V4_CPU_ORIGINAL_WAIT_ACTUAL.json','e3_initial_query_integration_contract_v1.py','selected_original_query_API_fixture_v1.py']
 for name in additions:
  p=B/name;assert p.is_file();m['files'].append(dict(relative=name,local_path=str(p),bytes=p.stat().st_size,SHA=H(p.read_bytes()),index_kind='new_source_or_existing_actual_metadata_bytes'))
 assert len({x['relative'] for x in m['files']})==len(m['files'])
 save(MF,m);save('NEW_WORKER_EXACT_TEXT_DERIVATION_INVERSE_OPERATIONS.json',dict(passed_assembly=True,source_worker=str(OLD/WORK0),source_worker_SHA=H((OLD/WORK0).read_bytes()),selected_worker_SHA=H((B/WORK).read_bytes()),files=per_file,edits=edits,no_existing_model_binary_NPZ_USD_raw_stat_or_content_read=True))
 print(json.dumps(dict(prepared=True,files=len(m['files']),worker_SHA=H((B/WORK).read_bytes()),target=JOB)))
if __name__=='__main__':
 try:main()
 except BaseException:save('SOURCE_ASSEMBLY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(traceback=traceback.format_exc(),source_only=True));raise
