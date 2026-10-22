from pathlib import Path
import ast,hashlib,json,shutil,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports'
read=lambda p:json.loads(Path(p).read_bytes())
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(name,v):
 with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 cfg=read(N/'PAIR_RESERVED_SOURCE_CONFIG_NO_TOKEN.json');P=Path(cfg['previous_stage_dir'])
 approved=read(T/'reports/V101_HUMAN_EXPLICIT_FUTURE_TRACE_RETENTION_APPROVAL_ACTUAL.json');retention=read(T/'reports/V101_FUTURE_BOUNDED_TRACE_PAIR_RETENTION_CANDIDATE_CPU_ACTUAL.json');assert approved['approved'] and retention['passed'] and approved['candidate_trace_SHA']==retention['candidate_trace']['SHA'] and approved['candidate_adapter_SHA']==retention['candidate_adapter']['SHA']
 receipt=read(P/'reports/E3_ONLY_COMPLETE_FINAL_ORIGINAL_COST_RETURNED_ACTUAL.json')
 e3proof=read(P/'reports/E3_ONLY_COMPLETE_MODEL_ORIGINAL_COST_CPU_ACTUAL.json')
 prior=T/'H1_STEP270_E3_BOUNDED_TRACE_PAIR_V15_20261022'
 h1proof=read(prior/'reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json')
 oldq=read(P/'reports/TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json')
 h1q=read(prior/'reports/TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json')
 retired=read(T/'H1_STEP270_REWARD_PATH_V1_20261022/reports/UNSTARTED_H1_ADMISSION_ORIGINAL_FINALLY_TERMINAL_ACTUAL.json')
 assert retired['passed'] and retired['no_H1_learning_GO_or_cost_interval']
 assert receipt['actual_finite_transport_returned'] and e3proof['passed'] and e3proof['H1_learning_GO_absent'] and e3proof['all_owner_nodes_children_actual_out'] and e3proof['original_canonical_cost_settled'] and e3proof['all_original_private_shared_locks_free']
 assert h1proof['passed'] and h1proof['all_owner_nodes_children_actual_out'] and h1proof['original_canonical_cost_settled']
 proof=dict(e3proof,models=dict(h1=h1proof['models']['h1'],recovery=e3proof['models']['recovery']))
 assert proof['remaining_actual_snapshot']>82512.86069250107
 put('PAIR_LATEST_SOURCES_PREPARE_STARTED_ACTUAL.json',dict(epoch=time.time(),no_GO=True))
 rec=read(P/'reports/ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json')
 rec.update(remaining_after=proof['remaining_actual_snapshot'],derived_current_cohort_source_cost_receipt_only=True,legacy18_pending_not_reconciled_again=True,source_current_cohort_original_cost_summary=proof)
 put('ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json',rec)
 payloads={};specs={};sources={}
 for key in ('h1','recovery'):
  base=Path(h1q['payloads']['h1'] if key=='h1' else oldq['payloads'][key]);dest=N/'payloads'/key;assert not dest.exists();shutil.copytree(base,dest)
  oldm=read(base/'THREE_SLOT_COMPLETE_MANIFEST_V1.json');model=proof['models'][key];final=model['final'];source=Path(final['local_path'])
  assert final['twohost_complete_SHA'] and source.stat().st_size==final['bytes']
  spec=dict(oldq['specs'][key]);oldAdam=spec['source_Adamstep'];previous_root=h1q['roots']['h1'] if key=='h1' else oldq['roots'][key]
  spec.update(previous_runtime_root=previous_root,previous_exit_kind='node',source_SHA=final['SHA'],source_Adamstep=model['Adam'],closed_production_continuation=True,reuse_completed_native=False)
  shutil.copy2(source,dest/'job0/source'/spec['source_filename'])
  if key=='h1':
   spec['reward_migration']=True
   shutil.copy2(T/'H1_STEP270_REWARD_PATH_V1_20261022/closed_step270_reward_migration_owner_schema_source_CPU_v2.py',dest/'closed_production_continuation_CPU_v2.py')
   for name in ('h1_production_control_prefix_trace_v1.py','h1_prefix_pair_retention_v1.py'):
    shutil.copy2(T/'trace_retention_candidate_V1_UNINSTALLED'/name,dest/name)
   (dest/'H1_TRACE_RETENTION_HUMAN_APPROVAL_ACTUAL.json').write_text(json.dumps(approved,indent=2),encoding='utf8')
   (dest/'H1_TRACE_RETENTION_CANDIDATE_CPU_ACTUAL.json').write_text(json.dumps(retention,indent=2),encoding='utf8')
   shutil.copy2(T/'target_H1_step270_closed_source_sdk_cpu_review_v1.py',dest/'target_H1_step270_closed_source_sdk_cpu_review_v1.py')
   reward_stage=T/'H1_STEP270_REWARD_PATH_V1_20261022'
   for name in ('h1_step270_sdk_runtime_candidate.py','h1_step270_path_reward_v1.py','step270_reward_installed_CPU_v1.py'):
    shutil.copy2(reward_stage/name,dest/name)
   shutil.copy2(reward_stage/'target_H1_step270_reward_path_closed_source_sdk_cpu_review_v1.py',dest/'target_H1_step270_closed_source_sdk_cpu_review_v1.py')
   shutil.copy2(reward_stage/'reports/HUMAN_REWARD_CHANGE_AND_SOURCE_CPU_AUTH_ACTUAL.json',dest/'H1_REWARD_CHANGE_AUTH_AND_SOURCE_CPU_ACTUAL.json')
   proofname='CURRENT_ORIGINAL_PAIR_CLOSED_MODELS_COST_CPU_ACTUAL.json'
  else:
   worker=dest/'recovery_worker.py';text=worker.read_text('utf8');needle='{'+str(oldAdam)+'+20*updates}';assert text.count(needle)==1
   worker.write_text(text.replace(needle,'{'+str(model['Adam'])+'+20*updates}'),encoding='utf8')
   proofname='CURRENT_ORIGINAL_COHORT_CLOSED_COST_CPU_ACTUAL.json'
  if key=='h1':
   (dest/'OWNER_REWARD_MIGRATION_SCHEMA_CPU_ACTUAL.json').write_text((T/'H1_STEP270_REWARD_PATH_V1_20261022/reports/ORIGINAL_OWNER_REWARD_MIGRATION_ADMISSION_SCHEMA_CPU_ACTUAL.json').read_text('utf8'),encoding='utf8')
  for p in (N/'controllers').glob('*.py'):shutil.copy2(p,dest/p.name)
  task=read(dest/'job0/TASK.json')
  (dest/'PREVIOUS_TASK_METADATA_HISTORICAL.json').write_text(json.dumps(task,indent=2),encoding='utf8')
  task.update(explicit_human_authorized_reward_path_change=key=='h1',reward_recipe_version='step270_forward_clearance_path_reward_v1' if key=='h1' else None,approved_future_prefix_retention_policy=retention['policy'] if key=='h1' else None,qualified_source_fallback_after_failed_pair7=False,only_command_audit_adapter_repair=False,id=cfg['cohort_id']+'_'+key,GPU_UUID=spec['GPU_UUID'],execution_backend=spec['execution_backend'],source_SHA=final['SHA'],source_Adamstep=model['Adam'],source_H1_actual_latest_Adamstep=model['Adam'] if key=='h1' else None,source_parent_production_root=previous_root,source_policy_hz=spec['policy_hz'],policy_hz=spec['policy_hz'],source_owned_updates=model['updates'],source_owned_completed_updates=model['updates'],exact_closed_source_updates=model['updates'],same_clock_complete_source_no_native_replay=True,explicit_step270_task_migration=False if key=='h1' else task.get('explicit_step270_task_migration',False),same_step270_phase_complete_continuation=key=='h1')
  (dest/'job0/TASK.json').write_text(json.dumps(task,indent=2),encoding='utf8')
  for name,value in [('QUALIFIED_RUNTIME_BASE_MANIFEST.json',oldm),(proofname,h1proof if key=='h1' else proof),('ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json',rec)]:
   (dest/name).write_text(json.dumps(value,indent=2),encoding='utf8')
  prior={x['relative']:x for x in oldm['files']};rows=[]
  for p in sorted(dest.rglob('*')):
   if not p.is_file() or p.name=='THREE_SLOT_COMPLETE_MANIFEST_V1.json' or '__pycache__' in p.parts:continue
   if p.suffix=='.py':ast.parse(p.read_text('utf8'))
   rel=p.relative_to(dest).as_posix()
   sha=(final['SHA'] if rel=='job0/source/'+spec['source_filename'] else prior[rel]['SHA']) if p.suffix in ('.pt','.npz','.usd','.stl') else H(p)
   rows.append(dict(relative=rel,bytes=p.stat().st_size,SHA=sha))
  m=dict(oldm,source_SHA=final['SHA'],source_Adamstep=model['Adam'],files=rows,closed_step270_samephase_continuation=key=='h1',explicit_command_audit_adapter_repair=False)
  (dest/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').write_text(json.dumps(m,indent=2),encoding='utf8')
  spec['manifest_SHA']=H(dest/'THREE_SLOT_COMPLETE_MANIFEST_V1.json');payloads[key]=str(dest);specs[key]=spec
  sources[key]=dict(SHA=final['SHA'],bytes=final['bytes'],Adam=model['Adam'],updates=model['updates'],path=final['path'])
 q=dict(epoch=time.time(),passed=True,payloads=payloads,specs=specs,sources=sources,roots=cfg['roots'],owner_root=cfg['owner_root'],previous_owner_root=read(P/'reports/PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json')['owner_root'],both_latest_complete_model_CPU_original_cost_allout=True,no_native_or_query_replay=True,no_remote_Task_or_GO_yet=True)
 put('TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json',q)
 print(json.dumps(dict(prepared=True,sources=sources,no_GO=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  put('PAIR_PREPARE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_retry_or_GO=True));raise
