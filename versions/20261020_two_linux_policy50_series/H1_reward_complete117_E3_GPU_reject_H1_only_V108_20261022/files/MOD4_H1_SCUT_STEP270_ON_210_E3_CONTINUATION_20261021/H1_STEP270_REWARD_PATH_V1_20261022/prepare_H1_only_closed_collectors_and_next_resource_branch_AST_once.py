from pathlib import Path
import ast,json,shutil,time,traceback
B=Path(__file__).resolve().parent;T=B.parent;R=B/'reports';N=T/'H1_STEP270_REWARD_H1_ONLY_V20_20261022';P=T/'H1_STEP270_E3_REWARD_PATH_PAIR_V19_20261022';C18=T/'H1_STEP270_E3_REWARD_PATH_PAIR_V18_20261022'
read=lambda p:json.loads(Path(p).read_bytes())
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
try:
 assert read(N/'reports/H1_ONLY_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_ACTUAL.json')['passed']
 full=(C18/'collect_pair_complete_finals_original_cost_bounded_once.py').read_text('utf8');start=full.index('READ72=r');cap=full.index('def capture(',start);main=full.index('def main():',cap)
 prefix=full[:start]+full[cap:main];prefix=prefix.replace("{'h1','recovery'}","{'h1'}")
 close=prefix+'''def main():
 metadata=json.loads((R/'H1_ONLY_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_ACTUAL.json').read_bytes());assert metadata['passed'] and metadata['source210']['H1_actual_GO']['nominal_end_epoch']-time.time()<=900
 q=json.loads((R/'H1_ONLY_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json').read_bytes());put('H1_ONLY_CLOSING_STARTED_ACTUAL.json',dict(epoch=time.time(),actual_owner=q['owner_identity']));c=d.t.connect()
 try:
  a=d.code(c,d.t.PY,READ210,dict(q=q),timeout=900);put('H1_ONLY_CLOSED_CANONICAL_COST_ACTUAL.json',a);final=a['cohort']['rows']['h1'].get('final') or {};texts,models=capture(c,a,[final['final']] if final.get('passed') else [],'h1')
 finally:c.close()
 result=dict(epoch=time.time(),actual_finite_transport_returned=True,source210=a,complete_models=dict(h1=models),all_texts=texts,original_canonical_cost_settled=True,E3_no_GO_or_cost_interval=True,not_skill_qualification=True)
 put('H1_ONLY_COMPLETE_FINAL_ORIGINAL_COST_RETURNED_ACTUAL.json',result);print(json.dumps(dict(closed=True,H1_complete_models=len(models),original_cost_settled=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  put('H1_ONLY_CLOSING_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_rerun_or_refund=True));raise
''';(N/'collect_H1_only_complete_final_original_cost_bounded_once.py').write_text(close,encoding='utf8')
 review=(C18/'review_pair_complete_models_original_cost_CPU_once.py').read_text('utf8').replace('PAIR_COMPLETE_FINALS_AND_ORIGINAL_COST_RETURNED_ACTUAL','H1_ONLY_COMPLETE_FINAL_ORIGINAL_COST_RETURNED_ACTUAL').replace("{'h1','recovery'}","{'h1'}").replace("for key in ('h1','recovery'):","for key in ('h1',):").replace('PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL','H1_ONLY_COMPLETE_MODEL_ORIGINAL_COST_CPU_ACTUAL')
 (N/'review_H1_only_complete_model_original_cost_CPU_once.py').write_text(review,encoding='utf8')
 storage=(C18/'relocate_actual_closed_H1_forensics_peer_TLS_bounded_once.py').read_text('utf8').replace('PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL','H1_ONLY_COMPLETE_MODEL_ORIGINAL_COST_CPU_ACTUAL').replace('PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL','H1_ONLY_ORIGINAL_ACCOUNT_DETACHED_ACTUAL')
 (N/'relocate_actual_closed_H1_only_forensics_peer_TLS_bounded_once.py').write_text(storage,encoding='utf8')
 F=T/'H1_STEP270_REWARD_RESOURCE_BRANCH_V21_20261022';assert not F.exists();F.mkdir();(F/'reports').mkdir()
 shutil.copytree(P/'controllers',F/'paired_controllers');shutil.copytree(N/'controllers',F/'h1_only_controllers')
 for src,dst in [(P/'deploy_pair_new_original_writer_bounded_once.py','deploy_selected_pair_unused_once.py'),(N/'deploy_H1_only_new_original_writer_bounded_once.py','deploy_selected_H1_only_unused_once.py'),(P/'collect_pair_first_actual_GO_positive_PPO_once.py','collect_selected_pair_first_PPO_unused_once.py'),(N/'collect_H1_only_actual_GO_positive_PPO_once.py','collect_selected_H1_first_PPO_unused_once.py'),(C18/'collect_pair_complete_finals_original_cost_bounded_once.py','collect_selected_pair_finals_unused_once.py'),(C18/'review_pair_complete_models_original_cost_CPU_once.py','review_selected_pair_models_unused_once.py'),(N/'collect_H1_only_complete_final_original_cost_bounded_once.py','collect_selected_H1_final_unused_once.py'),(N/'review_H1_only_complete_model_original_cost_CPU_once.py','review_selected_H1_model_unused_once.py')]:shutil.copy2(src,F/dst)
 # Future boundary probe only, never during the current healthy H1 window.
 probe=(B/'read_pair19_actual_resource_rejection_bounded_once.py').read_text('utf8')
 probe=probe.replace("N=B.parent/'H1_STEP270_E3_REWARD_PATH_PAIR_V19_20261022'", "N=Path(__file__).resolve().parent;B=N.parent/'H1_STEP270_REWARD_PATH_V1_20261022';R=N/'reports'")
 probe=probe.replace("q=json.loads((N/'reports/TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json').read_bytes())", "proof=json.loads((N.parent/'H1_STEP270_REWARD_H1_ONLY_V20_20261022/reports/H1_ONLY_COMPLETE_MODEL_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes());assert proof['passed'] and proof['original_canonical_cost_settled'] and proof['all_owner_nodes_children_actual_out']\n q=json.loads((N.parent/'H1_STEP270_E3_REWARD_PATH_PAIR_V19_20261022/reports/TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json').read_bytes())")
 probe=probe.replace('PAIR19_ACTUAL_RESOURCE_REJECTION_COMPONENTS_ACTUAL','NEXT_E3_BOUNDARY_RESOURCE_COMPONENTS_ACTUAL').replace('PAIR19_RESOURCE_READER_ORIGINAL_ERROR_','NEXT_E3_BOUNDARY_RESOURCE_ORIGINAL_ERROR_')
 (F/'read_E3_resource_only_after_actual_H1_closed_CPU_once.py').write_text(probe,encoding='utf8')
 prep=(P/'prepare_pair_from_actual_closed_reward_pair_CPU_once.py').read_text('utf8')
 a=prep.index(" cfg=read(N/'PAIR_RESERVED_SOURCE_CONFIG_NO_TOKEN.json')");z=prep.index(" put('PAIR_LATEST_SOURCES_PREPARE_STARTED_ACTUAL.json'",a)
 prep=prep[:a]+''' P=T/'H1_STEP270_REWARD_H1_ONLY_V20_20261022';E=T/'H1_STEP270_E3_REWARD_PATH_PAIR_V18_20261022'
 approved=read(T/'reports/V101_HUMAN_EXPLICIT_FUTURE_TRACE_RETENTION_APPROVAL_ACTUAL.json');retention=read(T/'reports/V101_FUTURE_BOUNDED_TRACE_PAIR_RETENTION_CANDIDATE_CPU_ACTUAL.json');assert approved['approved'] and retention['passed']
 receipt=read(P/'reports/H1_ONLY_COMPLETE_FINAL_ORIGINAL_COST_RETURNED_ACTUAL.json');hp=read(P/'reports/H1_ONLY_COMPLETE_MODEL_ORIGINAL_COST_CPU_ACTUAL.json');ep=read(E/'reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json')
 assert receipt['actual_finite_transport_returned'] and hp['passed'] and hp['all_owner_nodes_children_actual_out'] and hp['original_canonical_cost_settled'] and ep['passed'] and ep['original_canonical_cost_settled']
 resource=read(R/'NEXT_E3_BOUNDARY_RESOURCE_COMPONENTS_ACTUAL.json');assert time.time()-resource['epoch']<600
 paired=all(resource[k] for k in ('expected_GPU_empty','GPU7000_passed','disk25_passed','RAM8_passed'));keys=('h1','recovery') if paired else ('h1',)
 hq=read(P/'reports/TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json');eq=read(E/'reports/TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json')
 oldq=dict(payloads={k:(hq if k=='h1' else eq)['payloads'][k] for k in keys},specs={k:(hq if k=='h1' else eq)['specs'][k] for k in keys},roots={k:(hq if k=='h1' else eq)['roots'][k] for k in keys})
 proof=dict(hp,models=dict(h1=hp['models']['h1'],**(dict(recovery=ep['models']['recovery']) if paired else {})),historical_E3_source_cost_already_settled_not_current_charge=True)
 assert proof['remaining_actual_snapshot']>82512.86069250107
 cfg=dict(cohort_id=N.name,owner_root='/mnt/mod4_linux_durable_20261013/H1step270_reward_resource_2210v21/owner',roots={k:('/mnt/mod4_linux_durable_20261013/H1step270_reward_resource_2210v21/h1' if k=='h1' else '/home/lc01/Zonglin Li/zonglin2/tasks/H1step270_reward_resource_2210v21/recovery') for k in keys})
 shutil.copytree(N/('paired_controllers' if paired else 'h1_only_controllers'),N/'controllers')
 scheduler=read(P/'reports/H1_ONLY_ORIGINAL_ACCOUNT_SCHEDULER_CPU_ACTUAL.json')
 if not paired:
  scheduler.update(owner_SHA=H(N/'controllers/three_slot_finite_owner_v1.py'),not_remote_installed_or_GO_yet=True);put('H1_ONLY_ORIGINAL_ACCOUNT_SCHEDULER_CPU_ACTUAL.json',scheduler)
 put('RESOURCE_BRANCH_PREPARE_DECISION_ACTUAL.json',dict(epoch=time.time(),paired=paired,resource=resource,keys=keys,no_GO=True))
''' +prep[z:]
 prep=prep.replace("for key in ('h1','recovery'):","for key in keys:")
 prep=prep.replace("rec=read(P/'reports/ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json')","rec=read(P/'reports/ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json')")
 prep=prep.replace("read(P/'reports/PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json')", "read(P/'reports/H1_ONLY_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json')")
 # Keep the irrelevant unused owner file inside the H1 node payload byteexact; actual owner code lives separately.
 prep=prep.replace("for p in (N/'controllers').glob('*.py'):shutil.copy2(p,dest/p.name)", "for p in (N/'controllers').glob('*.py'):\n   if p.name!='three_slot_finite_owner_v1.py':shutil.copy2(p,dest/p.name)")
 (F/'prepare_next_latest_sources_after_actual_H1_closed_resource_CPU_once.py').write_text(prep,encoding='utf8')
 for p in [*N.glob('*.py'),*F.rglob('*.py')]:ast.parse(p.read_text('utf8'))
 put(R/'V108_H1_ONLY_CURRENT_CLOSING_AND_NEXT_RESOURCE_BRANCH_UNUSED_SOURCE_AST_ACTUAL.json',dict(epoch=time.time(),passed_AST=True,current_H1_close_collect_review_storage_unused=True,next_stage=str(F),next_E3_resource_probe_only_after_current_complete_CPU=True,next_preparer_binds_latest_H1_and_last_qualified_E3_no_phantom_E3_cost=True,only_AST_reserved_no_future_payload_remote_Task_or_GO=True))
 print(json.dumps(dict(passed_AST=True,current_closing_prepared=True,next_resource_branch_reserved=True)))
except BaseException:
 put(R/('H1_ONLY_CLOSING_BRANCH_PREPARE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(error=traceback.format_exc()));raise
