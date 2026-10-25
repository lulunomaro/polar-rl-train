"""Late binding only: do not run before actual73b complete models and original cost closure."""
from pathlib import Path
import ast,hashlib,json,shutil,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;P=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V73B_20261025';R=N/'reports'
read=lambda p:json.loads(Path(p).read_bytes())
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):
 with Path(p).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def main():
 proof=read(P/'reports/THREE_EXPERT_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json')
 assert proof['passed'] and proof['all_owner_nodes_children_actual_out'] and proof['original_canonical_cost_settled'] and proof['all_original_private_shared_locks_free'] and set(proof['models'])=={'h1','e2','recovery'}
 assert all(v['actual_cost']['duration_bound_passed'] for v in proof['models'].values()) and proof['remaining_actual_snapshot']>86412.86069250107
 oldq=read(P/'reports/THREE_EXPERTS_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json')
 rec=read(P/'reports/ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json')
 rec.update(remaining_after=proof['remaining_actual_snapshot'],source_current_cohort_original_cost_summary=proof,latest73b_original_cost_closure=proof,derived_current_cohort_source_cost_receipt_only=True,legacy18_pending_not_reconciled_again=True,historical_E2_source52_cost_not_recharged=True)
 put(R/'ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json',rec)
 assert not (N/'controllers').exists();shutil.copytree(P/'controllers',N/'controllers')
 q=dict(epoch=time.time(),passed=True,payloads={},specs={},sources={},roots={},owner_root='/mnt/mod4_linux_durable_20261013/H1step270_three_experts_2610v74/owner',previous_owner_root=oldq['owner_root'],three_slot_strict_remaining_guard=86412.86069250107,actual73b_original_models_cost_allout=True,no_remote_GO_or_new_fee_yet=True)
 for key in ('h1','e2','recovery'):
  base=Path(oldq['payloads'][key]);out=N/'payloads'/key;assert not out.exists();shutil.copytree(base,out,ignore=shutil.ignore_patterns('__pycache__','*.pyc'));prior=read(base/'THREE_SLOT_COMPLETE_MANIFEST_V1.json');model=proof['models'][key];final=model['final']
  assert final['twohost_complete_SHA'] and Path(final['local_path']).stat().st_size==final['bytes'] and model['Adam']==prior['source_Adamstep']+20*model['updates']
  hist=out/('prebind_'+prior['source_SHA'][:12]+'_exact_history');hist.mkdir()
  for name in ('THREE_SLOT_COMPLETE_MANIFEST_V1.json','job0/TASK.json','ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json','QUALIFIED_RUNTIME_BASE_MANIFEST.json'):
   shutil.copy2(out/name,hist/Path(name).name)
  role='closed_production_continuation_CPU_v2.py' if key=='h1' else 'original_account_policy50_source_CPU.py';shutil.copy2(out/role,hist/(role+'.original_bytes.txt'))
  spec=dict(oldq['specs'][key]);spec.update(previous_runtime_root=oldq['roots'][key],previous_exit_kind='node',source_SHA=final['SHA'],source_Adamstep=model['Adam'],reward_migration=False,cross_host_qualified_source=False,closed_production_continuation=True,reuse_completed_native=False)
  shutil.copy2(final['local_path'],out/'job0/source'/spec['source_filename'])
  shutil.copy2(N/'candidates/same_three_closed_source_unchanged_V7_CPU_v1.py',out/role)
  shutil.copy2(N/'candidates/same_optimized_source_contract_metadata_candidate_v1.py',out/'same_optimized_source_contract_metadata_candidate_v1.py')
  if key=='recovery':
   p=out/'recovery_worker.py';s=p.read_text('utf8');old='{'+str(prior['source_Adamstep'])+'+20*updates}';assert s.count(old)==1;p.write_text(s.replace(old,'{'+str(model['Adam'])+'+20*updates}',1),'utf8')
  task=read(out/'job0/TASK.json');task.update(id=N.name+'_'+key,source_SHA=final['SHA'],source_Adamstep=model['Adam'],source_owned_updates=model['updates'],source_owned_completed_updates=model['updates'],exact_closed_source_updates=model['updates'],source_parent_production_root=oldq['roots'][key],three_GPU_existing_experts_authorized=True)
  if key=='h1':task.update(source_H1_actual_latest_Adamstep=model['Adam'],reward_recipe_version='step270_near_edge_takeoff_gate_v7_reward_only')
  (out/'job0/TASK.json').write_text(json.dumps(task,indent=2),'utf8')
  for name,val in [('QUALIFIED_RUNTIME_BASE_MANIFEST.json',prior),('CURRENT_ORIGINAL_THREE_CLOSED_MODELS_COST_CPU_ACTUAL.json',proof),('ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json',rec)]:
   (out/name).write_text(json.dumps(val,indent=2),'utf8')
  put(out/'THREE_EXPERT_SAME_V7_CONTINUATION_AUTH_ACTUAL.json',dict(epoch=time.time(),approved=True,kind='actual_closed_three_same_V7_continuation',source_SHA=final['SHA'],source_Adam=model['Adam'],guard_SHA=H(out/role),metadata_SHA=H(out/'same_optimized_source_contract_metadata_candidate_v1.py'),actual_closed73b_report_SHA=H(P/'reports/THREE_EXPERT_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json'),no_reward_actor_controller_physics_change=True))
  before={r['relative']:r for r in prior['files']};rows=[]
  for p in sorted(out.rglob('*')):
   if not p.is_file() or p.name=='THREE_SLOT_COMPLETE_MANIFEST_V1.json' or '__pycache__' in p.parts:continue
   rel=p.relative_to(out).as_posix()
   if p.suffix=='.py':ast.parse(p.read_text('utf8'))
   digest=(final['SHA'] if rel=='job0/source/'+spec['source_filename'] else before[rel]['SHA']) if p.suffix in ('.pt','.npz','.usd','.stl') else H(p)
   rows.append(dict(relative=rel,bytes=p.stat().st_size,SHA=digest))
  m=dict(prior,source_SHA=final['SHA'],source_Adamstep=model['Adam'],files=rows,same_V7_three_expert_continuation=True)
  (out/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').write_text(json.dumps(m,indent=2),'utf8');spec['manifest_SHA']=H(out/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')
  q['payloads'][key]=str(out);q['specs'][key]=spec;q['sources'][key]=dict(SHA=final['SHA'],bytes=final['bytes'],Adam=model['Adam'],updates=model['updates'],path=final['path'])
  q['roots'][key]=('/mnt/mod4_linux_durable_20261013' if key=='h1' else '/home/lc01/Zonglin Li/zonglin2/tasks')+'/H1step270_three_experts_2610v74/'+key
 put(R/'THREE_EXPERTS_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json',q)
 print(json.dumps(dict(bound_actual73b_sources=True,source_Adams={k:v['Adam'] for k,v in q['sources'].items()},no_GO=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  put(R/('SOURCE_BIND_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),do_not_rerun_same_once_or_root=True));raise
