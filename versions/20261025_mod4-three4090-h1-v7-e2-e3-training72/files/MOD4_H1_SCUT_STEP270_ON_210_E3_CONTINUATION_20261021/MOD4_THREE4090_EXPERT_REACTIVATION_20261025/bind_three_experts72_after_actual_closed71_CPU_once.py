"""Late bind only actually closed71 H1/E3 and the admitted original52 E2 source."""
from pathlib import Path
import ast,hashlib,json,shutil,time,traceback
S=Path(__file__).resolve().parent;T=S.parent;R=S/'reports';N=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V72_20261025';P=T/'H1_STEP270_SAGITTAL_V6A_SAMPLING_OPT_NET_V5_RESOURCE_V71_20261025'
read=lambda p:json.loads(Path(p).read_bytes());H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):
 with Path(p).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
try:
 proof=read(P/'reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json');assert proof['passed'] and proof['all_owner_nodes_children_actual_out'] and proof['original_canonical_cost_settled'] and proof['all_original_private_shared_locks_free'] and all(v['actual_cost']['duration_bound_passed'] for v in proof['models'].values())
 assert proof['remaining_actual_snapshot']>86412.86069250107
 e2=read(N/'reports/E2_CROSS_HOST_TARGET_PAYLOAD_SOURCE_CPU_PREPARED_V2_ACTUAL.json');installed=read(R/'E2_THIRD_HOST_CPU_INSTALL_RETURNED_ACTUAL.json');assert installed['passed'] and installed['actual_finite_returned']
 v7=read(R/'H1_V7_NEAR_EDGE_TAKEOFF_REWARD_ONLY_CPU_ACTUAL.json');assert v7['passed'] and v7['source_AST_only_three_recipe_literals_changed']
 oldq=read(P/'reports/TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json');controller=read(R/'THREE_GPU_CONTROLLER_SOURCE_AUTH_ACTUAL.json')
 rec=read(P/'reports/ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json');rec.update(remaining_after=proof['remaining_actual_snapshot'],source_current_cohort_original_cost_summary=proof,latest71_original_cost_closure=proof,derived_current_cohort_source_cost_receipt_only=True,legacy18_pending_not_reconciled_again=True,historical_E2_source52_cost_not_recharged=True)
 put(N/'reports/ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json',rec)
 payloads=dict(e2=e2['payload']);specs=dict(e2=e2['spec']);sources=dict(e2=dict(SHA=e2['source']['SHA'],bytes=e2['source']['bytes'],Adam=839920,updates=e2['source']['updates'],path=e2['source']['path']));roots=dict(e2=e2['root'])
 for key in ('h1','recovery'):
  base=Path(oldq['payloads'][key]);out=N/'payloads'/key;assert not out.exists();shutil.copytree(base,out,ignore=shutil.ignore_patterns('__pycache__','*.pyc'));oldm=read(base/'THREE_SLOT_COMPLETE_MANIFEST_V1.json');model=proof['models'][key];final=model['final'];assert final['twohost_complete_SHA'] and Path(final['local_path']).stat().st_size==final['bytes']
  hist=out/'prebind71_exact_history';hist.mkdir()
  for name in ('THREE_SLOT_COMPLETE_MANIFEST_V1.json','job0/TASK.json','ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json','QUALIFIED_RUNTIME_BASE_MANIFEST.json'):
   shutil.copy2(out/name,hist/Path(name).name)
  spec=dict(oldq['specs'][key]);spec.update(previous_runtime_root=oldq['roots'][key],previous_exit_kind='node',source_SHA=final['SHA'],source_Adamstep=model['Adam'],reward_migration=key=='h1',closed_production_continuation=True,reuse_completed_native=False)
  shutil.copy2(final['local_path'],out/'job0/source'/spec['source_filename'])
  for p in (N/'controllers').glob('*.py'):shutil.copy2(p,out/p.name)
  role='closed_production_continuation_CPU_v2.py' if key=='h1' else 'original_account_policy50_source_CPU.py';shutil.copy2(S/'three_expert_closed71_source_admission_v5.py',out/role)
  if key=='h1':
   for name in ('h1_step270_path_reward_v1.py','step270_reward_installed_CPU_v1.py'):shutil.copy2(S/'H1_V7_reward_only_candidate'/name,out/name)
   put(out/'H1_V7_REWARD_ONLY_AUTH_AND_CPU_ACTUAL.json',dict(v7,approved=True))
  else:
   p=out/'recovery_worker.py';text=p.read_text('utf8');a='{'+str(oldm['source_Adamstep'])+'+20*updates}';assert text.count(a)==1;p.write_text(text.replace(a,'{'+str(model['Adam'])+'+20*updates}',1),encoding='utf8')
  task=read(out/'job0/TASK.json');task.update(id=N.name+'_'+key,source_SHA=final['SHA'],source_Adamstep=model['Adam'],source_H1_actual_latest_Adamstep=model['Adam'] if key=='h1' else None,source_owned_updates=model['updates'],source_owned_completed_updates=model['updates'],exact_closed_source_updates=model['updates'],source_parent_production_root=oldq['roots'][key],reward_recipe_version='step270_near_edge_takeoff_gate_v7_reward_only' if key=='h1' else None,explicit_human_authorized_reward_path_change=key=='h1',three_GPU_existing_experts_authorized=True)
  (out/'job0/TASK.json').write_text(json.dumps(task,indent=2),encoding='utf8')
  for name,val in [('QUALIFIED_RUNTIME_BASE_MANIFEST.json',oldm),('CURRENT_ORIGINAL_PAIR_CLOSED_MODELS_COST_CPU_ACTUAL.json',proof),('ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json',rec)]: (out/name).write_text(json.dumps(val,indent=2),encoding='utf8')
  put(out/'THREE_GPU_CONTROLLER_SOURCE_AUTH_ACTUAL.json',controller)
  auth=dict(epoch=time.time(),approved=True,kind='actual_closed71_to_three_experts72',source_SHA=final['SHA'],source_Adam=model['Adam'],source_complete_CPU_report_SHA=H(P/'reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json'),new_guard_SHA=H(out/role),metadata_contract_SHA=H(out/'same_optimized_source_contract_metadata_candidate_v1.py'),original_single_writer_3_caps_11700=True,no_original_approval_rewrite=True)
  put(out/'THREE_EXPERT_CONTINUATION_SOURCE_AUTH_ACTUAL.json',auth)
  before={r['relative']:r for r in oldm['files']};rows=[]
  for p in sorted(out.rglob('*')):
   if not p.is_file() or p.name=='THREE_SLOT_COMPLETE_MANIFEST_V1.json' or '__pycache__' in p.parts:continue
   rel=p.relative_to(out).as_posix()
   if p.suffix=='.py':ast.parse(p.read_text('utf8'))
   digest=(final['SHA'] if rel=='job0/source/'+spec['source_filename'] else before[rel]['SHA']) if p.suffix in ('.pt','.npz','.usd','.stl') else H(p)
   rows.append(dict(relative=rel,bytes=p.stat().st_size,SHA=digest))
  m=dict(oldm,source_SHA=final['SHA'],source_Adamstep=model['Adam'],files=rows,three_existing_experts_authorized=True,H1_V7_reward_only=key=='h1')
  (out/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').write_text(json.dumps(m,indent=2),encoding='utf8');spec['manifest_SHA']=H(out/'THREE_SLOT_COMPLETE_MANIFEST_V1.json');payloads[key]=str(out);specs[key]=spec;sources[key]=dict(SHA=final['SHA'],bytes=final['bytes'],Adam=model['Adam'],updates=model['updates'],path=final['path'])
  roots[key]=('/mnt/mod4_linux_durable_20261013/H1step270_three_experts_2510v72/h1' if key=='h1' else '/home/lc01/Zonglin Li/zonglin2/tasks/H1step270_three_experts_2510v72/recovery')
 q=dict(epoch=time.time(),passed=True,payloads=payloads,specs=specs,sources=sources,roots=roots,owner_root='/mnt/mod4_linux_durable_20261013/H1step270_three_experts_2510v72/owner',previous_owner_root=oldq['owner_root'],E2_preinstalled_CPU=installed,both_latest71_complete_source_models_CPU_cost_allout=True,historical_E2_source52_already_cost_settled=True,three_slot_strict_remaining_guard=86412.86069250107,no_remote_GO_or_new_fee_yet=True)
 put(N/'reports/THREE_EXPERTS_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json',q)
 print(json.dumps(dict(bound=True,source_Adams={k:v['Adam'] for k,v in sources.items()},three_slots=True,H1_V7_reward_only=True,no_GO=True)))
except BaseException:
 put(R/('THREE_GPU_LATE_BIND_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),no_retry_same_once_or_refund=True));raise
