from pathlib import Path
import ast,hashlib,json,shutil,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports';R.mkdir(exist_ok=True)
Q=T/'H1_STEP270_MIXED_UNISUPERMIMIC_RESOURCE_V82Q_20261026';P=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V80_20261026'
read=lambda p:json.loads(Path(p).read_bytes());SHA=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):
 with Path(p).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 current=read(Q/'reports/PRODUCTION_PAIR_AND_NATIVE_METHOD_FULLSTATE_ORIGINAL_COST_CPU_ACTUAL.json');old80=read(P/'reports/THREE_EXPERT_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json')
 assert current['passed'] and current['original_canonical_cost_settled'] and current['all_owner_nodes_children_actual_out'] and current['all_original_private_shared_locks_free'] and set(current['models'])=={'h1','recovery'} and current['native_method']['original_terminal']['original_error'] and current['native_method']['present'] is False
 assert current['qualification_scope']=='production_h1_recovery_pair_and_separate_native_method_diagnostic' and set(current['original_slots_cost'])=={'h1','e2','recovery'} and all(v['duration_bound_passed'] for v in current['original_slots_cost'].values()) and abs(current['actual_cost_sumonce']-sum(v['charged_seconds'] for v in current['original_slots_cost'].values()))<1e-5
 assert old80['passed'] and old80['all_owner_nodes_children_actual_out'] and old80['original_canonical_cost_settled'] and old80['models']['e2']['Adam']==855660 and old80['models']['e2']['final']['SHA']=='632b3ffb929d76fcdf6b057aae4846424dcf09c90e4277bdbeedb78dccaaacaf'
 aq=read(Q/'reports/THREE_EXPERTS_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json');ap=read(P/'reports/THREE_EXPERTS_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json')
 assert not (N/'payloads').exists() and not (N/'controllers').exists();shutil.copytree(P/'controllers',N/'controllers')
 rec=read(Q/'reports/ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json');rec.update(remaining_after=current['remaining_actual_snapshot'],latest_actual82Q_original_all3_cost_closure=current,source_current_cohort_original_cost_summary=current,old_E2_80_original_cost_source_only_not_recharged=True,native82Q_not_a_production_source=True)
 put(R/'ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json',rec)
 outq=dict(epoch=time.time(),passed=True,payloads={},specs={},sources={},roots={},owner_root='/mnt/mod4_linux_durable_20261013/H1step270_three_experts_2610v83/owner',previous_owner_root=aq['owner_root'],strict_three_cap_remaining=86412.86069250107,normal_H1_E2_E3_no_method_scope=True,source_production_windows=dict(h1='82Q',recovery='82Q',e2='80'),no_GO_or_new_fee_yet=True)
 for key in ('h1','recovery','e2'):
  sourceq=ap if key=='e2' else aq;proof=old80 if key=='e2' else current;model=proof['models'][key];final=model['final'];base=Path(sourceq['payloads'][key]);out=N/'payloads'/key;shutil.copytree(base,out,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
  prior=read(out/'THREE_SLOT_COMPLETE_MANIFEST_V1.json');hist=out/'prebind83_exact_history';hist.mkdir()
  role='closed_production_continuation_CPU_v2.py' if key=='h1' else 'original_account_policy50_source_CPU.py'
  for name in ('THREE_SLOT_COMPLETE_MANIFEST_V1.json','job0/TASK.json','QUALIFIED_RUNTIME_BASE_MANIFEST.json','CURRENT_ORIGINAL_THREE_CLOSED_MODELS_COST_CPU_ACTUAL.json',role):shutil.copy2(out/name,hist/(Path(name).name+'.original_bytes.txt'))
  spec=dict(sourceq['specs'][key]);spec.update(previous_runtime_root=sourceq['roots'][key],previous_exit_kind='node',source_SHA=final['SHA'],source_Adamstep=model['Adam'],reward_migration=False,cross_host_qualified_source=False,closed_production_continuation=True,reuse_completed_native=False)
  assert not spec.get('finite_method_test') and not spec.get('h1_step270_method_test')
  assert final['twohost_complete_SHA'] and Path(final['local_path']).stat().st_size==final['bytes'];shutil.copy2(final['local_path'],out/'job0/source'/spec['source_filename'])
  if key=='e2':
   guard=(P/'candidates/closed_three_V8_landing_journal_source_CPU_v1.py').read_text('utf8');oldauth='THREE_EXPERT_V8_LIFETIME_DIAG_CONTINUATION_AUTH_80_ACTUAL.json'
   assert oldauth in guard;guard=guard.replace(oldauth,'NORMAL_THREE_83_PRODUCTION_SOURCE_AUTH_ACTUAL.json')
   needle=" qualified=validate_closed69_metadata(proof,key,prior['source_Adamstep']);"
   assert guard.count(needle)==1
   extra=""" if key=='e2':
  closure=read(B/'CURRENT_DISPLACED_NATIVE_82Q_CLOSURE_ACTUAL.json');assert H(B/'CURRENT_DISPLACED_NATIVE_82Q_CLOSURE_ACTUAL.json')==auth['current_resource_closure_SHA'] and closure['qualification_scope']=='production_h1_recovery_pair_and_separate_native_method_diagnostic' and set(closure['models'])=={'h1','recovery'} and closure['all_owner_nodes_children_actual_out'] and closure['original_canonical_cost_settled'] and closure['all_original_private_shared_locks_free']
  assert closure['native_method']['present'] is False and closure['native_method']['original_terminal']['original_error'] and closure['original_slots_cost']['e2']['duration_bound_passed']
  displaced=Path(spec['displaced_runtime_root']);assert str(displaced)=='/home/lc01/Zonglin Li/zonglin2/tasks/H1step270_mixed_supermimic_2610v82q/e2' and str(old)=='/home/lc01/Zonglin Li/zonglin2/tasks/H1step270_three_experts_2610v80/e2'
  dx=read(displaced/'NODE_EXIT_ACTUAL.json');dt=read(displaced/'NODE_TERMINAL_ACTUAL.json')['row'];assert dx['actual_all_own_children_waited'] and dx['validation_fcntl_released_if_acquired'] and dt['terminal_all_own_children_waited'] and dt['original_error'] and not (dt.get('final') or {}).get('passed')
  assert not any(p.pid!=os.getpid() and any(x.startswith(str(displaced)+'/') for x in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))
"""
   guard=guard.replace(needle,extra+needle,1);spec['displaced_runtime_root']=aq['roots']['e2']
   put(out/'CURRENT_DISPLACED_NATIVE_82Q_CLOSURE_ACTUAL.json',current)
  else:
   guard=(Q/'payloads'/key/role).read_text('utf8').replace('HEALTHY81O_SAME_V8_CONTINUATION_AUTH_82P_ACTUAL.json','NORMAL_THREE_83_PRODUCTION_SOURCE_AUTH_ACTUAL.json').replace('actual_closed_healthy_pair_failed_method_all3_cost_same_V8','actual_closed_production_pair_native_diagnostic_all3_cost_same_V8')
   guard=guard.replace("proof['qualification_scope']=='healthy_h1_recovery_models_with_failed_method_all3_original_cost'","proof['qualification_scope']=='production_h1_recovery_pair_and_separate_native_method_diagnostic'")
   guard=guard.replace("proof['failed_method']['original_error'] and proof['failed_method']['no_qualified_model']","proof['native_method']['original_terminal']['original_error'] and proof['native_method']['present'] is False")
   if key=='recovery':
    p=out/'recovery_worker.py';s=p.read_text('utf8');needle='{'+str(prior['source_Adamstep'])+'+20*updates}';assert s.count(needle)==1;p.write_text(s.replace(needle,'{'+str(model['Adam'])+'+20*updates}',1),'utf8')
  ast.parse(guard);(out/role).write_text(guard,'utf8')
  assert SHA(out/'same_optimized_source_contract_metadata_candidate_v1.py')==SHA(base/'same_optimized_source_contract_metadata_candidate_v1.py')=='c6e421115263e6bfd0fb31630882087fb644efbfb3a56bfbd39643c4478c891e'
  task=read(out/'job0/TASK.json');task.update(id=N.name+'_'+key,source_SHA=final['SHA'],source_Adamstep=model['Adam'],source_owned_updates=model['updates'],source_owned_completed_updates=model['updates'],exact_closed_source_updates=model['updates'],source_parent_production_root=sourceq['roots'][key])
  if key=='h1':task.update(source_H1_actual_latest_Adamstep=model['Adam'],reward_recipe_version='step270_sampled_leg_excess_v8_reward_only')
  (out/'job0/TASK.json').write_text(json.dumps(task,indent=2),'utf8')
  for name,value in [('QUALIFIED_RUNTIME_BASE_MANIFEST.json',prior),('CURRENT_ORIGINAL_THREE_CLOSED_MODELS_COST_CPU_ACTUAL.json',proof),('ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json',rec)]: (out/name).write_text(json.dumps(value,indent=2),'utf8')
  auth=dict(epoch=time.time(),approved=True,kind=('actual_closed_three_same_V8_landing_journal_continuation' if key=='e2' else 'actual_closed_production_pair_native_diagnostic_all3_cost_same_V8'),source_SHA=final['SHA'],source_Adam=model['Adam'],guard_SHA=SHA(out/role),metadata_SHA=SHA(out/'same_optimized_source_contract_metadata_candidate_v1.py'),source_production_window='80' if key=='e2' else '82Q',current_resource_closure_SHA=SHA(out/'CURRENT_DISPLACED_NATIVE_82Q_CLOSURE_ACTUAL.json') if key=='e2' else None,no_reward_actor_PPO_physics_or_success_change=True,no_native_checkpoint_promoted=True)
  put(out/'NORMAL_THREE_83_PRODUCTION_SOURCE_AUTH_ACTUAL.json',auth)
  before={r['relative']:r for r in prior['files']};rows=[]
  for p in sorted(out.rglob('*')):
   if not p.is_file() or p.name=='THREE_SLOT_COMPLETE_MANIFEST_V1.json' or '__pycache__' in p.parts:continue
   rel=p.relative_to(out).as_posix()
   if p.suffix=='.py':ast.parse(p.read_text('utf8'))
   digest=(final['SHA'] if rel=='job0/source/'+spec['source_filename'] else before[rel]['SHA']) if p.suffix in ('.pt','.npz','.usd','.stl') else SHA(p)
   rows.append(dict(relative=rel,bytes=p.stat().st_size,SHA=digest))
  manifest=dict(prior,source_SHA=final['SHA'],source_Adamstep=model['Adam'],files=rows)
  (out/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').write_text(json.dumps(manifest,indent=2),'utf8');spec['manifest_SHA']=SHA(out/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')
  outq['payloads'][key]=str(out);outq['specs'][key]=spec;outq['sources'][key]=dict(SHA=final['SHA'],bytes=final['bytes'],Adam=model['Adam'],updates=model['updates'],path=final['path']);outq['roots'][key]=('/mnt/mod4_linux_durable_20261013' if key=='h1' else '/home/lc01/Zonglin Li/zonglin2/tasks')+'/H1step270_three_experts_2610v83/'+key
 put(R/'THREE_EXPERTS_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json',outq)
 put(R/'NORMAL_THREE_83_QUALIFIED_SOURCE_DISPLACED_RESOURCE_PREPARATION_ACTUAL.json',dict(epoch=time.time(),passed_source_preparation_only=True,source_windows=outq['source_production_windows'],source_Adam={k:v['Adam'] for k,v in outq['sources'].items()},current_original_closing=current['remaining_actual_snapshot'],normal_E2_source80_not_native_method=True,original_controller_charge_and_runtime_resources_unchanged=True,no_GO_or_new_fee_yet=True,nonfatal_three_backslash_S_ASTwarnings=True,initial_local_missing_source_name_readers_not_training_failures=['80/candidates/same_three_closed_source_V8_landing_journal_CPU_v1.py','80/deploy_actual_three_experts80_original_writer_unused_once.py']))
 print(json.dumps(dict(prepared83=True,source_Adam={k:v['Adam'] for k,v in outq['sources'].items()},no_GO=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  put(R/('SOURCE83_PREPARE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),no_same_once_replay_or_original_source_mutation=True));raise
