"""Bind closed69 full sources to a new same-reward, same-optimized continuation."""
from pathlib import Path
import ast,hashlib,importlib.util,json,shutil,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
P=T/'H1_STEP270_SAGITTAL_V6A_SAMPLING_OPT_V4_RESOURCE_V69_20261025'
D=T/'MOD4_CLOSED68_ORIGINAL_HANDOFF_V69_COMBINED_RESTART_20261025'
read=lambda p:json.loads(Path(p).read_bytes())
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):
 with Path(p).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
AST_CHECK='''
def exact_recovery_source_adam_change(before_text,after_text,old_Adam,new_Adam):
    import ast,copy
    before=ast.parse(before_text);after=ast.parse(after_text)
    expected=ast.parse(str(old_Adam)+'+20*updates',mode='eval').body
    target=ast.parse(str(new_Adam)+'+20*updates',mode='eval').body
    matches=[]
    class Replace(ast.NodeTransformer):
        def visit_Assert(self,node):
            if (isinstance(node.test,ast.Compare) and isinstance(node.test.left,ast.Name)
                and node.test.left.id=='steps' and len(node.test.ops)==1 and isinstance(node.test.ops[0],ast.Eq)
                and len(node.test.comparators)==1 and isinstance(node.test.comparators[0],ast.Set)
                and len(node.test.comparators[0].elts)==1
                and ast.dump(node.test.comparators[0].elts[0])==ast.dump(expected)):
                matches.append(node.lineno);node.test.comparators[0].elts[0]=copy.deepcopy(target)
            return self.generic_visit(node)
    changed=Replace().visit(before)
    assert len(matches)==1 and ast.dump(changed)==ast.dump(after),'Only exact saved-Adam assertion literal may change'
    return dict(passed=True,old_source_Adam=old_Adam,new_source_Adam=new_Adam,changed_assert_lines=matches,all_other_AST_exact=True)
'''
try:
 assert not any((N/x).exists() for x in ('payloads','controllers'))
 proof=read(P/'reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json')
 assert proof['passed'] and proof['all_owner_nodes_children_actual_out'] and proof['original_canonical_cost_settled'] and proof['all_original_private_shared_locks_free']
 assert proof['remaining_actual_snapshot']>82512.86069250107
 oldq=read(P/'reports/TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json')
 sp=importlib.util.spec_from_file_location('metadata70',N/'same_optimized_source_contract_metadata_candidate_v1.py');md=importlib.util.module_from_spec(sp);sp.loader.exec_module(md)
 for key,start in [('h1',790480),('recovery',837420)]:md.validate_closed69_metadata(proof,key,start)
 guard=(N/'same_optimized_installed_source_admission_candidate_v1.py').read_text('utf8')
 guard=guard.replace('import hashlib,json,os','import ast,hashlib,json,os',1)
 needle="\ndef load(spec,B):";assert guard.count(needle)==1;guard=guard.replace(needle,AST_CHECK+needle,1)
 needle="if rel.endswith('.py') and rel!=role:";assert guard.count(needle)==1
 guard=guard.replace(needle,"if rel.endswith('.py') and rel!=role and not (key=='recovery' and rel=='recovery_worker.py'):",1)
 needle="    new_python={r for r in after if r.endswith('.py') and r not in before}";assert guard.count(needle)==1
 guard=guard.replace(needle,"    if key=='recovery':\n        exact_recovery_source_adam_change((old/'recovery_worker.py').read_text('utf8'),(B/'recovery_worker.py').read_text('utf8'),837420,spec['source_Adamstep'])\n"+needle,1)
 needle="assert spec['policy_hz']==spec['source_policy_hz']==50 and cpu['source_schema_counts']==[173,96]";assert guard.count(needle)==1
 guard=guard.replace(needle,needle+"\n        clock=read(old/'job0/production/E3_POLICY50_CLOCK_ACTUAL.json')\n        assert clock['policy_hz']==50 and clock['physics_dt_s']==.0025 and clock['decimation']==8",1)
 guard=guard.replace('Uninstalled70 candidate load API. Requires real closed69, full installed CPU, new source auth.','Installed70 source guard V2: closed69 normal cost, unchanged optimized source, exact saved-Adam substitution.',1)
 path=N/'same_optimized_installed_source_admission_v2.py'
 with path.open('x',encoding='utf8') as f:f.write(guard)
 ast.parse(guard)
 check={};exec(AST_CHECK,check)
 old_worker=(Path(oldq['payloads']['recovery'])/'recovery_worker.py').read_text('utf8')
 expected='{837420+20*updates}';assert old_worker.count(expected)==1
 new_worker=old_worker.replace(expected,'{839020+20*updates}',1)
 tests=[check['exact_recovery_source_adam_change'](old_worker,new_worker,837420,839020)]
 for label,bad in [('wrong_source_Adam',new_worker.replace('{839020+20*updates}','{839040+20*updates}')),('changed_optimizer_increment',new_worker.replace('{839020+20*updates}','{839020+10*updates}')),('removed_guard',new_worker.replace('assert steps=={839020+20*updates}','assert True')),('unrelated_extra_statement',new_worker+'\nUNAPPROVED=1\n')]:
  try:check['exact_recovery_source_adam_change'](old_worker,bad,837420,839020)
  except AssertionError:tests.append(dict(test=label,rejected=True))
  else:raise AssertionError(label)
 put(R/'SAME_OPTIMIZED70_EXACT_ADAM_GUARD_V2_CPU_ACTUAL.json',dict(epoch=time.time(),passed=True,tests=tests,actual_old_recovery_worker_SHA=H(Path(oldq['payloads']['recovery'])/'recovery_worker.py'),guard_SHA=H(path),source_full_models_not_reloaded_locally=True,not_remote_installed_or_GO=True))
 shutil.copytree(P/'controllers',N/'controllers')
 payloads={};specs={};sources={}
 rec=read(P/'reports/ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json')
 rec.update(remaining_after=proof['remaining_actual_snapshot'],source_current_cohort_original_cost_summary=proof,latest69_original_cost_closure=proof,derived_current_cohort_source_cost_receipt_only=True,legacy18_pending_not_reconciled_again=True)
 put(R/'ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json',rec)
 for key in ('h1','recovery'):
  base=Path(oldq['payloads'][key]);out=N/'payloads'/key
  shutil.copytree(base,out,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
  oldm=read(base/'THREE_SLOT_COMPLETE_MANIFEST_V1.json');model=proof['models'][key];final=model['final'];source=Path(final['local_path'])
  assert source.stat().st_size==final['bytes'] and final['twohost_complete_SHA']
  spec=dict(oldq['specs'][key]);spec.update(previous_runtime_root=oldq['roots'][key],previous_exit_kind='node',source_SHA=final['SHA'],source_Adamstep=model['Adam'],closed_production_continuation=True,reuse_completed_native=False)
  if key=='h1':spec['reward_migration']=False
  captures=out/'source_bind_history69';captures.mkdir()
  for name in ('THREE_SLOT_COMPLETE_MANIFEST_V1.json','job0/TASK.json'):
   shutil.copy2(out/name,captures/Path(name).name)
  shutil.copy2(source,out/'job0/source'/spec['source_filename'])
  role='closed_production_continuation_CPU_v2.py' if key=='h1' else 'original_account_policy50_source_CPU.py'
  shutil.copy2(path,out/role)
  shutil.copy2(N/'same_optimized_source_contract_metadata_candidate_v1.py',out/'same_optimized_source_contract_metadata_candidate_v1.py')
  if key=='recovery':(out/'recovery_worker.py').write_text(new_worker,encoding='utf8')
  task=read(out/'job0/TASK.json')
  task.update(id=N.name+'_'+key,source_SHA=final['SHA'],source_Adamstep=model['Adam'],source_H1_actual_latest_Adamstep=model['Adam'] if key=='h1' else None,source_parent_production_root=oldq['roots'][key],source_policy_hz=spec['policy_hz'],policy_hz=spec['policy_hz'],source_owned_updates=model['updates'],source_owned_completed_updates=model['updates'],exact_closed_source_updates=model['updates'],same_clock_complete_source_no_native_replay=True,same_step270_phase_complete_continuation=key=='h1',explicit_human_authorized_reward_path_change=False,reward_recipe_version='same_V6A_sagittal_tuck_and_sampling_optimization_continuation' if key=='h1' else None)
  (out/'job0/TASK.json').write_text(json.dumps(task,indent=2),encoding='utf8')
  proofname='CURRENT_ORIGINAL_PAIR_CLOSED_MODELS_COST_CPU_ACTUAL.json' if key=='h1' else 'CURRENT_ORIGINAL_COHORT_CLOSED_COST_CPU_ACTUAL.json'
  for name,val in [('QUALIFIED_RUNTIME_BASE_MANIFEST.json',oldm),(proofname,proof),('ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json',rec)]:
   (out/name).write_text(json.dumps(val,indent=2),encoding='utf8')
  auth=dict(epoch=time.time(),approved=True,kind='actual_closed69_to_same_optimized_source70',human_scope='Continue authorized step270 repair and sampling acceleration training; unchanged V6A reward/physics/actor/PPO',source69_complete_SHA=final['SHA'],source69_Adam=model['Adam'],source69_updates=model['updates'],source69_complete_original_cost_report_SHA=H(P/'reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json'),new_guard_SHA=H(out/role),metadata_contract_SHA=H(out/'same_optimized_source_contract_metadata_candidate_v1.py'),exact_Adam_guard_CPU_report_SHA=H(R/'SAME_OPTIMIZED70_EXACT_ADAM_GUARD_V2_CPU_ACTUAL.json'),no_new_reward_inputs_physics_or_amp=True,no_prior_approval_JSON_rewritten=True)
  put(out/'SAME_OPTIMIZED_CONTINUATION_SOURCE_AUTH_ACTUAL.json',auth)
  prior={x['relative']:x for x in oldm['files']};rows=[]
  for p in sorted(out.rglob('*')):
   if not p.is_file() or p.name=='THREE_SLOT_COMPLETE_MANIFEST_V1.json' or '__pycache__' in p.parts:continue
   rel=p.relative_to(out).as_posix()
   if p.suffix=='.py':ast.parse(p.read_text('utf8'))
   if p.suffix in ('.pt','.npz','.usd','.stl'):
    digest=final['SHA'] if rel=='job0/source/'+spec['source_filename'] else prior[rel]['SHA']
   else:digest=H(p)
   rows.append(dict(relative=rel,bytes=p.stat().st_size,SHA=digest))
  manifest=dict(oldm,source_SHA=final['SHA'],source_Adamstep=model['Adam'],files=rows,closed_step270_samephase_continuation=key=='h1',explicit_command_audit_adapter_repair=False)
  md.validate_same_optimized_protected_inventory(oldm,manifest)
  (out/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
  spec['manifest_SHA']=H(out/'THREE_SLOT_COMPLETE_MANIFEST_V1.json');payloads[key]=str(out);specs[key]=spec
  sources[key]=dict(SHA=final['SHA'],bytes=final['bytes'],Adam=model['Adam'],updates=model['updates'],path=final['path'])
 root='H1step270_sampling_opt1_sagtuck6a_2510v70'
 q=dict(epoch=time.time(),passed=True,payloads=payloads,specs=specs,sources=sources,roots=dict(h1='/mnt/mod4_linux_durable_20261013/'+root+'/h1',recovery='/home/lc01/Zonglin Li/zonglin2/tasks/'+root+'/recovery'),owner_root='/mnt/mod4_linux_durable_20261013/'+root+'/owner',previous_owner_root=oldq['owner_root'],both_latest_complete_model_CPU_original_cost_allout=True,no_native_or_query_replay=True,no_remote_Task_or_GO_yet=True,not_fresh_resource_or_installed_source_CPU_admission=True)
 put(R/'TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json',q)
 deploy=(P/'deploy_selected_pair_unused_once.py').read_text('utf8');needle="assert s['reward_migration'] and valid_ready(row,s)";assert deploy.count(needle)==1
 deploy=deploy.replace(needle,"assert not s.get('reward_migration') and valid_ready(row,s)",1)
 with (N/'deploy_selected_pair_unused_once.py').open('x',encoding='utf8') as f:f.write(deploy)
 for name in ('collect_selected_pair_first_PPO_unused_once.py','collect_selected_pair_finals_unused_once.py','review_selected_pair_models_unused_once.py'):
  shutil.copy2(P/name,N/name)
 print(json.dumps(dict(prepared_local_payloads=True,source_final_Adam={k:v['Adam'] for k,v in sources.items()},guard_fixture_tests=len(tests),same_V6A_reward_and_optimized_runtime=True,no_remote_install_Task_GO_or_fee=True)))
except BaseException:
 put(R/('SOURCE70_BOUND_PREPARE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),no_retry_same_once_or_remote_GO=True));raise
