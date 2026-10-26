from pathlib import Path
import ast,hashlib,json,shutil,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports';O=T/'H1_STEP270_MIXED_UNISUPERMIMIC_RESOURCE_V81O_20261026';H=T/'MOD4_UNISUPERMIMIC_H1_STEP270_ON72_CONVERGENCE_20261026'
read=lambda p:json.loads(Path(p).read_bytes());SHA=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 proof=read(O/'reports/HEALTHY_PRODUCTION_PAIR_AND_FAILED_METHOD_ORIGINAL_ALL_COST_CPU_ACTUAL.json')
 assert proof['passed'] and proof['qualification_scope']=='healthy_h1_recovery_models_with_failed_method_all3_original_cost' and set(proof['models'])=={'h1','recovery'} and proof['failed_method']['original_error'] and proof['failed_method']['no_qualified_model']
 assert proof['original_canonical_cost_settled'] and proof['all_owner_nodes_children_actual_out'] and proof['all_original_private_shared_locks_free'] and proof['remaining_actual_snapshot']>86412.86069250107
 assert set(proof['original_slots_cost'])=={'h1','e2','recovery'} and all(v['duration_bound_passed'] for v in proof['original_slots_cost'].values())
 assert read(H/'reports/AST_CANDIDATE_V5_CHECKPOINT_BOOTSTRAP_AND_SAMPLING_CONTEXT_ACTUAL.json')['all_other_private_bridge_logic_AST_exact']
 for name in ('ACTUAL_RSL_CHECKPOINT_API_AND_INFERENCE_CONTEXT_CPU_V5_ACTUAL.json','CANDIDATE_V5_PHYSICAL_FORWARDING_AND_SAVE_FAILURE_CPU_ACTUAL.json'):assert read(H/'reports'/name)['passed']
 oldq=read(O/'reports/THREE_EXPERTS_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json');rec=read(O/'reports/ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json')
 rec.update(remaining_after=proof['remaining_actual_snapshot'],latest_original_mixed_cohort_closure=proof,source_current_cohort_original_cost_summary=proof,derived_current_cohort_source_cost_receipt_only=True,failed_method_cost_preserved_not_refunded=True)
 put(R/'ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json',rec)
 assert not (N/'controllers').exists();shutil.copytree(O/'controllers',N/'controllers')
 q=dict(epoch=time.time(),passed=True,payloads={},specs={},sources={},roots={},owner_root='/mnt/mod4_linux_durable_20261013/H1step270_mixed_supermimic_2610v82p/owner',previous_owner_root=oldq['owner_root'],three_slot_strict_remaining_guard=86412.86069250107,closed81o_healthy_pair_failed_method_original_all_cost=True,no_remote_GO_or_new_fee_yet=True)
 for key in ('h1','recovery','e2'):
  base=Path(oldq['payloads'][key]);out=N/'payloads'/key;assert not out.exists();shutil.copytree(base,out,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
  prior=read(base/'THREE_SLOT_COMPLETE_MANIFEST_V1.json');model=proof['models']['h1' if key=='e2' else key];final=model['final'];spec=dict(oldq['specs'][key])
  hist=out/'prebind82P_exact_history';hist.mkdir()
  for name in ('THREE_SLOT_COMPLETE_MANIFEST_V1.json','job0/TASK.json','ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json','QUALIFIED_RUNTIME_BASE_MANIFEST.json'):
   shutil.copy2(out/name,hist/(Path(name).name+'.original_bytes.txt'))
  role='closed_production_continuation_CPU_v2.py' if key in ('h1','e2') else 'original_account_policy50_source_CPU.py';shutil.copy2(out/role,hist/(role+'.original_bytes.txt'))
  spec.update(previous_runtime_root=oldq['roots'][key],previous_exit_kind=('failed_native_h1_method81o' if key=='e2' else 'node'),source_SHA=final['SHA'],source_Adamstep=model['Adam'],reward_migration=False,cross_host_qualified_source=False)
  assert Path(final['local_path']).stat().st_size==final['bytes'] and final['twohost_complete_SHA'];shutil.copy2(final['local_path'],out/'job0/source'/spec['source_filename'])
  if key!='e2':
   shutil.copy2(N/'candidates/healthy_pair_failed_method_same_V8_source_guard_v1.py',out/role)
   if key=='recovery':
    p=out/'recovery_worker.py';s=p.read_text('utf8');a='{'+str(prior['source_Adamstep'])+'+20*updates}';assert s.count(a)==1;p.write_text(s.replace(a,'{'+str(model['Adam'])+'+20*updates}',1),'utf8')
   auth=dict(epoch=time.time(),approved=True,kind='actual_closed_healthy_pair_failed_method_all3_cost_same_V8',source_SHA=final['SHA'],source_Adam=model['Adam'],guard_SHA=SHA(out/role),metadata_SHA=SHA(out/'same_optimized_source_contract_metadata_candidate_v1.py'),no_reward_actor_command_physics_or_success_change=True)
   put(out/'HEALTHY81O_SAME_V8_CONTINUATION_AUTH_82P_ACTUAL.json',auth)
  else:
   # Native models are initialized normally outside inference mode; only the physical sampler uses inference context.
   p=out/'source/h1_supermimic_bridge_v1.py';shutil.copy2(p,hist/'h1_supermimic_bridge81O_original_bytes.txt');shutil.copy2(H/'candidate_source_v5/h1_supermimic_bridge_v1.py',p)
   src=(out/role).read_text('utf8').replace('source80_actual_cost_models_allout_passed=True','source81o_healthy_H1_original_cost_models_allout_passed=True');(out/role).write_text(src,'utf8')
   p=out/'three_real_gpu_resource_v1.py';src=p.read_text('utf8');needle=" elif kind=='native_only':"
   branch=""" elif kind=='failed_native_h1_method81o':
  assert spec['key']=='e2' and spec.get('h1_step270_method_test') and spec['GPU_UUID']=='GPU-16828f91-2b45-b646-8dc0-9481138e2842' and str(old)=='/home/lc01/Zonglin Li/zonglin2/tasks/H1step270_mixed_supermimic_2610v81o/e2'
  proof=json.loads((B/'CURRENT_ORIGINAL_THREE_CLOSED_MODELS_COST_CPU_ACTUAL.json').read_bytes());assert proof['qualification_scope']=='healthy_h1_recovery_models_with_failed_method_all3_original_cost' and proof['original_canonical_cost_settled'] and proof['all_owner_nodes_children_actual_out'] and proof['all_original_private_shared_locks_free'] and proof['failed_method']['original_error'] and proof['failed_method']['no_qualified_model']
  e=json.loads((old/'NODE_EXIT_ACTUAL.json').read_bytes());r=json.loads((old/'NODE_TERMINAL_ACTUAL.json').read_bytes())['row'];assert e['actual_all_own_children_waited'] and e['validation_fcntl_released_if_acquired'] and r['terminal_all_own_children_waited'] and r['original_error'] and not (r.get('final') or {}).get('passed')
  cost=proof['original_slots_cost']['e2'];assert cost['duration_bound_passed'] and cost['charged_seconds']>0 and abs(cost['charged_seconds']-(cost['ended_epoch']-cost['started_epoch']))<1e-5
"""
   assert src.count(needle)==1;p.write_text(src.replace(needle,branch+needle,1),'utf8')
   put(out/'H1_NATIVE_METHOD_CHECKPOINT_WRITER_CONTEXT_V5_FIX_AUTH_ACTUAL.json',dict(epoch=time.time(),under_human_authorized_real_H1_convergence_test=True,bridge_SHA=SHA(out/'source/h1_supermimic_bridge_v1.py'),actual_observed_fix='Initialize original RSL logger.writer=None before first preupdate save',prospective_sampling_inference_context=True,no_native_optimizer_or_physical_equation_change=True,original_primary_secondary_errors_retained=True,source_healthy_H1_SHA=final['SHA'],failed81O_not_a_model_source=True))
  assert SHA(out/'same_optimized_source_contract_metadata_candidate_v1.py')==SHA(base/'same_optimized_source_contract_metadata_candidate_v1.py')=='c6e421115263e6bfd0fb31630882087fb644efbfb3a56bfbd39643c4478c891e'
  task=read(out/'job0/TASK.json');task.update(id=N.name+'_'+key,source_SHA=final['SHA'],source_Adamstep=model['Adam'],source_owned_updates=model['updates'],source_owned_completed_updates=model['updates'],exact_closed_source_updates=model['updates'],source_parent_production_root=oldq['roots']['h1' if key=='e2' else key])
  if key in ('h1','e2'):task['source_H1_actual_latest_Adamstep']=model['Adam']
  (out/'job0/TASK.json').write_text(json.dumps(task,indent=2),'utf8')
  for name,val in [('QUALIFIED_RUNTIME_BASE_MANIFEST.json',prior),('CURRENT_ORIGINAL_THREE_CLOSED_MODELS_COST_CPU_ACTUAL.json',proof),('ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json',rec)]: (out/name).write_text(json.dumps(val,indent=2),'utf8')
  before={r['relative']:r for r in prior['files']};rows=[]
  for p in sorted(out.rglob('*')):
   if not p.is_file() or p.name=='THREE_SLOT_COMPLETE_MANIFEST_V1.json' or '__pycache__' in p.parts:continue
   rel=p.relative_to(out).as_posix()
   if p.suffix=='.py':ast.parse(p.read_text('utf8'))
   digest=(final['SHA'] if rel=='job0/source/'+spec['source_filename'] else before[rel]['SHA']) if p.suffix in ('.pt','.npz','.usd','.stl') else SHA(p)
   rows.append(dict(relative=rel,bytes=p.stat().st_size,SHA=digest))
  manifest=dict(prior,source_SHA=final['SHA'],source_Adamstep=model['Adam'],files=rows)
  (out/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').write_text(json.dumps(manifest,indent=2),'utf8');spec['manifest_SHA']=SHA(out/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')
  q['payloads'][key]=str(out);q['specs'][key]=spec;q['sources'][key]=dict(SHA=final['SHA'],bytes=final['bytes'],Adam=model['Adam'],updates=model['updates'],path=final['path']);q['roots'][key]=('/mnt/mod4_linux_durable_20261013' if key=='h1' else '/home/lc01/Zonglin Li/zonglin2/tasks')+'/H1step270_mixed_supermimic_2610v82p/'+key
 put(R/'THREE_EXPERTS_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json',q)
 print(json.dumps(dict(bound=True,latest81o_healthy_sources_only=True,failed81o_only_resource_scope_not_source=True,source_Adam={k:v['Adam'] for k,v in q['sources'].items()},no_GO=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  put(R/('BIND_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),no_same_root_or_once_retry=True));raise
